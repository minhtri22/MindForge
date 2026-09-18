"""KCL-5.1: reconstruct a second unseen CL substrate without replay.

Protocol: docs/research/kernel-continual-learning/kcl51-protocol.md
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any

import torch

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    evaluate,
    independent_run,
    optimizer_for,
    parameter_count,
    train_stage,
)


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl51-protocol.md")
KCL5_EVIDENCE = Path("experiments/kernel_cl/results/kcl5_summary.json")

CANDIDATE_ORDER = (
    "U3_MIXED_POSITION",
    "U4_DISJOINT_OUTPUT_PREFIX",
    "U5_AFFINE_PREFIX_ALT",
)
QUALIFICATION_SEEDS = (1212, 1414)

INDEPENDENT_ACCURACY_MIN = 0.95
SEQUENTIAL_ACQUISITION_MIN = 0.95
FORGETTING_MIN = 0.50
CONTROL_DRIFT_ABS_MAX = 0.10


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _load_kcl5_anchor() -> dict[str, Any]:
    raw = json.loads(KCL5_EVIDENCE.read_text(encoding="utf-8"))
    qualification = {
        item["family"]: item["qualified"]
        for item in raw.get("qualification", [])
    }
    valid = (
        raw.get("status") == "FAIL"
        and raw.get("verdict") == "UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED"
        and qualification.get("U1_AFFINE_PREFIX") is True
        and qualification.get("U2_STRIDE_SUFFIX") is False
    )
    return {
        "valid": valid,
        "kcl5_status": raw.get("status"),
        "kcl5_verdict": raw.get("verdict"),
        "u1_qualified": qualification.get("U1_AFFINE_PREFIX"),
        "u2_qualified": qualification.get("U2_STRIDE_SUFFIX"),
        "sha256": _sha256(KCL5_EVIDENCE),
    }


def candidate_tasks(
    candidate: str,
    config: KCL1Config,
) -> tuple[tuple[torch.Tensor, torch.Tensor], tuple[torch.Tensor, torch.Tensor]]:
    if config.relations != 24:
        raise ValueError("KCL-5.1 frozen protocol requires 24 relations")

    keys = torch.arange(10, 34, dtype=torch.long)
    i = torch.arange(24, dtype=torch.long)

    if candidate == "U3_MIXED_POSITION":
        a_index = (17 * i + 4) % 24
        b_index = (19 * i + 7) % 24
        input_a = torch.stack([torch.full_like(keys, 8), keys], dim=1)
        input_b = torch.stack([keys, torch.full_like(keys, 9)], dim=1)
        values_a = 40 + a_index
        values_b = 40 + b_index

    elif candidate == "U4_DISJOINT_OUTPUT_PREFIX":
        a_index = (5 * i + 9) % 24
        b_index = (7 * i + 11) % 24
        input_a = torch.stack([torch.full_like(keys, 10), keys], dim=1)
        input_b = torch.stack([torch.full_like(keys, 11), keys], dim=1)
        values_a = 40 + a_index
        values_b = 64 + b_index

    elif candidate == "U5_AFFINE_PREFIX_ALT":
        a_index = (17 * i + 13) % 24
        b_index = (23 * i + 6) % 24
        input_a = torch.stack([torch.full_like(keys, 12), keys], dim=1)
        input_b = torch.stack([torch.full_like(keys, 13), keys], dim=1)
        values_a = 40 + a_index
        values_b = 40 + b_index

    else:
        raise ValueError(f"unknown KCL-5.1 candidate: {candidate}")

    if int(max(values_a.max(), values_b.max())) >= config.vocab_size:
        raise ValueError("KCL-5.1 frozen vocabulary is too small")

    return (input_a, values_a), (input_b, values_b)


def _sequential_untreated(
    candidate: str,
    seed: int,
    config: KCL1Config,
) -> dict[str, Any]:
    task_a, task_b = candidate_tasks(candidate, config)
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

    return {
        "a_after_a": a_after_a,
        "a_after_b": a_after_b,
        "b_after_b": b_after_b,
        "a_after_a2_control": a_after_a2,
        "forgetting_accuracy": a_after_a["accuracy"] - a_after_b["accuracy"],
        "control_drift_accuracy": a_after_a["accuracy"] - a_after_a2["accuracy"],
    }


def _seed_pass(result: dict[str, Any]) -> bool:
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
        and result["independent_a"]["accuracy"] >= INDEPENDENT_ACCURACY_MIN
        and result["independent_b"]["accuracy"] >= INDEPENDENT_ACCURACY_MIN
        and seq["a_after_a"]["accuracy"] >= SEQUENTIAL_ACQUISITION_MIN
        and seq["b_after_b"]["accuracy"] >= SEQUENTIAL_ACQUISITION_MIN
        and seq["forgetting_accuracy"] >= FORGETTING_MIN
        and abs(seq["control_drift_accuracy"]) <= CONTROL_DRIFT_ABS_MAX
    )


def qualify_candidate(candidate: str, config: KCL1Config) -> dict[str, Any]:
    task_a, task_b = candidate_tasks(candidate, config)
    per_seed: list[dict[str, Any]] = []

    for seed in QUALIFICATION_SEEDS:
        row = {
            "seed": seed,
            "independent_a": independent_run(
                task_a, config=config, seed=seed, stream_offset=17
            ),
            "independent_b": independent_run(
                task_b, config=config, seed=seed, stream_offset=31
            ),
            "sequential": _sequential_untreated(candidate, seed, config),
        }
        row["pass"] = _seed_pass(row)
        per_seed.append(row)

    return {
        "candidate": candidate,
        "seeds": list(QUALIFICATION_SEEDS),
        "per_seed": per_seed,
        "qualified": all(row["pass"] for row in per_seed),
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    anchor = _load_kcl5_anchor()

    evaluated: list[dict[str, Any]] = []
    selected: str | None = None

    if anchor["valid"]:
        for candidate in CANDIDATE_ORDER:
            outcome = qualify_candidate(candidate, config)
            evaluated.append(outcome)
            if outcome["qualified"]:
                selected = candidate
                break

    if not anchor["valid"]:
        status = "REVISE"
        verdict = "SUBSTRATE_RECONSTRUCTION_INVALID"
    elif selected is not None:
        status = "PASS"
        verdict = "SECOND_UNSEEN_SUBSTRATE_ESTABLISHED"
    else:
        status = "STOP"
        verdict = "UNSEEN_GENERALIZATION_BENCHMARK_NOT_ESTABLISHED"

    model = build_model(config, QUALIFICATION_SEEDS[0])
    return {
        "experiment": "KCL-5.1",
        "status": status,
        "verdict": verdict,
        "candidate_order": list(CANDIDATE_ORDER),
        "qualification_seeds": list(QUALIFICATION_SEEDS),
        "selected_candidate": selected,
        "evaluated_candidates": [row["candidate"] for row in evaluated],
        "candidate_results": evaluated,
        "historical_anchor": anchor,
        "config": config.__dict__,
        "gates": {
            "independent_accuracy_min": INDEPENDENT_ACCURACY_MIN,
            "sequential_acquisition_min": SEQUENTIAL_ACQUISITION_MIN,
            "forgetting_min": FORGETTING_MIN,
            "control_drift_abs_max": CONTROL_DRIFT_ABS_MAX,
        },
        "integrity": {
            "historical_anchor_valid": anchor["valid"],
            "first_pass_selection_rule": True,
            "model_architecture_changed": False,
            "candidate_pool_extended_after_outcome": False,
            "replay_calls": 0,
            "treatment_runs": 0,
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
            "kcl52_started": False,
            "kcl6_started": False,
            "replay_executed": False,
            "challenger_started": False,
            "reasoning_work": False,
            "external_api_calls": 0,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen KCL-5.1 substrate reconstruction")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl51_summary.json",
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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
