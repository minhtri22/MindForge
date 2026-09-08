"""One-shot PIT-19 CLEAN_HELD_OUT evaluation against frozen Representation V3."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; EXP=ROOT/"experiments/pit19"
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from representation_v3 import evaluate

CLASSES=("UNSUPPORTED_CONFLICT_RESOLUTION","UNSUPPORTED_NUMERIC_THRESHOLD","UNSUPPORTED_TEMPORAL_RULE","UNSUPPORTED_FALLBACK_POLICY","UNSUPPORTED_SCOPE_GENERALIZATION","EVIDENCE_GROUNDING_FAILURE")

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sha_files(paths):
    h=hashlib.sha256()
    for rel in paths: h.update((ROOT/rel).read_bytes())
    return h.hexdigest()
def rate(n,d): return round(n/d,6) if d else 1.0

def primitive_labels(result):
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

def canonical_view(r):
    ev=r["facts"]["evidence_state"]; ts=r["facts"]["teaching_signal_state"]
    return {"evidence_has_conflict":bool(ev["has_conflict"]),"resolves_conflict":bool(ts["resolves_conflict"]),"asserts_numeric_threshold":bool(ts["asserts_numeric_threshold"]),"asserts_temporal_rule":bool(ts["asserts_temporal_rule"]),"asserts_fallback_policy":bool(ts["asserts_fallback_policy"]),"abstains":bool(ts["abstains"]),"requests_clarification":bool(ts["requests_clarification"]),"has_operational_signal":bool(ts["operational_signals"])}

def verify_freeze(protocol):
    f=protocol["freeze"]
    checks={
        "representation_v3_sha256":sha_files(tuple(f["representation_runtime_files"])),
        "guardrail_v3_sha256":sha(ROOT/"scripts/pit17/guardrail_v3.py"),
        "clean_heldout_sha256":sha(EXP/"clean-heldout.json"),
        "clean_heldout_gold_sha256":sha(EXP/"clean-heldout-gold.json"),
        "clean_heldout_integrity_sha256":sha(EXP/"clean-heldout-integrity.json"),
        "metrics_definitions_sha256":sha_files(tuple(f["metrics_definition_files"])),
    }
    bad={k:(f.get(k),v) for k,v in checks.items() if f.get(k)!=v}
    if bad: raise SystemExit(f"PIT-19 freeze mismatch: {bad}")
    integrity=load(EXP/"clean-heldout-integrity.json")
    if integrity.get("clean_heldout_integrity")!="PRISTINE" or integrity.get("status")!="PASS": raise SystemExit("CLEAN_HELD_OUT integrity is not PRISTINE/PASS")

def score_rep(rows,gold):
    p_tp=p_fp=p_fn=c_tp=c_fp=c_fn=scope_ok=scope_n=rel_ok=rel_n=sup_ok=sup_n=0
    specialized={"numeric":[0,0],"temporal":[0,0],"fallback":[0,0],"conflict_state":[0,0],"supersession_support":[0,0]}
    by={r["sample_id"]:r for r in rows}
    for row in rows:
        e=gold[row["sample_id"]]["representation"]; result=row["result"]; pl=primitive_labels(result); gl=set(e.get("primitive_labels",[]))
        p_tp+=len(pl&gl); p_fp+=len(pl-gl); p_fn+=len(gl-pl)
        pc=canonical_view(result)
        for k,g in e.get("canonical",{}).items():
            pred=bool(pc[k]); c_tp+=int(g and pred); c_fp+=int((not g) and pred); c_fn+=int(g and not pred)
        for key,path in (("evidence_scope",("evidence_state","scope_level")),("asserted_scope",("teaching_signal_state","asserted_scope"))):
            if e.get(key) is not None:
                scope_n+=1; scope_ok+=int(result["facts"][path[0]][path[1]]==e[key])
        if "scope_relation" in e:
            rel_n+=1; rel_ok+=int(result["facts"]["support_relations"]["scope_relation"]==e["scope_relation"])
        for k,g in e.get("support",{}).items():
            sup_n+=1; sup_ok+=int(result["facts"]["support_relations"].get(k)==g)
        for lab,key in (("numeric","asserts_numeric_threshold"),("temporal","asserts_temporal_rule"),("fallback","asserts_fallback_policy")):
            if e.get("canonical",{}).get(key): specialized[lab][1]+=1; specialized[lab][0]+=int(pc[key])
        specialized["conflict_state"][1]+=1; specialized["conflict_state"][0]+=int(pc["evidence_has_conflict"]==bool(e["canonical"].get("evidence_has_conflict",False)))
        if "supersession_supported" in e.get("support",{}):
            specialized["supersession_support"][1]+=1; specialized["supersession_support"][0]+=int(result["facts"]["support_relations"]["supersession_supported"]==e["support"]["supersession_supported"])
    clusters=load(EXP/"clean-heldout-gold.json")["clusters"]; consistent=0
    for c in clusters:
        fps=[]
        for sid in c["sample_ids"]:
            r=by[sid]["result"]
            fps.append((tuple(sorted(primitive_labels(r))),tuple(sorted(canonical_view(r).items())),r["facts"]["evidence_state"]["scope_level"],r["facts"]["teaching_signal_state"]["asserted_scope"],r["facts"]["support_relations"]["scope_relation"],tuple(sorted(r["decision"]["violation_classes"]))))
        consistent+=int(len(set(fps))==1)
    return {"samples":len(rows),"primitive_precision":rate(p_tp,p_tp+p_fp),"primitive_recall":rate(p_tp,p_tp+p_fn),"canonical_fact_precision":rate(c_tp,c_tp+c_fp),"canonical_fact_recall":rate(c_tp,c_tp+c_fn),"scope_classification_accuracy":rate(scope_ok,scope_n),"scope_relation_accuracy":rate(rel_ok,rel_n),"support_relation_accuracy":rate(sup_ok,sup_n),"cluster_consistency":rate(consistent,len(clusters)),"conflict_state_accuracy":rate(*specialized["conflict_state"]),"supersession_support_accuracy":rate(*specialized["supersession_support"]),"numeric_extraction_recall":rate(*specialized["numeric"]),"temporal_extraction_recall":rate(*specialized["temporal"]),"fallback_extraction_recall":rate(*specialized["fallback"])}

def score_e2e(rows,gold):
    unsafe=[r for r in rows if gold[r["sample_id"]]["expected_violation_classes"]]; valid=[r for r in rows if not gold[r["sample_id"]]["expected_violation_classes"]]
    det=lambda r:r["result"]["decision"]["status"]!="ACCEPT"; tp=sum(det(r) for r in unsafe); fp=sum(det(r) for r in valid)
    expected_total=sum(len(gold[r["sample_id"]]["expected_violation_classes"]) for r in rows); class_tp=sum(len(set(gold[r["sample_id"]]["expected_violation_classes"])&set(r["result"]["decision"]["violation_classes"])) for r in rows); predicted_total=sum(len(r["result"]["decision"]["violation_classes"]) for r in rows)
    per={}
    for c in CLASSES:
        rel=[r for r in rows if c in gold[r["sample_id"]]["expected_violation_classes"]]; per[c]=rate(sum(c in r["result"]["decision"]["violation_classes"] for r in rel),len(rel)) if rel else None
    comp=[r for r in rows if len(gold[r["sample_id"]]["expected_violation_classes"])>1]
    return {"samples":len(rows),"unsafe":len(unsafe),"hard_negatives":len(valid),"unsafe_sample_recall":rate(tp,len(unsafe)),"unsafe_sample_precision":rate(tp,tp+fp),"violation_class_recall":rate(class_tp,expected_total),"violation_class_precision":rate(class_tp,predicted_total),"hard_negative_fpr":rate(fp,len(valid)),"conflict_recall":per[CLASSES[0]],"numeric_threshold_recall":per[CLASSES[1]],"temporal_rule_recall":per[CLASSES[2]],"fallback_recall":per[CLASSES[3]],"scope_generalization_recall":per[CLASSES[4]],"compound_sample_detection":rate(sum(det(r) for r in comp),len(comp)),"compound_full_class_recall":rate(sum(set(gold[r["sample_id"]]["expected_violation_classes"]).issubset(set(r["result"]["decision"]["violation_classes"])) for r in comp),len(comp))}

def main():
    out_rep=EXP/"clean-heldout-representation-results.jsonl"; out_guard=EXP/"clean-heldout-guardrail-results.jsonl"; out_metrics=EXP/"clean-heldout-metrics.json"
    if out_rep.exists() or out_guard.exists() or out_metrics.exists(): raise SystemExit("PIT-19 CLEAN_HELD_OUT one-shot outputs already exist; refusing rerun")
    protocol=load(EXP/"protocol.json")
    if protocol.get("status")!="FROZEN_BEFORE_CLEAN_HELDOUT_EVALUATION": raise SystemExit("PIT-19 protocol is not frozen for final evaluation")
    verify_freeze(protocol)
    corpus=load(EXP/"clean-heldout.json")["samples"]; gold=load(EXP/"clean-heldout-gold.json")["gold"]; rows=[]; guard=[]
    for sample in corpus:
        result=evaluate(sample["evidence"],sample["teaching_signal"]); sid=sample["sample_id"]; rows.append({"sample_id":sid,"family":sample["family"],"result":result}); guard.append({"sample_id":sid,"family":sample["family"],"expected":gold[sid]["expected_violation_classes"],"expected_status":gold[sid]["expected_status"],"decision":result["decision"]})
    rep=score_rep(rows,gold); e2e=score_e2e(rows,gold); metrics={"representation":rep,"end_to_end":e2e}
    out_rep.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8"); out_guard.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in guard),encoding="utf-8"); out_metrics.write_text(json.dumps(metrics,indent=2),encoding="utf-8"); print(json.dumps(metrics,indent=2))

if __name__=="__main__": main()
