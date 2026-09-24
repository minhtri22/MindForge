from tools.msa.verify_msa3_execution_lock import verify


def test_independent_msa3_lock_verification_passes() -> None:
    r = verify()
    assert r["status"] == "PASS", r
    assert r["verdict"] == "MSA3_EXECUTION_LOCK_VERIFICATION_PASS"


def test_replication_contract_is_exact_copy() -> None:
    r = verify()
    assert r["checks"]["scientific_contract_exact_copy"], r
    assert r["checks"]["replication_rule_exact"], r
    assert r["checks"]["discovery_binding_exact"], r


def test_freshness_and_collisions_are_clean() -> None:
    r = verify()
    assert r["checks"]["seed_regeneration_exact"], r
    assert r["collisions"]["historical_kcl"] == []
    assert r["collisions"]["protected_kcl"] == []
    assert r["collisions"]["spent_aco"] == []
    assert r["collisions"]["spent_cprm"] == []
    assert r["collisions"]["spent_msa1"] == []


def test_no_fresh_execution_or_result_exists() -> None:
    r = verify()
    assert r["checks"]["fresh_collection_absent"], r
    assert r["checks"]["formal_result_absent"], r
    assert r["checks"]["fresh_execution_workflow_absent"], r
    assert r["fresh_seed_execution_attempted"] is False
    assert r["scientific_outcome_generated"] is False
    assert r["difficulty_mutation_performed"] is False
    assert r["predictor_fitting_performed"] is False


def test_static_verifier_is_independent() -> None:
    r = verify()
    assert r["checks"]["verifier_independent"], r
    assert all(r["static_safety"].values()), r
