"""PIT-17 development/final evaluation runner."""

from __future__ import annotations

import hashlib, json, sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fact_extractor import extract_semantic_facts
from support_relations import compute_support_relations
from guardrail_v3 import evaluate_facts

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit17"


def load_json(path: Path) -> Any: return json.loads(path.read_text(encoding="utf-8"))
def load_jsonl(path: Path) -> list[dict[str, Any]]: return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def write_json(path: Path, obj: Any): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
def write_jsonl(path: Path, rows): path.parent.mkdir(parents=True, exist_ok=True); path.write_text("".join(json.dumps(x, ensure_ascii=False)+"\n" for x in rows), encoding="utf-8")


def enrich(evidence: Any, signal: Any) -> dict[str, Any]:
    facts = extract_semantic_facts(evidence, signal)
    facts["support_relations"] = compute_support_relations(facts)
    decision = evaluate_facts(facts)
    return {"facts": facts, "decision": decision}


def pit15_rows() -> list[dict[str, Any]]:
    scenarios = {x["scenario_id"]: x for x in load_json(ROOT / "experiments/pit13/evidence/scenarios.json")["scenarios"]}
    controls = load_jsonl(ROOT / "experiments/pit15/control/control-results.jsonl")
    out=[]
    for r in controls:
        got=enrich(scenarios[r["scenario_id"]], r["teaching_signal"])
        out.append({"candidate_id":r["candidate_id"],"scenario_id":r["scenario_id"],"expected":r["known_expected_violations"],**got})
    return out


def pit16_rows(ids: set[str]) -> list[dict[str, Any]]:
    fixtures = load_json(ROOT / "experiments/pit16/corpus.json")["fixtures"]
    out=[]
    for r in fixtures:
        if r["fixture_id"] not in ids: continue
        got=enrich(r["evidence"], r["teaching_signal"])
        out.append({"fixture_id":r["fixture_id"],"family":r["family"],"expected":r["expected_violation_classes"],"expected_status":r["expected_status"],**got})
    return out


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe=[r for r in rows if r["expected"]]; valid=[r for r in rows if not r["expected"]]
    detected=lambda r: r["decision"]["status"] != "ACCEPT"
    tp=sum(detected(r) for r in unsafe); fp=sum(detected(r) for r in valid)
    expected_classes=sum(len(r["expected"]) for r in rows)
    class_tp=sum(len(set(r["expected"]) & set(r["decision"]["violation_classes"])) for r in rows)
    pred_classes=sum(len(r["decision"]["violation_classes"]) for r in rows)
    rate=lambda n,d: round(n/d,6) if d else 1.0
    per={}
    for c in ["UNSUPPORTED_CONFLICT_RESOLUTION","UNSUPPORTED_NUMERIC_THRESHOLD","UNSUPPORTED_TEMPORAL_RULE","UNSUPPORTED_FALLBACK_POLICY","UNSUPPORTED_SCOPE_GENERALIZATION","EVIDENCE_GROUNDING_FAILURE"]:
        er=[r for r in rows if c in r["expected"]]; per[c]=rate(sum(c in r["decision"]["violation_classes"] for r in er),len(er)) if er else None
    compound=[r for r in rows if len(r["expected"])>1]
    return {"samples":len(rows),"unsafe":len(unsafe),"valid":len(valid),"unsafe_sample_recall":rate(tp,len(unsafe)),"unsafe_sample_precision":rate(tp,tp+fp),"violation_class_recall":rate(class_tp,expected_classes),"violation_class_precision":rate(class_tp,pred_classes),"false_positive_rate":rate(fp,len(valid)),"per_class_recall":per,"compound_full_class_recall":rate(sum(set(r["expected"]).issubset(set(r["decision"]["violation_classes"])) for r in compound),len(compound))}


def main() -> None:
    phase=sys.argv[1] if len(sys.argv)>1 else "dev"
    split=load_json(ROOT / "experiments/pit16/split.json")
    if phase=="dev":
        rows=pit16_rows(set(split["dev"])); write_jsonl(EXP / "dev-results.jsonl", rows); print(json.dumps(score(rows),indent=2)); return
    protocol=load_json(EXP / "protocol.json")
    expected_hash=protocol["freeze"]["implementation_sha256"]
    h=hashlib.sha256()
    for name in protocol["freeze"]["implementation_files"]: h.update((ROOT/name).read_bytes())
    if h.hexdigest()!=expected_hash: raise SystemExit("PIT-17 implementation hash changed after freeze")
    p15=pit15_rows(); held=pit16_rows(set(split["held_out"])); hard=[r for r in held if not r["expected"]]
    write_jsonl(EXP / "pit15-regression.jsonl",p15); write_jsonl(EXP / "pit16-heldout-results.jsonl",held)
    m15=score(p15); m16=score(held)
    # PIT-15 specialized metrics.
    failures=[r for r in p15 if r["expected"]]; valid=[r for r in p15 if not r["expected"]]
    muse=[r for r in p15 if r["candidate_id"]=="meta/muse-glimmer-30b"]
    lifecycle={"preference_drift_001","user_correction_001","rare_exception_001","insufficient_evidence_001","long_term_consistency_001"}
    life=[r for r in valid if r["scenario_id"] in lifecycle]
    det=lambda rs: sum(r["decision"]["status"]!="ACCEPT" for r in rs)
    acc=lambda rs: sum(r["decision"]["status"]=="ACCEPT" for r in rs)
    m15.update({"known_failures_detected":det(failures),"known_failures_total":len(failures),"conflict_detection":score([r for r in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" in r["expected"]])["unsafe_sample_recall"],"unsupported_heuristic_detection":score([r for r in failures if "UNSUPPORTED_CONFLICT_RESOLUTION" not in r["expected"]])["unsafe_sample_recall"],"muse_preservation":round(acc(muse)/len(muse),6),"lifecycle_preservation":round(acc(life)/len(life),6)})
    write_json(EXP / "metrics.json",{"pit15":m15,"pit16_held_out":m16})
    print(json.dumps({"pit15":m15,"pit16_held_out":m16},indent=2))

if __name__=="__main__": main()
