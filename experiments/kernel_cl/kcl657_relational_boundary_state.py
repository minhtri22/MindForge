"""KCL-6.5.7: relational / multivariate boundary-state representation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from experiments.kernel_cl import kcl656_boundary_health_signal as k656

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl657-protocol.md")
KCL656_EVIDENCE = Path("experiments/kernel_cl/results/kcl656_discovery.json")

BASE_ORDER = ("D", "M1", "M2", "P", "G", "R")
FEATURE_ORDER = (
    "zD",
    "zM1",
    "zM2",
    "zP",
    "zG",
    "zR",
    "zD*zP",
    "zD*zR",
    "zP*zR",
    "zG*zR",
    "zM1*zM2",
)
ABLATIONS = {
    "A_DP": ("zD", "zP", "zD*zP"),
    "A_DR": ("zD", "zR", "zD*zR"),
    "A_MOMENT": ("zM1", "zM2", "zM1*zM2"),
    "A_NO_RETENTION": (
        "zD", "zM1", "zM2", "zP", "zG",
        "zD*zP", "zM1*zM2",
    ),
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
BOOTSTRAP_SEED = 657657

DISCOVERY_SEEDS = k656.DISCOVERY_SEEDS
CONFIRM_SEEDS = k656.CONFIRM_SEEDS


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _load_discovery() -> dict[str, Any]:
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
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "records": records,
        "sha256": _sha256(KCL656_EVIDENCE),
    }


def _base_from_record(record: dict[str, Any]) -> dict[str, float]:
    f = record["features"]
    out = {
        "D": float(f["H4_TASK_DRIFT_RELATIVE_L2"]),
        "M1": float(f["H1_M1_RMS"]),
        "M2": float(f["H2_SQRT_M2_RMS"]),
        "P": float(f["H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS"]),
        "G": float(f["H6_DRIFT_PRESSURE_COSINE"]),
        "R": 1.0 - float(f["H8_PRIOR_WORST_ACCURACY"]),
    }
    if not all(math.isfinite(v) for v in out.values()):
        raise ValueError("non-finite base feature")
    return out


def fit_scaler(records: list[dict[str, Any]]) -> dict[str, Any]:
    x = np.array(
        [[_base_from_record(r)[name] for name in BASE_ORDER] for r in records],
        dtype=np.float64,
    )
    means = x.mean(axis=0)
    stds = x.std(axis=0, ddof=0)
    stds = np.maximum(stds, 1e-12)
    return {
        "base_order": list(BASE_ORDER),
        "means": means.tolist(),
        "stds": stds.tolist(),
    }


def _zbase(record: dict[str, Any], scaler: dict[str, Any]) -> dict[str, float]:
    base = _base_from_record(record)
    means = scaler["means"]
    stds = scaler["stds"]
    return {
        name: (base[name] - float(means[i])) / float(stds[i])
        for i, name in enumerate(BASE_ORDER)
    }


def full_feature_map(record: dict[str, Any], scaler: dict[str, Any]) -> dict[str, float]:
    z = _zbase(record, scaler)
    return {
        "zD": z["D"],
        "zM1": z["M1"],
        "zM2": z["M2"],
        "zP": z["P"],
        "zG": z["G"],
        "zR": z["R"],
        "zD*zP": z["D"] * z["P"],
        "zD*zR": z["D"] * z["R"],
        "zP*zR": z["P"] * z["R"],
        "zG*zR": z["G"] * z["R"],
        "zM1*zM2": z["M1"] * z["M2"],
    }


def design_matrix(
    records: list[dict[str, Any]],
    scaler: dict[str, Any],
    feature_names: tuple[str, ...] = FEATURE_ORDER,
) -> np.ndarray:
    return np.array(
        [[full_feature_map(r, scaler)[name] for name in feature_names] for r in records],
        dtype=np.float64,
    )


def labels_array(records: list[dict[str, Any]]) -> np.ndarray:
    return np.array(
        [1.0 if r["labels"]["SAFE_RESET_OPPORTUNITY"] else 0.0 for r in records],
        dtype=np.float64,
    )


def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x))


def fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict[str, Any]:
    n, d = x.shape
    xa = np.concatenate([np.ones((n, 1), dtype=np.float64), x], axis=1)
    theta = np.zeros(d + 1, dtype=np.float64)
    converged = False

    reg = np.zeros(d + 1, dtype=np.float64)
    reg[1:] = ridge_lambda

    for it in range(MAX_NEWTON_ITERS):
        logits = xa @ theta
        p = _sigmoid(logits)
        grad = (xa.T @ (p - y)) / n + reg * theta
        w = p * (1.0 - p)
        h = (xa.T * w) @ xa / n
        h += np.diag(reg)
        h += np.eye(d + 1, dtype=np.float64) * HESSIAN_JITTER
        # Never regularize intercept beyond numerical jitter.
        try:
            delta = np.linalg.solve(h, grad)
        except np.linalg.LinAlgError:
            delta = np.linalg.pinv(h) @ grad
        theta_next = theta - delta
        if float(np.linalg.norm(theta_next - theta)) < NEWTON_TOL:
            theta = theta_next
            converged = True
            break
        theta = theta_next

    return {
        "intercept": float(theta[0]),
        "weights": theta[1:].tolist(),
        "iterations": it + 1,
        "converged": converged,
        "ridge_lambda": ridge_lambda,
    }


def predict_prob(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    w = np.array(model["weights"], dtype=np.float64)
    return _sigmoid(float(model["intercept"]) + x @ w)


def _threshold_candidates(values: list[float]) -> list[float]:
    uniq = sorted(set(float(v) for v in values))
    mids = [(a + b) / 2.0 for a, b in zip(uniq, uniq[1:])]
    return [
        math.nextafter(uniq[0], -math.inf),
        *mids,
        math.nextafter(uniq[-1], math.inf),
    ]


def fit_score_threshold(scores: list[float], labels: list[bool]) -> dict[str, Any]:
    best = None
    for threshold in _threshold_candidates(scores):
        for direction_order, direction in enumerate((">=", "<=")):
            preds = [
                s >= threshold if direction == ">=" else s <= threshold
                for s in scores
            ]
            m = k656._metrics(labels, preds)
            key = (
                m["balanced_accuracy"],
                min(m["sensitivity"], m["specificity"]),
                -direction_order,
                -threshold,
            )
            if best is None or key > best["_key"]:
                best = {
                    "direction": direction,
                    "threshold": threshold,
                    "training_metrics": m,
                    "_key": key,
                }
    assert best is not None
    best.pop("_key")
    return best


def apply_threshold(
    scores: list[float],
    direction: str,
    threshold: float,
) -> list[bool]:
    return [
        s >= threshold if direction == ">=" else s <= threshold
        for s in scores
    ]


def fit_representation(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...] = FEATURE_ORDER,
) -> dict[str, Any]:
    scaler = fit_scaler(records)
    x = design_matrix(records, scaler, feature_names)
    y = labels_array(records)
    model = fit_logistic(x, y)
    scores = predict_prob(x, model).tolist()
    threshold = fit_score_threshold(
        scores,
        [bool(v) for v in y.tolist()],
    )
    return {
        "feature_names": list(feature_names),
        "scaler": scaler,
        "model": model,
        "threshold": threshold,
    }


def predict_representation(
    records: list[dict[str, Any]],
    fitted: dict[str, Any],
) -> tuple[list[float], list[bool]]:
    feature_names = tuple(fitted["feature_names"])
    x = design_matrix(records, fitted["scaler"], feature_names)
    scores = predict_prob(x, fitted["model"]).tolist()
    th = fitted["threshold"]
    preds = apply_threshold(scores, th["direction"], float(th["threshold"]))
    return scores, preds


def loso_representation(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...] = FEATURE_ORDER,
) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    labels_all: list[bool] = []
    preds_all: list[bool] = []
    fold_models = []

    for held in seeds:
        train = [r for r in records if int(r["seed"]) != held]
        test = [r for r in records if int(r["seed"]) == held]
        fitted = fit_representation(train, feature_names)
        _, preds = predict_representation(test, fitted)
        labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in test]
        labels_all.extend(labels)
        preds_all.extend(preds)
        fold_models.append({
            "held_seed": held,
            "threshold_direction": fitted["threshold"]["direction"],
            "threshold": fitted["threshold"]["threshold"],
            "logistic_converged": fitted["model"]["converged"],
            "iterations": fitted["model"]["iterations"],
        })

    return {
        "feature_names": list(feature_names),
        "metrics": k656._metrics(labels_all, preds_all),
        "fold_models": fold_models,
    }


def scalar_baselines(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "stage": k656.loso_evaluate(records, k656.STAGE_BASELINE),
        "H4_drift": k656.loso_evaluate(records, "H4_TASK_DRIFT_RELATIVE_L2"),
    }


def discovery_qualified(
    rbs_metrics: dict[str, Any],
    baselines: dict[str, Any],
) -> bool:
    best_baseline = max(
        baselines["stage"]["metrics"]["balanced_accuracy"],
        baselines["H4_drift"]["metrics"]["balanced_accuracy"],
    )
    return (
        rbs_metrics["balanced_accuracy"] >= DISCOVERY_BA_MIN
        and rbs_metrics["sensitivity"] >= DISCOVERY_SENS_MIN
        and rbs_metrics["specificity"] >= DISCOVERY_SPEC_MIN
        and rbs_metrics["balanced_accuracy"]
        >= best_baseline + BASELINE_SUPERIORITY_MIN
    )


def _cluster_bootstrap_ba(
    records: list[dict[str, Any]],
    preds: list[bool],
) -> dict[str, Any]:
    seeds = sorted(set(int(r["seed"]) for r in records))
    by_seed = {s: [] for s in seeds}
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)

    rng = random.Random(BOOTSTRAP_SEED)
    values = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        idxs = [i for s in drawn for i in by_seed[s]]
        labels = [bool(records[i]["labels"]["SAFE_RESET_OPPORTUNITY"]) for i in idxs]
        pp = [preds[i] for i in idxs]
        if any(labels) and not all(labels):
            values.append(k656._metrics(labels, pp)["balanced_accuracy"])
    values.sort()
    if not values:
        return {"valid": False}
    lo_idx = int(0.025 * (len(values) - 1))
    hi_idx = int(0.975 * (len(values) - 1))
    return {
        "valid": True,
        "ci_lower": values[lo_idx],
        "ci_upper": values[hi_idx],
        "resamples_used": len(values),
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def run_discovery() -> dict[str, Any]:
    source = _load_discovery()
    if not source["valid"]:
        return {
            "experiment": "KCL-6.5.7-DISCOVERY",
            "status": "REVISE",
            "verdict": "RELATIONAL_BOUNDARY_STATE_INVALID",
            "reason": "canonical KCL-6.5.6 discovery evidence invalid",
        }

    records = source["records"]
    rbs = loso_representation(records)
    baselines = scalar_baselines(records)
    qualified = discovery_qualified(rbs["metrics"], baselines)

    ablations = {
        name: loso_representation(records, tuple(features))
        for name, features in ABLATIONS.items()
    }

    final_model = fit_representation(records)
    baseline_stage_rule = k656.fit_threshold(records, k656.STAGE_BASELINE)
    baseline_h4_rule = k656.fit_threshold(records, "H4_TASK_DRIFT_RELATIVE_L2")

    rule_artifact = None
    if qualified:
        rule_artifact = {
            "experiment": "KCL-6.5.7-RULE",
            "representation": "RBS-v1",
            "target": "SAFE_RESET_OPPORTUNITY",
            "base_order": list(BASE_ORDER),
            "feature_order": list(FEATURE_ORDER),
            "scaler": final_model["scaler"],
            "model": final_model["model"],
            "threshold": final_model["threshold"],
            "discovery_metrics": rbs["metrics"],
            "stage_baseline_rule": {
                "signal": baseline_stage_rule["signal"],
                "direction": baseline_stage_rule["direction"],
                "threshold": baseline_stage_rule["threshold"],
            },
            "H4_baseline_rule": {
                "signal": baseline_h4_rule["signal"],
                "direction": baseline_h4_rule["direction"],
                "threshold": baseline_h4_rule["threshold"],
            },
            "source_discovery_sha256": source["sha256"],
            "protocol_sha256": _sha256(PROTOCOL),
        }

    if qualified:
        status = "PASS"
        verdict = "DISCOVERY_RELATIONAL_BOUNDARY_STATE_SELECTED"
    else:
        status = "NEGATIVE"
        verdict = "RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED"

    best_ablation = max(
        (v["metrics"]["balanced_accuracy"], k)
        for k, v in ablations.items()
    )

    return {
        "experiment": "KCL-6.5.7-DISCOVERY",
        "status": status,
        "verdict": verdict,
        "representation": "RBS-v1",
        "source": {
            "path": str(KCL656_EVIDENCE),
            "sha256": source["sha256"],
            "instances": len(records),
            "seeds": list(DISCOVERY_SEEDS),
        },
        "rbs_v1": rbs,
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
        "best_ablation": {
            "name": best_ablation[1],
            "balanced_accuracy": best_ablation[0],
        },
        "final_discovery_model": final_model if qualified else None,
        "rule_artifact": rule_artifact,
        "integrity": {
            "valid": True,
            "confirmatory_seeds_absent": set(
                int(r["seed"]) for r in records
            ).isdisjoint(CONFIRM_SEEDS),
            "all_folds_hold_out_whole_seed": True,
            "fold_local_scaling": True,
            "fold_local_weights": True,
            "fold_local_threshold": True,
            "future_outcomes_not_used_as_features": True,
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def _rule_valid(rule: dict[str, Any], source_sha: str) -> bool:
    return (
        rule.get("experiment") == "KCL-6.5.7-RULE"
        and rule.get("representation") == "RBS-v1"
        and rule.get("target") == "SAFE_RESET_OPPORTUNITY"
        and rule.get("base_order") == list(BASE_ORDER)
        and rule.get("feature_order") == list(FEATURE_ORDER)
        and rule.get("source_discovery_sha256") == source_sha
        and rule.get("protocol_sha256") == _sha256(PROTOCOL)
    )


def _apply_scalar_rule(
    records: list[dict[str, Any]],
    rule: dict[str, Any],
) -> tuple[list[bool], dict[str, Any]]:
    preds = [
        k656._predict(
            float(r["features"][rule["signal"]]),
            rule["direction"],
            float(rule["threshold"]),
        )
        for r in records
    ]
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    return preds, k656._metrics(labels, preds)


def run_confirm(rule_path: Path) -> dict[str, Any]:
    source = _load_discovery()
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if not source["valid"] or not _rule_valid(rule, source["sha256"]):
        return {
            "experiment": "KCL-6.5.7-CONFIRM",
            "status": "REVISE",
            "verdict": "RELATIONAL_BOUNDARY_STATE_INVALID",
            "reason": "source/rule invalid",
        }

    config = k656.KCL1Config()
    records = [
        r
        for seed in CONFIRM_SEEDS
        for r in k656.build_boundary_records(seed, config)
    ]
    integrity = (
        len(records) == 60
        and all(r["integrity"]["valid"] for r in records)
        and set(int(r["seed"]) for r in records) == set(CONFIRM_SEEDS)
    )

    fitted = {
        "feature_names": rule["feature_order"],
        "scaler": rule["scaler"],
        "model": rule["model"],
        "threshold": rule["threshold"],
    }
    _, preds = predict_representation(records, fitted)
    labels = [bool(r["labels"]["SAFE_RESET_OPPORTUNITY"]) for r in records]
    metrics = k656._metrics(labels, preds)
    ci = _cluster_bootstrap_ba(records, preds)

    _, stage_metrics = _apply_scalar_rule(records, rule["stage_baseline_rule"])
    _, h4_metrics = _apply_scalar_rule(records, rule["H4_baseline_rule"])
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
        verdict = "RELATIONAL_BOUNDARY_STATE_INVALID"
    elif confirmed:
        status = "PASS"
        verdict = "RELATIONAL_BOUNDARY_STATE_QUALIFIED"
    else:
        status = "NEGATIVE"
        verdict = "RELATIONAL_BOUNDARY_STATE_NOT_GENERALIZED"

    return {
        "experiment": "KCL-6.5.7-CONFIRM",
        "status": status,
        "verdict": verdict,
        "representation": "RBS-v1",
        "cohort": {
            "seeds": list(CONFIRM_SEEDS),
            "instances": len(records),
        },
        "metrics": metrics,
        "balanced_accuracy_seed_bootstrap": ci,
        "baselines": {
            "stage": stage_metrics,
            "H4_drift": h4_metrics,
            "best_baseline_BA": best_baseline,
        },
        "stage_H4_superiority": metrics["balanced_accuracy"] - best_baseline,
        "label_counts": {
            "positive": sum(labels),
            "negative": sum(not x for x in labels),
        },
        "records": records,
        "integrity": {
            "valid": integrity,
            "rule_refit_on_confirmation": False,
            "scaler_refit_on_confirmation": False,
            "threshold_refit_on_confirmation": False,
            "counterfactual_integrity_all": all(
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
            raise SystemExit("--rule is required for confirm")
        result = run_confirm(Path(args.rule))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 3 if result["status"] == "REVISE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
