from tools.clrm.verify_clrm2_validation_lock import verify

def test_validation_lock_passes():
    r = verify()
    assert r["status"] == "PASS", r
    assert r["verdict"] == "CLRM2_VALIDATION_LOCK_VERIFICATION_PASS", r

def test_candidate_and_dtrain_are_exact_and_frozen():
    r = verify()
    assert r["checks"]["candidate_exact"], r
    assert r["checks"]["candidate_contract"], r
    assert r["checks"]["lock_candidate_matches"], r
    assert r["checks"]["dtrain_exact"], r
    assert r["checks"]["dtrain_spent"], r

def test_phase_a_is_hard_disabled():
    r = verify()
    assert r["checks"]["phase_a_workflow_retired_exact"], r
    assert r["checks"]["phase_a_hard_disabled"], r

def test_dval_contract_is_exact_and_still_sealed():
    r = verify()
    assert r["checks"]["dval_manifest_exact"], r
    assert r["checks"]["obs11_exact"], r
    assert r["checks"]["targets_exact"], r
    assert r["checks"]["bootstrap_exact"], r
    assert r["checks"]["gate2_exact"], r
    assert r["checks"]["dval_absent"], r
    assert r["checks"]["formal_absent"], r

def test_verifier_is_independent_and_zero_science():
    r = verify()
    assert r["checks"]["verifier_independent"], r
    assert all(r["static_safety"].values()), r
    assert r["dval_outcomes_generated"] is False
    assert r["gate2_called"] is False
    assert r["scientific_outcome_generated"] is False
