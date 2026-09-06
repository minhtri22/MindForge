from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tools.research.ppf_l4.baselines import BASELINE_BY_ID
from tools.research.ppf_l5.mechanism import TREATMENT_BY_ID, predict as l5_predict, validate_method_payload

from .generate import BENCH_ROOT, C1_VERSION, E1_STATES, load_json, semantic_hash


NEGATIVE_STATES = {
    "INSUFFICIENT_EVIDENCE", "CONFLICTING_EVIDENCE", "UNKNOWN_CONTEXT",
    "NOT_OBSERVABLE", "STALE", "USER_REJECTED", "SUPERSEDED", "DELETED",
}


def _prefix(history: list[dict], checkpoint_time: str) -> list[dict]:
    return [r for r in history if r.get("time", {}).get("ingested_time", "") <= checkpoint_time]


def _predict(records: list[dict], treatment_id: str) -> str:
    validate_method_payload(records)
    if treatment_id == "T0":
        return BASELINE_BY_ID["B9"].predict(records)
    if treatment_id == "T1":
        return l5_predict(records, TREATMENT_BY_ID["T1"])
    raise ValueError("C1 permits only frozen T0 and T1")


def predict_all(treatment_id: str) -> dict:
    cases=[]
    for case_dir in sorted((BENCH_ROOT/"generated"/"cases").iterdir()):
        if not case_dir.is_dir():
            continue
        history=load_json(case_dir/"history.json"); checkpoints=load_json(case_dir/"checkpoints.json")
        validate_method_payload(history); validate_method_payload(checkpoints)
        preds=[]
        for cp in checkpoints["checkpoints"]:
            visible=_prefix(history["history"],cp["time"])
            preds.append({"checkpoint_id":cp["checkpoint_id"],"predicted_answer":_predict(visible,treatment_id),"visible_record_count":len(visible)})
        cases.append({"case_id":history["case_id"],"predictions":preds})
    return {"version":C1_VERSION,"treatment_id":treatment_id,"cases":cases}


def _ratio(n: int, d: int) -> float | None:
    return None if d == 0 else n/d


def _latest_non_control(history: list[dict], checkpoint: str) -> dict | None:
    rows=[r for r in history if r.get("event_type")!="user.feedback" and r.get("time",{}).get("ingested_time","")<=checkpoint]
    return max(rows,key=lambda r:(r["time"]["ingested_time"],r["event_id"])) if rows else None


def score(prediction_doc: dict) -> tuple[dict,list[dict]]:
    rows=[]
    for case in prediction_doc["cases"]:
        cid=case["case_id"]
        expected=load_json(BENCH_ROOT/"evaluator_private"/"expected"/f"{cid}.json")
        truth=load_json(BENCH_ROOT/"evaluator_private"/"truth"/f"{cid}.json")
        history=load_json(BENCH_ROOT/"generated"/"cases"/cid/"history.json")
        checkpoints=load_json(BENCH_ROOT/"generated"/"cases"/cid/"checkpoints.json")
        exp={x["checkpoint_id"]:x["expected_answer"] for x in expected["answers"]}
        cpt={x["checkpoint_id"]:x["time"] for x in checkpoints["checkpoints"]}
        for p in case["predictions"]:
            cp=p["checkpoint_id"]; latest=_latest_non_control(history["history"],cpt[cp])
            latest_state=latest.get("observability",{}).get("state") if latest else None
            rows.append({
                "case_id":cid,"checkpoint_id":cp,"predicted":p["predicted_answer"],"expected":exp[cp],
                "risk_class":truth["risk_class"],"family":truth["family"],"structural_holdout":truth["structural_holdout"],
                "pair_id":truth.get("pair_id"),"pair_template":truth.get("pair_template"),"pair_arm":truth.get("pair_arm"),
                "latest_observability_state":latest_state,"correct":p["predicted_answer"]==exp[cp],
            })
    tp=sum(r["predicted"]=="SUPPORTED" and r["expected"]=="SUPPORTED" for r in rows)
    fp=sum(r["predicted"]=="SUPPORTED" and r["expected"]!="SUPPORTED" for r in rows)
    fn=sum(r["predicted"]!="SUPPORTED" and r["expected"]=="SUPPORTED" for r in rows)
    negatives=sum(r["expected"]!="SUPPORTED" for r in rows)
    confusion: dict[str,Counter]=defaultdict(Counter)
    for r in rows: confusion[r["expected"]][r["predicted"]]+=1
    hard={
        "not_observable_as_current":sum(r["expected"]=="NOT_OBSERVABLE" and r["predicted"]=="SUPPORTED" for r in rows),
        "correction_resurrection":sum(r["expected"]=="USER_REJECTED" and r["predicted"]=="SUPPORTED" for r in rows),
        "deleted_active_return":sum(r["expected"]=="DELETED" and r["predicted"]=="SUPPORTED" for r in rows),
        "observable_non_occurrence_semantic_regression":sum(r["latest_observability_state"]=="OBSERVABLE_NON_OCCURRENCE" and r["predicted"]=="NOT_OBSERVABLE" for r in rows),
    }
    metrics={
        "units":len(rows),"exact_state_count":sum(r["correct"] for r in rows),"exact_state_accuracy":_ratio(sum(r["correct"] for r in rows),len(rows)),
        "supported_tp":tp,"supported_fp":fp,"supported_fn":fn,"supported_recall":_ratio(tp,tp+fn),"false_promotion_rate":_ratio(fp,negatives),"negative_units":negatives,
        "hard_violations":hard,"confusion_matrix":{k:dict(sorted(v.items())) for k,v in sorted(confusion.items())},
    }
    return metrics,rows


