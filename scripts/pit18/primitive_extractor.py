"""Deterministic semantic primitive extraction for PIT-18 Representation V2."""

from __future__ import annotations

import re
from typing import Any

from primitive_schema import primitive
from scope_lattice import SCOPE_LEVELS, classify_scope, has_explicit_global_scope
from surface_normalizer import sentences, textify

NUMBER_VALUES = {
    "zero": 0, "a": 1, "an": 1, "one": 1, "first": 1, "two": 2, "second": 2, "three": 3, "third": 3,
    "four": 4, "fourth": 4, "five": 5, "fifth": 5, "six": 6, "sixth": 6,
    "seven": 7, "seventh": 7, "eight": 8, "eighth": 8, "nine": 9, "ninth": 9,
    "ten": 10, "tenth": 10, "eleven": 11, "twelfth": 12, "twelve": 12,
    "twenty": 20, "thirty": 30, "sixty": 60, "ninety": 90,
}
NUMBER_TOKEN = r"(?:\d+|zero|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|sixty|ninety|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|several|multiple|few|handful)"
COUNT_TARGET = r"(?:confirmations?|occurrences?|interactions?|sessions?|events?|repetitions?|trials?|observations?|uses?|examples?|signals?|samples?)"
DURATION_UNIT = r"(?:minutes?|hours?|days?|weeks?|months?|quarters?|years?)"

COUNT_RX = re.compile(
    rf"\b(?P<num>{NUMBER_TOKEN})\b(?:\s+(?:or more|or fewer|consecutive|repeated|prior|additional|successful)){{0,3}}(?:\s+[a-z][\w-]*){{0,2}}\s+(?P<target>{COUNT_TARGET})\b|"
    rf"\b(?P<target2>{COUNT_TARGET})\b[^.\n]{{0,45}}\b(?:reach|reaches|total|count|at least|minimum|maximum)\b[^.\n]{{0,20}}\b(?P<num2>{NUMBER_TOKEN})\b",
    re.I,
)
COUNT_POLICY_CUE = re.compile(
    r"\b(?:after|once|when|only after|require|requires|required|promote|revise|switch|change|treat|mark|"
    r"consider|trigger|threshold|minimum|maximum|at least|no more than|fewer than|more than|repeated)\b",
    re.I,
)
ORDINAL_RX = re.compile(r"\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b", re.I)

DURATION_RX = re.compile(rf"\b(?P<num>{NUMBER_TOKEN})[-\s]*(?P<unit>{DURATION_UNIT})\b", re.I)
PERIODIC_RX = re.compile(r"\b(?:daily|weekly|monthly|quarterly|annually|periodically|every\s+(?:day|week|month|quarter|year))\b", re.I)
TEMPORAL_ACTION_RX = re.compile(
    r"\b(?:after|before|every|expire|expires|expiry|decay|refresh|revalidate|stale|invalidate|recheck|"
    r"revisit|reset|forget|drop|reduce confidence|age out|sunset|retire)\b",
    re.I,
)
NEGATED_TEMPORAL_POLICY_RX = re.compile(
    r"\b(?:no|without|not)\b[^.\n]{0,55}\b(?:expiry|expiration|ageing|aging|temporal|schedule|rule|"
    r"revalidation|recheck|refresh|decay|duration|time window)\b",
    re.I,
)

CONFLICT_RX = re.compile(r"\b(?:conflict|conflicting|contradict|contradictory|incompatible|mutually exclusive|opposing|disagree)\b", re.I)
UNRESOLVED_PAIR_RX = re.compile(
    r"\b(?:both|two|multiple)\s+(?:instructions?|preferences?|statements?|messages?)\b[^.\n]{0,180}"
    r"\b(?:no|without)\b[^.\n]{0,100}\b(?:correction|retraction|supersession|context)\b",
    re.I,
)
NO_SUPERSESSION_RX = re.compile(r"\b(?:no|without)\b[^.\n]{0,100}\b(?:correction|retraction|supersession|context difference|context distinction|clarification)\b", re.I)
CORRECTION_RX = re.compile(r"\b(?:correction|corrected|explicitly corrected|retract|retracted|withdraw|withdrawn)\b", re.I)
SUPERSESSION_RX = re.compile(r"\b(?:supersed(?:e|es|ed)|replace(?:s|d)?\s+(?:the\s+)?(?:earlier|previous|prior)|from now on|ignore the earlier|now prefer|new default|starting (?:now|today))\b", re.I)
CONTEXT_SCOPE_RX = re.compile(r"\b(?:only for|limited to|specific to|context[- ]specific|does not apply to|exception for|scoped to)\b", re.I)

