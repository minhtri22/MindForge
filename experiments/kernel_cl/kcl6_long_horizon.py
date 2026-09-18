"""KCL-6: four-task long-horizon stress with fixed replay compute.

Protocol: docs/research/kernel-continual-learning/kcl6-protocol.md
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


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6-protocol.md")
KCL52_EVIDENCE = Path("experiments/kernel_cl/results/kcl52_summary.json")

TASK_ORDER = ("T1_U1_A", "T2_U1_B", "T3_U3_A", "T4_U3_B")
FINAL_SEEDS = (2323, 2525, 2727, 2929, 3131)

CONTROL_CURRENT_PER_BATCH = 16
TREATMENT_CURRENT_PER_BATCH = 15
TREATMENT_REPLAY_PER_BATCH = 1
REPLAY_FRACTION = 1 / 16

CURRENT_TASK_ACCURACY_MIN = 0.95
FINAL_WORST_PRIOR_ACCURACY_MIN = 0.25
FINAL_MEAN_PRIOR_ACCURACY_MIN_PER_SEED = 0.50
FINAL_MEAN_PRIOR_ACCURACY_MEAN_MIN = 0.60
FINAL_RETENTION_GAIN_MEAN_MIN = 0.30
FINAL_WORST_PRIOR_ACCURACY_MEAN_MIN = 0.30
STABILITY_RATIO_MIN = 0.50


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


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL52_EVIDENCE.read_text(encoding="utf-8"))
    families = raw.get("families")
    valid = (
        raw.get("status") == "PASS"
        and raw.get("verdict") == "REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS"
        and families == ["U1_AFFINE_PREFIX", "U3_MIXED_POSITION"]
        and abs(float(raw["replay"]["fraction"]) - REPLAY_FRACTION) < 1e-12
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "families": families,
        "replay_fraction": raw.get("replay", {}).get("fraction"),
        "sha256": _sha256(KCL52_EVIDENCE),
    }


def task_sequence(
    config: KCL1Config,
) -> list[tuple[str, tuple[torch.Tensor, torch.Tensor]]]:
    u1_a, u1_b = kcl5_tasks("U1_AFFINE_PREFIX", config)
    u3_a, u3_b = kcl51_tasks("U3_MIXED_POSITION", config)
    return [
        ("T1_U1_A", u1_a),
        ("T2_U1_B", u1_b),
        ("T3_U3_A", u3_a),
        ("T4_U3_B", u3_b),
    ]


def replay_task_index(step: int, previous_task_count: int) -> int:
    if previous_task_count <= 0:
        raise ValueError("previous_task_count must be positive")
    return step % previous_task_count


def logical_task_storage(task: tuple[torch.Tensor, torch.Tensor]) -> dict[str, int]:
    x, y = task
    examples = int(len(y))
    tensor_bytes = int(x.numel() * x.element_size() + y.numel() * y.element_size())
    return {"examples": examples, "tensor_bytes": tensor_bytes}


def _replay_stage(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    previous_tasks: list[tuple[torch.Tensor, torch.Tensor]],
    current_task: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
    stage_index: int,
) -> dict[str, Any]:
    if not previous_tasks:
        raise ValueError("KCL-6 replay stage requires at least one previous task")

    current_x, current_y = current_task
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage_index + 101)

    replay_gens: list[torch.Generator] = []
    for task_index in range(len(previous_tasks)):
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed + 1000 * stage_index + 503 + 37 * task_index)
        replay_gens.append(gen)

    replay_counts = [0 for _ in previous_tasks]

    model.train()
    for step in range(steps):
        idx_current = torch.randint(
            0,
            len(current_y),
            (TREATMENT_CURRENT_PER_BATCH,),
            generator=current_gen,
        )

        replay_source = replay_task_index(step, len(previous_tasks))
        replay_counts[replay_source] += 1
        replay_x, replay_y = previous_tasks[replay_source]
        idx_replay = torch.randint(
            0,
            len(replay_y),
            (TREATMENT_REPLAY_PER_BATCH,),
            generator=replay_gens[replay_source],
        )

        x = torch.cat([current_x[idx_current], replay_x[idx_replay]], dim=0)
        y = torch.cat([current_y[idx_current], replay_y[idx_replay]], dim=0)

        logits = model(x)[:, -1, :]
        loss = F.cross_entropy(logits, y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-6 treatment loss")

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    return {
        "previous_task_count": len(previous_tasks),
        "replay_counts_by_previous_task": replay_counts,
        "total_replay_examples": sum(replay_counts),
        "total_current_examples": steps * TREATMENT_CURRENT_PER_BATCH,
        "total_processed_examples": steps
        * (TREATMENT_CURRENT_PER_BATCH + TREATMENT_REPLAY_PER_BATCH),
    }


def _evaluate_learned(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    learned_count: int,
) -> dict[str, dict[str, float]]:
    return {
        name: evaluate(model, task)
        for name, task in tasks[:learned_count]
    }


def _mean_prior_accuracy(
    matrix: dict[str, dict[str, dict[str, float]]],
    stage_name: str,
    prior_task_names: list[str],
) -> float:
    return statistics.fmean(
        matrix[stage_name][task_name]["accuracy"]
        for task_name in prior_task_names
    )


def run_seed(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    task_names = [name for name, _ in tasks]

    base_model = build_model(config, seed)
    base_optimizer = optimizer_for(base_model, config)

    # T1 is learned once, before the paired fork.
    train_stage(
        base_model,
        base_optimizer,
        tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )
    t1_eval = evaluate(base_model, tasks[0][1])

    control_model = copy.deepcopy(base_model)
    control_optimizer = optimizer_for(control_model, config)
    control_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    treatment_model = copy.deepcopy(base_model)
    treatment_optimizer = optimizer_for(treatment_model, config)
    treatment_optimizer.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    post_t1_model_state_equal = all(
        torch.equal(control_model.state_dict()[name], treatment_model.state_dict()[name])
        for name in control_model.state_dict()
    )
    post_t1_optimizer_state_equal = _deep_equal(
        control_optimizer.state_dict(), treatment_optimizer.state_dict()
    )

    control_matrix: dict[str, dict[str, dict[str, float]]] = {
        "after_T1": {task_names[0]: t1_eval}
    }
    treatment_matrix: dict[str, dict[str, dict[str, float]]] = {
        "after_T1": {task_names[0]: t1_eval}
    }

    control_learning_baseline = {task_names[0]: t1_eval["accuracy"]}
    treatment_learning_baseline = {task_names[0]: t1_eval["accuracy"]}

    replay_stage_accounting: dict[str, Any] = {}

    for stage_idx in range(1, len(tasks)):
        stage_number = stage_idx + 1
        stage_name = f"after_T{stage_number}"
        current_name, current_task = tasks[stage_idx]

        train_stage(
            control_model,
            control_optimizer,
            current_task,
            steps=config.stage_steps,
            batch_size=CONTROL_CURRENT_PER_BATCH,
            seed=seed + 1000 * stage_number + 307,
        )

        previous_task_data = [task for _, task in tasks[:stage_idx]]
        accounting = _replay_stage(
            treatment_model,
            treatment_optimizer,
            previous_task_data,
            current_task,
            steps=config.stage_steps,
            seed=seed,
            stage_index=stage_number,
        )
        replay_stage_accounting[stage_name] = accounting

        control_matrix[stage_name] = _evaluate_learned(
            control_model, tasks, stage_idx + 1
        )
        treatment_matrix[stage_name] = _evaluate_learned(
            treatment_model, tasks, stage_idx + 1
        )

        control_learning_baseline[current_name] = control_matrix[stage_name][current_name][
            "accuracy"
        ]
        treatment_learning_baseline[current_name] = treatment_matrix[stage_name][
            current_name
        ]["accuracy"]

    final_stage = "after_T4"
    prior_names = task_names[:3]

    control_final_prior = [
        control_matrix[final_stage][name]["accuracy"] for name in prior_names
    ]
    treatment_final_prior = [
        treatment_matrix[final_stage][name]["accuracy"] for name in prior_names
    ]
    per_task_gain = {
        name: treatment_matrix[final_stage][name]["accuracy"]
        - control_matrix[final_stage][name]["accuracy"]
        for name in prior_names
    }

    control_final_forgetting = {
        name: control_learning_baseline[name]
        - control_matrix[final_stage][name]["accuracy"]
        for name in prior_names
    }
    treatment_final_forgetting = {
        name: treatment_learning_baseline[name]
        - treatment_matrix[final_stage][name]["accuracy"]
        for name in prior_names
    }

    treatment_prior_after_t2 = _mean_prior_accuracy(
        treatment_matrix, "after_T2", [task_names[0]]
    )
    treatment_prior_after_t3 = _mean_prior_accuracy(
        treatment_matrix, "after_T3", task_names[:2]
    )
    treatment_prior_after_t4 = statistics.fmean(treatment_final_prior)

    control_current_accuracies = {
        "T1": t1_eval["accuracy"],
        "T2": control_matrix["after_T2"][task_names[1]]["accuracy"],
        "T3": control_matrix["after_T3"][task_names[2]]["accuracy"],
        "T4": control_matrix["after_T4"][task_names[3]]["accuracy"],
    }
    treatment_current_accuracies = {
        "T1": t1_eval["accuracy"],
        "T2": treatment_matrix["after_T2"][task_names[1]]["accuracy"],
        "T3": treatment_matrix["after_T3"][task_names[2]]["accuracy"],
        "T4": treatment_matrix["after_T4"][task_names[3]]["accuracy"],
    }

    substrate_valid = all(
        value >= CURRENT_TASK_ACCURACY_MIN
        for value in control_current_accuracies.values()
    )
    plasticity_valid = all(
        value >= CURRENT_TASK_ACCURACY_MIN
        for value in treatment_current_accuracies.values()
    )
    directional_gain = all(value > 0 for value in per_task_gain.values())
    worst_prior_floor = min(treatment_final_prior) >= FINAL_WORST_PRIOR_ACCURACY_MIN
    mean_prior_floor = (
        statistics.fmean(treatment_final_prior)
        >= FINAL_MEAN_PRIOR_ACCURACY_MIN_PER_SEED
    )
    final_current_task_gate = (
        treatment_matrix[final_stage][task_names[3]]["accuracy"]
        >= CURRENT_TASK_ACCURACY_MIN
    )
    stability_gate = (
        treatment_prior_after_t4
        >= STABILITY_RATIO_MIN * treatment_prior_after_t2
    )

    all_scalar_values: list[float] = []
    for matrix in (control_matrix, treatment_matrix):
        for stage in matrix.values():
            for metric in stage.values():
                all_scalar_values.extend([metric["accuracy"], metric["loss"]])
    all_scalar_values.extend(per_task_gain.values())
    all_scalar_values.extend(control_final_forgetting.values())
    all_scalar_values.extend(treatment_final_forgetting.values())
    all_metrics_finite = all(math.isfinite(float(v)) for v in all_scalar_values)

    storage_per_task = logical_task_storage(tasks[0][1])
    replay_storage = {
        "per_task_examples": storage_per_task["examples"],
        "per_task_tensor_bytes": storage_per_task["tensor_bytes"],
        "after_T1_total_learned_examples": 24,
        "after_T2_total_learned_examples": 48,
        "after_T3_total_learned_examples": 72,
        "after_T4_total_learned_examples": 96,
        "T2_replay_source_examples": 24,
        "T3_replay_source_examples": 48,
        "T4_replay_source_examples": 72,
        "T4_replay_source_tensor_bytes": 3 * storage_per_task["tensor_bytes"],
    }

    return {
        "seed": seed,
        "task_order": task_names,
        "control_matrix": control_matrix,
        "treatment_matrix": treatment_matrix,
        "learning_baselines": {
            "control": control_learning_baseline,
            "treatment": treatment_learning_baseline,
        },
        "current_task_accuracies": {
            "control": control_current_accuracies,
            "treatment": treatment_current_accuracies,
        },
        "final": {
            "control_prior_accuracies": dict(zip(prior_names, control_final_prior)),
            "treatment_prior_accuracies": dict(zip(prior_names, treatment_final_prior)),
            "retention_gain_by_prior_task": per_task_gain,
            "control_forgetting_by_prior_task": control_final_forgetting,
            "treatment_forgetting_by_prior_task": treatment_final_forgetting,
            "control_mean_prior_accuracy": statistics.fmean(control_final_prior),
            "treatment_mean_prior_accuracy": statistics.fmean(treatment_final_prior),
            "treatment_worst_prior_accuracy": min(treatment_final_prior),
            "control_mean_prior_forgetting": statistics.fmean(
                control_final_forgetting.values()
            ),
            "treatment_mean_prior_forgetting": statistics.fmean(
                treatment_final_forgetting.values()
            ),
            "mean_retention_gain": statistics.fmean(per_task_gain.values()),
            "control_average_accuracy_all_tasks": statistics.fmean(
                control_matrix[final_stage][name]["accuracy"] for name in task_names
            ),
            "treatment_average_accuracy_all_tasks": statistics.fmean(
                treatment_matrix[final_stage][name]["accuracy"] for name in task_names
            ),
            "treatment_T4_accuracy": treatment_matrix[final_stage][task_names[3]][
                "accuracy"
            ],
        },
        "retention_trajectory": {
            "treatment_mean_prior_after_T2": treatment_prior_after_t2,
            "treatment_mean_prior_after_T3": treatment_prior_after_t3,
            "treatment_mean_prior_after_T4": treatment_prior_after_t4,
            "final_over_T2_ratio": (
                treatment_prior_after_t4 / treatment_prior_after_t2
                if treatment_prior_after_t2 > 0
                else None
            ),
        },
        "replay_stage_accounting": replay_stage_accounting,
        "replay_storage": replay_storage,
        "gates": {
            "substrate_valid": substrate_valid,
            "treatment_plasticity_valid": plasticity_valid,
            "directional_gain_all_prior_tasks": directional_gain,
            "worst_prior_floor_pass": worst_prior_floor,
            "mean_prior_floor_pass": mean_prior_floor,
            "final_current_task_pass": final_current_task_gate,
            "stability_gate_pass": stability_gate,
        },
        "integrity": {
            "all_metrics_finite": all_metrics_finite,
            "post_t1_model_state_equal": post_t1_model_state_equal,
            "post_t1_optimizer_state_equal": post_t1_optimizer_state_equal,
            "equal_optimizer_steps_per_stage": True,
            "equal_batch_size_per_stage": (
                CONTROL_CURRENT_PER_BATCH
                == TREATMENT_CURRENT_PER_BATCH + TREATMENT_REPLAY_PER_BATCH
                == config.batch_size
            ),
            "fixed_total_replay_items_per_update": TREATMENT_REPLAY_PER_BATCH == 1,
        },
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    anchor = _load_anchor()

    per_seed: list[dict[str, Any]] = []
    if anchor["valid"]:
        per_seed = [run_seed(seed, config) for seed in FINAL_SEEDS]

    if not anchor["valid"]:
        status = "REVISE"
        verdict = "LONG_HORIZON_CONTRAST_INVALID"
    else:
        integrity_valid = all(
            all(value is True for value in row["integrity"].values())
            for row in per_seed
        )
        substrate_valid = all(row["gates"]["substrate_valid"] for row in per_seed)
        plasticity_valid = all(
            row["gates"]["treatment_plasticity_valid"]
            and row["gates"]["final_current_task_pass"]
            for row in per_seed
        )

        final_mean_prior = [
            row["final"]["treatment_mean_prior_accuracy"] for row in per_seed
        ]
        final_mean_gain = [
            row["final"]["mean_retention_gain"] for row in per_seed
        ]
        final_worst_prior = [
            row["final"]["treatment_worst_prior_accuracy"] for row in per_seed
        ]
        final_t4 = [
            row["final"]["treatment_T4_accuracy"] for row in per_seed
        ]

        per_seed_retention_valid = all(
            row["gates"]["directional_gain_all_prior_tasks"]
            and row["gates"]["worst_prior_floor_pass"]
            and row["gates"]["mean_prior_floor_pass"]
            and row["gates"]["stability_gate_pass"]
            for row in per_seed
        )

        aggregate_valid = (
            statistics.fmean(final_mean_prior)
            >= FINAL_MEAN_PRIOR_ACCURACY_MEAN_MIN
            and statistics.fmean(final_mean_gain)
            >= FINAL_RETENTION_GAIN_MEAN_MIN
            and statistics.fmean(final_worst_prior)
            >= FINAL_WORST_PRIOR_ACCURACY_MEAN_MIN
            and statistics.fmean(final_t4)
            >= CURRENT_TASK_ACCURACY_MIN
        )

        if not integrity_valid:
            status = "REVISE"
            verdict = "LONG_HORIZON_CONTRAST_INVALID"
        elif not substrate_valid:
            status = "REVISE"
            verdict = "LONG_HORIZON_SUBSTRATE_INVALID"
        elif not plasticity_valid:
            status = "FAIL"
            verdict = "LONG_HORIZON_REPLAY_IMPAIRS_PLASTICITY"
        elif per_seed_retention_valid and aggregate_valid:
            status = "PASS"
            verdict = "FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON"
        else:
            status = "FAIL"
            verdict = "FIXED_BUDGET_REPLAY_LONG_HORIZON_LIMIT_REACHED"

    aggregates: dict[str, Any] = {}
    if per_seed:
        aggregates = {
            "treatment_final_mean_prior_accuracy": _stats([
                row["final"]["treatment_mean_prior_accuracy"] for row in per_seed
            ]),
            "control_final_mean_prior_accuracy": _stats([
                row["final"]["control_mean_prior_accuracy"] for row in per_seed
            ]),
            "treatment_final_worst_prior_accuracy": _stats([
                row["final"]["treatment_worst_prior_accuracy"] for row in per_seed
            ]),
            "mean_retention_gain": _stats([
                row["final"]["mean_retention_gain"] for row in per_seed
            ]),
            "treatment_final_T4_accuracy": _stats([
                row["final"]["treatment_T4_accuracy"] for row in per_seed
            ]),
            "treatment_final_average_accuracy_all_tasks": _stats([
                row["final"]["treatment_average_accuracy_all_tasks"] for row in per_seed
            ]),
            "control_final_average_accuracy_all_tasks": _stats([
                row["final"]["control_average_accuracy_all_tasks"] for row in per_seed
            ]),
            "treatment_final_mean_prior_forgetting": _stats([
                row["final"]["treatment_mean_prior_forgetting"] for row in per_seed
            ]),
            "control_final_mean_prior_forgetting": _stats([
                row["final"]["control_mean_prior_forgetting"] for row in per_seed
            ]),
            "stability_final_over_T2_ratio": _stats([
                row["retention_trajectory"]["final_over_T2_ratio"] for row in per_seed
            ]),
        }

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-6",
        "status": status,
        "verdict": verdict,
        "task_order": list(TASK_ORDER),
        "final_seeds": list(FINAL_SEEDS),
        "config": config.__dict__,
        "replay": {
            "fraction": REPLAY_FRACTION,
            "current_examples_per_batch": TREATMENT_CURRENT_PER_BATCH,
            "replay_examples_per_batch": TREATMENT_REPLAY_PER_BATCH,
            "allocation_rule": "round_robin_across_all_previous_tasks",
            "budget_scales_with_task_count": False,
            "storage_scales_with_task_count": True,
        },
        "gates": {
            "current_task_accuracy_min": CURRENT_TASK_ACCURACY_MIN,
            "final_worst_prior_accuracy_min_per_seed": FINAL_WORST_PRIOR_ACCURACY_MIN,
            "final_mean_prior_accuracy_min_per_seed": FINAL_MEAN_PRIOR_ACCURACY_MIN_PER_SEED,
            "final_mean_prior_accuracy_mean_min": FINAL_MEAN_PRIOR_ACCURACY_MEAN_MIN,
            "final_retention_gain_mean_min": FINAL_RETENTION_GAIN_MEAN_MIN,
            "final_worst_prior_accuracy_mean_min": FINAL_WORST_PRIOR_ACCURACY_MEAN_MIN,
            "stability_final_over_T2_ratio_min": STABILITY_RATIO_MIN,
        },
        "historical_anchor": anchor,
        "per_seed": per_seed,
        "aggregates": aggregates,
        "integrity": {
            "historical_anchor_valid": anchor["valid"],
            "expected_task_order": list(TASK_ORDER),
            "expected_final_seeds_exact": [row["seed"] for row in per_seed] == list(FINAL_SEEDS)
            if per_seed else False,
            "model_architecture_changed": False,
            "replay_ratio_search_performed": False,
            "replay_budget_increased_with_task_count": False,
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
            "kcl7_started": False,
            "challenger_started": False,
            "reasoning_work": False,
            "external_api_calls": 0,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen KCL-6 long-horizon stress")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl6_summary.json",
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
