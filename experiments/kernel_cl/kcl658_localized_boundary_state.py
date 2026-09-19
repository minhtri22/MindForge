"""KCL-6.5.8: localized relational boundary-state attribution."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import random
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    evaluate,
    optimizer_for,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl653_sequential_trajectory_isolation as k653
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl657_relational_boundary_state as k657

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl658-protocol.md")
KCL656_EVIDENCE = Path("experiments/kernel_cl/results/kcl656_discovery.json")

DISCOVERY_SEEDS = k656.DISCOVERY_SEEDS
CONFIRM_SEEDS = k656.CONFIRM_SEEDS
GROUP_ORDER = k653.GROUP_ORDER

FEATURE_ORDER = tuple(f"F{i}" for i in range(1, 14))
ABLATIONS = {
    "A_OVERLAP": ("F1", "F2", "F3", "F4"),
    "A_MISMATCH": ("F5", "F6", "F7", "F8"),
    "A_IDENTITY": ("F9", "F10", "F11", "F12"),
    "A_NO_DIRECTION": tuple(f"F{i}" for i in range(1, 13)),
}

RIDGE_LAMBDA = 1.0
MAX_NEWTON_ITERS = 100
NEWTON_TOL = 1e-10
HESSIAN_JITTER = 1e-8

DISCOVERY_BA_MIN = 0.70
DISCOVERY_SENS_MIN = 0.65
DISCOVERY_SPEC_MIN = 0.65
BASELINE_SUPERIORITY_MIN = 0.03

CONFIRM_BA_MIN = 0.70
CONFIRM_SENS_MIN = 0.65
CONFIRM_SPEC_MIN = 0.65
CONFIRM_CI_LOWER_MIN = 0.55
BOOTSTRAP_RESAMPLES = 20000
BOOTSTRAP_SEED = 658658
REPRO_TOLERANCE = 1e-9


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _load_canonical() -> dict[str, Any]:
    raw = json.loads(KCL656_EVIDENCE.read_text(encoding="utf-8"))
    records = raw.get("records", [])
    valid = (
        raw.get("status") == "NEGATIVE"
        and raw.get("verdict") == "NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL"
        and raw.get("integrity", {}).get("valid") is True
        and len(records) == 60
        and set(int(r["seed"]) for r in records) == set(DISCOVERY_SEEDS)
        and set(int(r["seed"]) for r in records).isdisjoint(CONFIRM_SEEDS)
    )
    by_key = {(int(r["seed"]), int(r["boundary_index"])): r for r in records}
    return {
        "valid": valid and len(by_key) == 60,
        "raw": raw,
        "records": records,
        "by_key": by_key,
        "sha256": _sha256(KCL656_EVIDENCE),
    }


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = float(torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b))
    if denom <= 1e-20:
        return 0.0
    return float(torch.dot(a, b) / denom)


def _normalize_shares(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if not math.isfinite(total) or total <= 1e-20:
        raise RuntimeError("localized share denominator is zero/non-finite")
    shares = {k: float(v / total) for k, v in values.items()}
    if abs(sum(shares.values()) - 1.0) > 1e-9:
        raise RuntimeError("localized shares do not sum to one")
    return shares


def _group_vectors(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    pre_task_model_state: dict[str, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
) -> dict[str, Any]:
    groups = k653.parameter_groups(model)
    if not k653.group_coverage_valid(model, groups):
        raise RuntimeError("parameter-group coverage invalid")

    params = dict(model.named_parameters())
    opt_group = optimizer.param_groups[0]
    beta1, beta2 = opt_group["betas"]
    eps = float(opt_group["eps"])

    # Protected-retention gradient uses only already-observed tasks.
    model.zero_grad(set_to_none=True)
    losses = []
    for _, task in observed_tasks:
        x, y = task
        losses.append(F.cross_entropy(model(x)[:, -1, :], y))
    retention_loss = torch.stack(losses).mean()
    retention_loss.backward()

    out = {}
    for group in GROUP_ORDER:
        drift_parts = []
        pressure_parts = []
        retention_grad_parts = []
        for name in groups[group]:
            p = params[name]
            post = p.detach().float().reshape(-1)
            pre = pre_task_model_state[name].detach().float().reshape(-1)
            drift_parts.append(post - pre)

            state = optimizer.state.get(p)
            if not state:
                raise RuntimeError(f"optimizer state missing for {name}")
            step = float(state["step"].item())
            m = state["exp_avg"].detach().float().reshape(-1)
            v = state["exp_avg_sq"].detach().float().reshape(-1)
            m_hat = m / (1.0 - beta1 ** step)
            v_hat = v / (1.0 - beta2 ** step)
            pressure_parts.append(m_hat / (torch.sqrt(v_hat) + eps))

            grad = p.grad
            if grad is None:
                retention_grad_parts.append(torch.zeros_like(post))
            else:
                retention_grad_parts.append(grad.detach().float().reshape(-1))

        drift = torch.cat(drift_parts)
        pressure = torch.cat(pressure_parts)
        ret_grad = torch.cat(retention_grad_parts)
        out[group] = {
            "drift": drift,
            "pressure": pressure,
            "retention_grad": ret_grad,
            "D": float(torch.linalg.vector_norm(drift)),
            "P": float(torch.linalg.vector_norm(pressure)),
            "K": float(torch.linalg.vector_norm(ret_grad)),
            "C_DP": _cosine(drift, -pressure),
            "C_PK": _cosine(-pressure, -ret_grad),
        }

    model.zero_grad(set_to_none=True)
    if any(p.grad is not None for p in model.parameters()):
        raise RuntimeError("parameter gradients not cleared after attribution")

    return {
        "groups": groups,
        "vectors": out,
        "retention_loss": float(retention_loss.detach()),
    }


def extract_localized_features(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    pre_task_model_state: dict[str, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    boundary_index: int,
) -> dict[str, Any]:
    state = _group_vectors(
        model,
        optimizer,
        pre_task_model_state,
        observed_tasks,
    )
    vec = state["vectors"]

    d = _normalize_shares({g: vec[g]["D"] for g in GROUP_ORDER})
    p = _normalize_shares({g: vec[g]["P"] for g in GROUP_ORDER})
    k = _normalize_shares({g: vec[g]["K"] for g in GROUP_ORDER})

    f1 = sum(d[g] * p[g] for g in GROUP_ORDER)
    f2 = sum(d[g] * k[g] for g in GROUP_ORDER)
    f3 = sum(p[g] * k[g] for g in GROUP_ORDER)
    f4 = sum(d[g] * p[g] * k[g] for g in GROUP_ORDER)
    f5 = 0.5 * sum(abs(d[g] - p[g]) for g in GROUP_ORDER)
    f6 = 0.5 * sum(abs(d[g] - k[g]) for g in GROUP_ORDER)
    f7 = 0.5 * sum(abs(p[g] - k[g]) for g in GROUP_ORDER)

    seen_acc = [evaluate(model, task)["accuracy"] for _, task in observed_tasks]
    f8 = 1.0 - min(seen_acc)

    triple = {g: d[g] * p[g] * k[g] for g in GROUP_ORDER}
    f13 = sum(k[g] * vec[g]["C_DP"] for g in GROUP_ORDER)
    retention_pressure_alignment = sum(k[g] * vec[g]["C_PK"] for g in GROUP_ORDER)

    # Canonical H4 baseline reconstructed in the exact named-parameter
    # concatenation order used by KCL-6.5.6.  Group-order concatenation is
    # mathematically equivalent but changes floating reduction order.
    theta_post = torch.cat([
        param.detach().float().reshape(-1)
        for _, param in model.named_parameters()
    ])
    pre_vec = torch.cat([
        pre_task_model_state[name].detach().float().reshape(-1)
        for name, _ in model.named_parameters()
    ])
    full_drift = theta_post - pre_vec
    h4 = float(torch.linalg.vector_norm(full_drift)) / max(
        float(torch.linalg.vector_norm(pre_vec)), 1e-12
    )

    features = {
        "BOUNDARY_INDEX": float(boundary_index),
        "H4_TASK_DRIFT_RELATIVE_L2": h4,
        "F1": f1,
        "F2": f2,
        "F3": f3,
        "F4": f4,
        "F5": f5,
        "F6": f6,
        "F7": f7,
        "F8": f8,
        "F9": triple[k653.GROUP_TOKEN],
        "F10": triple[k653.GROUP_POSITION],
        "F11": triple[k653.GROUP_TRANSFORMER],
        "F12": triple[k653.GROUP_FINAL_NORM],
        "F13": f13,
    }
    if not all(math.isfinite(float(v)) for v in features.values()):
        raise RuntimeError("non-finite LRBS feature")

    details = {
        "drift_share": d,
        "pressure_share": p,
        "retention_attribution_share": k,
        "group_drift_pressure_cosine": {g: vec[g]["C_DP"] for g in GROUP_ORDER},
        "group_pressure_retention_cosine": {g: vec[g]["C_PK"] for g in GROUP_ORDER},
        "retention_weighted_pressure_retention_cosine": retention_pressure_alignment,
        "retention_objective_loss": state["retention_loss"],
        "share_sums": {
            "drift": sum(d.values()),
            "pressure": sum(p.values()),
            "retention": sum(k.values()),
        },
    }
    return {"features": features, "details": details}


def _outcome_reproduction_detail(
    new: dict[str, Any],
    canonical: dict[str, Any],
) -> dict[str, Any]:
    deltas: dict[str, float] = {}
    ok = True
    for policy in (
        "A_CARRY_ALL",
        "B_RESET_ALL",
        "C_CARRY_STEP_RESET_MOMENTS",
    ):
        a = new["outcomes"][policy]
        b = canonical["counterfactual_outcomes"][policy]
        for key in ("auc", "final_accuracy", "retention"):
            delta = float(a[key]) - float(b[key])
            deltas[f"{policy}.{key}"] = delta
            ok = ok and abs(delta) <= REPRO_TOLERANCE
    label_equal = bool(new["SAFE_RESET_OPPORTUNITY"]) == bool(
        canonical["labels"]["SAFE_RESET_OPPORTUNITY"]
    )
    return {
        "outcomes_match": ok,
        "label_equal": label_equal,
        "deltas": deltas,
    }


def build_localized_records(
    seed: int,
    config: KCL1Config,
    canonical_by_key: dict[tuple[int, int], dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    tasks = task_sequence(config)
    model = build_model(config, seed)
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
    observed = [tasks[0]]
    records = []

    for boundary_index in (1, 2, 3):
        current_task = observed[-1]
        canonical_boundary_features = k656.extract_boundary_features(
            model=model,
            optimizer=opt,
            pre_task_model_state=pre_task_model_state,
            observed_tasks=observed,
            current_task=current_task,
            boundary_index=boundary_index,
        )
        localized = extract_localized_features(
            model=model,
            optimizer=opt,
            pre_task_model_state=pre_task_model_state,
            observed_tasks=observed,
            boundary_index=boundary_index,
        )
        # Reuse the exact canonical implementation for the two baseline
        # features instead of numerically reconstructing them.
        localized["features"]["BOUNDARY_INDEX"] = float(
            canonical_boundary_features["BOUNDARY_INDEX"]
        )
        localized["features"]["H4_TASK_DRIFT_RELATIVE_L2"] = float(
            canonical_boundary_features["H4_TASK_DRIFT_RELATIVE_L2"]
        )

        next_task = tasks[boundary_index]
        counter = k656.run_next_task_counterfactual(
            model=model,
            optimizer=opt,
            memories=memories,
            observed_tasks=observed,
            next_task=next_task,
            seed=seed,
            next_stage=boundary_index + 1,
            config=config,
        )

        canonical_match = True
        reproduction_detail = None
        if canonical_by_key is not None:
            canonical = canonical_by_key[(seed, boundary_index)]
            reproduction_detail = _outcome_reproduction_detail(counter, canonical)
            h4_delta = (
                localized["features"]["H4_TASK_DRIFT_RELATIVE_L2"]
                - float(canonical["features"]["H4_TASK_DRIFT_RELATIVE_L2"])
            )
            reproduction_detail["H4_delta"] = h4_delta
            canonical_match = (
                reproduction_detail["outcomes_match"]
                and reproduction_detail["label_equal"]
                and abs(h4_delta) <= REPRO_TOLERANCE
            )

        records.append({
            "seed": seed,
            "boundary_index": boundary_index,
            "after_task": observed[-1][0],
            "features": localized["features"],
            "localized_details": localized["details"],
            "labels": {
                "SAFE_RESET_OPPORTUNITY": counter["SAFE_RESET_OPPORTUNITY"],
                "CARRY_PLASTICITY_FAILURE": counter["CARRY_PLASTICITY_FAILURE"],
                "BEST_SAFE_ACTION": counter["BEST_SAFE_ACTION"],
            },
            "counterfactual_outcomes": counter["outcomes"],
            "integrity": {
                **counter["integrity"],
                "canonical_reproduction": canonical_match,
                "canonical_reproduction_detail": reproduction_detail,
                "gradients_cleared_before_counterfactual": all(
                    p.grad is None for p in model.parameters()
                ),
            },
        })

        # Continue only A reference trajectory; preserve pre-task snapshot
        # exactly as KCL-6.5.6.
        pre_task_model_state = copy.deepcopy(model.state_dict())
        model = counter["_reference_model"]
        opt = counter["_reference_optimizer"]
        memories = counter["_next_memories"]
        observed = tasks[: boundary_index + 1]

    return records


def _fit_scaler(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...],
) -> dict[str, Any]:
    x = np.array(
        [[float(r["features"][name]) for name in feature_names] for r in records],
        dtype=np.float64,
    )
    means = x.mean(axis=0)
    stds = np.maximum(x.std(axis=0, ddof=0), 1e-12)
    return {
        "feature_names": list(feature_names),
        "means": means.tolist(),
        "stds": stds.tolist(),
    }


def _design(
    records: list[dict[str, Any]],
    scaler: dict[str, Any],
) -> np.ndarray:
    names = tuple(scaler["feature_names"])
    x = np.array(
        [[float(r["features"][name]) for name in names] for r in records],
        dtype=np.float64,
    )
    means = np.array(scaler["means"], dtype=np.float64)
    stds = np.array(scaler["stds"], dtype=np.float64)
    return (x - means) / stds


def fit_model(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...] = FEATURE_ORDER,
) -> dict[str, Any]:
    scaler = _fit_scaler(records, feature_names)
    x = _design(records, scaler)
    y = k657.labels_array(records)
    model = k657.fit_logistic(x, y, ridge_lambda=RIDGE_LAMBDA)
    scores = k657.predict_prob(x, model).tolist()
    threshold = k657.fit_score_threshold(
        scores,
        [bool(v) for v in y.tolist()],
    )
    return {
        "feature_names": list(feature_names),
        "scaler": scaler,
        "model": model,
        "threshold": threshold,
    }


def predict_model(
    records: list[dict[str, Any]],
    fitted: dict[str, Any],
) -> tuple[list[float], list[bool]]:
    x = _design(records, fitted["scaler"])
    scores = k657.predict_prob(x, fitted["model"]).tolist()
    th = fitted["threshold"]
    preds = k657.apply_threshold(scores, th["direction"], float(th["threshold"]))
    return scores, preds


def loso(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...] = FEATURE_ORDER,
) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    labels_all = []
    preds_all = []
    folds = []
    for held in seeds:
        train = [r for r in records if int(r["seed"]) != held]
        test = [r for r in records if int(r["seed"]) == held]
        fitted = fit_model(train, feature_names)
        _, preds = predict_model(test, fitted)
        labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in test]
        labels_all.extend(labels)
        preds_all.extend(preds)
        folds.append({
            "held_seed": held,
            "threshold": fitted["threshold"]["threshold"],
            "direction": fitted["threshold"]["direction"],
            "converged": fitted["model"]["converged"],
            "iterations": fitted["model"]["iterations"],
        })
    return {
        "feature_names": list(feature_names),
        "metrics": k656._metrics(labels_all, preds_all),
        "folds": folds,
    }


def _scalar_baselines(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "stage": k656.loso_evaluate(records, k656.STAGE_BASELINE),
        "H4_drift": k656.loso_evaluate(records, "H4_TASK_DRIFT_RELATIVE_L2"),
    }


def _qualified(metrics: dict[str, Any], baselines: dict[str, Any]) -> bool:
    best = max(
        baselines["stage"]["metrics"]["balanced_accuracy"],
        baselines["H4_drift"]["metrics"]["balanced_accuracy"],
    )
    return (
        metrics["balanced_accuracy"] >= DISCOVERY_BA_MIN
        and metrics["sensitivity"] >= DISCOVERY_SENS_MIN
        and metrics["specificity"] >= DISCOVERY_SPEC_MIN
        and metrics["balanced_accuracy"] >= best + BASELINE_SUPERIORITY_MIN
    )


def _cluster_bootstrap(
    records: list[dict[str, Any]],
    preds: list[bool],
) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    by_seed = {s: [] for s in seeds}
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
            bas.append(k656._metrics(labels, pp)["balanced_accuracy"])
    bas.sort()
    if not bas:
        return {"valid": False}
    return {
        "valid": True,
        "ci_lower": bas[int(0.025 * (len(bas) - 1))],
        "ci_upper": bas[int(0.975 * (len(bas) - 1))],
        "resamples_used": len(bas),
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def _fit_scalar_rule(records: list[dict[str, Any]], signal: str) -> dict[str, Any]:
    r = k656.fit_threshold(records, signal)
    return {
        "signal": r["signal"],
        "direction": r["direction"],
        "threshold": r["threshold"],
    }


def _apply_scalar(
    records: list[dict[str, Any]],
    rule: dict[str, Any],
) -> dict[str, Any]:
    preds = [
        k656._predict(
            float(r["features"][rule["signal"]]),
            rule["direction"],
            float(rule["threshold"]),
        )
        for r in records
    ]
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    return k656._metrics(labels, preds)


def run_discovery() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    canonical = _load_canonical()
    if not canonical["valid"]:
        return {
            "experiment": "KCL-6.5.8-DISCOVERY",
            "status": "REVISE",
            "verdict": "LOCALIZED_BOUNDARY_RECONSTRUCTION_INVALID",
            "reason": "canonical KCL-6.5.6 evidence invalid",
        }

    config = KCL1Config()
    records = [
        r
        for seed in DISCOVERY_SEEDS
        for r in build_localized_records(seed, config, canonical["by_key"])
    ]

    reproduction = all(
        r["integrity"]["canonical_reproduction"]
        and r["integrity"]["gradients_cleared_before_counterfactual"]
        and r["integrity"]["valid"]
        for r in records
    )

    baselines = _scalar_baselines(records)
    canonical_selection = canonical["raw"]["selection"]
    canonical_stage = canonical_selection["stage_baseline_cv"]["metrics"]
    canonical_h4 = next(
        x["cv"]["metrics"]
        for x in canonical_selection["candidates"]
        if x["signal"] == "H4_TASK_DRIFT_RELATIVE_L2"
    )
    baseline_reproduction = (
        all(
            abs(
                float(baselines["stage"]["metrics"][k])
                - float(canonical_stage[k])
            ) <= REPRO_TOLERANCE
            for k in ("balanced_accuracy", "sensitivity", "specificity", "accuracy")
        )
        and all(
            abs(
                float(baselines["H4_drift"]["metrics"][k])
                - float(canonical_h4[k])
            ) <= REPRO_TOLERANCE
            for k in ("balanced_accuracy", "sensitivity", "specificity", "accuracy")
        )
    )

    lrbs = loso(records) if reproduction and baseline_reproduction else None
    ablations = (
        {name: loso(records, tuple(features)) for name, features in ABLATIONS.items()}
        if lrbs is not None
        else {}
    )

    qualified = (
        lrbs is not None
        and _qualified(lrbs["metrics"], baselines)
    )

    if not reproduction or not baseline_reproduction:
        status = "REVISE"
        verdict = "LOCALIZED_BOUNDARY_RECONSTRUCTION_INVALID"
    elif qualified:
        status = "PASS"
        verdict = "DISCOVERY_LOCALIZED_RELATIONAL_STATE_SELECTED"
    else:
        status = "NEGATIVE"
        verdict = "LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED"

    final_model = fit_model(records) if qualified else None
    rule_artifact = None
    if qualified:
        rule_artifact = {
            "experiment": "KCL-6.5.8-RULE",
            "representation": "LRBS-v1",
            "target": "SAFE_RESET_OPPORTUNITY",
            "group_order": list(GROUP_ORDER),
            "feature_order": list(FEATURE_ORDER),
            "scaler": final_model["scaler"],
            "model": final_model["model"],
            "threshold": final_model["threshold"],
            "discovery_metrics": lrbs["metrics"],
            "stage_baseline_rule": _fit_scalar_rule(records, "BOUNDARY_INDEX"),
            "H4_baseline_rule": _fit_scalar_rule(
                records, "H4_TASK_DRIFT_RELATIVE_L2"
            ),
            "source_kcl656_sha256": canonical["sha256"],
            "protocol_sha256": _sha256(PROTOCOL),
        }

    best_ablation = None
    if ablations:
        ba, name = max(
            (v["metrics"]["balanced_accuracy"], k)
            for k, v in ablations.items()
        )
        best_ablation = {"name": name, "balanced_accuracy": ba}

    return {
        "experiment": "KCL-6.5.8-DISCOVERY",
        "status": status,
        "verdict": verdict,
        "representation": "LRBS-v1",
        "source": {
            "canonical_kcl656_sha256": canonical["sha256"],
            "instances": len(records),
            "seeds": list(DISCOVERY_SEEDS),
        },
        "lrbs_v1": lrbs,
        "baselines": baselines,
        "qualification": {
            "qualified": qualified,
            "BA_min": DISCOVERY_BA_MIN,
            "sensitivity_min": DISCOVERY_SENS_MIN,
            "specificity_min": DISCOVERY_SPEC_MIN,
            "baseline_superiority_min": BASELINE_SUPERIORITY_MIN,
            "best_baseline_BA": max(
                baselines["stage"]["metrics"]["balanced_accuracy"],
                baselines["H4_drift"]["metrics"]["balanced_accuracy"],
            ),
        },
        "ablations": ablations,
        "best_ablation": best_ablation,
        "rule_artifact": rule_artifact,
        "records": records,
        "integrity": {
            "valid": reproduction and baseline_reproduction,
            "canonical_60_of_60_reproduced": reproduction,
            "stage_H4_baselines_reproduced": baseline_reproduction,
            "confirmatory_seeds_absent": set(
                int(r["seed"]) for r in records
            ).isdisjoint(CONFIRM_SEEDS),
            "whole_seed_holdout": True,
            "fold_local_scaler_weights_threshold": True,
            "future_task_not_used_as_feature": True,
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
        },
    }


def _rule_valid(rule: dict[str, Any], canonical_sha: str) -> bool:
    return (
        rule.get("experiment") == "KCL-6.5.8-RULE"
        and rule.get("representation") == "LRBS-v1"
        and rule.get("target") == "SAFE_RESET_OPPORTUNITY"
        and rule.get("group_order") == list(GROUP_ORDER)
        and rule.get("feature_order") == list(FEATURE_ORDER)
        and rule.get("source_kcl656_sha256") == canonical_sha
        and rule.get("protocol_sha256") == _sha256(PROTOCOL)
    )


def run_confirm(rule_path: Path) -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    canonical = _load_canonical()
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if not canonical["valid"] or not _rule_valid(rule, canonical["sha256"]):
        return {
            "experiment": "KCL-6.5.8-CONFIRM",
            "status": "REVISE",
            "verdict": "LOCALIZED_RELATIONAL_STATE_INVALID",
            "reason": "canonical source/rule invalid",
        }

    config = KCL1Config()
    records = [
        r
        for seed in CONFIRM_SEEDS
        for r in build_localized_records(seed, config, None)
    ]
    integrity = (
        len(records) == 60
        and all(
            r["integrity"]["valid"]
            and r["integrity"]["gradients_cleared_before_counterfactual"]
            for r in records
        )
        and set(int(r["seed"]) for r in records) == set(CONFIRM_SEEDS)
    )

    fitted = {
        "feature_names": rule["feature_order"],
        "scaler": rule["scaler"],
        "model": rule["model"],
        "threshold": rule["threshold"],
    }
    _, preds = predict_model(records, fitted)
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    metrics = k656._metrics(labels, preds)
    ci = _cluster_bootstrap(records, preds)

    stage_metrics = _apply_scalar(records, rule["stage_baseline_rule"])
    h4_metrics = _apply_scalar(records, rule["H4_baseline_rule"])
    best_baseline = max(
        stage_metrics["balanced_accuracy"],
        h4_metrics["balanced_accuracy"],
    )

    confirmed = (
        integrity
        and metrics["balanced_accuracy"] >= CONFIRM_BA_MIN
        and ci.get("valid") is True
        and ci["ci_lower"] > CONFIRM_CI_LOWER_MIN
        and metrics["sensitivity"] >= CONFIRM_SENS_MIN
        and metrics["specificity"] >= CONFIRM_SPEC_MIN
        and metrics["balanced_accuracy"]
        >= best_baseline + BASELINE_SUPERIORITY_MIN
    )

    if not integrity:
        status = "REVISE"
        verdict = "LOCALIZED_RELATIONAL_STATE_INVALID"
    elif confirmed:
        status = "PASS"
        verdict = "LOCALIZED_RELATIONAL_BOUNDARY_STATE_QUALIFIED"
    else:
        status = "NEGATIVE"
        verdict = "LOCALIZED_RELATIONAL_STATE_NOT_GENERALIZED"

    return {
        "experiment": "KCL-6.5.8-CONFIRM",
        "status": status,
        "verdict": verdict,
        "representation": "LRBS-v1",
        "cohort": {"seeds": list(CONFIRM_SEEDS), "instances": len(records)},
        "metrics": metrics,
        "balanced_accuracy_seed_bootstrap": ci,
        "baselines": {
            "stage": stage_metrics,
            "H4_drift": h4_metrics,
            "best_baseline_BA": best_baseline,
        },
        "baseline_superiority": metrics["balanced_accuracy"] - best_baseline,
        "records": records,
        "integrity": {
            "valid": integrity,
            "rule_refit_on_confirmation": False,
            "confirmatory_counterfactual_integrity": all(
                r["integrity"]["valid"] for r in records
            ),
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "rule_sha256": _sha256(rule_path),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
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
            raise SystemExit("--rule required for confirm phase")
        result = run_confirm(Path(args.rule))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 3 if result["status"] == "REVISE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