RECENCY_RX = re.compile(
    r"\b(?:latest|most recent|newer|newest|later|latter|subsequent|following|second|afterward|afterwards|"
    r"came after|comes after|issued later|occurred later|chronologically later|recent instruction|later in the sequence)\b",
    re.I,
)
RESOLUTION_RX = re.compile(
    r"\b(?:current|active|operative|authoritative|prevail|prevails|govern|governs|choose|chosen|adopt|use|prefer|"
    r"treat|shifted|supersed(?:e|es|ed)?|replace(?:s|d)?|wins|takes precedence|controls)\b",
    re.I,
)
PRESERVE_CONFLICT_RX = re.compile(
    r"\b(?:unresolved|remain(?:s)? contradictory|cannot be treated as definitive|insufficient evidence to resolve|"
    r"do not choose|should not choose|preserve the conflict)\b",
    re.I,
)

FALLBACK_CONDITION_RX = re.compile(
    r"\b(?:if|when|whenever|in case|should)\b[^.\n]{0,120}\b(?:unknown|uncertain|unresolved|conflict|clarification|"
    r"user|contact|evidence|preference|source)\b[^.\n]{0,100}\b(?:unavailable|cannot|can't|absent|missing|not available|not obtained|insufficient|fails?|unreachable|unclear)\b",
    re.I,
)
FALLBACK_ACTION_RX = re.compile(
    r"\b(?:default|choose|use|select|average|blend|mix|combine|retain|fallback|fall back|neutral|midpoint|"
    r"prior behavior|safer interpretation|balanced approach|conservative option|keep the previous)\b",
    re.I,
)

ABSTAIN_RX = re.compile(r"\b(?:insufficient evidence|cannot (?:conclude|determine|infer)|no evidence to conclude|not enough evidence|do not infer|abstain|uncertain|unresolved)\b", re.I)
CLARIFY_RX = re.compile(r"\b(?:ask|request|seek|obtain)\b[^.\n]{0,45}\bclarif|\bwhich\b[^.\n]{0,40}\b(?:want|prefer|applies)\b", re.I)
LOW_CONF_RX = re.compile(r"\b(?:low confidence|uncertain|tentative|probably|possibly|may be|might be)\b", re.I)

OPERATING_RX = re.compile(
    r"\b(?:satisfaction metrics?|engagement scores?|telemetry|analytics score|quality score|sentiment score|"
    r"usage score|performance dashboard|external metric|click[- ]through rate|retention metric)\b",
    re.I,
)


def _facts(obj: Any) -> dict[str, Any]:
    return obj.get("facts", {}) if isinstance(obj, dict) and isinstance(obj.get("facts"), dict) else {}


def _number(raw: str):
    token = raw.lower()
    if token.isdigit():
        return int(token)
    return NUMBER_VALUES.get(token, token.upper())


def _scope_primitive(text: str, source: str):
    scope = classify_scope(text)
    return primitive("SCOPE", f"{scope}_SCOPE", source, text, scope=scope)


def _teaching_scope_primitive(signal_obj: Any, fallback_text: str):
    """Resolve the broadest explicit positive policy scope across semantic roles."""
    if not isinstance(signal_obj, dict):
        return _scope_primitive(fallback_text, "teaching_signal")
    inference = textify(signal_obj.get("inference", ""))
    boundary = textify(signal_obj.get("applicability_boundary", ""))
    revision = textify(signal_obj.get("revision_trigger", ""))
    if has_explicit_global_scope(inference):
        scope = "GLOBAL"
        surface = inference
    else:
        candidates = [
            (classify_scope(inference, allow_untargeted_universal=False), inference),
            (classify_scope(boundary), boundary),
            (classify_scope(revision, allow_untargeted_universal=False), revision),
        ]
        scope, surface = max(candidates, key=lambda item: SCOPE_LEVELS[item[0]])
        if not surface:
            surface = fallback_text
    return primitive("SCOPE", f"{scope}_SCOPE", "teaching_signal", surface, scope=scope)


def _quantifier_primitives(text: str, source: str, force_policy: bool = False):
    out = []
    for sentence in sentences(text):
        if not force_policy and not COUNT_POLICY_CUE.search(sentence):
            continue
        for m in COUNT_RX.finditer(sentence):
            raw = m.group("num") or m.group("num2")
            target = m.group("target") or m.group("target2")
            if raw.lower() in {"several", "multiple", "few", "handful"} and not re.search(
                r"\b(?:at least|after|only after|once|require|required|threshold|minimum|maximum|reach|reaches)\b",
                sentence,
                re.I,
            ):
                ptype = "REPETITION_TRIGGER"
            else:
                ptype = "ORDINAL_TRIGGER" if ORDINAL_RX.search(raw) else "COUNT_THRESHOLD"
            operator = "<=" if re.search(r"\b(?:maximum|no more than|or fewer|fewer than)\b", sentence, re.I) else ">="
            out.append(primitive("QUANTIFIER", ptype, source, m.group(0), value=_number(raw), target=target.lower(), operator=operator))
    return out


