"""Independent static verification of CLRM2-A Training Lock.

No CLRM-2 scientific runner is imported or executed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import platform
import re
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Any

import torch

ROOT=Path(__file__).resolve().parents[2]
LOCK=ROOT/"docs/research/continual-loss-response/CLRM2_TRAINING_LOCK.json"
PROTOCOL=ROOT/"docs/research/continual-loss-response/clrm2-predictive-discovery-protocol.md"
MANIFEST=ROOT/"docs/research/continual-loss-response/CLRM2_DISCOVERY_SEED_MANIFEST.json"
RUNNER=ROOT/"experiments/clrm/clrm2_predictive_discovery.py"
TESTS=ROOT/"tests/test_clrm2_predictive_discovery.py"
PREFLIGHT_WF=ROOT/".github/workflows/clrm2-zero-science-preflight.yml"
PREFLIGHT_QA=ROOT/"docs/research/continual-loss-response/CLRM2_PREFLIGHT_QA.md"
FEATURE_SRC=ROOT/"experiments/kernel_cl/kcl656_boundary_health_signal.py"
HIST_OBS=ROOT/"experiments/kernel_cl/kcl6592_regime_predictability.py"
CLRM1_RUNNER=ROOT/"experiments/clrm/clrm1_loss_response_support.py"
MSA1_RUNNER=ROOT/"experiments/msa/msa1_endpoint_adequacy.py"
MSA3_RUNNER=ROOT/"experiments/msa/msa3_independent_replication.py"

EXPECTED_LOCK_SHA="e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5"
EXPECTED_PROTOCOL_BLOB="9c35a9b8648ae2581a9f111680364dc75ffcf8a8"
EXPECTED_MANIFEST_BLOB="c7600a8963a15b03a1d3c27a4134e0a724088519"
EXPECTED_RUNNER_BLOB="2b802f0ff10508d573e0c8ae61b6337ef80a1807"
EXPECTED_TEST_BLOB="e9dcd706aa72d09de69523323675601d7ae1d28a"
EXPECTED_PREFLIGHT_WF_BLOB="9e439da9ffc6e865961fd67e3dc738a8100137c6"
EXPECTED_FEATURE_BLOB="cd1ce639435df7f94499d2a22c3087334bbcadc5"
EXPECTED_HIST_OBS_BLOB="16e48196d09a661c145ee5efdd264d2abd4d6f96"
EXPECTED_CLRM1_BLOB="deb0c30af6a981705587637706e98ddc1cbc1ceb"
EXPECTED_PREFLIGHT_JSON_SHA="d790f55f0e599bcdb4f774d154dff2cf05ee7a045320b331e4dcf0ddf73c7140"

EXPECTED_ALL_HASH="05b7d1a077b3b4a152882fc42e67f6189d3f66d55ff0dc50b859ffd022480374"
EXPECTED_TRAIN_HASH="bc7f7dd941a5ec280156e9cbfc3f1501565213db7efa3b940dd4d189891b93e8"
EXPECTED_VAL_HASH="a2287c490acf6c8a94cff56be1a5eb4aaa0115fce26675312ac590d5bfe6ee96"
PHRASE="MindForge|CLRM-2|predictive-discovery|v1"

OBS11=(
"STAGE_2","STAGE_3","H1_M1_RMS","H2_SQRT_M2_RMS",
"H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS","H4_TASK_DRIFT_RELATIVE_L2",
"H5_PRESSURE_TO_DRIFT_RATIO","H6_DRIFT_PRESSURE_COSINE",
"H7_PRIOR_MEAN_ACCURACY","H8_PRIOR_WORST_ACCURACY","H9_CURRENT_TASK_LOSS",
)
TARGETS=(
"A.current_loss","A.prior_mean_loss","B.current_loss","B.prior_mean_loss",
"C.current_loss","C.prior_mean_loss",
)
SUBSTRATE={
"experiments/kernel_cl/kcl1_substrate.py":"4303dd544e0bdb935c499abedc62aa095bc56674",
"experiments/kernel_cl/kcl6_long_horizon.py":"33a743d62b5a83286c8945ffc0f473ae66fe50c0",
"experiments/kernel_cl/kcl61_weighted_replay_ab.py":"9a2ea8435bc92d65af7044b5351d06adc6cc2d44",
"experiments/kernel_cl/kcl63_fuzzy_decay_abcd.py":"cb6cf442d9d6a01c6cec173ecd73771fc6ba30c7",
"experiments/kernel_cl/kcl65_specificity_ab.py":"88aa11fea6e8474c323c02491c0b85a91722c686",
"experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py":"7119b9520f50de53a42313f7c7173c8d5daec2f1",
"mindforge/config.py":"54ab270a25edd962e62360e14736b28f52a4fbcd",
"mindforge/model.py":"3f6b8f1f411d7a3ba061d4bca10cd0002ae91594",
}
PROTECTED={13635,13837,14039,14241,14443,14645,14847,15049,15251,15453,15655,15857,16059,16261,16463,16665,16867,17069,17271,17473}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mh(xs): return hashlib.sha256(",".join(str(int(x)) for x in xs).encode()).hexdigest()
def git(*a): return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()
def blob(path): return git("hash-object",str(path.relative_to(ROOT)))

def assigns(path):
    t=ast.parse(path.read_text())
    o={}
    for n in t.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:o[n.targets[0].id]=ast.literal_eval(n.value)
            except Exception:pass
    return o

def regen():
    out=[]; seen=set(); i=0
    while len(out)<240:
        d=hashlib.sha256(f"{PHRASE}|{i}".encode()).digest()
        x=30_000_000+(int.from_bytes(d[:8],"big")%10_000_000)
        if x not in seen: out.append(x); seen.add(x)
        i+=1
    return tuple(out)

def historical_kcl():
    paths=[ROOT/"Lineage.md"]
    for base in (ROOT/"docs/research/kernel-continual-learning",ROOT/"experiments/kernel_cl"):
        if base.exists(): paths.extend(p for p in base.rglob("*") if p.is_file())
    out=set()
    for p in paths:
        txt=p.read_text(encoding="utf-8",errors="replace")
        for line in txt.splitlines():
            if "seed" in line.lower():
                out.update(int(x) for x in re.findall(r"\b\d{4,8}\b",line))
    return out

def feature_signature_ok():
    t=ast.parse(FEATURE_SRC.read_text())
    fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=="extract_boundary_features")
    args=[a.arg for a in fn.args.args+fn.args.kwonlyargs]
    return "next_task" not in args and all(x in args for x in ["model","optimizer","pre_task_model_state","observed_tasks","current_task","boundary_index"])

def execution_workflows():
    hits=[]
    for p in (ROOT/".github/workflows").glob("*"):
        if p.is_file():
            txt=p.read_text(encoding="utf-8",errors="replace")
            if "clrm2_predictive_discovery.py" in txt and ("--phase collect-train" in txt or "--phase collect-val" in txt):
                hits.append(str(p.relative_to(ROOT)))
    return sorted(hits)

def verifier_safety():
    t=ast.parse(Path(__file__).read_text())
    imp=False; call=False; launch=False
    forbidden={"preflight","build_discovery_records","collect-train","fit_candidate_package","adjudicate_validation"}
    for n in ast.walk(t):
        if isinstance(n,ast.Import):
            imp |= any(a.name.startswith("experiments.clrm.clrm2") for a in n.names)
        elif isinstance(n,ast.ImportFrom):
            imp |= bool(n.module and n.module.startswith("experiments.clrm.clrm2"))
        elif isinstance(n,ast.Call):
            f=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else ""
            call |= f in forbidden
            if f in {"run","call","check_call","check_output","Popen"}:
                lits=[x.value for x in ast.walk(n) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
                if any("clrm2_predictive_discovery.py" in x for x in lits):
                    launch=True
    return {"no_import_clrm2":not imp,"no_scientific_call":not call,"no_runner_launch":not launch}

def verify()->dict[str,Any]:
    lock=json.loads(LOCK.read_text())
    man=json.loads(MANIFEST.read_text())
    ra=assigns(RUNNER); ha=assigns(HIST_OBS)
    m1=assigns(MSA1_RUNNER); m3=assigns(MSA3_RUNNER); c1=assigns(CLRM1_RUNNER)
    train=tuple(man["dtrain"]["seeds"]); val=tuple(man["dval"]["seeds"]); allseeds=train+val
    fresh=set(allseeds); hist=historical_kcl()
    spent={
      "ACO-1":tuple(m1["SPENT_ACO_SEEDS"]),
      "CPRM-1":tuple(m1["SPENT_CPRM_SEEDS"]),
      "MSA-1":tuple(m1["FRESH_SEEDS"]),
      "MSA-3":tuple(m3["FRESH_SEEDS"]),
      "CLRM-1":tuple(c1["FRESH_SEEDS"]),
    }
    col={"historical_kcl":sorted(fresh&hist),"protected_kcl":sorted(fresh&PROTECTED)}
    checks={}
    checks["lock_hash"]=sha(LOCK)==EXPECTED_LOCK_SHA
    checks["protocol_blob"]=blob(PROTOCOL)==EXPECTED_PROTOCOL_BLOB==lock["protocol"]["git_blob_sha"]
    checks["manifest_blob"]=blob(MANIFEST)==EXPECTED_MANIFEST_BLOB==lock["discovery_manifest"]["git_blob_sha"]
    checks["runner_blob"]=blob(RUNNER)==EXPECTED_RUNNER_BLOB==lock["implementation"]["runner_git_blob_sha"]
    checks["test_blob"]=blob(TESTS)==EXPECTED_TEST_BLOB==lock["implementation"]["test_git_blob_sha"]
    checks["preflight_workflow_blob"]=blob(PREFLIGHT_WF)==EXPECTED_PREFLIGHT_WF_BLOB==lock["implementation"]["preflight_workflow_git_blob_sha"]
    checks["feature_blobs"]=blob(FEATURE_SRC)==EXPECTED_FEATURE_BLOB and blob(HIST_OBS)==EXPECTED_HIST_OBS_BLOB and blob(CLRM1_RUNNER)==EXPECTED_CLRM1_BLOB
    checks["substrate_blobs"]=lock["substrate"]["git_blobs"]==SUBSTRATE and all(blob(ROOT/p)==h for p,h in SUBSTRATE.items())
    checks["feature_preboundary_signature"]=feature_signature_ok()
    checks["obs11_exact"]=tuple(ra["OBS11"])==OBS11 and tuple(ha["PRIMARY_FEATURES"])==OBS11 and lock["feature_contract"]["exact_order"]==list(OBS11)
    checks["targets_exact"]=tuple(ra["TARGETS"])==TARGETS and lock["target_contract"]["exact_six_channels"]==list(TARGETS)
    checks["manifest_counts"]=len(train)==160 and len(val)==80 and len(fresh)==240 and set(train).isdisjoint(val)
    checks["manifest_regen"]=regen()==allseeds
    checks["manifest_hashes"]=mh(allseeds)==EXPECTED_ALL_HASH and mh(train)==EXPECTED_TRAIN_HASH and mh(val)==EXPECTED_VAL_HASH
    checks["manifest_file_hashes"]=man["all_sha256"]==EXPECTED_ALL_HASH and man["dtrain"]["sha256"]==EXPECTED_TRAIN_HASH and man["dval"]["sha256"]==EXPECTED_VAL_HASH
    checks["historical_disjoint"]=not col["historical_kcl"]
    checks["protected_disjoint"]=not col["protected_kcl"]
    for name,seq in spent.items():
        col[name]=sorted(fresh&set(seq))
        checks[f"{name}_disjoint"]=not col[name]
        checks[f"{name}_hash"]=mh(seq)==lock["exclusions"]["spent_manifest_sha256"][name]
    checks["candidate_grid"]=tuple(ra["KRR_GAMMAS"])==(0.02,0.10,0.50) and tuple(ra["KRR_LAMBDAS"])==(1e-4,1e-2,1.0)
    checks["baseline_grid"]=tuple(ra["B2_LAMBDAS"])==(1e-6,1e-4,1e-2,1.0,100.0)
    checks["cv_exact"]=ra["CV_FOLDS"]==5 and ra["CV_PHRASE"]=="CLRM2-CV-v1"
    checks["bootstrap_exact"]=ra["BOOTSTRAP_RESAMPLES"]==20000 and ra["BOOTSTRAP_SEED"]==72002
    checks["phase_A_only"]=lock["phase"]=="A_DTRAIN_ONLY" and lock["discovery_manifest"]["dval"]["sealed"] is True and lock["discovery_manifest"]["dval"]["execution_authorized"] is False
    checks["validation_transition"]=lock["validation_transition"]["requires_separate_validation_lock"] is True and lock["validation_transition"]["requires_independent_validation_lock_verification"] is True
    rt=lock["runtime"]
    checks["runtime"]=platform.machine()==rt["architecture"]=="x86_64" and platform.python_version()==rt["python"]=="3.12.14" and version("pip")==rt["pip"]=="26.2.1" and version("numpy")==rt["numpy"]=="2.3.3" and version("pytest")==rt["pytest"]=="8.4.2" and torch.__version__==rt["torch"]=="2.10.0+cpu"
    pq=PREFLIGHT_QA.read_text()
    checks["preflight_closure"]="CLRM2_ZERO_SCIENCE_PREFLIGHT_PASS" in pq and EXPECTED_LOCK_SHA in pq and EXPECTED_PREFLIGHT_JSON_SHA in pq
    checks["dtrain_absent"]=not (ROOT/lock["outputs"]["dtrain"]).exists()
    checks["candidate_absent"]=not (ROOT/lock["outputs"]["candidate"]).exists()
    checks["dval_absent"]=not (ROOT/lock["outputs"]["dval"]).exists()
    checks["formal_absent"]=not (ROOT/lock["outputs"]["formal"]).exists()
    hits=execution_workflows()
    checks["fresh_execution_workflows_absent"]=not hits
    safety=verifier_safety(); checks["verifier_independent"]=all(safety.values())
    ok=all(checks.values())
    return {
      "schema":"CLRM2-TRAINING-LOCK-VERIFICATION-v1","program":"CLRM-2","phase":"A_DTRAIN_ONLY",
      "status":"PASS" if ok else "FAIL",
      "verdict":"CLRM2_TRAINING_LOCK_VERIFICATION_PASS" if ok else "CLRM2_TRAINING_LOCK_VERIFICATION_FAIL",
      "head_commit":git("rev-parse","HEAD"),"lock_sha256":sha(LOCK),"checks":checks,
      "collisions":col,"execution_workflow_hits":hits,"static_safety":safety,
      "fresh_seed_execution_attempted":False,"fresh_predictor_fitting_performed":False,
      "dval_outcomes_generated":False,"scientific_outcome_generated":False,
    }

def main():
    out=ROOT/"artifacts/clrm2_training_lock_verification.json"; out.parent.mkdir(parents=True,exist_ok=True)
    r=verify(); out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    return 0 if r["status"]=="PASS" else 2

if __name__=="__main__": raise SystemExit(main())
