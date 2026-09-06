from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from .baselines import BASELINES, BaselineSpec


BENCHMARK_VERSION = "ppf-l3-benchmark/v1"
L4_VERSION = "ppf-l4-minimal-baselines/v1"
NEGATIVE_STATES = {
    "INSUFFICIENT_EVIDENCE",
    "CONFLICTING_EVIDENCE",
    "UNKNOWN_CONTEXT",
    "NOT_OBSERVABLE",
    "STALE",
    "USER_REJECTED",
    "SUPERSEDED",
    "DELETED",
}
LIFECYCLE_STATES = {"USER_REJECTED", "SUPERSEDED", "DELETED", "STALE"}


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _prefix(history: list[dict], checkpoint_time: str) -> list[dict]:
    return [
        record
        for record in history
        if record.get("time", {}).get("ingested_time", "") <= checkpoint_time
    ]


def predict_case(history_doc: dict, checkpoints_doc: dict, baseline: BaselineSpec) -> dict:
    if history_doc.get("benchmark_version") != BENCHMARK_VERSION:
        raise ValueError("unexpected benchmark version in history")
    if checkpoints_doc.get("benchmark_version") != BENCHMARK_VERSION:
        raise ValueError("unexpected benchmark version in checkpoints")
    if history_doc.get("case_id") != checkpoints_doc.get("case_id"):
        raise ValueError("case_id mismatch")
    history = history_doc["history"]
    predictions = []
    for checkpoint in checkpoints_doc["checkpoints"]:
        visible = _prefix(history, checkpoint["time"])
        predictions.append(
            {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "predicted_answer": baseline.predict(visible),
                "visible_record_count": len(visible),
            }
        )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l4_version": L4_VERSION,
        "baseline_id": baseline.baseline_id,
        "case_id": history_doc["case_id"],
        "predictions": predictions,
    }


def predict_split(benchmark_root: Path, split: str, baseline: BaselineSpec) -> dict:
    case_root = benchmark_root / "generated" / split / "cases"
    if not case_root.is_dir():
        raise FileNotFoundError(case_root)
    cases = []
    for case_dir in sorted(p for p in case_root.iterdir() if p.is_dir()):
        cases.append(
            predict_case(
                _load(case_dir / "history.json"),
                _load(case_dir / "checkpoints.json"),
                baseline,
            )
        )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l4_version": L4_VERSION,
        "split": split,
        "baseline_id": baseline.baseline_id,
        "baseline_name": baseline.name,
        "baseline_parameters": baseline.parameters,
        "cases": cases,
    }


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _slice_accuracy(rows: list[dict], key: str) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        values = row[key] if isinstance(row[key], list) else [row[key]]
        for value in values:
            grouped[str(value)].append(row)
    result = {}
    for value, items in sorted(grouped.items()):
        result[value] = {
            "units": len(items),
            "exact": sum(x["correct"] for x in items),
            "exact_accuracy": _safe_ratio(sum(x["correct"] for x in items), len(items)),
            "predicted_supported": sum(x["predicted"] == "SUPPORTED" for x in items),
        }
    return result


def _truth_root(benchmark_root: Path, split: str) -> Path:
    if split == "final":
        return benchmark_root / "evaluator_private" / "final"
    return benchmark_root / "evaluator" / split