def _temporal_primitives(text: str, source: str, force_policy: bool = False):
    out = []
    for sentence in sentences(text):
        if source == "evidence" and NEGATED_TEMPORAL_POLICY_RX.search(sentence):
            continue
        duration_matches = list(DURATION_RX.finditer(sentence))
        if duration_matches and (force_policy or TEMPORAL_ACTION_RX.search(sentence)):
            for m in duration_matches:
                out.append(primitive("TEMPORAL", "AFTER_DURATION", source, m.group(0), value=_number(m.group("num")), unit=m.group("unit").lower()))
        if PERIODIC_RX.search(sentence) and TEMPORAL_ACTION_RX.search(sentence):
            out.append(primitive("TEMPORAL", "PERIODIC_REVALIDATION", source, sentence))
        if re.search(r"\b(?:expire|expiry|stale|age out|sunset|retire)\b", sentence, re.I):
            out.append(primitive("TEMPORAL", "EXPIRY_RULE", source, sentence))
        # RECENCY_ORDER is a relation used to select active/current state. A
        # bare elapsed-time phrase such as "thirty days later" is temporal
        # duration, not recency-based precedence.
        if RECENCY_RX.search(sentence) and (source != "teaching_signal" or RESOLUTION_RX.search(sentence)):
            out.append(primitive("TEMPORAL", "RECENCY_ORDER", source, sentence))
    return out


def _temporal_quantity_primitives(text: str, source: str, force_policy: bool = False):
    """Represent explicit duration quantities as quantitative policy primitives too."""
    out = []
    for sentence in sentences(text):
        if not force_policy and not TEMPORAL_ACTION_RX.search(sentence):
            continue
        # A duration value is normally a temporal parameter, not a second numeric policy.
        # Promote it to a numeric threshold only when the sentence explicitly compares
        # the quantity (for example "more than 60 days" or "at least two weeks").
        if not re.search(
            r"\b(?:more than|less than|fewer than|at least|at most|no more than|minimum|maximum|exceeds?|under|over)\b",
            sentence,
            re.I,
        ):
            continue
        for m in DURATION_RX.finditer(sentence):
            out.append(
                primitive(
                    "QUANTIFIER",
                    "COUNT_THRESHOLD",
                    source,
                    m.group(0),
                    value=_number(m.group("num")),
                    target=m.group("unit").lower(),
                    operator=">=",
                    temporal_quantity=True,
                )
            )
    return out


def _fallback_primitives(text: str, source: str):
    out = []
    for sentence in sentences(text):
        if FALLBACK_ACTION_RX.search(sentence) and FALLBACK_CONDITION_RX.search(sentence):
            if re.search(r"\b(?:conflict|contradict|unresolved)\b", sentence, re.I):
                kind = "FALLBACK_IF_CONFLICT"
            elif re.search(r"\b(?:unavailable|missing|absent|unreachable|not available|fails?)\b", sentence, re.I):
                kind = "FALLBACK_IF_UNAVAILABLE"
            else:
                kind = "FALLBACK_IF_UNKNOWN"
            out.append(primitive("FALLBACK", kind, source, sentence))
    return out


