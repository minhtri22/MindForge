"""Semantic primitive schema for PIT-19 Representation V3."""
from __future__ import annotations

REPRESENTATION_VERSION = "pit19-representation-v3"
PRIMITIVE_SCHEMA_VERSION = "pit19-semantic-primitives-v3"

PRIMITIVE_FAMILIES = {
    "RELATION": (
        "CONFLICT_EXISTS", "EXPLICIT_SUPERSESSION", "IMPLICIT_SELECTION",
        "CORRECTION", "CONTEXT_SPLIT", "EXCEPTS",
    ),
    "QUANTIFIER": (
        "EXACT_THRESHOLD", "LOWER_BOUND_THRESHOLD", "UPPER_BOUND_THRESHOLD",
        "ORDINAL_TRIGGER", "VAGUE_COUNT_POLICY",
    ),
    "TEMPORAL": (
        "EXACT_DURATION", "APPROX_DURATION", "PERIODIC_RULE", "EXPIRY_RULE",
        "RECENCY_RELATION",
    ),
    "FALLBACK": (
        "FALLBACK_IF_UNKNOWN", "FALLBACK_IF_CONFLICT", "FALLBACK_IF_UNAVAILABLE",
    ),
    "UNCERTAINTY": (
        "ABSTAINS", "REQUESTS_CLARIFICATION", "LOW_CONFIDENCE", "PRESERVES_CONFLICT",
    ),
    "SCOPE": (
        "OBSERVATION_SCOPE", "TURN_SCOPE", "SESSION_SCOPE", "TASK_SCOPE",
        "WORKFLOW_SCOPE", "DOMAIN_SCOPE", "GLOBAL_SCOPE", "CONTEXTUAL_SCOPE",
    ),
    "CLAIM": ("OPERATIONAL_SIGNAL",),
}


def primitive(family: str, primitive_type: str, source: str, surface: str, **attrs):
    return {
        "family": family,
        "type": primitive_type,
        "source": source,
        "surface": surface,
        "attributes": attrs,
    }
