"""Deterministic semantic primitive extraction for PIT-19 Representation V3."""
from __future__ import annotations
import re, sys
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
PIT18=HERE.parent/"pit18"
if str(PIT18) not in sys.path: sys.path.insert(0,str(PIT18))
from surface_normalizer import sentences, textify
from primitive_schema_v3 import primitive
from quantitative_normalizer import extract_quantifiers
from temporal_normalizer import extract_temporal
from scope_lattice_v3 import classify_scope

CONFLICT = re.compile(r"\b(?:conflict|conflicting|contradict|contradictory|incompatible|mutually exclusive|opposing|disagree|cannot both|at odds|pull in different directions)\b", re.I)
UNRESOLVED = re.compile(r"\b(?:unresolved|no (?:explicit )?correction|no (?:explicit )?retraction|no (?:explicit )?supersession|without correction|without retraction|neither .* revoked|no indication .* replaced|no .* context (?:difference|distinction))\b", re.I)
CORRECTION = re.compile(r"\b(?:correct(?:ed|ion)?|retract(?:ed|ion)?|withdrawn?|revok(?:e|ed)|mistaken|was wrong)\b", re.I)
SUPERSESSION = re.compile(r"\b(?:supersed(?:e|es|ed)|replace(?:s|d)?\s+(?:the\s+)?(?:earlier|previous|prior)|from now on|new default|previous .* revoked|earlier .* revoked|no longer use|use .* instead|starting (?:now|today))\b", re.I)
CONTEXT_SPLIT = re.compile(r"\b(?:only for|limited to|specific to|context[- ]specific|does not apply to|exception for|scoped to|in .* context but not|separate contexts?)\b", re.I)
RECENCY = re.compile(r"\b(?:latest|most recent|newer|newest|later|latter|subsequent|following instruction|afterward|afterwards|came after|comes after|follows|issued later|chronologically later|second statement|second request)\b", re.I)
SELECT = re.compile(r"\b(?:current|active|operative|authoritative|prevail|prevails|govern|governs|choose|adopt|use|prefer|working default|active state|takes precedence|controls|should be followed|should apply|shifted|shift to|indicates .* shifted|becomes operative)\b", re.I)
PRESERVE = re.compile(r"\b(?:unresolved|do not choose|should not choose|preserve (?:the )?conflict|cannot determine which|insufficient evidence to resolve|ask .* clarification before choosing)\b", re.I)
ABSTAIN = re.compile(r"\b(?:insufficient evidence|no evidence to conclude|cannot (?:conclude|determine|infer)|not enough evidence|do not infer|abstain|remain uncertain)\b", re.I)
CLARIFY = re.compile(r"\b(?:ask|request|seek|obtain)\b[^.\n]{0,60}\bclarif|\bwhich\b[^.\n]{0,50}\b(?:want|prefer|applies)\b", re.I)
LOW_CONF = re.compile(r"\b(?:low confidence|uncertain|tentative|probably|possibly|may be|might be)\b", re.I)
FALLBACK_CONDITION = re.compile(r"\b(?:if|when|whenever|in case|should)\b[^.\n]{0,160}\b(?:unknown|uncertain|unresolved|(?:preferences?|instructions?|evidence)\s+conflicts?|clarification(?:\s+is)?\s+(?:absent|unavailable|not obtained)|unavailable|cannot\s+(?:clarify|be contacted|be reached|be obtained)|can't\s+(?:clarify|be contacted|be reached|be obtained)|(?:source|user)\s+(?:is\s+)?absent|missing|not available|not obtained|insufficient|unreachable|unclear)\b", re.I)
FALLBACK_ACTION = re.compile(r"\b(?:default|choose|use|select|retain|average|fallback|fall back|neutral|midpoint|previous state|prior behavior|safer interpretation|conservative option|keep the previous|blend|combine|provide)\b", re.I)
OP_SIGNAL = re.compile(r"\b(?:satisfaction metrics?|engagement scores?|telemetry|analytics score|quality score|sentiment score|usage score|performance dashboard|external metric|click[- ]through rate|retention metric)\b", re.I)


