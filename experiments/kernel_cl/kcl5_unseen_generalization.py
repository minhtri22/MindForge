"""KCL-5: unseen task-pair generalization for frozen 6.25% replay.

Protocol: docs/research/kernel-continual-learning/kcl5-protocol.md
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import statistics
import subprocess
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    Gates,
    KCL1Config,
    build_model,
    evaluate,
    independent_run,
    optimizer_for,
    parameter_count,
    train_stage,
)


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl5-protocol.md")
FAMILIES = ("U1_AFFINE_PREFIX", "U2_STRIDE_SUFFIX")
QUALIFICATION_SEEDS = (606, 808)
FINAL_SEEDS = (111, 222, 333, 777, 999)

CONTROL_B_PER_BATCH = 16
TREATMENT_B_PER_BATCH = 15
TREATMENT_A_PER_BATCH = 1
REPLAY_FRACTION = 1 / 16

QUALIFICATION_GATES = Gates()
TREATMENT_B_ACCURACY_MIN = 0.95
CONTROL_B_ACCURACY_MIN = 0.95
CONTROL_FORGETTING_MIN = 0.50
RETENTION_GAIN_MEAN_MIN = 0.30
RELATIVE_FORGETTING_REDUCTION_MEAN_MIN = 0.50
TREATMENT_B_ACCURACY_MEAN_MIN = 0.95


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "pstdev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def _deep_equal(a: Any, b: Any) -> bool:
    if torch.is_tensor(a) and torch.is_tensor(b):
        return torch.equal(a, b)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_deep_equal(x, y) for x, y in zip(a, b))
    return a == b


def unseen_tasks(
    family: str,
    config: KCL1Config,
) -> tuple[tuple[torch.Tensor, torch.Tensor], tuple[torch.Tensor, torch.Tensor]]:
    if config.relations != 24:
        raise ValueError("KCL-5 frozen protocol requires 24 relations")

    keys = torch.arange(10, 34, dtype=torch.long)
    i = torch.arange(24, dtype=torch.long)

    if family == "U1_AFFINE_PREFIX":
        task_a_id, task_b_id = 4, 5
        a_index = (5 * i + 1) % 24
        b_index = (7 * i + 3) % 24
        input_a = torch.stack([torch.full_like(keys, task_a_id), keys], dim=1)
        input_b = torch.stack([torch.full_like(keys, task_b_id), keys], dim=1)
    elif family == "U2_STRIDE_SUFFIX":
        task_a_id, task_b_id = 6, 7
        a_index = (11 * i + 5) % 24
        b_index = (13 * i + 2) % 24
        input_a = torch.stack([keys, torch.full_like(keys, task_a_id)], dim=1)
        input_b = torch.stack([keys, torch.full_like(keys, task_b_id)], dim=1)
    else:
        raise ValueError(f"unknown KCL-5 family: {family}")

    values_a = 40 + a_index
    values_b = 40 + b_index
    if int(max(values_a.max(), values_b.max())) >= config.vocab_size:
        raise ValueError("frozen KCL-5 vocabulary too small")

    return (input_a, values_a), (input_b, values_b)


def _qualification_sequential(
    family: str,
    seed: int,
    config: KCL1Config,
) -> dict[str, Any]:
    task_a, task_b = unseen_tasks(family, config)
    model = build_model(config, seed)
    optimizer = optimizer_for(model, config)

    train_stage(
        model,
        optimizer,
        task_a,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )
    a_after_a = evaluate(model, task_a)

    control_model = copy.deepcopy(model)
    control_optimizer = optimizer_for(control_model, config)
    control_optimizer.load_state_dict(copy.deepcopy(optimizer.state_dict()))

    train_stage(
        control_model,
        control_optimizer,
        task_a,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 211,
    )
    a_after_a2 = evaluate(control_model, task_a)

    train_stage(
        model,
        optimizer,
        task_b,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 307,
    )
    a_after_b = evaluate(model, task_a)
    b_after_b = evaluate(model, task_b)

    forgetting = a_after_a["accuracy"] - a_after_b["accuracy"]
    control_drift = a_after_a["accuracy"] - a_after_a2["accuracy"]

    return {
        "a_after_a": a_after_a,
        "a_after_b": a_after_b,
        "b_after_b": b_after_b,
        "a_after_a2_control": a_after_a2,
        "forgetting_accuracy": forgetting,
        "control_drift_accuracy": control_drift,
    }


def _qualification_seed_pass(result: dict[str, Any]) -> bool:
    seq = result["sequential"]
    values = [
        result["independent_a"]["accuracy"],
        result["independent_b"]["accuracy"],
        seq["a_after_a"]["accuracy"],
        seq["b_after_b"]["accuracy"],
        seq["forgetting_accuracy"],
        seq["control_drift_accuracy"],
    ]
    return (
        all(math.isfinite(float(v)) for v in values)
        and result["independent_a"]["accuracy"] >= 0.95
        and result["independent_b"]["accuracy"] >= 0.95
        and seq["a_after_a"]["accuracy"] >= 0.95
        and seq["b_after_b"]["accuracy"] >= 0.95
        and seq["forgetting_accuracy"] >= 0.50
        and abs(seq["control_drift_accuracy"]) <= 0.10
    )


def qualify_family(family: str, config: KCL1Config) -> dict[str, Any]:
    task_a, task_b = unseen_tasks(family, config)
    rows = []
    for seed in QUALIFICATION_SEEDS:
        result = {
            "seed": seed,
            "independent_a": independent_run(
                task_a, config=config, seed=seed, stream_offset=17
            ),
            "independent_b": independent_run(
                task_b, config=config, seed=seed, stream_offset=31
            ),
            "sequential": _qualification_sequential(family, seed, config),
        }
        result["pass"] = _qualification_seed_pass(result)
        rows.append(result)
    return {
        "family": family,
        "seeds": list(QUALIFICATION_SEEDS),
        "per_seed": rows,
        "qualified": all(row["pass"] for row in rows),
    }


def _replay_stage(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    task_a: tuple[torch.Tensor, torch.Tensor],
    task_b: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
) -> None:
    a_x, a_y = task_a
    b_x, b_y = task_b
    gen_a = torch.Generator(device="cpu")
    gen_b = torch.Generator(device="cpu")
    gen_a.manual_seed(seed + 811)
    gen_b.manual_seed(seed + 919)

    model.train()
    for _ in range(steps):
        idx_b = torch.randint(0, len(b_y), (TREATMENT_B_PER_BATCH,), generator=gen_b)
        idx_a = torch.randint(0, len(a_y), (TREATMENT_A_PER_BATCH,), generator=gen_a)
        x = torch.cat([b_x[idx_b], a_x[idx_a]], dim=0)
        y = torch.cat([b_y[idx_b], a_y[idx_a]], dim=0)
        logits = model(x)[:, -1, :]
        loss = F.cross_entropy(logits, y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-5 replay loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


def run_final_seed(family: str, seed: int, config: KCL1Config) -> dict[str, Any]:
    task_a, task_b = unseen_tasks(family, config)
    base_model = build_model(config, seed)
    base_optimizer = optimizer_for(base_model, config)

    train_stage(
        base_model,
        base_optimizer,
        task_a,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )
    a_after_a = evaluate(base_model, task_a)

    control_model = copy.deepcopy(base_model)
    control_optimizer = optimizer_for(control_model, config)
    control_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    treatment_model = copy.deepcopy(base_model)
    treatment_optimizer = optimizer_for(treatment_model, config)
    treatment_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    model_state_equal = all(
        torch.equal(control_model.state_dict()[name], treatment_model.state_dict()[name])
        for name in control_model.state_dict()
    )
    optimizer_state_equal = _deep_equal(
        control_optimizer.state_dict(), treatment_optimizer.state_dict()
    )

    train_stage(
        control_model,
        control_optimizer,
        task_b,
        steps=config.stage_steps,
        batch_size=CONTROL_B_PER_BATCH,
        seed=seed + 307,
    )
    _replay_stage(
        treatment_model,
        treatment_optimizer,
        task_a,
        task_b,
        steps=config.stage_steps,
        seed=seed,
    )

    control_a = evaluate(control_model, task_a)
    control_b = evaluate(control_model, task_b)
    treatment_a = evaluate(treatment_model, task_a)
    treatment_b = evaluate(treatment_model, task_b)

    control_forgetting = a_after_a["accuracy"] - control_a["accuracy"]
    treatment_forgetting = a_after_a["accuracy"] - treatment_a["accuracy"]
    retention_gain = treatment_a["accuracy"] - control_a["accuracy"]
    forgetting_reduction = control_forgetting - treatment_forgetting
    relative_reduction = (
        forgetting_reduction / control_forgetting
        if control_forgetting > 0
        else None
    )

    values = [
        a_after_a["accuracy"],
        control_a["accuracy"],
        control_b["accuracy"],
        treatment_a["accuracy"],
        treatment_b["accuracy"],
        control_forgetting,
        treatment_forgetting,
        retention_gain,
        forgetting_reduction,
    ]
    finite = all(math.isfinite(float(v)) for v in values)
    if relative_reduction is not None:
        finite = finite and math.isfinite(float(relative_reduction))

    per_seed_pass = (
        finite
        and model_state_equal
        and optimizer_state_equal
        and control_b["accuracy"] >= CONTROL_B_ACCURACY_MIN
        and control_forgetting >= CONTROL_FORGETTING_MIN
        and treatment_b["accuracy"] >= TREATMENT_B_ACCURACY_MIN
        and retention_gain > 0
    )

    return {
        "seed": seed,
        "a_after_a": a_after_a,
        "control": {
            "a_after_b": control_a,
            "b_after_b": control_b,
            "forgetting_accuracy": control_forgetting,
        },
        "treatment": {
            "a_after_b": treatment_a,
            "b_after_b": treatment_b,
            "forgetting_accuracy": treatment_forgetting,
            "replay_fraction": REPLAY_FRACTION,
            "a_replay_examples_per_batch": TREATMENT_A_PER_BATCH,
            "b_examples_per_batch": TREATMENT_B_PER_BATCH,
        },
        "effects": {
            "retention_gain": retention_gain,
            "forgetting_reduction": forgetting_reduction,
            "relative_forgetting_reduction": relative_reduction,
            "b_accuracy_delta": treatment_b["accuracy"] - control_b["accuracy"],
        },
        "integrity": {
            "all_metrics_finite": finite,
            "post_a_model_state_equal": model_state_equal,
            "post_a_optimizer_state_equal": optimizer_state_equal,
            "equal_optimizer_steps": True,
            "equal_batch_size": (
                CONTROL_B_PER_BATCH
                == TREATMENT_B_PER_BATCH + TREATMENT_A_PER_BATCH
                == config.batch_size
            ),
        },
        "per_seed_generalization_gate_pass": per_seed_pass,
    }


def evaluate_family(family: str, config: KCL1Config) -> dict[str, Any]:
    rows = [run_final_seed(family, seed, config) for seed in FINAL_SEEDS]
    retention = [row["effects"]["retention_gain"] for row in rows]
    relative = [row["effects"]["relative_forgetting_reduction"] for row in rows]
    treatment_b = [row["treatment"]["b_after_b"]["accuracy"] for row in rows]
    control_a = [row["control"]["a_after_b"]["accuracy"] for row in rows]
    treatment_a = [row["treatment"]["a_after_b"]["accuracy"] for row in rows]
    control_forgetting = [row["control"]["forgetting_accuracy"] for row in rows]
    treatment_forgetting = [row["treatment"]["forgetting_accuracy"] for row in rows]

    relative_defined = all(value is not None for value in relative)
    integrity_pass = all(
        all(value is True for value in row["integrity"].values())
        for row in rows
    )
    per_seed_gate = all(row["per_seed_generalization_gate_pass"] for row in rows)
    mean_retention_pass = statistics.fmean(retention) >= RETENTION_GAIN_MEAN_MIN
    mean_relative_pass = (
        relative_defined
        and statistics.fmean([float(x) for x in relative]) >= RELATIVE_FORGETTING_REDUCTION_MEAN_MIN
    )
    mean_plasticity_pass = (
        statistics.fmean(treatment_b) >= TREATMENT_B_ACCURACY_MEAN_MIN
    )

    passed = (
        integrity_pass
        and per_seed_gate
        and mean_retention_pass
        and mean_relative_pass
        and mean_plasticity_pass
    )

    return {
        "family": family,
        "seeds": list(FINAL_SEEDS),
        "per_seed": rows,
        "aggregates": {
            "control_a_after_b_accuracy": _stats(control_a),
            "treatment_a_after_b_accuracy": _stats(treatment_a),
            "control_forgetting_accuracy": _stats(control_forgetting),
            "treatment_forgetting_accuracy": _stats(treatment_forgetting),
            "retention_gain": _stats(retention),
            "relative_forgetting_reduction": (
                _stats([float(x) for x in relative]) if relative_defined else None
            ),
            "treatment_b_after_b_accuracy": _stats(treatment_b),
        },
        "gates": {
            "integrity_pass": integrity_pass,
            "per_seed_gate_pass": per_seed_gate,
            "mean_retention_gain_pass": mean_retention_pass,
            "mean_relative_forgetting_reduction_pass": mean_relative_pass,
            "mean_treatment_b_accuracy_pass": mean_plasticity_pass,
        },
        "pass": passed,
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    config = KCL1Config()

    qualification = [qualify_family(family, config) for family in FAMILIES]
    all_qualified = all(row["qualified"] for row in qualification)

    if all_qualified:
        final = [evaluate_family(family, config) for family in FAMILIES]
    else:
        final = []

    if not all_qualified:
        status = "FAIL"
        verdict = "UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED"
    else:
        pass_count = sum(1 for row in final if row["pass"])
        integrity_valid = all(
            row["gates"]["integrity_pass"] for row in final
        )
        if not integrity_valid:
            status = "REVISE"
            verdict = "GENERALIZATION_CONTRAST_INVALID"
        elif pass_count == len(FAMILIES):
            status = "PASS"
            verdict = "REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS"
        elif pass_count == 1:
            status = "PARTIAL"
            verdict = "REPLAY_GENERALIZATION_PARTIAL"
        else:
            status = "FAIL"
            verdict = "REPLAY_DOES_NOT_GENERALIZE"

    model = build_model(config, QUALIFICATION_SEEDS[0])
    return {
        "experiment": "KCL-5",
        "status": status,
        "verdict": verdict,
        "families": list(FAMILIES),
        "qualification_seeds": list(QUALIFICATION_SEEDS),
        "final_seeds": list(FINAL_SEEDS),
        "config": config.__dict__,
        "replay": {
            "fraction": REPLAY_FRACTION,
            "a_replay_examples_per_batch": TREATMENT_A_PER_BATCH,
            "b_examples_per_batch": TREATMENT_B_PER_BATCH,
            "total_batch_size": config.batch_size,
            "ratio_search_performed": False,
            "family_specific_adaptation": False,
        },
        "qualification": qualification,
        "final_generalization": final,
        "integrity": {
            "all_families_qualified": all_qualified,
            "qualification_and_final_seeds_disjoint": set(QUALIFICATION_SEEDS).isdisjoint(FINAL_SEEDS),
            "prior_kcl_seeds_reused": False,
            "model_architecture_changed": False,
            "family_selection_performed": False,
        },
        "model_parameter_count": parameter_count(model),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "scope": {
            "kcl6_started": False,
            "challenger_started": False,
            "reasoning_work": False,
            "external_api_calls": 0,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen MindForge KCL-5 unseen generalization")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl5_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] == "PASS":
        return 0
    if result["status"] == "REVISE":
        return 3
    if result["status"] == "PARTIAL":
        return 4
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
