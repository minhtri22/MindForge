"""KCL-6.5.9.5 — Mechanism-Specific Target Identifiability.

Prospective two-phase comparison of the monolithic A_ONLY target against the two
stably replicated KCL-6.5.9.4 mechanism targets. No controller is implemented.
"""

from __future__ import annotations

import argparse
import copy
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

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    optimizer_for,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl658_localized_boundary_state as k658
from experiments.kernel_cl import kcl659_boundary_regime_decomposition as k659
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592
from experiments.kernel_cl import kcl6593_action_identifiability as k6593
from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6595-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6595_mechanism_target_identifiability.py")

TARGET_A = "Y_A"
TARGET_PR = "Y_PR"
TARGET_PRR = "Y_PRR"
TARGETS = (TARGET_A, TARGET_PR, TARGET_PRR)
CLASS_ORDER = ("NEG", "POS")

MECH_PR = "MECH{P,R}"
MECH_PRR = "MECH{P+R,R}"

S0_FEATURES = ("STAGE_2", "STAGE_3")
S1_FEATURES = k6592.PRIMARY_FEATURES
S2_FEATURES = S1_FEATURES + tuple(f"F{i}" for i in range(1, 14))
FEATURE_SETS = {
    "S0": S0_FEATURES,
    "S1": S1_FEATURES,
    "S2": S2_FEATURES,
}

_generated = random.Random(6595).sample(range(3_000_001, 5_000_000), 720)
TRAIN_SEEDS = tuple(_generated[:480])
VALIDATION_SEEDS = tuple(_generated[480:])
ALL_SEED_SHA256 = "5463cd9804c8f4e857a5e5a32a85119f0ab459e5857dcc6a5123123c28b22318"
TRAIN_SEED_SHA256 = "9ed96c29e86613ac10572f4079b080c5ae70638aa70c3080b4d1773e1736e2d7"
VALIDATION_SEED_SHA256 = "c4f5b8d112cc8fbe7235a22e32ccfe33dcca0c265baca496c440a1517c67df0d"

TRAIN_MIN_COUNT = 50
TRAIN_MIN_SEEDS = 40
VAL_MIN_COUNT = 25
VAL_MIN_SEEDS = 20

RIDGE_LAMBDA = 1.0
LBFGS_LR = 1.0
LBFGS_MAX_ITER = 200
LBFGS_HISTORY = 20
LBFGS_TOL_GRAD = 1e-9
LBFGS_TOL_CHANGE = 1e-12

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6595

QUAL_MACRO_RECALL = 0.60
QUAL_MACRO_F1 = 0.50
QUAL_CLASS_RECALL = 0.50
QUAL_CLASS_F1 = 0.35
QUAL_BOOTSTRAP_LOWER = 0.45

GAIN_POINT_MIN = 0.10
GAIN_CI_LOWER_MIN = 0.03


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_seed_list(seeds: tuple[int, ...] | list[int]) -> str:
    return hashlib.sha256(",".join(map(str, seeds)).encode("utf-8")).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def prior_seed_set() -> set[int]:
    return (
        set(k656.DISCOVERY_SEEDS)
        | set(k656.CONFIRM_SEEDS)
        | set(k6591.REPLICATION_SEEDS)
        | set(k6592.TRAIN_SEEDS)
        | set(k6592.VALIDATION_SEEDS)
        | set(k6593.TRAIN_SEEDS)
        | set(k6593.VALIDATION_SEEDS)
        | set(k6594.DISCOVERY_SEEDS)
        | set(k6594.REPLICATION_SEEDS)
    )


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    return set(seeds).isdisjoint(prior_seed_set())


def mechanism_from_outcomes(outcomes: dict[str, Any]) -> tuple[str, str | None]:
    dec = k659.decompose_outcomes(outcomes)
    if bool(dec["safe_B"]) or bool(dec["safe_C"]):
        return k6592.target_from_outcomes(outcomes)[0], None

    bcomp = dec["policy_components"][k659.B]
    ccomp = dec["policy_components"][k659.C]
    code_b = k6594.cause_code(k6594.failure_reasons(bcomp))
    code_c = k6594.cause_code(k6594.failure_reasons(ccomp))
    return "A_ONLY", k6594.mechanism_signature(code_b, code_c)