def _slice(rows: list[dict], predicate) -> dict:
    xs=[r for r in rows if predicate(r)]
    return {"units":len(xs),"exact":sum(r["correct"] for r in xs),"exact_accuracy":_ratio(sum(r["correct"] for r in xs),len(xs)),"predicted_supported":sum(r["predicted"]=="SUPPORTED" for r in xs)}


def pair_analysis(rows: list[dict]) -> dict:
    out={}
    for pid in sorted({r["pair_id"] for r in rows if r["pair_id"]}):
        items=[r for r in rows if r["pair_id"]==pid]; arms={}
        for arm in ("A","B"):
            a=sorted([r for r in items if r["pair_arm"]==arm],key=lambda r:r["checkpoint_id"])
            arms[arm]={"predictions":[r["predicted"] for r in a],"expected":[r["expected"] for r in a]}
        arms_ok=arms["A"]["predictions"]==arms["A"]["expected"] and arms["B"]["predictions"]==arms["B"]["expected"]
        out[pid]={"template":items[0]["pair_template"],"arms":arms,"expected_distinction":arms["A"]["expected"]!=arms["B"]["expected"],"predicted_distinction":arms["A"]["predictions"]!=arms["B"]["predictions"],"correct_direction":arms_ok}
    return out


def evaluate() -> dict:
    treatments={}
    for tid in ("T0","T1"):
        prediction=predict_all(tid); metrics,rows=score(prediction)
        treatments[tid]={
            "prediction_sha256":semantic_hash(prediction),"metrics":metrics,
            "slices":{
                "STANDARD":_slice(rows,lambda r:r["risk_class"]=="STANDARD"),
                "HIGH-RISK":_slice(rows,lambda r:r["risk_class"]=="HIGH-RISK"),
                "structural_holdouts":_slice(rows,lambda r:r["structural_holdout"]),
                "fully_observable_controls":_slice(rows,lambda r:r["family"]=="fully observable positive control"),
                "unknown_context":_slice(rows,lambda r:r["expected"]=="UNKNOWN_CONTEXT"),
                "lifecycle":_slice(rows,lambda r:r["expected"] in {"USER_REJECTED","DELETED"}),
            },
            "counterfactual_pairs":pair_analysis(rows),
        }
    t0,t1=treatments["T0"]["metrics"],treatments["T1"]["metrics"]
    gates={
        "exact_improves":t1["exact_state_accuracy"]>t0["exact_state_accuracy"],
        "false_promotion_improves":t1["false_promotion_rate"]<t0["false_promotion_rate"],
        "supported_recall_preserved":t1["supported_recall"]>=t0["supported_recall"],
        "not_observable_violation_improves":t1["hard_violations"]["not_observable_as_current"]<t0["hard_violations"]["not_observable_as_current"],
        "correction_resurrection_zero":t1["hard_violations"]["correction_resurrection"]==0,
        "deleted_active_return_zero":t1["hard_violations"]["deleted_active_return"]==0,
        "observable_nonoccurrence_specificity":t1["hard_violations"]["observable_non_occurrence_semantic_regression"]==0,
    }
    core=all(v for k,v in gates.items() if k!="observable_nonoccurrence_specificity")
    verdict="PASS" if all(gates.values()) else ("PARTIAL" if core else "FAIL")
    return {
        "version":C1_VERSION,"treatments":treatments,"delta_t1_minus_t0":{
            "exact_state_accuracy":t1["exact_state_accuracy"]-t0["exact_state_accuracy"],
            "false_promotion_rate":t1["false_promotion_rate"]-t0["false_promotion_rate"],
            "supported_recall":t1["supported_recall"]-t0["supported_recall"],
            "not_observable_as_current":t1["hard_violations"]["not_observable_as_current"]-t0["hard_violations"]["not_observable_as_current"],
        },"confirmatory_gates":gates,"decision":verdict,"confirmatory_status":"BLINDLY CONFIRMED" if verdict=="PASS" else "NOT CONFIRMED",
    }
