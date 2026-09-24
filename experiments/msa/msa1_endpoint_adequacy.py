"""MSA-1 current-substrate endpoint adequacy qualification.

Zero-science preflight uses only a historical KCL probe.
Fresh MSA-1 execution is blocked pending independent verification of the exact
execution lock. This module never fits a predictor.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

import torch

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    optimizer_for,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl656_boundary_health_signal as k656

PROGRAM = "MSA-1"
PROTOCOL = Path("docs/research/measurement-substrate-adequacy/msa1-endpoint-adequacy-protocol.md")
EXECUTION_LOCK = Path("docs/research/measurement-substrate-adequacy/MSA1_EXECUTION_LOCK.json")
LOCK_VERIFICATION = Path("docs/research/measurement-substrate-adequacy/MSA1_EXECUTION_LOCK_VERIFICATION.md")
DEFAULT_RECORDS = Path("experiments/msa/results/msa1_fresh_endpoints.json")
DEFAULT_FORMAL = Path("experiments/msa/results/FORMAL_RESULT.json")

POLICIES = ("A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS")
A_POLICY = POLICIES[0]

FRESH_SEEDS = (
    7852877,2761307,7980060,8886053,8372679,3779647,
    4340369,4656404,2606362,8420602,5624433,6963476,
    7109847,4349361,4173979,3032355,8811213,4469405,
    2348174,7601591,7945831,7994374,4658109,2192576,
    4761197,2128138,3590175,2017834,8060511,5925203,
    8484385,2496490,2757847,3322545,8487705,3599975,
    3093036,2132012,4581015,6358053,8139369,8085240,
    5318924,7730623,5530158,8191416,7476487,5469329,
    3337298,7726785,7539302,6456627,7169558,2637791,
    4500255,3710728,8425464,8494433,5135219,6119817,
    4907431,8799077,8489437,5715340,2301093,2230544,
    7672062,2312271,6591423,5628578,5723797,6209697,
)
SEED_MANIFEST_SHA256 = "e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347"
RELIABILITY_SEEDS = FRESH_SEEDS[:6]

SPENT_ACO_SEEDS = (
    714845,799297,471852,671302,797856,525370,494800,333039,618491,662800,
    265044,434671,501990,723350,393434,774787,806053,890854,613906,707487,
    415555,641958,505262,776960,428051,767077,464825,448672,416287,770416,
    596609,359597,454064,431281,705347,294795,641624,345481,326782,242385,
)
SPENT_CPRM_SEEDS = (
    814887,863137,944290,493874,333929,674723,629896,563470,452971,659444,
    563718,222175,332624,957861,506630,735777,693319,612663,330455,271971,
    396729,463395,650240,394015,596743,717212,700981,787278,430901,538687,
    927431,885588,748598,724163,573227,689490,439438,774009,639141,850216,
    427422,235913,355296,574310,665271,791304,909129,757353,834226,280648,
    906973,523942,480884,388898,404202,430651,508646,398464,915507,458769,
)
PROTECTED_KCL_SEEDS = tuple(k656.CONFIRM_SEEDS)

EXPECTED_SEEDS = 72
EXPECTED_BOUNDARIES = 216
EXPECTED_PER_STAGE = 72
EXPECTED_ENDPOINT_PAIRS = 648

ACCURACY_CEILING_MIN = 0.50
ACCURACY_P10_SAT_MIN = 23.0 / 24.0
ACCURACY_MIN_UNIQUE = 4
ACCURACY_MIN_SPAN = 2.0 / 24.0
LOSS_MASTERY_95 = -math.log(0.95)
LOSS_MIN_UNIQUE = 10
LOSS_MIN_SPAN = 0.02
GLOBAL_MIN_POLICIES_PER_STAGE = 2

HISTORICAL_PROBE_SEED = 9595

SUBSTRATE_BLOBS = {
    "experiments/kernel_cl/kcl1_substrate.py": "4303dd544e0bdb935c499abedc62aa095bc56674",
    "experiments/kernel_cl/kcl6_long_horizon.py": "33a743d62b5a83286c8945ffc0f473ae66fe50c0",
    "experiments/kernel_cl/kcl61_weighted_replay_ab.py": "9a2ea8435bc92d65af7044b5351d06adc6cc2d44",
    "experiments/kernel_cl/kcl63_fuzzy_decay_abcd.py": "cb6cf442d9d6a01c6cec173ecd73771fc6ba30c7",
    "experiments/kernel_cl/kcl65_specificity_ab.py": "88aa11fea6e8474c323c02491c0b85a91722c686",
    "experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py": "7119b9520f50de53a42313f7c7173c8d5daec2f1",
    "mindforge/config.py": "54ab270a25edd962e62360e14736b28f52a4fbcd",
    "mindforge/model.py": "3f6b8f1f411d7a3ba061d4bca10cd0002ae91594",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_manifest_sha256(values: Iterable[int] = FRESH_SEEDS) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def git_blob(path: str | Path) -> str:
    return git("hash-object", str(path))


def _percentile(values: list[float], q: float) -> float:
    xs = sorted(float(x) for x in values)
    pos = (len(xs)-1)*q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[int(lo)]
    frac = pos-lo
    return xs[int(lo)]*(1-frac)+xs[int(hi)]*frac


def _historical_seed_candidates() -> set[int]:
    paths = [Path("Lineage.md")]
    for base in (
        Path("docs/research/kernel-continual-learning"),
        Path("experiments/kernel_cl"),
        Path("docs/research/adaptive-continual-outcomes"),
        Path("docs/research/continual-policy-response"),
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out = set()
    for path in paths:
        try:
            txt = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in txt.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


def validate_seed_manifest() -> dict[str, Any]:
    fresh=set(FRESH_SEEDS)
    historical=_historical_seed_candidates()
    protected=set(PROTECTED_KCL_SEEDS)
    aco=set(SPENT_ACO_SEEDS)
    cprm=set(SPENT_CPRM_SEEDS)
    checks={
        "count_72":len(FRESH_SEEDS)==EXPECTED_SEEDS,
        "unique_72":len(fresh)==EXPECTED_SEEDS,
        "manifest_hash":seed_manifest_sha256()==SEED_MANIFEST_SHA256,
        "historical_disjoint":fresh.isdisjoint(historical),
        "protected_disjoint":fresh.isdisjoint(protected),
        "aco_spent_disjoint":fresh.isdisjoint(aco),
        "cprm_spent_disjoint":fresh.isdisjoint(cprm),
    }
    return {
        "valid":all(checks.values()),
        "checks":checks,
        "historical_collisions":sorted(fresh & historical),
        "protected_collisions":sorted(fresh & protected),
        "aco_spent_collisions":sorted(fresh & aco),
        "cprm_spent_collisions":sorted(fresh & cprm),
        "manifest_sha256":seed_manifest_sha256(),
    }


def frozen_substrate_snapshot() -> dict[str, Any]:
    cfg=KCL1Config()
    checks={
        "config_exact":(
            cfg.vocab_size==96 and cfg.d_model==16 and cfg.n_heads==2
            and cfg.n_layers==1 and cfg.max_context==2 and cfg.ff_mult==4
            and cfg.dropout==0.0 and cfg.relations==24 and cfg.batch_size==16
            and cfg.stage_steps==250 and cfg.learning_rate==3e-3
            and cfg.weight_decay==0.0
        ),
        "task_order_exact":[x[0] for x in task_sequence(cfg)]==[
            "T1_U1_A","T2_U1_B","T3_U3_A","T4_U3_B"
        ],
        "policies_exact":tuple(k655.POLICIES)==POLICIES,
        "checkpoints_exact":tuple(k655.CHECKPOINTS)==tuple(range(0,251,25)),
        "source_blobs_exact":all(git_blob(p)==sha for p,sha in SUBSTRATE_BLOBS.items()),
    }
    return {"valid":all(checks.values()),"checks":checks}


def _clone_model_opt(model, opt, cfg):
    m=copy.deepcopy(model)
    o=optimizer_for(m,cfg)
    o.load_state_dict(copy.deepcopy(opt.state_dict()))
    return m,o


def run_endpoint_counterfactual(*,model,optimizer,memories,observed_tasks,next_task,seed,next_stage,cfg):
    models={}
    opts={}
    infos={}
    for policy in POLICIES:
        m,o=_clone_model_opt(model,optimizer,cfg)
        o,info=k655._policy_boundary(policy,m,o,cfg)
        models[policy]=m
        opts[policy]=o
        infos[policy]=info

    fork_equal=all(
        all(torch.equal(models[A_POLICY].state_dict()[name],models[p].state_dict()[name])
            for name in models[A_POLICY].state_dict())
        for p in POLICIES[1:]
    )
    memory_copy=copy.deepcopy(memories)
    stage=k655._train_stage_lockstep(
        models,opts,memory_copy,next_task[1],
        [task for _,task in observed_tasks],
        seed=seed,stage=next_stage,
    )

    endpoints={}
    endpoint_consistency=True
    for policy in POLICIES:
        point=stage["curves"][policy][-1]
        summary=stage["curve_summary"][policy]
        endpoint_consistency = endpoint_consistency and int(point["step"])==250
        endpoint_consistency = endpoint_consistency and float(point["accuracy"])==float(summary["final_accuracy"])
        endpoints[policy]={
            "terminal_accuracy":float(point["accuracy"]),
            "terminal_cross_entropy_loss":float(point["loss"]),
            "step":int(point["step"]),
        }

    integrity={
        "fork_models_equal":fork_equal,
        "boundary_model_unchanged":all(bool(x["model_unchanged"]) for x in infos.values()),
        "exact_replay_match":math.isclose(float(stage["exact_replay_match_rate"]),1.0,abs_tol=0.0,rel_tol=0.0),
        "endpoint_same_curve_state":endpoint_consistency,
    }
    integrity["valid"]=all(integrity.values())

    next_memories=k655._decay(memory_copy)
    next_memories.append(k63.ExactMemory.from_task(next_task[1]))
    return {
        "endpoints":endpoints,
        "integrity":integrity,
        "_reference_model":models[A_POLICY],
        "_reference_optimizer":opts[A_POLICY],
        "_next_memories":next_memories,
    }


def build_endpoint_records(seed: int, cfg: KCL1Config | None=None) -> list[dict[str,Any]]:
    cfg=cfg or KCL1Config()
    tasks=task_sequence(cfg)
    model=build_model(cfg,seed)
    opt=optimizer_for(model,cfg)
    train_stage(model,opt,tasks[0][1],steps=250,batch_size=16,seed=seed+101)
    memories=[k63.ExactMemory.from_task(tasks[0][1])]
    observed=[tasks[0]]
    rows=[]
    for boundary in (1,2,3):
        next_task=tasks[boundary]
        out=run_endpoint_counterfactual(
            model=model,optimizer=opt,memories=memories,observed_tasks=observed,
            next_task=next_task,seed=seed,next_stage=boundary+1,cfg=cfg,
        )
        rows.append({
            "seed":int(seed),
            "boundary_index":boundary,
            "after_task":observed[-1][0],
            "next_task":next_task[0],
            "endpoints":out["endpoints"],
            "integrity":out["integrity"],
        })
        model=out["_reference_model"]
        opt=out["_reference_optimizer"]
        memories=out["_next_memories"]
        observed=tasks[:boundary+1]
    return rows


def compare_repeat(a,b):
    av=[]; bv=[]
    for ra,rb in zip(a,b):
        for p in POLICIES:
            av += [ra["endpoints"][p]["terminal_accuracy"],ra["endpoints"][p]["terminal_cross_entropy_loss"]]
            bv += [rb["endpoints"][p]["terminal_accuracy"],rb["endpoints"][p]["terminal_cross_entropy_loss"]]
    md=max(abs(float(x)-float(y)) for x,y in zip(av,bv))
    structure=[
        (r["seed"],r["boundary_index"],sorted(r["endpoints"]),r["integrity"]) for r in a
    ] == [
        (r["seed"],r["boundary_index"],sorted(r["endpoints"]),r["integrity"]) for r in b
    ]
    return {"max_abs_diff":md,"same_structure":structure,"exact":md==0.0 and structure}


def _row_valid(r):
    if not bool(r["integrity"]["valid"]):
        return False
    if set(r["endpoints"])!=set(POLICIES):
        return False
    for p in POLICIES:
        e=r["endpoints"][p]
        if int(e["step"])!=250:
            return False
        a=float(e["terminal_accuracy"])
        l=float(e["terminal_cross_entropy_loss"])
        if not (math.isfinite(a) and 0.0<=a<=1.0 and math.isfinite(l) and l>=0.0):
            return False
    return True


def support_integrity(records, expected_seeds=FRESH_SEEDS):
    expected=set(int(x) for x in expected_seeds)
    observed=set(int(r["seed"]) for r in records)
    per_seed={s:0 for s in expected}
    per_stage={1:0,2:0,3:0}
    for r in records:
        if int(r["seed"]) in per_seed: per_seed[int(r["seed"])]+=1
        if int(r["boundary_index"]) in per_stage: per_stage[int(r["boundary_index"])]+=1
    n=len(expected)
    checks={
        "seed_set_exact":observed==expected,
        "seed_count_exact":len(observed)==n,
        "records_exact":len(records)==n*3,
        "three_boundaries_per_seed":all(v==3 for v in per_seed.values()),
        "stage_counts_exact":per_stage=={1:n,2:n,3:n},
        "all_rows_valid":all(_row_valid(r) for r in records),
    }
    return {"valid":all(checks.values()),"checks":checks,"per_stage":per_stage}


def _cell(values, metric):
    p10=_percentile(values,0.10)
    p90=_percentile(values,0.90)
    span=p90-p10
    unique=len(set(values))
    if metric=="accuracy":
        ceiling=sum(float(x)==1.0 for x in values)/len(values)
        saturated=ceiling>=ACCURACY_CEILING_MIN and p10>=ACCURACY_P10_SAT_MIN
        informative=unique>=ACCURACY_MIN_UNIQUE and span>=ACCURACY_MIN_SPAN
        return {"p10":p10,"p90":p90,"robust_span":span,"unique_count":unique,
                "ceiling_fraction":ceiling,"saturated":saturated,"informative":informative}
    saturated=p90<=LOSS_MASTERY_95
    informative=unique>=LOSS_MIN_UNIQUE and span>=LOSS_MIN_SPAN and p90>LOSS_MASTERY_95
    return {"p10":p10,"p90":p90,"robust_span":span,"unique_count":unique,
            "saturated":saturated,"informative":informative}


def _global_state(cells, state):
    by_stage={}
    for stage in (1,2,3):
        n=sum(bool(cells[f"{p}|stage{stage}"][state]) for p in POLICIES)
        by_stage[str(stage)]=n
    return {
        "qualified":all(n>=GLOBAL_MIN_POLICIES_PER_STAGE for n in by_stage.values()),
        "qualifying_policies_per_stage":by_stage,
    }


def endpoint_geometry(records):
    accuracy={}
    loss={}
    for p in POLICIES:
        for stage in (1,2,3):
            rows=[r for r in records if int(r["boundary_index"])==stage]
            av=[float(r["endpoints"][p]["terminal_accuracy"]) for r in rows]
            lv=[float(r["endpoints"][p]["terminal_cross_entropy_loss"]) for r in rows]
            accuracy[f"{p}|stage{stage}"]=_cell(av,"accuracy")
            loss[f"{p}|stage{stage}"]=_cell(lv,"loss")
    return {
        "accuracy_cells":accuracy,
        "loss_cells":loss,
        "accuracy_saturated":_global_state(accuracy,"saturated"),
        "accuracy_informative":_global_state(accuracy,"informative"),
        "loss_saturated":_global_state(loss,"saturated"),
        "loss_informative":_global_state(loss,"informative"),
    }


def adjudicate_records(records,reliability_checks,expected_seeds=FRESH_SEEDS):
    support=support_integrity(records,expected_seeds)
    reliability_ok=(
        len(reliability_checks)==len(RELIABILITY_SEEDS)
        and all(bool(x.get("exact")) for x in reliability_checks)
    )
    if not support["valid"] or not reliability_ok:
        return {"status":"STOP","verdict":"STOP_INTEGRITY_OR_SUPPORT",
                "reason":"INTEGRITY_OR_RELIABILITY_FAILURE",
                "support_integrity":support,"reliability_ok":reliability_ok}

    g=endpoint_geometry(records)
    ai=g["accuracy_informative"]["qualified"]
    az=g["accuracy_saturated"]["qualified"]
    li=g["loss_informative"]["qualified"]
    lz=g["loss_saturated"]["qualified"]

    if ai and li:
        status,verdict,reason="PASS","ENDPOINT_MEASUREMENT_ADEQUATE","JOINT_ENDPOINTS_INFORMATIVE"
    elif az and li:
        status,verdict,reason="PASS","ACCURACY_COARSE_LOSS_INFORMATIVE","ACCURACY_SATURATED_LOSS_INFORMATIVE"
    elif az and lz:
        status,verdict,reason="PASS","CURRENT_SUBSTRATE_ENDPOINT_SATURATED","JOINT_ENDPOINT_SATURATION"
    else:
        status,verdict,reason="STOP","STOP_INTEGRITY_OR_SUPPORT","CLASSIFICATION_SUPPORT_INSUFFICIENT"
    return {"status":status,"verdict":verdict,"reason":reason,
            "support_integrity":support,"reliability_ok":reliability_ok,
            "endpoint_geometry":g}


def _historical_probe():
    first=build_endpoint_records(HISTORICAL_PROBE_SEED)
    second=build_endpoint_records(HISTORICAL_PROBE_SEED)
    repeat=compare_repeat(first,second)
    return {
        "seed":HISTORICAL_PROBE_SEED,
        "record_count":len(first),
        "all_integrity_valid":len(first)==3 and all(_row_valid(r) for r in first),
        "repeat":repeat,
        "fresh_seed_used":HISTORICAL_PROBE_SEED in set(FRESH_SEEDS),
    }


def _validate_lock(lock):
    checks={
        "program":lock.get("program")==PROGRAM,
        "seed_manifest":lock.get("seed_manifest",{}).get("sha256")==SEED_MANIFEST_SHA256,
        "protocol_blob":lock.get("protocol",{}).get("git_blob_sha")==git_blob(PROTOCOL),
        "runner_blob":lock.get("implementation",{}).get("runner_git_blob_sha")==git_blob(Path(__file__)),
        "substrate_blobs":lock.get("substrate",{}).get("git_blobs")==SUBSTRATE_BLOBS,
    }
    return {"valid":all(checks.values()),"checks":checks}


def execution_authorized():
    if not EXECUTION_LOCK.exists() or not LOCK_VERIFICATION.exists():
        return False
    txt=LOCK_VERIFICATION.read_text(encoding="utf-8")
    return "MSA1_EXECUTION_LOCK_VERIFICATION_PASS" in txt and sha256_file(EXECUTION_LOCK) in txt


def preflight():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    seeds=validate_seed_manifest()
    substrate=frozen_substrate_snapshot()
    lock=(
        _validate_lock(json.loads(EXECUTION_LOCK.read_text(encoding="utf-8")))
        if EXECUTION_LOCK.exists() else {"valid":False,"checks":{"lock_exists":False}}
    )
    probe=_historical_probe()
    checks={
        "seed_manifest_valid":seeds["valid"],
        "substrate_exact":substrate["valid"],
        "lock_valid":lock["valid"],
        "historical_probe_integrity":probe["all_integrity_valid"],
        "historical_probe_repeat_exact":probe["repeat"]["exact"],
        "historical_probe_not_fresh":not probe["fresh_seed_used"],
        "fresh_records_absent":not DEFAULT_RECORDS.exists(),
        "formal_result_absent":not DEFAULT_FORMAL.exists(),
        "independent_verification_absent":not LOCK_VERIFICATION.exists(),
        "fresh_execution_blocked":not execution_authorized(),
    }
    ok=all(checks.values())
    return {
        "schema":"MSA1-ZERO-SCIENCE-PREFLIGHT-v1",
        "program":PROGRAM,
        "status":"PASS" if ok else "FAIL",
        "verdict":"MSA1_ZERO_SCIENCE_PREFLIGHT_PASS" if ok else "MSA1_ZERO_SCIENCE_PREFLIGHT_FAIL",
        "git_commit":git("rev-parse","HEAD"),
        "protocol_sha256":sha256_file(PROTOCOL),
        "seed_manifest":seeds,
        "substrate":substrate,
        "execution_lock":lock,
        "historical_probe":probe,
        "checks":checks,
        "fresh_seed_execution_attempted":False,
        "scientific_outcome_generated":False,
        "difficulty_mutation_performed":False,
        "predictor_fitting_performed":False,
    }


def collect_fresh():
    if not execution_authorized():
        raise RuntimeError("MSA-1 fresh execution is not independently authorized")
    if not validate_seed_manifest()["valid"] or not frozen_substrate_snapshot()["valid"]:
        raise RuntimeError("MSA-1 frozen identity invalid")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    records=[]
    reliability=[]
    for seed in FRESH_SEEDS:
        first=build_endpoint_records(seed)
        records.extend(first)
        if seed in RELIABILITY_SEEDS:
            second=build_endpoint_records(seed)
            reliability.append({"seed":seed,**compare_repeat(first,second)})
    return {
        "schema":"MSA1-FRESH-COLLECTION-v1","program":PROGRAM,
        "protocol_sha256":sha256_file(PROTOCOL),
        "seed_manifest_sha256":seed_manifest_sha256(),
        "records":records,"reliability_checks":reliability,
    }


def _write(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",required=True,choices=("preflight","collect","adjudicate"))
    p.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.phase=="preflight":
        out=preflight(); _write(args.output,out)
        return 0 if out["status"]=="PASS" else 2
    if args.phase=="collect":
        _write(args.output,collect_fresh()); return 0
    if args.input is None:
        p.error("--input required")
    raw=json.loads(args.input.read_text(encoding="utf-8"))
    result=adjudicate_records(raw["records"],raw["reliability_checks"])
    _write(args.output,{
        "schema":"MSA1-FORMAL-RESULT-v1","program":PROGRAM,
        "protocol_sha256":sha256_file(PROTOCOL),
        "source_records_sha256":sha256_file(args.input),
        "adjudication":result,
    })
    return 0

if __name__=="__main__":
    raise SystemExit(main())