def labels_from_outcomes(outcomes: dict[str, Any]) -> dict[str, bool]:
    action_target, mechanism = mechanism_from_outcomes(outcomes)
    a_only = action_target == "A_ONLY"
    labels = {
        TARGET_A: a_only,
        TARGET_PR: a_only and mechanism == MECH_PR,
        TARGET_PRR: a_only and mechanism == MECH_PRR,
    }
    if labels[TARGET_PR] and not labels[TARGET_A]:
        raise RuntimeError("Y_PR is not a subset of Y_A")
    if labels[TARGET_PRR] and not labels[TARGET_A]:
        raise RuntimeError("Y_PRR is not a subset of Y_A")
    return labels


def build_records(seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    cfg = KCL1Config()
    out: list[dict[str, Any]] = []

    for seed in seeds:
        tasks = task_sequence(cfg)
        model = build_model(cfg, seed)
        opt = optimizer_for(model, cfg)
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

        for boundary_index in (1, 2, 3):
            current_task = observed[-1]
            global_features = k656.extract_boundary_features(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                current_task=current_task,
                boundary_index=boundary_index,
            )
            localized = k658.extract_localized_features(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                boundary_index=boundary_index,
            )

            features = {k: float(v) for k, v in global_features.items()}
            for name in tuple(f"F{i}" for i in range(1, 14)):
                features[name] = float(localized["features"][name])

            next_task = tasks[boundary_index]
            counter = k656.run_next_task_counterfactual(
                model=model,
                optimizer=opt,
                memories=memories,
                observed_tasks=observed,
                next_task=next_task,
                seed=seed,
                next_stage=boundary_index + 1,
                config=cfg,
            )
            labels = labels_from_outcomes(counter["outcomes"])
            action_target, mechanism = mechanism_from_outcomes(counter["outcomes"])
            share_sums = localized["details"]["share_sums"]
            lrbs_shares_valid = all(
                abs(float(share_sums[name]) - 1.0) <= 1e-9
                for name in ("drift", "pressure", "retention")
            )

            out.append({
                "seed": int(seed),
                "boundary_index": int(boundary_index),
                "after_task": current_task[0],
                "features": features,
                "labels": labels,
                "action_target": action_target,
                "mechanism_signature": mechanism,
                "counterfactual_outcomes": counter["outcomes"],
                "integrity": {
                    "counterfactual_valid": bool(counter["integrity"]["valid"]),
                    "lrbs_shares_valid": bool(lrbs_shares_valid),
                },
            })

            pre_task_model_state = copy.deepcopy(model.state_dict())
            model = counter["_reference_model"]
            opt = counter["_reference_optimizer"]
            memories = counter["_next_memories"]
            observed = tasks[: boundary_index + 1]

    return out


def feature_value(record: dict[str, Any], name: str) -> float:
    if name == "STAGE_2":
        return 1.0 if int(record["boundary_index"]) == 2 else 0.0
    if name == "STAGE_3":
        return 1.0 if int(record["boundary_index"]) == 3 else 0.0
    return float(record["features"][name])


def binary_class(record: dict[str, Any], target: str) -> str:
    return "POS" if bool(record["labels"][target]) else "NEG"


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for target in TARGETS:
        per: dict[str, Any] = {}
        for cls in CLASS_ORDER:
            rr = [r for r in records if binary_class(r, target) == cls]
            per[cls] = {
                "count": len(rr),
                "unique_seed_count": len({int(r["seed"]) for r in rr}),
                "boundary_counts": dict(sorted(Counter(
                    int(r["boundary_index"]) for r in rr
                ).items())),
            }
        out[target] = per
    return out


def support_pass(
    table: dict[str, dict[str, Any]],
    *,
    min_count: int,
    min_seeds: int,
) -> bool:
    return all(
        int(table[target][cls]["count"]) >= min_count
        and int(table[target][cls]["unique_seed_count"]) >= min_seeds
        for target in TARGETS
        for cls in CLASS_ORDER
    )


def cohort_integrity(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
    expected_records: int,
    expected_seed_sha: str,
) -> dict[str, bool]:
    counts = Counter(int(r["seed"]) for r in records)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))

    return {
        "seed_sha_matches": sha_seed_list(seeds) == expected_seed_sha,
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(boundaries[s] == {1, 2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "train_validation_disjoint": set(TRAIN_SEEDS).isdisjoint(VALIDATION_SEEDS),
        "features_finite": all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        ),
        "counterfactual_integrity_valid": all(
            r["integrity"]["counterfactual_valid"] for r in records
        ),
        "lrbs_shares_valid": all(
            r["integrity"]["lrbs_shares_valid"] for r in records
        ),
        "mechanism_targets_subset_A_ONLY": all(
            (not r["labels"][TARGET_PR] or r["labels"][TARGET_A])
            and (not r["labels"][TARGET_PRR] or r["labels"][TARGET_A])
            for r in records
        ),
        "stable_mechanism_names_exact": all(
            (
                r["mechanism_signature"] is None
                or isinstance(r["mechanism_signature"], str)
            )
            for r in records
        ),
        "future_probe_absent": all(
            not any(k.startswith("P") and "_NEXT_" in k for k in r["features"])
            for r in records
        ),
    }


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


def design(records: list[dict[str, Any]], scaler: dict[str, Any]) -> np.ndarray:
    names = tuple(scaler["feature_names"])
    x = np.array(
        [[feature_value(r, n) for n in names] for r in records],
        dtype=np.float64,
    )
    means = np.asarray(scaler["means"], dtype=np.float64)
    stds = np.asarray(scaler["stds"], dtype=np.float64)
    return (x - means) / stds


def fit_binary(
    records: list[dict[str, Any]],
    target: str,
    feature_names: tuple[str, ...],
) -> dict[str, Any]:
    scaler = scaler_for(records, feature_names)
    x_np = design(records, scaler)
    y_labels = [binary_class(r, target) for r in records]
    idx = {c: i for i, c in enumerate(CLASS_ORDER)}
    y_np = np.asarray([idx[x] for x in y_labels], dtype=np.int64)
    counts = Counter(y_labels)
    n = len(records)
    k = len(CLASS_ORDER)
    cw = {c: n / (k * counts[c]) for c in CLASS_ORDER}

    x = torch.tensor(x_np, dtype=torch.float64)
    y = torch.tensor(y_np, dtype=torch.long)
    sample_w = torch.tensor(
        [cw[CLASS_ORDER[int(i)]] for i in y_np],
        dtype=torch.float64,
    )

    d = x.shape[1]
    w = torch.zeros((d, 2), dtype=torch.float64, requires_grad=True)
    b = torch.zeros(2, dtype=torch.float64, requires_grad=True)

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
        return weighted + 0.5 * RIDGE_LAMBDA * (w * w).sum()

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
    finite = bool(
        math.isfinite(float(final_loss.detach()))
        and math.isfinite(grad_max)
        and torch.isfinite(w.detach()).all().item()
        and torch.isfinite(b.detach()).all().item()
    )
    state = opt.state.get(w, {})
    n_iter = int(state.get("n_iter", LBFGS_MAX_ITER))
    converged = bool(
        finite and (grad_max <= LBFGS_TOL_GRAD or n_iter < LBFGS_MAX_ITER)
    )

    return {
        "target": target,
        "class_order": list(CLASS_ORDER),
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
            "n_iter": n_iter,
            "final_loss": float(final_loss.detach()),
            "final_grad_max": grad_max,
            "finite": finite,
            "converged": converged,
        },
    }


