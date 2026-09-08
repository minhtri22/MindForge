"""Summarize one frozen PIT-16 held-out execution into full/pristine/pre-exposed views."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit18"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    from evaluate_pit16_heldout import score

    rows = load_jsonl(EXP / "pit16-heldout-results.jsonl")
    manifest = json.loads((EXP / "pre-exposure-manifest.json").read_text(encoding="utf-8"))
    exposed = set(manifest["pre_exposed_ids"])
    pristine = [row for row in rows if row["fixture_id"] not in exposed]
    pre = [row for row in rows if row["fixture_id"] in exposed]
    pre_metrics = score(pre)
    out = {
        "full": score(rows),
        "pristine": score(pristine),
        "pre_exposed": {
            "samples": pre_metrics["samples"],
            "sample_recall": pre_metrics["unsafe_sample_recall"],
            "violation_class_recall": pre_metrics["violation_class_recall"],
            "conflict_recall": pre_metrics["conflict_recall"],
            "ids": sorted(exposed),
        },
    }
    (EXP / "pit16-heldout-views.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
