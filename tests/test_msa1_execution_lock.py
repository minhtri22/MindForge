from tools.msa.verify_msa1_execution_lock import verify


def test_independent_lock_verification_passes() -> None:
    result = verify()
    assert result["status"] == "PASS", result
    assert result["verdict"] == "MSA1_EXECUTION_LOCK_VERIFICATION_PASS"


def test_verifier_is_static_and_independent() -> None:
    result = verify()
    assert result["checks"]["verifier_independent"], result
    assert all(result["verifier_static_safety"].values()), result


def test_no_fresh_science_or_execution_workflow_exists() -> None:
    result = verify()
    assert result["checks"]["fresh_collection_absent"], result
    assert result["checks"]["formal_result_absent"], result
    assert result["checks"]["fresh_execution_workflow_absent"], result
    assert result["fresh_seed_execution_attempted"] is False
    assert result["scientific_outcome_generated"] is False
    assert result["difficulty_mutation_performed"] is False
    assert result["predictor_fitting_performed"] is False


def test_collision_audit_is_zero() -> None:
    result = verify()
    assert result["collisions"]["historical_kcl"] == []
    assert result["collisions"]["protected_kcl"] == []
    assert result["collisions"]["spent_aco"] == []
    assert result["collisions"]["spent_cprm"] == []


def test_all_frozen_contract_groups_pass() -> None:
    result = verify()
    for name in (
        "protocol_blob_exact",
        "runner_blob_exact",
        "eight_substrate_blobs_exact",
        "seed_manifest_hash_exact",
        "seed_generation_reproducible",
        "runtime_exact",
        "accuracy_gates_exact",
        "loss_gates_exact",
        "classification_matrix_exact",
        "retry_policy_exact",
    ):
        assert result["checks"][name], (name, result)
