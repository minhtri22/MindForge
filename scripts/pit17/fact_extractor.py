"""Deterministic, model-agnostic PIT-17 semantic fact extraction."""

from __future__ import annotations

import re
from typing import Any

from semantic_facts import SCHEMA_VERSION, SCOPE_LEVELS

NUMBERS = {
    "one": 1, "first": 1, "two": 2, "second": 2, "three": 3, "third": 3,
    "four": 4, "fourth": 4, "five": 5, "fifth": 5, "six": 6, "sixth": 6,
    "seven": 7, "seventh": 7, "eight": 8, "eighth": 8, "nine": 9, "ninth": 9,
    "ten": 10, "tenth": 10, "eleven": 11, "twelve": 12, "thirty": 30,
    "sixty": 60, "ninety": 90,
}

COUNT_UNIT = r"(?:confirmations?|occurrences?|interactions?|sessions?|events?|repetitions?|trials?|observations?|uses?)"
COUNT_QUANT = r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|first|second|third|fourth|fifth|several|multiple|few|handful"
COUNT_RX = re.compile(
    rf"(?:\b(?:after|on|once|when|only after|require|requires|reach|reaches|promote|switch|revise|change|treat|consider|trigger)\b[^.\n]{{0,70}})?"
    rf"(?:\b(?:at least\s+)?(?:{COUNT_QUANT})\b(?:\s+(?:or more|consecutive|repeated|prior|additional)){{0,3}}\s+\b{COUNT_UNIT}\b|"
    rf"\b{COUNT_UNIT}\b[^.\n]{{0,45}}\b(?:reach|reaches|count|total|at least)\b[^.\n]{{0,20}}\b(?:{COUNT_QUANT})\b)",
    re.I,
)

DURATION_RX = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|thirty|sixty|ninety|several|few)\s*(?:days?|weeks?|months?|quarters?|years?)\b|"
    r"\bevery\s+(?:day|week|month|quarter|year)\b|\b(?:daily|weekly|monthly|quarterly|annually|periodically)\b|"
    r"\b(?:prolonged inactivity|stale after|after prolonged inactivity)\b",
    re.I,
)
TEMPORAL_ACTION_RX = re.compile(r"\b(?:after|every|expire|decay|refresh|revalidate|stale|invalidate|recheck|revisit|reset|forget|drop|reduce confidence|pass|passes)\b", re.I)

FALLBACK_COND_RX = re.compile(r"\b(?:if|when|whenever|in case)\b[^.\n]{0,110}\b(?:clarification|contact|user|evidence|preference)\b[^.\n]{0,80}\b(?:unavailable|cannot|can't|absent|not available|not obtained|insufficient|unresolved)\b", re.I)
FALLBACK_ACTION_RX = re.compile(r"\b(?:default|choose|use|select|average|blend|mix|combine|retain|fallback|fall back|neutral|midpoint|prior behavior|safer interpretation|balanced)\b", re.I)

GLOBAL_RX = re.compile(r"\b(?:all|every|any)\s+(?:future\s+)?(?:tasks?|workflows?|projects?|runs?|interactions?|cases?|domains?)\b|\b(?:globally|global default|universal default|default everywhere|across all|all future)\b", re.I)
WORKFLOW_RX = re.compile(r"\b(?:workflow|experiment runs?|stable reruns?|benchmark work|file handling operations)\b", re.I)
DOMAIN_RX = re.compile(r"\b(?:planning|roadmap|code reviews?|experiments?|benchmarks?|dashboard|theme preference|regulatory|legal)\b", re.I)
TASK_RX = re.compile(r"\b(?:this task|this plan|this review|this experiment|this run|this fixture|this process|specific process|specific project)\b", re.I)

