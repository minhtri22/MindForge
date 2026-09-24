from __future__ import annotations
import math
import pytest
from experiments.msa import msa1_endpoint_adequacy as m


def _records(mode: str):
    seeds=tuple(range(3000001,3000073))
    rows=[]
    for i,seed in enumerate(seeds):
        for stage in (1,2,3):
            endpoints={}
            for pi,p in enumerate(m.POLICIES):
                if mode=="adequate":
                    acc=0.55 + ((i+pi+stage)%10)/24
                    loss=0.12 + ((i+3*pi+stage)%20)*0.012
                elif mode=="coarse":
                    acc=1.0 if i%3 else 23/24
                    loss=0.10 + ((i+3*pi+stage)%20)*0.012
                elif mode=="saturated":
                    acc=1.0 if i%3 else 23/24
                    loss=0.010 + ((i+pi+stage)%10)*0.002
                else:
                    acc=1.0
                    loss=0.08
                endpoints[p]={
                    "terminal_accuracy":min(1.0,acc),
                    "terminal_cross_entropy_loss":loss,
                    "step":250,
                }
            rows.append({
                "seed":seed,"boundary_index":stage,
                "after_task":f"T{stage}","next_task":f"T{stage+1}",
                "endpoints":endpoints,
                "integrity":{
                    "fork_models_equal":True,
                    "boundary_model_unchanged":True,
                    "exact_replay_match":True,
                    "endpoint_same_curve_state":True,
                    "valid":True,
                },
            })
    return seeds,rows


def _rel():
    return [{"seed":s,"max_abs_diff":0.0,"same_structure":True,"exact":True}
            for s in m.RELIABILITY_SEEDS]


def test_seed_manifest_frozen() -> None:
    assert len(m.FRESH_SEEDS)==72
    assert len(set(m.FRESH_SEEDS))==72
    assert m.seed_manifest_sha256()==m.SEED_MANIFEST_SHA256
    assert set(m.FRESH_SEEDS).isdisjoint(m.SPENT_ACO_SEEDS)
    assert set(m.FRESH_SEEDS).isdisjoint(m.SPENT_CPRM_SEEDS)
    assert set(m.FRESH_SEEDS).isdisjoint(m.PROTECTED_KCL_SEEDS)


@pytest.mark.parametrize("mode,verdict",[
    ("adequate","ENDPOINT_MEASUREMENT_ADEQUATE"),
    ("coarse","ACCURACY_COARSE_LOSS_INFORMATIVE"),
    ("saturated","CURRENT_SUBSTRATE_ENDPOINT_SATURATED"),
])
def test_synthetic_classification_matrix(mode,verdict) -> None:
    seeds,rows=_records(mode)
    out=m.adjudicate_records(rows,_rel(),expected_seeds=seeds)
    assert out["verdict"]==verdict, out


def test_stop_on_integrity_failure() -> None:
    seeds,rows=_records("adequate")
    rows[0]["integrity"]["valid"]=False
    out=m.adjudicate_records(rows,_rel(),expected_seeds=seeds)
    assert out["verdict"]=="STOP_INTEGRITY_OR_SUPPORT"


def test_no_predictor_or_difficulty_api() -> None:
    assert not hasattr(m,"fit_model")
    assert not hasattr(m,"train_predictor")
    assert not hasattr(m,"change_difficulty")


def test_execution_blocked_without_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m,"LOCK_VERIFICATION",m.Path("/definitely/absent"))
    assert m.execution_authorized() is False
