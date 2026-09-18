"""KCL-6.5.3: isolate the sequential trajectory mechanism behind seed-9393 T4 failure."""

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
    optimizer_for,
    parameter_count,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl652_t4_failure_decomposition as k652

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl653-protocol.md")
KCL652_EVIDENCE = Path("experiments/kernel_cl/results/kcl652_summary.json")

SEED = 9393
STRICT_T4_MIN = 0.95
REPRO_TOLERANCE = 1e-9
T4_STREAM_SEED = SEED + 4000 + 307
CHECKPOINTS = tuple(range(0, 251, 25))

GROUP_TOKEN = "G_TOKEN_SHARED"
GROUP_POSITION = "G_POSITION"
GROUP_TRANSFORMER = "G_TRANSFORMER"
GROUP_FINAL_NORM = "G_FINAL_NORM"
GROUP_ORDER = (GROUP_TOKEN, GROUP_POSITION, GROUP_TRANSFORMER, GROUP_FINAL_NORM)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _deep_equal(a: Any, b: Any) -> bool:
    return k652._deep_equal(a, b)


def _model_equal(a: torch.nn.Module, b: torch.nn.Module) -> bool:
    return k652._model_equal(a, b)


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL652_EVIDENCE.read_text(encoding="utf-8"))
    finals = raw.get("final_T4_accuracy", {})
    valid = (
        raw.get("status") == "PASS"
        and raw.get("verdict") == "SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE"
        and abs(float(finals.get("G0", -1)) - 1.0) <= REPRO_TOLERANCE
        and abs(float(finals.get("G1", -1)) - 0.875) <= REPRO_TOLERANCE
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "G0": finals.get("G0"),
        "G1": finals.get("G1"),
        "sha256": _sha256(KCL652_EVIDENCE),
    }


