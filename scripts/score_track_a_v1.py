#!/usr/bin/env python3
import argparse, json
from collections import defaultdict

def read_jsonl(path):
    with open(path, encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]
def f1_sets(a,b):
    a,b=set(a),set(b)
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    tp=len(a&b); p=tp/len(b); r=tp/len(a)
    return 0.0 if p+r==0 else 2*p*r/(p+r)
def exact(expected,pred,key): return float(pred.get(key)==expected.get(key))
def slots(expected,pred):
    e=expected.get("arguments",{}); p=pred.get("arguments",{}); keys=set(e)|set(p)
    if not keys: return 1.0
    tp=sum(1 for k in keys if k in e and k in p and e[k]==p[k]); fp=sum(1 for k in keys if k in p and (k not in e or e.get(k)!=p.get(k))); fn=sum(1 for k in keys if k in e and (k not in p or e.get(k)!=p.get(k))); den=2*tp+fp+fn
    return 1.0 if den==0 else 2*tp/den
def score_case(case,pred):
    fam=case["family"]; e=case["expected"]; out={}
    if fam=="A1": out["primary"]=exact(e,pred,"intent_label")
    elif fam=="A2": out.update(primary=f1_sets(e.get("resolved_entity_ids",[]),pred.get("resolved_entity_ids",[])),resolved_value_accuracy=f1_sets(e.get("resolved_values",[]),pred.get("resolved_values",[])),clarification_accuracy=float(pred.get("clarification_required")==e.get("clarification_required")))
    elif fam=="A3": out["primary"]=float(pred.get("normalized")==e.get("normalized"))
    elif fam=="A4":
        out["primary"]=exact(e,pred,"action_id")
        if "unavailable_tool" in case["adversarial_tags"]:
            available={x["id"] for x in case["input"].get("available_actions",[])}; sel=pred.get("action_id"); out["unavailable_false_selection"]=float(sel not in {None,"NONE","CLARIFY"} and sel not in available)
    elif fam=="A5": out["primary"]=slots(e,pred); out["exact_record_match"]=float(pred.get("arguments")==e.get("arguments"))
    elif fam=="A6":
        truth=e.get("clarification_required"); guess=pred.get("clarification_required"); out["primary"]=float(guess==truth); out["under_clarification"]=float(truth is True and guess is not True); out["over_clarification"]=float(truth is False and guess is True)
    elif fam=="A7":
        out["primary"]=exact(e,pred,"route"); truth=e.get("route"); guess=pred.get("route"); out["false_local"]=float(truth=="EXTERNAL" and guess in {"LOCAL_MODEL","LOCAL_APP_OR_TOOL"}); out["unnecessary_external"]=float(truth in {"LOCAL_MODEL","LOCAL_APP_OR_TOOL"} and guess=="EXTERNAL")
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cases",required=True); ap.add_argument("--predictions",required=True); args=ap.parse_args()
    cases=read_jsonl(args.cases); preds={r["case_id"]:r.get("prediction",r) for r in read_jsonl(args.predictions)}; fam_scores=defaultdict(list); secondary=defaultdict(lambda:defaultdict(list)); by_case={}; missing=[]
    for c in cases:
        p=preds.get(c["case_id"],{}); missing += [] if c["case_id"] in preds else [c["case_id"]]; s=score_case(c,p); by_case[c["case_id"]]=s; fam_scores[c["family"]].append(s.get("primary",0.0))
        for k,v in s.items():
            if k!="primary": secondary[c["family"]][k].append(v)
    result={"cases":len(cases),"missing_predictions":len(missing),"families":{}}; prim=[]
    for fam in sorted(fam_scores):
        primary=sum(fam_scores[fam])/len(fam_scores[fam]); prim.append(primary); result["families"][fam]={"primary":primary}
        for k,vals in secondary[fam].items(): result["families"][fam][k]=sum(vals)/len(vals) if vals else None
    result["macro_family_primary"]=sum(prim)/len(prim); groups=defaultdict(list)
    for c in cases:
        if c.get("counterfactual_group_id"): groups[c["counterfactual_group_id"]].append(c)
    good=sum(1 for cs in groups.values() if all(by_case[c["case_id"]].get("primary",0.0)==1.0 for c in cs)); result["counterfactual_consistency"]=good/len(groups) if groups else None
    f=result["families"]; macro=result["macro_family_primary"]; unavailable=f.get("A4",{}).get("unavailable_false_selection",0.0); under=f.get("A6",{}).get("under_clarification",0.0); false_local=f.get("A7",{}).get("false_local",0.0)
    result["RVE_PASS"]=macro>=.80 and all(v["primary"]>=.70 for v in f.values()) and under<=.08 and false_local<=.05 and unavailable<=.05
    result["TUE_PASS"]=macro>=.90 and all(v["primary"]>=.85 for v in f.values()) and f.get("A2",{}).get("resolved_value_accuracy",0)>=.90 and f.get("A5",{}).get("exact_record_match",0)>=.85 and under<=.03 and false_local<=.02 and unavailable<=.02 and (result["counterfactual_consistency"] or 0)>=.90
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
