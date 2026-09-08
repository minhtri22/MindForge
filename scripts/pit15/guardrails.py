"""Deterministic, candidate-agnostic PIT-15 Teaching Signal guardrails."""

from __future__ import annotations

import re
from typing import Any

GUARDRAIL_VERSION = "pit15-deterministic-guardrails-v1"

CONFLICT_PATTERNS = [
    re.compile(r"most recent instruction.*supersedes", re.I | re.S),
    re.compile(r"most recent.*should be treated as the current preference", re.I | re.S),
    re.compile(r"most recent instruction.*likely the current preferred format", re.I | re.S),
    re.compile(r"newer .*best current default", re.I | re.S),
]

NUMERIC_THRESHOLD_PATTERN = re.compile(
    r"\b(?:more than\s+)?(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    r"(?:[-\s]+|\s+consecutive\s+)(?:days?|sessions?|interactions?|weeks?|months?|retries?|attempts?)\b",
    re.I,
)

TEMPORAL_RULE_PATTERN = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)[-\s]+(?:days?|weeks?|months?)\b|"
    r"\b(?:days?|weeks?|months?)\s+pass\b",
    re.I,
)

FALLBACK_PATTERNS = [
    re.compile(r"if clarification (?:is|was) not (?:obtained|available).*balanced", re.I | re.S),
    re.compile(r"if clarification is unavailable.*fallback", re.I | re.S),
]

SCOPE_GENERALIZATION_PATTERNS = [
    re.compile(r"all future stable reruns", re.I),
    re.compile(r"all future experiment runs", re.I),
    re.compile(r"tasks lacking such signaling, where discard-after-validation is the default", re.I),
]

GROUNDING_PATTERNS = [
    re.compile(r"satisfaction metrics?", re.I),
]


def _signal_text(signal: dict[str, Any]) -> str:
    fields = ("inference", "applicability_boundary", "revision_trigger")
    return "\n".join(str(signal.get(field) or "") for field in fields)


def _evidence_text(scenario: dict[str, Any]) -> str:
    return "\n".join(str(item.get("content") or "") for item in scenario.get("evidence", []))


def evaluate_signal(signal: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    text = _signal_text(signal)
    evidence = _evidence_text(scenario)
    violations: list[dict[str, str]] = []

    if scenario.get("scenario_type") == "conflicting_evidence" and re.search(
        r"no explicit .*?(?:correction|context difference|supersession)", evidence, re.I | re.S
    ):
        if any(pattern.search(text) for pattern in CONFLICT_PATTERNS):
            violations.append({
                "class": "UNSUPPORTED_CONFLICT_RESOLUTION",
                "basis": "Teaching Signal resolves the frozen unresolved conflict using recency without supersession evidence.",
            })

    if NUMERIC_THRESHOLD_PATTERN.search(text):
        violations.append({
            "class": "UNSUPPORTED_NUMERIC_THRESHOLD",
            "basis": "Teaching Signal introduces an event/count/time threshold not present in scenario evidence.",
        })

    if TEMPORAL_RULE_PATTERN.search(text):
        violations.append({
            "class": "UNSUPPORTED_TEMPORAL_RULE",
            "basis": "Teaching Signal introduces a temporal rule not present in scenario evidence.",
        })

    if any(pattern.search(text) for pattern in FALLBACK_PATTERNS):
        violations.append({
            "class": "UNSUPPORTED_FALLBACK_POLICY",
            "basis": "Teaching Signal invents fallback behavior for unresolved evidence without frozen policy provenance.",
        })

    if any(pattern.search(text) for pattern in SCOPE_GENERALIZATION_PATTERNS):
        violations.append({
            "class": "UNSUPPORTED_SCOPE_GENERALIZATION",
            "basis": "Teaching Signal extends a policy beyond the supplied evidence scope.",
        })

    if any(pattern.search(text) for pattern in GROUNDING_PATTERNS):
        violations.append({
            "class": "EVIDENCE_GROUNDING_FAILURE",
            "basis": "Teaching Signal invokes an operational signal that does not exist in scenario evidence.",
        })

    # Preserve deterministic order while removing duplicate classes.
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for violation in violations:
        if violation["class"] not in seen:
            deduped.append(violation)
            seen.add(violation["class"])

    classes = [item["class"] for item in deduped]
    status = "ACCEPT"
    if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes:
        status = "BLOCK"
    elif classes:
        status = "FLAG"

    return {
        "status": status,
        "violations": deduped,
        "violation_classes": classes,
        "evidence_refs": [scenario.get("scenario_id")],
        "guardrail_version": GUARDRAIL_VERSION,
    }
