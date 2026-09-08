"""Report PIT-19 historical regression mismatches using only known corpora."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def rows(name): return [json.loads(x) for x in (ROOT/"experiments/pit19"/name).read_text(encoding="utf-8").splitlines() if x.strip()]

out={}
for name in ("pit15-regression.jsonl","pit16-full-regression.jsonl"):
    bad=[]
    for r in rows(name):
        exp=set(r["expected"]); act=set(r["decision"]["violation_classes"])
        if exp != act:
            bad.append({
                "id":r.get("scenario_id") or r.get("fixture_id"),
                "candidate_id":r.get("candidate_id"),
                "expected":sorted(exp),"actual":sorted(act),
                "evidence_text":r["primitives"]["evidence_text"],
                "teaching_signal_text":r["primitives"]["teaching_signal_text"],
                "evidence_primitives":[p["type"] for p in r["primitives"]["evidence_primitives"]],
                "teaching_primitives":[p["type"] for p in r["primitives"]["teaching_signal_primitives"]],
                "evidence_scope":r["facts"]["evidence_state"]["scope_level"],
                "asserted_scope":r["facts"]["teaching_signal_state"]["asserted_scope"],
            })
    out[name]=bad
print(json.dumps(out,indent=2))
