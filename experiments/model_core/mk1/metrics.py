"""Frozen MK-1 representation and canonical-state metrics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np
import torch

from .contracts import C_SLICES, H1B_BOOTSTRAP_RESAMPLES, H1B_BOOTSTRAP_SEED, Z1_LABELS, Z4_FIELDS


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