def extract_primitives(evidence: Any, teaching_signal: Any) -> dict[str, Any]:
    ev_text = textify(evidence)
    ts_text = textify(teaching_signal)
    ev_facts = _facts(evidence)
    signal_obj = teaching_signal.get("teaching_signal", teaching_signal) if isinstance(teaching_signal, dict) else {}
    revision_text = textify(signal_obj.get("revision_trigger", "")) if isinstance(signal_obj, dict) else ""
    boundary_text = textify(signal_obj.get("applicability_boundary", "")) if isinstance(signal_obj, dict) else ""
    inference_text = textify(signal_obj.get("inference", "")) if isinstance(signal_obj, dict) else ts_text
    policy_text = "\n".join(x for x in (inference_text, boundary_text, revision_text) if x)
    ev = []
    ts = []

    # Evidence relations/claims.
    conflict = bool(ev_facts.get("conflict_present") is True or CONFLICT_RX.search(ev_text) or UNRESOLVED_PAIR_RX.search(ev_text))
    if conflict:
        ev.append(primitive("RELATION", "CONTRADICTS", "evidence", ev_text))
    correction = bool(CORRECTION_RX.search(ev_text))
    if NO_SUPERSESSION_RX.search(ev_text):
        correction = False
    if correction:
        ev.append(primitive("RELATION", "CORRECTS", "evidence", ev_text))
        ev.append(primitive("CLAIM", "CLAIM_CORRECTION", "evidence", ev_text))
    supersession = bool(ev_facts.get("supersession_supported") is True or SUPERSESSION_RX.search(ev_text))
    if conflict and NO_SUPERSESSION_RX.search(ev_text):
        supersession = False
    if supersession:
        ev.append(primitive("RELATION", "SUPERSEDES", "evidence", ev_text))
    if CONTEXT_SCOPE_RX.search(ev_text):
        ev.append(primitive("RELATION", "APPLIES_TO", "evidence", ev_text, context_distinction=True))
    ev.extend(_quantifier_primitives(ev_text, "evidence"))
    ev.extend(_temporal_quantity_primitives(ev_text, "evidence"))
    ev.extend(_temporal_primitives(ev_text, "evidence"))
    ev.extend(_fallback_primitives(ev_text, "evidence"))
    ev.append(_scope_primitive(ev_text, "evidence"))

    # Teaching signal relations/claims.
    preserves = bool(PRESERVE_CONFLICT_RX.search(policy_text) or ((ABSTAIN_RX.search(policy_text) or CLARIFY_RX.search(policy_text)) and conflict))
    if preserves:
        ts.append(primitive("UNCERTAINTY", "PRESERVES_CONFLICT", "teaching_signal", ts_text))
    for sentence in sentences(policy_text):
        if RECENCY_RX.search(sentence) and RESOLUTION_RX.search(sentence):
            ts.append(primitive("TEMPORAL", "RECENCY_ORDER", "teaching_signal", sentence))
            if RESOLUTION_RX.search(sentence) and not preserves and not ABSTAIN_RX.search(policy_text):
                ts.append(primitive("RELATION", "RESOLVES_BY_RECENCY", "teaching_signal", sentence))
        if SUPERSESSION_RX.search(sentence):
            ts.append(primitive("RELATION", "SUPERSEDES", "teaching_signal", sentence))
        if CORRECTION_RX.search(sentence) and not re.search(r"\b(?:no|without)\b[^.\n]{0,40}\b(?:correction|retraction)\b", sentence, re.I):
            ts.append(primitive("RELATION", "CORRECTS", "teaching_signal", sentence))
        if re.search(r"\b(?:except|exception|unless|other than)\b", sentence, re.I):
            ts.append(primitive("RELATION", "EXCEPTS", "teaching_signal", sentence))
    ts.extend(_quantifier_primitives(policy_text, "teaching_signal"))
    ts.extend(_temporal_quantity_primitives(policy_text, "teaching_signal"))
    ts.extend(_temporal_primitives(policy_text, "teaching_signal"))
    if revision_text:
        existing = {(p["family"], p["type"], p["surface"]) for p in ts}
        extra = (
            _quantifier_primitives(revision_text, "teaching_signal", force_policy=True)
            + _temporal_quantity_primitives(revision_text, "teaching_signal", force_policy=True)
            + _temporal_primitives(revision_text, "teaching_signal", force_policy=True)
        )
        ts.extend(p for p in extra if (p["family"], p["type"], p["surface"]) not in existing)
    ts.extend(_fallback_primitives(policy_text, "teaching_signal"))
    if ABSTAIN_RX.search(policy_text):
        ts.append(primitive("UNCERTAINTY", "ABSTAINS", "teaching_signal", policy_text))
    if CLARIFY_RX.search(policy_text):
        ts.append(primitive("UNCERTAINTY", "REQUESTS_CLARIFICATION", "teaching_signal", policy_text))
    if LOW_CONF_RX.search(policy_text):
        ts.append(primitive("UNCERTAINTY", "LOW_CONFIDENCE", "teaching_signal", policy_text))
    for m in OPERATING_RX.finditer(policy_text):
        ts.append(primitive("CLAIM", "CLAIM_CURRENT_STATE", "teaching_signal", m.group(0), operational_signal=m.group(0).lower()))
    ts.append(_teaching_scope_primitive(signal_obj, ts_text))

    return {
        "evidence_text": ev_text,
        "teaching_signal_text": ts_text,
        "evidence_primitives": ev,
        "teaching_signal_primitives": ts,
    }