def _clone_pair(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[torch.nn.Module, torch.optim.Optimizer]:
    cloned_model = copy.deepcopy(model)
    cloned_opt = optimizer_for(cloned_model, config)
    cloned_opt.load_state_dict(copy.deepcopy(optimizer.state_dict()))
    return cloned_model, cloned_opt


def _snapshot(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
) -> dict[str, Any]:
    return {
        "model": copy.deepcopy(model),
        "optimizer_state": copy.deepcopy(optimizer.state_dict()),
    }


def _optimizer_on(
    model: torch.nn.Module,
    optimizer_state: dict[str, Any],
    config: KCL1Config,
) -> torch.optim.Optimizer:
    opt = optimizer_for(model, config)
    opt.load_state_dict(copy.deepcopy(optimizer_state))
    return opt


def _probe_t4(
    model: torch.nn.Module,
    optimizer_state: dict[str, Any],
    t4: tuple[torch.Tensor, torch.Tensor],
    config: KCL1Config,
) -> dict[str, Any]:
    probe_model = copy.deepcopy(model)
    probe_opt = _optimizer_on(probe_model, optimizer_state, config)
    result = k652._train_current_only_curve(
        probe_model,
        probe_opt,
        t4,
        generator_seed=T4_STREAM_SEED,
    )
    return {
        "curve": result["curve"],
        "steps_to_95_checkpoint": result["steps_to_95_checkpoint"],
        "final_accuracy": result["final_accuracy"],
        "max_accuracy": result["max_accuracy"],
        "fell_below_95_after_first_reach": result["fell_below_95_after_first_reach"],
        "pass_95_final": result["pass_95_final"],
    }


def _prefix_snapshots(config: KCL1Config) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tasks = task_sequence(config)
    model = build_model(config, SEED)
    optimizer = optimizer_for(model, config)

    snapshots = [_snapshot(model, optimizer)]
    own_task_metrics: list[dict[str, Any]] = []

    # T1
    train_stage(
        model,
        optimizer,
        tasks[0][1],
        steps=config.stage_steps,
        batch_size=16,
        seed=SEED + 101,
    )
    own_task_metrics.append({"task": tasks[0][0], **evaluate(model, tasks[0][1])})
    snapshots.append(_snapshot(model, optimizer))

    # T2, T3 use KCL-6 current-only streams.
    for stage_idx in (1, 2):
        stage = stage_idx + 1
        train_stage(
            model,
            optimizer,
            tasks[stage_idx][1],
            steps=config.stage_steps,
            batch_size=16,
            seed=SEED + 1000 * stage + 307,
        )
        own_task_metrics.append({
            "task": tasks[stage_idx][0],
            **evaluate(model, tasks[stage_idx][1]),
        })
        snapshots.append(_snapshot(model, optimizer))

    return snapshots, own_task_metrics


def find_first_failing_transition(prefix_results: list[dict[str, Any]]) -> int | None:
    for j in (1, 2, 3):
        if (
            prefix_results[j - 1]["final_accuracy"] >= STRICT_T4_MIN
            and prefix_results[j]["final_accuracy"] < STRICT_T4_MIN
        ):
            return j
    return None


def state_factor_class(x10: float, x01: float, x11: float) -> str:
    # X00 is guaranteed PASS by transition definition; X11 is guaranteed FAIL.
    if x11 >= STRICT_T4_MIN:
        return "STATE_FACTOR_UNRESOLVED"
    x10_fail = x10 < STRICT_T4_MIN
    x01_fail = x01 < STRICT_T4_MIN
    if not x10_fail and x01_fail:
        return "OPTIMIZER_STATE_DOMINANT"
    if x10_fail and not x01_fail:
        return "MODEL_STATE_DOMINANT"
    if x10_fail and x01_fail:
        return "BOTH_STATES_INDEPENDENTLY_SUFFICIENT"
    if not x10_fail and not x01_fail:
        return "MODEL_OPTIMIZER_INTERACTION_ONLY"
    return "STATE_FACTOR_UNRESOLVED"


def parameter_groups(model: torch.nn.Module) -> dict[str, list[str]]:
    groups = {
        GROUP_TOKEN: [],
        GROUP_POSITION: [],
        GROUP_TRANSFORMER: [],
        GROUP_FINAL_NORM: [],
    }
    for name, _ in model.named_parameters():
        if name in {"token_embedding.weight", "lm_head.weight"}:
            groups[GROUP_TOKEN].append(name)
        elif name == "position_embedding.weight":
            groups[GROUP_POSITION].append(name)
        elif name.startswith("layers."):
            groups[GROUP_TRANSFORMER].append(name)
        elif name.startswith("norm."):
            groups[GROUP_FINAL_NORM].append(name)
        else:
            raise RuntimeError(f"uncovered parameter: {name}")
    return groups


def group_coverage_valid(model: torch.nn.Module, groups: dict[str, list[str]]) -> bool:
    all_names = [name for name, _ in model.named_parameters()]
    flat = [name for group in GROUP_ORDER for name in groups[group]]
    return (
        len(flat) == len(set(flat))
        and set(flat) == set(all_names)
        and all(groups[g] for g in GROUP_ORDER)
    )


def _copy_group(
    target: torch.nn.Module,
    source: torch.nn.Module,
    names: list[str],
) -> None:
    t = dict(target.named_parameters())
    s = dict(source.named_parameters())
    with torch.no_grad():
        for name in names:
            t[name].copy_(s[name])


def parameter_drift(
    pre: torch.nn.Module,
    post: torch.nn.Module,
    groups: dict[str, list[str]],
) -> dict[str, Any]:
    pre_params = dict(pre.named_parameters())
    post_params = dict(post.named_parameters())
    output: dict[str, Any] = {}
    for group in GROUP_ORDER:
        deltas = []
        pres = []
        max_abs = 0.0
        count = 0
        for name in groups[group]:
            p0 = pre_params[name].detach().float().reshape(-1)
            p1 = post_params[name].detach().float().reshape(-1)
            d = p1 - p0
            deltas.append(d)
            pres.append(p0)
            max_abs = max(max_abs, float(d.abs().max()))
            count += d.numel()
        delta_vec = torch.cat(deltas)
        pre_vec = torch.cat(pres)
        l2 = float(torch.linalg.vector_norm(delta_vec))
        pre_l2 = float(torch.linalg.vector_norm(pre_vec))
        output[group] = {
            "parameter_count": int(count),
            "l2_delta": l2,
            "relative_l2_delta": l2 / max(pre_l2, 1e-12),
            "max_abs_delta": max_abs,
        }
    return output


def classify_group_localization(group_results: dict[str, dict[str, Any]]) -> str:
    both = [
        g for g in GROUP_ORDER
        if group_results[g]["sufficient"] and group_results[g]["necessary"]
    ]
    sufficient = [g for g in GROUP_ORDER if group_results[g]["sufficient"]]
    necessary = [g for g in GROUP_ORDER if group_results[g]["necessary"]]

    if len(both) == 1 and len(sufficient) == 1 and len(necessary) == 1:
        return f"STRONG_LOCALIZATION_{both[0]}"
    if len(sufficient) >= 2 and len(necessary) == 0:
        return "MULTI_GROUP_REDUNDANT"
    if len(sufficient) == 0 and len(necessary) >= 1:
        return "MULTI_GROUP_INTERACTION"
    if len(sufficient) == 0 and len(necessary) == 0:
        return "DISTRIBUTED_PARAMETER_INTERFERENCE"
    return "MIXED_PARAMETER_LOCALIZATION"


def architecture_gap_candidate(
    state_class: str,
    group_class: str | None,
) -> str:
    if state_class == "OPTIMIZER_STATE_DOMINANT":
        return "TASK_BOUNDARY_OPTIMIZER_STATE_LIFECYCLE"
    if state_class == "MODEL_OPTIMIZER_INTERACTION_ONLY":
        return "JOINT_MODEL_OPTIMIZER_TASK_BOUNDARY_COORDINATION"
    if state_class == "BOTH_STATES_INDEPENDENTLY_SUFFICIENT":
        if group_class and group_class.startswith("STRONG_LOCALIZATION_"):
            return "COMBINED_PARAMETER_PLASTICITY_AND_OPTIMIZER_LIFECYCLE"
        return "GLOBAL_PLASTICITY_GOVERNOR_PLUS_OPTIMIZER_LIFECYCLE"
    if state_class == "MODEL_STATE_DOMINANT":
        if group_class == f"STRONG_LOCALIZATION_{GROUP_TOKEN}":
            return "SHARED_TOKEN_OUTPUT_REPRESENTATION_PROTECTION"
        if group_class == f"STRONG_LOCALIZATION_{GROUP_POSITION}":
            return "POSITION_CONTEXT_REPRESENTATION_ISOLATION"
        if group_class == f"STRONG_LOCALIZATION_{GROUP_TRANSFORMER}":
            return "BACKBONE_REPRESENTATION_PLASTICITY_CONTROL"
        if group_class == f"STRONG_LOCALIZATION_{GROUP_FINAL_NORM}":
            return "NORMALIZATION_AFFINE_ADAPTATION_ISOLATION"
        return "GLOBAL_PARAMETER_PLASTICITY_GOVERNOR_OR_SUBSPACE_SEPARATION"
    return "ARCHITECTURE_GAP_UNRESOLVED"


def _run_factorial(
    pre: dict[str, Any],
    post: dict[str, Any],
    t4: tuple[torch.Tensor, torch.Tensor],
    config: KCL1Config,
) -> dict[str, Any]:
    cells = {}
    combinations = {
        "X00_PRE_MODEL_PRE_OPT": (pre["model"], pre["optimizer_state"]),
        "X10_POST_MODEL_PRE_OPT": (post["model"], pre["optimizer_state"]),
        "X01_PRE_MODEL_POST_OPT": (pre["model"], post["optimizer_state"]),
        "X11_POST_MODEL_POST_OPT": (post["model"], post["optimizer_state"]),
    }
    for name, (model, opt_state) in combinations.items():
        cells[name] = _probe_t4(model, opt_state, t4, config)
    return cells


def _run_group_localization(
    pre: dict[str, Any],
    post: dict[str, Any],
    t4: tuple[torch.Tensor, torch.Tensor],
    config: KCL1Config,
    groups: dict[str, list[str]],
) -> dict[str, Any]:
    results: dict[str, dict[str, Any]] = {}
    for group in GROUP_ORDER:
        only = copy.deepcopy(pre["model"])
        _copy_group(only, post["model"], groups[group])
        only_probe = _probe_t4(only, pre["optimizer_state"], t4, config)

        without = copy.deepcopy(post["model"])
        _copy_group(without, pre["model"], groups[group])
        without_probe = _probe_t4(without, pre["optimizer_state"], t4, config)

        results[group] = {
            "names": groups[group],
            "ONLY_post_group": only_probe,
            "WITHOUT_post_group": without_probe,
            "sufficient": only_probe["final_accuracy"] < STRICT_T4_MIN,
            "necessary": without_probe["final_accuracy"] >= STRICT_T4_MIN,
        }
    return results


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    anchor = _load_anchor()
    config = KCL1Config()
    tasks = task_sequence(config)
    t4 = tasks[3][1]

    if not anchor["valid"]:
        return {
            "experiment": "KCL-6.5.3",
            "status": "REVISE",
            "verdict": "SEQUENTIAL_MECHANISM_ISOLATION_INVALID",
            "reason": "KCL-6.5.2 anchor invalid",
            "historical_anchor": anchor,
        }

    snapshots, own_task_metrics = _prefix_snapshots(config)

    prefix_results = [
        _probe_t4(s["model"], s["optimizer_state"], t4, config)
        for s in snapshots
    ]

    reproduction_valid = (
        abs(prefix_results[0]["final_accuracy"] - 1.0) <= REPRO_TOLERANCE
        and abs(prefix_results[3]["final_accuracy"] - 0.875) <= REPRO_TOLERANCE
    )

    trigger = find_first_failing_transition(prefix_results) if reproduction_valid else None

    if not reproduction_valid or trigger is None:
        return {
            "experiment": "KCL-6.5.3",
            "status": "REVISE",
            "verdict": "SEQUENTIAL_MECHANISM_ISOLATION_INVALID",
            "reason": "prefix reproduction/transition invalid",
            "historical_anchor": anchor,
            "prefix_results": prefix_results,
            "trigger_transition": trigger,
            "protocol": str(PROTOCOL),
            "protocol_sha256": _sha256(PROTOCOL),
            "git_commit": _git_commit(),
        }

    pre = snapshots[trigger - 1]
    post = snapshots[trigger]
    factorial = _run_factorial(pre, post, t4, config)

    x00 = factorial["X00_PRE_MODEL_PRE_OPT"]["final_accuracy"]
    x10 = factorial["X10_POST_MODEL_PRE_OPT"]["final_accuracy"]
    x01 = factorial["X01_PRE_MODEL_POST_OPT"]["final_accuracy"]
    x11 = factorial["X11_POST_MODEL_POST_OPT"]["final_accuracy"]

    factorial_integrity = (
        abs(x00 - prefix_results[trigger - 1]["final_accuracy"]) <= REPRO_TOLERANCE
        and abs(x11 - prefix_results[trigger]["final_accuracy"]) <= REPRO_TOLERANCE
    )

    state_class = state_factor_class(x10, x01, x11)

    groups = parameter_groups(pre["model"])
    coverage_valid = group_coverage_valid(pre["model"], groups)
    drift = parameter_drift(pre["model"], post["model"], groups) if coverage_valid else {}

    model_implicated = x10 < STRICT_T4_MIN
    group_results = None
    group_class = None
    if factorial_integrity and coverage_valid and model_implicated:
        group_results = _run_group_localization(pre, post, t4, config, groups)
        group_class = classify_group_localization(group_results)

    all_curves = [p["curve"] for p in prefix_results] + [
        c["curve"] for c in factorial.values()
    ]
    if group_results:
        for result in group_results.values():
            all_curves.append(result["ONLY_post_group"]["curve"])
            all_curves.append(result["WITHOUT_post_group"]["curve"])

    finite = all(
        math.isfinite(float(point["accuracy"])) and math.isfinite(float(point["loss"]))
        for curve in all_curves
        for point in curve
    )

    architecture_gap = architecture_gap_candidate(state_class, group_class)

    valid = reproduction_valid and factorial_integrity and coverage_valid and finite

    if not valid:
        status = "REVISE"
        verdict = "SEQUENTIAL_MECHANISM_ISOLATION_INVALID"
    elif state_class == "STATE_FACTOR_UNRESOLVED":
        status = "INCONCLUSIVE"
        verdict = "SEQUENTIAL_STATE_FACTOR_UNRESOLVED"
    else:
        status = "PASS"
        verdict = state_class if group_class is None else f"{state_class}__{group_class}"

    return {
        "experiment": "KCL-6.5.3",
        "status": status,
        "verdict": verdict,
        "seed": SEED,
        "historical_anchor": anchor,
        "prefixes": {
            "P0_FRESH": prefix_results[0],
            "P1_T1": prefix_results[1],
            "P2_T1_T2": prefix_results[2],
            "P3_T1_T2_T3": prefix_results[3],
        },
        "prefix_own_task_metrics": own_task_metrics,
        "trigger_transition": {
            "j_star": trigger,
            "task": tasks[trigger - 1][0],
            "pre_prefix": trigger - 1,
            "post_prefix": trigger,
        },
        "factorial_2x2": factorial,
        "state_factor_class": state_class,
        "parameter_groups": groups,
        "parameter_group_coverage_valid": coverage_valid,
        "parameter_drift": drift,
        "group_localization": {
            "executed": group_results is not None,
            "classification": group_class,
            "results": group_results,
        },
        "architecture_gap_candidate": architecture_gap,
        "integrity": {
            "canonical_prefix_reproduced": reproduction_valid,
            "factorial_X00_X11_reproduced": factorial_integrity,
            "group_coverage_valid": coverage_valid,
            "all_metrics_finite": finite,
            "architecture_changed": False,
            "optimizer_hyperparameters_changed": False,
            "kcl7_started": False,
        },
        "frozen_streams": {
            "T1": SEED + 101,
            "T2": SEED + 2000 + 307,
            "T3": SEED + 3000 + 307,
            "T4_probe": T4_STREAM_SEED,
        },
        "model_parameter_count": parameter_count(build_model(config, SEED)),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl653_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] in {"PASS", "INCONCLUSIVE"}:
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
