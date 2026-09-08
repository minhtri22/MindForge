"""Canonical facts for PIT-19 Representation V3."""
from __future__ import annotations
from typing import Any
from primitive_schema_v3 import REPRESENTATION_VERSION

NUMERIC={"EXACT_THRESHOLD","LOWER_BOUND_THRESHOLD","UPPER_BOUND_THRESHOLD","ORDINAL_TRIGGER","VAGUE_COUNT_POLICY"}
TEMPORAL={"EXACT_DURATION","APPROX_DURATION","PERIODIC_RULE","EXPIRY_RULE"}

def _has(ps,t): return any(p["type"]==t for p in ps)
def _scope(ps):
    p=next((x for x in reversed(ps) if x["family"]=="SCOPE"),None)
    if not p: return {"scope_level":"OBSERVATION","scope_target":None,"scope_constraints":[],"scope_provenance":""}
    a=p.get("attributes",{})
    return {k:a.get(k) for k in ("scope_level","scope_target","scope_constraints","scope_provenance")}

def canonicalize(extracted: dict[str,Any], evidence: Any):
    evp=extracted["evidence_primitives"]; tsp=extracted["teaching_signal_primitives"]
    facts=evidence.get("facts",{}) if isinstance(evidence,dict) and isinstance(evidence.get("facts"),dict) else {}
    nev=[p for p in evp if p["type"] in NUMERIC]; nts=[p for p in tsp if p["type"] in NUMERIC]
    tev=[p for p in evp if p["type"] in TEMPORAL]; tts=[p for p in tsp if p["type"] in TEMPORAL]
    fev=[p for p in evp if p["family"]=="FALLBACK"]; fts=[p for p in tsp if p["family"]=="FALLBACK"]
    evscope=_scope(evp); tsscope=_scope(tsp)
    if facts.get("global_scope_supported") is True: evscope["scope_level"]="GLOBAL"
    op=[p["attributes"]["operational_signal"] for p in tsp if "operational_signal" in p.get("attributes",{})]
    evidence_state={
        "has_conflict":_has(evp,"CONFLICT_EXISTS"),
        "has_explicit_correction":_has(evp,"CORRECTION"),
        "has_explicit_supersession":_has(evp,"EXPLICIT_SUPERSESSION"),
        "has_context_scope_distinction":_has(evp,"CONTEXT_SPLIT"),
        "has_numeric_policy":bool(nev or facts.get("supported_numeric_threshold") is True),
        "has_temporal_policy":bool(tev or facts.get("supported_temporal_rule") is True),
        "has_fallback_policy":bool(fev or facts.get("supported_fallback_policy") is True),
        "scope_level":evscope["scope_level"] or "OBSERVATION",
        "scope_target":evscope["scope_target"],"scope_constraints":evscope["scope_constraints"] or [],"scope_provenance":evscope["scope_provenance"],
        "evidence_refs":[],"allowed_operational_signals":list(facts.get("allowed_operational_signals",[])),
    }
    teaching_state={
        "resolves_conflict":bool(_has(evp,"CONFLICT_EXISTS") and (_has(tsp,"IMPLICIT_SELECTION") or _has(tsp,"EXPLICIT_SUPERSESSION"))),
        "asserts_supersession":_has(tsp,"EXPLICIT_SUPERSESSION") or _has(tsp,"IMPLICIT_SELECTION"),
        "asserts_numeric_threshold":bool(nts),
        "numeric_thresholds":[p["attributes"]|{"type":p["type"],"surface":p["surface"]} for p in nts],
        "asserts_temporal_rule":bool(tts),
        "temporal_rules":[p["attributes"]|{"type":p["type"],"surface":p["surface"]} for p in tts],
        "asserts_fallback_policy":bool(fts),"fallback_policies":[p["type"] for p in fts],
        "asserted_scope":tsscope["scope_level"] or "OBSERVATION",
        "scope_target":tsscope["scope_target"],"scope_constraints":tsscope["scope_constraints"] or [],"scope_provenance":tsscope["scope_provenance"],
        "asserts_globalization":tsscope["scope_level"]=="GLOBAL",
        "abstains":_has(tsp,"ABSTAINS"),"requests_clarification":_has(tsp,"REQUESTS_CLARIFICATION"),
        "revision_rules":[],"operational_signals":op,
    }
    return {"representation_version":REPRESENTATION_VERSION,"evidence_state":evidence_state,"teaching_signal_state":teaching_state,"provenance":{"evidence_primitives":evp,"teaching_signal_primitives":tsp}}
