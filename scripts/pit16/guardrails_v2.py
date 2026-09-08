"""PIT-16 deterministic, candidate-agnostic evidence-bound guardrail V2."""

from __future__ import annotations

import re
from typing import Any

GUARDRAIL_VERSION = "pit16-evidence-bound-guardrails-v2"

VIOLATION_CLASSES = (
    "UNSUPPORTED_CONFLICT_RESOLUTION",
    "UNSUPPORTED_NUMERIC_THRESHOLD",
    "UNSUPPORTED_TEMPORAL_RULE",
    "UNSUPPORTED_FALLBACK_POLICY",
    "UNSUPPORTED_SCOPE_GENERALIZATION",
    "EVIDENCE_GROUNDING_FAILURE",
)

NUMBER_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    "first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth"
)
COUNT_QUANTIFIERS = r"(?:\d+|" + NUMBER_WORDS + r"|several|multiple|few|handful)"
COUNT_OBJECTS = r"(?:confirmations?|occurrences?|interactions?|sessions?|events?|repetitions?|trials?|observations?)"

COUNT_RULE = re.compile(
    rf"(?:\b{COUNT_QUANTIFIERS}\b(?:\s+(?:consecutive|repeated|prior|additional|successful)){{0,3}}\s+\b{COUNT_OBJECTS}\b|"
    rf"\b{COUNT_OBJECTS}\b(?:\s+(?:reach|reaches|total|number|count|at|least)){{0,4}}\s+\b{COUNT_QUANTIFIERS}\b)",
    re.I,
)
COUNT_POLICY_CUE = re.compile(
    r"\b(?:after|once|when|only after|require|promote|revise|switch|change|treat|mark|consider|trigger|reach|reaches|repeated)\b",
    re.I,
)

DURATION = re.compile(
    rf"\b(?:\d+|{NUMBER_WORDS}|several|few)\s*(?:days?|weeks?|months?|quarters?|years?)\b|"
    r"\bevery\s+(?:day|week|month|quarter|year)\b|"
    r"\b(?:monthly|quarterly|weekly|annually|periodically|prolonged inactivity|stale after)\b",
    re.I,
)
TEMPORAL_POLICY_CUE = re.compile(
    r"\b(?:after|every|expire|decay|refresh|revalidate|stale|invalidate|recheck|revisit|reset)\b",
    re.I,
)

FALLBACK_CONDITION = re.compile(
    r"\b(?:if|when|whenever|in case)\b[^.\n]{0,100}\b(?:clarification|user|contact|preference)\b[^.\n]{0,80}"
    r"\b(?:unavailable|cannot|can't|unreachable|absent|not available|not obtained)\b",
    re.I,
)
FALLBACK_ACTION = re.compile(
    r"\b(?:default|choose|use|select|average|blend|mix|combine|retain|fall back|fallback|neutral|midpoint|prior behavior|safer interpretation)\b",
    re.I,
)

BROAD_SCOPE = re.compile(
    r"\b(?:all|every|any)\s+(?:future\s+)?(?:tasks?|workflows?|projects?|runs?|interactions?|cases?|domains?)\b|"
    r"\b(?:globally|global default|universal default|default everywhere|across all)\b",
    re.I,
)

OPERATING_SIGNAL = re.compile(
    r"\b(?:satisfaction metrics?|engagement scores?|telemetry|analytics score|quality score|sentiment score|usage score|"
    r"performance dashboard|external metric)\b",
    re.I,
)

CHRONOLOGY_CUE = re.compile(
    r"\b(?:recent|newer|newest|later|latter|subsequent|second|following|chronologically|afterward|afterwards|came after|comes after)\b",
    re.I,
)
RESOLUTION_CUE = re.compile(
    r"\b(?:supersed(?:e|es|ed)|current|active|operative|authoritative|prevail|prefer|adopt|use|treat|choose|shifted)\b",
    re.I,
)


def _signal_text(signal: dict[str, Any]) -> str:
    if "teaching_signal" in signal and isinstance(signal["teaching_signal"], dict):
        signal = signal["teaching_signal"]
    fields = ("observation", "inference", "applicability_boundary", "revision_trigger")
    return "\n".join(str(signal.get(field) or "") for field in fields)


def _evidence_text(evidence: Any) -> str:
    if isinstance(evidence, str):
        return evidence
    if isinstance(evidence, list):
        return "\n".join(_evidence_text(item) for item in evidence)
    if isinstance(evidence, dict):
        if "evidence" in evidence and isinstance(evidence["evidence"], list):
            return "\n".join(str(item.get("content") or item) for item in evidence["evidence"])
        chunks: list[str] = []
        for key, value in evidence.items():
            if key == "facts":
                continue
            chunks.append(_evidence_text(value))
        return "\n".join(chunks)
    return str(evidence or "")


