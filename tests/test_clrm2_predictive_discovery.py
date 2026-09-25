import numpy as np
from experiments.clrm import clrm2_predictive_discovery as c2


def synthetic_records(seeds, nonlinear=False):
    rows=[]
    for s in seeds:
        u=((s % 997)/997.0)-0.5
        for stage in (1,2,3):
            f={
                "STAGE_2":1.0 if stage==2 else 0.0,
                "STAGE_3":1.0 if stage==3 else 0.0,
                "H1_M1_RMS":u,
                "H2_SQRT_M2_RMS":u*u,
                "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS":u+0.1*stage,
                "H4_TASK_DRIFT_RELATIVE_L2":abs(u),
                "H5_PRESSURE_TO_DRIFT_RATIO":u*u+0.2,
                "H6_DRIFT_PRESSURE_COSINE":np.sin(u),
                "H7_PRIOR_MEAN_ACCURACY":0.7+0.02*stage,
                "H8_PRIOR_WORST_ACCURACY":0.6+0.01*stage,
                "H9_CURRENT_TASK_LOSS":0.2+0.03*stage+0.05*u,
            }
            z=np.asarray([f[n] for n in c2.OBS11])
            base=float(0.3+0.05*stage+(0.15*u*u if nonlinear else 0.05*u))
            vals=[base+0.01*j+0.005*np.sum(z[:4]) for j in range(6)]
            rows.append({
                "seed":int(s),"boundary_index":stage,"features":f,
                "targets":dict(zip(c2.TARGETS,vals)),
                "accuracy_sentinel":{},"integrity":{"valid":True},
            })
    return rows


def test_manifest_and_folds():
    r=c2.validate_manifests()
    assert r["valid"],r
    assert c2.regenerate_seeds()==c2.ALL_SEEDS
    fs={c2.fold_for_seed(s) for s in c2.DTRAIN_SEEDS}
    assert fs==set(range(5))


def test_obs11_order_and_candidate_determinism():
    rows=synthetic_records(c2.DTRAIN_SEEDS[:30],nonlinear=True)
    a=c2.candidate_cv(rows)
    b=c2.candidate_cv(rows)
    assert a["selected_gamma"]==b["selected_gamma"]
    assert a["selected_lambda"]==b["selected_lambda"]
    assert abs(a["cv_score"]-b["cv_score"])<1e-15


def test_baseline_family_selection_is_frozen():
    rows=synthetic_records(c2.DTRAIN_SEEDS[:40])
    b=c2.baseline_oof(rows)
    assert b["strongest"] in {"B0","B1","B2"}
    assert len(b["b2_lambdas"])==6


def test_validation_adjudicator_structure():
    tr=synthetic_records(c2.DTRAIN_SEEDS,nonlinear=True)
    pkg=c2.fit_candidate_package(tr)
    va=synthetic_records(c2.DVAL_SEEDS,nonlinear=True)
    r=c2.adjudicate_validation(pkg,va)
    assert r["verdict"] in {
        "LOSS_RESPONSE_PREDICTABILITY_QUALIFIED",
        "LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED",
        "STOP_INTEGRITY_OR_BASELINE",
    }


def test_fresh_fitting_blocked_before_lock_verification():
    assert c2.training_authorized() is False
    assert c2.validation_authorized() is False
