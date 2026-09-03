"""PPF-L3 E1 generator hardening + small smoke benchmark.

Research tooling only. No recognizer, scoring rule, or production runtime logic.
"""
from __future__ import annotations

import copy
import fnmatch
import hashlib
import inspect
import json
import random
import re
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Any

from tools.research.ppf_l2_validation import validate_fixture, semantic_errors, load_json, SCHEMA_PATH
from tools.research.ppf_l3 import e0
from tools.research.ppf_l2_validate import negative_tests
from jsonschema import Draft202012Validator, FormatChecker

V = "ppf-l3-e1-smoke/1"
STARTING_COMMIT = "7b7856aa1dbc31cf331064e37349da335f881d1b"
MASTER = "mindforge-ppf-l3-e1-v1"

LEAK = {
    "latent_truth", "expected_answer", "identifiability", "scenario_family",
    "behavior_seed", "observation_seed", "pair_id", "no_pattern", "fake_drift",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def derive_seed(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256(canonical_bytes([str(p) for p in parts])).digest()[:8], "big")


def opaque(kind: str, value: str) -> str:
    return f"{kind}-{hashlib.sha256(f'{V}|{kind}|{value}'.encode()).hexdigest()[:10]}"


def iso(base: datetime, minutes: int) -> str:
    return (base + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Scenario:
    key: str
    person: str
    structure: str
    variant: str
    truth_kind: str
    occurrence_plan: tuple[int, ...]
    alternatives: tuple[tuple[str, ...], ...]
    observation_policy: str = "FULL"
    context_mode: str = "KNOWN"
    control: str | None = None
    replica: bool = False
    derived: bool = False
    delayed_index: int | None = None
    answers: tuple[str, ...] = ("INSUFFICIENT_EVIDENCE", "SUPPORTED", "SUPPORTED", "SUPPORTED")
    identifiability: str = "YES"


def _alts(n: int, values: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(values for _ in range(n))


def scenarios() -> list[Scenario]:
    # 15 registered variants across exactly 10 structures. Each variant receives two observation replicas -> 30 histories.
    base = [
        Scenario("s1", "p1", "S1", "primary", "STABLE_ROUTINE", (1,1,0,1,1,0), _alts(6,("act","not-act")), delayed_index=4),
        Scenario("s2", "p2", "S2", "primary", "NO_PATTERN", (1,0,1,0,0,1), _alts(6,("act","not-act")), answers=("INSUFFICIENT_EVIDENCE",)*4),
        Scenario("s3a", "p3", "S3", "full", "STABLE_ROUTINE", (1,1,1,1,1,1), _alts(6,("act","not-act"))),
        Scenario("s3b", "p3", "S3", "permission-loss", "STABLE_ROUTINE", (1,1,1,1,1,1), _alts(6,("act","not-act")), observation_policy="PERMISSION_LOSS", answers=("INSUFFICIENT_EVIDENCE","SUPPORTED","NOT_OBSERVABLE","NOT_OBSERVABLE"), identifiability="NO"),
        Scenario("s4a", "p4", "S4", "base", "STABLE_ROUTINE", (1,1,1,1,1,1), _alts(6,("act","not-act"))),
        Scenario("s4b", "p4", "S4", "rejected", "STABLE_ROUTINE", (1,1,1,1,1,1), _alts(6,("act","not-act")), control="REJECT", answers=("INSUFFICIENT_EVIDENCE","SUPPORTED","USER_REJECTED","USER_REJECTED")),
        Scenario("s5", "p5", "S5", "deleted", "STABLE_ROUTINE", (1,1,1,1,1,1), _alts(6,("act","not-act")), control="DELETE", answers=("INSUFFICIENT_EVIDENCE","SUPPORTED","DELETED","DELETED")),
        Scenario("s6a", "p6", "S6", "single", "SINGLE_OCCURRENCE", (1,0,0,0,0,0), _alts(6,("act","not-act")), answers=("INSUFFICIENT_EVIDENCE",)*4),
        Scenario("s6b", "p6", "S6", "replicated", "SINGLE_OCCURRENCE", (1,0,0,0,0,0), _alts(6,("act","not-act")), replica=True, answers=("INSUFFICIENT_EVIDENCE",)*4),
        Scenario("s7", "p1", "S7", "meaningful-alternatives", "PREFERENCE", (1,1,1,1,1,1), _alts(6,("tea","coffee","water")), answers=("INSUFFICIENT_EVIDENCE","INSUFFICIENT_EVIDENCE","SUPPORTED","SUPPORTED")),
        Scenario("s8", "p1", "S8", "constrained-availability", "INSUFFICIENT_TRUE_SUPPORT", (1,1,1,1,1,1), _alts(6,("tea",)), answers=("INSUFFICIENT_EVIDENCE",)*4, identifiability="PARTIAL"),
        Scenario("s9a", "p2", "S9", "known-context", "CONTEXT_ACTION_ASSOCIATION", (1,1,1,1,1,1), _alts(6,("act","not-act")), context_mode="KNOWN"),
        Scenario("s9b", "p2", "S9", "hidden-context", "CONTEXT_ACTION_ASSOCIATION", (1,1,1,1,1,1), _alts(6,("act","not-act")), context_mode="UNKNOWN", answers=("INSUFFICIENT_EVIDENCE","UNKNOWN_CONTEXT","UNKNOWN_CONTEXT","UNKNOWN_CONTEXT"), identifiability="NO"),
        Scenario("s10a", "p5", "S10", "raw-only", "SINGLE_OCCURRENCE", (1,0,0,0,0,0), _alts(6,("act","not-act")), answers=("INSUFFICIENT_EVIDENCE",)*4),
        Scenario("s10b", "p5", "S10", "raw-derived", "SINGLE_OCCURRENCE", (1,0,0,0,0,0), _alts(6,("act","not-act")), derived=True, answers=("INSUFFICIENT_EVIDENCE",)*4),
    ]
    return [replace(x, occurrence_plan=x.occurrence_plan+(0,), alternatives=x.alternatives+(x.alternatives[-1],)) for x in base]


def truth_spec(s: Scenario) -> dict:
    return {
        "person_id": opaque("person", s.person),
        "structure": s.structure,
        "behavioral_truth": s.truth_kind,
        "scope": "choice:generic" if s.structure in {"S7","S8"} else "activity:generic",
        "lifecycle": "ACTIVE",
        "identifiability": s.identifiability,
    }


def _seed_group(s: Scenario) -> str:
    return "preference-pair" if s.structure in {"S7", "S8"} else s.structure

def opportunity_sequence(s: Scenario, truth: dict) -> list[dict]:
    group=_seed_group(s)
    rng = random.Random(derive_seed(MASTER, group, s.person, "opportunity"))
    base = datetime(2026, 2, 1, 8, tzinfo=timezone.utc)
    result=[]
    for i, alternatives in enumerate(s.alternatives):
        result.append({
            "opportunity_id": opaque("opp", f"{truth['person_id']}:{_seed_group(s)}:{i}"),
            "phenomenon_time": iso(base, i*25+rng.randint(0,2)),
            "alternatives": list(alternatives),
            "context": {"period": "morning", "critical": "known" if s.context_mode=="KNOWN" else "unknown"},
        })
    return result


def realize_behavior(s: Scenario, opportunities: list[dict], behavior_replica: int=0) -> list[dict]:
    rng = random.Random(derive_seed(MASTER, s.person, _seed_group(s), "behavior", behavior_replica))
    behavior=[]
    for i, op in enumerate(opportunities):
        occurred=bool(s.occurrence_plan[i])
        choice=(op["alternatives"][0] if occurred and op["alternatives"] else None)
        behavior.append({
            "opportunity_id": op["opportunity_id"], "occurred": occurred, "choice": choice,
            "behavior_nonce": rng.randint(0,10**9), "phenomenon_time": op["phenomenon_time"],
        })
    return behavior


def _base_event(s: Scenario, i: int, op: dict, bh: dict, ingested: str) -> dict:
    occurred=bh["occurred"]; obs="OBSERVED_OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE"; ost="OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE"
    ctx={"critical":{"status":"KNOWN","value":"workday","sources":["e1-sensor"]}}
    if s.context_mode=="UNKNOWN": ctx={"critical":{"status":"UNKNOWN","sources":["e1-sensor"]}}
    return {
        "schema_version":"ppf-l2/1", "event_id":opaque("event",f"{s.key}:{i}:raw"), "event_type":"choice.sample" if s.structure in {"S7","S8"} else "activity.sample",
        "source":{"platform":"GENERIC","device_class":"SERVICE","provider":"e1-sensor","source_event_id":opaque("src",f"{s.person}:{s.structure:{i}")},
        "time":{"phenomenon_time":{"start":bh["phenomenon_time"],"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":bh["phenomenon_time"],"ingested_time":ingested},
        "evidence_kind":"RAW_OBSERVATION","capture_policy":{"mode":"EVENT_DRIVEN","expected_observability":"EXPECTED"},
        "observability":{"state":obs},"opportunity":{"id":op["opportunity_id"],"state":ost,"alternatives":op["alternatives"],"observability":"FULL"},
        "context":ctx,"quality":{"quality_state":"GOOD","coverage_state":"COMPLETE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},
        "payload":{"action":bh["choice"] if s.structure in {"S7","S8"} else ("act" if occurred else "not-act")},
    }


def render_observations(s: Scenario, opportunities: list[dict], behavior: list[dict], observation_replica: int=0) -> tuple[dict,dict]:
    rng=random.Random(derive_seed(MASTER,s.person,s.structure,"observation",observation_replica)); records=[]; provenance={"policy":s.observation_policy,"render_nonce":rng.randint(0,10**9),"records":[]}
    for i,(op,bh) in enumerate(zip(opportunities,behavior)):
        pt=datetime.fromisoformat(bh["phenomenon_time"].replace("Z","+00:00")); delay=(75+rng.randint(0,3)) if s.delayed_index==i else (1+rng.randint(0,3)); ing=(pt+timedelta(minutes=delay)).isoformat().replace("+00:00","Z"); ev=_base_event(s,i,op,bk,ing)
        if s.observation_policy=="PERMISSION_LOSS" and i>=3:
            ev["event_type"]="source.observability"; ev["evidence_kind"]="OBSERVABILITY_RECORD"; ev["observability"]={"state":"PERMISSION_UNAVAILABLE_OR_UNKNOWN","missingness_reason":"PERMISSION_LIMITATION"}; ev["opportunity"]["state"]="UNKNOWN_OUTCOME"; ev["opportunity"]["observability"]="UNKNOWN"; ev["quality"]={"quality_state":"UNKNOWN","coverage_state":"UNKNOWN"}; ev["payload"]={"availability":"unavailable"}
        records.append(ev); provenance["records"].append({"event_id":ev["event_id"],"behavior_occurred":bh["occurred"]})
        if s.replica and i==0:
            replica=copy.deepcopy(ev); replica["event_id"]=opaque("event",f"{s.key}:{i}:replica"); replica["relations"]=[{"type":"SAME_ORIGIN_REPLICATED","target_event_id":ev["event_id"]}]; records.append(replica); provenance["records"].append({"event_id":replica["event_id"],"same_origin_of":ev["event_id"]})
        if s.derived and i==0:
            derived=copy.deepcopy(ev); derived["event_id"]=opaque("event",f"{s.key}:{i}:derived"); derived["source"]["source_event_id"]=opaque("src",f"{s.person}:{s.structure}:{i}:derived"); derived["evidence_kind"]="DERIVED_OBSERVATION"; derived["provenance"]={"procedure_status":"KNOWN","procedure":"e1-derivation-v1","input_event_refs":[ev["event_id"]]}; derived["relations"]=[{"type":"DERIVED_FROM","target_event_id":ev["event_id"]}]; dt=datetime.fromisoformat(ev["time"]["ingested_time"].replace("Z","+00:00")); derived["time"]["ingested_time"]=(dt+timedelta(minutes=5)).isoformat().replace("+00:00","Z"); records.append(derived); provenance["records"].append({"event_id":derived["event_id"],"derived_from":ev["event_id"]})
    if s.control:
        ct="2026-02-01T09:00:00Z"; target=records[1]["event_id"]; cid=opaque("event",f"{s.key}:control"); rel="CORRECTS" if s.control=="REJECT" else "DELETES"; records.append({"schema_version":"ppf-l2/1","event_id":cid,"event_type":"user.feedback","source":{"platform":"USER","device_class":"USER","provider":"user"},"time":{"phenomenon_time":{"start":ct,"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":ct,"ingested_time":ct},"evidence_kind":"USER_FEEDBACK","observability":{"state":"OBSERVED_OCCURRENCE"},"context":{},"quality":{"quality_state":"GOOD","coverage_state":"NOT_APPLICABLE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},"relations":[{"type":rel,"target_event_id":target}],"payload":{"operation":"reject" if s.control=="REJECT" else "remove","scope":"activity:generic"}}); provenance["control"]={"event_id":cid,"operation":s.control,"effective_time":ct}
    fixture={"fixture_id":"L2-F001","title":"E1 smoke visible history","family":"E1","purpose":"Validate L2 semantics for E1","source_platform_class":"GENERIC","records":records,"expected":{"semantic_interpretation":"Visible evidence only","observability":"Explicit","opportunity":"Explicit","time":"Three-time explicit","provenance":"Retained","multi_device":"Lineage retained","raw_derived":"Explicit","lineage":"Explicit","must_not_infer":"Truth is evaluator-only"},"adversarial":True,"gates":["L2-G1"]}
    return fixture,provenance


def checkpoint_prefix(records: list[dict], when: str) -> list[dict]:
    t=datetime.fromisoformat(when.replace("Z","+00:00"))
    return [e for e in records if datetime.fromisoformat(e["time"]["ingested_time"].replace("Z","+00:00"))<=t]


def checkpoint_oracle(s: Scenario, records: list[dict]) -> list[dict]:
    base=datetime(2026,2,1,8,tzinfo=timezone.utc); mins=(10,50,110,230)
    return [{"checkpoint_id":opaque("cp",f"{s.key}:{i}"),"time":iso(base,m),"expected_answer":s.answers[i],"identifiability":s.identifiability,"visible_event_ids":[e["event_id"] for e in checkpoint_prefix(records,iso(base,m))]} for i,m in enumerate(mins)]


def generate_case(s: Scenario, behavior_replica: int=0, observation_replica: int=0) -> dict:
    truth=truth_spec(s); opportunities=opportunity_sequence(s,truth); behavior=realize_behavior(s,opportunities,behavior_replica); fixture,prov=render_observations(s,opportunities,behavior,observation_replica); cps=checkpoint_oracle(s,fixture["records"]); cid=opaque("case",f"{s.key}:{behavior_replice}:{observation_replica}")
    evaluator={"case_id":cid,"smoke_version":prov,"scenario":{"key":s.key,"structure":s.structure,"variant":s.variant},"truth":truth,"seeds":{"behavior_replica":behavior_replica,"observation_replica":observation_replica},"observation_provenance":{},"identifiability":s.identifiability,"expected_answers":[c["expected_answer"] for c in cps]}
    return {"id":cid,"scenario":s,"truth":truth,"opps":opportunities,"behavior":behavior,"fixture":fixture,"checkpoints":cps,"eval":evaluator}


def method_manifest(case: dict) -> dict:
    return {"case_id":case["id"],"smoke_version":V,"history":case["fixture"]["records"],"checkpoints":[{"checkpoint_id":c["checkpoint_id"],"time":c["time"]} for c in case["checkpoints"]]}


def leak_paths(case: dict) -> list[str]:
    x=json.dumps(method_manifest(case),sort_keys=True).lower()
    return sorted(u for u in LEAK if u in x)


def _role_records(case: dict) -> dict:
    result={}
    for i,e in enumerate(case["fixture"]["records"]):
        if e["evidence_kind"]=="USER_FEEDBACK": role="control"
        elif any(r["type"]=="SAME_ORIGIN_REPLICATED" for r in e.get("relations",[])): role="replica0"
        elif e["evidence_kind"]=="DERIVED_OBSERVATION": role="derived0"
        else: role=f"base{i}"
        result[role]=e
    return result

def normalize(case: dict) -> dict:
    truth={k:v for k,v in case["truth"].items() if k not in {"structure"}}
    opps=[{"alternatives":o["alternatives"],"context":o["context"]} for o in case["opps"]]
    beh=[{"occurred":b["occurred"],"choice":b["choice"]} for b in case["behavior"]]
    recs={k:_normalize_record(v) for k,v in _role_records(case).items()}
    return {"truth":truth,"opportunities":opps,"behavior":beh,"observation_policy":case["scenario"].observation_policy,"visible_records":recs,"control":case["scenario"].control,"expected_answers":[c["expected_answer"] for c in case["checkpoints"]]}

def _normalize_record(e: dict) -> dict:
    x=copy.deepcopy(e)
    x.pop("event_id",None); x.pop("event_type",None); x["source"].pop("source_event_id",None);  x["source"].pop("uri",None)
    x.pop("time",None)
    for r in x.get("relations",[]): r.discard("target_event_id") if isinstance(r,set) else r.pop("target_event_id",None)
    if "provenance" in x and "input_event_refs" in x["provenance"]: x["provenance"]["input_event_refs"]=["<ref>"]*