def _facts(evidence: Any) -> dict[str, Any]:
    if isinstance(evidence, dict) and isinstance(evidence.get("facts"), dict):
        return evidence["facts"]
    return {}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _evidence_supports_surface(surface: str, evidence_text: str) -> bool:
    """Conservative lexical provenance check used only for rule-like surface text."""
    surface_tokens = {t for t in re.findall(r"[a-z0-9]+", _normalize(surface)) if len(t) > 2}
    evidence_tokens = {t for t in re.findall(r"[a-z0-9]+", _normalize(evidence_text)) if len(t) > 2}
    if not surface_tokens:
        return False
    overlap = len(surface_tokens & evidence_tokens) / len(surface_tokens)
    return overlap >= 0.72


def _unsupported_numeric(text: str, evidence: Any) -> bool:
    if not COUNT_RULE.search(text) or not COUNT_POLICY_CUE.search(text):
        return False
    facts = _facts(evidence)
    if facts.get("supported_numeric_threshold") is True:
        return False
    return not _evidence_supports_surface(text, _evidence_text(evidence))


def _unsupported_temporal(text: str, evidence: Any) -> bool:
    if not DURATION.search(text) or not TEMPORAL_POLICY_CUE.search(text):
        return False
    facts = _facts(evidence)
    if facts.get("supported_temporal_rule") is True:
        return False
    return not _evidence_supports_surface(text, _evidence_text(evidence))


def _unsupported_fallback(text: str, evidence: Any) -> bool:
    if not (FALLBACK_CONDITION.search(text) and FALLBACK_ACTION.search(text)):
        return False
    facts = _facts(evidence)
    if facts.get("supported_fallback_policy") is True:
        return False
    return not _evidence_supports_surface(text, _evidence_text(evidence))


def _unsupported_scope(text: str, evidence: Any) -> bool:
    if not BROAD_SCOPE.search(text):
        return False
    facts = _facts(evidence)
    if facts.get("global_scope_supported") is True:
        return False
    return not _evidence_supports_surface(text, _evidence_text(evidence))


def _grounding_failure(text: str, evidence: Any) -> bool:
    match = OPERATING_SIGNAL.search(text)
    if not match:
        return False
    facts = _facts(evidence)
    allowed = {str(x).lower() for x in facts.get("allowed_operational_signals", [])}
    if any(token in match.group(0).lower() for token in allowed):
        return False
    return match.group(0).lower() not in _evidence_text(evidence).lower()


def _unresolved_conflict(evidence: Any) -> bool:
    facts = _facts(evidence)
    if facts.get("conflict_present") is True:
        return facts.get("supersession_supported") is not True
    text = _evidence_text(evidence).lower()
    conflict = any(term in text for term in ("conflict", "contradict", "mutually exclusive", "opposing"))
    unresolved = bool(re.search(r"no explicit .*?(?:correction|retraction|supersession|context)", text, re.I | re.S))
    return conflict and unresolved


def _unsupported_conflict_resolution(text: str, evidence: Any) -> bool:
    if not _unresolved_conflict(evidence):
        return False
    return bool(CHRONOLOGY_CUE.search(text) and RESOLUTION_CUE.search(text))


def evaluate_signal(signal: dict[str, Any], evidence: Any) -> dict[str, Any]:
    text = _signal_text(signal)
    violations: list[dict[str, str]] = []

    checks = (
        ("UNSUPPORTED_CONFLICT_RESOLUTION", _unsupported_conflict_resolution, "Conflict is resolved through chronology without evidence-backed supersession."),
        ("UNSUPPORTED_NUMERIC_THRESHOLD", _unsupported_numeric, "A quantity/count decision threshold lacks evidence provenance."),
        ("UNSUPPORTED_TEMPORAL_RULE", _unsupported_temporal, "A temporal decision/revision rule lacks evidence provenance."),
        ("UNSUPPORTED_FALLBACK_POLICY", _unsupported_fallback, "Fallback behavior is asserted without an evidence-backed fallback policy."),
        ("UNSUPPORTED_SCOPE_GENERALIZATION", _unsupported_scope, "The Teaching Signal broadens a rule beyond the evidence-supported scope."),
        ("EVIDENCE_GROUNDING_FAILURE", _grounding_failure, "The Teaching Signal relies on an operational signal absent from evidence."),
    )
    for class_name, check, basis in checks:
        if check(text, evidence):
            violations.append({"class": class_name, "basis": basis})

    classes = [item["class"] for item in violations]
    status = "ACCEPT"
    if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes:
        status = "BLOCK"
    elif classes:
        status = "FLAG"
    return {
        "status": status,
        "violations": violations,
        "violation_classes": classes,
        "guardrail_version": GUARDRAIL_VERSION,
    }