def _facts(obj):
    return obj.get("facts",{}) if isinstance(obj,dict) and isinstance(obj.get("facts"),dict) else {}


def _scope_primitive(text, source):
    s=classify_scope(text)
    ptype=f"{s['scope_level']}_SCOPE"
    return primitive("SCOPE",ptype,source,text,**s)


def _teaching_scope(signal_obj, fallback):
    if not isinstance(signal_obj,dict): return _scope_primitive(fallback,"teaching_signal")
    inf=textify(signal_obj.get("inference","")); boundary=textify(signal_obj.get("applicability_boundary","")); revision=textify(signal_obj.get("revision_trigger",""))
    # Explicitly broad inference is semantically authoritative. Otherwise an explicit
    # applicability boundary defines the scope and prevents incidental nouns from broadening it.
    inf_scope=classify_scope(inf)
    strong_global=bool(re.search(r"\b(?:universally|globally|everywhere|all\s+future|any\s+future|every\s+future|across\s+all|every\s+project|all\s+domains|universal\s+default|global\s+default)\b",inf,re.I))
    if strong_global: chosen=inf_scope
    elif boundary: chosen=classify_scope(boundary)
    elif inf: chosen=inf_scope
    elif revision: chosen=classify_scope(revision)
    else: chosen=classify_scope(fallback)
    surface=inf if chosen is inf_scope else (boundary or inf or revision or fallback)
    return primitive("SCOPE",f"{chosen['scope_level']}_SCOPE","teaching_signal",surface,**chosen)


def _fallback(text, source):
    out=[]
    for s in sentences(text):
        if FALLBACK_ACTION.search(s) and FALLBACK_CONDITION.search(s):
            if re.search(r"\b(?:conflict|contradict|unresolved)\b",s,re.I): kind="FALLBACK_IF_CONFLICT"
            elif re.search(r"\b(?:unavailable|missing|absent|unreachable|not available|fails?)\b",s,re.I): kind="FALLBACK_IF_UNAVAILABLE"
            else: kind="FALLBACK_IF_UNKNOWN"
            out.append(primitive("FALLBACK",kind,source,s))
    return out