def predict_binary(
    records: list[dict[str, Any]],
    model: dict[str, Any],
) -> tuple[list[str], np.ndarray]:
    x = design(records, model["scaler"])
    w = np.asarray(model["weights"], dtype=np.float64)
    b = np.asarray(model["intercepts"], dtype=np.float64)
    logits = x @ w + b
    logits -= logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    probs = exp / exp.sum(axis=1, keepdims=True)
    ii = probs.argmax(axis=1)
    return [CLASS_ORDER[int(i)] for i in ii], probs


def metrics_binary(
    records: list[dict[str, Any]],
    target: str,
    preds: list[str],
    probs: np.ndarray | None = None,
) -> dict[str, Any]:
    idx = {c: i for i, c in enumerate(CLASS_ORDER)}
    cm = np.zeros((2, 2), dtype=np.int64)
    true = [binary_class(r, target) for r in records]
    for y, p in zip(true, preds):
        cm[idx[y], idx[p]] += 1

    per: dict[str, Any] = {}
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

    macro_precision = sum(per[c]["precision"] for c in CLASS_ORDER) / 2
    macro_recall = sum(per[c]["recall"] for c in CLASS_ORDER) / 2
    macro_f1 = sum(per[c]["f1"] for c in CLASS_ORDER) / 2
    accuracy = float(np.trace(cm) / cm.sum()) if cm.sum() else 0.0

    log_loss = None
    if probs is not None:
        yi = np.asarray([idx[y] for y in true], dtype=np.int64)
        chosen = np.clip(probs[np.arange(len(yi)), yi], 1e-15, 1.0)
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


