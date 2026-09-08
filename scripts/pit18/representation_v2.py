"""Public Representation V2 pipeline for PIT-18."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PIT17 = HERE.parent / "pit17"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PIT17) not in sys.path:
    sys.path.insert(0, str(PIT17))

from canonicalizer import canonicalize
from primitive_extractor import extract_primitives
from support_relations_v2 import compute_support_relations
from guardrail_v3 import evaluate_facts


def represent(evidence: Any, teaching_signal: Any) -> dict[str, Any]:
    primitives = extract_primitives(evidence, teaching_signal)
    facts = canonicalize(primitives, evidence)
    facts["support_relations"] = compute_support_relations(facts)
    return {"primitives": primitives, "facts": facts}


def evaluate(evidence: Any, teaching_signal: Any) -> dict[str, Any]:
    rep = represent(evidence, teaching_signal)
    decision = evaluate_facts(rep["facts"])
    return {**rep, "decision": decision}

