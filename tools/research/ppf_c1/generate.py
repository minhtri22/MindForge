from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.research.ppf_l2_validation import validate_fixture


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "benchmarks" / "ppf_c1"
DATA_ROOT = ROOT / "docs" / "research" / "data" / "ppf-c1"
C1_VERSION = "ppf-c1-confirmatory/v1"
METHOD_BENCHMARK_VERSION = "ppf-l3-benchmark/v1"
GENERATOR_VERSION = "ppf-c1-generator/v1"
STARTING_COMMIT = "aa90af6ba0f45903d99cec4829355962cb613fa2"
MASTER_SEED = "mindforge-ppf-c1-confirmatory-v1"
MECHANISM_LOCK_SHA256 = "092cb0bb367eac49284f377d1f7e3cfba425edf1f5298136bf8068dbe7cd4e70"
E1_STATES = {
    "NO_OBSERVATION", "SOURCE_UNAVAILABLE", "PERMISSION_UNAVAILABLE_OR_UNKNOWN",
    "DATA_DELAYED", "UNKNOWN_OUTCOME",
}


@dataclass(frozen=True)
class Config:
    config_id: str
    person_key: str
    risk_class: str
    family: str
    scope: str
    plan: tuple[int, ...]
    semantic_mode: str = "ordinary"
    structural_holdout: bool = False
    structural_novelty: str | None = None


@dataclass(frozen=True)
class HistorySpec:
    config_id: str
    behavior_replica: int
    observation_replica: int
    pair_id: str | None = None
    pair_template: str | None = None
    pair_arm: str | None = None


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_preregistration_hash(value: dict) -> str:
    payload = dict(value)
    payload.pop("canonical_preregistration_sha256", None)
    return semantic_hash(payload)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_seed(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256(canonical_bytes([str(x) for x in parts])).digest()[:8], "big")


def opaque(kind: str, value: str) -> str:
    return f"{kind}-{hashlib.sha256(f'{C1_VERSION}|{kind}|{value}'.encode()).hexdigest()[:14]}"