CONFLICT_EVIDENCE_RX = re.compile(r"\b(?:conflict|contradict|incompatible|mutually exclusive|opposing|two .* preferences)\b", re.I | re.S)
NO_SUPERSESSION_RX = re.compile(r"\bno\b[^.\n]{0,90}\b(?:correction|retraction|supersession|context difference|context distinction)\b", re.I)
EXPLICIT_SUPERSESSION_RX = re.compile(r"\b(?:replace(?:s|d)? previous|supersed(?:e|es|ed)|from now on|ignore earlier|correction:|corrected this|retract(?:s|ed)?|now prefer|starting today|replaces preference)\b", re.I)
CONTEXT_DISTINCTION_RX = re.compile(r"\b(?:only for|specific|when .* stable|during .* phase|does not apply|exception|context-specific|scoped)\b", re.I)

RESOLUTION_RX = re.compile(r"\b(?:current|active|operative|authoritative|prevail|choose|adopt|treat|supersed|shifted|replaces?)\b", re.I)
USE_AS_RESOLUTION_RX = re.compile(r"\buse\b[^.\n]{0,35}\b(?:as\s+)?(?:current|active|operative|authoritative|default)\b", re.I)
CHRONOLOGY_RX = re.compile(r"\b(?:recent|newer|newest|later|latter|subsequent|second|following|afterward|afterwards|follows|followed|came after|comes after|most recent)\b", re.I)
PRESERVE_CONFLICT_RX = re.compile(r"\b(?:unresolved|contradictory|cannot be treated as definitive|ask .* clarify|seek clarification|which format .* want|insufficient evidence to resolve)\b", re.I)

ABSTAIN_RX = re.compile(r"\b(?:insufficient evidence|cannot (?:conclude|determine|infer)|no evidence to conclude|not enough evidence|uncertain|unresolved)\b", re.I)
CLARIFY_RX = re.compile(r"\b(?:ask .* clarif|seek clarif|clarification|which .* want)\b", re.I)
OPERATING_RX = re.compile(r"\b(?:satisfaction metrics?|engagement scores?|telemetry|analytics score|quality score|sentiment score|usage score|performance dashboard|external metric)\b", re.I)