def extract_primitives(evidence: Any, teaching_signal: Any):
    ev_text=textify(evidence); ts_text=textify(teaching_signal); evfacts=_facts(evidence)
    signal_obj=teaching_signal.get("teaching_signal",teaching_signal) if isinstance(teaching_signal,dict) else {}
    inference=textify(signal_obj.get("inference","")) if isinstance(signal_obj,dict) else ts_text
    boundary=textify(signal_obj.get("applicability_boundary","")) if isinstance(signal_obj,dict) else ""
    revision=textify(signal_obj.get("revision_trigger","")) if isinstance(signal_obj,dict) else ""
    main_policy="\n".join(x for x in (inference,boundary) if x) or ts_text
    policy="\n".join(x for x in (main_policy,revision) if x)
    ev=[]; ts=[]

    multiple_preference_context=bool(len(re.findall(r"\b(?:instruction|preference|statement|message)s?\b",ev_text,re.I))>=2 and UNRESOLVED.search(ev_text))
    conflict=bool(evfacts.get("conflict_present") is True or CONFLICT.search(ev_text) or multiple_preference_context)
    if conflict: ev.append(primitive("RELATION","CONFLICT_EXISTS","evidence",ev_text))
    correction=bool(CORRECTION.search(ev_text) and not re.search(r"\b(?:no|without)\b[^.\n]{0,50}\b(?:correction|retraction)\b",ev_text,re.I))
    if correction: ev.append(primitive("RELATION","CORRECTION","evidence",ev_text))
    supersession=bool(evfacts.get("supersession_supported") is True or SUPERSESSION.search(ev_text))
    if conflict and re.search(r"\b(?:no|without)\b[^.\n]{0,80}\b(?:supersession|correction|retraction)\b",ev_text,re.I): supersession=False
    if supersession: ev.append(primitive("RELATION","EXPLICIT_SUPERSESSION","evidence",ev_text))
    if CONTEXT_SPLIT.search(ev_text): ev.append(primitive("RELATION","CONTEXT_SPLIT","evidence",ev_text,context_distinction=True))
    ev += extract_quantifiers(ev_text,"evidence")
    ev += extract_temporal(ev_text,"evidence")
    ev += _fallback(ev_text,"evidence")
    ev.append(_scope_primitive(ev_text,"evidence"))

    preserves=bool(PRESERVE.search(policy) or ((ABSTAIN.search(policy) or CLARIFY.search(policy)) and conflict))
    if preserves: ts.append(primitive("UNCERTAINTY","PRESERVES_CONFLICT","teaching_signal",policy))
    for s in sentences(main_policy):
        explicit_subject=bool(re.search(r"\b(?:instruction|preference|message|statement|guidance|request)s?\b",s,re.I))
        structural_order=bool(re.search(r"\b[\w-]+\s+(?:follows|came\s+after|came\s+afterward)\s+[\w-]+\b|\bbecause\s+[\w-]+\s+came\s+afterward\b",s,re.I))
        has_recency=bool(RECENCY.search(s) and (explicit_subject or structural_order))
        if has_recency: ts.append(primitive("TEMPORAL","RECENCY_RELATION","teaching_signal",s))
        if conflict and has_recency and SELECT.search(s) and not preserves and not ABSTAIN.search(policy):
            ts.append(primitive("RELATION","IMPLICIT_SELECTION","teaching_signal",s,basis="RECENCY"))
        negated_supersession=bool(re.search(r"\b(?:no|without|not|never)\b[^.\n]{0,90}\b(?:supersed|replace|retract|revoke)",s,re.I))
        if SUPERSESSION.search(s) and not negated_supersession: ts.append(primitive("RELATION","EXPLICIT_SUPERSESSION","teaching_signal",s))
        if CORRECTION.search(s) and not re.search(r"\b(?:no|without)\b[^.\n]{0,50}\b(?:correction|retraction)\b",s,re.I): ts.append(primitive("RELATION","CORRECTION","teaching_signal",s))
        if re.search(r"\b(?:except|exception|unless|other than)\b",s,re.I): ts.append(primitive("RELATION","EXCEPTS","teaching_signal",s))
    ts += extract_quantifiers(main_policy,"teaching_signal")
    ts += extract_temporal(main_policy,"teaching_signal")
    if revision:
        ts += extract_quantifiers(revision,"teaching_signal",True)
        ts += [p for p in extract_temporal(revision,"teaching_signal",True) if p["type"]!="RECENCY_RELATION"]
    ts += _fallback(policy,"teaching_signal")
    if ABSTAIN.search(policy): ts.append(primitive("UNCERTAINTY","ABSTAINS","teaching_signal",policy))
    if CLARIFY.search(policy): ts.append(primitive("UNCERTAINTY","REQUESTS_CLARIFICATION","teaching_signal",policy))
    if LOW_CONF.search(policy): ts.append(primitive("UNCERTAINTY","LOW_CONFIDENCE","teaching_signal",policy))
    for m in OP_SIGNAL.finditer(policy): ts.append(primitive("CLAIM","OPERATIONAL_SIGNAL","teaching_signal",m.group(0),operational_signal=m.group(0).lower()))
    ts.append(_teaching_scope(signal_obj,ts_text))
    return {"evidence_text":ev_text,"teaching_signal_text":ts_text,"evidence_primitives":_dedupe(ev),"teaching_signal_primitives":_dedupe(ts)}


def _dedupe(items):
    seen=set(); out=[]
    for p in items:
        key=(p["family"],p["type"],p["source"],p["surface"].lower())
        if key not in seen: seen.add(key); out.append(p)
    return out