def fit_all(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        target: {
            arm: fit_binary(records, target, features)
            for arm, features in FEATURE_SETS.items()
        }
        for target in TARGETS
    }


def metrics_all(
    records: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, list[str]]],
    dict[str, dict[str, np.ndarray]],
]:
    metrics: dict[str, dict[str, Any]] = {}
    preds: dict[str, dict[str, list[str]]] = {}
    probs: dict[str, dict[str, np.ndarray]] = {}
    for target in TARGETS:
        metrics[target], preds[target], probs[target] = {}, {}, {}
        for arm in FEATURE_SETS:
            p, pr = predict_binary(records, models[target][arm])
            preds[target][arm] = p
            probs[target][arm] = pr
            metrics[target][arm] = metrics_binary(records, target, p, pr)
    return metrics, preds, probs


def _percentile(values: list[float], q: float) -> float:
    return float(np.percentile(
        np.asarray(values, dtype=np.float64),
        q,
        method="linear",
    ))


def paired_bootstrap(
    records: list[dict[str, Any]],
    preds: dict[str, dict[str, list[str]]],
    probs: dict[str, dict[str, np.ndarray]],
) -> dict[str, Any]:
    seeds = sorted({int(r["seed"]) for r in records})
    by_seed: dict[int, list[int]] = {s: [] for s in seeds}
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    arm_recall = {
        target: {arm: [] for arm in FEATURE_SETS}
        for target in TARGETS
    }
    deltas = {"D_PR": [], "D_PRR": []}

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = rng.integers(0, len(seeds), size=len(seeds))
        idxs = [i for j in drawn for i in by_seed[seeds[int(j)]]]
        rr = [records[i] for i in idxs]
        s2_mr: dict[str, float] = {}

        for target in TARGETS:
            for arm in FEATURE_SETS:
                pp = [preds[target][arm][i] for i in idxs]
                pr = probs[target][arm][idxs, :]
                m = metrics_binary(rr, target, pp, pr)
                mr = float(m["macro_recall"])
                arm_recall[target][arm].append(mr)
                if arm == "S2":
                    s2_mr[target] = mr

        deltas["D_PR"].append(s2_mr[TARGET_PR] - s2_mr[TARGET_A])
        deltas["D_PRR"].append(s2_mr[TARGET_PRR] - s2_mr[TARGET_A])

    arms: dict[str, Any] = {}
    for target in TARGETS:
        arms[target] = {}
        for arm in FEATURE_SETS:
            vals = arm_recall[target][arm]
            arms[target][arm] = {
                "macro_recall": {
                    "ci_lower": _percentile(vals, 2.5),
                    "ci_upper": _percentile(vals, 97.5),
                }
            }

    delta_out = {
        name: {
            "ci_lower": _percentile(vals, 2.5),
            "ci_upper": _percentile(vals, 97.5),
        }
        for name, vals in deltas.items()
    }
    return {
        "arms": arms,
        "deltas": delta_out,
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
    }


def qualified(
    metrics: dict[str, Any],
    bootstrap_arm: dict[str, Any],
) -> bool:
    return bool(
        metrics["macro_recall"] >= QUAL_MACRO_RECALL
        and metrics["macro_f1"] >= QUAL_MACRO_F1
        and all(
            metrics["per_class"][c]["recall"] >= QUAL_CLASS_RECALL
            and metrics["per_class"][c]["f1"] >= QUAL_CLASS_F1
            for c in CLASS_ORDER
        )
        and bootstrap_arm["macro_recall"]["ci_lower"] > QUAL_BOOTSTRAP_LOWER
    )


