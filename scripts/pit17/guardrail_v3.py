"""PIT-17 unified guardrail V3. Consumes canonical facts only."""

from __future__ import annotations

from typing import Any

GUARDRAIL_VERSION = "pit17-unified-semantic-fact-guardrail-v3"


def evaluate_facts(facts: dict[str, Any]) -> dict[str, Any]:
    ev = facts["evidence_state"]
    ts = facts["teaching_signal_state"]
    sup = facts["support_relations"]
    classes: list[str] = []
    if ev["has_conflict"] and ts["resolves_conflict"] and not sup["supersession_supported"]:
        classes.append("UNSUPPORTED_CONFLICT_RESOLUTION")
    if ts["asserts_numeric_threshold"] and not sup["numeric_threshold_supported"]:
        classes.append("UNSUPPORTED_NUMERIC_THRESHOLD")
    if ts["asserts_temporal_rule"] and not sup["temporal_rule_supported"]:
        classes.append("UNSUPPORTED_TEMPORAL_RULE")
    if ts["asserts_fallback_policy"] and not sup["fallback_policy_supported"]:
        classes.append("UNSUPPORTED_FALLBACK_POLICY")
    if ts["asserted_scope"] != "OBSERVATION" and not sup["scope_supported"]:
        classes.append("UNSUPPORTED_SCOPE_GENERALIZATION")
    if ts.get("operational_signals") and not sup["operational_signals_supported"]:
        classes.append("EVIDENCE_GROUNDING_FAILURE")
    status = "BLOCK" if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes else ("FLAG" if classes else "ACCEPT")
    return {"status": status, "violation_classes": classes, "guardrail_version": GUARDRAIL_VERSION}