def score_predictions(benchmark_root: Path, split: str, prediction_doc: dict) -> dict:
    eval_root = _truth_root(benchmark_root, split)
    rows: list[dict] = []
    for case in prediction_doc["cases"]:
        case_id = case["case_id"]
        expected_doc = _load(eval_root / "expected" / f"{case_id}.json")
        truth_doc = _load(eval_root / "truth" / f"{case_id}.json")
        expected_by_cp = {x["checkpoint_id"]: x for x in expected_doc["answers"]}
        for prediction in case["predictions"]:
            expected = expected_by_cp[prediction["checkpoint_id"]]
            rows.append(
                {
                    "case_id": case_id,
                    "checkpoint_id": prediction["checkpoint_id"],
                    "predicted": prediction["predicted_answer"],
                    "expected": expected["expected_answer"],
                    "identifiability": expected["identifiability"],
                    "families": truth_doc.get("families", []),
                    "truth_kind": truth_doc.get("truth", {}).get("truth_kind"),
                    "truth_scope": truth_doc.get("truth", {}).get("scope"),
                    "pair_template": truth_doc.get("pair_template") or "NONE",
                    "correct": prediction["predicted_answer"] == expected["expected_answer"],
                }
            )

    total = len(rows)
    exact = sum(row["correct"] for row in rows)
    tp = sum(row["predicted"] == "SUPPORTED" and row["expected"] == "SUPPORTED" for row in rows)
    fp = sum(row["predicted"] == "SUPPORTED" and row["expected"] != "SUPPORTED" for row in rows)
    fn = sum(row["predicted"] != "SUPPORTED" and row["expected"] == "SUPPORTED" for row in rows)
    negative_units = sum(row["expected"] != "SUPPORTED" for row in rows)
    predicted_positive = tp + fp
    expected_positive = tp + fn
    confusion: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        confusion[row["expected"]][row["predicted"]] += 1
    by_expected = {}
    for state in sorted({row["expected"] for row in rows}):
        items = [row for row in rows if row["expected"] == state]
        by_expected[state] = {
            "units": len(items),
            "exact": sum(row["correct"] for row in items),
            "exact_accuracy": _safe_ratio(sum(row["correct"] for row in items), len(items)),
            "predicted_supported": sum(row["predicted"] == "SUPPORTED" for row in items),
        }

    lifecycle_rows = [row for row in rows if row["expected"] in LIFECYCLE_STATES]
    negative_rows = [row for row in rows if row["expected"] in NEGATIVE_STATES]
    hard_violations = {
        "deleted_active_return_violations": sum(
            row["expected"] == "DELETED" and row["predicted"] == "SUPPORTED" for row in rows
        ),
        "correction_resurrection_violations": sum(
            row["expected"] == "USER_REJECTED" and row["predicted"] == "SUPPORTED" for row in rows
        ),
        "stale_as_current_violations": sum(
            row["expected"] == "STALE" and row["predicted"] == "SUPPORTED" for row in rows
        ),
        "not_observable_as_current_violations": sum(
            row["expected"] == "NOT_OBSERVABLE" and row["predicted"] == "SUPPORTED" for row in rows
        ),
        "unknown_context_positive_violations": sum(
            row["expected"] == "UNKNOWN_CONTEXT" and row["predicted"] == "SUPPORTED" for row in rows
        ),
        "conflict_positive_violations": sum(
            row["expected"] == "CONFLICTING_EVIDENCE" and row["predicted"] == "SUPPORTED" for row in rows
        ),
    }
    return {
        "units": total,
        "exact_state_accuracy": _safe_ratio(exact, total),
        "exact_state_count": exact,
        "pattern_precision_status_proxy": _safe_ratio(tp, predicted_positive),
        "pattern_recall_status_proxy": _safe_ratio(tp, expected_positive),
        "false_discovery_rate": _safe_ratio(fp, predicted_positive),
        "false_promotion_rate": _safe_ratio(fp, negative_units),
        "negative_exact_accuracy": _safe_ratio(sum(x["correct"] for x in negative_rows), len(negative_rows)),
        "lifecycle_exact_accuracy": _safe_ratio(sum(x["correct"] for x in lifecycle_rows), len(lifecycle_rows)),
        "predicted_supported": predicted_positive,
        "expected_supported": expected_positive,
        "negative_units": negative_units,
        "confusion_matrix": {k: dict(sorted(v.items())) for k, v in sorted(confusion.items())},
        "by_expected_state": by_expected,
        "by_identifiability": _slice_accuracy(rows, "identifiability"),
        "by_family": _slice_accuracy(rows, "families"),
        "by_truth_kind": _slice_accuracy(rows, "truth_kind"),
        "by_truth_scope": _slice_accuracy(rows, "truth_scope"),
        "by_counterfactual_template": _slice_accuracy(rows, "pair_template"),
        "hard_violations": hard_violations,
        "scope_correctness": "NOT_APPLICABLE_TO_STATUS_ONLY_L3_V1_OUTPUT",
        "note": "Baselines predict checkpoint semantic state only. Family/scope/pair fields are evaluator-only slices and are never method inputs.",
    }


def evaluate_all(benchmark_root: Path, split: str) -> dict:
    baselines = []
    for baseline in BASELINES:
        predictions = predict_split(benchmark_root, split, baseline)
        baselines.append(
            {
                "baseline_id": baseline.baseline_id,
                "name": baseline.name,
                "parameters": baseline.parameters,
                "prediction_sha256": sha256_json(predictions),
                "metrics": score_predictions(benchmark_root, split, predictions),
            }
        )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l4_version": L4_VERSION,
        "split": split,
        "baselines": baselines,
    }

