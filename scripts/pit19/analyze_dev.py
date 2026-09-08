"""Report known-development mismatches without touching held-out data."""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from evaluate_dev import labels, canonical

rows=[json.loads(x) for x in (ROOT/"experiments/pit19/dev-results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
bad=[]
for r in rows:
    e=r["expected"]; pl=labels(r["result"]); gl=set(e.get("primitive_labels",[])); pc=canonical(r["result"]); diff=[]
    if pl != gl: diff.append({"primitive_missing":sorted(gl-pl),"primitive_extra":sorted(pl-gl)})
    for k,v in e.get("canonical",{}).items():
        if bool(pc[k]) != bool(v): diff.append({k:{"expected":bool(v),"actual":bool(pc[k])}})
    evscope=r["result"]["facts"]["evidence_state"]["scope_level"]; tsscope=r["result"]["facts"]["teaching_signal_state"]["asserted_scope"]
    if e.get("evidence_scope") is not None and evscope != e["evidence_scope"]: diff.append({"evidence_scope":{"expected":e["evidence_scope"],"actual":evscope}})
    if e.get("asserted_scope") is not None and tsscope != e["asserted_scope"]: diff.append({"asserted_scope":{"expected":e["asserted_scope"],"actual":tsscope}})
    if "scope_relation" in e and r["result"]["facts"]["support_relations"]["scope_relation"] != e["scope_relation"]: diff.append({"scope_relation":{"expected":e["scope_relation"],"actual":r["result"]["facts"]["support_relations"]["scope_relation"]}})
    for k,v in e.get("support",{}).items():
        actual=r["result"]["facts"]["support_relations"].get(k)
        if actual != v: diff.append({f"support.{k}":{"expected":v,"actual":actual}})
    if diff:
        src=next(s for s in json.loads((ROOT/"experiments/pit19/dev-corpus.json").read_text(encoding="utf-8"))["samples"] if s["gold_id"]==r["gold_id"])
        bad.append({"gold_id":r["gold_id"],"evidence":src["evidence"],"teaching_signal":src["teaching_signal"],"diff":diff})
print(json.dumps({"mismatch_count":len(bad),"mismatches":bad},indent=2))
