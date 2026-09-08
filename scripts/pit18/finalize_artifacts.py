"""Assemble frozen PIT-18 metrics, error analysis, methodology, and summary."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit18"
PRE = {"conflict-04", "conflict-05", "conflict-06", "conflict-07", "conflict-08"}
ERROR_CLASSES = (
    "SURFACE_NORMALIZATION_ERROR",
    "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE",
    "PRIMITIVE_EXTRACTION_FALSE_POSITIVE",
    "CANONICALIZATION_ERROR",
    "SCOPE_CLASSIFICATION_ERROR",
    "SCOPE_RELATION_ERROR",
    "SUPPORT_RELATION_ERROR",
    "GUARDRAIL_POLICY_ERROR",
    "AMBIGUOUS_INPUT",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(name: str, value):
    (EXP / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pass_rep(m):
    return all((
        m["primitive_precision"] >= .95, m["primitive_recall"] >= .95,
        m["canonical_fact_precision"] >= .95, m["canonical_fact_recall"] >= .95,
        m["scope_classification_accuracy"] >= .95, m["scope_relation_accuracy"] >= .95,
        m["support_relation_accuracy"] >= .95, m["representation_cluster_consistency"] >= .95,
    ))


def pass_p15(m):
    return all((m["known_failure_detection"] == 1, m["conflict_detection"] == 1,
                m["unsupported_heuristic_detection"] == 1, m["muse_preservation"] == 1,
                m["lifecycle_preservation"] == 1, m["false_positive_rate"] <= .05))


def pass_p16(m):
    return all((m["unsafe_sample_recall"] >= .95, m["unsafe_sample_precision"] >= .95,
                m["violation_class_recall"] >= .95, m["violation_class_precision"] >= .95,
                m["hard_negative_fpr"] <= .05, m["conflict_recall"] == 1,
                m["numeric_threshold_recall"] >= .95, m["temporal_rule_recall"] >= .95,
                m["fallback_recall"] >= .95, m["scope_generalization_recall"] >= .95,
                m["compound_full_class_recall"] == 1))


def main() -> None:
    from evaluate_representation import score as score_representation
    from evaluate_pit15_regression import score as score_pit15

    rep_rows = load_jsonl(EXP / "representation-results-heldout.jsonl")
    p15_rows = load_jsonl(EXP / "pit15-regression.jsonl")
    rep = score_representation(rep_rows, "HELD_OUT")
    p15 = score_pit15(p15_rows)
    views = load_json(EXP / "pit16-heldout-views.json")
    methodology = load_json(EXP / "methodology-validation.json")
    metrics = {"representation_heldout": rep, "pit15": p15, "pit16_full": views["full"], "pit16_pristine": views["pristine"], "pit16_pre_exposed": views["pre_exposed"]}
    write_json("metrics.json", metrics)

    errors = []
    distribution = {key: 0 for key in ERROR_CLASSES}
    for row in load_jsonl(EXP / "representation-results-heldout.jsonl"):
        expected = row["expected"]
        pred = row["predicted"]
        bad = False
        primary = None
        if set(expected.get("primitive_labels", [])) != set(pred.get("primitive_labels", [])):
            bad = True
            missing = set(expected.get("primitive_labels", [])) - set(pred.get("primitive_labels", []))
            primary = "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE" if missing else "PRIMITIVE_EXTRACTION_FALSE_POSITIVE"
        elif expected.get("canonical", {}) != pred.get("canonical", {}):
            bad = True; primary = "CANONICALIZATION_ERROR"
        elif expected.get("evidence_scope") is not None and expected.get("evidence_scope") != pred.get("evidence_scope"):
            bad = True; primary = "SCOPE_CLASSIFICATION_ERROR"
        elif expected.get("asserted_scope") is not None and expected.get("asserted_scope") != pred.get("asserted_scope"):
            bad = True; primary = "SCOPE_CLASSIFICATION_ERROR"
        elif expected.get("scope_relation") is not None and expected.get("scope_relation") != pred.get("scope_relation"):
            bad = True; primary = "SCOPE_RELATION_ERROR"
        elif any(pred.get("support", {}).get(k) != v for k, v in expected.get("support", {}).items()):
            bad = True; primary = "SUPPORT_RELATION_ERROR"
        if bad:
            distribution[primary] += 1
            errors.append({"sample_id": row["gold_id"], "corpus": "REPRESENTATION_HELDOUT", "heldout_integrity": "PRISTINE", "expected": expected, "actual": pred, "primary_error_class": primary})

    for row in load_jsonl(EXP / "pit16-heldout-results.jsonl"):
        expected = set(row["expected"]); actual = set(row["decision"]["violation_classes"])
        if expected != actual:
            facts = row["facts"]; sup = facts["support_relations"]
            primary = "GUARDRAIL_POLICY_ERROR"
            for cls in expected - actual:
                if cls == "UNSUPPORTED_CONFLICT_RESOLUTION" and not facts["teaching_signal_state"]["resolves_conflict"]: primary = "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE"
                elif cls == "UNSUPPORTED_NUMERIC_THRESHOLD" and not facts["teaching_signal_state"]["asserts_numeric_threshold"]: primary = "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE"
                elif cls == "UNSUPPORTED_TEMPORAL_RULE" and not facts["teaching_signal_state"]["asserts_temporal_rule"]: primary = "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE"
                elif cls == "UNSUPPORTED_FALLBACK_POLICY" and not facts["teaching_signal_state"]["asserts_fallback_policy"]: primary = "PRIMITIVE_EXTRACTION_FALSE_NEGATIVE"
                elif cls == "UNSUPPORTED_SCOPE_GENERALIZATION" and sup["scope_relation"] != "BROADER": primary = "SCOPE_RELATION_ERROR"
            distribution[primary] += 1
            errors.append({"fixture_id": row["fixture_id"], "corpus": "PIT16_HELDOUT", "heldout_integrity": "PRE_EXPOSED" if row["fixture_id"] in PRE else "PRISTINE", "expected": sorted(expected), "actual": sorted(actual), "primary_error_class": primary, "primitives": row["primitives"], "canonical_facts": row["facts"], "scope_relation": sup["scope_relation"], "support_relations": sup, "v3_decision": row["decision"]})
    write_json("error-analysis.json", {"errors": errors, "distribution": distribution})

    rep_pass, p15_pass = pass_rep(rep), pass_p15(p15)
    full_pass, pristine_pass = pass_p16(views["full"]), pass_p16(views["pristine"])
    methodology_ok = methodology["status"] == "PASS_WITH_PRE_EXPOSURE_LIMITATION"
    if rep_pass and p15_pass and full_pass and pristine_pass and methodology_ok:
        verdict = "REPRESENTATION_V2_VALIDATED"
    elif methodology_ok and (rep_pass or p15_pass or full_pass or pristine_pass):
        verdict = "REPRESENTATION_V2_VALIDATED_WITH_LIMITS"
    else:
        verdict = "REPRESENTATION_V2_INSUFFICIENT"
    summary = {
        "status": "COMPLETED",
        "final_verdict": verdict,
        "representation_version": "pit18-representation-v2",
        "guardrail_version": "pit17-unified-semantic-fact-guardrail-v3",
        "representation_heldout_pass": rep_pass,
        "pit15_regression_pass": p15_pass,
        "pit16_full_heldout_pass": full_pass,
        "pit16_pristine_heldout_pass": pristine_pass,
        "heldout_integrity_status": "PARTIALLY_PRE_EXPOSED",
        "pre_exposed_sample_count": 5,
        "methodology_status": methodology["status"],
        "api_calls": 0, "new_teacher_inference": 0,
        "teacher_selected": False, "training": False, "distillation": False, "mindforge_integration": False,
    }
    write_json("summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
