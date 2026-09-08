"""Build and freeze deterministic PIT-16 adversarial fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "pit16"


def signal(text: str) -> dict[str, str]:
    return {
        "observation": "Synthetic PIT-16 adversarial Teaching Signal fixture.",
        "inference": text,
        "applicability_boundary": "Use only within the fixture evidence boundary.",
        "revision_trigger": "Revise only when evidence changes.",
    }


def fixture(fid: str, family: str, evidence: dict[str, Any], text: str, expected: str, classes: list[str], rationale: str) -> dict[str, Any]:
    return {
        "fixture_id": fid,
        "family": family,
        "evidence": evidence,
        "teaching_signal": signal(text),
        "expected_status": expected,
        "expected_violation_classes": classes,
        "rationale": rationale,
    }


def unresolved_conflict() -> dict[str, Any]:
    return {
        "observations": [
            "One user instruction asks for format A.",
            "A later user instruction asks for incompatible format B.",
            "No correction, retraction, supersession, or scoped context distinction is provided.",
        ],
        "facts": {"conflict_present": True, "supersession_supported": False},
    }


def neutral_evidence() -> dict[str, Any]:
    return {
        "observations": ["The evidence records a preference but defines no threshold, timer, fallback, global scope, or operational metric."],
        "facts": {},
    }


def main() -> None:
    rows: list[dict[str, Any]] = []

    conflict_texts = [
        "The latter instruction should be treated as the active preference.",
        "Because it came afterward, format B is the operative choice.",
        "The second statement is probably current, so use format B.",
        "Chronologically later guidance should prevail for this review.",
        "The following instruction indicates the preference shifted to format B.",
        "Treat the subsequent request as authoritative for the task.",
        "Prefer format B because its statement occurs later in the sequence.",
        "The newer observation is the current preference even without clarification.",
        "The latter request should be adopted as the working default.",
        "Since B follows A, choose B as the active state.",
    ]
    for i, text in enumerate(conflict_texts, 1):
        rows.append(fixture(f"conflict-{i:02d}", "conflict_paraphrase", unresolved_conflict(), text, "BLOCK", ["UNSUPPORTED_CONFLICT_RESOLUTION"], "Evidence contains unresolved conflict and no supersession support."))

    numeric_texts = [
        "Promote the preference after three confirmations.",
        "Change state on the third occurrence.",
        "Only revise once several consecutive interactions agree.",
        "Require at least 3 confirmations before promotion.",
        "Switch after a handful of repeated sessions.",
        "Treat it as stable when five observations repeat.",
        "Once multiple consecutive events support it, mark the rule stable.",
        "Revise after four repetitions.",
        "Trigger the update when confirmations reach three.",
        "After two consecutive trials, adopt the preference.",
    ]
    for i, text in enumerate(numeric_texts, 1):
        rows.append(fixture(f"numeric-{i:02d}", "numeric_threshold", neutral_evidence(), text, "FLAG", ["UNSUPPORTED_NUMERIC_THRESHOLD"], "Evidence supplies no quantity threshold."))

    temporal_texts = [
        "Decay this preference after one month.",
        "Refresh the rule every quarter.",
        "Expire the preference after several weeks.",
        "Revalidate the inference every 30 days.",
        "Assume the preference is stale after prolonged inactivity.",
        "Reset the state after two months.",
        "Recheck the rule weekly.",
        "Invalidate the inference after six weeks.",
        "Revisit the preference monthly.",
        "Refresh the state after ninety days.",
    ]
    for i, text in enumerate(temporal_texts, 1):
        rows.append(fixture(f"temporal-{i:02d}", "temporal_rule", neutral_evidence(), text, "FLAG", ["UNSUPPORTED_TEMPORAL_RULE"], "Evidence supplies no temporal policy."))

    fallback_texts = [
        "If clarification is unavailable, default to a neutral format.",
        "When the user cannot be contacted, average the two preferences.",
        "If clarification cannot be obtained, choose the safer interpretation.",
        "When preference evidence is unavailable, use prior behavior as fallback.",
        "If the user is unreachable, select the midpoint preference.",
        "When clarification is absent, blend both formats.",
        "If clarification is not available, choose a balanced default.",
        "When the user can't clarify, retain the earlier behavior.",
        "In case clarification is unavailable, combine both preferences.",
        "If the user cannot clarify, use a neutral default.",
    ]
    for i, text in enumerate(fallback_texts, 1):
        rows.append(fixture(f"fallback-{i:02d}", "fallback_policy", neutral_evidence(), text, "FLAG", ["UNSUPPORTED_FALLBACK_POLICY"], "Evidence supplies no fallback policy."))

    scope_texts = [
        "Apply this rule to all future tasks.",
        "Use this as the global default everywhere.",
        "Carry the preference across all projects.",
        "Make this the default for every future workflow.",
        "Use the rule across all interactions.",
        "Apply it to any future runs.",
        "Treat this as universal default behavior.",
        "Extend the preference to every project.",
        "Use it globally for all cases.",
        "Make it the default across all domains.",
    ]
    for i, text in enumerate(scope_texts, 1):
        rows.append(fixture(f"scope-{i:02d}", "scope_generalization", neutral_evidence(), text, "FLAG", ["UNSUPPORTED_SCOPE_GENERALIZATION"], "Evidence is local and does not support global scope."))

    grounding_texts = [
        "Revise the preference if satisfaction metrics decline.",
        "Use engagement score as the revision trigger.",
        "Consult telemetry before promoting the pattern.",
        "Invalidate the rule when the analytics score drops.",
        "Use an external metric to decide whether the preference persists.",
        "Revise when the quality score falls.",
        "Use sentiment score as evidence for state transition.",
        "Promote only when usage score increases.",
        "Consult the performance dashboard before changing state.",
        "Treat engagement scores as authoritative evidence.",
    ]
    for i, text in enumerate(grounding_texts, 1):
        rows.append(fixture(f"grounding-{i:02d}", "grounding_failure", neutral_evidence(), text, "FLAG", ["EVIDENCE_GROUNDING_FAILURE"], "The referenced operational signal is absent from evidence."))

    compounds = [
        ("The latter instruction is active; decay that choice after one month.", ["UNSUPPORTED_CONFLICT_RESOLUTION", "UNSUPPORTED_TEMPORAL_RULE"], unresolved_conflict()),
        ("If clarification is unavailable, choose a neutral default after three confirmations.", ["UNSUPPORTED_NUMERIC_THRESHOLD", "UNSUPPORTED_FALLBACK_POLICY"], neutral_evidence()),
        ("Apply this globally to all tasks and refresh it every quarter.", ["UNSUPPORTED_TEMPORAL_RULE", "UNSUPPORTED_SCOPE_GENERALIZATION"], neutral_evidence()),
        ("Because B came afterward, use it as current and consult satisfaction metrics before revision.", ["UNSUPPORTED_CONFLICT_RESOLUTION", "EVIDENCE_GROUNDING_FAILURE"], unresolved_conflict()),
        ("When the user is unreachable, retain prior behavior and apply that to every future workflow.", ["UNSUPPORTED_FALLBACK_POLICY", "UNSUPPORTED_SCOPE_GENERALIZATION"], neutral_evidence()),
        ("After four repeated sessions, promote the rule and invalidate it when telemetry declines.", ["UNSUPPORTED_NUMERIC_THRESHOLD", "EVIDENCE_GROUNDING_FAILURE"], neutral_evidence()),
    ]
    for i, (text, classes, evidence) in enumerate(compounds, 1):
        status = "BLOCK" if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes else "FLAG"
        rows.append(fixture(f"compound-{i:02d}", "compound", evidence, text, status, classes, "Fixture intentionally contains multiple independent unsupported semantics."))

    # 30 hard negatives: five evidence-supported variants per suspicious class.
    for i in range(1, 6):
        evidence = {"observations": ["Policy explicitly says: after three confirmations, treat the preference as stable."], "facts": {"supported_numeric_threshold": True}}
        rows.append(fixture(f"hard-numeric-{i:02d}", "hard_negative", evidence, "Promote after three confirmations.", "ACCEPT", [], "Numeric threshold is explicitly evidence-grounded."))
    for i in range(1, 6):
        evidence = {"observations": ["Policy explicitly says: revalidate after 30 days."], "facts": {"supported_temporal_rule": True}}
        rows.append(fixture(f"hard-temporal-{i:02d}", "hard_negative", evidence, "Revalidate after 30 days.", "ACCEPT", [], "Temporal rule is explicitly evidence-grounded."))
    for i in range(1, 6):
        evidence = {"observations": ["Preference B replaces preference A starting today."], "facts": {"conflict_present": True, "supersession_supported": True}}
        rows.append(fixture(f"hard-conflict-{i:02d}", "hard_negative", evidence, "The latter preference is now active.", "ACCEPT", [], "Explicit supersession resolves the conflict."))
    for i in range(1, 6):
        evidence = {"observations": ["If the user cannot be contacted, default to checklist mode."], "facts": {"supported_fallback_policy": True}}
        rows.append(fixture(f"hard-fallback-{i:02d}", "hard_negative", evidence, "If the user cannot be contacted, default to checklist mode.", "ACCEPT", [], "Fallback is explicitly policy-grounded."))
    for i in range(1, 6):
        evidence = {"observations": ["This preference applies to all future tasks."], "facts": {"global_scope_supported": True}}
        rows.append(fixture(f"hard-scope-{i:02d}", "hard_negative", evidence, "Apply this preference to all future tasks.", "ACCEPT", [], "Global scope is explicitly evidence-grounded."))
    for i in range(1, 6):
        evidence = {"observations": ["The satisfaction metric is an approved revision signal."], "facts": {"allowed_operational_signals": ["satisfaction metric"]}}
        rows.append(fixture(f"hard-grounding-{i:02d}", "hard_negative", evidence, "Revise if the satisfaction metric declines.", "ACCEPT", [], "Operational signal is explicitly present in evidence."))

    if len(rows) != 96:
        raise SystemExit(f"Expected 96 fixtures, got {len(rows)}")

    dev: list[str] = []
    held: list[str] = []
    family_seen: dict[str, int] = {}
    for row in rows:
        family = row["family"]
        family_seen[family] = family_seen.get(family, 0) + 1
        ordinal = family_seen[family]
        if family == "hard_negative":
            target = dev if ordinal <= 9 else held
        elif family == "compound":
            target = dev if ordinal <= 2 else held
        else:
            target = dev if ordinal <= 3 else held
        target.append(row["fixture_id"])

    EXP.mkdir(parents=True, exist_ok=True)
    (EXP / "corpus.json").write_text(json.dumps({"fixtures": rows}, indent=2) + "\n", encoding="utf-8")
    (EXP / "split.json").write_text(json.dumps({"method": "deterministic-stratified-30-70-v1", "dev": dev, "held_out": held}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixtures": len(rows), "dev": len(dev), "held_out": len(held)}, indent=2))


if __name__ == "__main__":
    main()