def adjudicate(
    metrics: dict[str, dict[str, Any]],
    bootstrap: dict[str, Any],
) -> dict[str, Any]:
    q = {
        target: qualified(
            metrics[target]["S2"],
            bootstrap["arms"][target]["S2"],
        )
        for target in TARGETS
    }
    mr_a = float(metrics[TARGET_A]["S2"]["macro_recall"])
    d_pr = float(metrics[TARGET_PR]["S2"]["macro_recall"]) - mr_a
    d_prr = float(metrics[TARGET_PRR]["S2"]["macro_recall"]) - mr_a

    gain_pr = bool(
        q[TARGET_PR]
        and d_pr >= GAIN_POINT_MIN
        and bootstrap["deltas"]["D_PR"]["ci_lower"] > GAIN_CI_LOWER_MIN
    )
    gain_prr = bool(
        q[TARGET_PRR]
        and d_prr >= GAIN_POINT_MIN
        and bootstrap["deltas"]["D_PRR"]["ci_lower"] > GAIN_CI_LOWER_MIN
    )

    if gain_pr and gain_prr:
        status = "PASS"
        verdict = "BOTH_REPLICATED_MECHANISM_TARGETS_MORE_IDENTIFIABLE_THAN_A_ONLY"
    elif gain_pr or gain_prr:
        status = "NEGATIVE"
        verdict = "MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN_NOT_GENERALIZED_ACROSS_BOTH_TARGETS"
    else:
        status = "NEGATIVE"
        verdict = "NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN"

    return {
        "status": status,
        "verdict": verdict,
        "qualified_S2": q,
        "routes": {
            "H_PR": gain_pr,
            "H_PRR": gain_prr,
        },
        "point_deltas_macro_recall": {
            "D_PR": d_pr,
            "D_PRR": d_prr,
        },
        "frozen_gain_thresholds": {
            "point_delta_min": GAIN_POINT_MIN,
            "bootstrap_ci_lower_min": GAIN_CI_LOWER_MIN,
        },
    }


def rule_payload(
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "rule": "MSTI-v1",
        "experiment": "KCL-6.5.9.5",
        "targets": list(TARGETS),
        "stable_mechanisms": [MECH_PR, MECH_PRR],
        "feature_sets": {k: list(v) for k, v in FEATURE_SETS.items()},
        "primary_feature_set": "S2",
        "models": models,
        "protocol_sha256": sha256_file(PROTOCOL),
        "script_sha256": sha256_file(SCRIPT),
        "training_seed_sha256": sha_seed_list(TRAIN_SEEDS),
        "source_git_commit": git_commit(),
        "validation_executed_before_freeze": False,
        "controller_implemented": False,
        "protected_confirmatory_touched": False,
        "kcl7_started": False,
    }


