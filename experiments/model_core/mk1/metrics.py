"""Frozen MK-1 representation and canonical-state metrics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np
import torch

from .contracts import (
    C_SLICES,
    H1B_BOOTSTRAP_RESAMPLES,
    H1B_BOOTSTRAP_SEED,
    H1C_BOOTSTRAP_RESAMPLES,
    H1C_BOOTSTRAP_SEED,
    PIT_COMMON_Z4_FIELDS,
    SCOPES,
    SCOPE_RELATIONS,
    Z1_LABELS,
    Z4_FIELDS,
)


def decode_direct_logits(logits: torch.Tensor) -> dict[str, torch.Tensor]:
    if logits.ndim != 2 or logits.size(1) != 34:
        raise ValueError("direct logits must have shape [batch,34]")
    return {
        "c1": logits[:, C_SLICES["c1"]] >= 0,
        "c2": torch.argmax(logits[:, C_SLICES["c2"]], dim=1),
        "c3": torch.argmax(logits[:, C_SLICES["c3"]], dim=1),
        "c4": torch.argmax(logits[:, C_SLICES["c4"]], dim=1),
        "c5": logits[:, C_SLICES["c5"]] >= 0,
    }


def canonical_to_python(value: dict[str, torch.Tensor]) -> list[dict[str, Any]]:
    batch = int(value["c1"].size(0))
    return [
        {
            "c1": [int(x) for x in value["c1"][i].detach().cpu().tolist()],
            "c2": int(value["c2"][i].detach().cpu()),
            "c3": int(value["c3"][i].detach().cpu()),
            "c4": int(value["c4"][i].detach().cpu()),
            "c5": [int(x) for x in value["c5"][i].detach().cpu().tolist()],
        }
        for i in range(batch)
    ]


def _binary_counts(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[int, int, int]:
    truth = y_true.astype(bool)
    pred = y_pred.astype(bool)
    tp = int(np.logical_and(truth, pred).sum())
    fp = int(np.logical_and(~truth, pred).sum())
    fn = int(np.logical_and(truth, ~pred).sum())
    return tp, fp, fn


def _precision_recall_f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def binary_macro_f1(gold: np.ndarray, pred: np.ndarray) -> float:
    if gold.shape != pred.shape or gold.ndim != 2:
        raise ValueError("binary macro F1 expects matching [n,fields] arrays")
    scores = []
    for col in range(gold.shape[1]):
        scores.append(_precision_recall_f1(*_binary_counts(gold[:, col], pred[:, col]))[2])
    return float(np.mean(scores)) if scores else 0.0


def binary_micro_prf(gold: np.ndarray, pred: np.ndarray) -> tuple[float, float, float]:
    return _precision_recall_f1(*_binary_counts(gold.reshape(-1), pred.reshape(-1)))


def canonical_metrics(gold_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> dict[str, float]:
    if len(gold_rows) != len(pred_rows) or not gold_rows:
        raise ValueError("canonical metrics require non-empty aligned rows")
    g1 = np.asarray([r["c1"] for r in gold_rows], dtype=np.int8)
    p1 = np.asarray([r["c1"] for r in pred_rows], dtype=np.int8)
    g5 = np.asarray([r["c5"] for r in gold_rows], dtype=np.int8)
    p5 = np.asarray([r["c5"] for r in pred_rows], dtype=np.int8)
    values = {
        "c1_macro_f1": binary_macro_f1(g1, p1),
        "c2_accuracy": float(np.mean([g["c2"] == p["c2"] for g, p in zip(gold_rows, pred_rows)])),
        "c3_accuracy": float(np.mean([g["c3"] == p["c3"] for g, p in zip(gold_rows, pred_rows)])),
        "c4_accuracy": float(np.mean([g["c4"] == p["c4"] for g, p in zip(gold_rows, pred_rows)])),
        "c5_macro_f1": binary_macro_f1(g5, p5),
    }
    values["balanced_score"] = float(np.mean(list(values.values())))
    field_hits = []
    exact = []
    for gold, pred in zip(gold_rows, pred_rows):
        checks = [a == b for a, b in zip(gold["c1"], pred["c1"])]
        checks += [gold["c2"] == pred["c2"], gold["c3"] == pred["c3"], gold["c4"] == pred["c4"]]
        checks += [a == b for a, b in zip(gold["c5"], pred["c5"])]
        field_hits.extend(checks)
        exact.append(all(checks))
    values["field_accuracy"] = float(np.mean(field_hits))
    values["full_state_exact_match"] = float(np.mean(exact))
    return values


def z1_metrics(gold: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    precision, recall, micro_f1 = binary_micro_prf(gold, pred)
    per_class = []
    for i, name in enumerate(Z1_LABELS):
        p, r, f = _precision_recall_f1(*_binary_counts(gold[:, i], pred[:, i]))
        per_class.append({"name": name, "precision": p, "recall": r, "f1": f})
    return {
        "micro_precision": precision,
        "micro_recall": recall,
        "micro_f1": micro_f1,
        "macro_f1": float(np.mean([row["f1"] for row in per_class])),
        "exact_set_match": float(np.mean(np.all(gold == pred, axis=1))),
        "per_class": per_class,
    }


def z4_metrics(gold: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    precision, recall, micro_f1 = binary_micro_prf(gold, pred)
    per_field = []
    for i, name in enumerate(Z4_FIELDS):
        p, r, f = _precision_recall_f1(*_binary_counts(gold[:, i], pred[:, i]))
        per_field.append({"name": name, "precision": p, "recall": r, "f1": f})
    return {
        "pooled_precision": precision,
        "pooled_recall": recall,
        "pooled_f1": micro_f1,
        "macro_f1": float(np.mean([row["f1"] for row in per_field])),
        "per_field": per_field,
    }


def normalized_absolute_error(pred: np.ndarray, gold: np.ndarray) -> np.ndarray:
    return np.abs(pred - gold) / np.maximum(np.abs(gold), 1.0)


def invariance_cluster_consistency(rows: Iterable[tuple[str, dict[str, Any]]]) -> float:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for scene_id, pred in rows:
        grouped[scene_id].append(pred)
    if not grouped:
        raise ValueError("no invariance rows")
    consistent = 0
    for values in grouped.values():
        first = values[0]
        consistent += int(all(value == first for value in values[1:]))
    return consistent / len(grouped)


def paired_h1b_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Rows contain scene_id, seed, gold_c, direct_c, m1z_c."""
    if not rows:
        raise ValueError("bootstrap rows cannot be empty")
    scene_ids = sorted({str(row["scene_id"]) for row in rows})
    seeds = sorted({int(row["seed"]) for row in rows})
    lookup = {(str(r["scene_id"]), int(r["seed"])): r for r in rows}
    for scene_id in scene_ids:
        for seed in seeds:
            if (scene_id, seed) not in lookup:
                raise ValueError("bootstrap rows must contain every scene x seed pair")

    def delta_for(sampled: list[str]) -> float:
        seed_deltas = []
        for seed in seeds:
            selected = [lookup[(scene_id, seed)] for scene_id in sampled]
            gold = [r["gold_c"] for r in selected]
            direct = [r["direct_c"] for r in selected]
            m1z = [r["m1z_c"] for r in selected]
            seed_deltas.append(canonical_metrics(gold, m1z)["balanced_score"] - canonical_metrics(gold, direct)["balanced_score"])
        return float(np.mean(seed_deltas))

    point = delta_for(scene_ids)
    rng = np.random.default_rng(H1B_BOOTSTRAP_SEED)
    draws = np.empty(H1B_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(H1B_BOOTSTRAP_RESAMPLES):
        sampled = [scene_ids[j] for j in rng.integers(0, len(scene_ids), size=len(scene_ids))]
        draws[i] = delta_for(sampled)
    return {
        "point_delta": point,
        "lower_95": float(np.percentile(draws, 2.5)),
        "upper_95": float(np.percentile(draws, 97.5)),
        "resamples": H1B_BOOTSTRAP_RESAMPLES,
        "rng_seed": H1B_BOOTSTRAP_SEED,
        "scenes": len(scene_ids),
        "model_seeds": seeds,
    }


def relative_error_reduction(error_model: float, error_baseline: float) -> float:
    if error_baseline <= 0:
        raise ValueError("baseline error must be positive for relative error reduction")
    return (error_baseline - error_model) / error_baseline


def pit_v3_common_view(result: dict[str, Any]) -> dict[str, Any]:
    """Project an unchanged PIT-v3 result onto the frozen exact common-field set."""
    primitives = result["primitives"]
    types = {
        str(item["type"])
        for item in primitives["evidence_primitives"] + primitives["teaching_signal_primitives"]
    }
    facts = result["facts"]
    ev = facts["evidence_state"]
    ts = facts["teaching_signal_state"]
    support = facts["support_relations"]
    z1 = [int(name in types) for name in Z1_LABELS]
    z4 = {
        "conflict_present": int(bool(ev["has_conflict"])),
        "supersession_supported": int(bool(support["supersession_supported"])),
        "scope_supported": int(bool(support["scope_supported"])),
        "temporal_rule_supported": int(bool(support["temporal_rule_supported"])),
        "fallback_policy_supported": int(bool(support["fallback_policy_supported"])),
        "operational_signal_supported": int(bool(support["operational_signals_supported"])),
    }
    c1 = [
        int(bool(ev["has_conflict"])),
        int(bool(ts["resolves_conflict"])),
        int(bool(ts["asserts_numeric_threshold"])),
        int(bool(ts["asserts_temporal_rule"])),
        int(bool(ts["asserts_fallback_policy"])),
        int(bool(ts["abstains"])),
        int(bool(ts["requests_clarification"])),
        int(bool(ts["operational_signals"])),
    ]
    return {
        "z1": z1,
        "z3_evidence_scope": SCOPES.index(str(ev["scope_level"]).upper()),
        "z3_asserted_scope": SCOPES.index(str(ts["asserted_scope"]).upper()),
        "z3_scope_relation": SCOPE_RELATIONS.index(str(support["scope_relation"]).upper()),
        "z4_common": z4,
        "c1": c1,
    }


def _common_field_errors(
    gold_z: dict[str, Any],
    gold_c: dict[str, Any],
    predicted_z: dict[str, Any],
    predicted_c: dict[str, Any],
    *,
    pit: bool = False,
) -> tuple[int, int]:
    errors = 0
    fields = 0
    for gold, pred in zip(gold_z["z1"], predicted_z["z1"]):
        errors += int(int(gold) != int(pred))
        fields += 1
    for key in ("z3_evidence_scope", "z3_asserted_scope", "z3_scope_relation"):
        errors += int(int(gold_z[key]) != int(predicted_z[key]))
        fields += 1
    z4_index = {name: i for i, name in enumerate(Z4_FIELDS)}
    if pit:
        z4_pred = predicted_z["z4_common"]
        for name in PIT_COMMON_Z4_FIELDS:
            errors += int(int(gold_z["z4"][z4_index[name]]) != int(z4_pred[name]))
            fields += 1
    else:
        for name in PIT_COMMON_Z4_FIELDS:
            errors += int(int(gold_z["z4"][z4_index[name]]) != int(predicted_z["z4"][z4_index[name]]))
            fields += 1
    for gold, pred in zip(gold_c["c1"], predicted_c["c1"]):
        errors += int(int(gold) != int(pred))
        fields += 1
    return errors, fields


def h1c_common_field_summary(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Rows contain gold_z, gold_c, m1z_z, m1z_c, and pit_result."""
    if not rows:
        raise ValueError("H1c rows cannot be empty")
    m1_errors = pit_errors = total_fields = 0
    m1_z1_gold: list[list[int]] = []
    m1_z1_pred: list[list[int]] = []
    pit_z1_pred: list[list[int]] = []
    for row in rows:
        pit_view = pit_v3_common_view(row["pit_result"])
        m1e, fields = _common_field_errors(row["gold_z"], row["gold_c"], row["m1z_z"], row["m1z_c"])
        pite, pit_fields = _common_field_errors(
            row["gold_z"],
            row["gold_c"],
            pit_view,
            {"c1": pit_view["c1"]},
            pit=True,
        )
        if pit_fields != fields:
            raise AssertionError("H1c common-field counts diverged")
        m1_errors += m1e
        pit_errors += pite
        total_fields += fields
        m1_z1_gold.append([int(v) for v in row["gold_z"]["z1"]])
        m1_z1_pred.append([int(v) for v in row["m1z_z"]["z1"]])
        pit_z1_pred.append([int(v) for v in pit_view["z1"]])

    m1_error = m1_errors / total_fields
    pit_error = pit_errors / total_fields
    reduction = relative_error_reduction(m1_error, pit_error)
    gold = np.asarray(m1_z1_gold, dtype=np.int8)
    m1_pred = np.asarray(m1_z1_pred, dtype=np.int8)
    pit_pred = np.asarray(pit_z1_pred, dtype=np.int8)
    m1_precision = binary_micro_prf(gold, m1_pred)[0]
    pit_precision = binary_micro_prf(gold, pit_pred)[0]
    return {
        "m1z_error_rate": float(m1_error),
        "pit_error_rate": float(pit_error),
        "relative_error_reduction": float(reduction),
        "m1z_primitive_precision": float(m1_precision),
        "pit_primitive_precision": float(pit_precision),
        "primitive_precision_delta": float(m1_precision - pit_precision),
        "common_fields_per_scene": float(total_fields / len(rows)),
    }


def h1c_whole_scene_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("H1c bootstrap rows cannot be empty")
    by_scene = {str(row["scene_id"]): row for row in rows}
    if len(by_scene) != len(rows):
        raise ValueError("H1c rows must contain exactly one record per canonical scene")
    scene_ids = sorted(by_scene)
    point = h1c_common_field_summary(rows)
    rng = np.random.default_rng(H1C_BOOTSTRAP_SEED)
    draws: list[float] = []
    for _ in range(H1C_BOOTSTRAP_RESAMPLES):
        sampled = [by_scene[scene_ids[j]] for j in rng.integers(0, len(scene_ids), size=len(scene_ids))]
        try:
            draws.append(h1c_common_field_summary(sampled)["relative_error_reduction"])
        except ValueError:
            continue
    if not draws:
        raise ValueError("H1c bootstrap undefined because PIT error is zero in every resample")
    values = np.asarray(draws, dtype=np.float64)
    return {
        **point,
        "lower_95": float(np.percentile(values, 2.5)),
        "upper_95": float(np.percentile(values, 97.5)),
        "resamples_requested": H1C_BOOTSTRAP_RESAMPLES,
        "resamples_defined": len(draws),
        "rng_seed": H1C_BOOTSTRAP_SEED,
        "scenes": len(scene_ids),
    }


def h1a_representation_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the frozen H1a metric bundle from aligned per-surface predictions."""
    if not rows:
        raise ValueError("H1a rows cannot be empty")
    z1_gold = np.asarray([row["gold_z"]["z1"] for row in rows], dtype=np.int8)
    z1_pred = np.asarray([row["pred_z"]["z1"] for row in rows], dtype=np.int8)
    z4_gold = np.asarray([row["gold_z"]["z4"] for row in rows], dtype=np.int8)
    z4_pred = np.asarray([row["pred_z"]["z4"] for row in rows], dtype=np.int8)

    scalar_metrics: dict[str, dict[str, float | int]] = {}
    scalar_names = ("numeric_value", "ordinal_index", "duration_seconds", "period_seconds")
    for index, name in enumerate(scalar_names):
        gold_values = []
        pred_values = []
        for row in rows:
            if bool(row["gold_z"]["z2_scalar_mask"][index]):
                gold_values.append(float(row["gold_z"]["z2_scalars"][index]))
                pred_values.append(float(row["pred_z"]["z2_scalars"][index]))
        if gold_values:
            errors = normalized_absolute_error(
                np.asarray(pred_values, dtype=np.float64),
                np.asarray(gold_values, dtype=np.float64),
            )
            scalar_metrics[name] = {
                "count": len(gold_values),
                "mean_nAE": float(np.mean(errors)),
                "p95_nAE": float(np.percentile(errors, 95.0)),
            }
        else:
            scalar_metrics[name] = {"count": 0, "mean_nAE": float("nan"), "p95_nAE": float("nan")}

    gold_c = [row["gold_c"] for row in rows]
    pred_c = [row["pred_c"] for row in rows]
    return {
        "z1": z1_metrics(z1_gold, z1_pred),
        "z2": {
            "comparator_accuracy": float(np.mean([
                int(row["gold_z"]["z2_comparator"]) == int(row["pred_z"]["z2_comparator"]) for row in rows
            ])),
            "temporal_precision_accuracy": float(np.mean([
                int(row["gold_z"]["z2_temporal_precision"]) == int(row["pred_z"]["z2_temporal_precision"]) for row in rows
            ])),
            "scalars": scalar_metrics,
        },
        "z3": {
            "evidence_scope_accuracy": float(np.mean([
                int(row["gold_z"]["z3_evidence_scope"]) == int(row["pred_z"]["z3_evidence_scope"]) for row in rows
            ])),
            "asserted_scope_accuracy": float(np.mean([
                int(row["gold_z"]["z3_asserted_scope"]) == int(row["pred_z"]["z3_asserted_scope"]) for row in rows
            ])),
            "scope_relation_accuracy": float(np.mean([
                int(row["gold_z"]["z3_scope_relation"]) == int(row["pred_z"]["z3_scope_relation"]) for row in rows
            ])),
        },
        "z4": z4_metrics(z4_gold, z4_pred),
        "canonical": canonical_metrics(gold_c, pred_c),
        "invariance_cluster_consistency": invariance_cluster_consistency(
            (str(row["scene_id"]), row["pred_c"]) for row in rows
        ),
    }
