"""Support relations for Representation V3; policy semantics remain compatible with frozen Guardrail V3."""
from __future__ import annotations
from scope_lattice_v3 import relation, supported

def compute_support_relations(facts):
    ev=facts["evidence_state"]; ts=facts["teaching_signal_state"]
    allowed={str(x).lower() for x in ev.get("allowed_operational_signals",[])}; op=ts.get("operational_signals",[])
    op_supported=all(any(a in s.lower() for a in allowed) for s in op) if op else True
    numeric_supported=not ts["asserts_numeric_threshold"] or ev["has_numeric_policy"]
    scope_relation=relation(ts["asserted_scope"],ev["scope_level"])
    return {
        "supersession_supported":bool(ev["has_explicit_supersession"] or ev["has_explicit_correction"] or (ev["has_context_scope_distinction"] and not ev["has_conflict"])),
        "numeric_threshold_supported":bool(numeric_supported),
        "temporal_rule_supported":bool(not ts["asserts_temporal_rule"] or ev["has_temporal_policy"]),
        "fallback_policy_supported":bool(not ts["asserts_fallback_policy"] or ev["has_fallback_policy"]),
        "scope_supported":bool(supported(ts["asserted_scope"],ev["scope_level"])),
        "scope_relation":scope_relation,
        "operational_signals_supported":bool(op_supported),
        "provenance":{"evidence_scope":ev.get("scope_provenance"),"teaching_scope":ts.get("scope_provenance")},
    }
