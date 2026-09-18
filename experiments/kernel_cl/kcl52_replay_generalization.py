"""KCL-5.2: frozen 6.25% replay generalization across U1 + U3.

Protocol: docs/research/kernel-continual-learning/kcl52-protocol.md
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
    KCL1Config,
    build_model,
    evaluate,
    optimizer_for,
    parameter_count,
    train_stage,
)
from experiments.kernel_cl.kcl5_unseen_generalization import unseen_tasks as kcl5_tasks
from experiments.kernel_cl.kcl51_substrate_reconstruction import candidate_tasks as kcl51_tasks


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl52-protocol.md")
KCL5_EVIDENCE = Path("experiments/kernel_cl/results/kcl5_summary.json")
KCL51_EVIDENCE = Path("experiments/kernel_cl/results/kcl51_summary.json")

FAMILIES = ("U1_AFFINE_PREFIX", "U3_MIXED_POSITION")
FINAL_SEEDS = (1313, 1515, 1717, 1919, 2121)

CONTROL_B_PER_BATCH = 16
TREATMENT_B_PER_BATCH = 15
TREATMENT_A_PER_BATCH = 1
REPLAY_FRACTION = 1 / 16

CONTROL_B_ACCURACY_MIN = 0.95
CONTROL_FORGETTING_MIN = 0.50
TREATMENT_B_ACCURACY_MIN = 0.95
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


def _load_anchors() -> dict[str, Any]:
    kcl5 = json.loads(KCL5_EVIDENCE.read_text(encoding="utf-8"))
    kcl51 = json.loads(KCL51_EVIDENCE.read_text(encoding="utf-8"))

    kcl5_q = {
        item["family"]: item["qualified"]
        for item in kcl5.get("qualification", [])
    }

    kcl5_valid = (
        kcl5.get("status") == "FAIL"
        and kcl5.get("verdict") == "UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED"
        and kcl5_q.get("U1_AFFINE_PREFIX") is True
    )
    kcl51_valid = (
        kcl51.get("status") == "PASS"
        and kcl51.get("verdict") == "SECOND_UNSEEN_SUBSTRATE_ESTABLISHED"
        and kcl51.get("selected_candidate") == "U3_MIXED_POSITION"
    )

    return {
        "valid": kcl5_valid and kcl51_valid,
        "kcl5_valid": kcl5_valid,
        "kcl51_valid": kcl51_valid,
        "u1_qualified": kcl5_q.get("U1_AFFINE_PREFIX"),
        "u3_selected": kcl51.get("selected_candidate"),
        "kcl5_sha256": _sha256(KCL5_EVIDENCE),
        "kcl51_sha256": _sha256(KCL51_EVIDENCE),
    }


def family_tasks(
    family: str,
    config: KCL1Config,
) -> tuple[tuple[torch.Tensor, torch.Tensor], tuple[torch.Tensor, torch.Tensor]]:
    if family == "U1_AFFINE_PREFIX":
        return kcl5_tasks(family, config)
    if family == "U3_MIXED_POSITION":
        return kcl51_tasks(family, config)
    raise ValueError(f"unknown KCL-5.2 family: {family}")


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
            raise RuntimeError("non-finite KCL-5.2 replay loss")

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


def run_seed(family: str, seed: int, config: KCL1Config) -> dict[str, Any]:
    task_a, task_b = family_tasks(family, config)

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
    b_delta = treatment_b["accuracy"] - control_b["accuracy"]

    scalar_values = [
        a_after_a["accuracy"],
        control_a["accuracy"],
        control_b["accuracy"],
        treatment_a["accuracy"],
        treatment_b["accuracy"],
        control_forgetting,
        treatment_forgetting,
        retention_gain,
        forgetting_reduction,
        b_delta,
    ]
    all_finite = all(math.isfinite(float(v)) for v in scalar_values)
    if relative_reduction is not None:
        all_finite = all_finite and math.isfinite(float(relative_reduction))

    per_seed_pass = (
        all_finite
        and model_state_equal
        and optimizer_state_equal
        and control_b["accuracy"] >= CONTROL_B_ACCURACY_MIN
        and control_forgetting >= CONTROL_FORGETTING_MIN
        and treatment_b["accuracy"] >= TREATMENT_B_ACCURACY_MIN
        and retention_gain > 0
        and relative_reduction is not None
    )

    return {
        "seed": seed,
        "a_after_a": a_after_a,
        "control": {
            "a_after_b": control_a,
            "b_after_b": control_b,
            "forgetting_accuracy": control_forgetting,
            "b_examples_per_batch": CONTROL_B_PER_BATCH,
            "a_replay_examples_per_batch": 0,
        },
        "treatment": {
            "a_after_b": treatment_a,
            "b_after_b": treatment_b,
            "forgetting_accuracy": treatment_forgetting,
            "replay_fraction": REPLAY_FRACTION,
            "b_examples_per_batch": TREATMENT_B_PER_BATCH,
            "a_replay_examples_per_batch": TREATMENT_A_PER_BATCH,
        },
        "effects": {
            "retention_gain": retention_gain,
            "forgetting_reduction": forgetting_reduction,
            "relative_forgetting_reduction": relative_reduction,
            "b_accuracy_delta": b_delta,
        },
        "integrity": {
            "all_metrics_finite": all_finite,
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
    rows = [run_seed(family, seed, config) for seed in FINAL_SEEDS]

    control_a = [row["control"]["a_after_b"]["accuracy"] for row in rows]
    treatment_a = [row["treatment"]["a_after_b"]["accuracy"] for row in rows]
    control_b = [row["control"]["b_after_b"]["accuracy"] for row in rows]
    treatment_b = [row["treatment"]["b_after_b"]["accuracy"] for row in rows]
    control_forgetting = [row["control"]["forgetting_accuracy"] for row in rows]
    treatment_forgetting = [row["treatment"]["forgetting_accuracy"] for row in rows]
    retention_gain = [row["effects"]["retention_gain"] for row in rows]
    relative_reduction = [row["effects"]["relative_forgetting_reduction"] for row in rows]
    b_delta = [row["effects"]["b_accuracy_delta"] for row in rows]

    integrity_pass = all(
        all(v is True for v in row["integrity"].values())
        for row in rows
    )
    per_seed_pass = all(row["per_seed_generalization_gate_pass"] for row in rows)
    relative_defined = all(v is not None for v in relative_reduction)

    mean_retention_pass = statistics.fmean(retention_gain) >= RETENTION_GAIN_MEAN_MIN
    mean_relative_pass = (
        relative_defined
        and statistics.fmean([float(v) for v in relative_reduction])
        >= RELATIVE_FORGETTING_REDUCTION_MEAN_MIN
    )
    mean_plasticity_pass = (
        statistics.fmean(treatment_b) >= TREATMENT_B_ACCURACY_MEAN_MIN
    )

    passed = (
        integrity_pass
        and per_seed_pass
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
            "control_b_after_b_accuracy": _stats(control_b),
            "treatment_b_after_b_accuracy": _stats(treatment_b),
            "control_forgetting_accuracy": _stats(control_forgetting),
            "treatment_forgetting_accuracy": _stats(treatment_forgetting),
            "retention_gain": _stats(retention_gain),
            "relative_forgetting_reduction": (
                _stats([float(v) for v in relative_reduction])
                if relative_defined else None
            ),
            "b_accuracy_delta": _stats(b_delta),
        },
        "gates": {
            "integrity_pass": integrity_pass,
            "per_seed_gate_pass": per_seed_pass,
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
    anchors = _load_anchors()

    family_results: list[dict[str, Any]] = []
    if anchors["valid"]:
        family_results = [evaluate_family(family, config) for family in FAMILIES]

    if not anchors["valid"]:
        status = "REVISE"
        verdict = "GENERALIZATION_ANCHOR_INVALID"
    else:
        integrity_valid = all(
            result["gates"]["integrity_pass"] for result in family_results
        )
        if not integrity_valid:
            status = "REVISE"
            verdict = "GENERALIZATION_CONTRAST_INVALID"
        else:
            passed = sum(1 for result in family_results if result["pass"])
            if passed == len(FAMILIES):
                status = "PASS"
                verdict = "REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS"
            elif passed == 1:
                status = "PARTIAL"
                verdict = "REPLAY_GENERALIZATION_PARTIAL"
            else:
                status = "FAIL"
                verdict = "REPLAY_DOES_NOT_GENERALIZE"

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-5.2",
        "status": status,
        "verdict": verdict,
        "families": list(FAMILIES),
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
        "gates": {
            "control_b_accuracy_min_per_seed": CONTROL_B_ACCURACY_MIN,
            "control_forgetting_min_per_seed": CONTROL_FORGETTING_MIN,
            "treatment_b_accuracy_min_per_seed": TREATMENT_B_ACCURACY_MIN,
            "retention_gain_direction_per_seed": "strictly_positive",
            "retention_gain_mean_min_per_family": RETENTION_GAIN_MEAN_MIN,
            "relative_forgetting_reduction_mean_min_per_family": RELATIVE_FORGETTING_REDUCTION_MEAN_MIN,
            "treatment_b_accuracy_mean_min_per_family": TREATMENT_B_ACCURACY_MEAN_MIN,
        },
        "historical_anchors": anchors,
        "family_results": family_results,
        "integrity": {
            "historical_anchors_valid": anchors["valid"],
            "expected_families_exact": [r["family"] for r in family_results] == list(FAMILIES)
                if family_results else False,
            "expected_final_seeds_exact": all(
                r["seeds"] == list(FINAL_SEEDS) for r in family_results
            ) if family_results else False,
            "cross_family_rescue_allowed": False,
            "model_architecture_changed": False,
            "replay_ratio_search_performed": False,
            "family_specific_adaptation": False,
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
    parser = argparse.ArgumentParser(description="Run frozen KCL-5.2 replay generalization")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl52_summary.json",
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
