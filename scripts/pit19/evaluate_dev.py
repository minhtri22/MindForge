"""Build PIT-19 known DEV provenance and evaluate Representation V3."""
from __future__ import annotations
import json, sys
from pathlib import Path
from itertools import combinations

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; EXP=ROOT/"experiments/pit19"
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from representation_v3 import evaluate

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def rate(n,d): return round(n/d,6) if d else 1.0

def labels(result):
    ev=result["primitives"]["evidence_primitives"]; ts=result["primitives"]["teaching_signal_primitives"]; f=result["facts"]
    out=set()
    if any(p["type"]=="CONFLICT_EXISTS" for p in ev): out.add("EV:CONTRADICTS")
    if any(p["type"]=="RECENCY_RELATION" for p in ts): out.add("TS:RECENCY_ORDER")
    if any(p["type"]=="IMPLICIT_SELECTION" for p in ts): out.add("TS:RESOLVES_BY_RECENCY")
    if f["teaching_signal_state"]["asserts_numeric_threshold"]: out.add("TS:COUNT_THRESHOLD")
    if f["teaching_signal_state"]["asserts_temporal_rule"]: out.add("TS:TEMPORAL_POLICY")
    if f["teaching_signal_state"]["asserts_fallback_policy"]: out.add("TS:FALLBACK")
    if any(p["type"]=="ABSTAINS" for p in ts): out.add("TS:ABSTAINS")
    if any(p["type"]=="REQUESTS_CLARIFICATION" for p in ts): out.add("TS:REQUESTS_CLARIFICATION")
    if f["teaching_signal_state"]["operational_signals"]: out.add("TS:OPERATIONAL_SIGNAL")
    return out

def canonical(r):
    ev=r["facts"]["evidence_state"]; ts=r["facts"]["teaching_signal_state"]
    return {"evidence_has_conflict":bool(ev["has_conflict"]),"resolves_conflict":bool(ts["resolves_conflict"]),"asserts_numeric_threshold":bool(ts["asserts_numeric_threshold"]),"asserts_temporal_rule":bool(ts["asserts_temporal_rule"]),"asserts_fallback_policy":bool(ts["asserts_fallback_policy"]),"abstains":bool(ts["abstains"]),"requests_clarification":bool(ts["requests_clarification"]),"has_operational_signal":bool(ts["operational_signals"])}

def build_dev():
    samples=[]
    for name in ("representation-gold-dev.json","representation-gold-heldout.json"):
        for s in load(ROOT/"experiments/pit18"/name)["samples"]:
            c=json.loads(json.dumps(s))
            c["pit19_provenance"]={"source_artifact":f"experiments/pit18/{name}","status":"KNOWN_DEV","pit18_gold_id":s["gold_id"]}
            # PIT-18 documented these four frozen annotations as inconsistent with their explicit conflict surfaces.
            if s["gold_id"] in {"heldout-extra-02","heldout-extra-07","heldout-extra-12","heldout-extra-17"}:
                pls=c["expected"].setdefault("primitive_labels",[])
                if "EV:CONTRADICTS" not in pls: pls.append("EV:CONTRADICTS")
                c["expected"].setdefault("canonical",{})["evidence_has_conflict"]=True
                c["pit19_provenance"]["annotation_revision"]="PIT18_DOCUMENTED_GOLD_LIMITATION_CORRECTED_FOR_KNOWN_DEV_ONLY"
            samples.append(c)
    return samples

def score(rows,clusters):
    p_tp=p_fp=p_fn=c_tp=c_fp=c_fn=scope_ok=scope_n=rel_ok=rel_n=sup_ok=sup_n=0
    spec={"numeric":[0,0],"temporal":[0,0],"fallback":[0,0],"conflict":[0,0]}
    for row in rows:
        e=row["expected"]; pl=labels(row["result"]); gl=set(e.get("primitive_labels",[]))
        p_tp+=len(pl&gl); p_fp+=len(pl-gl); p_fn+=len(gl-pl)
        pc=canonical(row["result"])
        for k,g in e.get("canonical",{}).items():
            p=bool(pc[k]); c_tp+=int(g and p); c_fp+=int((not g) and p); c_fn+=int(g and not p)
        for key,path in (("evidence_scope",("evidence_state","scope_level")),("asserted_scope",("teaching_signal_state","asserted_scope"))):
            if e.get(key) is not None:
                scope_n+=1; scope_ok+=row["result"]["facts"][path[0]][path[1]]==e[key]
        if "scope_relation" in e:
            rel_n+=1; rel_ok+=row["result"]["facts"]["support_relations"]["scope_relation"]==e["scope_relation"]
        for k,g in e.get("support",{}).items():
            sup_n+=1; sup_ok+=row["result"]["facts"]["support_relations"].get(k)==g
        for lab,key in (("numeric","asserts_numeric_threshold"),("temporal","asserts_temporal_rule"),("fallback","asserts_fallback_policy"),("conflict","resolves_conflict")):
            if e.get("canonical",{}).get(key): spec[lab][1]+=1; spec[lab][0]+=int(pc[key])
    by={r["gold_id"]:r for r in rows}; cons=0; n=0
    for c in clusters:
        ids=[x for x in c["sample_ids"] if x in by]
        if len(ids)<2: continue
        n+=1
        fps=[]
        for i in ids:
            r=by[i]["result"]; fps.append((tuple(sorted(labels(r))),tuple(sorted(canonical(r).items())),r["facts"]["evidence_state"]["scope_level"],r["facts"]["teaching_signal_state"]["asserted_scope"],r["facts"]["support_relations"]["scope_relation"]))
        cons+=len(set(fps))==1
    return {"samples":len(rows),"primitive_precision":rate(p_tp,p_tp+p_fp),"primitive_recall":rate(p_tp,p_tp+p_fn),"canonical_fact_precision":rate(c_tp,c_tp+c_fp),"canonical_fact_recall":rate(c_tp,c_tp+c_fn),"scope_classification_accuracy":rate(scope_ok,scope_n),"scope_relation_accuracy":rate(rel_ok,rel_n),"support_relation_accuracy":rate(sup_ok,sup_n),"cluster_consistency":rate(cons,n),"numeric_recall":rate(*spec["numeric"]),"temporal_recall":rate(*spec["temporal"]),"fallback_recall":rate(*spec["fallback"]),"conflict_resolution_recall":rate(*spec["conflict"])}

def main():
    EXP.mkdir(parents=True,exist_ok=True); samples=build_dev(); (EXP/"dev-corpus.json").write_text(json.dumps({"status":"KNOWN_DEVELOPMENT_EVIDENCE","samples":samples},ensure_ascii=False,indent=2),encoding="utf-8")
    rows=[]
    for s in samples: rows.append({"gold_id":s["gold_id"],"expected":s["expected"],"result":evaluate(s["evidence"],s["teaching_signal"])})
    (EXP/"dev-results.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")
    clusters=load(ROOT/"experiments/pit18/representation-clusters.json")["clusters"]
    metrics=score(rows,clusters); (EXP/"dev-metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8"); print(json.dumps(metrics,indent=2))

if __name__=="__main__": main()
