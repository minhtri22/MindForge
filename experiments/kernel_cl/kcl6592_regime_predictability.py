"""KCL-6.5.9.2 — Boundary Regime Predictability Qualification.

Two-stage execution:
  train    -> generate only frozen training seeds and freeze RPQ-v1 rule
  validate -> apply the already-frozen rule to frozen validation seeds

No controller is implemented. Protected confirmatory seeds remain untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from experiments.kernel_cl.kcl1_substrate import KCL1Config
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl659_boundary_regime_decomposition as k659
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6592-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6592_regime_predictability.py")

CLASS_ORDER = ("A_ONLY", "C_ONLY", "B_AND_C_SAFE", "B_ONLY")
PRIMARY_FEATURES = (
    "STAGE_2",
    "STAGE_3",
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
BASELINE_FEATURES = {
    "B_STAGE": ("STAGE_2", "STAGE_3"),
    "B_H4": ("H4_TASK_DRIFT_RELATIVE_L2",),
    "B_STAGE_H4": ("STAGE_2", "STAGE_3", "H4_TASK_DRIFT_RELATIVE_L2"),
}

TRAIN_SEEDS = (
857358,348434,468582,461139,473479,327035,376368,705271,378009,762246,530553,653483,799618,671805,556535,659145,373486,801628,834743,665330,830692,383139,448112,324812,448781,888462,883531,711545,875550,465689,856408,697066,614578,735005,529287,646853,528638,871673,822516,701571,457351,528572,783495,419315,845774,877397,851929,492207,826924,672086,498167,645017,310029,427666,718671,352185,414107,541624,390348,633150,345751,577928,511849,772521,789592,451590,363425,894707,423888,574921,851601,632470,302881,634338,557864,467365,342140,795434,379754,453294,603564,622086,326515,568333,817464,601779,795496,463602,614571,518648,655754,486850,798851,648142,638696,512088,717672,349969,519679,655889,765254,875709,531987,685908,701296,504219,334514,410848,528357,669199,554446,497698,419027,494564,544410,709276,795282,689126,872997,336152,814395,761781,737231,651805,677211,301391,345926,441301,332714,632994,472554,339215,641864,536651,579223,702505,843624,748965,730314,594138,621698,737680,676216,645867,718426,365404,617147,732718,869341,822746,825339,618354,699284,520741,748531,615493,304544,704801,502068,443342,394247,362756,666212,676263,775696,610769,705295,409438,346707,795604,367193,567522,463611,781026,573729,714292,447472,767857,798337,713339,570695,400614,584796,866480,529565,802765,656999,776014,409735,565714,533747,560722,435207,846906,890786,821404,317775,330665,738279,479078,514252,773216,655469,801139,850287,582985,865828,808042,511264,698003,521999,528443,834157,669881,350931,456619,368498,615812,433078,774212,736883,866007,821000,887108,813458,896365,509196,895686,426598,540180,749014,406612,562615,718200,311196,617622,811197,514044,869931,374540
)
VALIDATION_SEEDS = (
384891,314256,314740,727553,506172,608741,843687,486364,425737,330214,775722,325734,460280,480300,439813,726715,356352,499291,370753,647972,808425,575331,538327,506660,765810,620872,897523,517764,578334,425323,506256,442330,309925,628393,714826,639547,872908,451207,697314,811852,330684,469692,308074,561294,408157,534162,423691,814699,870274,559113,494592,488533,836183,706092,624263,346755,643663,438370,724657,350340,784596,629041,347772,713121,618230,858299,579744,838079,790316,472521,388908,591976,553827,769806,879361,746756,645486,838695,432484,533728,472072,603113,597733,322891,877808,577990,763710,680552,355772,392840,398325,882431,495882,873447,779476,396884,807818,782730,367545,728868,710558,564601,402575,612256,763601,570016,704251,523135,770290,783234,570147,397731,612432,597905,709599,503627,741049,779883,328666,318719
)

TRAIN_MIN_COUNT = 10
TRAIN_MIN_SEEDS = 10
VAL_MIN_COUNT = 5
VAL_MIN_SEEDS = 5

RIDGE_LAMBDA = 1.0
LBFGS_LR = 1.0
LBFGS_MAX_ITER = 200
LBFGS_HISTORY = 20
LBFGS_TOL_GRAD = 1e-9
LBFGS_TOL_CHANGE = 1e-12

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6592

QUAL_MACRO_RECALL = 0.60
QUAL_MACRO_F1 = 0.50
QUAL_CLASS_RECALL = 0.50
QUAL_CLASS_F1 = 0.35
QUAL_BASELINE_MARGIN = 0.05
QUAL_BOOTSTRAP_LOWER = 0.45


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def target_from_outcomes(outcomes: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    dec = k659.decompose_outcomes(outcomes)
    safe_b = bool(dec["safe_B"])
    safe_c = bool(dec["safe_C"])
    if safe_b and safe_c:
        label = "B_AND_C_SAFE"
    elif safe_b:
        label = "B_ONLY"
    elif safe_c:
        label = "C_ONLY"
    else:
        label = "A_ONLY"
    return label, {"safe_B": safe_b, "safe_C": safe_c}


def feature_value(record: dict[str, Any], name: str) -> float:
    if name == "STAGE_2":
        return 1.0 if int(record["boundary_index"]) == 2 else 0.0
    if name == "STAGE_3":
        return 1.0 if int(record["boundary_index"]) == 3 else 0.0
    return float(record["features"][name])


def build_records(seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    cfg = KCL1Config()
    out: list[dict[str, Any]] = []
    for seed in seeds:
        source = k656.build_boundary_records(seed, cfg)
        for row in source:
            label, flags = target_from_outcomes(row["counterfactual_outcomes"])
            out.append({
                "seed": int(seed),
                "boundary_index": int(row["boundary_index"]),
                "after_task": row.get("after_task"),
                "features": {k: float(v) for k, v in row["features"].items()},
                "target": label,
                "safe_flags": flags,
                "counterfactual_outcomes": row["counterfactual_outcomes"],
                "counterfactual_integrity_valid": bool(row["integrity"]["valid"]),
            })
    return out


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    table: dict[str, dict[str, Any]] = {}
    for cls in CLASS_ORDER:
        rr = [r for r in records if r["target"] == cls]
        table[cls] = {
            "count": len(rr),
            "unique_seed_count": len({int(r["seed"]) for r in rr}),
            "boundary_counts": dict(sorted(Counter(
                int(r["boundary_index"]) for r in rr
            ).items())),
        }
    return table


def support_pass(
    table: dict[str, dict[str, Any]],
    min_count: int,
    min_seeds: int,
) -> bool:
    return all(
        int(table[c]["count"]) >= min_count
        and int(table[c]["unique_seed_count"]) >= min_seeds
        for c in CLASS_ORDER
    )


def scaler_for(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...],
) -> dict[str, Any]:
    x = np.array(
        [[feature_value(r, n) for n in feature_names] for r in records],
        dtype=np.float64,
    )
    means = x.mean(axis=0)
    stds = np.maximum(x.std(axis=0, ddof=0), 1e-12)
    return {
        "feature_names": list(feature_names),
        "means": means.tolist(),
        "stds": stds.tolist(),
    }


def design(
    records: list[dict[str, Any]],
    scaler: dict[str, Any],
) -> np.ndarray:
    names = tuple(scaler["feature_names"])
    x = np.array(
        [[feature_value(r, n) for n in names] for r in records],
        dtype=np.float64,
    )
    means = np.asarray(scaler["means"], dtype=np.float64)
    stds = np.asarray(scaler["stds"], dtype=np.float64)
    return (x - means) / stds


def class_weights(records: list[dict[str, Any]]) -> dict[str, float]:
    counts = Counter(r["target"] for r in records)
    n = len(records)
    k = len(CLASS_ORDER)
    return {c: n / (k * counts[c]) for c in CLASS_ORDER}


def labels_array(records: list[dict[str, Any]]) -> np.ndarray:
    index = {c: i for i, c in enumerate(CLASS_ORDER)}
    return np.array([index[r["target"]] for r in records], dtype=np.int64)


def fit_softmax(
    records: list[dict[str, Any]],
    feature_names: tuple[str, ...],
) -> dict[str, Any]:
    scaler = scaler_for(records, feature_names)
    x_np = design(records, scaler)
    y_np = labels_array(records)
    cw = class_weights(records)

    x = torch.tensor(x_np, dtype=torch.float64)
    y = torch.tensor(y_np, dtype=torch.long)
    sample_w = torch.tensor(
        [cw[CLASS_ORDER[int(i)]] for i in y_np],
        dtype=torch.float64,
    )

    d = x.shape[1]
    k = len(CLASS_ORDER)
    w = torch.zeros((d, k), dtype=torch.float64, requires_grad=True)
    b = torch.zeros(k, dtype=torch.float64, requires_grad=True)

    opt = torch.optim.LBFGS(
        [w, b],
        lr=LBFGS_LR,
        max_iter=LBFGS_MAX_ITER,
        history_size=LBFGS_HISTORY,
        tolerance_grad=LBFGS_TOL_GRAD,
        tolerance_change=LBFGS_TOL_CHANGE,
        line_search_fn="strong_wolfe",
    )
    closure_calls = 0

    def loss_fn() -> torch.Tensor:
        logits = x @ w + b
        ce = torch.nn.functional.cross_entropy(logits, y, reduction="none")
        weighted = (ce * sample_w).sum() / sample_w.sum()
        penalty = 0.5 * RIDGE_LAMBDA * (w * w).sum()
        return weighted + penalty

    def closure() -> torch.Tensor:
        nonlocal closure_calls
        closure_calls += 1
        opt.zero_grad()
        loss = loss_fn()
        loss.backward()
        return loss

    opt.step(closure)

    opt.zero_grad()
    final_loss = loss_fn()
    final_loss.backward()
    grad_max = max(
        float(w.grad.detach().abs().max()),
        float(b.grad.detach().abs().max()),
    )
    finite = (
        math.isfinite(float(final_loss.detach()))
        and math.isfinite(grad_max)
        and torch.isfinite(w.detach()).all().item()
        and torch.isfinite(b.detach()).all().item()
    )
    converged = bool(finite and grad_max <= LBFGS_TOL_GRAD)

    return {
        "feature_names": list(feature_names),
        "scaler": scaler,
        "class_weights": cw,
        "weights": w.detach().cpu().numpy().tolist(),
        "intercepts": b.detach().cpu().numpy().tolist(),
        "solver": {
            "name": "torch.optim.LBFGS",
            "ridge_lambda": RIDGE_LAMBDA,
            "lr": LBFGS_LR,
            "max_iter": LBFGS_MAX_ITER,
            "history_size": LBFGS_HISTORY,
            "tolerance_grad": LBFGS_TOL_GRAD,
            "tolerance_change": LBFGS_TOL_CHANGE,
            "line_search_fn": "strong_wolfe",
            "closure_calls": closure_calls,
            "final_loss": float(final_loss.detach()),
            "final_grad_max": grad_max,
            "finite": bool(finite),
            "converged": converged,
        },
    }


def predict_model(
    records: list[dict[str, Any]],
    model: dict[str, Any],
) -> tuple[list[str], np.ndarray]:
    x = design(records, model["scaler"])
    w = np.asarray(model["weights"], dtype=np.float64)
    b = np.asarray(model["intercepts"], dtype=np.float64)
    logits = x @ w + b
    logits = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    probs = exp / exp.sum(axis=1, keepdims=True)
    idx = probs.argmax(axis=1)
    return [CLASS_ORDER[int(i)] for i in idx], probs


def metrics(
    records: list[dict[str, Any]],
    preds: list[str],
    probs: np.ndarray | None = None,
) -> dict[str, Any]:
    idx = {c: i for i, c in enumerate(CLASS_ORDER)}
    cm = np.zeros((len(CLASS_ORDER), len(CLASS_ORDER)), dtype=np.int64)
    true = [r["target"] for r in records]
    for y, p in zip(true, preds):
        cm[idx[y], idx[p]] += 1

    per = {}
    for c in CLASS_ORDER:
        i = idx[c]
        tp = int(cm[i, i])
        fn = int(cm[i, :].sum() - tp)
        fp = int(cm[:, i].sum() - tp)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
        per[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": tp + fn,
        }

    macro_precision = sum(per[c]["precision"] for c in CLASS_ORDER) / len(CLASS_ORDER)
    macro_recall = sum(per[c]["recall"] for c in CLASS_ORDER) / len(CLASS_ORDER)
    macro_f1 = sum(per[c]["f1"] for c in CLASS_ORDER) / len(CLASS_ORDER)
    accuracy = float(np.trace(cm) / cm.sum()) if cm.sum() else 0.0

    log_loss = None
    if probs is not None:
        y_idx = np.array([idx[y] for y in true], dtype=np.int64)
        chosen = np.clip(probs[np.arange(len(y_idx)), y_idx], 1e-15, 1.0)
        log_loss = float(-np.log(chosen).mean())

    return {
        "confusion_matrix": cm.tolist(),
        "class_order": list(CLASS_ORDER),
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "log_loss": log_loss,
        "per_class": per,
    }


def bootstrap_validation(
    records: list[dict[str, Any]],
    preds: list[str],
    probs: np.ndarray,
) -> dict[str, Any]:
    by_seed: dict[int, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)
    seeds = list(VALIDATION_SEEDS)
    rng = random.Random(BOOTSTRAP_SEED)
    vals = {"macro_recall": [], "macro_f1": [], "accuracy": []}

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        ii = [i for s in drawn for i in by_seed[s]]
        rr = [records[i] for i in ii]
        pp = [preds[i] for i in ii]
        pr = probs[ii, :]
        m = metrics(rr, pp, pr)
        for key in vals:
            vals[key].append(float(m[key]))

    out = {}
    for key, arr in vals.items():
        a = np.sort(np.asarray(arr, dtype=np.float64))
        out[key] = {
            "ci_lower": float(np.percentile(a, 2.5, method="linear")),
            "ci_upper": float(np.percentile(a, 97.5, method="linear")),
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
        }
    return out


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    prior = (
        set(k656.DISCOVERY_SEEDS)
        | set(k656.CONFIRM_SEEDS)
        | set(k6591.REPLICATION_SEEDS)
    )
    return set(seeds).isdisjoint(prior)


def cohort_integrity(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
    expected_records: int,
) -> dict[str, bool]:
    counts = Counter(int(r["seed"]) for r in records)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))
    finite = all(
        all(math.isfinite(float(v)) for v in r["features"].values())
        for r in records
    )
    valid_target = all(r["target"] in CLASS_ORDER for r in records)
    return {
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(boundaries[s] == {1, 2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "counterfactual_integrity_valid": all(
            r["counterfactual_integrity_valid"] for r in records
        ),
        "features_finite": finite,
        "target_valid": valid_target,
    }


def model_metrics_on_train(
    records: list[dict[str, Any]],
    model: dict[str, Any],
) -> dict[str, Any]:
    preds, probs = predict_model(records, model)
    return metrics(records, preds, probs)


def run_train(output: Path, rule_path: Path) -> dict[str, Any]:
    if set(TRAIN_SEEDS) & set(VALIDATION_SEEDS):
        raise RuntimeError("train/validation seed overlap")

    records = build_records(TRAIN_SEEDS)
    integ = cohort_integrity(records, TRAIN_SEEDS, 720)
    integ["validation_seeds_executed"] = False
    integ["protected_confirmatory_touched"] = False
    integ["kcl7_started"] = False

    support = support_table(records)
    support_ok = support_pass(support, TRAIN_MIN_COUNT, TRAIN_MIN_SEEDS)

    if not all(v for k, v in integ.items() if k not in {
        "validation_seeds_executed",
        "protected_confirmatory_touched",
        "kcl7_started",
    }) or integ["validation_seeds_executed"] or integ["protected_confirmatory_touched"] or integ["kcl7_started"]:
        result = {
            "experiment": "KCL-6.5.9.2-TRAIN",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_PREDICTABILITY_INVALID",
            "integrity": integ,
            "support": support,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    if not support_ok:
        result = {
            "experiment": "KCL-6.5.9.2-TRAIN",
            "status": "NEGATIVE",
            "verdict": "REGIME_PREDICTABILITY_TRAIN_SUPPORT_INSUFFICIENT",
            "support": support,
            "integrity": integ,
            "records": records,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    primary = fit_softmax(records, PRIMARY_FEATURES)
    baselines = {
        name: fit_softmax(records, features)
        for name, features in BASELINE_FEATURES.items()
    }
    solver_ok = primary["solver"]["converged"] and all(
        m["solver"]["converged"] for m in baselines.values()
    )
    integ["all_solvers_converged"] = bool(solver_ok)

    if not solver_ok:
        result = {
            "experiment": "KCL-6.5.9.2-TRAIN",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_PREDICTABILITY_INVALID",
            "reason": "frozen solver did not converge",
            "support": support,
            "integrity": integ,
            "primary_solver": primary["solver"],
            "baseline_solvers": {k: v["solver"] for k, v in baselines.items()},
            "records": records,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    train_metrics = {
        "RPQ_V1": model_metrics_on_train(records, primary),
        **{
            name: model_metrics_on_train(records, model)
            for name, model in baselines.items()
        },
    }
    majority = Counter(r["target"] for r in records).most_common(1)[0][0]
    majority_metrics = metrics(records, [majority] * len(records), None)

    result = {
        "experiment": "KCL-6.5.9.2-TRAIN",
        "status": "PASS",
        "verdict": "REGIME_PREDICTOR_TRAINED_AND_READY_TO_FREEZE",
        "cohort": {"seeds": list(TRAIN_SEEDS), "records": len(records)},
        "support": support,
        "train_metrics": train_metrics,
        "majority_baseline": {
            "class": majority,
            "metrics": majority_metrics,
        },
        "integrity": integ,
        "records": records,
        "protocol": {
            "path": str(PROTOCOL),
            "sha256": sha256_file(PROTOCOL),
        },
        "environment": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    train_sha = sha256_file(output)

    rule = {
        "experiment": "KCL-6.5.9.2-RULE",
        "status": "FROZEN_FROM_TRAIN_ONLY",
        "target": "SAFE_ACTION_SET-v1",
        "class_order": list(CLASS_ORDER),
        "truth_table": {
            "A_ONLY": {"safe_B": False, "safe_C": False},
            "C_ONLY": {"safe_B": False, "safe_C": True},
            "B_AND_C_SAFE": {"safe_B": True, "safe_C": True},
            "B_ONLY": {"safe_B": True, "safe_C": False},
        },
        "train_seeds": list(TRAIN_SEEDS),
        "validation_seeds": list(VALIDATION_SEEDS),
        "primary_feature_order": list(PRIMARY_FEATURES),
        "baseline_feature_sets": {
            k: list(v) for k, v in BASELINE_FEATURES.items()
        },
        "RPQ_V1": primary,
        "baselines": baselines,
        "training_support": support,
        "training_metrics": train_metrics,
        "protocol_sha256": sha256_file(PROTOCOL),
        "training_evidence_sha256": train_sha,
        "script_sha256": sha256_file(SCRIPT),
        "source_git_commit": git_commit(),
        "solver_contract": {
            "ridge_lambda": RIDGE_LAMBDA,
            "class_weight_formula": "N/(K*n_c)",
            "argmax_prediction": True,
        },
        "qualification_gates": {
            "macro_recall_min": QUAL_MACRO_RECALL,
            "macro_f1_min": QUAL_MACRO_F1,
            "per_class_recall_min": QUAL_CLASS_RECALL,
            "per_class_f1_min": QUAL_CLASS_F1,
            "baseline_macro_recall_margin": QUAL_BASELINE_MARGIN,
            "bootstrap_macro_recall_lower_strictly_gt": QUAL_BOOTSTRAP_LOWER,
            "val_min_count_per_class": VAL_MIN_COUNT,
            "val_min_unique_seeds_per_class": VAL_MIN_SEEDS,
        },
        "governance": {
            "validation_executed_before_freeze": False,
            "protected_confirmatory_touched": False,
            "controller_implemented": False,
            "kcl7_started": False,
        },
    }
    rule_path.write_text(json.dumps(rule, indent=2, sort_keys=True) + "\n")
    return result


def validate_rule(rule: dict[str, Any]) -> bool:
    return (
        rule.get("experiment") == "KCL-6.5.9.2-RULE"
        and rule.get("status") == "FROZEN_FROM_TRAIN_ONLY"
        and tuple(rule.get("class_order", [])) == CLASS_ORDER
        and tuple(rule.get("train_seeds", [])) == TRAIN_SEEDS
        and tuple(rule.get("validation_seeds", [])) == VALIDATION_SEEDS
        and tuple(rule.get("primary_feature_order", [])) == PRIMARY_FEATURES
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and rule.get("governance", {}).get("validation_executed_before_freeze") is False
        and rule.get("governance", {}).get("protected_confirmatory_touched") is False
        and rule.get("governance", {}).get("controller_implemented") is False
        and rule.get("governance", {}).get("kcl7_started") is False
    )


def qualification(
    primary: dict[str, Any],
    baselines: dict[str, dict[str, Any]],
    bootstrap: dict[str, Any],
    support_ok: bool,
) -> tuple[bool, list[str], float]:
    failed: list[str] = []
    if not support_ok:
        failed.append("validation_class_support")
    if primary["macro_recall"] < QUAL_MACRO_RECALL:
        failed.append("macro_recall")
    if primary["macro_f1"] < QUAL_MACRO_F1:
        failed.append("macro_f1")
    for cls in CLASS_ORDER:
        if primary["per_class"][cls]["recall"] < QUAL_CLASS_RECALL:
            failed.append(f"recall:{cls}")
        if primary["per_class"][cls]["f1"] < QUAL_CLASS_F1:
            failed.append(f"f1:{cls}")
    best_baseline = max(m["macro_recall"] for m in baselines.values())
    if primary["macro_recall"] < best_baseline + QUAL_BASELINE_MARGIN:
        failed.append("baseline_superiority")
    if bootstrap["macro_recall"]["ci_lower"] <= QUAL_BOOTSTRAP_LOWER:
        failed.append("bootstrap_macro_recall_lower")
    return len(failed) == 0, failed, best_baseline


def run_validate(rule_path: Path, output: Path) -> dict[str, Any]:
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    rule_sha = sha256_file(rule_path)
    if not validate_rule(rule):
        result = {
            "experiment": "KCL-6.5.9.2-VALIDATION",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_PREDICTABILITY_INVALID",
            "reason": "frozen rule contract invalid",
            "rule_sha256": rule_sha,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    records = build_records(VALIDATION_SEEDS)
    integ = cohort_integrity(records, VALIDATION_SEEDS, 360)
    integ.update({
        "train_validation_overlap_absent": set(TRAIN_SEEDS).isdisjoint(VALIDATION_SEEDS),
        "rule_loaded_without_refit": True,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })
    positive_required = {
        k: v for k, v in integ.items()
        if k not in {
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = (
        integ["protected_confirmatory_touched"] is False
        and integ["controller_implemented"] is False
        and integ["kcl7_started"] is False
    )
    if not all(positive_required.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.2-VALIDATION",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_PREDICTABILITY_INVALID",
            "integrity": integ,
            "rule_sha256": rule_sha,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    support = support_table(records)
    support_ok = support_pass(support, VAL_MIN_COUNT, VAL_MIN_SEEDS)

    primary_preds, primary_probs = predict_model(records, rule["RPQ_V1"])
    primary_metrics = metrics(records, primary_preds, primary_probs)

    baseline_metrics: dict[str, dict[str, Any]] = {}
    for name, model in rule["baselines"].items():
        preds, probs = predict_model(records, model)
        baseline_metrics[name] = metrics(records, preds, probs)

    majority = Counter(
        {c: int(rule["training_support"][c]["count"]) for c in CLASS_ORDER}
    ).most_common(1)[0][0]
    majority_metrics = metrics(records, [majority] * len(records), None)

    bootstrap = bootstrap_validation(records, primary_preds, primary_probs)
    qualified, failed, best_baseline = qualification(
        primary_metrics, baseline_metrics, bootstrap, support_ok
    )

    if not support_ok:
        status = "NEGATIVE"
        verdict = "REGIME_PREDICTABILITY_VALIDATION_SUPPORT_INSUFFICIENT"
    elif qualified:
        status = "PASS"
        verdict = "BOUNDARY_REGIME_PREDICTOR_QUALIFIED"
    else:
        status = "NEGATIVE"
        verdict = "BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED"

    result = {
        "experiment": "KCL-6.5.9.2-VALIDATION",
        "status": status,
        "verdict": verdict,
        "cohort": {"seeds": list(VALIDATION_SEEDS), "records": len(records)},
        "support": support,
        "RPQ_V1": primary_metrics,
        "baselines": baseline_metrics,
        "majority_baseline": {
            "class": majority,
            "metrics": majority_metrics,
        },
        "bootstrap_95pct": bootstrap,
        "qualification": {
            "qualified": qualified,
            "failed_gates": failed,
            "best_baseline_macro_recall": best_baseline,
            "required_margin": QUAL_BASELINE_MARGIN,
            "gates": rule["qualification_gates"],
        },
        "integrity": integ,
        "rule": {
            "path": str(rule_path),
            "sha256": rule_sha,
            "source_git_commit": rule["source_git_commit"],
            "training_evidence_sha256": rule["training_evidence_sha256"],
        },
        "protocol": {
            "path": str(PROTOCOL),
            "sha256": sha256_file(PROTOCOL),
        },
        "records": [
            {
                **r,
                "prediction": p,
                "probabilities": {
                    c: float(primary_probs[i, j])
                    for j, c in enumerate(CLASS_ORDER)
                },
            }
            for i, (r, p) in enumerate(zip(records, primary_preds))
        ],
        "environment": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
        },
        "governance": {
            "refit_on_validation": False,
            "protected_confirmatory_touched": False,
            "controller_implemented": False,
            "kcl7_started": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "validate"), required=True)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--rule",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl6592_rule.json"),
    )
    args = parser.parse_args()

    if args.phase == "train":
        result = run_train(args.output, args.rule)
    else:
        result = run_validate(args.rule, args.output)

    summary = {
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "support": result.get("support"),
        "train_metrics": result.get("train_metrics"),
        "RPQ_V1": result.get("RPQ_V1"),
        "baselines": result.get("baselines"),
        "bootstrap_95pct": result.get("bootstrap_95pct"),
        "qualification": result.get("qualification"),
        "integrity": result.get("integrity"),
        "rule": result.get("rule"),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
