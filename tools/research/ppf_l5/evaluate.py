from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from .mechanism import L5_VERSION, TREATMENTS, TreatmentSpec, predict, validate_method_payload


BENCHMARK_VERSION = "ppf-l3-benchmark/v1"
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
HARD_KEYS = (
    "deleted_active_return_violations",
    "correction_resurrection_violations",
    "stale_as_current_violations",
    "not_observable_as_current_violations",
    "unknown_context_positive_violations",
    "conflict_positive_violations",
)


def load_json(path: Path) -> dict:
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
    return [r for r in history if r.get("time", {}).get("ingested_time", "") <= checkpoint_time]


def predict_case(history_doc: dict, checkpoints_doc: dict, treatment: TreatmentSpec) -> dict:
    validate_method_payload(history_doc)
    validate_method_payload(checkpoints_doc)
    if history_doc.get("benchmark_version") != BENCHMARK_VERSION:
        raise ValueError("unexpected benchmark version in history")
    if checkpoints_doc.get("benchmark_version") != BENCHMARK_VERSION:
        raise ValueError("unexpected benchmark version in checkpoints")
    if history_doc.get("case_id") != checkpoints_doc.get("case_id"):
        raise ValueError("case_id mismatch")
    predictions = []
    for checkpoint in checkpoints_doc["checkpoints"]:
        visible = _prefix(history_doc["history"], checkpoint["time"])
        predictions.append(
            {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "predicted_answer": predict(visible, treatment),
                "visible_record_count": len(visible),
            }
        )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l5_version": L5_VERSION,
        "treatment_id": treatment.treatment_id,
        "case_id": history_doc["case_id"],
        "predictions": predictions,
    }


def predict_split(benchmark_root: Path, split: str, treatment: TreatmentSpec) -> dict:
    if split not in {"dev", "validation"}:
        raise ValueError("L5 permits DEV and VALIDATION only; L3 FINAL is scientifically spent")
    case_root = benchmark_root / "generated" / split / "cases"
    cases = []
    for case_dir in sorted(p for p in case_root.iterdir() if p.is_dir()):
        cases.append(
            predict_case(
                load_json(case_dir / "history.json"),
                load_json(case_dir / "checkpoints.json"),
                treatment,
            )
        )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l5_version": L5_VERSION,
        "split": split,
        "treatment_id": treatment.treatment_id,
        "components": list(treatment.components),
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
        exact = sum(x["correct"] for x in items)
        result[value] = {
            "units": len(items),
            "exact": exact,
            "exact_accuracy": _safe_ratio(exact, len(items)),
            "predicted_supported": sum(x["predicted"] == "SUPPORTED" for x in items),
        }
    return result


