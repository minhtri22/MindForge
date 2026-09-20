from tools.msa.verify_msa0_spec import verify

def test_msa0_specification_passes() -> None:
    r=verify()
    assert r["status"]=="PASS", r
    assert r["verdict"]=="MSA0_ZERO_SCIENCE_SPEC_QA_PASS"

def test_msa0_is_zero_science() -> None:
    r=verify()
    assert r["scientific_execution_attempted"] is False
    assert r["fresh_scientific_seed_generated"] is False
    assert r["difficulty_mutation_performed"] is False
    assert r["predictor_fitting_performed"] is False

def test_no_execution_or_seed_manifest_exists() -> None:
    r=verify()
    assert r["checks"]["no_msa_execution_workflow"], r
    assert r["checks"]["no_fresh_msa_seed_manifest"], r
    assert r["checks"]["no_msa_scientific_artifacts_or_runners"], r