def iso(base: datetime, minutes: int) -> str:
    return (base + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def configs() -> tuple[Config, ...]:
    return (
        Config("c1-s01", "c1-p01", "STANDARD", "routine/opportunity", "activity:morning-mobility", (1,1,0,1,1,1,0,1,1,0)),
        Config("c1-s02", "c1-p02", "STANDARD", "preference/availability", "choice:midday-beverage", (1,1,1,0,1,1,1,0,1,1)),
        Config("c1-s03", "c1-p03", "STANDARD", "context-conditioned pattern", "activity:workspace-mode", (1,1,0,1,1,0,1,1,1,0), "context"),
        Config("c1-s04", "c1-p04", "STANDARD", "relationship-conditioned pattern", "activity:collaboration-mode", (1,1,1,0,1,1,0,1,1,1), "relationship"),
        Config("c1-s05", "c1-p05", "STANDARD", "temporal sequence", "sequence:evening-routine", (1,0,1,1,1,0,1,1,0,1), "conflict"),
        Config("c1-s06", "c1-p06", "STANDARD", "exception", "activity:weekend-exception", (1,1,1,0,1,1,1,0,1,1), "negative-control"),
        Config("c1-s07", "c1-p07", "STANDARD", "explicit lifecycle", "activity:notification-choice", (1,1,1,1,0,1,1,1,0,1), "lifecycle"),
        Config("c1-s08", "c1-p08", "STANDARD", "fully observable positive control", "activity:daily-checkin", (1,1,0,1,1,1,0,1,1,1)),
        Config("c1-h01", "c1-p09", "HIGH-RISK", "observability / permission loss", "activity:location-routine", (1,1,0,1,1,1,0,1,1,1), "permission", True, "permission loss after stable positive history with separate late recovery/source-unavailable variants"),
        Config("c1-h02", "c1-p10", "HIGH-RISK", "delayed/unknown observation outcome", "activity:sync-routine", (1,1,1,0,1,1,0,1,1,1), "delay", True, "mixed delayed and unknown-outcome observation schedules on a new temporal plan"),
        Config("c1-h03", "c1-p11", "HIGH-RISK", "observability x context interaction", "activity:contextual-commute", (1,1,1,1,1,1,1,1,1,0), "obs-context", True, "unknown context precedes observation loss and direct observable-nonoccurrence versus no-observation controls"),
        Config("c1-h04", "c1-p12", "HIGH-RISK", "observability x lifecycle/currentness interaction", "activity:managed-reminder", (1,1,0,1,1,1,1,0,1,1), "obs-lifecycle", True, "explicit lifecycle controls coexist with later observation unavailability without changing lifecycle precedence"),
    )


def config_map() -> dict[str, Config]:
    return {c.config_id: c for c in configs()}


def pair_map() -> dict[tuple[str, int, int], tuple[str, str, str]]:
    rows: dict[tuple[str,int,int], tuple[str,str,str]] = {}
    def add(config_id: str, behavior: int, pair_id: str, template: str) -> None:
        rows[(config_id, behavior, 0)] = (pair_id, template, "A")
        rows[(config_id, behavior, 1)] = (pair_id, template, "B")
    add("c1-h01", 0, "C1-CF01", "full_observability_vs_permission_loss")
    add("c1-h01", 1, "C1-CF02", "full_observability_vs_permission_loss")
    add("c1-h02", 0, "C1-CF03", "normal_observation_vs_data_delayed")
    add("c1-h02", 1, "C1-CF04", "normal_observation_vs_data_delayed")
    add("c1-h03", 0, "C1-CF05", "observable_nonoccurrence_vs_no_observation")
    add("c1-h03", 1, "C1-CF06", "observable_nonoccurrence_vs_no_observation")
    add("c1-h04", 0, "C1-CF07", "observability_loss_with_lifecycle_control")
    add("c1-h04", 1, "C1-CF08", "observability_loss_with_unknown_context")
    return rows


def history_specs() -> tuple[HistorySpec, ...]:
    pmap = pair_map()
    out: list[HistorySpec] = []
    for config in configs():
        obs_count = 4 if config.risk_class == "HIGH-RISK" else 2
        for b in range(2):
            for o in range(obs_count):
                pair = pmap.get((config.config_id, b, o), (None, None, None))
                out.append(HistorySpec(config.config_id, b, o, *pair))
    return tuple(out)


def case_id(spec: HistorySpec) -> str:
    return opaque("case", f"{spec.config_id}:b{spec.behavior_replica}:o{spec.observation_replica}")


def person_id(config: Config) -> str:
    return opaque("person", config.person_key)


def history_seed_record(spec: HistorySpec) -> dict:
    config = config_map()[spec.config_id]
    return {
        "master_seed_namespace": MASTER_SEED,
        "person_seed": derive_seed(MASTER_SEED, config.person_key, "person"),
        "config_seed": derive_seed(MASTER_SEED, config.config_id, "config"),
        "behavior_seed": derive_seed(MASTER_SEED, config.config_id, "behavior", spec.behavior_replica),
        "observation_seed": derive_seed(MASTER_SEED, config.config_id, "observation", spec.observation_replica),
    }


def checkpoint_times() -> tuple[int, ...]:
    return (125, 245, 365, 485, 605)


def preregistration_document(baseline_source_sha256: str, mechanism_source_sha256: str) -> dict:
    cfgs, specs = configs(), history_specs()
    templates = (
        "full_observability_vs_permission_loss","full_observability_vs_permission_loss",
        "normal_observation_vs_data_delayed","normal_observation_vs_data_delayed",
        "observable_nonoccurrence_vs_no_observation","observable_nonoccurrence_vs_no_observation",
        "observability_loss_with_lifecycle_control","observability_loss_with_unknown_context",
    )
    doc = {
        "version": C1_VERSION, "starting_commit": STARTING_COMMIT, "split": "c1-confirmatory",
        "scientific_hypothesis": "Explicit Observability Eligibility before frozen B9 reduces false active claims caused by unavailable/unknown observation state while preserving SUPPORTED recall and lifecycle correctness.",
        "treatments": {
            "T0": {"definition":"frozen L4 B9 Lifecycle-Naive Rule","baseline_id":"B9","baseline_source_sha256":baseline_source_sha256},
            "T1": {"definition":"frozen L5 B9 + E1 Observability Eligibility","treatment_id":"T1","components":["E1"],"mechanism_source_sha256":mechanism_source_sha256,"mechanism_lock_sha256":MECHANISM_LOCK_SHA256},
        },
        "persons": [{"person_id":person_id(c),"person_key":c.person_key,"truth_config_id":c.config_id} for c in cfgs],
        "truth_configurations": [asdict(c) for c in cfgs],
        "risk_allocation": {"STANDARD":8,"HIGH-RISK":4},
        "structural_holdouts": [{"truth_config_id":c.config_id,"novelty":c.structural_novelty} for c in cfgs if c.structural_holdout],
        "history_specifications": [{**asdict(s),"case_id":case_id(s),"seed_registry":history_seed_record(s)} for s in specs],
        "history_count":64,
        "replication":{"STANDARD":"2 behavior x 2 observation = 4/config = 32","HIGH-RISK":"2 behavior x 4 observation = 8/config = 32"},
        "seed_namespace":MASTER_SEED,
        "counterfactual_pairs": [{
            "pair_id":f"C1-CF{i:02d}","template":template,
            "arm_a_case_id":case_id(next(s for s in specs if s.pair_id==f"C1-CF{i:02d}" and s.pair_arm=="A")),
            "arm_b_case_id":case_id(next(s for s in specs if s.pair_id==f"C1-CF{i:02d}" and s.pair_arm=="B")),
        } for i,template in enumerate(templates,1)],
        "checkpoint_plan":{"offset_minutes":list(checkpoint_times()),"checkpoints_per_history":5},
        "expected_metric_vector":["exact_state_accuracy","false_promotion_rate","SUPPORTED_recall","NOT_OBSERVABLE_as_current","correction_resurrection","deleted_active_return","observable_non_occurrence_semantic_regression"],
        "success_rule":[
            "exact_state_accuracy(T1) > exact_state_accuracy(T0)","false_promotion_rate(T1) < false_promotion_rate(T0)",
            "SUPPORTED_recall(T1) >= SUPPORTED_recall(T0)","NOT_OBSERVABLE_as_current(T1) < NOT_OBSERVABLE_as_current(T0)",
            "correction_resurrection(T1) = 0","deleted_active_return(T1) = 0","observable_non_occurrence_semantic_regression(T1) = 0",
        ],
        "failure_rule":"Any primary or specificity condition failing means C1 is not blind confirmation; no treatment change or rerun is allowed.",
        "one_shot_policy":{"semantic_run_count_max":1,"second_run_refused":True,"no_rerolls":True},
        "canonical_hash_rule":"SHA256(canonical JSON excluding canonical_preregistration_sha256), UTF-8, sorted keys, compact separators.",
        "private_evaluator_separation":{"method_visible":["history","checkpoint"],"forbidden_method_inputs":["truth","expected answers","family","pair membership","risk class","structural holdout label","seed semantics"]},
        "registered_before_generation":True,"reroll_count":0,
    }
    doc["canonical_preregistration_sha256"] = canonical_preregistration_hash(doc)
    return doc


def _base() -> datetime:
    return datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc)


