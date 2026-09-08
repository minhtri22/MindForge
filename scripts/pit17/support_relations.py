"""Compute evidence support relations over canonical PIT-17 semantic facts."""

from __future__ import annotations

from typing import Any

from semantic_facts import SCOPE_LEVELS


def compute_support_relations(facts: dict[str, Any]) -> dict[str, bool]:
    ev = facts["evidence_state"]
    ts = facts["teaching_signal_state"]
    allowed = {str(x).lower() for x in ev.get("allowed_operational_signals", [])}
    op_supported = all(any(a in sig for a in allowed) for sig in ts.get("operational_signals", [])) if ts.get("operational_signals") else True
    scope_supported = SCOPE_LEVELS[ts["asserted_scope"]] <= SCOPE_LEVELS[ev["scope_level"]]
    return {
        "supersession_supported": bool(ev["has_explicit_supersession"] or ev["has_explicit_correction"] or (ev["has_context_scope_distinction"] and not ev["has_conflict"])),
        "numeric_threshold_supported": bool(not ts["asserts_numeric_threshold"] or ev["has_numeric_policy"] or (ev["has_temporal_policy"] and all(x.get("type") == "temporal_quantity_threshold" for x in ts.get("numeric_thresholds", [])))),
        "temporal_rule_supported": bool(not ts["asserts_temporal_rule"] or ev["has_temporal_policy"]),
        "fallback_policy_supported": bool(not ts["asserts_fallback_policy"] or ev["has_fallback_policy"]),
        "scope_supported": bool(scope_supported),
        "operational_signals_supported": bool(op_supported),
    }
