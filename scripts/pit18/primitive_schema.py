"""Frozen semantic primitive schema used by PIT-18 Representation V2."""

REPRESENTATION_VERSION = "pit18-representation-v2"
PRIMITIVE_SCHEMA_VERSION = "pit18-semantic-primitives-v1"

PRIMITIVE_FAMILIES = {
    "CLAIM": (
        "CLAIM_PREFERENCE", "CLAIM_CURRENT_STATE", "CLAIM_GLOBAL_POLICY",
        "CLAIM_TASK_POLICY", "CLAIM_EXCEPTION", "CLAIM_CORRECTION",
    ),
    "RELATION": (
        "CONTRADICTS", "SUPERSEDES", "CORRECTS", "EXCEPTS", "APPLIES_TO",
        "REVISES", "DEPENDS_ON", "RESOLVES_BY_RECENCY",
    ),
    "QUANTIFIER": (
        "COUNT_THRESHOLD", "MIN_OCCURRENCES", "MAX_OCCURRENCES",
        "ORDINAL_TRIGGER", "REPETITION_TRIGGER",
    ),
    "TEMPORAL": (
        "AFTER_DURATION", "BEFORE_TIME", "PERIODIC_REVALIDATION",
        "EXPIRY_RULE", "RECENCY_ORDER",
    ),
    "FALLBACK": (
        "FALLBACK_IF_UNKNOWN", "FALLBACK_IF_CONFLICT", "FALLBACK_IF_UNAVAILABLE",
    ),
    "UNCERTAINTY": (
        "ABSTAINS", "REQUESTS_CLARIFICATION", "LOW_CONFIDENCE", "PRESERVES_CONFLICT",
    ),
    "SCOPE": (
        "OBSERVATION_SCOPE", "SESSION_SCOPE", "TASK_SCOPE", "WORKFLOW_SCOPE",
        "DOMAIN_SCOPE", "GLOBAL_SCOPE",
    ),
}

ALL_PRIMITIVE_TYPES = tuple(x for family in PRIMITIVE_FAMILIES.values() for x in family)


def primitive(family: str, primitive_type: str, source: str, surface: str, **attrs):
    return {
        "family": family,
        "type": primitive_type,
        "source": source,
        "surface": surface,
        "attributes": attrs,
    }