def _behavior_plan(config: Config, replica: int) -> list[int]:
    plan = list(config.plan)
    if replica == 1:
        plan[4] = 1 - plan[4]
    if config.semantic_mode == "negative-control":
        plan = [1,0,0,1,0,0,1,0,0,0] if replica == 0 else [0,1,0,0,1,0,0,0,1,0]
    return plan


def _opportunities(config: Config, spec: HistorySpec) -> list[dict]:
    rng = random.Random(derive_seed(MASTER_SEED, config.config_id, "opportunity"))
    return [{
        "opportunity_id":opaque("opp",f"{spec.config_id}:b{spec.behavior_replica}:{i}"),
        "phenomenon_time":iso(_base(),i*60+rng.randint(0,2)), "alternatives":["primary","alternative"],
        "context":{"period":"early" if i<5 else "late","relationship":"known","segment":"a" if i%2==0 else "b"},
    } for i in range(10)]


def _observation_mode(config: Config, spec: HistorySpec, i: int) -> str:
    o = spec.observation_replica
    if config.semantic_mode == "permission":
        if o == 1 and i >= 7: return "PERMISSION_UNAVAILABLE_OR_UNKNOWN"
        if o == 2 and 6 <= i <= 7: return "NO_OBSERVATION"
        if o == 3 and i >= 8: return "SOURCE_UNAVAILABLE"
    if config.semantic_mode == "delay":
        if o == 1 and i >= 7: return "DATA_DELAYED"
        if o == 2 and i >= 8: return "UNKNOWN_OUTCOME"
        if o == 3 and i in {6,8,9}: return "DATA_DELAYED"
    if config.semantic_mode == "obs-context":
        if o == 1 and i == 9: return "NO_OBSERVATION"
        if o == 2 and i >= 8: return "PERMISSION_UNAVAILABLE_OR_UNKNOWN"
        if o == 3 and i >= 7: return "NO_OBSERVATION"
    if config.semantic_mode == "obs-lifecycle":
        if o == 1 and i >= 8: return "PERMISSION_UNAVAILABLE_OR_UNKNOWN"
        if o == 2 and i >= 8: return "HISTORY_UNAVAILABLE"
        if o == 3 and i == 9: return "NO_OBSERVATION"
    return "NORMAL"


