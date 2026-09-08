"""Build provenance-preserving canonical facts from PIT-18 primitives."""

from __future__ import annotations

from typing import Any

from primitive_schema import REPRESENTATION_VERSION


def _of(primitives: list[dict[str, Any]], ptype: str) -> list[dict[str, Any]]:
    return [p for p in primitives if p["type"] == ptype]


def _scope(primitives: list[dict[str, Any]]) -> str:
    scopes = [p["attributes"].get("scope") for p in primitives if p["family"] == "SCOPE"]
    return scopes[-1] if scopes else "OBSERVATION"


def canonicalize(extracted: dict[str, Any], evidence: Any) -> dict[str, Any]:
    evp = extracted["evidence_primitives"]
    tsp = extracted["teaching_signal_primitives"]
    facts = evidence.get("facts", {}) if isinstance(evidence, dict) and isinstance(evidence.get("facts"), dict) else {}
    numeric_types = {"COUNT_THRESHOLD", "MIN_OCCURRENCES", "MAX_OCCURRENCES", "ORDINAL_TRIGGER"}
    numeric_ev = [p for p in evp if p["family"] == "QUANTIFIER" and p["type"] in numeric_types]
    temporal_ev = [p for p in evp if p["family"] == "TEMPORAL" and p["type"] != "RECENCY_ORDER"]
    fallback_ev = [p for p in evp if p["family"] == "FALLBACK"]
    numeric_ts = [p for p in tsp if p["family"] == "QUANTIFIER" and p["type"] in numeric_types]
    temporal_ts = [p for p in tsp if p["family"] == "TEMPORAL" and p["type"] != "RECENCY_ORDER"]
    fallback_ts = [p for p in tsp if p["family"] == "FALLBACK"]
    op = [p["attributes"]["operational_signal"] for p in tsp if "operational_signal" in p["attributes"]]

    # Frozen evidence fixtures may carry explicit support facts. They remain provenance inputs,
    # while surface-derived primitives provide the general representation path.
    has_numeric = bool(numeric_ev or facts.get("supported_numeric_threshold") is True)
    has_temporal = bool(temporal_ev or facts.get("supported_temporal_rule") is True)
    has_fallback = bool(fallback_ev or facts.get("supported_fallback_policy") is True)
    ev_scope = "GLOBAL" if facts.get("global_scope_supported") is True else _scope(evp)

    evidence_state = {
        "has_conflict": bool(_of(evp, "CONTRADICTS")),
        "has_explicit_correction": bool(_of(evp, "CORRECTS")),
        "has_explicit_supersession": bool(_of(evp, "SUPERSEDES")),
        "has_context_scope_distinction": any(p.get("attributes", {}).get("context_distinction") for p in evp),
        "has_numeric_policy": has_numeric,
        "has_temporal_policy": has_temporal,
        "has_fallback_policy": has_fallback,
        "scope_level": ev_scope,
        "evidence_refs": [],
        "allowed_operational_signals": list(facts.get("allowed_operational_signals", [])),
    }
    teaching_state = {
        "resolves_conflict": bool(_of(tsp, "RESOLVES_BY_RECENCY")),
        "asserts_supersession": bool(_of(tsp, "SUPERSEDES") or _of(tsp, "RESOLVES_BY_RECENCY")),
        "asserts_numeric_threshold": bool(numeric_ts),
        "numeric_thresholds": [p["attributes"] | {"type": p["type"], "surface": p["surface"]} for p in numeric_ts],
        "asserts_temporal_rule": bool(temporal_ts),
        "temporal_rules": [p["attributes"] | {"type": p["type"], "surface": p["surface"]} for p in temporal_ts],
        "asserts_fallback_policy": bool(fallback_ts),
        "fallback_policies": [p["type"] for p in fallback_ts],
        "asserted_scope": _scope(tsp),
        "asserts_globalization": _scope(tsp) == "GLOBAL",
        "abstains": bool(_of(tsp, "ABSTAINS")),
        "requests_clarification": bool(_of(tsp, "REQUESTS_CLARIFICATION")),
        "revision_rules": [],
        "operational_signals": op,
    }
    return {
        "representation_version": REPRESENTATION_VERSION,
        "evidence_state": evidence_state,
        "teaching_signal_state": teaching_state,
        "provenance": {
            "evidence_primitives": evp,
            "teaching_signal_primitives": tsp,
        },
    }
