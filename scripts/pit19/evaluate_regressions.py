"""PIT-15 and PIT-16 historical regression evaluation for Representation V3."""
from __future__ import annotations
import json,sys,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; EXP=ROOT/"experiments/pit19"
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from representation_v3 import evaluate

CLASSES=("UNSUPPORTED_CONFLICT_RESOLUTION","UNSUPPORTED_NUMERIC_THRESHOLD","UNSUPPORTED_TEMPORAL_RULE","UNSUPPORTED_FALLBACK_POLICY","UNSUPPORTED_SCOPE_GENERALIZATION","EVIDENCE_GROUNDING_FAILURE")
PRE={"conflict-04","conflict-05","conflict-06","conflict-07","conflict-08"}
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def loadl(p): return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
def rate(n,d): return round(n/d,6) if d else 1.0
def write(name,rows): (EXP/name).write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")

def pit15():
    scenarios={r["scenario_id"]:r for r in load(ROOT/"experiments/pit13/evidence/scenarios.json")["scenarios"]}; rows=[]
    for row in loadl(ROOT/"experiments/pit15/control/control-results.jsonl"):
        got=evaluate(scenarios[row["scenario_id"]],row["teaching_signal"]); rows.append({"candidate_id":row["candidate_id"],"scenario_id":row["scenario_id"],"expected":row["known_expected_violations"],**got})
    failures=[r for r in rows if r["expected"]]; valid=[r for r in rows if not r["expected"]]; det=lambda r:r["decision"]["status"]!="ACCEPT"
    conflict=[r for r in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" in r["expected"]]; heur=[r for r in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" not in r["expected"]]
    muse=[r for r in rows if r["candidate_id"]=="meta/muse-glimmer-30b"]; lifecycle_ids={"preference_drift_001","user_correction_001","rare_exception_001","insufficient_evidence_001","long_term_consistency_001"}; life=[r for r in valid if r["scenario_id"] in lifecycle_ids]
    acc=lambda g:sum(r["decision"]["status"]=="ACCEPT" for r in g)
    m={"samples":len(rows),"known_failures_detected":sum(det(r) for r in failures),"known_failures_total":len(failures),"conflict_detection":rate(sum(det(r) for r in conflict),len(conflict)),"unsupported_heuristic_detection":rate(sum(det(r) for r in heur),len(heur)),"muse_preservation":rate(acc(muse),len(muse)),"lifecycle_preservation":rate(acc(life),len(life)),"false_positive_rate":rate(sum(det(r) for r in valid),len(valid))}
    write("pit15-regression.jsonl",rows); return m

def pit16_rows():
    split=load(ROOT/"experiments/pit16/split.json"); ids=set(split["held_out"]); rows=[]
    for f in load(ROOT/"experiments/pit16/corpus.json")["fixtures"]:
        if f["fixture_id"] in ids:
            got=evaluate(f["evidence"],f["teaching_signal"]); rows.append({"fixture_id":f["fixture_id"],"family":f["family"],"expected":f["expected_violation_classes"],"expected_status":f["expected_status"],**got})
    return rows
def score16(rows):
    unsafe=[r for r in rows if r["expected"]]; valid=[r for r in rows if not r["expected"]]; det=lambda r:r["decision"]["status"]!="ACCEPT"; tp=sum(det(r) for r in unsafe); fp=sum(det(r) for r in valid)
    ect=sum(len(r["expected"]) for r in rows); ctp=sum(len(set(r["expected"])&set(r["decision"]["violation_classes"])) for r in rows); pct=sum(len(r["decision"]["violation_classes"]) for r in rows)
    per={}
    for c in CLASSES:
        rel=[r for r in rows if c in r["expected"]]; per[c]=rate(sum(c in r["decision"]["violation_classes"] for r in rel),len(rel)) if rel else None
    comp=[r for r in rows if len(r["expected"])>1]
    return {"samples":len(rows),"unsafe_sample_recall":rate(tp,len(unsafe)),"unsafe_sample_precision":rate(tp,tp+fp),"violation_class_recall":rate(ctp,ect),"violation_class_precision":rate(ctp,pct),"hard_negative_fpr":rate(fp,len(valid)),"conflict_recall":per[CLASSES[0]],"numeric_threshold_recall":per[CLASSES[1]],"temporal_rule_recall":per[CLASSES[2]],"fallback_recall":per[CLASSES[3]],"scope_generalization_recall":per[CLASSES[4]],"compound_full_class_recall":rate(sum(set(r["expected"]).issubset(set(r["decision"]["violation_classes"])) for r in comp),len(comp))}

def main():
    EXP.mkdir(parents=True,exist_ok=True); m15=pit15(); rows=pit16_rows(); pristine=[r for r in rows if r["fixture_id"] not in PRE]; write("pit16-full-regression.jsonl",rows); write("pit16-pristine-regression.jsonl",pristine)
    out={"pit15":m15,"pit16_full":score16(rows),"pit16_pristine":score16(pristine)}; (EXP/"regression-metrics.json").write_text(json.dumps(out,indent=2),encoding="utf-8"); print(json.dumps(out,indent=2))
if __name__=="__main__": main()
