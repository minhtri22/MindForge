from tools.cprm.verify_cprm0_spec import verify


def test_cprm0_specification_contract_passes() -> None:
    r = verify()
    assert r["status"] == "PASS", r


def test_cprm0_is_zero_science() -> None:
    r = verify()
    assert r["scientific_execution_attempted"] is False
    assert r["fresh_scientific_seed_consumed"] is False
    assert r["model_fitting_performed"] is False


def test_cprm0_has_no_execution_workflow_or_science_artifact() -> None:
    r = verify()
    assert r["checks"]["no_cprm_execution_workflow"], r
    assert r["checks"]["no_cprm_scientific_artifacts"], r
