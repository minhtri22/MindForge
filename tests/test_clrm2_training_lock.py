from tools.clrm.verify_clrm2_training_lock import verify

def test_training_lock_passes():
    r=verify()
    assert r["status"]=="PASS",r
    assert r["verdict"]=="CLRM2_TRAINING_LOCK_VERIFICATION_PASS",r

def test_obs11_is_exact_and_preboundary():
    r=verify()
    assert r["checks"]["feature_preboundary_signature"],r
    assert r["checks"]["obs11_exact"],r
    assert r["checks"]["targets_exact"],r

def test_all_freshness_exclusions_clean():
    r=verify()
    assert not any(r["collisions"].values()),r
    assert r["checks"]["manifest_regen"],r
    assert r["checks"]["manifest_hashes"],r

def test_phase_a_preserves_sealed_validation():
    r=verify()
    assert r["checks"]["phase_A_only"],r
    assert r["checks"]["validation_transition"],r
    assert r["checks"]["dval_absent"],r
    assert r["checks"]["fresh_execution_workflows_absent"],r

def test_no_fresh_science_or_fit_exists():
    r=verify()
    assert r["checks"]["dtrain_absent"],r
    assert r["checks"]["candidate_absent"],r
    assert r["checks"]["formal_absent"],r
    assert r["fresh_seed_execution_attempted"] is False
    assert r["fresh_predictor_fitting_performed"] is False
    assert r["dval_outcomes_generated"] is False
    assert r["scientific_outcome_generated"] is False

def test_verifier_is_independent():
    r=verify()
    assert r["checks"]["verifier_independent"],r
    assert all(r["static_safety"].values()),r
