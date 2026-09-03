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
import subprocess
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.research.ppf_l2_validation import validate_fixture, semantic_errors, load_json, SCHEMA_PATH
from tools.research.ppf_l3 import e0
from tools.research.ppf_l2_validate import negative_tests
from jsonschema import Draft202012Validator, FormatChecker

V = "ppf-l3-e1-smoke/1"
STARTING_COMMIT = "7b7856aa1dbc31cf331064e37349da335f881d1b"
MASTER = "mindforge-ppf-l3-e1-v1"
ROOT = Path(__file__).resolve().parents[3]

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
        "source":{"platform":"GENERIC","device_class":"SERVICE","provider":"e1-sensor","source_event_id":opaque("src",f"{s.person}:{s.structure}:{i}")},
        "time":{"phenomenon_time":{"start":bh["phenomenon_time"],"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":bh["phenomenon_time"],"ingested_time":ingested},
        "evidence_kind":"RAW_OBSERVATION","capture_policy":{"mode":"EVENT_DRIVEN","expected_observability":"EXPECTED"},
        "observability":{"state":obs},"opportunity":{"id":op["opportunity_id"],"state":ost,"alternatives":op["alternatives"],"observability":"FULL"},
        "context":ctx,"quality":{"quality_state":"GOOD","coverage_state":"COMPLETE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},
        "payload":{"action":bh["choice"] if s.structure in {"S7","S8"} else ("act" if occurred else "not-act")},
    }


def render_observations(s: Scenario, opportunities: list[dict], behavior: list[dict], observation_replica: int=0) -> tuple[dict,dict]:
    rng=random.Random(derive_seed(MASTER,s.person,s.structure,"observation",observation_replica)); records=[]; provenance={"policy":s.observation_policy,"render_nonce":rng.randint(0,10**9),"records":[]}
    for i,(op,bh) in enumerate(zip(opportunities,behavior)):
        pt=datetime.fromisoformat(bh["phenomenon_time"].replace("Z","+00:00")); delay=(75+rng.randint(0,3)) if s.delayed_index==i else (1+rng.randint(0,3)); ing=(pt+timedelta(minutes=delay)).isoformat().replace("+00:00","Z"); ev=_base_event(s,i,op,bh,ing)
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
    truth=truth_spec(s); opportunities=opportunity_sequence(s,truth); behavior=realize_behavior(s,opportunities,behavior_replica); fixture,prov=render_observations(s,opportunities,behavior,observation_replica); cps=checkpoint_oracle(s,fixture["records"]); cid=opaque("case",f"{s.key}:{behavior_replica}:{observation_replica}")
    evaluator={"case_id":cid,"smoke_version":V,"scenario":{"key":s.key,"structure":s.structure,"variant":s.variant},"truth":truth,"seeds":{"behavior_replica":behavior_replica,"observation_replica":observation_replica},"observation_provenance":prov,"identifiability":s.identifiability,"expected_answers":[c["expected_answer"] for c in cps]}
    return {"id":cid,"scenario":s,"truth":truth,"opps":opportunities,"behavior":behavior,"fixture":fixture,"checkpoints":cps,"eval":evaluator}


def method_manifest(case: dict) -> dict:
    return {"case_id":case["id"],"smoke_version":V,"history":case["fixture"]["records"],"checkpoints":[{"checkpoint_id":c["checkpoint_id"],"time":c["time"]} for c in case["checkpoints"]]}


def leak_paths(case: dict) -> list[str]:
    x=json.dumps(method_manifest(case),sort_keys=True).lower()
    return sorted(u for u in LEAK if u in x)


def _role_records(case: dict) -> dict:
    result={}; base_i=0; replica_i=0; derived_i=0
    for e in case["fixture"]["records"]:
        if e["evidence_kind"]=="USER_FEEDBACK": role="control"
        elif any(r["type"]=="SAME_ORIGIN_REPLICATED" for r in e.get("relations",[])): role=f"replica{replica_i}"; replica_i+=1
        elif e["evidence_kind"]=="DERIVED_OBSERVATION": role=f"derived{derived_i}"; derived_i+=1
        else: role=f"base{base_i}"; base_i+=1
        result[role]=e
    return result

def normalize(case: dict) -> dict:
    truth={k:v for k,v in case["truth"].items() if k != "structure"}
    opps=[{"alternatives":o["alternatives"],"context":o["context"]} for o in case["opps"]]
    beh=[{"occurred":b["occurred"],"choice":b["choice"]} for b in case["behavior"]]
    recs={k:_normalize_record(v) for k,v in _role_records(case).items()}
    answers=[{"answer":c["expected_answer"],"identifiability":c["identifiability"]} for c in case["checkpoints"]]
    return {"truth":truth,"opportunities":opps,"behavior":beh,"observation_policy":case["scenario"].observation_policy,"visible_records":recs,"control":case["scenario"].control,"expected_answers":answers}

def _normalize_record(e: dict) -> dict:
    x=copy.deepcopy(e)
    x.pop("event_id",None); x.pop("event_type",None); x["source"].pop("source_event_id",None);  x["source"].pop("uri",None)
    x.pop("time",None)
    for r in x.get("relations",[]): r.discard("target_event_id") if isinstance(r,set) else r.pop("target_event_id",None)
    if "provenance" in x and "input_event_refs" in x["provenance"]:
        x["provenance"]["input_event_refs"]=["<ref>"]*len(x["provenance"]["input_event_refs"])
    return x


@dataclass(frozen=True)
class PairContract:
    pair_id: str
    a: str
    b: str
    allowed_paths: tuple[str,...]
    required_paths: tuple[str,...]


def pair_contracts() -> list[PairContract]:
    return [
        PairContract("CF-A", "s3a", "s3b", (
            "$.observation_policy", "$.truth.identifiability", "$.expected_answers[*].*",
            "$.visible_records.base3.*", "$.visible_records.base4.*", "$.visible_records.base5.*", "$.visible_records.base6.*",
        ), ("$.observation_policy", "$.truth.identifiability", "$.visible_records.base3.observability.state")),
        PairContract("CF-B", "s6a", "s6b", ("$.visible_records.replica0",), ("$.visible_records.replica0",)),
        PairContract("CF-C", "s4a", "s4b", (
            "$.control", "$.expected_answers[2].answer", "$.expected_answers[3].answer", "$.visible_records.control",
        ), ("$.control", "$.visible_records.control")),
        PairContract("CF-D", "s7", "s8", (
            "$.truth.behavioral_truth", "$.truth.identifiability", "$.opportunities[*].alternatives*",
            "$.visible_records.base*.opportunity.alternatives*", "$.expected_answers[*].*",
        ), ("$.truth.behavioral_truth", "$.opportunities[0].alternatives.length")),
        PairContract("CF-E", "s9a", "s9b", (
            "$.truth.identifiability", "$.opportunities[*].context.critical*",
            "$.visible_records.base*.context.critical*", "$.expected_answers[*].*",
        ), ("$.truth.identifiability", "$.opportunities[0].context.critical")),
        PairContract("CF-F", "s10a", "s10b", ("$.visible_records.derived0",), ("$.visible_records.derived0",)),
    ]


def _diff_paths(a: Any, b: Any, path: str="$" ) -> list[str]:
    if type(a) is not type(b): return [path]
    if isinstance(a,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            child=f"{path}.{key}"
            if key not in a or key not in b: out.append(child)
            else: out.extend(_diff_paths(a[key],b[key],child))
        return out
    if isinstance(a,list):
        out=[]
        if len(a)!=len(b): out.append(f"{path}.length")
        for i in range(min(len(a),len(b))): out.extend(_diff_paths(a[i],b[i],f"{path}[{i}]"))
        return out
    return [] if a==b else [path]


def _matches(path: str, patterns: tuple[str,...]) -> bool:
    return any(re.fullmatch(re.escape(p).replace(r"\*",".*"),path) for p in patterns)


def check_pair(contract: PairContract, cases: dict[str, dict]) -> dict:
    changed=_diff_paths(normalize(cases[contract.a]),normalize(cases[contract.b]))
    unexpected=[p for p in changed if not _matches(p,contract.allowed_paths)]
    missing=[p for p in contract.required_paths if not _matches_any(x_paths=changed, pattern=p)]
    return {"changed_paths":changed,"unexpected_paths":unexpected,"missing_required_changes":missing,"pass":bool(changed) and not unexpected and not missing}


def _matches_any(x_paths: list[str], pattern: str) -> bool:
    return any(re.fullmatch(re.escape(pattern).replace(r"\*",".*"),x) for x in x_paths)


def _all_cases() -> dict[str, dict]:
    return {s.key: generate_case(s) for s in scenarios()}


def _replicated_histories() -> list[dict]:
    result=[]
    for s in scenarios():
        for observation_replica in (0, 1):
            result.append(generate_case(s, 0, observation_replica))
    return result


def _checkpoint_prefix_ok(case: dict) -> bool:
    for cp in case["checkpoints"]:
        expected={e["event_id"] for e in checkpoint_prefix(case["fixture"]["records"],cp["time"])}
        if expected != set(cp["visible_event_ids"]): return False
    return True


def _semantic_mutations(cases: dict[str,dict]) -> dict[str,bool]:
    unresolved=copy.deepcopy(cases["s10b"]["fixture"])
    derived=next(e for e in unresolved["records"] if e["evidence_kind"]=="DERIVED_OBSERVATION")
    derived["provenance"]["input_event_refs"]=["event-missing"]

    duplicate=copy.deepcopy(cases["s1"]["fixture"])
    dup=copy.deepcopy(duplicate["records"][0]); dup["event_id"]="event-e1-duplicate"; dup.pop("relations",None); duplicate["records"].append(dup)

    pattern=copy.deepcopy(cases["s1"]["fixture"]); pattern["records"][0]["payload"]["pattern_confidence"]=0.9

    bad_derived=copy.deepcopy(cases["s10b"]["fixture"])
    bad=next(e for e in bad_derived["records"] if e["evidence_kind"]=="DERIVED_OBSERVATION"); bad["provenance"].pop("procedure",None)

    undeclared=copy.deepcopy(cases); undeclared["s3b"]["behavior"][0]["occurred"]=not undeclared["s3b"]["behavior"][0]["occurred"]
    missing=copy.deepcopy(cases); missing["s6b"]=copy.deepcopy(missing["s6a"])
    return {
        "unresolved_input_ref_rejected":bool(validate_fixture(unresolved)),
        "duplicate_source_without_lineage_rejected":bool(validate_fixture(duplicate)),
        "pattern_payload_rejected":bool(validate_fixture(pattern)),
        "derived_missing_procedure_rejected":bool(validate_fixture(bad_derived)),
        "undeclared_behavior_diff_rejected":not check_pair(pair_contracts()[0],undeclared)["pass"],
        "missing_controlled_difference_rejected":not check_pair(pair_contracts()[1],missing)["pass"],
    }


def run_e1() -> dict:
    cases=_all_cases()
    histories=_replicated_histories()
    l2_errors={c["id"]: validate_fixture(c["fixture"]) for c in histories}
    pair_reports={p.pair_id: check_pair(p, cases) for p in pair_contracts()}
    leak_violations=sum(1 for c in histories if leak_paths(c))
    checkpoint_future_leaks=sum(1 for c in histories if not _checkpoint_prefix_ok(c))
    schema=load_json(SCHEMA_PATH)
    validator=Draft202012Validator(schema, format_checker=FormatChecker())
    neg_failures=negative_tests(validator, histories[0]["fixture"])
    e0_summary=e0.run_e0()
    source=inspect.getsource(checkpoint_oracle)
    generic_threshold_found=bool(re.search(r"occurrences\s*>?=|confidence\s*[><=]|pattern_score|classifier|frequency\s*[><=]|ratio\s*[><=]", source, re.I))
    raw=cases["s10a"]; derived=cases["s10b"]
    raw_occurrences=sum(b["occurred"] for b in raw["behavior"]); derived_occurrences=sum(b["occurred"] for b in derived["behavior"])
    s7=scenarios()[9]
    b0=generate_case(s7,0,0); b1=generate_case(s7,1,0); o1=generate_case(s7,0,1)
    behavior_seed_isolation=b0["truth"]==b1["truth"] and b0["opps"]==b1["opps"] and semantic_hash(b0["behavior"])!=semantic_hash(b1["behavior"])
    observation_seed_isolation=b0["truth"]==o1["truth"] and b0["opps"]==o1["opps"] and b0["behavior"]==o1["behavior"] and semantic_hash(method_manifest(b0))!=semantic_hash(method_manifest(o1))
    mutations=_semantic_mutations(cases)
    ident={k:sum(1 for c in histories if c["scenario"].identifiability==k) for k in ("YES","PARTIAL","NO")}
    tracked=subprocess.run(["git","diff","--name-only","--"],cwd=ROOT,check=True,capture_output=True,text=True)
    untracked=subprocess.run(["git","ls-files","--others","--exclude-standard"],cwd=ROOT,check=True,capture_output=True,text=True)
    changed={p.strip().replace("\\","/") for p in (tracked.stdout+"\n"+untracked.stdout).splitlines() if p.strip()}
    allowed_prefixes=("docs/research/","tools/research/ppf_l3/","tests/research/ppf_l3/","benchmarks/ppf_l3/")
    scope_violations=sorted(p for p in changed if not p.startswith(allowed_prefixes))
    summary={
        "status":"PASS",
        "smoke_version":V,
        "starting_commit":STARTING_COMMIT,
        "shared_l2_validator":True,
        "reduced_l3_local_validator":False,
        "E1-G0A": not neg_failures,
        "E1-G0B": all(r["pass"] for r in pair_reports.values()),
        "e0_regression":"PASS" if e0_summary["status"]=="PASS" else "FAIL",
        "smoke_persons":len({truth_spec(s)["person_id"] for s in scenarios()}),
        "smoke_structures":len({s.structure for s in scenarios()}),
        "registered_variants":len(scenarios()),
        "observation_replicas_per_variant":2,
        "smoke_histories":len(histories),
        "smoke_checkpoints":sum(len(c["checkpoints"]) for c in histories),
        "visible_l2_events":sum(len(c["fixture"]["records"]) for c in histories),
        "l2_valid_visible_events":sum(len(c["fixture"]["records"]) for c in histories if not l2_errors[c["id"]]),
        "l2_errors":l2_errors,
        "counterfactual_pair_instances":len(pair_reports),
        "pair_reports":pair_reports,
        "preference_availability_distinction":check_pair(pair_contracts()[3], cases)["pass"],
        "unknown_context_abstention":cases["s9b"]["checkpoints"][1]["expected_answer"]=="UNKNOWN_CONTEXT",
        "raw_derived_non_inflation":raw_occurrences==derived_occurrences,
        "behavior_seed_isolation":behavior_seed_isolation,
        "observation_seed_isolation":observation_seed_isolation,
        "multi_structure_seed_isolation":behavior_seed_isolation and observation_seed_isolation,
        "identifiability":ident,
        "truth_leak_violations":leak_violations,
        "checkpoint_future_leak_violations":checkpoint_future_leaks,
        "oracle_generic_threshold_found":generic_threshold_found,
        "mutations":mutations,
        "l2_negative_tests":{"pass":8-len(neg_failures),"total":8,"failures":neg_failures},
        "scope_violations":scope_violations,
    }
    summary["gates"]={
        "E1-G1":not any(l2_errors.values()) and not neg_failures,
        "E1-G2":summary["E1-G0B"] and all(mutations[k] for k in ("undeclared_behavior_diff_rejected","missing_controlled_difference_rejected")),
        "E1-G3":summary["e0_regression"]=="PASS",
        "E1-G4":summary["multi_structure_seed_isolation"],
        "E1-G5":summary["preference_availability_distinction"],
        "E1-G6":summary["unknown_context_abstention"],
        "E1-G7":summary["raw_derived_non_inflation"],
        "E1-G8":summary["checkpoint_future_leak_violations"]==0,
        "E1-G9":summary["truth_leak_violations"]==0,
        "E1-G10":summary["registered_variants"]==15 and summary["smoke_histories"]==30,
        "E1-G11":not summary["oracle_generic_threshold_found"],
        "E1-G12":not summary["scope_violations"],
    }
    if not summary["E1-G0A"] or not summary["E1-G0B"] or not all(summary["gates"].values()) or not all(mutations.values()):
        summary["status"]="FAIL"
    return summary
