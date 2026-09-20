from tools.cprm.verify_cprm1_execution_lock import verify


def test_independent_lock_verification_passes() -> None:
    result = verify()
    assert result["status"] == "PASS", result
    assert result["verdict"] == "CPRM1_EXECUTION_LOCK_VERIFICATION_PASS"


def test_verification_is_zero_science() -> None:
    result = verify()
    assert result["fresh_seed_execution_attempted"] is False
    assert result["scientific_outcome_generated"] is False
    assert result["model_fitting_performed"] is False


def test_no_execution_workflow_or_scientific_result_exists() -> None:
    result = verify()
    assert result["checks"]["fresh_execution_workflow_absent"], result
    assert result["checks"]["fresh_collection_absent"], result
    assert result["checks"]["formal_result_absent"], result


def test_collision_audit_is_clean() -> None:
    result = verify()
    assert result["collisions"]["historical_kcl"] == []
    assert result["collisions"]["protected_kcl"] == []
    assert result["collisions"]["spent_aco"] == []
