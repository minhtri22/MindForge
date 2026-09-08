"""Semantic scope lattice for PIT-19 Representation V3."""
from __future__ import annotations
import re

SCOPE_LEVELS = {"OBSERVATION":0,"TURN":1,"SESSION":2,"TASK":3,"WORKFLOW":4,"DOMAIN":5,"GLOBAL":6}

GLOBAL = re.compile(r"\b(?:universally|globally|everywhere)\b|\b(?:all|every|any)\s+(?:future\s+)?(?:\w+\s+){0,2}(?:task|workflow|project|run|rerun|interaction|case|domain|work)s?\b|\bacross\s+(?:all|every)\b|\bfor\s+all\s+future\b|\buniversal\s+default\b|\bglobal\s+default\b|\b(?:tasks?|cases?|workflows?)\s+(?:lacking|without|outside)\b[^.\n]{0,100}\bdefault\b", re.I)
DOMAIN = re.compile(r"\b(?:tasks? like this|similar\s+(?:planning\s+)?tasks?|planning\s+tasks(?:\s+share)?|planning\s+and\s+roadmap\s+tasks|roadmap\s+(?:planning|tasks)|for\s+planning\s+tasks|code\s+reviews?|experimental\s+workflows?|benchmark\s+workflows?|this\s+domain|within\s+this\s+domain|across\s+the\s+domain|class\s+of\s+tasks)\b", re.I)
WORKFLOW = re.compile(r"\b(?:this|current|the|one)\s+(?:workflow|pipeline|process)\b|\b(?:within|restricted to|limited to)\s+(?:this|one)\s+(?:workflow|pipeline|process)\b", re.I)
TASK = re.compile(r"\b(?:this|current|specific|single|one-off)\s+(?:task|experiment|plan|case)\b|\bfor\s+this\s+(?:task|experiment|plan|case)\b", re.I)
SESSION = re.compile(r"\b(?:this|current)\s+(?:session|conversation|chat)\b|\bfor\s+this\s+(?:session|conversation|chat)\b", re.I)
TURN = re.compile(r"\b(?:this|current)\s+turn\b|\bfor\s+this\s+turn\b", re.I)
OBS = re.compile(r"\b(?:this|that|single|one)\s+(?:observation|message|statement|event|interaction|fixture)\b|\b(?:fixture|evidence)\s+boundary\b|\bthis\s+review\b", re.I)
CONTEXTUAL = re.compile(r"\b(?:depending on context|context dependent|context-dependent|where applicable|in the relevant context|for that context)\b", re.I)
NEG_GLOBAL = re.compile(r"\b(?:not|never|do not|does not|don't|doesn't)\b[^.\n]{0,70}\b(?:global|univers|all future|everywhere|always|by default)\b", re.I)


def classify_scope(text: str, allow_contextual: bool = True) -> dict:
    text=str(text or "").strip()
    scrub=NEG_GLOBAL.sub("", text)
    strong_global=bool(re.search(r"\b(?:universally|globally|everywhere|all\s+future|any\s+future|every\s+future|across\s+all|every\s+project|all\s+domains|universal\s+default|global\s+default)\b",scrub,re.I))
    if re.search(r"\b(?:this|that)\s+observation\b[^.\n]{0,60}\b(?:task|workflow|domain|project)\b",scrub,re.I): level="OBSERVATION"
    elif strong_global: level="GLOBAL"
    elif DOMAIN.search(scrub): level="DOMAIN"
    elif GLOBAL.search(scrub): level="GLOBAL"
    elif WORKFLOW.search(scrub): level="WORKFLOW"
    elif TASK.search(scrub): level="TASK"
    elif SESSION.search(scrub): level="SESSION"
    elif TURN.search(scrub): level="TURN"
    elif allow_contextual and CONTEXTUAL.search(scrub): level="CONTEXTUAL"
    else: level="OBSERVATION"
    target = None
    if level != "OBSERVATION":
        target = level.lower()
    constraints=[]
    if re.search(r"\b(?:only|limited to|specific to|within)\b", scrub, re.I): constraints.append("EXPLICIT_LIMIT")
    return {"scope_level":level,"scope_target":target,"scope_constraints":constraints,"scope_provenance":text}


def relation(asserted: str, evidence: str) -> str:
    if asserted == "CONTEXTUAL" or evidence == "CONTEXTUAL": return "CONTEXTUAL"
    a=SCOPE_LEVELS.get(asserted,0); e=SCOPE_LEVELS.get(evidence,0)
    return "NARROWER" if a<e else ("EQUAL" if a==e else "BROADER")


def supported(asserted: str, evidence: str) -> bool:
    if asserted == "CONTEXTUAL": return True
    if evidence == "CONTEXTUAL": return asserted in {"OBSERVATION","TURN","SESSION","CONTEXTUAL"}
    return SCOPE_LEVELS.get(asserted,0) <= SCOPE_LEVELS.get(evidence,0)
