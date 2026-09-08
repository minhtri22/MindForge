"""Evaluate Representation V2 + frozen V3 on a frozen PIT-16 split."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from representation_v2 import evaluate

CLASSES = (
    "UNSUPPORTED_CONFLICT_RESOLUTION",
    "UNSUPPORTED_NUMERIC_THRESHOLD",
    "UNSUPPORTED_TEMPORAL_RULE",
    "UNSUPPORTED_FALLBACK_POLICY",
    "UNSUPPORTED_SCOPE_GENERALIZATION",
    "EVIDENCE_GROUNDING_FAILURE",
)
RUNTIME_FILES = (
    "scripts/pit18/surface_normalizer.py",
    "scripts/pit18/primitive_schema.py",
    "scripts/pit18/primitive_extractor.py",
    "scripts/pit18/canonicalizer.py",
    "scripts/pit18/scope_lattice.py",
    "scripts/pit18/support_relations_v2.py",
    "scripts/pit18/representation_v2.py",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def rate(n: int, d: int) -> float:
    return round(n / d, 6) if d else 1.0


def sha256_files(paths: tuple[str, ...]) -> str:
    h = hashlib.sha256()
    for rel in paths:
        h.update((ROOT / rel).read_bytes())
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_for_heldout() -> None:
    protocol = load_json(ROOT / "experiments/pit18/protocol.json")
    freeze = protocol["freeze"]
    checks = {
        "representation_v2_sha256": sha256_files(RUNTIME_FILES),
        "pit16_corpus_sha256": sha256_file(ROOT / "experiments/pit16/corpus.json"),
        "pit16_split_sha256": sha256_file(ROOT / "experiments/pit16/split.json"),
        "guardrail_v3_sha256": sha256_file(ROOT / "scripts/pit17/guardrail_v3.py"),
    }
    for key, actual in checks.items():
        if freeze.get(key) != actual:
            raise SystemExit(f"PIT-18 freeze mismatch for {key}")


def build_rows(split_name: str) -> list[dict[str, Any]]:
    split = load_json(ROOT / "experiments/pit16/split.json")
    ids = set(split[split_name])
    fixtures = load_json(ROOT / "experiments/pit16/corpus.json")["fixtures"]
    rows = []
    for fixture in fixtures:
        if fixture["fixture_id"] not in ids:
            continue
        got = evaluate(fixture["evidence"], fixture["teaching_signal"])
        rows.append(
            {
                "fixture_id": fixture["fixture_id"],
                "family": fixture["family"],
                "expected": fixture["expected_violation_classes"],
                "expected_status": fixture["expected_status"],
                **got,
            }
        )
    return rows


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = [row for row in rows if row["expected"]]
    valid = [row for row in rows if not row["expected"]]
    detected = lambda row: row["decision"]["status"] != "ACCEPT"
    tp = sum(detected(row) for row in unsafe)
    fp = sum(detected(row) for row in valid)
    expected_classes = sum(len(row["expected"]) for row in rows)
    class_tp = sum(len(set(row["expected"]) & set(row["decision"]["violation_classes"])) for row in rows)
    predicted_classes = sum(len(row["decision"]["violation_classes"]) for row in rows)
    per_class = {}
    for class_name in CLASSES:
        relevant = [row for row in rows if class_name in row["expected"]]
        per_class[class_name] = (
            rate(sum(class_name in row["decision"]["violation_classes"] for row in relevant), len(relevant))
            if relevant else None
        )
    compounds = [row for row in rows if len(row["expected"]) > 1]
    compound_detected = sum(detected(row) for row in compounds)
    full = sum(set(row["expected"]).issubset(set(row["decision"]["violation_classes"])) for row in compounds)
    return {
        "samples": len(rows),
        "unsafe": len(unsafe),
        "valid": len(valid),
        "unsafe_sample_recall": rate(tp, len(unsafe)),
        "unsafe_sample_precision": rate(tp, tp + fp),
        "violation_class_recall": rate(class_tp, expected_classes),
        "violation_class_precision": rate(class_tp, predicted_classes),
        "hard_negative_fpr": rate(fp, len(valid)),
        "per_class_recall": per_class,
        "conflict_recall": per_class["UNSUPPORTED_CONFLICT_RESOLUTION"],
        "numeric_threshold_recall": per_class["UNSUPPORTED_NUMERIC_THRESHOLD"],
        "temporal_rule_recall": per_class["UNSUPPORTED_TEMPORAL_RULE"],
        "fallback_recall": per_class["UNSUPPORTED_FALLBACK_POLICY"],
        "scope_generalization_recall": per_class["UNSUPPORTED_SCOPE_GENERALIZATION"],
        "compound_sample_detection": rate(compound_detected, len(compounds)),
        "compound_full_class_recall": rate(full, len(compounds)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("dev", "held_out"), default="held_out")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.split == "held_out":
        verify_freeze_for_heldout()
    rows = build_rows(args.split)
    if args.output:
        write_jsonl(args.output, rows)
    print(json.dumps(score(rows), indent=2))


if __name__ == "__main__":
    main()
