"""KCL-6.5.9.7 — Temporal Mechanistic Representation Qualification.

Tests TRIG-v1, a history-only temporal reset-interference representation,
against the frozen static S3 definition. No future-task leakage and no
controller.
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
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl658_localized_boundary_state as k658
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592
from experiments.kernel_cl import kcl6593_action_identifiability as k6593
from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594
from experiments.kernel_cl import kcl6595_mechanism_target_identifiability as k6595
from experiments.kernel_cl import kcl6596_mechanistic_representation as k6596

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6597-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6597_temporal_mechanistic_representation.py")

TARGET_A = k6595.TARGET_A
TARGET_PR = k6595.TARGET_PR
TARGET_PRR = k6595.TARGET_PRR
TARGETS = (TARGET_A, TARGET_PR, TARGET_PRR)
CLASS_ORDER = k6595.CLASS_ORDER

S3_FEATURES = k6596.S3_FEATURES
TRIG_FEATURES = (
    "Q1_CURRENT_GRAD_ROTATION",
    "Q2_RETENTION_GRAD_ROTATION",
    "Q3_MIN_TRANSFER_PLASTICITY_CONTRAST",
    "Q4_MAX_TRANSFER_PLASTICITY_CONTRAST",
    "Q5_TRANSFER_PLASTICITY_GAP",
    "Q6_MIN_TRANSFER_RETENTION_CONTRAST",
    "Q7_MAX_TRANSFER_RETENTION_CONTRAST",
    "Q8_TRANSFER_RETENTION_GAP",
    "Q9_PLASTICITY_GAP_DELTA",
    "Q10_RETENTION_GAP_DELTA",
    "Q11_BOTH_RETENTION_BADNESS_DELTA",
    "Q12_STEP_SCALE_GAP_DELTA",
)
S4_FEATURES = S3_FEATURES + TRIG_FEATURES
FEATURE_SETS = {"S3": S3_FEATURES, "S4": S4_FEATURES}

_generated = random.Random(6597).sample(range(7_000_001, 10_000_000), 1080)
TRAIN_SEEDS = tuple(_generated[:720])
VALIDATION_SEEDS = tuple(_generated[720:])
ALL_SEED_SHA256 = "8afb9745bdb6d7c7d0c7973076a486867a42cb5d232cd1d9db18a920b96667b3"
TRAIN_SEED_SHA256 = "7fcd7b700060d22d1d4adae3534db7835a3c3425b78a736309d391f283335025"
VALIDATION_SEED_SHA256 = "86508c96cc1872e7a171324192642ae09be6532f44dfb7f3a38acbb4b70736c7"

TRAIN_MIN_COUNT = 50
TRAIN_MIN_SEEDS = 40
VAL_MIN_COUNT = 25
VAL_MIN_SEEDS = 20

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6597

GAIN_POINT_MIN = 0.10
GAIN_CI_LOWER_MIN = 0.03
EPS = 1e-12


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
        | set(k6595.TRAIN_SEEDS)
        | set(k6595.VALIDATION_SEEDS)
        | set(k6596.TRAIN_SEEDS)
        | set(k6596.VALIDATION_SEEDS)
    )


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    return set(seeds).isdisjoint(prior_seed_set())


def _norm(x: torch.Tensor) -> float:
    return float(torch.linalg.vector_norm(x))


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = _norm(a) * _norm(b)
    if denom <= 1e-20:
        return 0.0
    return float(torch.dot(a, b) / denom)


def build_probe_bundle(
    *,
    seed: int,
    boundary_index: int,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    config: KCL1Config,
    current_task: tuple[torch.Tensor, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
) -> dict[str, Any]:
    model_before = copy.deepcopy(model.state_dict())
    opt_before = copy.deepcopy(optimizer.state_dict())

    grads = k6596.observed_gradients(
        model=model,
        current_task=current_task,
        observed_tasks=observed_tasks,
    )
    g_cur = k6596._flatten_named(grads["current"], model)
    g_ret = k6596._flatten_named(grads["retention"], model)

    gcur_sq = float(torch.dot(g_cur, g_cur))
    gret_sq = float(torch.dot(g_ret, g_ret))
    gcur_norm = _norm(g_cur)

    responses: dict[str, dict[str, float]] = {}
    updates: dict[str, torch.Tensor] = {}
    policy_integrity = {}

    for policy in k655.POLICIES:
        vr = k6596.virtual_policy_update(
            model=model,
            optimizer=optimizer,
            config=config,
            policy=policy,
            gradient=grads["current"],
        )
        u = vr["update"].detach().clone()
        updates[policy] = u
        responses[policy] = {
            "adaptation_response": float(
                -torch.dot(g_cur, u) / (gcur_sq + EPS)
            ),
            "retention_cost": float(
                torch.dot(g_ret, u) / (gret_sq + EPS)
            ),
            "step_scale": float(
                torch.linalg.vector_norm(u) / (gcur_norm + EPS)
            ),
        }
        policy_integrity[policy] = bool(
            vr["finite"] and vr["boundary_info"]["model_unchanged"]
        )

    mrig = k6596.mrigr_features_from_responses(
        _cosine(g_cur, g_ret),
        responses,
    )

    model_unchanged = all(
        torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    optimizer_unchanged = k655._deep_equal(
        opt_before,
        optimizer.state_dict(),
    )
    gradients_cleared = all(p.grad is None for p in model.parameters())

    return {
        "seed": int(seed),
        "boundary_index": int(boundary_index),
        "g_cur": g_cur.detach().clone(),
        "g_ret": g_ret.detach().clone(),
        "updates": updates,
        "mrig_features": mrig,
        "responses": responses,
        "integrity": {
            "gradient_model_unchanged": bool(grads["model_unchanged"]),
            "gradient_cleanup_valid": bool(grads["gradients_cleared"]),
            "original_model_unchanged": bool(model_unchanged),
            "original_optimizer_unchanged": bool(optimizer_unchanged),
            "gradients_cleared": bool(gradients_cleared),
            "virtual_updates_valid": all(policy_integrity.values()),
        },
    }


def temporal_features(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, float]:
    if int(current["boundary_index"]) != int(previous["boundary_index"]) + 1:
        raise RuntimeError("temporal probe is not immediately consecutive")
    if int(current["seed"]) != int(previous["seed"]):
        raise RuntimeError("temporal probe seed mismatch")

    g_cur = current["g_cur"]
    g_ret = current["g_ret"]

    x: dict[str, float] = {}
    y: dict[str, float] = {}
    for policy in k655.POLICIES:
        u = previous["updates"][policy]
        denom_x = _norm(g_cur) * _norm(u) + EPS
        denom_y = _norm(g_ret) * _norm(u) + EPS
        x[policy] = float(-torch.dot(g_cur, u) / denom_x)
        y[policy] = float(torch.dot(g_ret, u) / denom_y)

    A, B, C = k655.POLICIES
    dx_b = x[B] - x[A]
    dx_c = x[C] - x[A]
    dy_b = y[B] - y[A]
    dy_c = y[C] - y[A]

    pm = previous["mrig_features"]
    cm = current["mrig_features"]

    out = {
        "Q1_CURRENT_GRAD_ROTATION": _cosine(previous["g_cur"], g_cur),
        "Q2_RETENTION_GRAD_ROTATION": _cosine(previous["g_ret"], g_ret),
        "Q3_MIN_TRANSFER_PLASTICITY_CONTRAST": min(dx_b, dx_c),
        "Q4_MAX_TRANSFER_PLASTICITY_CONTRAST": max(dx_b, dx_c),
        "Q5_TRANSFER_PLASTICITY_GAP": abs(dx_b - dx_c),
        "Q6_MIN_TRANSFER_RETENTION_CONTRAST": min(dy_b, dy_c),
        "Q7_MAX_TRANSFER_RETENTION_CONTRAST": max(dy_b, dy_c),
        "Q8_TRANSFER_RETENTION_GAP": abs(dy_b - dy_c),
        "Q9_PLASTICITY_GAP_DELTA": (
            cm["M6_PLASTICITY_CONTRAST_GAP"]
            - pm["M6_PLASTICITY_CONTRAST_GAP"]
        ),
        "Q10_RETENTION_GAP_DELTA": (
            cm["M7_RETENTION_CONTRAST_GAP"]
            - pm["M7_RETENTION_CONTRAST_GAP"]
        ),
        "Q11_BOTH_RETENTION_BADNESS_DELTA": (
            cm["M8_BOTH_RETENTION_BADNESS"]
            - pm["M8_BOTH_RETENTION_BADNESS"]
        ),
        "Q12_STEP_SCALE_GAP_DELTA": (
            cm["M10_STEP_SCALE_LOG_GAP"]
            - pm["M10_STEP_SCALE_LOG_GAP"]
        ),
    }
    if not all(math.isfinite(float(v)) for v in out.values()):
        raise RuntimeError("non-finite TRIG-v1 feature")
    return out


def temporal_exchange_symmetric(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> bool:
    base = temporal_features(previous, current)
    A, B, C = k655.POLICIES
    swapped = {
        **previous,
        "updates": {
            A: previous["updates"][A],
            B: previous["updates"][C],
            C: previous["updates"][B],
        },
    }
    other = temporal_features(swapped, current)
    return all(
        abs(float(base[k]) - float(other[k])) <= 1e-15
        for k in TRIG_FEATURES
    )


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
        previous_probe: dict[str, Any] | None = None

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
            probe = build_probe_bundle(
                seed=seed,
                boundary_index=boundary_index,
                model=model,
                optimizer=opt,
                config=cfg,
                current_task=current_task[1],
                observed_tasks=observed,
            )

            features = {k: float(v) for k, v in global_features.items()}
            for name in tuple(f"F{i}" for i in range(1, 14)):
                features[name] = float(localized["features"][name])
            features.update({
                k: float(v) for k, v in probe["mrig_features"].items()
            })

            temporal = None
            temporal_symmetry = True
            history_lineage_valid = True
            if boundary_index >= 2:
                if previous_probe is None:
                    raise RuntimeError("missing previous probe")
                temporal = temporal_features(previous_probe, probe)
                temporal_symmetry = temporal_exchange_symmetric(
                    previous_probe,
                    probe,
                )
                history_lineage_valid = bool(
                    previous_probe["seed"] == seed
                    and previous_probe["boundary_index"] == boundary_index - 1
                )
                features.update(temporal)

            # Future task is bound only after current static + temporal features exist.
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

            if boundary_index >= 2:
                labels = k6595.labels_from_outcomes(counter["outcomes"])
                action_target, mechanism = k6595.mechanism_from_outcomes(
                    counter["outcomes"]
                )
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
                    "temporal_diagnostics": {
                        "previous_boundary_index": int(
                            previous_probe["boundary_index"]
                        ),
                        "current_boundary_index": int(boundary_index),
                    },
                    "counterfactual_outcomes": counter["outcomes"],
                    "integrity": {
                        "counterfactual_valid": bool(
                            counter["integrity"]["valid"]
                        ),
                        "lrbs_shares_valid": bool(lrbs_shares_valid),
                        "history_lineage_valid": bool(history_lineage_valid),
                        "temporal_exchange_symmetric": bool(
                            temporal_symmetry
                        ),
                        "no_previous_counterfactual_history_used": True,
                        **{
                            f"probe_{k}": bool(v)
                            for k, v in probe["integrity"].items()
                        },
                        **{
                            f"previous_probe_{k}": bool(v)
                            for k, v in previous_probe["integrity"].items()
                        },
                    },
                })

            previous_probe = probe

            pre_task_model_state = copy.deepcopy(model.state_dict())
            model = counter["_reference_model"]
            opt = counter["_reference_optimizer"]
            memories = counter["_next_memories"]
            observed = tasks[: boundary_index + 1]

    return out


def binary_class(record: dict[str, Any], target: str) -> str:
    return "POS" if bool(record["labels"][target]) else "NEG"


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for target in TARGETS:
        out[target] = {}
        for cls in CLASS_ORDER:
            rr = [r for r in records if binary_class(r, target) == cls]
            out[target][cls] = {
                "count": len(rr),
                "unique_seed_count": len({int(r["seed"]) for r in rr}),
                "boundary_counts": dict(sorted(Counter(
                    int(r["boundary_index"]) for r in rr
                ).items())),
            }
    return out


def primary_support_pass(
    table: dict[str, dict[str, Any]],
    *,
    min_count: int,
    min_seeds: int,
) -> bool:
    return all(
        int(table[TARGET_PRR][cls]["count"]) >= min_count
        and int(table[TARGET_PRR][cls]["unique_seed_count"]) >= min_seeds
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

    bool_integrities = [
        bool(v)
        for r in records
        for v in r["integrity"].values()
        if isinstance(v, bool)
    ]

    return {
        "seed_sha_matches": sha_seed_list(seeds) == expected_seed_sha,
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "two_records_per_seed": all(counts[s] == 2 for s in seeds),
        "boundaries_2_3_per_seed": all(boundaries[s] == {2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "train_validation_disjoint": set(TRAIN_SEEDS).isdisjoint(
            VALIDATION_SEEDS
        ),
        "features_finite": all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        ),
        "trig_features_exact": all(
            all(k in r["features"] for k in TRIG_FEATURES)
            for r in records
        ),
        "history_integrity_valid": all(bool_integrities),
        "mechanism_targets_subset_A_ONLY": all(
            (not r["labels"][TARGET_PR] or r["labels"][TARGET_A])
            and (not r["labels"][TARGET_PRR] or r["labels"][TARGET_A])
            for r in records
        ),
        "future_probe_absent": all(
            not any("_NEXT_" in k for k in r["features"])
            for r in records
        ),
    }


def fit_all(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        target: {
            arm: k6595.fit_binary(records, target, features)
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
            p, pr = k6595.predict_binary(records, models[target][arm])
            preds[target][arm] = p
            probs[target][arm] = pr
            metrics[target][arm] = k6595.metrics_binary(
                records,
                target,
                p,
                pr,
            )
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
    recall = {
        target: {arm: [] for arm in FEATURE_SETS}
        for target in TARGETS
    }
    deltas = {"D_TRIG": [], "D_PR": [], "D_A": []}

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = rng.integers(0, len(seeds), size=len(seeds))
        idxs = [i for j in drawn for i in by_seed[seeds[int(j)]]]
        rr = [records[i] for i in idxs]
        mr: dict[str, dict[str, float]] = {}

        for target in TARGETS:
            mr[target] = {}
            for arm in FEATURE_SETS:
                pp = [preds[target][arm][i] for i in idxs]
                pr = probs[target][arm][idxs, :]
                m = k6595.metrics_binary(rr, target, pp, pr)
                value = float(m["macro_recall"])
                recall[target][arm].append(value)
                mr[target][arm] = value

        deltas["D_TRIG"].append(
            mr[TARGET_PRR]["S4"] - mr[TARGET_PRR]["S3"]
        )
        deltas["D_PR"].append(
            mr[TARGET_PR]["S4"] - mr[TARGET_PR]["S3"]
        )
        deltas["D_A"].append(
            mr[TARGET_A]["S4"] - mr[TARGET_A]["S3"]
        )

    arms = {
        target: {
            arm: {
                "macro_recall": {
                    "ci_lower": _percentile(recall[target][arm], 2.5),
                    "ci_upper": _percentile(recall[target][arm], 97.5),
                }
            }
            for arm in FEATURE_SETS
        }
        for target in TARGETS
    }
    delta_out = {
        name: {
            "ci_lower": _percentile(values, 2.5),
            "ci_upper": _percentile(values, 97.5),
        }
        for name, values in deltas.items()
    }
    return {
        "arms": arms,
        "deltas": delta_out,
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
    }


def adjudicate(
    metrics: dict[str, dict[str, Any]],
    bootstrap: dict[str, Any],
) -> dict[str, Any]:
    q_s3 = k6595.qualified(
        metrics[TARGET_PRR]["S3"],
        bootstrap["arms"][TARGET_PRR]["S3"],
    )
    q_s4 = k6595.qualified(
        metrics[TARGET_PRR]["S4"],
        bootstrap["arms"][TARGET_PRR]["S4"],
    )
    delta = (
        float(metrics[TARGET_PRR]["S4"]["macro_recall"])
        - float(metrics[TARGET_PRR]["S3"]["macro_recall"])
    )
    gain = bool(
        q_s4
        and delta >= GAIN_POINT_MIN
        and bootstrap["deltas"]["D_TRIG"]["ci_lower"] > GAIN_CI_LOWER_MIN
    )

    if gain:
        status = "PASS"
        verdict = "TRIG_V1_QUALIFIES_TEMPORAL_MECH_PRR_REPRESENTATION"
    elif q_s4:
        status = "NEGATIVE"
        verdict = "TRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S3"
    else:
        status = "NEGATIVE"
        verdict = "TRIG_V1_DOES_NOT_QUALIFY_TEMPORAL_MECH_PRR_REPRESENTATION"

    return {
        "status": status,
        "verdict": verdict,
        "primary": {
            "S3_qualified": bool(q_s3),
            "S4_qualified": bool(q_s4),
            "D_TRIG": delta,
            "route_pass": gain,
            "point_gain_min": GAIN_POINT_MIN,
            "bootstrap_ci_lower_min": GAIN_CI_LOWER_MIN,
        },
    }


def trig_feature_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in TRIG_FEATURES:
        arr = np.asarray(
            [float(r["features"][name]) for r in records],
            dtype=np.float64,
        )
        out[name] = {
            "mean": float(arr.mean()),
            "std": float(arr.std(ddof=0)),
            "min": float(arr.min()),
            "max": float(arr.max()),
        }
    return out


def boundary_metrics(
    records: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    out = {}
    for boundary in (2, 3):
        rr = [r for r in records if int(r["boundary_index"]) == boundary]
        out[str(boundary)] = {}
        for arm in FEATURE_SETS:
            p, pr = k6595.predict_binary(rr, models[TARGET_PRR][arm])
            out[str(boundary)][arm] = k6595.metrics_binary(
                rr,
                TARGET_PRR,
                p,
                pr,
            )
    return out


def rule_payload(
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "rule": "TRIG-Q-v1",
        "experiment": "KCL-6.5.9.7",
        "primary_target": TARGET_PRR,
        "diagnostic_targets": [TARGET_PR, TARGET_A],
        "eligible_boundaries": [2, 3],
        "feature_sets": {k: list(v) for k, v in FEATURE_SETS.items()},
        "trig_features": list(TRIG_FEATURES),
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
    support_ok = primary_support_pass(
        support,
        min_count=TRAIN_MIN_COUNT,
        min_seeds=TRAIN_MIN_SEEDS,
    )

    hard = {
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

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.7-TRAIN",
            "status": "REVISE",
            "verdict": "TRIG_V1_TRAIN_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.7-TRAIN",
            "status": "NEGATIVE",
            "verdict": "TRIG_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "trig_feature_summary": trig_feature_summary(records),
            "records": records,
        }
    else:
        models = fit_all(records)
        solver_ok = all(
            models[target][arm]["solver"]["converged"]
            for target in TARGETS
            for arm in FEATURE_SETS
        )
        integrity["all_solvers_converged"] = bool(solver_ok)

        if not solver_ok:
            result = {
                "experiment": "KCL-6.5.9.7-TRAIN",
                "status": "REVISE",
                "verdict": "TRIG_V1_TRAIN_INVALID",
                "reason": "frozen solver did not converge",
                "integrity": integrity,
                "support": support,
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
                "experiment": "KCL-6.5.9.7-TRAIN",
                "status": "PASS",
                "verdict": "TRIG_V1_MODELS_TRAINED_AND_READY_TO_FREEZE",
                "integrity": integrity,
                "support": support,
                "train_metrics_descriptive": metrics,
                "trig_feature_summary": trig_feature_summary(records),
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
        rule.get("rule") == "TRIG-Q-v1"
        and rule.get("experiment") == "KCL-6.5.9.7"
        and rule.get("primary_target") == TARGET_PRR
        and rule.get("diagnostic_targets") == [TARGET_PR, TARGET_A]
        and rule.get("eligible_boundaries") == [2, 3]
        and rule.get("trig_features") == list(TRIG_FEATURES)
        and rule.get("feature_sets") == {
            k: list(v) for k, v in FEATURE_SETS.items()
        }
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and rule.get("script_sha256") == sha256_file(SCRIPT)
        and rule.get("training_seed_sha256") == TRAIN_SEED_SHA256
        and rule.get("validation_executed_before_freeze") is False
        and rule.get("controller_implemented") is False
        and rule.get("protected_confirmatory_touched") is False
        and rule.get("kcl7_started") is False
        and set(rule.get("models", {})) == set(TARGETS)
        and all(
            set(rule["models"][target]) == set(FEATURE_SETS)
            for target in TARGETS
        )
    )


def run_validation(output: Path, rule_path: Path) -> dict[str, Any]:
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if not validate_rule(rule):
        result = {
            "experiment": "KCL-6.5.9.7-VALIDATION",
            "status": "REVISE",
            "verdict": "TRIG_V1_VALIDATION_INVALID",
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
    support_ok = primary_support_pass(
        support,
        min_count=VAL_MIN_COUNT,
        min_seeds=VAL_MIN_SEEDS,
    )

    hard = {
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

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.7-VALIDATION",
            "status": "REVISE",
            "verdict": "TRIG_V1_VALIDATION_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.7-VALIDATION",
            "status": "NEGATIVE",
            "verdict": "TRIG_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "trig_feature_summary": trig_feature_summary(records),
            "records": records,
        }
    else:
        models = rule["models"]
        metrics, preds, probs = metrics_all(records, models)
        bootstrap = paired_bootstrap(records, preds, probs)
        adj = adjudicate(metrics, bootstrap)
        secondary = {
            "D_PR": (
                metrics[TARGET_PR]["S4"]["macro_recall"]
                - metrics[TARGET_PR]["S3"]["macro_recall"]
            ),
            "D_A": (
                metrics[TARGET_A]["S4"]["macro_recall"]
                - metrics[TARGET_A]["S3"]["macro_recall"]
            ),
            "boundary_metrics_Y_PRR": boundary_metrics(records, models),
        }
        result = {
            "experiment": "KCL-6.5.9.7-VALIDATION",
            **adj,
            "integrity": integrity,
            "support": support,
            "metrics": metrics,
            "bootstrap": bootstrap,
            "secondary_diagnostics": secondary,
            "trig_feature_summary": trig_feature_summary(records),
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
        default=Path("experiments/kernel_cl/results/kcl6597_rule.json"),
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
        "primary": result.get("primary"),
        "metrics": result.get("metrics"),
        "bootstrap": result.get("bootstrap"),
        "secondary_diagnostics": result.get("secondary_diagnostics"),
        "trig_feature_summary": result.get("trig_feature_summary"),
        "rule": result.get("rule"),
    }, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
