"""Public PIT-19 Representation V3 pipeline."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent; PIT17=HERE.parent/"pit17"
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
if str(PIT17) not in sys.path: sys.path.insert(0,str(PIT17))
from primitive_extractor_v3 import extract_primitives
from canonicalizer_v3 import canonicalize
from support_relations_v3 import compute_support_relations
from guardrail_v3 import evaluate_facts

def represent(evidence:Any,teaching_signal:Any):
    p=extract_primitives(evidence,teaching_signal); f=canonicalize(p,evidence); f["support_relations"]=compute_support_relations(f); return {"primitives":p,"facts":f}
def evaluate(evidence:Any,teaching_signal:Any):
    r=represent(evidence,teaching_signal); return {**r,"decision":evaluate_facts(r["facts"])}
