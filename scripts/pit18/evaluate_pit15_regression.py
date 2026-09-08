"""Evaluate Representation V2 + frozen V3 on the PIT-15 historical corpus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from representation_v2 import evaluate


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def rate(n: int, d: int) -> float:
    return round(n / d, 6) if d else 1.0


def build_rows() -> list[dict[str, Any]]:
    scenarios = {
        row["scenario_id"]: row
        for row in load_json(ROOT / "experiments/pit13/evidence/scenarios.json")["scenarios"]
    }
    controls = load_jsonl(ROOT / "experiments/pit15/control/control-results.jsonl")
    rows = []
    for row in controls:
        got = evaluate(scenarios[row["scenario_id"]], row["teaching_signal"])
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "scenario_id": row["scenario_id"],
                "expected": row["known_expected_violations"],
                **got,
            }
        )
    return rows


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [row for row in rows if row["expected"]]
    valid = [row for row in rows if not row["expected"]]
    detected = lambda row: row["decision"]["status"] != "ACCEPT"
    known_detected = sum(detected(row) for row in failures)
    false_positives = sum(detected(row) for row in valid)

    conflict = [row for row in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" in row["expected"]]
    heuristic = [row for row in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" not in row["expected"]]
    muse = [row for row in rows if row["candidate_id"] == "meta/muse-glimmer-30b"]
    lifecycle_ids = {
        "preference_drift_001", "user_correction_001", "rare_exception_001",
        "insufficient_evidence_001", "long_term_consistency_001",
    }
    lifecycle = [row for row in valid if row["scenario_id"] in lifecycle_ids]
    accepted = lambda group: sum(row["decision"]["status"] == "ACCEPT" for row in group)
    exact = sum(set(row["expected"]) == set(row["decision"]["violation_classes"]) for row in rows)
    return {
        "samples": len(rows),
        "known_failures_detected": known_detected,
        "known_failures_total": len(failures),
        "known_failure_detection": rate(known_detected, len(failures)),
        "conflict_detection": rate(sum(detected(row) for row in conflict), len(conflict)),
        "unsupported_heuristic_detection": rate(sum(detected(row) for row in heuristic), len(heuristic)),
        "muse_preservation": rate(accepted(muse), len(muse)),
        "lifecycle_preservation": rate(accepted(lifecycle), len(lifecycle)),
        "false_positive_rate": rate(false_positives, len(valid)),
        "exact_class_agreement": rate(exact, len(rows)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = build_rows()
    if args.output:
        write_jsonl(args.output, rows)
    print(json.dumps(score(rows), indent=2))


if __name__ == "__main__":
    main()

