"""KCL-3: causal bounded-replay treatment on the frozen KCL substrate.

Protocol: docs/research/kernel-continual-learning/kcl3-protocol.md
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


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl3-protocol.md")
CANDIDATE = "C1_TASK_PREFIX_CYCLIC"
CONTROL_B_PER_BATCH = 16
TREATMENT_B_PER_BATCH = 14
TREATMENT_A_PER_BATCH = 2
REPLAY_FRACTION = TREATMENT_A_PER_BATCH / (TREATMENT_A_PER_BATCH + TREATMENT_B_PER_BATCH)

RETENTION_GAIN_PER_SEED_MIN = 0.30
RETENTION_GAIN_MEAN_MIN = 0.50
TREATMENT_FORGETTING_MEAN_MAX = 0.50
TREATMENT_B_ACCURACY_MIN = 0.95


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


def _mixed_replay_stage(
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
    generator_a.manual_seed(seed + 401)
    generator_b.manual_seed(seed + 503)

    model.train()
    for _ in range(steps):
        idx_b = torch.randint(
            0, len(b_y), (TREATMENT_B_PER_BATCH,), generator=generator_b
        )
        idx_a = torch.randint(
            0, len(a_y), (TREATMENT_A_PER_BATCH,), generator=generator_a
        )
        x = torch.cat([b_x[idx_b], a_x[idx_a]], dim=0)
        y = torch.cat([b_y[idx_b], a_y[idx_a]], dim=0)

        logits = model(x)[:, -1, :]
        loss = F.cross_entropy(logits, y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-3 treatment loss")
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

    treatment_model = copy.deepcopy(base_model)
    treatment_optimizer = optimizer_for(treatment_model, config)
    treatment_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    post_a_state_equal = all(
        torch.equal(control_model.state_dict()[name], treatment_model.state_dict()[name])
        for name in control_model.state_dict()
    )
    optimizer_state_equal = json.dumps(
        control_optimizer.state_dict(), default=str, sort_keys=True
    ) == json.dumps(
        treatment_optimizer.state_dict(), default=str, sort_keys=True
    )

    train_stage(
        control_model,
        control_optimizer,
        task_b,
        steps=config.stage_steps,
        batch_size=CONTROL_B_PER_BATCH,
        seed=seed + 307,
    )
    _mixed_replay_stage(
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
    b_delta = treatment_b["accuracy"] - control_b["accuracy"]

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
        b_delta,
    ]
    finite = all(math.isfinite(float(value)) for value in values)

    seed_pass = (
        finite
        and post_a_state_equal
        and optimizer_state_equal
        and treatment_b["accuracy"] >= TREATMENT_B_ACCURACY_MIN
        and retention_gain >= RETENTION_GAIN_PER_SEED_MIN
        and treatment_a["accuracy"] > control_a["accuracy"]
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
            "b_examples_per_batch": TREATMENT_B_PER_BATCH,
            "a_replay_examples_per_batch": TREATMENT_A_PER_BATCH,
            "replay_fraction": REPLAY_FRACTION,
        },
        "effects": {
            "retention_gain": retention_gain,
            "forgetting_reduction": forgetting_reduction,
            "b_accuracy_delta": b_delta,
        },
        "integrity": {
            "all_metrics_finite": finite,
            "post_a_model_state_equal": post_a_state_equal,
            "post_a_optimizer_state_equal": optimizer_state_equal,
            "equal_b_stage_optimizer_steps": True,
            "equal_b_stage_batch_size": (
                CONTROL_B_PER_BATCH
                == TREATMENT_B_PER_BATCH + TREATMENT_A_PER_BATCH
                == config.batch_size
            ),
        },
        "pass": seed_pass,
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    per_seed = [run_seed(seed, config) for seed in FINAL_SEEDS]

    retention = [row["effects"]["retention_gain"] for row in per_seed]
    control_forgetting = [row["control"]["forgetting_accuracy"] for row in per_seed]
    treatment_forgetting = [row["treatment"]["forgetting_accuracy"] for row in per_seed]
    control_a = [row["control"]["a_after_b"]["accuracy"] for row in per_seed]
    treatment_a = [row["treatment"]["a_after_b"]["accuracy"] for row in per_seed]
    control_b = [row["control"]["b_after_b"]["accuracy"] for row in per_seed]
    treatment_b = [row["treatment"]["b_after_b"]["accuracy"] for row in per_seed]
    b_delta = [row["effects"]["b_accuracy_delta"] for row in per_seed]

    all_integrity = all(
        all(value is True for value in row["integrity"].values())
        for row in per_seed
    )
    exact_seeds = [row["seed"] for row in per_seed] == list(FINAL_SEEDS)
    plasticity_pass = all(
        row["treatment"]["b_after_b"]["accuracy"] >= TREATMENT_B_ACCURACY_MIN
        for row in per_seed
    )
    per_seed_retention_pass = all(
        row["effects"]["retention_gain"] >= RETENTION_GAIN_PER_SEED_MIN
        for row in per_seed
    )
    directional_pass = all(
        row["treatment"]["a_after_b"]["accuracy"] > row["control"]["a_after_b"]["accuracy"]
        for row in per_seed
    )
    mean_retention_pass = statistics.fmean(retention) >= RETENTION_GAIN_MEAN_MIN
    mean_treatment_forgetting_pass = (
        statistics.fmean(treatment_forgetting) <= TREATMENT_FORGETTING_MEAN_MAX
    )

    passed = (
        all_integrity
        and exact_seeds
        and plasticity_pass
        and per_seed_retention_pass
        and directional_pass
        and mean_retention_pass
        and mean_treatment_forgetting_pass
        and all(row["pass"] for row in per_seed)
    )

    if passed:
        status = "PASS"
        verdict = "BOUNDED_REPLAY_CAUSALLY_REDUCES_FORGETTING"
    elif not all_integrity or not exact_seeds:
        status = "REVISE"
        verdict = "CAUSAL_CONTRAST_INVALID"
    elif not plasticity_pass:
        status = "FAIL"
        verdict = "REPLAY_IMPAIRS_PLASTICITY"
    else:
        status = "FAIL"
        verdict = "REPLAY_EFFECT_INSUFFICIENT"

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-3",
        "status": status,
        "verdict": verdict,
        "candidate": CANDIDATE,
        "seeds": list(FINAL_SEEDS),
        "config": config.__dict__,
        "treatment": {
            "name": "bounded_replay",
            "replay_fraction": REPLAY_FRACTION,
            "a_replay_examples_per_batch": TREATMENT_A_PER_BATCH,
            "b_examples_per_batch": TREATMENT_B_PER_BATCH,
            "total_batch_size": config.batch_size,
            "b_stage_steps": config.stage_steps,
            "total_examples_per_arm_b_stage": config.batch_size * config.stage_steps,
        },
        "gates": {
            "treatment_b_accuracy_min_per_seed": TREATMENT_B_ACCURACY_MIN,
            "retention_gain_min_per_seed": RETENTION_GAIN_PER_SEED_MIN,
            "retention_gain_mean_min": RETENTION_GAIN_MEAN_MIN,
            "treatment_forgetting_mean_max": TREATMENT_FORGETTING_MEAN_MAX,
            "directional_improvement_every_seed": True,
        },
        "per_seed": per_seed,
        "aggregates": {
            "control_a_after_b_accuracy": _stats(control_a),
            "treatment_a_after_b_accuracy": _stats(treatment_a),
            "control_b_after_b_accuracy": _stats(control_b),
            "treatment_b_after_b_accuracy": _stats(treatment_b),
            "control_forgetting_accuracy": _stats(control_forgetting),
            "treatment_forgetting_accuracy": _stats(treatment_forgetting),
            "retention_gain": _stats(retention),
            "b_accuracy_delta": _stats(b_delta),
        },
        "integrity": {
            "expected_seeds_present_exactly_once": exact_seeds,
            "all_pair_integrity_checks_pass": all_integrity,
            "plasticity_gate_pass": plasticity_pass,
            "per_seed_retention_gate_pass": per_seed_retention_pass,
            "directional_consistency_gate_pass": directional_pass,
            "mean_retention_gate_pass": mean_retention_pass,
            "mean_treatment_forgetting_gate_pass": mean_treatment_forgetting_pass,
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
            "external_api_calls": 0,
            "teacher_inference": 0,
            "reasoning_work": False,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
            "alternative_cl_mechanisms": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen MindForge KCL-3 causal replay test")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl3_summary.json",
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
