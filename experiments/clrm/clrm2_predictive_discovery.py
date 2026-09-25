"""CLRM-2 predictive discovery.

Fresh scientific fitting is blocked until independent CLRM2-A training-lock
verification. Sealed validation is separately blocked until a later CLRM2-B
validation-lock verification after the D-train candidate package is frozen.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config, build_model, optimizer_for, train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.clrm import clrm1_loss_response_support as c1

PROGRAM = "CLRM-2"
PROTOCOL = Path("docs/research/continual-loss-response/clrm2-predictive-discovery-protocol.md")
SEED_MANIFEST = Path("docs/research/continual-loss-response/CLRM2_DISCOVERY_SEED_MANIFEST.json")
TRAINING_LOCK = Path("docs/research/continual-loss-response/CLRM2_TRAINING_LOCK.json")
TRAINING_VERIFICATION = Path("docs/research/continual-loss-response/CLRM2_TRAINING_LOCK_VERIFICATION.md")
VALIDATION_LOCK = Path("docs/research/continual-loss-response/CLRM2_VALIDATION_LOCK.json")
VALIDATION_VERIFICATION = Path("docs/research/continual-loss-response/CLRM2_VALIDATION_LOCK_VERIFICATION.md")

DTRAIN_RECORDS = Path("experiments/clrm/results/clrm2_dtrain.json")
CANDIDATE_PACKAGE = Path("experiments/clrm/results/CLRM2_DISCOVERY_CANDIDATE.json")
DVAL_RECORDS = Path("experiments/clrm/results/clrm2_dval.json")
FORMAL_RESULT = Path("experiments/clrm/results/CLRM2_FORMAL_RESULT.json")

GENERATION_PHRASE = "MindForge|CLRM-2|predictive-discovery|v1"
ALL_SHA256 = "05b7d1a077b3b4a152882fc42e67f6189d3f66d55ff0dc50b859ffd022480374"
DTRAIN_SHA256 = "bc7f7dd941a5ec280156e9cbfc3f1501565213db7efa3b940dd4d189891b93e8"
DVAL_SHA256 = "a2287c490acf6c8a94cff56be1a5eb4aaa0115fce26675312ac590d5bfe6ee96"

DTRAIN_SEEDS = (33399510,37262210,36103596,31258121,31951464,36717679,38890782,32910194,34733123,34363630,33545483,32402319,32404953,33342990,35841920,33101003,31040538,34346871,34244567,38485763,34495653,33603701,33996396,30871357,32573775,32442578,30911759,32105063,33685043,34953394,36249987,36264295,35562089,30608391,35160781,31261338,32615077,31964072,30065235,36585881,31004775,36094827,39532591,36271578,32259319,39802010,35244922,34474644,31433237,38982915,39666502,38021427,35064494,34737593,32552261,30208043,31047325,31808790,39805365,34820046,34776398,38197086,30822997,37854491,38704911,38193061,31928444,39046598,35692761,36339344,35380471,35705561,39254574,30153195,39400051,33151164,38749323,30695286,33559241,36187530,35342592,31891834,32827786,34990923,32509271,33150888,39375347,36988342,39945032,35673006,35963726,31289642,34422466,36771225,36429783,31129004,34097678,30314270,39836618,39371175,34008214,30194107,30656461,35526266,39013659,30709292,38948548,33826659,35470140,32326386,35225787,32893873,38572495,33686815,36285637,31499002,37337664,32375151,31246636,39724881,33088181,37829469,34236847,35425622,38922682,32881334,33579679,30166819,35754478,38650864,34530089,39784742,35690302,33040126,35305491,39764796,36062359,38947269,34028587,30190917,32558396,36149313,31469753,32387203,32811528,34922699,32141815,35428299,39905514,34621003,33860272,39669643,31430252,35647600,32966943,32124020,32454401,39482019,30862362,36572733,)
DVAL_SEEDS = (38586846,33259692,36699610,32768986,38791450,33391014,33741513,31477657,35310515,37153987,30548632,34890017,39460539,36441436,30775610,32356234,33112091,32827887,30859532,36244137,30993119,32977476,33023532,37879705,33027791,30942424,36134089,35342652,39509693,31734873,34305287,36238795,39590462,30831627,37650983,35536842,36156242,30780706,36940484,38272770,36841946,33198723,32767657,33049167,31294462,36417472,35261236,35334506,31650056,38656059,33066316,34758916,30231773,38129532,35815192,39328047,36793969,38704719,37019605,37980392,39071926,39058675,36438143,31789420,34989884,33116635,30648318,30090754,36691356,38714879,39172567,38393098,36189500,34805596,30245209,39293261,39083241,34630795,34531288,34109380,)
ALL_SEEDS = DTRAIN_SEEDS + DVAL_SEEDS

OBS11 = (
    "STAGE_2",
    "STAGE_3",
    "H1_M1_RMS",
    "H2_SQRT_M2_RMS",
    "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS",
    "H4_TASK_DRIFT_RELATIVE_L2",
    "H5_PRESSURE_TO_DRIFT_RATIO",
    "H6_DRIFT_PRESSURE_COSINE",
    "H7_PRIOR_MEAN_ACCURACY",
    "H8_PRIOR_WORST_ACCURACY",
    "H9_CURRENT_TASK_LOSS",
)

TARGETS = (
    "A.current_loss",
    "A.prior_mean_loss",
    "B.current_loss",
    "B.prior_mean_loss",
    "C.current_loss",
    "C.prior_mean_loss",
)

POLICY_MAP = {
    "A": "A_CARRY_ALL",
    "B": "B_RESET_ALL",
    "C": "C_CARRY_STEP_RESET_MOMENTS",
}

KRR_GAMMAS = (0.02, 0.10, 0.50)
KRR_LAMBDAS = (1e-4, 1e-2, 1.0)
B2_LAMBDAS = (1e-6, 1e-4, 1e-2, 1.0, 100.0)
CV_FOLDS = 5
CV_PHRASE = "CLRM2-CV-v1"
BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 72002
EPS = 1e-12

SPENT_HASHES = {
    "ACO-1":"9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91",
    "CPRM-1":"d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3",
    "MSA-1":"e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347",
    "MSA-3":"5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8",
    "CLRM-1":"3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6",
}

PROTECTED_KCL = (
    13635,13837,14039,14241,14443,14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,16665,16867,17069,17271,17473,
)

SUBSTRATE_BLOBS = c1.SUBSTRATE_BLOBS
FEATURE_EXTRACTOR_BLOB = "cd1ce639435df7f94499d2a22c3087334bbcadc5"
HISTORICAL_OBS11_SOURCE_BLOB = "16e48196d09a661c145ee5efdd264d2abd4d6f96"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(values: Iterable[int]) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def git_blob(path: str | Path) -> str:
    return git("hash-object", str(path))


def regenerate_seeds() -> tuple[int, ...]:
    out: list[int] = []
    seen: set[int] = set()
    i = 0
    while len(out) < 240:
        d = hashlib.sha256(f"{GENERATION_PHRASE}|{i}".encode()).digest()
        x = 30_000_000 + (int.from_bytes(d[:8], "big") % 10_000_000)
        if x not in seen:
            out.append(x)
            seen.add(x)
        i += 1
    return tuple(out)


def _historical_kcl_seeds() -> set[int]:
    paths=[Path("Lineage.md")]
    for base in (Path("docs/research/kernel-continual-learning"),Path("experiments/kernel_cl")):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out=set()
    for p in paths:
        txt=p.read_text(encoding="utf-8",errors="replace")
        for line in txt.splitlines():
            if "seed" in line.lower():
                out.update(int(x) for x in re.findall(r"\b\d{4,8}\b",line))
    return out


def validate_manifests() -> dict[str, Any]:
    m=json.loads(SEED_MANIFEST.read_text(encoding="utf-8"))
    all_set=set(ALL_SEEDS)
    historical=_historical_kcl_seeds()
    checks={
        "counts":len(DTRAIN_SEEDS)==160 and len(DVAL_SEEDS)==80 and len(ALL_SEEDS)==240,
        "unique":len(all_set)==240,
        "train_val_disjoint":set(DTRAIN_SEEDS).isdisjoint(set(DVAL_SEEDS)),
        "regeneration":regenerate_seeds()==ALL_SEEDS,
        "all_hash":manifest_hash(ALL_SEEDS)==ALL_SHA256==m["all_sha256"],
        "train_hash":manifest_hash(DTRAIN_SEEDS)==DTRAIN_SHA256==m["dtrain"]["sha256"],
        "val_hash":manifest_hash(DVAL_SEEDS)==DVAL_SHA256==m["dval"]["sha256"],
        "file_train_sequence":tuple(m["dtrain"]["seeds"])==DTRAIN_SEEDS,
        "file_val_sequence":tuple(m["dval"]["seeds"])==DVAL_SEEDS,
        "historical_kcl_disjoint":all_set.isdisjoint(historical),
        "protected_disjoint":all_set.isdisjoint(set(PROTECTED_KCL)),
        "clrm1_disjoint":all_set.isdisjoint(set(c1.FRESH_SEEDS)),
    }
    # Other spent cohorts are checked by their frozen source/hashes in the lock verifier.
    return {
        "valid":all(checks.values()),
        "checks":checks,
        "collisions":{
            "historical_kcl":sorted(all_set & historical),
            "protected_kcl":sorted(all_set & set(PROTECTED_KCL)),
            "clrm1":sorted(all_set & set(c1.FRESH_SEEDS)),
        },
    }


def fold_for_seed(seed:int)->int:
    d=hashlib.sha256(f"{CV_PHRASE}|{int(seed)}".encode()).digest()
    return int.from_bytes(d[:8],"big") % CV_FOLDS


def extract_obs11(global_features:dict[str,float],boundary_index:int)->dict[str,float]:
    out={
        "STAGE_2":1.0 if boundary_index==2 else 0.0,
        "STAGE_3":1.0 if boundary_index==3 else 0.0,
    }
    for name in OBS11[2:]:
        out[name]=float(global_features[name])
    return out


def build_discovery_records(seed:int)->list[dict[str,Any]]:
    cfg=KCL1Config()
    tasks=task_sequence(cfg)
    model=build_model(cfg,seed)
    opt=optimizer_for(model,cfg)
    pre_task_model_state=copy.deepcopy(model.state_dict())
    train_stage(model,opt,tasks[0][1],steps=250,batch_size=16,seed=seed+101)
    memories=[k63.ExactMemory.from_task(tasks[0][1])]
    observed=[tasks[0]]
    rows=[]
    for boundary in (1,2,3):
        current_task=observed[-1]
        gf=k656.extract_boundary_features(
            model=model,optimizer=opt,pre_task_model_state=pre_task_model_state,
            observed_tasks=observed,current_task=current_task,boundary_index=boundary,
        )
        features=extract_obs11(gf,boundary)
        next_task=tasks[boundary]
        resp=c1.run_response_counterfactual(
            model=model,optimizer=opt,memories=memories,observed_tasks=observed,
            next_task=next_task,seed=seed,next_stage=boundary+1,cfg=cfg,
        )
        targets={}
        for short,policy in POLICY_MAP.items():
            targets[f"{short}.current_loss"]=float(resp["responses"][policy]["current_loss"])
            targets[f"{short}.prior_mean_loss"]=float(resp["responses"][policy]["prior_mean_loss"])
        rows.append({
            "seed":int(seed),
            "boundary_index":boundary,
            "features":features,
            "targets":targets,
            "accuracy_sentinel":{
                p:resp["responses"][p]["accuracy_sentinel"] for p in c1.POLICIES
            },
            "integrity":resp["integrity"],
        })
        pre_task_model_state=copy.deepcopy(model.state_dict())
        model=resp["_reference_model"]
        opt=resp["_reference_optimizer"]
        memories=resp["_next_memories"]
        observed=tasks[:boundary+1]
    return rows


def arrays(records:list[dict[str,Any]]):
    x=np.asarray([[float(r["features"][n]) for n in OBS11] for r in records],dtype=np.float64)
    y=np.asarray([[float(r["targets"][n]) for n in TARGETS] for r in records],dtype=np.float64)
    seeds=np.asarray([int(r["seed"]) for r in records],dtype=np.int64)
    stages=np.asarray([int(r["boundary_index"]) for r in records],dtype=np.int64)
    return x,y,seeds,stages


def robust_scales(y:np.ndarray)->np.ndarray:
    return np.maximum(np.quantile(y,0.90,axis=0)-np.quantile(y,0.10,axis=0),EPS)


def standardizer(x:np.ndarray):
    mean=x.mean(axis=0)
    std=np.maximum(x.std(axis=0,ddof=0),EPS)
    return mean,std


def sx(x,mean,std):
    return (x-mean)/std


def rbf_kernel(x:np.ndarray,z:np.ndarray,gamma:float)->np.ndarray:
    xx=np.sum(x*x,axis=1)[:,None]
    zz=np.sum(z*z,axis=1)[None,:]
    d2=np.maximum(xx+zz-2*x@z.T,0.0)
    return np.exp(-gamma*d2)


def fit_krr(x:np.ndarray,y:np.ndarray,gamma:float,lam:float)->dict[str,Any]:
    mean,std=standardizer(x)
    xs=sx(x,mean,std)
    k=rbf_kernel(xs,xs,gamma)
    alpha=np.linalg.solve(k+lam*np.eye(len(xs),dtype=np.float64),y)
    return {"x_mean":mean,"x_std":std,"x_train":xs,"alpha":alpha,"gamma":gamma,"lambda":lam}


def pred_krr(model:dict[str,Any],x:np.ndarray)->np.ndarray:
    xs=sx(x,model["x_mean"],model["x_std"])
    return rbf_kernel(xs,model["x_train"],float(model["gamma"])) @ model["alpha"]


def fit_ridge(x:np.ndarray,y:np.ndarray,lam:float)->dict[str,Any]:
    mean,std=standardizer(x)
    xs=sx(x,mean,std)
    xa=np.column_stack([xs,np.ones(len(xs))])
    pen=np.eye(xa.shape[1]); pen[-1,-1]=0.0
    coef=np.linalg.solve(xa.T@xa+lam*pen,xa.T@y)
    return {"x_mean":mean,"x_std":std,"coef":coef,"lambda":lam}


def pred_ridge(model:dict[str,Any],x:np.ndarray)->np.ndarray:
    xs=sx(x,model["x_mean"],model["x_std"])
    xa=np.column_stack([xs,np.ones(len(xs))])
    return xa @ model["coef"]


def cv_masks(seeds:np.ndarray):
    fs=np.asarray([fold_for_seed(int(s)) for s in seeds],dtype=np.int64)
    if set(fs.tolist()) != set(range(CV_FOLDS)):
        raise RuntimeError("CLRM2 CV has empty fold")
    return fs


def macro_scaled_mae(y:np.ndarray,p:np.ndarray,scales:np.ndarray)->float:
    return float(np.mean(np.mean(np.abs(y-p),axis=0)/scales))


def candidate_cv(records:list[dict[str,Any]])->dict[str,Any]:
    x,y,seeds,_=arrays(records)
    scales=robust_scales(y)
    folds=cv_masks(seeds)
    scored=[]
    for gamma in KRR_GAMMAS:
        for lam in KRR_LAMBDAS:
            oof=np.zeros_like(y)
            for f in range(CV_FOLDS):
                tr=folds!=f; te=folds==f
                m=fit_krr(x[tr],y[tr],gamma,lam)
                oof[te]=pred_krr(m,x[te])
            score=macro_scaled_mae(y,oof,scales)
            scored.append((score,gamma,lam,oof))
    scored.sort(key=lambda t:(t[0],t[1],t[2]))
    score,gamma,lam,oof=scored[0]
    final=fit_krr(x,y,gamma,lam)
    return {
        "selected_gamma":gamma,"selected_lambda":lam,"cv_score":score,
        "cv_channel_mae":np.mean(np.abs(y-oof),axis=0),
        "final":final,
    }


def baseline_oof(records:list[dict[str,Any]])->dict[str,Any]:
    x,y,seeds,stages=arrays(records)
    scales=robust_scales(y)
    folds=cv_masks(seeds)
    preds={name:np.zeros_like(y) for name in ("B0","B1")}
    for f in range(CV_FOLDS):
        tr=folds!=f; te=folds==f
        preds["B0"][te]=y[tr].mean(axis=0)
        for stage in (1,2,3):
            mask=te & (stages==stage)
            preds["B1"][mask]=y[tr & (stages==stage)].mean(axis=0)

    b2_by_lambda={}
    for lam in B2_LAMBDAS:
        oof=np.zeros_like(y)
        for f in range(CV_FOLDS):
            tr=folds!=f; te=folds==f
            # fit all outputs; per-channel selection happens after OOF predictions exist
            m=fit_ridge(x[tr],y[tr],lam)
            oof[te]=pred_ridge(m,x[te])
        b2_by_lambda[lam]=oof
    chosen=[]
    b2=np.zeros_like(y)
    for j in range(y.shape[1]):
        ranked=sorted(
            (float(np.mean(np.abs(y[:,j]-p[:,j]))),lam)
            for lam,p in b2_by_lambda.items()
        )
        _,lam=ranked[0]
        chosen.append(lam)
        b2[:,j]=b2_by_lambda[lam][:,j]
    preds["B2"]=b2

    scores={k:macro_scaled_mae(y,p,scales) for k,p in preds.items()}
    preference={"B2":0,"B1":1,"B0":2}
    strongest=sorted(scores,key=lambda k:(scores[k],preference[k]))[0]
    return {
        "scores":scores,
        "strongest":strongest,
        "b2_lambdas":chosen,
        "oof_predictions":preds,
    }


def fit_baselines(records:list[dict[str,Any]],binfo:dict[str,Any])->dict[str,Any]:
    x,y,_,stages=arrays(records)
    b0={"means":y.mean(axis=0)}
    b1={"means_by_stage":{s:y[stages==s].mean(axis=0) for s in (1,2,3)}}
    b2_models=[]
    for j,lam in enumerate(binfo["b2_lambdas"]):
        b2_models.append(fit_ridge(x,y[:,[j]],float(lam)))
    return {"B0":b0,"B1":b1,"B2":{"channels":b2_models}}


def predict_baseline(package:dict[str,Any],family:str,records:list[dict[str,Any]])->np.ndarray:
    x,y,_,stages=arrays(records)
    if family=="B0":
        return np.tile(package["B0"]["means"],(len(records),1))
    if family=="B1":
        out=np.zeros_like(y)
        for s in (1,2,3):
            out[stages==s]=package["B1"]["means_by_stage"][s]
        return out
    out=np.zeros_like(y)
    for j,m in enumerate(package["B2"]["channels"]):
        out[:,j]=pred_ridge(m,x).reshape(-1)
    return out


def jsonable(x):
    if isinstance(x,np.ndarray): return x.tolist()
    if isinstance(x,np.generic): return x.item()
    if isinstance(x,dict): return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [jsonable(v) for v in x]
    return x


def fit_candidate_package(records:list[dict[str,Any]])->dict[str,Any]:
    if set(int(r["seed"]) for r in records)!=set(DTRAIN_SEEDS) or len(records)!=480:
        raise RuntimeError("D-train population mismatch")
    cand=candidate_cv(records)
    binfo=baseline_oof(records)
    baselines=fit_baselines(records,binfo)
    return jsonable({
        "schema":"CLRM2-DISCOVERY-CANDIDATE-v1",
        "program":PROGRAM,
        "dtrain_seed_sha256":DTRAIN_SHA256,
        "representation":"OBS11-v1",
        "feature_names":OBS11,
        "target_names":TARGETS,
        "candidate_family":"RBF-KRR-v1",
        "candidate":{
            "gamma":cand["selected_gamma"],
            "lambda":cand["selected_lambda"],
            "cv_score":cand["cv_score"],
            "cv_channel_mae":cand["cv_channel_mae"],
            "model":cand["final"],
        },
        "baseline_selection":{
            "family_scores":binfo["scores"],
            "strongest_baseline":binfo["strongest"],
            "b2_lambdas":binfo["b2_lambdas"],
        },
        "baselines":baselines,
        "dval_used":False,
    })


def package_candidate_predict(pkg:dict[str,Any],records:list[dict[str,Any]])->np.ndarray:
    x,_,_,_=arrays(records)
    m=pkg["candidate"]["model"]
    mm={k:np.asarray(v,dtype=np.float64) if k in {"x_mean","x_std","x_train","alpha"} else v for k,v in m.items()}
    return pred_krr(mm,x)


def package_baseline_predict(pkg:dict[str,Any],records:list[dict[str,Any]])->np.ndarray:
    # rebuild arrays inside serialized baseline models
    bp=pkg["baselines"]
    conv={"B0":{"means":np.asarray(bp["B0"]["means"],dtype=np.float64)},
          "B1":{"means_by_stage":{int(k):np.asarray(v,dtype=np.float64) for k,v in bp["B1"]["means_by_stage"].items()}},
          "B2":{"channels":[]}}
    for m in bp["B2"]["channels"]:
        conv["B2"]["channels"].append({
            "x_mean":np.asarray(m["x_mean"],dtype=np.float64),
            "x_std":np.asarray(m["x_std"],dtype=np.float64),
            "coef":np.asarray(m["coef"],dtype=np.float64),
            "lambda":m["lambda"],
        })
    return predict_baseline(conv,pkg["baseline_selection"]["strongest_baseline"],records)


def calibration(y:np.ndarray,p:np.ndarray,bmae:np.ndarray)->dict[str,Any]:
    out={}
    all_ok=True
    for j,name in enumerate(TARGETS):
        x=p[:,j]; yy=y[:,j]
        var=float(np.var(x))
        if var<=EPS or float(bmae[j])<=0:
            item={"valid":False,"pass":False}
        else:
            beta=float(np.cov(x,yy,ddof=0)[0,1]/var)
            alpha=float(np.mean(yy)-beta*np.mean(x))
            ok=0.80<=beta<=1.20 and abs(alpha)/float(bmae[j])<=0.10
            item={"valid":True,"alpha":alpha,"beta":beta,
                  "normalized_abs_alpha":abs(alpha)/float(bmae[j]),"pass":ok}
        out[name]=item
        all_ok=all_ok and bool(item["pass"])
    return {"channels":out,"all_pass":all_ok}


def bootstrap_macro_ratio(records,y,pc,pb,resamples=BOOTSTRAP_RESAMPLES):
    seed_list=sorted(set(int(r["seed"]) for r in records))
    by_seed={s:np.asarray([i for i,r in enumerate(records) if int(r["seed"])==s],dtype=int) for s in seed_list}
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    vals=[]
    for _ in range(resamples):
        chosen=rng.choice(seed_list,size=len(seed_list),replace=True)
        idx=np.concatenate([by_seed[int(s)] for s in chosen])
        c=np.mean(np.abs(y[idx]-pc[idx]),axis=0)
        b=np.mean(np.abs(y[idx]-pb[idx]),axis=0)
        if np.any(b<=0):
            vals.append(math.inf)
        else:
            vals.append(float(np.mean(c/b)))
    return {"lower_2p5":float(np.quantile(vals,0.025)),
            "upper_97p5":float(np.quantile(vals,0.975))}


def adjudicate_validation(pkg:dict[str,Any],records:list[dict[str,Any]])->dict[str,Any]:
    if set(int(r["seed"]) for r in records)!=set(DVAL_SEEDS) or len(records)!=240:
        return {"status":"STOP","verdict":"STOP_INTEGRITY_OR_BASELINE","reason":"DVAL_POPULATION_MISMATCH"}
    if not all(bool(r["integrity"]["valid"]) for r in records):
        return {"status":"STOP","verdict":"STOP_INTEGRITY_OR_BASELINE","reason":"DVAL_INTEGRITY_FAILURE"}
    y=arrays(records)[1]
    pc=package_candidate_predict(pkg,records)
    pb=package_baseline_predict(pkg,records)
    cmae=np.mean(np.abs(y-pc),axis=0)
    bmae=np.mean(np.abs(y-pb),axis=0)
    if np.any(bmae<=0):
        return {"status":"STOP","verdict":"STOP_INTEGRITY_OR_BASELINE","reason":"ZERO_BASELINE_MAE"}
    ratios=cmae/bmae
    macro=float(np.mean(ratios))
    rel=1.0-macro
    boot=bootstrap_macro_ratio(records,y,pc,pb)
    superiority=bool(rel>=0.10 and boot["upper_97p5"]<1.0 and np.all(ratios<=1.05))
    cal=calibration(y,pc,bmae)
    passed=superiority and cal["all_pass"]
    return jsonable({
        "status":"PASS" if passed else "NEGATIVE",
        "verdict":"LOSS_RESPONSE_PREDICTABILITY_QUALIFIED" if passed else "LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED",
        "candidate_mae":dict(zip(TARGETS,cmae)),
        "baseline_mae":dict(zip(TARGETS,bmae)),
        "ratios":dict(zip(TARGETS,ratios)),
        "macro_ratio":macro,
        "relative_gain":rel,
        "bootstrap":boot,
        "baseline_superiority_pass":superiority,
        "calibration":cal,
        "predictor_family":"RBF-KRR-v1",
        "strongest_baseline":pkg["baseline_selection"]["strongest_baseline"],
    })


def training_authorized()->bool:
    if not TRAINING_LOCK.exists() or not TRAINING_VERIFICATION.exists(): return False
    t=TRAINING_VERIFICATION.read_text(encoding="utf-8")
    return "CLRM2_TRAINING_LOCK_VERIFICATION_PASS" in t and sha256_file(TRAINING_LOCK) in t


def validation_authorized()->bool:
    if not VALIDATION_LOCK.exists() or not VALIDATION_VERIFICATION.exists(): return False
    t=VALIDATION_VERIFICATION.read_text(encoding="utf-8")
    return "CLRM2_VALIDATION_LOCK_VERIFICATION_PASS" in t and sha256_file(VALIDATION_LOCK) in t


def historical_probe()->dict[str,Any]:
    rows=build_discovery_records(9595)
    return {
        "seed":9595,"record_count":len(rows),
        "obs11_exact":all(tuple(r["features"].keys())==OBS11 for r in rows),
        "integrity":all(bool(r["integrity"]["valid"]) for r in rows),
        "fresh_seed_used":9595 in set(ALL_SEEDS),
        "predictor_fitted":False,
    }


def preflight()->dict[str,Any]:
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    mf=validate_manifests()
    probe=historical_probe()
    checks={
        "manifest_valid":mf["valid"],
        "feature_extractor_blob":git_blob("experiments/kernel_cl/kcl656_boundary_health_signal.py")==FEATURE_EXTRACTOR_BLOB,
        "historical_obs11_blob":git_blob("experiments/kernel_cl/kcl6592_regime_predictability.py")==HISTORICAL_OBS11_SOURCE_BLOB,
        "clrm1_runner_exact":git_blob("experiments/clrm/clrm1_loss_response_support.py")=="deb0c30af6a981705587637706e98ddc1cbc1ceb",
        "historical_probe":probe["record_count"]==3 and probe["obs11_exact"] and probe["integrity"] and not probe["fresh_seed_used"],
        "dtrain_absent":not DTRAIN_RECORDS.exists(),
        "candidate_absent":not CANDIDATE_PACKAGE.exists(),
        "dval_absent":not DVAL_RECORDS.exists(),
        "formal_absent":not FORMAL_RESULT.exists(),
        "training_blocked":not training_authorized(),
        "validation_blocked":not validation_authorized(),
    }
    ok=all(checks.values())
    return {
        "schema":"CLRM2-ZERO-SCIENCE-PREFLIGHT-v1",
        "status":"PASS" if ok else "FAIL",
        "verdict":"CLRM2_ZERO_SCIENCE_PREFLIGHT_PASS" if ok else "CLRM2_ZERO_SCIENCE_PREFLIGHT_FAIL",
        "checks":checks,"manifest":mf,"historical_probe":probe,
        "fresh_seed_execution_attempted":False,
        "fresh_predictor_fitting_performed":False,
        "dval_outcomes_generated":False,
        "scientific_outcome_generated":False,
    }


def write(path:Path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(jsonable(obj),indent=2,sort_keys=True)+"\n",encoding="utf-8")


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--phase",required=True,choices=("preflight","collect-train","fit-freeze","collect-val","adjudicate"))
    p.add_argument("--input",type=Path)
    p.add_argument("--candidate",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.phase=="preflight":
        out=preflight(); write(a.output,out); return 0 if out["status"]=="PASS" else 2
    if a.phase=="collect-train":
        if not training_authorized(): raise RuntimeError("CLRM2-A training lock not verified")
        rows=[]; [rows.extend(build_discovery_records(s)) for s in DTRAIN_SEEDS]
        write(a.output,{"schema":"CLRM2-DTRAIN-v1","records":rows,"seed_sha256":DTRAIN_SHA256}); return 0
    if a.phase=="fit-freeze":
        if a.input is None: p.error("--input required")
        raw=json.loads(a.input.read_text()); write(a.output,fit_candidate_package(raw["records"])); return 0
    if a.phase=="collect-val":
        if not validation_authorized(): raise RuntimeError("CLRM2-B validation lock not verified")
        rows=[]; [rows.extend(build_discovery_records(s)) for s in DVAL_SEEDS]
        write(a.output,{"schema":"CLRM2-DVAL-v1","records":rows,"seed_sha256":DVAL_SHA256}); return 0
    if a.input is None or a.candidate is None: p.error("--input and --candidate required")
    raw=json.loads(a.input.read_text()); pkg=json.loads(a.candidate.read_text())
    write(a.output,{"schema":"CLRM2-FORMAL-RESULT-v1","adjudication":adjudicate_validation(pkg,raw["records"])})
    return 0


if __name__=="__main__":
    raise SystemExit(main())
