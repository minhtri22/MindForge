from tools.clrm.verify_clrm1_execution_lock import verify


def test_independent_lock_verification_passes():
    r = verify()
    assert r["status"] == "PASS", r
    assert r["verdict"] == "CLRM1_EXECUTION_LOCK_VERIFICATION_PASS", r


def test_freshness_and_spent_collisions_are_zero():
    r = verify()
    assert not any(r["collisions"].values()), r
    assert r["checks"]["seed_regeneration_exact"], r
    assert r["checks"]["seed_sequence_exact_everywhere"], r


def test_scientific_contract_is_frozen():
    r = verify()
    assert r["checks"]["response_contract_exact"], r
    assert r["checks"]["population_exact"], r
    assert r["checks"]["geometry_gate_exact"], r
    assert r["checks"]["reliability_exact"], r
    assert r["checks"]["adjudication_exact"], r
    assert r["checks"]["retry_policy_exact"], r


def test_no_fresh_execution_or_result_exists():
    r = verify()
    assert r["checks"]["fresh_collection_absent"], r
    assert r["checks"]["formal_result_absent"], r
    assert r["checks"]["fresh_execution_workflow_absent"], r
    assert r["fresh_seed_execution_attempted"] is False
    assert r["scientific_outcome_generated"] is False
    assert r["response_geometry_inspected"] is False
    assert r["predictor_fitting_performed"] is False
    assert r["difficulty_mutation_performed"] is False
    assert r["controller_execution_performed"] is False


def test_verifier_is_static_and_independent():
    r = verify()
    assert r["checks"]["verifier_independent"], r
    assert all(r["static_safety"].values()), r
