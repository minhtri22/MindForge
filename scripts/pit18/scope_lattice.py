"""Explicit frozen PIT-18 scope lattice."""

from __future__ import annotations

import re

SCOPE_LEVELS = {
    "OBSERVATION": 0,
    "SESSION": 1,
    "TASK": 2,
    "WORKFLOW": 3,
    "DOMAIN": 4,
    "GLOBAL": 5,
}

# Category cues are intentionally semantic families, not benchmark phrases.
GLOBAL_CUES = re.compile(
    r"\b(?:universally|globally|everywhere)\b|"
    r"\b(?:all\s+future|every|any)\s+(?:\w+[ -]?){0,2}(?:tasks?|workflows?|projects?|runs?|reruns?|interactions?|cases?|domains?)\b|"
    r"\ball\s+(?:tasks?|workflows?|projects?|runs?|reruns?|interactions?|cases?|domains?)\b|"
    r"\bacross\s+(?:all|every)\b|\bfor\s+all\s+future\b|"
    r"\b(?:tasks?|cases?|workflows?)\s+(?:lacking|without|outside)\b[^.\n]{0,80}\b(?:the\s+)?default\b",
    re.I,
)
UNTARGETED_UNIVERSAL = re.compile(r"\b(?:always|generally|by default)\b", re.I)
NEGATED_GLOBAL = re.compile(
    r"\b(?:does not|doesn't|do not|don't|not|never)\s+(?:apply|extend|generalize|broaden|carry)\s+"
    r"(?:to|across|into)?\s*(?:all|every|any)\s+(?:future\s+)?(?:task|workflow|project|run|interaction|case|domain)s?\b",
    re.I,
)
DOMAIN_CUES = re.compile(
    r"\b(?:domain|category|class of tasks|similar tasks|planning tasks|roadmap tasks|code reviews?|"
    r"experiments?|benchmarks?|experiment files?|experiment outputs?|raw logs?|benchmark evidence|"
    r"file handling|regulatory tasks|legal tasks|UI settings?|dashboard|dark mode|theme preference)\b",
    re.I,
)
WORKFLOW_CUES = re.compile(
    r"\b(?:workflow|pipeline|process|reruns?|recurring run|benchmark run|experiment run|"
    r"operational phase|stable phase|stable runs?)\b",
    re.I,
)
TASK_CUES = re.compile(
    r"\b(?:this|current|specific|one[- ]off|single)\s+(?:task|review|experiment|run|fixture|project|plan|case)\b|"
    r"\bfor\s+(?:the|this)\s+(?:task|review|experiment|run|project|plan|case)\b",
    re.I,
)
SESSION_CUES = re.compile(
    r"\b(?:this|current)\s+(?:session|conversation|chat)\b|\bfor\s+this\s+(?:session|conversation|chat)\b",
    re.I,
)
OBSERVATION_CUES = re.compile(
    r"\b(?:this|that|single|one)\s+(?:observation|message|statement|event|interaction)\b|"
    r"\bfor\s+this\s+(?:observation|message|statement|event|interaction)\b",
    re.I,
)
OBSERVATION_FRAME = re.compile(
    r"\bthis\s+observation\b\s+(?:concerns|describes|records|reports|notes|covers)\b",
    re.I,
)


def classify_scope(text: str, allow_untargeted_universal: bool = True) -> str:
    """Return the broadest explicitly asserted semantic scope."""
    text = NEGATED_GLOBAL.sub("", text)
    if GLOBAL_CUES.search(text):
        return "GLOBAL"
    # A sentence can mention a task as the subject of one observation without
    # asserting task-wide applicability. Preserve that semantic role.
    if OBSERVATION_FRAME.search(text):
        return "OBSERVATION"
    matches = [
        scope
        for scope, rx in (
            ("DOMAIN", DOMAIN_CUES), ("WORKFLOW", WORKFLOW_CUES), ("TASK", TASK_CUES),
            ("SESSION", SESSION_CUES), ("OBSERVATION", OBSERVATION_CUES),
        )
        if rx.search(text)
    ]
    if matches:
        return max(matches, key=lambda x: SCOPE_LEVELS[x])
    if allow_untargeted_universal and UNTARGETED_UNIVERSAL.search(text):
        return "GLOBAL"
    return "OBSERVATION"


def has_explicit_global_scope(text: str) -> bool:
    return bool(GLOBAL_CUES.search(NEGATED_GLOBAL.sub("", text)))


def relation(asserted_scope: str, evidence_scope: str) -> str:
    a = SCOPE_LEVELS[asserted_scope]
    e = SCOPE_LEVELS[evidence_scope]
    if a < e:
        return "NARROWER"
    if a == e:
        return "EQUAL"
    return "BROADER"


def supported(asserted_scope: str, evidence_scope: str) -> bool:
    return SCOPE_LEVELS[asserted_scope] <= SCOPE_LEVELS[evidence_scope]
