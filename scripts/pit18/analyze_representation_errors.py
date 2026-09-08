"""Inspect PIT-18 representation result mismatches without touching source corpora."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    rows = [json.loads(x) for x in args.results.read_text(encoding="utf-8").splitlines() if x.strip()]
    for row in rows:
        exp = row["expected"]
        pred = row["predicted"]
        primitive_bad = set(exp.get("primitive_labels", [])) != set(pred.get("primitive_labels", []))
        canonical_bad = any(bool(pred["canonical"].get(k)) != bool(v) for k, v in exp.get("canonical", {}).items())
        scope_bad = any(
            exp.get(key) != pred.get(key)
            for key in ("evidence_scope", "asserted_scope", "scope_relation")
            if key in exp
        )
        support_bad = any(pred["support"].get(k) != v for k, v in exp.get("support", {}).items())
        if primitive_bad or canonical_bad or scope_bad or support_bad:
            print(json.dumps({
                "gold_id": row["gold_id"],
                "source": row["source"],
                "primitive_expected": exp.get("primitive_labels", []),
                "primitive_predicted": pred.get("primitive_labels", []),
                "canonical_expected": exp.get("canonical", {}),
                "canonical_predicted": pred.get("canonical", {}),
                "scope_expected": [exp.get("evidence_scope"), exp.get("asserted_scope"), exp.get("scope_relation")],
                "scope_predicted": [pred.get("evidence_scope"), pred.get("asserted_scope"), pred.get("scope_relation")],
                "support_expected": exp.get("support", {}),
                "support_predicted": {k: pred["support"].get(k) for k in exp.get("support", {})},
            }, ensure_ascii=False))


if __name__ == "__main__":
    main()

