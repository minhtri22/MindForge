"""Evaluate canonical fact extraction separately from V3 policy."""
from __future__ import annotations
import json
from pathlib import Path
from fact_extractor import extract_semantic_facts
from support_relations import compute_support_relations

ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit17"

def main():
    gold=json.loads((EXP/"fact-goldset.json").read_text(encoding="utf-8"))["samples"]
    pit15=[json.loads(x) for x in (ROOT/"experiments/pit15/control/control-results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    p15={f"pit15:{r['candidate_id']}:{r['scenario_id']}":r for r in pit15}
    corpus=json.loads((ROOT/"experiments/pit16/corpus.json").read_text(encoding="utf-8"))["fixtures"]
    p16={f"pit16dev:{r['fixture_id']}":r for r in corpus}
    keys=("resolves_conflict","asserts_numeric_threshold","asserts_temporal_rule","asserts_fallback_policy","asserts_globalization","abstains")
    tp=fp=fn=0; rows=[]
    feature_stats={k:{"tp":0,"fp":0,"fn":0,"tn":0} for k in keys}
    for g in gold:
        src=p15.get(g["gold_id"]) or p16[g["gold_id"]]
        sig=src["teaching_signal"]
        evidence = ({"evidence": []} if g["source"]=="PIT15_HISTORICAL" else src["evidence"])
        if g["source"]=="PIT15_HISTORICAL":
            scenarios=json.loads((ROOT/"experiments/pit13/evidence/scenarios.json").read_text(encoding="utf-8"))["scenarios"]
            evidence=next(x for x in scenarios if x["scenario_id"]==src["scenario_id"])
        facts=extract_semantic_facts(evidence,sig); facts["support_relations"]=compute_support_relations(facts); got=facts["teaching_signal_state"]
        pred={k:bool(got[k]) for k in keys}
        expected={k:bool(g["expected"][k]) for k in keys}
        expected["has_operational_signal"]=bool(g["expected"]["has_operational_signal"])
        pred["has_operational_signal"]=bool(got["operational_signals"])
        for k in list(keys)+["has_operational_signal"]:
            e=expected[k]; p=pred[k]
            if e and p: tp+=1; feature_stats.setdefault(k,{"tp":0,"fp":0,"fn":0,"tn":0})["tp"]+=1
            elif not e and p: fp+=1; feature_stats.setdefault(k,{"tp":0,"fp":0,"fn":0,"tn":0})["fp"]+=1
            elif e and not p: fn+=1; feature_stats.setdefault(k,{"tp":0,"fp":0,"fn":0,"tn":0})["fn"]+=1
            else: feature_stats.setdefault(k,{"tp":0,"fp":0,"fn":0,"tn":0})["tn"]+=1
        rows.append({"gold_id":g["gold_id"],"expected":expected,"predicted":pred})
    rate=lambda n,d: round(n/d,6) if d else 1.0
    def acc(field, getter):
        pairs=[]
        for g,r in zip(gold,rows):
            if g["expected"].get(field) is not None: pairs.append((bool(g["expected"][field]), bool(getter(r))))
        return rate(sum(a==b for a,b in pairs),len(pairs))
    # Re-extract for evidence/support metrics to keep runtime output separate from gold labels.
    aux=[]
    for g in gold:
        src=p15.get(g["gold_id"]) or p16[g["gold_id"]]; sig=src["teaching_signal"]
        if g["source"]=="PIT15_HISTORICAL":
            scenarios=json.loads((ROOT/"experiments/pit13/evidence/scenarios.json").read_text(encoding="utf-8"))["scenarios"]
            evidence=next(x for x in scenarios if x["scenario_id"]==src["scenario_id"])
        else: evidence=src["evidence"]
        f=extract_semantic_facts(evidence,sig); f["support_relations"]=compute_support_relations(f); aux.append(f)
    def field_acc(gold_field, path):
        pairs=[]
        for g,f in zip(gold,aux):
            if g["expected"].get(gold_field) is None: continue
            val=f[path[0]][path[1]]; pairs.append((bool(g["expected"][gold_field]),bool(val)))
        return rate(sum(a==b for a,b in pairs),len(pairs))
    metrics={"gold_samples":len(gold),"fact_precision":rate(tp,tp+fp),"fact_recall":rate(tp,tp+fn),"conflict_state_accuracy":field_acc("evidence_has_conflict",("evidence_state","has_conflict")),"supersession_support_accuracy":field_acc("supersession_supported",("support_relations","supersession_supported")),"numeric_policy_extraction_recall":rate(feature_stats["asserts_numeric_threshold"]["tp"],feature_stats["asserts_numeric_threshold"]["tp"]+feature_stats["asserts_numeric_threshold"]["fn"]),"temporal_policy_extraction_recall":rate(feature_stats["asserts_temporal_rule"]["tp"],feature_stats["asserts_temporal_rule"]["tp"]+feature_stats["asserts_temporal_rule"]["fn"]),"fallback_extraction_recall":rate(feature_stats["asserts_fallback_policy"]["tp"],feature_stats["asserts_fallback_policy"]["tp"]+feature_stats["asserts_fallback_policy"]["fn"]),"scope_support_accuracy":field_acc("scope_supported",("support_relations","scope_supported")),"abstention_clarification_accuracy":rate(feature_stats["abstains"]["tp"]+feature_stats["abstains"]["tn"],sum(feature_stats["abstains"].values())),"feature_stats":feature_stats}
    (EXP/"fact-extraction-results.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows),encoding="utf-8")
    (EXP/"fact-metrics.json").write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(metrics,indent=2))
if __name__=="__main__": main()