def run_train(output: Path, rule_path: Path) -> dict[str, Any]:
    records = build_records(TRAIN_SEEDS)
    integrity = cohort_integrity(
        records,
        TRAIN_SEEDS,
        expected_records=1440,
        expected_seed_sha=TRAIN_SEED_SHA256,
    )
    integrity.update({
        "all_seed_sha_matches": sha_seed_list(
            tuple(list(TRAIN_SEEDS) + list(VALIDATION_SEEDS))
        ) == ALL_SEED_SHA256,
        "validation_seeds_executed": False,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })

    support = support_table(records)
    support_ok = support_pass(
        support,
        min_count=TRAIN_MIN_COUNT,
        min_seeds=TRAIN_MIN_SEEDS,
    )

    hard_integrity = {
        k: v for k, v in integrity.items()
        if k not in {
            "validation_seeds_executed",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_seeds_executed"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard_integrity.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.5-TRAIN",
            "status": "REVISE",
            "verdict": "MECHANISM_TARGET_IDENTIFIABILITY_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.5-TRAIN",
            "status": "NEGATIVE",
            "verdict": "MECHANISM_TARGET_TRAIN_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "records": records,
        }
    else:
        models = fit_all(records)
        solver_ok = all(
            models[target][arm]["solver"]["converged"]
            for target in TARGETS
            for arm in FEATURE_SETS
        )
        integrity["all_solvers_converged"] = solver_ok

        if not solver_ok:
            result = {
                "experiment": "KCL-6.5.9.5-TRAIN",
                "status": "REVISE",
                "verdict": "MECHANISM_TARGET_IDENTIFIABILITY_INVALID",
                "reason": "frozen solver did not converge",
                "integrity": integrity,
                "support": support,
                "solver": {
                    t: {a: models[t][a]["solver"] for a in FEATURE_SETS}
                    for t in TARGETS
                },
                "records": records,
            }
        else:
            metrics, _, _ = metrics_all(records, models)
            rule = rule_payload(models)
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            rule_path.write_text(
                json.dumps(rule, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            result = {
                "experiment": "KCL-6.5.9.5-TRAIN",
                "status": "PASS",
                "verdict": "MECHANISM_TARGET_MODELS_TRAINED_AND_READY_TO_FREEZE",
                "integrity": integrity,
                "support": support,
                "train_metrics_descriptive": metrics,
                "rule": {
                    "path": str(rule_path),
                    "sha256": sha256_file(rule_path),
                },
                "records": records,
                "protocol_sha256": sha256_file(PROTOCOL),
                "script_sha256": sha256_file(SCRIPT),
                "source_git_commit": git_commit(),
                "environment": {"python": platform.python_version()},
                "governance": {
                    "validation_executed": False,
                    "controller_implemented": False,
                    "protected_confirmatory_touched": False,
                    "kcl7_started": False,
                },
            }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def validate_rule(rule: dict[str, Any]) -> bool:
    return bool(
        rule.get("rule") == "MSTI-v1"
        and rule.get("targets") == list(TARGETS)
        and rule.get("stable_mechanisms") == [MECH_PR, MECH_PRR]
        and rule.get("primary_feature_set") == "S2"
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and rule.get("script_sha256") == sha256_file(SCRIPT)
        and rule.get("training_seed_sha256") == TRAIN_SEED_SHA256
        and rule.get("validation_executed_before_freeze") is False
        and rule.get("controller_implemented") is False
        and rule.get("protected_confirmatory_touched") is False
        and rule.get("kcl7_started") is False
        and set(rule.get("models", {})) == set(TARGETS)
        and all(
            set(rule["models"][t]) == set(FEATURE_SETS)
            for t in TARGETS
        )
    )


def run_validation(
    output: Path,
    rule_path: Path,
) -> dict[str, Any]:
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if not validate_rule(rule):
        result = {
            "experiment": "KCL-6.5.9.5-VALIDATION",
            "status": "REVISE",
            "verdict": "MECHANISM_TARGET_IDENTIFIABILITY_INVALID",
            "reason": "frozen rule contract invalid",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    records = build_records(VALIDATION_SEEDS)
    integrity = cohort_integrity(
        records,
        VALIDATION_SEEDS,
        expected_records=720,
        expected_seed_sha=VALIDATION_SEED_SHA256,
    )
    integrity.update({
        "rule_valid": True,
        "validation_refit": False,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })
    support = support_table(records)
    support_ok = support_pass(
        support,
        min_count=VAL_MIN_COUNT,
        min_seeds=VAL_MIN_SEEDS,
    )

    hard_integrity = {
        k: v for k, v in integrity.items()
        if k not in {
            "validation_refit",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_refit"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard_integrity.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.5-VALIDATION",
            "status": "REVISE",
            "verdict": "MECHANISM_TARGET_IDENTIFIABILITY_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.5-VALIDATION",
            "status": "NEGATIVE",
            "verdict": "MECHANISM_TARGET_VALIDATION_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "records": records,
        }
    else:
        models = rule["models"]
        metrics, preds, probs = metrics_all(records, models)
        bootstrap = paired_bootstrap(records, preds, probs)
        adj = adjudicate(metrics, bootstrap)
        secondary = {
            target: {
                "S2_minus_S0_macro_recall": (
                    metrics[target]["S2"]["macro_recall"]
                    - metrics[target]["S0"]["macro_recall"]
                ),
                "S2_minus_S1_macro_recall": (
                    metrics[target]["S2"]["macro_recall"]
                    - metrics[target]["S1"]["macro_recall"]
                ),
            }
            for target in TARGETS
        }
        result = {
            "experiment": "KCL-6.5.9.5-VALIDATION",
            **adj,
            "integrity": integrity,
            "support": support,
            "metrics": metrics,
            "bootstrap": bootstrap,
            "secondary_diagnostics": secondary,
            "rule": {
                "path": str(rule_path),
                "sha256": sha256_file(rule_path),
                "source_git_commit": rule.get("source_git_commit"),
            },
            "records": records,
            "protocol_sha256": sha256_file(PROTOCOL),
            "script_sha256": sha256_file(SCRIPT),
            "source_git_commit": git_commit(),
            "environment": {"python": platform.python_version()},
            "governance": {
                "validation_refit": False,
                "controller_implemented": False,
                "protected_confirmatory_touched": False,
                "kcl7_started": False,
            },
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "validate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--rule",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl6595_rule.json"),
    )
    args = parser.parse_args()

    if args.phase == "train":
        result = run_train(args.output, args.rule)
    else:
        result = run_validation(args.output, args.rule)

    print(json.dumps({
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "support": result.get("support"),
        "integrity": result.get("integrity"),
        "qualified_S2": result.get("qualified_S2"),
        "routes": result.get("routes"),
        "point_deltas_macro_recall": result.get("point_deltas_macro_recall"),
        "metrics": result.get("metrics"),
        "secondary_diagnostics": result.get("secondary_diagnostics"),
        "rule": result.get("rule"),
    }, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
