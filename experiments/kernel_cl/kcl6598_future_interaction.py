"""KCL-6.5.9.8 — Mechanism-Specific Future-Interaction Qualification.

Terminal active KCL-6.5.9.x information-class discriminator. Compares frozen
pre-boundary S2 against S2 plus the exact pre-existing FUTURE-PROBE-v1 P1-P8
on the replicated MECH{P+R,R} target. No controller.
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
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592
from experiments.kernel_cl import kcl6593_action_identifiability as k6593
from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594
from experiments.kernel_cl import kcl6595_mechanism_target_identifiability as k6595
from experiments.kernel_cl import kcl6596_mechanistic_representation as k6596
from experiments.kernel_cl import kcl6597_temporal_mechanistic_representation as k6597

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6598-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6598_future_interaction.py")

TARGET_A = k6595.TARGET_A
TARGET_PR = k6595.TARGET_PR
TARGET_PRR = k6595.TARGET_PRR
TARGETS = k6595.TARGETS
CLASS_ORDER = k6595.CLASS_ORDER

S2_FEATURES = k6595.S2_FEATURES
PROBE_FEATURES = k6593.PROBE_FEATURES
FUT_FEATURES = S2_FEATURES + PROBE_FEATURES
FEATURE_SETS = {"S2": S2_FEATURES, "FUT": FUT_FEATURES}

_generated = random.Random(6598).sample(range(10_000_001, 12_000_000), 720)
TRAIN_SEEDS = tuple(_generated[:480])
VALIDATION_SEEDS = tuple(_generated[480:])
ALL_SEED_SHA256 = "6071784d3447116db94576f93ae55c8bfc00aa5b67582b4a3ca65461bcc9c222"
TRAIN_SEED_SHA256 = "12478ab48bb834c536c652e5d89cd03d1e701518e774f70d5fde6483f2df45e9"
VALIDATION_SEED_SHA256 = "866c24667f3c2ea4d5317fc4f6c40e9050c255b00e65e4129e5026320a3f7f49"

TRAIN_MIN_COUNT = 50
TRAIN_MIN_SEEDS = 40
VAL_MIN_COUNT = 25
VAL_MIN_SEEDS = 20

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6598
GAIN_POINT_MIN = 0.15
GAIN_CI_LOWER_MIN = 0.05


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
        | set(k6597.TRAIN_SEEDS)
        | set(k6597.VALIDATION_SEEDS)
    )


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    return set(seeds).isdisjoint(prior_seed_set())


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

            next_task = tasks[boundary_index]
            probe = k6593.extract_future_probe(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                next_task=next_task[1],
            )

            features = {k: float(v) for k, v in global_features.items()}
            for name in tuple(f"F{i}" for i in range(1, 14)):
                features[name] = float(localized["features"][name])
            features.update({
                k: float(v) for k, v in probe["features"].items()
            })

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
                "counterfactual_outcomes": counter["outcomes"],
                "integrity": {
                    "counterfactual_valid": bool(
                        counter["integrity"]["valid"]
                    ),
                    "lrbs_shares_valid": bool(lrbs_shares_valid),
                    "probe_model_unchanged": bool(
                        probe["details"]["model_unchanged"]
                    ),
                    "probe_optimizer_unchanged": bool(
                        probe["details"]["optimizer_unchanged"]
                    ),
                    "probe_gradients_cleared": bool(
                        probe["details"]["gradients_cleared"]
                    ),
                },
            })

            pre_task_model_state = copy.deepcopy(model.state_dict())
            model = counter["_reference_model"]
            opt = counter["_reference_optimizer"]
            memories = counter["_next_memories"]
            observed = tasks[: boundary_index + 1]

    return out


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return k6595.support_table(records)


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

    return {
        "seed_sha_matches": sha_seed_list(seeds) == expected_seed_sha,
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(
            boundaries[s] == {1, 2, 3} for s in seeds
        ),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "train_validation_disjoint": set(TRAIN_SEEDS).isdisjoint(
            VALIDATION_SEEDS
        ),
        "features_finite": all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        ),
        "probe_features_exact": all(
            all(name in r["features"] for name in PROBE_FEATURES)
            for r in records
        ),
        "probe_model_unchanged": all(
            r["integrity"]["probe_model_unchanged"] for r in records
        ),
        "probe_optimizer_unchanged": all(
            r["integrity"]["probe_optimizer_unchanged"] for r in records
        ),
        "probe_gradients_cleared": all(
            r["integrity"]["probe_gradients_cleared"] for r in records
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
                records, target, p, pr
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
    recalls = {
        target: {arm: [] for arm in FEATURE_SETS}
        for target in TARGETS
    }
    deltas = {"D_FUTURE": [], "D_PR": [], "D_A": []}

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
                recalls[target][arm].append(value)
                mr[target][arm] = value

        deltas["D_FUTURE"].append(
            mr[TARGET_PRR]["FUT"] - mr[TARGET_PRR]["S2"]
        )
        deltas["D_PR"].append(
            mr[TARGET_PR]["FUT"] - mr[TARGET_PR]["S2"]
        )
        deltas["D_A"].append(
            mr[TARGET_A]["FUT"] - mr[TARGET_A]["S2"]
        )

    arms = {
        target: {
            arm: {
                "macro_recall": {
                    "ci_lower": _percentile(recalls[target][arm], 2.5),
                    "ci_upper": _percentile(recalls[target][arm], 97.5),
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
    q_s2 = k6595.qualified(
        metrics[TARGET_PRR]["S2"],
        bootstrap["arms"][TARGET_PRR]["S2"],
    )
    q_fut = k6595.qualified(
        metrics[TARGET_PRR]["FUT"],
        bootstrap["arms"][TARGET_PRR]["FUT"],
    )
    delta = (
        float(metrics[TARGET_PRR]["FUT"]["macro_recall"])
        - float(metrics[TARGET_PRR]["S2"]["macro_recall"])
    )
    gain = bool(
        q_fut
        and delta >= GAIN_POINT_MIN
        and bootstrap["deltas"]["D_FUTURE"]["ci_lower"]
        > GAIN_CI_LOWER_MIN
    )

    if gain and not q_s2:
        status = "PASS"
        verdict = (
            "FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED_FOR_MECH_PRR"
        )
    elif gain and q_s2:
        status = "PASS"
        verdict = "FUTURE_INTERACTION_MATERIAL_GAIN_FOR_MECH_PRR"
    elif q_fut:
        status = "NEGATIVE"
        verdict = "FUTURE_INTERACTION_QUALIFIED_BUT_NO_MATERIAL_GAIN"
    else:
        status = "NEGATIVE"
        verdict = "FUTURE_INTERACTION_DOES_NOT_QUALIFY_MECH_PRR"

    return {
        "status": status,
        "verdict": verdict,
        "primary": {
            "S2_qualified": bool(q_s2),
            "FUT_qualified": bool(q_fut),
            "D_FUTURE": delta,
            "route_pass": bool(gain),
            "point_gain_min": GAIN_POINT_MIN,
            "bootstrap_ci_lower_min": GAIN_CI_LOWER_MIN,
        },
    }


def probe_feature_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in PROBE_FEATURES:
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
    out: dict[str, Any] = {}
    for boundary in (1, 2, 3):
        rr = [r for r in records if int(r["boundary_index"]) == boundary]
        out[str(boundary)] = {}
        for arm in FEATURE_SETS:
            p, pr = k6595.predict_binary(rr, models[TARGET_PRR][arm])
            out[str(boundary)][arm] = k6595.metrics_binary(
                rr, TARGET_PRR, p, pr
            )
    return out


def rule_payload(
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "rule": "FUTURE-Q-v1",
        "experiment": "KCL-6.5.9.8",
        "primary_target": TARGET_PRR,
        "diagnostic_targets": [TARGET_PR, TARGET_A],
        "feature_sets": {k: list(v) for k, v in FEATURE_SETS.items()},
        "probe_features": list(PROBE_FEATURES),
        "probe_source": "KCL-6.5.9.3 FUTURE-PROBE-v1",
        "models": models,
        "protocol_sha256": sha256_file(PROTOCOL),
        "script_sha256": sha256_file(SCRIPT),
        "training_seed_sha256": sha_seed_list(TRAIN_SEEDS),
        "source_git_commit": git_commit(),
        "validation_executed_before_freeze": False,
        "controller_implemented": False,
        "protected_confirmatory_touched": False,
        "reverse_backlog_executed": False,
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
        "reverse_backlog_executed": False,
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
            "reverse_backlog_executed",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_seeds_executed"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["reverse_backlog_executed"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.8-TRAIN",
            "status": "REVISE",
            "verdict": "FUTURE_INTERACTION_TRAIN_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.8-TRAIN",
            "status": "NEGATIVE",
            "verdict": "FUTURE_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "probe_feature_summary": probe_feature_summary(records),
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
                "experiment": "KCL-6.5.9.8-TRAIN",
                "status": "REVISE",
                "verdict": "FUTURE_INTERACTION_TRAIN_INVALID",
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
                "experiment": "KCL-6.5.9.8-TRAIN",
                "status": "PASS",
                "verdict": "FUTURE_INTERACTION_MODELS_TRAINED_AND_READY_TO_FREEZE",
                "integrity": integrity,
                "support": support,
                "train_metrics_descriptive": metrics,
                "probe_feature_summary": probe_feature_summary(records),
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
                    "reverse_backlog_executed": False,
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
        rule.get("rule") == "FUTURE-Q-v1"
        and rule.get("experiment") == "KCL-6.5.9.8"
        and rule.get("primary_target") == TARGET_PRR
        and rule.get("diagnostic_targets") == [TARGET_PR, TARGET_A]
        and rule.get("feature_sets") == {
            k: list(v) for k, v in FEATURE_SETS.items()
        }
        and rule.get("probe_features") == list(PROBE_FEATURES)
        and rule.get("probe_source") == "KCL-6.5.9.3 FUTURE-PROBE-v1"
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and rule.get("script_sha256") == sha256_file(SCRIPT)
        and rule.get("training_seed_sha256") == TRAIN_SEED_SHA256
        and rule.get("validation_executed_before_freeze") is False
        and rule.get("controller_implemented") is False
        and rule.get("protected_confirmatory_touched") is False
        and rule.get("reverse_backlog_executed") is False
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
            "experiment": "KCL-6.5.9.8-VALIDATION",
            "status": "REVISE",
            "verdict": "FUTURE_INTERACTION_VALIDATION_INVALID",
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
        "reverse_backlog_executed": False,
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
            "reverse_backlog_executed",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_refit"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["reverse_backlog_executed"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.8-VALIDATION",
            "status": "REVISE",
            "verdict": "FUTURE_INTERACTION_VALIDATION_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.8-VALIDATION",
            "status": "NEGATIVE",
            "verdict": "FUTURE_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "probe_feature_summary": probe_feature_summary(records),
            "records": records,
        }
    else:
        models = rule["models"]
        metrics, preds, probs = metrics_all(records, models)
        bootstrap = paired_bootstrap(records, preds, probs)
        adj = adjudicate(metrics, bootstrap)
        secondary = {
            "D_PR": (
                metrics[TARGET_PR]["FUT"]["macro_recall"]
                - metrics[TARGET_PR]["S2"]["macro_recall"]
            ),
            "D_A": (
                metrics[TARGET_A]["FUT"]["macro_recall"]
                - metrics[TARGET_A]["S2"]["macro_recall"]
            ),
            "boundary_metrics_Y_PRR": boundary_metrics(records, models),
        }
        result = {
            "experiment": "KCL-6.5.9.8-VALIDATION",
            **adj,
            "integrity": integrity,
            "support": support,
            "metrics": metrics,
            "bootstrap": bootstrap,
            "secondary_diagnostics": secondary,
            "probe_feature_summary": probe_feature_summary(records),
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
                "reverse_backlog_executed": False,
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
        default=Path("experiments/kernel_cl/results/kcl6598_rule.json"),
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
        "probe_feature_summary": result.get("probe_feature_summary"),
        "rule": result.get("rule"),
    }, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
