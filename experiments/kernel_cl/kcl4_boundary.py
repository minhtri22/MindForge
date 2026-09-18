"""KCL-4: characterize the minimum effective replay boundary.

Protocol: docs/research/kernel-continual-learning/kcl4-protocol.md
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
    candidate_tasks,
    evaluate,
    optimizer_for,
    parameter_count,
    train_stage,
)
from experiments.kernel_cl.kcl2_baseline import FINAL_SEEDS


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl4-protocol.md")
KCL2_EVIDENCE = Path("experiments/kernel_cl/results/kcl2_summary.json")
KCL3_EVIDENCE = Path("experiments/kernel_cl/results/kcl3_summary.json")

CANDIDATE = "C1_TASK_PREFIX_CYCLIC"
CONTROL_B_PER_BATCH = 16
LOW_DOSE_B_PER_BATCH = 15
LOW_DOSE_A_PER_BATCH = 1
LOW_DOSE_REPLAY_FRACTION = LOW_DOSE_A_PER_BATCH / (
    LOW_DOSE_A_PER_BATCH + LOW_DOSE_B_PER_BATCH
)

RETENTION_GAIN_PER_SEED_MIN = 0.30
RETENTION_GAIN_MEAN_MIN = 0.50
LOW_DOSE_FORGETTING_MEAN_MAX = 0.50
LOW_DOSE_B_ACCURACY_MIN = 0.95


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


def _load_anchor(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_historical_anchors() -> dict[str, Any]:
    kcl2 = _load_anchor(KCL2_EVIDENCE)
    kcl3 = _load_anchor(KCL3_EVIDENCE)

    kcl2_ok = (
        kcl2.get("status") == "PASS"
        and kcl2.get("verdict") == "UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE"
        and abs(float(kcl2["aggregates"]["forgetting_accuracy"]["mean"]) - 0.975) < 1e-9
    )
    kcl3_ok = (
        kcl3.get("status") == "PASS"
        and kcl3.get("verdict") == "BOUNDED_REPLAY_CAUSALLY_REDUCES_FORGETTING"
        and abs(float(kcl3["treatment"]["replay_fraction"]) - 0.125) < 1e-12
    )
    return {
        "kcl2_anchor_valid": kcl2_ok,
        "kcl3_anchor_valid": kcl3_ok,
        "kcl2_sha256": _sha256(KCL2_EVIDENCE),
        "kcl3_sha256": _sha256(KCL3_EVIDENCE),
        "kcl2_verdict": kcl2.get("verdict"),
        "kcl3_verdict": kcl3.get("verdict"),
    }


def _low_dose_stage(
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

    generator_a = torch.Generator(device="cpu")
    generator_b = torch.Generator(device="cpu")
    generator_a.manual_seed(seed + 601)
    generator_b.manual_seed(seed + 701)

    model.train()
    for _ in range(steps):
        idx_b = torch.randint(
            0, len(b_y), (LOW_DOSE_B_PER_BATCH,), generator=generator_b
        )
        idx_a = torch.randint(
            0, len(a_y), (LOW_DOSE_A_PER_BATCH,), generator=generator_a
        )
        x = torch.cat([b_x[idx_b], a_x[idx_a]], dim=0)
        y = torch.cat([b_y[idx_b], a_y[idx_a]], dim=0)

        logits = model(x)[:, -1, :]
        loss = F.cross_entropy(logits, y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-4 low-dose loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


def run_seed(seed: int, config: KCL1Config) -> dict[str, Any]:
    task_a, task_b = candidate_tasks(CANDIDATE, config)

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

    low_model = copy.deepcopy(base_model)
    low_optimizer = optimizer_for(low_model, config)
    low_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    post_a_model_state_equal = all(
        torch.equal(control_model.state_dict()[name], low_model.state_dict()[name])
        for name in control_model.state_dict()
    )

    # Optimizer hyperparameters/state tensors are already cloned from the same
    # source. Equality here is checked structurally instead of serializing tensors.
    control_opt = control_optimizer.state_dict()
    low_opt = low_optimizer.state_dict()
    post_a_optimizer_state_equal = (
        control_opt["param_groups"] == low_opt["param_groups"]
        and control_opt["state"].keys() == low_opt["state"].keys()
        and all(
            all(
                torch.equal(control_opt["state"][key][field], low_opt["state"][key][field])
                if torch.is_tensor(control_opt["state"][key][field])
                else control_opt["state"][key][field] == low_opt["state"][key][field]
                for field in control_opt["state"][key]
            )
            for key in control_opt["state"]
        )
    )

    train_stage(
        control_model,
        control_optimizer,
        task_b,
        steps=config.stage_steps,
        batch_size=CONTROL_B_PER_BATCH,
        seed=seed + 307,
    )
    _low_dose_stage(
        low_model,
        low_optimizer,
        task_a,
        task_b,
        steps=config.stage_steps,
        seed=seed,
    )

    control_a = evaluate(control_model, task_a)
    control_b = evaluate(control_model, task_b)
    low_a = evaluate(low_model, task_a)
    low_b = evaluate(low_model, task_b)

    control_forgetting = a_after_a["accuracy"] - control_a["accuracy"]
    low_forgetting = a_after_a["accuracy"] - low_a["accuracy"]
    retention_gain = low_a["accuracy"] - control_a["accuracy"]
    forgetting_reduction = control_forgetting - low_forgetting
    b_delta = low_b["accuracy"] - control_b["accuracy"]

    values = [
        a_after_a["accuracy"],
        control_a["accuracy"],
        control_b["accuracy"],
        low_a["accuracy"],
        low_b["accuracy"],
        control_forgetting,
        low_forgetting,
        retention_gain,
        forgetting_reduction,
        b_delta,
    ]
    finite = all(math.isfinite(float(value)) for value in values)

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
        "low_dose": {
            "a_after_b": low_a,
            "b_after_b": low_b,
            "forgetting_accuracy": low_forgetting,
            "b_examples_per_batch": LOW_DOSE_B_PER_BATCH,
            "a_replay_examples_per_batch": LOW_DOSE_A_PER_BATCH,
            "replay_fraction": LOW_DOSE_REPLAY_FRACTION,
        },
        "effects": {
            "retention_gain": retention_gain,
            "forgetting_reduction": forgetting_reduction,
            "b_accuracy_delta": b_delta,
        },
        "integrity": {
            "all_metrics_finite": finite,
            "post_a_model_state_equal": post_a_model_state_equal,
            "post_a_optimizer_state_equal": post_a_optimizer_state_equal,
            "equal_b_stage_optimizer_steps": True,
            "equal_b_stage_batch_size": (
                CONTROL_B_PER_BATCH
                == LOW_DOSE_B_PER_BATCH + LOW_DOSE_A_PER_BATCH
                == config.batch_size
            ),
        },
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    anchors = _validate_historical_anchors()
    config = KCL1Config()
    per_seed = [run_seed(seed, config) for seed in FINAL_SEEDS]

    retention = [row["effects"]["retention_gain"] for row in per_seed]
    control_forgetting = [row["control"]["forgetting_accuracy"] for row in per_seed]
    low_forgetting = [row["low_dose"]["forgetting_accuracy"] for row in per_seed]
    control_a = [row["control"]["a_after_b"]["accuracy"] for row in per_seed]
    low_a = [row["low_dose"]["a_after_b"]["accuracy"] for row in per_seed]
    control_b = [row["control"]["b_after_b"]["accuracy"] for row in per_seed]
    low_b = [row["low_dose"]["b_after_b"]["accuracy"] for row in per_seed]
    b_delta = [row["effects"]["b_accuracy_delta"] for row in per_seed]

    exact_seeds = [row["seed"] for row in per_seed] == list(FINAL_SEEDS)
    pair_integrity = all(
        all(value is True for value in row["integrity"].values())
        for row in per_seed
    )
    anchors_valid = anchors["kcl2_anchor_valid"] and anchors["kcl3_anchor_valid"]

    plasticity_pass = all(
        row["low_dose"]["b_after_b"]["accuracy"] >= LOW_DOSE_B_ACCURACY_MIN
        for row in per_seed
    )
    per_seed_retention_pass = all(
        row["effects"]["retention_gain"] >= RETENTION_GAIN_PER_SEED_MIN
        for row in per_seed
    )
    directional_pass = all(
        row["low_dose"]["a_after_b"]["accuracy"] > row["control"]["a_after_b"]["accuracy"]
        for row in per_seed
    )
    mean_retention_pass = statistics.fmean(retention) >= RETENTION_GAIN_MEAN_MIN
    mean_forgetting_pass = (
        statistics.fmean(low_forgetting) <= LOW_DOSE_FORGETTING_MEAN_MAX
    )

    integrity_valid = exact_seeds and pair_integrity and anchors_valid
    low_dose_effective = (
        integrity_valid
        and plasticity_pass
        and per_seed_retention_pass
        and directional_pass
        and mean_retention_pass
        and mean_forgetting_pass
    )

    if not integrity_valid:
        status = "REVISE"
        verdict = "REVISE_BOUNDARY_CONTRAST_INVALID"
        minimum_proven = None
    elif low_dose_effective:
        status = "PASS"
        verdict = "MINIMUM_EFFECTIVE_REPLAY_BOUNDARY_6_25_PERCENT"
        minimum_proven = 0.0625
    else:
        status = "PASS"
        verdict = "MINIMUM_PROVEN_REPLAY_BOUNDARY_12_5_PERCENT"
        minimum_proven = 0.125

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-4",
        "status": status,
        "verdict": verdict,
        "candidate": CANDIDATE,
        "seeds": list(FINAL_SEEDS),
        "config": config.__dict__,
        "boundary": {
            "batch_size": config.batch_size,
            "zero_replay_anchor": 0.0,
            "tested_low_dose": LOW_DOSE_REPLAY_FRACTION,
            "proven_upper_anchor": 0.125,
            "minimum_positive_representable_dose": 1 / config.batch_size,
            "minimum_proven_effective_dose": minimum_proven,
            "ratio_search_performed": False,
        },
        "historical_anchors": anchors,
        "gates": {
            "low_dose_b_accuracy_min_per_seed": LOW_DOSE_B_ACCURACY_MIN,
            "retention_gain_min_per_seed": RETENTION_GAIN_PER_SEED_MIN,
            "retention_gain_mean_min": RETENTION_GAIN_MEAN_MIN,
            "low_dose_forgetting_mean_max": LOW_DOSE_FORGETTING_MEAN_MAX,
            "directional_improvement_every_seed": True,
        },
        "per_seed": per_seed,
        "aggregates": {
            "control_a_after_b_accuracy": _stats(control_a),
            "low_dose_a_after_b_accuracy": _stats(low_a),
            "control_b_after_b_accuracy": _stats(control_b),
            "low_dose_b_after_b_accuracy": _stats(low_b),
            "control_forgetting_accuracy": _stats(control_forgetting),
            "low_dose_forgetting_accuracy": _stats(low_forgetting),
            "retention_gain": _stats(retention),
            "b_accuracy_delta": _stats(b_delta),
        },
        "effectiveness": {
            "low_dose_effective": low_dose_effective,
            "plasticity_gate_pass": plasticity_pass,
            "per_seed_retention_gate_pass": per_seed_retention_pass,
            "directional_consistency_gate_pass": directional_pass,
            "mean_retention_gate_pass": mean_retention_pass,
            "mean_forgetting_gate_pass": mean_forgetting_pass,
        },
        "integrity": {
            "expected_seeds_present_exactly_once": exact_seeds,
            "all_pair_integrity_checks_pass": pair_integrity,
            "historical_anchors_valid": anchors_valid,
            "model_architecture_changed": False,
            "replay_ratio_search_performed": False,
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
            "kcl5_started": False,
            "external_api_calls": 0,
            "reasoning_work": False,
            "alternative_cl_mechanisms": False,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen MindForge KCL-4 replay boundary test")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl4_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
