from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluate import evaluate
from .generate import (
    BENCH_ROOT, C1_VERSION, DATA_ROOT, GENERATOR_VERSION, STARTING_COMMIT,
    canonical_preregistration_hash, file_hash, generate_dataset, load_json,
    preregistration_document, semantic_hash, write_json,
)


ROOT=Path(__file__).resolve().parents[3]
PREREG=DATA_ROOT/"c1-preregistration.json"
DATASET_LOCK=DATA_ROOT/"c1-dataset-lock.json"
RUN_LOCK=DATA_ROOT/"c1-run-lock.json"
RUN_STATE=DATA_ROOT/"c1-run-state.json"
RESULTS=DATA_ROOT/"c1-results.json"
SUMMARY=DATA_ROOT/"c1-summary.json"
BASELINE_SOURCE=ROOT/"tools"/"research"/"ppf_l4"/"baselines.py"
MECHANISM_SOURCE=ROOT/"tools"/"research"/"ppf_l5"/"mechanism.py"
EVALUATOR_SOURCE=Path(__file__).resolve().parent/"evaluate.py"
GENERATOR_SOURCE=Path(__file__).resolve().parent/"generate.py"


def _canonical_lock_hash(doc: dict, key: str) -> str:
    payload=dict(doc); payload.pop(key,None); return semantic_hash(payload)


def preregister() -> dict:
    if PREREG.exists() or BENCH_ROOT.exists(): raise RuntimeError("C1 preregistration/generation already exists")
    doc=preregistration_document(file_hash(BASELINE_SOURCE),file_hash(MECHANISM_SOURCE)); write_json(PREREG,doc); return doc


def _artifact_hashes() -> dict[str,str]:
    return {p.relative_to(BENCH_ROOT).as_posix():file_hash(p) for p in sorted(BENCH_ROOT.rglob("*")) if p.is_file()}


def generate_and_lock() -> dict:
    if not PREREG.exists(): raise RuntimeError("preregistration required before generation")
    prereg=load_json(PREREG)
    if canonical_preregistration_hash(prereg)!=prereg["canonical_preregistration_sha256"]: raise RuntimeError("preregistration hash invalid")
    qa=generate_dataset()
    if qa["status"]!="PASS": raise RuntimeError("generator QA failed; confirmation forbidden")
    artifacts=_artifact_hashes()
    lock={
        "version":C1_VERSION,"starting_commit":STARTING_COMMIT,"generator_version":GENERATOR_VERSION,
        "preregistration_sha256":prereg["canonical_preregistration_sha256"],"generator_source_sha256":file_hash(GENERATOR_SOURCE),
        "registry_sha256":file_hash(BENCH_ROOT/"specs"/"c1_scenario_registry.json"),"public_manifest_sha256":file_hash(BENCH_ROOT/"manifests"/"c1_public_manifest.json"),
        "private_manifest_sha256":file_hash(BENCH_ROOT/"manifests"/"c1_private_manifest.json"),"artifact_hashes":artifacts,"reroll_count":0,
    }
    lock["dataset_lock_sha256"]=_canonical_lock_hash(lock,"dataset_lock_sha256"); write_json(DATASET_LOCK,lock); return lock


def _verify_dataset_lock() -> dict:
    lock=load_json(DATASET_LOCK)
    if _canonical_lock_hash(lock,"dataset_lock_sha256")!=lock["dataset_lock_sha256"]: raise RuntimeError("dataset lock self-hash mismatch")
    if lock["artifact_hashes"]!=_artifact_hashes(): raise RuntimeError("C1 dataset hash mismatch")
    return lock


def create_run_lock() -> dict:
    dataset=_verify_dataset_lock(); prereg=load_json(PREREG)
    if file_hash(BASELINE_SOURCE)!=prereg["treatments"]["T0"]["baseline_source_sha256"]: raise RuntimeError("T0 source hash mismatch")
    if file_hash(MECHANISM_SOURCE)!=prereg["treatments"]["T1"]["mechanism_source_sha256"]: raise RuntimeError("T1 mechanism source hash mismatch")
    if RUN_LOCK.exists() or RUN_STATE.exists(): raise RuntimeError("confirmatory run already locked/started")
    lock={
        "version":C1_VERSION,"dataset_lock_sha256":dataset["dataset_lock_sha256"],"preregistration_sha256":prereg["canonical_preregistration_sha256"],
        "t0_source_sha256":file_hash(BASELINE_SOURCE),"t1_mechanism_source_sha256":file_hash(MECHANISM_SOURCE),"evaluation_source_sha256":file_hash(EVALUATOR_SOURCE),
        "CONFIRMATORY_RUN_NOT_YET_EXECUTED":True,"semantic_run_count":0,
    }
    lock["run_lock_sha256"]=_canonical_lock_hash(lock,"run_lock_sha256"); write_json(RUN_LOCK,lock); return lock


def _verify_run_lock() -> dict:
    run=load_json(RUN_LOCK); dataset=_verify_dataset_lock(); prereg=load_json(PREREG)
    if _canonical_lock_hash(run,"run_lock_sha256")!=run["run_lock_sha256"]: raise RuntimeError("run lock self-hash mismatch")
    expected={
        "dataset_lock_sha256":dataset["dataset_lock_sha256"],"preregistration_sha256":prereg["canonical_preregistration_sha256"],
        "t0_source_sha256":file_hash(BASELINE_SOURCE),"t1_mechanism_source_sha256":file_hash(MECHANISM_SOURCE),"evaluation_source_sha256":file_hash(EVALUATOR_SOURCE),
    }
    if any(run[k]!=v for k,v in expected.items()): raise RuntimeError("confirmatory source/dataset hash mismatch")
    if not run["CONFIRMATORY_RUN_NOT_YET_EXECUTED"] or run["semantic_run_count"]!=0: raise RuntimeError("run lock is not pre-execution")
    return run


def run_once() -> dict:
    if RUN_STATE.exists() or RESULTS.exists(): raise RuntimeError("C1 semantic confirmatory run already started/completed; refusing second run")
    _verify_run_lock()
    write_json(RUN_STATE,{"version":C1_VERSION,"status":"STARTED","semantic_run_count":1})
    result=evaluate(); write_json(RESULTS,result)
    write_json(RUN_STATE,{"version":C1_VERSION,"status":"COMPLETED","semantic_run_count":1,"results_sha256":semantic_hash(result)})
    dataset=load_json(DATASET_LOCK)
    summary={
        "version":C1_VERSION,"decision":result["decision"],"confirmatory_status":result["confirmatory_status"],"semantic_run_count":1,
        "canonical_preregistration_sha256":load_json(PREREG)["canonical_preregistration_sha256"],"dataset_lock_sha256":dataset["dataset_lock_sha256"],
        "run_lock_sha256":load_json(RUN_LOCK)["run_lock_sha256"],"primary_confirmatory_rule":all(v for k,v in result["confirmatory_gates"].items() if k!="observable_nonoccurrence_specificity"),
        "specificity_rule":result["confirmatory_gates"]["observable_nonoccurrence_specificity"],"delta_t1_minus_t0":result["delta_t1_minus_t0"],
        "t0":result["treatments"]["T0"]["metrics"],"t1":result["treatments"]["T1"]["metrics"],
    }
    write_json(SUMMARY,summary); return result


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("phase",choices=["preregister","generate","run-lock","run"]); args=parser.parse_args()
    if args.phase=="preregister": result=preregister()
    elif args.phase=="generate": result=generate_and_lock()
    elif args.phase=="run-lock": result=create_run_lock()
    else: result=run_once()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__=="__main__": main()
