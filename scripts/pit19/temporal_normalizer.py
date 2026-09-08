"""Temporal semantic normalization for Representation V3."""
from __future__ import annotations
import re
from primitive_schema_v3 import primitive
from quantitative_normalizer import NUM, NUMBER_VALUES

UNIT = r"(?:minutes?|hours?|days?|weeks?|months?|quarters?|years?)"
APPROX = r"(?:several|a few|few|a couple of|couple of|many)"
ACTION = re.compile(r"\b(?:after|before|expire|expires|expiry|decay|refresh|revalidate|recheck|revisit|reset|stale|invalidate|age out|sunset|retire|wait|inactive|inactivity|time gaps?)\b", re.I)
NEGATED = re.compile(r"\b(?:no|without|not)\b[^.\n]{0,55}\b(?:expiry|expiration|schedule|temporal rule|revalidation|refresh|decay|duration|time window)\b", re.I)


def _value(raw):
    t=raw.lower().strip(); return int(t) if t.isdigit() else NUMBER_VALUES.get(t)


def extract_temporal(text: str, source: str, force_policy: bool = False):
    out=[]
    chunks=[x.strip() for x in re.split(r"(?<=[.!?;])\s+|\n+", text) if x.strip()]
    for chunk in chunks:
        if source == "evidence" and NEGATED.search(chunk):
            continue
        policy = force_policy or ACTION.search(chunk)
        if policy:
            for m in re.finditer(rf"\b(?P<num>{NUM})[-\s]+(?P<unit>{UNIT})\b", chunk, re.I):
                out.append(primitive("TEMPORAL","EXACT_DURATION",source,m.group(0),value=_value(m.group("num")),unit=m.group("unit").lower()))
            for m in re.finditer(rf"\b(?P<num>{APPROX})\s+(?P<unit>{UNIT})\b", chunk, re.I):
                out.append(primitive("TEMPORAL","APPROX_DURATION",source,m.group(0),value=None,unit=m.group("unit").lower()))
        if re.search(r"\b(?:daily|weekly|monthly|quarterly|annually|periodically|from time to time|at regular intervals|every\s+(?:day|week|month|quarter|year))\b", chunk, re.I):
            out.append(primitive("TEMPORAL","PERIODIC_RULE",source,chunk))
        if re.search(r"\b(?:expire|expires|expiry|stale|age out|sunset|retire|after prolonged inactivity|after repeated time gaps)\b", chunk, re.I):
            out.append(primitive("TEMPORAL","EXPIRY_RULE",source,chunk))
        recency_word = re.search(r"\b(?:latest|most recent|newer|newest|later|latter|subsequent|afterward|afterwards|came after|comes after|follows|issued later|chronologically later|recent)\b", chunk, re.I)
        recency_subject = re.search(r"\b(?:instruction|preference|message|statement|guidance|request|signal)s?\b", chunk, re.I)
        if recency_word and recency_subject:
            out.append(primitive("TEMPORAL","RECENCY_RELATION",source,chunk))
    return _dedupe(out)


def _dedupe(items):
    seen=set(); out=[]
    for p in items:
        key=(p["family"],p["type"],p["surface"].lower())
        if key not in seen: seen.add(key); out.append(p)
    return out
