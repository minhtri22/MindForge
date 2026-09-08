"""Quantitative semantic normalization for Representation V3."""
from __future__ import annotations
import re
from primitive_schema_v3 import primitive

NUMBER_VALUES = {
    "zero": 0, "a": 1, "an": 1, "one": 1, "first": 1, "two": 2, "second": 2, "three": 3, "third": 3,
    "four": 4, "fourth": 4, "five": 5, "fifth": 5, "six": 6, "sixth": 6,
    "seven": 7, "seventh": 7, "eight": 8, "eighth": 8, "nine": 9, "ninth": 9,
    "ten": 10, "tenth": 10, "eleven": 11, "twelve": 12, "twenty": 20,
    "thirty": 30, "sixty": 60, "ninety": 90,
}
NUM = r"(?:\d+|zero|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|sixty|ninety)"
ORD = r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
VAGUE = r"(?:several|multiple|a few|few|a handful|handful|a number of)"
TARGET = r"(?:confirmations?|occurrences?|interactions?|sessions?|events?|repetitions?|trials?|observations?|uses?|examples?|signals?|samples?|checks?|reports?)"
DURATION_TARGET = r"(?:minutes?|hours?|days?|weeks?|months?|quarters?|years?)"

POLICY_CUE = re.compile(r"\b(?:after|upon|once|when|only after|require|requires|required|trigger|threshold|minimum|maximum|at least|at most|no more than|up to|promote|revise|switch|change|mark|consider|until)\b", re.I)


def _value(raw: str):
    token = raw.lower().strip()
    return int(token) if token.isdigit() else NUMBER_VALUES.get(token)


def extract_quantifiers(text: str, source: str, force_policy: bool = False):
    out = []
    chunks = [x.strip() for x in re.split(r"(?<=[.!?;])\s+|\n+", text) if x.strip()]
    for chunk in chunks:
        if not force_policy and not POLICY_CUE.search(chunk):
            continue
        # Ordinal trigger: "on the third occurrence", "third occurrence".
        for m in re.finditer(rf"\b(?P<num>{ORD})\s+(?P<target>{TARGET})\b", chunk, re.I):
            out.append(primitive("QUANTIFIER", "ORDINAL_TRIGGER", source, m.group(0), value=_value(m.group("num")), target=m.group("target").lower(), operator="=="))
        for m in re.finditer(rf"\b(?P<target>{TARGET})\s+number\s+(?P<num>{NUM}|{ORD})\b", chunk, re.I):
            out.append(primitive("QUANTIFIER", "ORDINAL_TRIGGER", source, m.group(0), value=_value(m.group("num")), target=m.group("target").lower(), operator="=="))
        patterns = [
            ("LOWER_BOUND_THRESHOLD", rf"\b(?:at least|minimum(?:\s+of)?|no fewer than)\s+(?P<num>{NUM})\s+(?P<target>{TARGET})\b", ">="),
            ("UPPER_BOUND_THRESHOLD", rf"\b(?:at most|maximum(?:\s+of)?|no more than|up to)\s+(?P<num>{NUM})\s+(?P<target>{TARGET})\b", "<="),
            ("LOWER_BOUND_THRESHOLD", rf"\b(?P<num>{NUM})\s+or\s+(?:more|additional)(?:\s+[\w-]+){{0,2}}\s+(?P<target>{TARGET})\b", ">="),
            ("EXACT_THRESHOLD", rf"\b(?:after|once|require(?:s|d)?|needs?)\s+(?P<num>{NUM})(?:\s+[\w-]+){{0,2}}\s+(?P<target>{TARGET})\b", ">="),
            ("EXACT_THRESHOLD", rf"\b(?P<num>{NUM})(?:\s+or\s+additional)?(?:\s+[\w-]+){{0,2}}\s+(?P<target>{TARGET})\b", ">="),
            ("LOWER_BOUND_THRESHOLD", rf"\b(?:more than|over|at least)\s+(?P<num>{NUM})\s+(?P<target>{DURATION_TARGET})\b", ">="),
            ("UPPER_BOUND_THRESHOLD", rf"\b(?:less than|under|at most|no more than)\s+(?P<num>{NUM})\s+(?P<target>{DURATION_TARGET})\b", "<="),
        ]
        occupied = set()
        for ptype, pattern, op in patterns:
            for m in re.finditer(pattern, chunk, re.I):
                span = m.span()
                if any(a <= span[0] < b or a < span[1] <= b for a,b in occupied):
                    continue
                occupied.add(span)
                out.append(primitive("QUANTIFIER", ptype, source, m.group(0), value=_value(m.group("num")), target=m.group("target").lower(), operator=op))
        if POLICY_CUE.search(chunk):
            for m in re.finditer(rf"\b(?P<num>{VAGUE})(?:\s+of)?(?:\s+repeated|\s+consecutive)?\s+(?P<target>{TARGET})\b", chunk, re.I):
                out.append(primitive("QUANTIFIER", "VAGUE_COUNT_POLICY", source, m.group(0), value=None, target=m.group("target").lower(), operator=None))
            for m in re.finditer(rf"\b(?P<target>{TARGET})\s+(?:reach|reaches|reached|total|count)\s+(?P<num>{NUM})\b", chunk, re.I):
                out.append(primitive("QUANTIFIER", "EXACT_THRESHOLD", source, m.group(0), value=_value(m.group("num")), target=m.group("target").lower(), operator=">="))
        if re.search(r"\brepeated\s+(?:a few|several)\s+times\b", chunk, re.I):
            out.append(primitive("QUANTIFIER", "VAGUE_COUNT_POLICY", source, chunk, value=None, target="repetitions", operator=None))
    return _dedupe(out)


def _dedupe(items):
    seen=set(); out=[]
    for p in items:
        key=(p["family"],p["type"],p["surface"].lower())
        if key not in seen:
            seen.add(key); out.append(p)
    return out
