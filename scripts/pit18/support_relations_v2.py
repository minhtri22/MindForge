"""PIT-18 support relations computed over Representation V2 canonical facts."""

from __future__ import annotations

from typing import Any

from scope_lattice import relation, supported


def compute_support_relations(facts: dict[str, Any]) -> dict[str, Any]:
    ev = facts["evidence_state"]
    ts = facts["teaching_signal_state"]
    allowed = {str(x).lower() for x in ev.get("allowed_operational_signals", [])}
    op = ts.get("operational_signals", [])
    op_supported = all(any(a in signal for a in allowed) for signal in op) if op else True

    numeric_supported = True
    if ts["asserts_numeric_threshold"]:
        numeric_supported = bool(ev["has_numeric_policy"])
        # A duration quantity can be represented as a number but is supported by a temporal rule.
        if not numeric_supported and ev["has_temporal_policy"]:
            temporal_quantity_only = all(
                str(x.get("target", "")).lower() in {"day", "days", "week", "weeks", "month", "months", "quarter", "quarters", "year", "years"}
                for x in ts.get("numeric_thresholds", [])
            )
            numeric_supported = temporal_quantity_only

    scope_relation = relation(ts["asserted_scope"], ev["scope_level"])
    return {
        "supersession_supported": bool(
            ev["has_explicit_supersession"]
            or ev["has_explicit_correction"]
            or (ev["has_context_scope_distinction"] and not ev["has_conflict"])
        ),
        "numeric_threshold_supported": bool(numeric_supported),
        "temporal_rule_supported": bool(not ts["asserts_temporal_rule"] or ev["has_temporal_policy"]),
        "fallback_policy_supported": bool(not ts["asserts_fallback_policy"] or ev["has_fallback_policy"]),
        "scope_supported": bool(supported(ts["asserted_scope"], ev["scope_level"])),
        "scope_relation": scope_relation,
        "operational_signals_supported": bool(op_supported),
    }

