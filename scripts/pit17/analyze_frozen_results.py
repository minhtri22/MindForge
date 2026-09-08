"""Post-hoc analysis of frozen PIT-17 outputs. Never reruns extraction or V3."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit17"

def load_jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def write_json(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_jsonl(path,rows): path.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows),encoding="utf-8")

def classify(expected, detected, facts):
    missing=set(expected)-set(detected); extra=set(detected)-set(expected); out=[]
    ts=facts["teaching_signal_state"]
    class_to_fact={
        "UNSUPPORTED_CONFLICT_RESOLUTION":"resolves_conflict",
        "UNSUPPORTED_NUMERIC_THRESHOLD":"asserts_numeric_threshold",
        "UNSUPPORTED_TEMPORAL_RULE":"asserts_temporal_rule",
        "UNSUPPORTED_FALLBACK_POLICY":"asserts_fallback_policy",
        "UNSUPPORTED_SCOPE_GENERALIZATION":"asserts_globalization",
        "EVIDENCE_GROUNDING_FAILURE":"operational_signals",
    }
    for c in missing:
        if c=="UNSUPPORTED_SCOPE_GENERALIZATION": out.append("SCOPE_NORMALIZATION_ERROR")
        elif not bool(ts.get(class_to_fact[c])): out.append("FACT_EXTRACTION_FALSE_NEGATIVE")
        else: out.append("SUPPORT_RELATION_ERROR")
    for c in extra:
        if c=="UNSUPPORTED_SCOPE_GENERALIZATION": out.append("SCOPE_NORMALIZATION_ERROR")
        else: out.append("FACT_EXTRACTION_FALSE_POSITIVE")
    return sorted(set(out)) or ["AMBIGUOUS_INPUT"]

def main():
    all_rows=[]; errors=[]; supports=[]
    for source,name in [(EXP/"pit15-regression.jsonl","PIT15"),(EXP/"pit16-heldout-results.jsonl","PIT16_HELD_OUT")]:
        for r in load_jsonl(source):
            ident=r.get("fixture_id") or f"{r.get('candidate_id')}|{r.get('scenario_id')}"
            supports.append({"source":name,"sample_id":ident,"support_relations":r["facts"]["support_relations"]})
            e=r["expected"]; d=r["decision"]["violation_classes"]
            if set(e)!=set(d):
                cats=classify(e,d,r["facts"]); errors.append({"source":name,"sample_id":ident,"expected_classes":e,"detected_classes":d,"error_taxonomy":cats})
    counts=Counter(c for r in errors for c in r["error_taxonomy"])
    for c in ["FACT_EXTRACTION_FALSE_NEGATIVE","FACT_EXTRACTION_FALSE_POSITIVE","SUPPORT_RELATION_ERROR","GUARDRAIL_POLICY_ERROR","SCOPE_NORMALIZATION_ERROR","AMBIGUOUS_INPUT"]: counts.setdefault(c,0)
    write_jsonl(EXP/"support-relation-results.jsonl",supports)
    write_json(EXP/"error-analysis.json",{"errors":errors,"error_distribution":dict(counts)})
    metrics=json.loads((EXP/"metrics.json").read_text(encoding="utf-8")); fact=json.loads((EXP/"fact-metrics.json").read_text(encoding="utf-8"))
    inv_rows=load_jsonl(EXP/"representation-invariance-results.jsonl"); clusters={r["cluster_id"] for r in inv_rows}; consistent=sum(all(x["fact_value"] for x in inv_rows if x["cluster_id"]==c) for c in clusters)
    invariance=round(consistent/len(clusters),6) if clusters else None
    summary={"task":"PIT-17 Semantic Fact Representation Layer / Guardrail Unification","status":"COMPLETED","final_verdict":"REPRESENTATION_LAYER_INSUFFICIENT","fact_precision":fact["fact_precision"],"fact_recall":fact["fact_recall"],"representation_cluster_consistency":invariance,"pit15_regression_pass":False,"pit16_held_out_pass":False,"methodological_interpretation":"Gold/dev representation checks pass, but the frozen representation does not generalize across full historical and held-out regimes. Errors are dominated by extraction and scope normalization, not unified guardrail policy.","api_calls":0,"new_teacher_inference":0,"teacher_selected":False,"training":False,"distillation":False,"mindforge_integration":False,"next_recommended_milestone":"PIT-18 Representation Layer Refinement"}
    write_json(EXP/"summary.json",summary); print(json.dumps({"summary":summary,"error_distribution":dict(counts)},indent=2))
if __name__=="__main__": main()