def _context_status(config: Config, spec: HistorySpec, i: int) -> str:
    if config.semantic_mode in {"context","relationship"} and spec.observation_replica == 1: return "UNKNOWN"
    if config.semantic_mode == "obs-context" and (spec.behavior_replica == 1 or spec.observation_replica in {2,3}): return "UNKNOWN"
    if config.semantic_mode == "obs-lifecycle" and spec.behavior_replica == 1: return "UNKNOWN"
    if config.semantic_mode == "conflict" and spec.observation_replica == 1 and i >= 6: return "CONFLICTING"
    return "KNOWN"


def _event(case: str, config: Config, spec: HistorySpec, i: int, opportunity: dict, occurred: bool) -> dict:
    mode = _observation_mode(config,spec,i)
    phenomenon = opportunity["phenomenon_time"]
    ingest = iso(datetime.fromisoformat(phenomenon.replace("Z","+00:00")),2)
    context_status = _context_status(config,spec,i)
    event = {
        "schema_version":"ppf-l2/1","event_id":opaque("event",f"{case}:{i}"),"event_type":"activity.sample",
        "source":{"platform":"GENERIC","device_class":"SERVICE","provider":"c1-sensor","source_event_id":opaque("src",f"{case}:{i}")},
        "time":{"phenomenon_time":{"start":phenomenon,"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":phenomenon,"ingested_time":ingest},
        "evidence_kind":"RAW_OBSERVATION","capture_policy":{"mode":"EVENT_DRIVEN","expected_observability":"EXPECTED"},
        "observability":{"state":"OBSERVED_OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE"},
        "opportunity":{"id":opportunity["opportunity_id"],"state":"OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE","alternatives":opportunity["alternatives"],"observability":"FULL"},
        "context":{"relationship":{"status":context_status,"value":"known" if context_status=="KNOWN" else None,"sources":["c1-sensor"]},"period":{"status":"KNOWN","value":opportunity["context"]["period"],"sources":["c1-sensor"]},"segment":{"status":"KNOWN","value":opportunity["context"]["segment"],"sources":["c1-sensor"]}},
        "quality":{"quality_state":"GOOD","coverage_state":"COMPLETE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},"payload":{"action":"primary" if occurred else "not-act"},
    }
    if mode != "NORMAL":
        event["event_type"]="source.observability"; event["evidence_kind"]="OBSERVABILITY_RECORD"
        event["observability"]={"state":mode,"missingness_reason":"C1_OBSERVATION_LIMITATION"}
        event["opportunity"]["state"]="UNKNOWN_OUTCOME"; event["opportunity"]["observability"]="UNKNOWN"
        event["quality"]={"quality_state":"UNKNOWN","coverage_state":"PARTIAL"}; event["payload"]={"availability":"unavailable"}
    return event


def _control(case: str, target: str, relation: str, operation: str, minute: int, scope: str) -> dict:
    when=iso(_base(),minute)
    return {
        "schema_version":"ppf-l2/1","event_id":opaque("event",f"{case}:control:{relation}"),"event_type":"user.feedback",
        "source":{"platform":"USER","device_class":"USER","provider":"user"},
        "time":{"phenomenon_time":{"start":when,"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":when,"ingested_time":when},
        "evidence_kind":"USER_FEEDBACK","observability":{"state":"OBSERVED_OCCURRENCE"},"context":{},"quality":{"quality_state":"GOOD","coverage_state":"NOT_APPLICABLE"},
        "provenance":{"procedure_status":"NOT_APPLICABLE"},"relations":[{"type":relation,"target_event_id":target}],"payload":{"operation":operation,"scope":scope},
    }


def _controls(config: Config, spec: HistorySpec, records: list[dict]) -> list[dict]:
    target=records[2]["event_id"]
    if config.semantic_mode == "lifecycle":
        return [_control(case_id(spec),target,"CORRECTS" if spec.behavior_replica==0 else "DELETES","reject" if spec.behavior_replica==0 else "remove",430,config.scope)]
    if config.semantic_mode == "obs-lifecycle" and spec.behavior_replica == 0:
        return [_control(case_id(spec),target,"CORRECTS","reject",430,config.scope)]
    if config.semantic_mode == "obs-lifecycle" and spec.behavior_replica == 1 and spec.observation_replica in {2,3}:
        return [_control(case_id(spec),target,"DELETES","remove",430,config.scope)]
    return []


def _latest(records: list[dict], checkpoint: str, control: bool) -> dict | None:
    visible=[r for r in records if (r["event_type"]=="user.feedback")==control and r["time"]["ingested_time"]<=checkpoint]
    return max(visible,key=lambda r:(r["time"]["ingested_time"],r["event_id"])) if visible else None


def _oracle_answer(config: Config, records: list[dict], checkpoint: str) -> str:
    control=_latest(records,checkpoint,True)
    if control:
        rel={x["type"] for x in control.get("relations",[])}; op=control.get("payload",{}).get("operation")
        if "DELETES" in rel or op in {"remove","reset"}: return "DELETED"
        if "CORRECTS" in rel or op=="reject": return "USER_REJECTED"
    latest=_latest(records,checkpoint,False)
    if latest is None: return "INSUFFICIENT_EVIDENCE"
    if latest.get("observability",{}).get("state") in E1_STATES: return "NOT_OBSERVABLE"
    visible=[r for r in records if r["event_type"]!="user.feedback" and r["time"]["ingested_time"]<=checkpoint]
    if config.semantic_mode in {"context","relationship","obs-context","obs-lifecycle"}:
        det=[r for r in visible if r.get("opportunity",{}).get("state") in {"OCCURRENCE","OBSERVABLE_NON_OCCURRENCE"}]
        if det and all(r.get("context",{}).get("relationship",{}).get("status")=="UNKNOWN" for r in det): return "UNKNOWN_CONTEXT"
    if any(any(v.get("status")=="CONFLICTING" for v in r.get("context",{}).values()) for r in visible): return "CONFLICTING_EVIDENCE"
    det=[r for r in visible if r.get("opportunity",{}).get("state") in {"OCCURRENCE","OBSERVABLE_NON_OCCURRENCE"}]
    if len(det)<3: return "INSUFFICIENT_EVIDENCE"
    pos=sum(r["opportunity"]["state"]=="OCCURRENCE" for r in det); neg=len(det)-pos
    return "SUPPORTED" if pos>neg else "INSUFFICIENT_EVIDENCE"


def generate_case(spec: HistorySpec) -> dict:
    config=config_map()[spec.config_id]; case=case_id(spec); opportunities=_opportunities(config,spec); plan=_behavior_plan(config,spec.behavior_replica)
    records=[_event(case,config,spec,i,op,bool(plan[i])) for i,op in enumerate(opportunities)]
    records.extend(_controls(config,spec,records)); records.sort(key=lambda r:(r["time"]["ingested_time"],r["event_id"]))
    checkpoints=[]
    for i,minute in enumerate(checkpoint_times()):
        when=iso(_base(),minute)
        visible_event_ids=[r["event_id"] for r in records if r["time"]["ingested_time"]<=when]
        checkpoints.append({"checkpoint_id":opaque("cp",f"{case}:{i}"),"time":when,"expected_answer":_oracle_answer(config,records,when),"visible_event_ids":visible_event_ids})
    fixture={"fixture_id":"L2-F001","title":"C1 visible history","family":"C1","purpose":"Validate L2 semantics for one blind confirmatory case","source_platform_class":"GENERIC","records":records,
             "expected":{"semantic_interpretation":"Visible evidence only","observability":"Explicit","opportunity":"Explicit","time":"Three-time explicit","provenance":"Retained","multi_device":"Not required","raw_derived":"Explicit","lineage":"Explicit","must_not_infer":"Private evaluator truth"},"adversarial":config.risk_class=="HIGH-RISK","gates":["L2-G1"]}
    return {"config":config,"spec":spec,"case_id":case,"person_id":person_id(config),"behavior_plan":plan,"records":records,"checkpoints":checkpoints,"fixture":fixture,"seeds":history_seed_record(spec)}


def method_history(case: dict) -> dict:
    return {"benchmark_version":METHOD_BENCHMARK_VERSION,"case_id":case["case_id"],"history":case["records"]}


def method_checkpoints(case: dict) -> dict:
    return {"benchmark_version":METHOD_BENCHMARK_VERSION,"case_id":case["case_id"],"checkpoints":[{"checkpoint_id":x["checkpoint_id"],"time":x["time"]} for x in case["checkpoints"]]}


def private_expected(case: dict) -> dict:
    return {"version":C1_VERSION,"case_id":case["case_id"],"answers":[{"checkpoint_id":x["checkpoint_id"],"expected_answer":x["expected_answer"],"visible_event_ids":x["visible_event_ids"]} for x in case["checkpoints"]]}


def private_truth(case: dict) -> dict:
    c,s=case["config"],case["spec"]
    return {"version":C1_VERSION,"case_id":case["case_id"],"person_id":case["person_id"],"truth_config_id":c.config_id,"risk_class":c.risk_class,"family":c.family,"scope":c.scope,
            "structural_holdout":c.structural_holdout,"structural_novelty":c.structural_novelty,"pair_id":s.pair_id,"pair_template":s.pair_template,"pair_arm":s.pair_arm,
            "behavior_replica":s.behavior_replica,"observation_replica":s.observation_replica,"seeds":case["seeds"],"behavior_plan":case["behavior_plan"]}


def _history_identity(doc: dict) -> str:
    return semantic_hash(doc.get("history",[]))


def _prior_identities() -> dict[str,set[str]]:
    result={"persons":set(),"configs":set(),"cases":set(),"history_identities":set()}; root=ROOT/"benchmarks"/"ppf_l3"
    for split in ("dev","validation","final"):
        case_root=root/"generated"/split/"cases"
        if case_root.exists():
            for d in case_root.iterdir():
                if d.is_dir():
                    h=load_json(d/"history.json"); result["cases"].add(h["case_id"]); result["history_identities"].add(_history_identity(h))
        for truth_root in (root/"evaluator"/split/"truth",root/"evaluator_private"/split/"truth"):
            if truth_root.exists():
                for p in truth_root.glob("*.json"):
                    t=load_json(p); result["persons"].add(t.get("person_id")); result["configs"].add(t.get("truth",{}).get("truth_config_id") or t.get("truth_config_id"))
    result["persons"].discard(None); result["configs"].discard(None); return result


def qa_cases(cases: list[dict]) -> dict:
    l2_errors={c["case_id"]:validate_fixture(c["fixture"]) for c in cases}; visible_events=sum(len(c["records"]) for c in cases); invalid=sum(len(v) for v in l2_errors.values())
    leak_keys={"truth","expected_answer","expected_answers","family","pair_id","pair_template","pair_arm","risk_class","structural_holdout","seeds","behavior_seed","observation_seed"}; truth_leaks=0
    def walk(v: object) -> None:
        nonlocal truth_leaks
        if isinstance(v,dict):
            truth_leaks += len(leak_keys.intersection(v)); [walk(x) for x in v.values()]
        elif isinstance(v,list): [walk(x) for x in v]
    for c in cases: walk(method_history(c)); walk(method_checkpoints(c))
    future_leaks=0
    for c in cases:
        for cp in c["checkpoints"]:
            expected_visible=[r["event_id"] for r in c["records"] if r["time"]["ingested_time"]<=cp["time"]]
            if cp["visible_event_ids"]!=expected_visible:
                future_leaks += 1
    prior=_prior_identities(); current_person={c["person_id"] for c in cases}; current_config={c["config"].config_id for c in cases}; current_case={c["case_id"] for c in cases}; current_hist={_history_identity(method_history(c)) for c in cases}
    pairs: dict[str,list[dict]]={}
    for c in cases:
        if c["spec"].pair_id: pairs.setdefault(c["spec"].pair_id,[]).append(c)
    pair_checks={}
    for pid,items in sorted(pairs.items()):
        arms={x["spec"].pair_arm:x for x in items}; ok=set(arms)=={"A","B"} and len(items)==2
        if ok:
            a,b=arms["A"],arms["B"]; ok=a["spec"].config_id==b["spec"].config_id and a["spec"].behavior_replica==b["spec"].behavior_replica and a["behavior_plan"]==b["behavior_plan"]
        pair_checks[pid]=ok
    coverage={
        "positive_cases":any(any(x["expected_answer"]=="SUPPORTED" for x in c["checkpoints"]) for c in cases),"negative_controls":any(c["config"].semantic_mode=="negative-control" for c in cases),
        "observability_loss":any(any(r["observability"]["state"] in E1_STATES for r in c["records"] if r["event_type"]!="user.feedback") for c in cases),"ordinary_observable":any(c["config"].semantic_mode=="ordinary" for c in cases),
        "unknown_context":any(any(x["expected_answer"]=="UNKNOWN_CONTEXT" for x in c["checkpoints"]) for c in cases),"conflict":any(any(x["expected_answer"]=="CONFLICTING_EVIDENCE" for x in c["checkpoints"]) for c in cases),
        "lifecycle":any(any(x["expected_answer"] in {"USER_REJECTED","DELETED"} for x in c["checkpoints"]) for c in cases),
    }
    overlaps={"prior_person_overlap":len(current_person&prior["persons"]),"prior_config_overlap":len(current_config&prior["configs"]),"prior_case_overlap":len(current_case&prior["cases"]),"prior_history_identity_overlap":len(current_hist&prior["history_identities"])}
    status="PASS" if len(cases)==64 and len(current_person)==12 and len(current_config)==12 and invalid==0 and truth_leaks==0 and future_leaks==0 and len(pairs)>=8 and all(pair_checks.values()) and all(v==0 for v in overlaps.values()) and all(coverage.values()) else "REVISE"
    return {"status":status,"persons":len(current_person),"truth_configs":len(current_config),"histories_registered":64,"histories_generated":len(cases),"histories_retained":len(cases),"rerolls":0,
            "risk_allocation":{"STANDARD":sum(c.risk_class=="STANDARD" for c in configs()),"HIGH-RISK":sum(c.risk_class=="HIGH-RISK" for c in configs())},"structural_holdouts":sum(c.structural_holdout for c in configs()),
            "visible_events":visible_events,"l2_valid_events":visible_events if invalid==0 else visible_events-invalid,"l2_errors":l2_errors,"truth_leaks":truth_leaks,"future_leaks":future_leaks,**overlaps,
            "focused_pairs":len(pairs),"pair_contracts":pair_checks,"coverage":coverage}


def generate_dataset() -> dict:
    prereg=load_json(DATA_ROOT/"c1-preregistration.json")
    if canonical_preregistration_hash(prereg)!=prereg["canonical_preregistration_sha256"]: raise RuntimeError("C1 preregistration canonical hash mismatch")
    if BENCH_ROOT.exists(): raise RuntimeError("C1 benchmark root already exists; generation is one-shot and refuses overwrite")
    cases=[generate_case(s) for s in history_specs()]; qa=qa_cases(cases)
    if qa["status"]!="PASS": raise RuntimeError(f"C1 generator QA failed before persistence: {qa}")
    for c in cases:
        d=BENCH_ROOT/"generated"/"cases"/c["case_id"]; write_json(d/"history.json",method_history(c)); write_json(d/"checkpoints.json",method_checkpoints(c))
        write_json(BENCH_ROOT/"evaluator_private"/"expected"/f"{c['case_id']}.json",private_expected(c)); write_json(BENCH_ROOT/"evaluator_private"/"truth"/f"{c['case_id']}.json",private_truth(c))
    registry={"version":C1_VERSION,"configs":[asdict(c) for c in configs()],"histories":[{**asdict(s),"case_id":case_id(s)} for s in history_specs()]}; write_json(BENCH_ROOT/"specs"/"c1_scenario_registry.json",registry)
    public_manifest={"version":C1_VERSION,"split":"c1-confirmatory","cases":[{"case_id":c["case_id"],"history_sha256":file_hash(BENCH_ROOT/"generated"/"cases"/c["case_id"]/"history.json"),"checkpoints_sha256":file_hash(BENCH_ROOT/"generated"/"cases"/c["case_id"]/"checkpoints.json")} for c in cases]}
    private_manifest={"version":C1_VERSION,"cases":[{"case_id":c["case_id"],"expected_sha256":file_hash(BENCH_ROOT/"evaluator_private"/"expected"/f"{c['case_id']}.json"),"truth_sha256":file_hash(BENCH_ROOT/"evaluator_private"/"truth"/f"{c['case_id']}.json")} for c in cases]}
    write_json(BENCH_ROOT/"manifests"/"c1_public_manifest.json",public_manifest); write_json(BENCH_ROOT/"manifests"/"c1_private_manifest.json",private_manifest); write_json(BENCH_ROOT/"reports"/"c1_generator_qa.json",qa)
    summary={k:qa[k] for k in ("persons","truth_configs","histories_registered","histories_generated","histories_retained","rerolls","risk_allocation","structural_holdouts","visible_events","l2_valid_events","truth_leaks","future_leaks","prior_person_overlap","prior_config_overlap","prior_case_overlap","prior_history_identity_overlap","focused_pairs")}
    write_json(BENCH_ROOT/"reports"/"c1_dataset_summary.json",summary); (BENCH_ROOT/"VERSION").write_text(C1_VERSION+"\n",encoding="utf-8")
    return qa