def score_predictions(benchmark_root: Path, split: str, prediction_doc: dict) -> tuple[dict, list[dict]]:
    if split not in {"dev", "validation"}:
        raise ValueError("L5 evaluator refuses FINAL")
    eval_root = benchmark_root / "evaluator" / split
    rows: list[dict] = []
    for case in prediction_doc["cases"]:
        case_id = case["case_id"]
        expected_doc = load_json(eval_root / "expected" / f"{case_id}.json")
        truth_doc = load_json(eval_root / "truth" / f"{case_id}.json")
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
                    "pair_template": truth_doc.get("pair_template") or "NONE",
                    "pair_arm": truth_doc.get("pair_arm"),
                    "correct": prediction["predicted_answer"] == expected["expected_answer"],
                }
            )

    total = len(rows)
    exact = sum(row["correct"] for row in rows)
    tp = sum(row["predicted"] == "SUPPORTED" and row["expected"] == "SUPPORTED" for row in rows)
    fp = sum(row["predicted"] == "SUPPORTED" and row["expected"] != "SUPPORTED" for row in rows)
    fn = sum(row["predicted"] != "SUPPORTED" and row["expected"] == "SUPPORTED" for row in rows)
    negative_units = sum(row["expected"] != "SUPPORTED" for row in rows)
    negative_rows = [row for row in rows if row["expected"] in NEGATIVE_STATES]
    lifecycle_rows = [row for row in rows if row["expected"] in LIFECYCLE_STATES]
    confusion: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        confusion[row["expected"]][row["predicted"]] += 1
    hard = {
        "deleted_active_return_violations": sum(r["expected"] == "DELETED" and r["predicted"] == "SUPPORTED" for r in rows),
        "correction_resurrection_violations": sum(r["expected"] == "USER_REJECTED" and r["predicted"] == "SUPPORTED" for r in rows),
        "stale_as_current_violations": sum(r["expected"] == "STALE" and r["predicted"] == "SUPPORTED" for r in rows),
        "not_observable_as_current_violations": sum(r["expected"] == "NOT_OBSERVABLE" and r["predicted"] == "SUPPORTED" for r in rows),
        "unknown_context_positive_violations": sum(r["expected"] == "UNKNOWN_CONTEXT" and r["predicted"] == "SUPPORTED" for r in rows),
        "conflict_positive_violations": sum(r["expected"] == "CONFLICTING_EVIDENCE" and r["predicted"] == "SUPPORTED" for r in rows),
    }
    metrics = {
        "units": total,
        "exact_state_accuracy": _safe_ratio(exact, total),
        "exact_state_count": exact,
        "pattern_precision_status_proxy": _safe_ratio(tp, tp + fp),
        "pattern_recall_status_proxy": _safe_ratio(tp, tp + fn),
        "false_discovery_rate": _safe_ratio(fp, tp + fp),
        "false_promotion_rate": _safe_ratio(fp, negative_units),
        "negative_exact_accuracy": _safe_ratio(sum(x["correct"] for x in negative_rows), len(negative_rows)),
        "lifecycle_exact_accuracy": _safe_ratio(sum(x["correct"] for x in lifecycle_rows), len(lifecycle_rows)),
        "predicted_supported": tp + fp,
        "expected_supported": tp + fn,
        "negative_units": negative_units,
        "confusion_matrix": {k: dict(sorted(v.items())) for k, v in sorted(confusion.items())},
        "by_identifiability": _slice_accuracy(rows, "identifiability"),
        "by_counterfactual_template": _slice_accuracy(rows, "pair_template"),
        "hard_violations": hard,
    }
    return metrics, rows


def pair_analysis(rows: list[dict]) -> dict:
    result = {}
    templates = sorted({r["pair_template"] for r in rows if r["pair_template"] != "NONE"})
    for template in templates:
        items = [r for r in rows if r["pair_template"] == template]
        by_arm: dict[str, list[dict]] = defaultdict(list)
        for row in items:
            by_arm[str(row.get("pair_arm"))].append(row)
        arms = {}
        for arm, arm_rows in sorted(by_arm.items()):
            arms[arm] = {
                "units": len(arm_rows),
                "exact": sum(r["correct"] for r in arm_rows),
                "prediction_sequence": [r["predicted"] for r in arm_rows],
                "expected_sequence": [r["expected"] for r in arm_rows],
            }
        a = arms.get("A", {}).get("prediction_sequence", [])
        b = arms.get("B", {}).get("prediction_sequence", [])
        ea = arms.get("A", {}).get("expected_sequence", [])
        eb = arms.get("B", {}).get("expected_sequence", [])
        result[template] = {
            "arms": arms,
            "distinguished_pair": a != b,
            "expected_distinction": ea != eb,
            "correct_direction": bool(a and b and a == ea and b == eb),
            "unchanged": a == b,
        }
    return result


def evaluate_treatment(benchmark_root: Path, split: str, treatment: TreatmentSpec) -> dict:
    predictions = predict_split(benchmark_root, split, treatment)
    metrics, rows = score_predictions(benchmark_root, split, predictions)
    return {
        "treatment_id": treatment.treatment_id,
        "description": treatment.description,
        "components": list(treatment.components),
        "prediction_sha256": sha256_json(predictions),
        "metrics": metrics,
        "counterfactual_pairs": pair_analysis(rows),
    }


def evaluate_all(benchmark_root: Path, split: str) -> dict:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "l5_version": L5_VERSION,
        "split": split,
        "treatments": [evaluate_treatment(benchmark_root, split, treatment) for treatment in TREATMENTS],
    }

