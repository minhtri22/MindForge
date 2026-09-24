from tools.clrm.validate_clrm0_spec import validate


def test_clrm0_spec_passes() -> None:
    r = validate()
    assert r["status"] == "PASS", r
    assert r["verdict"] == "CLRM0_ZERO_SCIENCE_SPEC_QA_PASS"


def test_no_science_or_predictor() -> None:
    r = validate()
    assert r["checks"]["no_scientific_runner"], r
    assert r["checks"]["no_clrm_results"], r
    assert r["checks"]["no_fresh_seed_manifest"], r
    assert r["fresh_seed_execution_attempted"] is False
    assert r["scientific_outcome_generated"] is False
    assert r["predictor_fitting_performed"] is False
    assert r["controller_execution_performed"] is False


def test_new_target_is_not_cprm_minus_accuracy() -> None:
    r = validate()
    assert r["checks"]["exact_two_axis_target"], r
    assert r["checks"]["no_cprm_target_reuse"], r
    assert r["checks"]["accuracy_sentinel_only"], r


def test_predictive_governance_is_frozen() -> None:
    r = validate()
    assert r["checks"]["baseline_family_frozen"], r
    assert r["checks"]["roles_separated"], r
    assert r["checks"]["superiority_gate_frozen"], r
    assert r["checks"]["calibration_gate_frozen"], r
    assert r["checks"]["finite_roadmap"], r
