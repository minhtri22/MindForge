"""Build the frozen PIT-17 fact gold subset from development-eligible sources only."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/pit17/fact-goldset.json"


def main() -> None:
    pit15 = [json.loads(x) for x in (ROOT / "experiments/pit15/control/control-results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    corpus = json.loads((ROOT / "experiments/pit16/corpus.json").read_text(encoding="utf-8"))["fixtures"]
    split = json.loads((ROOT / "experiments/pit16/split.json").read_text(encoding="utf-8"))
    dev = {x for x in split["dev"]}
    rows = []
    # 18 historical samples plus 18 PIT-16 DEV fixtures, explicitly including
    # unsafe families, compound violations, and clean hard negatives.
    for row in pit15[:18]:
        expected = row["known_expected_violations"]
        ts = row["teaching_signal"]
        rows.append({
            "gold_id": f"pit15:{row['candidate_id']}:{row['scenario_id']}",
            "source": "PIT15_HISTORICAL",
            "expected": {
                "resolves_conflict": "UNSUPPORTED_CONFLICT_RESOLUTION" in expected,
                "asserts_numeric_threshold": "UNSUPPORTED_NUMERIC_THRESHOLD" in expected,
                "asserts_temporal_rule": "UNSUPPORTED_TEMPORAL_RULE" in expected,
                "asserts_fallback_policy": "UNSUPPORTED_FALLBACK_POLICY" in expected,
                "asserts_globalization": "UNSUPPORTED_SCOPE_GENERALIZATION" in expected,
                "has_operational_signal": "EVIDENCE_GROUNDING_FAILURE" in expected,
                "abstains": row["scenario_id"] == "insufficient_evidence_001",
                "evidence_has_conflict": row["scenario_id"] == "conflicting_evidence_001",
                "supersession_supported": False if row["scenario_id"] == "conflicting_evidence_001" else None,
                "numeric_supported": False if "UNSUPPORTED_NUMERIC_THRESHOLD" in expected else None,
                "temporal_supported": False if "UNSUPPORTED_TEMPORAL_RULE" in expected else None,
                "fallback_supported": False if "UNSUPPORTED_FALLBACK_POLICY" in expected else None,
                "scope_supported": False if "UNSUPPORTED_SCOPE_GENERALIZATION" in expected else None,
            },
        })
    wanted = {
        "conflict-01","conflict-02","numeric-01","numeric-02","temporal-01","temporal-02",
        "fallback-01","fallback-02","scope-01","scope-02","grounding-01","grounding-02",
        "compound-01","compound-02","hard-numeric-01","hard-numeric-02","hard-temporal-01","hard-temporal-02"
    }
    dev_rows = [x for x in corpus if x["fixture_id"] in dev and x["fixture_id"] in wanted]
    for row in dev_rows:
        exp = set(row["expected_violation_classes"]); fam = row["family"]; ef = row["evidence"].get("facts", {})
        is_hard = fam == "hard_negative"
        signal_text = " ".join(str(row["teaching_signal"].get(k, "")) for k in ("inference","applicability_boundary","revision_trigger")).lower()
        rows.append({
            "gold_id": f"pit16dev:{row['fixture_id']}",
            "source": "PIT16_DEV",
            "expected": {
                "resolves_conflict": "UNSUPPORTED_CONFLICT_RESOLUTION" in exp or (is_hard and ef.get("supersession_supported") is True),
                "asserts_numeric_threshold": "UNSUPPORTED_NUMERIC_THRESHOLD" in exp or ef.get("supported_numeric_threshold") is True or bool(__import__('re').search(r"\b\d+\s*(?:days?|weeks?|months?|quarters?|years?)\b", signal_text)),
                "asserts_temporal_rule": "UNSUPPORTED_TEMPORAL_RULE" in exp or ef.get("supported_temporal_rule") is True,
                "asserts_fallback_policy": "UNSUPPORTED_FALLBACK_POLICY" in exp or ef.get("supported_fallback_policy") is True,
                "asserts_globalization": "UNSUPPORTED_SCOPE_GENERALIZATION" in exp or ef.get("global_scope_supported") is True,
                "has_operational_signal": "EVIDENCE_GROUNDING_FAILURE" in exp or bool(ef.get("allowed_operational_signals")),
                "abstains": False,
                "evidence_has_conflict": bool(ef.get("conflict_present", False)),
                "supersession_supported": bool(ef.get("supersession_supported", False)) if ef.get("conflict_present") else None,
                "numeric_supported": bool(ef.get("supported_numeric_threshold", False)) if ("UNSUPPORTED_NUMERIC_THRESHOLD" in exp or ef.get("supported_numeric_threshold") is True) else None,
                "temporal_supported": bool(ef.get("supported_temporal_rule", False)) if ("UNSUPPORTED_TEMPORAL_RULE" in exp or ef.get("supported_temporal_rule") is True) else None,
                "fallback_supported": bool(ef.get("supported_fallback_policy", False)) if ("UNSUPPORTED_FALLBACK_POLICY" in exp or ef.get("supported_fallback_policy") is True) else None,
                "scope_supported": bool(ef.get("global_scope_supported", False)) if ("UNSUPPORTED_SCOPE_GENERALIZATION" in exp or ef.get("global_scope_supported") is True) else None,
            },
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"version": "pit17-fact-goldset-v1", "samples": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"fact_gold_samples={len(rows)}")


if __name__ == "__main__":
    main()
