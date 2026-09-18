"""KCL-6.5.6: qualify a non-oracular boundary plasticity health signal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import random
import statistics
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
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl656-protocol.md")
KCL655_EVIDENCE = Path("experiments/kernel_cl/results/kcl655_summary.json")

DISCOVERY_SEEDS = (
    9595, 9797, 9999, 10201, 10403,
    10605, 10807, 11009, 11211, 11413,
    11615, 11817, 12019, 12221, 12423,
    12625, 12827, 13029, 13231, 13433,
)
CONFIRM_SEEDS = (
    13635, 13837, 14039, 14241, 14443,
    14645, 14847, 15049, 15251, 15453,
    15655, 15857, 16059, 16261, 16463,
    16665, 16867, 17069, 17271, 17473,
)

SIGNAL_ORDER = (
    "H1_M1_RMS",
    "H2_SQRT_M2_RMS",
    "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS",
    "H4_TASK_DRIFT_RELATIVE_L2",
    "H5_PRESSURE_TO_DRIFT_RATIO",
    "H6_DRIFT_PRESSURE_COSINE",
    "H7_PRIOR_MEAN_ACCURACY",
    "H8_PRIOR_WORST_ACCURACY",
    "H9_CURRENT_TASK_LOSS",
)
STAGE_BASELINE = "BOUNDARY_INDEX"

STRICT_CURRENT_MIN = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN = 1 / 24
DISCOVERY_BA_MIN = 0.65
DISCOVERY_SENS_MIN = 0.60
DISCOVERY_SPEC_MIN = 0.60
STAGE_SUPERIORITY_MIN = 0.05
BOOTSTRAP_RESAMPLES = 20000
BOOTSTRAP_SEED = 656656


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL655_EVIDENCE.read_text(encoding="utf-8"))
    adjud = raw.get("protocol_adjudication", {})
    valid = (
        adjud.get("adjudicated_status") == "FAIL"
        and adjud.get("adjudicated_verdict")
        == "BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION"
        and raw.get("integrity", {}).get("valid") is True
    )
    return {
        "valid": valid,
        "adjudicated_status": adjud.get("adjudicated_status"),
        "adjudicated_verdict": adjud.get("adjudicated_verdict"),
        "sha256": _sha256(KCL655_EVIDENCE),
    }


def _flatten_model(model: torch.nn.Module) -> torch.Tensor:
    return torch.cat([p.detach().float().reshape(-1) for p in model.parameters()])


def _optimizer_vectors(
    model: torch.nn.Module,
    opt: torch.optim.Optimizer,
) -> dict[str, torch.Tensor | float]:
    group = opt.param_groups[0]
    beta1, beta2 = group["betas"]
    eps = float(group["eps"])

    m_parts = []
    v_parts = []
    p_parts = []
    steps = []
    for p in model.parameters():
        state = opt.state.get(p)
        if not state:
            raise RuntimeError("boundary optimizer state missing")
        m = state["exp_avg"].detach().float().reshape(-1)
        v = state["exp_avg_sq"].detach().float().reshape(-1)
        step = float(state["step"].item())
        m_parts.append(m)
        v_parts.append(v)
        p_parts.append(p.detach().float().reshape(-1))
        steps.append(step)

    if len(set(steps)) != 1:
        raise RuntimeError("optimizer steps differ across parameters")
    step = steps[0]
    m = torch.cat(m_parts)
    v = torch.cat(v_parts)
    theta = torch.cat(p_parts)
    m_hat = m / (1.0 - beta1 ** step)
    v_hat = v / (1.0 - beta2 ** step)
    pressure = m_hat / (torch.sqrt(v_hat) + eps)
    return {
        "m": m,
        "v": v,
        "pressure": pressure,
        "theta": theta,
        "step": step,
    }


def _rms(x: torch.Tensor) -> float:
    return float(torch.sqrt(torch.mean(x.float() ** 2)))


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = float(torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b))
    if denom <= 1e-20:
        return 0.0
    return float(torch.dot(a, b) / denom)


def extract_boundary_features(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    pre_task_model_state: dict[str, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    current_task: tuple[str, tuple[torch.Tensor, torch.Tensor]],
    boundary_index: int,
) -> dict[str, float]:
    """Uses only state/tasks already observed at the boundary; no future task input."""
    vecs = _optimizer_vectors(model, optimizer)
    theta_post = vecs["theta"]
    theta_pre = torch.cat([
        pre_task_model_state[name].detach().float().reshape(-1)
        for name, _ in model.named_parameters()
    ])
    drift = theta_post - theta_pre
    pressure = vecs["pressure"]

    drift_norm = float(torch.linalg.vector_norm(drift))
    pre_norm = float(torch.linalg.vector_norm(theta_pre))
    pressure_norm = float(torch.linalg.vector_norm(pressure))

    seen_metrics = [evaluate(model, task) for _, task in observed_tasks]
    current_metric = evaluate(model, current_task[1])

    return {
        STAGE_BASELINE: float(boundary_index),
        "H1_M1_RMS": _rms(vecs["m"]),
        "H2_SQRT_M2_RMS": _rms(torch.sqrt(torch.clamp(vecs["v"], min=0))),
        "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS": _rms(pressure),
        "H4_TASK_DRIFT_RELATIVE_L2": drift_norm / max(pre_norm, 1e-12),
        "H5_PRESSURE_TO_DRIFT_RATIO": pressure_norm / max(drift_norm, 1e-12),
        "H6_DRIFT_PRESSURE_COSINE": _cosine(drift, -pressure),
        "H7_PRIOR_MEAN_ACCURACY": statistics.fmean(m["accuracy"] for m in seen_metrics),
        "H8_PRIOR_WORST_ACCURACY": min(m["accuracy"] for m in seen_metrics),
        "H9_CURRENT_TASK_LOSS": float(current_metric["loss"]),
    }


def _clone_model_opt(
    model: torch.nn.Module,
    opt: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[torch.nn.Module, torch.optim.Optimizer]:
    m = copy.deepcopy(model)
    o = optimizer_for(m, config)
    o.load_state_dict(copy.deepcopy(opt.state_dict()))
    return m, o


def _retention(
    model: torch.nn.Module,
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
) -> float:
    return statistics.fmean(evaluate(model, task)["accuracy"] for _, task in observed_tasks)


def _safe_beneficial(
    p: dict[str, Any],
    a: dict[str, Any],
) -> bool:
    plasticity = (
        p["auc"] - a["auc"] >= PLASTICITY_BENEFIT_MIN
        or (
            a["final_accuracy"] < STRICT_CURRENT_MIN
            and p["final_accuracy"] >= STRICT_CURRENT_MIN
        )
    )
    retention = p["retention"] - a["retention"] >= -RETENTION_MARGIN
    absolute = p["final_accuracy"] >= STRICT_CURRENT_MIN
    return plasticity and retention and absolute


def run_next_task_counterfactual(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    memories: list[k63.Memory],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    next_task: tuple[str, tuple[torch.Tensor, torch.Tensor]],
    seed: int,
    next_stage: int,
    config: KCL1Config,
) -> dict[str, Any]:
    """Runs outcomes only after feature extraction; receives the next task explicitly."""
    models: dict[str, torch.nn.Module] = {}
    opts: dict[str, torch.optim.Optimizer] = {}
    policy_integrity = {}

    for policy in k655.POLICIES:
        m, o = _clone_model_opt(model, optimizer, config)
        o, info = k655._policy_boundary(policy, m, o, config)
        models[policy] = m
        opts[policy] = o
        policy_integrity[policy] = info

    fork_equal = all(
        all(
            torch.equal(
                models[k655.POLICIES[0]].state_dict()[name],
                models[p].state_dict()[name],
            )
            for name in models[k655.POLICIES[0]].state_dict()
        )
        for p in k655.POLICIES[1:]
    )

    memory_copy = copy.deepcopy(memories)
    stage = k655._train_stage_lockstep(
        models,
        opts,
        memory_copy,
        next_task[1],
        [task for _, task in observed_tasks],
        seed=seed,
        stage=next_stage,
    )

    outcomes = {}
    for p in k655.POLICIES:
        summary = stage["curve_summary"][p]
        outcomes[p] = {
            "auc": float(summary["normalized_auc"]),
            "final_accuracy": float(summary["final_accuracy"]),
            "max_accuracy": float(summary["max_accuracy"]),
            "retention": _retention(models[p], observed_tasks),
        }

    a = outcomes["A_CARRY_ALL"]
    safe_b = _safe_beneficial(outcomes["B_RESET_ALL"], a)
    safe_c = _safe_beneficial(outcomes["C_CARRY_STEP_RESET_MOMENTS"], a)
    if safe_b and safe_c:
        best = (
            "B_RESET_ALL"
            if outcomes["B_RESET_ALL"]["auc"] >= outcomes["C_CARRY_STEP_RESET_MOMENTS"]["auc"]
            else "C_CARRY_STEP_RESET_MOMENTS"
        )
    elif safe_b:
        best = "B_RESET_ALL"
    elif safe_c:
        best = "C_CARRY_STEP_RESET_MOMENTS"
    else:
        best = "A_CARRY_ALL"

    integrity = (
        fork_equal
        and all(info["model_unchanged"] for info in policy_integrity.values())
        and math.isclose(stage["exact_replay_match_rate"], 1.0)
    )

    # A is the reference trajectory for the next boundary.
    ref_model = models["A_CARRY_ALL"]
    ref_opt = opts["A_CARRY_ALL"]
    next_memories = k655._decay(memory_copy)
    next_memories.append(k63.ExactMemory.from_task(next_task[1]))

    return {
        "outcomes": outcomes,
        "safe_B": safe_b,
        "safe_C": safe_c,
        "SAFE_RESET_OPPORTUNITY": bool(safe_b or safe_c),
        "CARRY_PLASTICITY_FAILURE": a["final_accuracy"] < STRICT_CURRENT_MIN,
        "BEST_SAFE_ACTION": best,
        "integrity": {
            "fork_models_equal": fork_equal,
            "exact_replay_match": math.isclose(stage["exact_replay_match_rate"], 1.0),
            "boundary_model_unchanged": all(
                info["model_unchanged"] for info in policy_integrity.values()
            ),
            "valid": integrity,
        },
        "_reference_model": ref_model,
        "_reference_optimizer": ref_opt,
        "_next_memories": next_memories,
    }


def build_boundary_records(seed: int, config: KCL1Config) -> list[dict[str, Any]]:
    tasks = task_sequence(config)

    fresh = build_model(config, seed)
    model = copy.deepcopy(fresh)
    opt = optimizer_for(model, config)
    pre_task_model_state = copy.deepcopy(model.state_dict())

    train_stage(
        model,
        opt,
        tasks[0][1],
        steps=250,
        batch_size=16,
        seed=seed + 101,
    )
    memories: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]

    records = []
    observed = [tasks[0]]

    for boundary_index in (1, 2, 3):
        current_task = observed[-1]
        # Anti-leakage: features are extracted before next_task is bound below.
        features = extract_boundary_features(
            model=model,
            optimizer=opt,
            pre_task_model_state=pre_task_model_state,
            observed_tasks=observed,
            current_task=current_task,
            boundary_index=boundary_index,
        )

        next_task = tasks[boundary_index]
        counter = run_next_task_counterfactual(
            model=model,
            optimizer=opt,
            memories=memories,
            observed_tasks=observed,
            next_task=next_task,
            seed=seed,
            next_stage=boundary_index + 1,
            config=config,
        )

        records.append({
            "seed": seed,
            "boundary_index": boundary_index,
            "after_task": current_task[0],
            "features": features,
            "labels": {
                "SAFE_RESET_OPPORTUNITY": counter["SAFE_RESET_OPPORTUNITY"],
                "CARRY_PLASTICITY_FAILURE": counter["CARRY_PLASTICITY_FAILURE"],
                "BEST_SAFE_ACTION": counter["BEST_SAFE_ACTION"],
            },
            "counterfactual_outcomes": counter["outcomes"],
            "integrity": counter["integrity"],
        })

        # Continue only the A reference trajectory.
        pre_task_model_state = copy.deepcopy(counter["_reference_model"].state_dict())
        model = counter["_reference_model"]
        opt = counter["_reference_optimizer"]
        memories = counter["_next_memories"]
        observed = tasks[: boundary_index + 1]

    return records


def _metrics(labels: list[bool], preds: list[bool]) -> dict[str, Any]:
    tp = sum(y and p for y, p in zip(labels, preds))
    tn = sum((not y) and (not p) for y, p in zip(labels, preds))
    fp = sum((not y) and p for y, p in zip(labels, preds))
    fn = sum(y and (not p) for y, p in zip(labels, preds))
    pos = tp + fn
    neg = tn + fp
    sens = tp / pos if pos else 0.0
    spec = tn / neg if neg else 0.0
    ba = 0.5 * (sens + spec)
    acc = (tp + tn) / len(labels) if labels else 0.0
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "sensitivity": sens,
        "specificity": spec,
        "balanced_accuracy": ba,
        "accuracy": acc,
        "positive_prevalence": pos / len(labels) if labels else 0.0,
    }


def _candidate_thresholds(values: list[float]) -> list[float]:
    uniq = sorted(set(float(v) for v in values))
    if not uniq:
        raise ValueError("empty threshold values")
    mids = [(a + b) / 2 for a, b in zip(uniq, uniq[1:])]
    return [math.nextafter(uniq[0], -math.inf), *mids, math.nextafter(uniq[-1], math.inf)]


def _predict(value: float, direction: str, threshold: float) -> bool:
    return value >= threshold if direction == ">=" else value <= threshold


def fit_threshold(records: list[dict[str, Any]], signal: str) -> dict[str, Any]:
    values = [float(r["features"][signal]) for r in records]
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    if not any(labels) or all(labels):
        return {
            "valid": False,
            "reason": "training labels contain only one class",
            "signal": signal,
        }

    best = None
    for threshold in _candidate_thresholds(values):
        for direction_order, direction in enumerate((">=", "<=")):
            preds = [_predict(v, direction, threshold) for v in values]
            m = _metrics(labels, preds)
            key = (
                m["balanced_accuracy"],
                min(m["sensitivity"], m["specificity"]),
                -direction_order,
                -threshold,
            )
            if best is None or key > best["_key"]:
                best = {
                    "valid": True,
                    "signal": signal,
                    "direction": direction,
                    "threshold": threshold,
                    "training_metrics": m,
                    "_key": key,
                }
    assert best is not None
    best.pop("_key", None)
    return best


def loso_evaluate(records: list[dict[str, Any]], signal: str) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    labels_all, preds_all = [], []
    fold_rules = []
    for held in seeds:
        train = [r for r in records if int(r["seed"]) != held]
        test = [r for r in records if int(r["seed"]) == held]
        rule = fit_threshold(train, signal)
        if not rule["valid"]:
            return {
                "valid": False,
                "signal": signal,
                "reason": rule.get("reason"),
            }
        labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in test]
        preds = [
            _predict(float(r["features"][signal]), rule["direction"], rule["threshold"])
            for r in test
        ]
        labels_all.extend(labels)
        preds_all.extend(preds)
        fold_rules.append({
            "held_seed": held,
            "direction": rule["direction"],
            "threshold": rule["threshold"],
        })
    return {
        "valid": True,
        "signal": signal,
        "metrics": _metrics(labels_all, preds_all),
        "fold_rules": fold_rules,
    }


def select_discovery_signal(records: list[dict[str, Any]]) -> dict[str, Any]:
    stage_cv = loso_evaluate(records, STAGE_BASELINE)
    candidates = []
    for order, signal in enumerate(SIGNAL_ORDER):
        cv = loso_evaluate(records, signal)
        if not cv["valid"]:
            candidates.append({
                "signal": signal,
                "order": order,
                "cv": cv,
                "qualified": False,
            })
            continue
        m = cv["metrics"]
        stage_ba = stage_cv["metrics"]["balanced_accuracy"]
        qualified = (
            m["balanced_accuracy"] >= DISCOVERY_BA_MIN
            and m["sensitivity"] >= DISCOVERY_SENS_MIN
            and m["specificity"] >= DISCOVERY_SPEC_MIN
            and m["balanced_accuracy"] >= stage_ba + STAGE_SUPERIORITY_MIN
        )
        candidates.append({
            "signal": signal,
            "order": order,
            "cv": cv,
            "qualified": qualified,
        })

    qualified = [x for x in candidates if x["qualified"]]
    selected = None
    if qualified:
        selected = max(
            qualified,
            key=lambda x: (
                x["cv"]["metrics"]["balanced_accuracy"],
                min(
                    x["cv"]["metrics"]["sensitivity"],
                    x["cv"]["metrics"]["specificity"],
                ),
                -x["order"],
            ),
        )
        final_rule = fit_threshold(records, selected["signal"])
        stage_rule = fit_threshold(records, STAGE_BASELINE)
        selected = {
            "signal": selected["signal"],
            "discovery_cv": selected["cv"],
            "final_rule": {
                "signal": final_rule["signal"],
                "direction": final_rule["direction"],
                "threshold": final_rule["threshold"],
                "training_metrics": final_rule["training_metrics"],
            },
            "stage_baseline_rule": {
                "signal": stage_rule["signal"],
                "direction": stage_rule["direction"],
                "threshold": stage_rule["threshold"],
                "training_metrics": stage_rule["training_metrics"],
            },
        }

    return {
        "stage_baseline_cv": stage_cv,
        "candidates": candidates,
        "selected": selected,
    }


def _cluster_bootstrap_ba(
    records: list[dict[str, Any]],
    preds: list[bool],
) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    by_seed: dict[int, list[int]] = {s: [] for s in seeds}
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)

    rng = random.Random(BOOTSTRAP_SEED)
    bas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        idxs = [i for s in drawn for i in by_seed[s]]
        labels = [bool(records[i]["labels"]["SAFE_RESET_OPPORTUNITY"]) for i in idxs]
        pp = [preds[i] for i in idxs]
        if any(labels) and not all(labels):
            bas.append(_metrics(labels, pp)["balanced_accuracy"])
    bas.sort()
    if not bas:
        return {"valid": False}
    lo = bas[int(0.025 * (len(bas) - 1))]
    hi = bas[int(0.975 * (len(bas) - 1))]
    return {
        "valid": True,
        "ci_lower": lo,
        "ci_upper": hi,
        "resamples_used": len(bas),
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def _apply_rule(records: list[dict[str, Any]], rule: dict[str, Any]) -> tuple[list[bool], dict[str, Any]]:
    preds = [
        _predict(
            float(r["features"][rule["signal"]]),
            rule["direction"],
            float(rule["threshold"]),
        )
        for r in records
    ]
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    return preds, _metrics(labels, preds)


def run_discovery() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    anchor = _load_anchor()
    config = KCL1Config()
    if not anchor["valid"]:
        return {
            "experiment": "KCL-6.5.6-DISCOVERY",
            "status": "REVISE",
            "verdict": "BOUNDARY_SIGNAL_QUALIFICATION_INVALID",
            "reason": "KCL-6.5.5 anchor invalid",
        }

    records = [r for seed in DISCOVERY_SEEDS for r in build_boundary_records(seed, config)]
    integrity = (
        len(records) == 60
        and all(r["integrity"]["valid"] for r in records)
        and all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        )
    )
    selection = select_discovery_signal(records) if integrity else {"selected": None}

    if not integrity:
        status, verdict = "REVISE", "BOUNDARY_SIGNAL_QUALIFICATION_INVALID"
    elif selection["selected"] is None:
        status, verdict = "NEGATIVE", "NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL"
    else:
        status, verdict = "PASS", "DISCOVERY_BOUNDARY_HEALTH_SIGNAL_SELECTED"

    label_counts = {
        "positive": sum(r["labels"]["SAFE_RESET_OPPORTUNITY"] for r in records),
        "negative": sum(not r["labels"]["SAFE_RESET_OPPORTUNITY"] for r in records),
        "carry_failures": sum(r["labels"]["CARRY_PLASTICITY_FAILURE"] for r in records),
    }

    rule_artifact = None
    if selection.get("selected"):
        s = selection["selected"]
        rule_artifact = {
            "experiment": "KCL-6.5.6-RULE",
            "source_phase": "discovery",
            "selected_signal": s["signal"],
            "direction": s["final_rule"]["direction"],
            "threshold": s["final_rule"]["threshold"],
            "discovery_cv_metrics": s["discovery_cv"]["metrics"],
            "stage_baseline": s["stage_baseline_rule"],
            "candidate_order": list(SIGNAL_ORDER),
            "target": "SAFE_RESET_OPPORTUNITY",
            "protocol_sha256": _sha256(PROTOCOL),
        }

    return {
        "experiment": "KCL-6.5.6-DISCOVERY",
        "status": status,
        "verdict": verdict,
        "anchor": anchor,
        "cohort": {"seeds": list(DISCOVERY_SEEDS), "instances": len(records)},
        "label_counts": label_counts,
        "selection": selection,
        "rule_artifact": rule_artifact,
        "records": records,
        "integrity": {
            "valid": integrity,
            "feature_extraction_before_counterfactual_by_construction": True,
            "future_task_not_passed_to_feature_function": True,
            "counterfactuals_matched": all(r["integrity"]["valid"] for r in records),
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
        },
    }


def run_confirm(rule_path: Path) -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    anchor = _load_anchor()
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    config = KCL1Config()

    rule_valid = (
        rule.get("experiment") == "KCL-6.5.6-RULE"
        and rule.get("selected_signal") in SIGNAL_ORDER
        and rule.get("target") == "SAFE_RESET_OPPORTUNITY"
        and rule.get("protocol_sha256") == _sha256(PROTOCOL)
    )
    if not anchor["valid"] or not rule_valid:
        return {
            "experiment": "KCL-6.5.6-CONFIRM",
            "status": "REVISE",
            "verdict": "BOUNDARY_SIGNAL_QUALIFICATION_INVALID",
            "reason": "anchor/rule invalid",
        }

    records = [r for seed in CONFIRM_SEEDS for r in build_boundary_records(seed, config)]
    integrity = len(records) == 60 and all(r["integrity"]["valid"] for r in records)

    frozen_rule = {
        "signal": rule["selected_signal"],
        "direction": rule["direction"],
        "threshold": rule["threshold"],
    }
    preds, metrics = _apply_rule(records, frozen_rule)
    ci = _cluster_bootstrap_ba(records, preds)

    stage_rule = rule["stage_baseline"]
    stage_preds, stage_metrics = _apply_rule(records, stage_rule)

    confirmed = (
        integrity
        and metrics["balanced_accuracy"] >= DISCOVERY_BA_MIN
        and ci.get("valid") is True
        and ci["ci_lower"] > 0.50
        and metrics["sensitivity"] >= DISCOVERY_SENS_MIN
        and metrics["specificity"] >= DISCOVERY_SPEC_MIN
        and metrics["balanced_accuracy"]
        >= stage_metrics["balanced_accuracy"] + STAGE_SUPERIORITY_MIN
    )

    if not integrity:
        status, verdict = "REVISE", "BOUNDARY_SIGNAL_QUALIFICATION_INVALID"
    elif confirmed:
        status, verdict = "PASS", "BOUNDARY_HEALTH_SIGNAL_QUALIFIED"
    else:
        status, verdict = "NEGATIVE", "BOUNDARY_HEALTH_SIGNAL_NOT_GENERALIZED"

    return {
        "experiment": "KCL-6.5.6-CONFIRM",
        "status": status,
        "verdict": verdict,
        "rule": frozen_rule,
        "cohort": {"seeds": list(CONFIRM_SEEDS), "instances": len(records)},
        "metrics": metrics,
        "balanced_accuracy_seed_bootstrap": ci,
        "stage_baseline_metrics": stage_metrics,
        "stage_superiority": (
            metrics["balanced_accuracy"] - stage_metrics["balanced_accuracy"]
        ),
        "label_counts": {
            "positive": sum(r["labels"]["SAFE_RESET_OPPORTUNITY"] for r in records),
            "negative": sum(not r["labels"]["SAFE_RESET_OPPORTUNITY"] for r in records),
            "carry_failures": sum(r["labels"]["CARRY_PLASTICITY_FAILURE"] for r in records),
        },
        "records": records,
        "integrity": {
            "valid": integrity,
            "rule_refit_on_confirmation": False,
            "feature_extraction_before_counterfactual_by_construction": True,
            "future_task_not_passed_to_feature_function": True,
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "rule_sha256": _sha256(rule_path),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("discovery", "confirm"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rule-output")
    parser.add_argument("--rule")
    args = parser.parse_args()

    if args.phase == "discovery":
        result = run_discovery()
        if args.rule_output and result.get("rule_artifact") is not None:
            rp = Path(args.rule_output)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(
                json.dumps(result["rule_artifact"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    else:
        if not args.rule:
            raise SystemExit("--rule is required for confirm phase")
        result = run_confirm(Path(args.rule))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    return 3 if result["status"] == "REVISE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
