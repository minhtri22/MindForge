"""KCL-2: characterize the frozen untreated forgetting baseline.

Protocol: docs/research/kernel-continual-learning/kcl2-protocol.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import subprocess
from pathlib import Path
from typing import Any

import torch

from experiments.kernel_cl.kcl1_substrate import (
    Gates,
    KCL1Config,
    build_model,
    candidate_tasks,
    independent_run,
    parameter_count,
    seed_pass,
    sequential_run,
)


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl2-protocol.md")
CANDIDATE = "C1_TASK_PREFIX_CYCLIC"
FINAL_SEEDS = (101, 202, 303, 707, 909)


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


def _flatten_metrics(result: dict[str, Any]) -> dict[str, float]:
    seq = result["sequential"]
    return {
        "independent_a_accuracy": result["independent_a"]["accuracy"],
        "independent_b_accuracy": result["independent_b"]["accuracy"],
        "a_after_a_accuracy": seq["a_after_a"]["accuracy"],
        "a_after_b_accuracy": seq["a_after_b"]["accuracy"],
        "b_after_b_accuracy": seq["b_after_b"]["accuracy"],
        "a_after_a2_control_accuracy": seq["a_after_a2_control"]["accuracy"],
        "forgetting_accuracy": seq["forgetting_accuracy"],
        "control_drift_accuracy": seq["control_drift_accuracy"],
    }


def run_final_seed(seed: int, config: KCL1Config, gates: Gates) -> dict[str, Any]:
    task_a, task_b = candidate_tasks(CANDIDATE, config)
    result: dict[str, Any] = {
        "seed": seed,
        "independent_a": independent_run(task_a, config=config, seed=seed, stream_offset=17),
        "independent_b": independent_run(task_b, config=config, seed=seed, stream_offset=31),
        "sequential": sequential_run(task_a, task_b, config=config, seed=seed),
    }
    result["pass"] = seed_pass(result, gates)
    return result


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    gates = Gates()
    per_seed = [run_final_seed(seed, config, gates) for seed in FINAL_SEEDS]

    flat = [_flatten_metrics(item) for item in per_seed]
    metric_names = tuple(flat[0])
    aggregates = {
        name: _stats([float(item[name]) for item in flat])
        for name in metric_names
    }

    all_finite = all(
        math.isfinite(float(value))
        for row in flat
        for value in row.values()
    )
    seeds_exact = [item["seed"] for item in per_seed] == list(FINAL_SEEDS)
    mean_forgetting_ok = aggregates["forgetting_accuracy"]["mean"] >= gates.forgetting_min
    max_control_drift_ok = max(abs(item["control_drift_accuracy"]) for item in flat) <= gates.control_drift_abs_max
    passed = (
        seeds_exact
        and all_finite
        and all(item["pass"] for item in per_seed)
        and mean_forgetting_ok
        and max_control_drift_ok
    )

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-2",
        "status": "PASS" if passed else "STOP",
        "verdict": (
            "UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE"
            if passed
            else "UNTREATED_FORGETTING_BASELINE_NOT_REPRODUCIBLE"
        ),
        "candidate": CANDIDATE,
        "final_seeds": list(FINAL_SEEDS),
        "qualification_seeds_reused": False,
        "config": config.__dict__,
        "gates": gates.__dict__,
        "model_parameter_count": parameter_count(model),
        "model_architecture_changed": False,
        "treatment_present": False,
        "per_seed": per_seed,
        "aggregates": aggregates,
        "integrity": {
            "all_metrics_finite": all_finite,
            "expected_seeds_present_exactly_once": seeds_exact,
            "all_seed_gates_pass": all(item["pass"] for item in per_seed),
            "mean_forgetting_gate_pass": mean_forgetting_ok,
            "max_control_drift_gate_pass": max_control_drift_ok,
        },
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
            "external_api_calls": 0,
            "teacher_inference": 0,
            "reasoning_work": False,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen MindForge KCL-2 untreated baseline")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl2_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