def _text(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(_text(x) for x in obj)
    if isinstance(obj, dict):
        if "teaching_signal" in obj and isinstance(obj["teaching_signal"], dict):
            return _text(obj["teaching_signal"])
        chunks = []
        for key in ("content", "observation", "inference", "applicability_boundary", "revision_trigger"):
            if key in obj:
                chunks.append(str(obj.get(key) or ""))
        if "evidence" in obj:
            chunks.append(_text(obj["evidence"]))
        if "observations" in obj:
            chunks.append(_text(obj["observations"]))
        return "\n".join(chunks)
    return str(obj or "")


def _facts(obj: Any) -> dict[str, Any]:
    return obj.get("facts", {}) if isinstance(obj, dict) and isinstance(obj.get("facts"), dict) else {}


def _scope(text: str) -> str:
    if GLOBAL_RX.search(text): return "GLOBAL"
    if WORKFLOW_RX.search(text): return "WORKFLOW"
    if DOMAIN_RX.search(text): return "DOMAIN"
    if TASK_RX.search(text): return "TASK"
    return "OBSERVATION"


def _numeric_rules(text: str) -> list[dict[str, Any]]:
    rows = []
    for m in COUNT_RX.finditer(text):
        surface = m.group(0).strip()
        token = re.search(r"\b\d+\b|\b(?:" + "|".join(NUMBERS) + r")\b|\b(?:several|multiple|few|handful)\b", surface, re.I)
        value: Any = None
        if token:
            raw = token.group(0).lower()
            value = int(raw) if raw.isdigit() else NUMBERS.get(raw, raw.upper())
        rows.append({"type": "count_threshold", "operator": ">=", "value": value, "surface": surface})
    return rows


def _temporal_rules(text: str) -> list[dict[str, Any]]:
    rows = []
    for m in DURATION_RX.finditer(text):
        window = text[max(0, m.start()-45):min(len(text), m.end()+45)]
        if TEMPORAL_ACTION_RX.search(window):
            rows.append({"type": "temporal_policy", "surface": m.group(0).strip()})
    return rows


def extract_evidence_state(evidence: Any) -> dict[str, Any]:
    text = _text(evidence)
    facts = _facts(evidence)
    has_conflict = bool(
        facts.get("conflict_present") is True
        or CONFLICT_EVIDENCE_RX.search(text)
        or (NO_SUPERSESSION_RX.search(text) and re.search(r"\b(?:two|both|multiple)\b[^.\n]{0,60}\b(?:instructions?|preferences?|observations?)\b", text, re.I))
    )
    explicit_correction = bool(re.search(r"\b(?:user_correction|correction:|corrected this|explicitly corrected)\b", text, re.I))
    explicit_supersession = bool(facts.get("supersession_supported") is True or EXPLICIT_SUPERSESSION_RX.search(text))
    if has_conflict and NO_SUPERSESSION_RX.search(text):
        explicit_supersession = False
    numeric = bool(facts.get("supported_numeric_threshold") is True or _numeric_rules(text))
    temporal = bool(facts.get("supported_temporal_rule") is True or _temporal_rules(text))
    fallback = bool(facts.get("supported_fallback_policy") is True or (FALLBACK_COND_RX.search(text) and FALLBACK_ACTION_RX.search(text)))
    global_scope = bool(facts.get("global_scope_supported") is True)
    scope = "GLOBAL" if global_scope else _scope(text)
    return {
        "has_conflict": has_conflict,
        "has_explicit_correction": explicit_correction,
        "has_explicit_supersession": explicit_supersession,
        "has_context_scope_distinction": bool(CONTEXT_DISTINCTION_RX.search(text)),
        "has_numeric_policy": numeric,
        "has_temporal_policy": temporal,
        "has_fallback_policy": fallback,
        "scope_level": scope,
        "evidence_refs": [],
        "allowed_operational_signals": list(facts.get("allowed_operational_signals", [])),
    }


def extract_teaching_signal_state(signal: Any) -> dict[str, Any]:
    text = _text(signal)
    numeric = _numeric_rules(text)
    temporal = _temporal_rules(text)
    for rule in temporal:
        surface = rule["surface"]
        token = re.search(r"\b\d+\b", surface, re.I)
        if token:
            raw = token.group(0).lower()
            numeric.append({"type": "temporal_quantity_threshold", "operator": ">=", "value": int(raw), "surface": surface})
    fallback = bool(FALLBACK_COND_RX.search(text) and FALLBACK_ACTION_RX.search(text))
    asserted_scope = _scope(text)
    preserves = bool(PRESERVE_CONFLICT_RX.search(text))
    clauses = re.split(r"(?<=[.!?;])\s+|\n+", text)
    resolves = bool(any((RESOLUTION_RX.search(c) or USE_AS_RESOLUTION_RX.search(c)) and CHRONOLOGY_RX.search(c) for c in clauses) and not preserves)
    op = [m.group(0).lower() for m in OPERATING_RX.finditer(text)]
    return {
        "resolves_conflict": resolves,
        "asserts_supersession": bool(RESOLUTION_RX.search(text) and (CHRONOLOGY_RX.search(text) or EXPLICIT_SUPERSESSION_RX.search(text))),
        "asserts_numeric_threshold": bool(numeric),
        "numeric_thresholds": numeric,
        "asserts_temporal_rule": bool(temporal),
        "temporal_rules": temporal,
        "asserts_fallback_policy": fallback,
        "fallback_policies": ["fallback"] if fallback else [],
        "asserted_scope": asserted_scope,
        "asserts_globalization": asserted_scope == "GLOBAL",
        "abstains": bool(ABSTAIN_RX.search(text)),
        "requests_clarification": bool(CLARIFY_RX.search(text)),
        "revision_rules": [],
        "operational_signals": op,
    }


def extract_semantic_facts(evidence: Any, signal: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_state": extract_evidence_state(evidence),
        "teaching_signal_state": extract_teaching_signal_state(signal),
    }
