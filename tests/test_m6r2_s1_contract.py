import json
from pathlib import Path

import pytest

from pipeline.m6r2_contract import (
    ContractError,
    EXPECTED_Q4_SHA256,
    EXPECTED_MODELFILE_SHA256,
    FROZEN_PARENT_VECTOR,
    adjudicate_completed_rows,
    classify_failure,
    response_exposes_outcome,
    row_from_response,
    scan_prior_outcome_directory,
    validate_owrq_binding,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "m6r2_parity_oneclick.ps1"
PREREG = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "PREREGISTRATION.json"
S2 = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "S2_INFRA_BINDING_AUTHORIZATION.json"
S3 = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "S3_EXECUTION_AUTHORIZATION.json"


def qualified_binding():
    return {
        "schema": "mindforge-owrq-qualified-runtime-scope-v1",
        "status": "QUALIFIED_RUNTIME_SCOPE",
        "qualification_sha256": "a" * 64,
        "runtime": {
            "ollama_version": "0.34.2",
            "ollama_executable_path": r"C:\\Users\\test\\ollama.exe",
            "ollama_executable_sha256": "b" * 64,
        },
        "runtime_environment": {
            "OLLAMA_KV_CACHE_TYPE": "f16",
            "OLLAMA_FLASH_ATTENTION_forced": False,
        },
        "target_scope": {"local_machine_fingerprint_sha256": "c" * 64},
        "adapter": {"runtime_adapter_git_blob_sha1": "d" * 40},
        "api_contract": {"host": "127.0.0.1:11468", "chat_endpoint": "/api/chat"},
    }


def test_frozen_science_identity():
    p = json.loads(PREREG.read_text(encoding="utf-8"))
    assert p["study_type"] == "FRESH_NO_TREATMENT_PARITY_REPLICATION"
    assert p["frozen_artifact"]["sha256"] == EXPECTED_Q4_SHA256
    assert p["frozen_modelfile_sha256"] == EXPECTED_MODELFILE_SHA256
    assert p["frozen_parent"]["task_vector"] == FROZEN_PARENT_VECTOR
    assert p["infrastructure"]["kv_cache_repair_is_scientific_treatment"] is False


def test_binding_accepts_only_qualified_scope():
    out = validate_owrq_binding(qualified_binding())
    assert out["ollama_version"] == "0.34.2"
    assert out["kv_cache_type"] == "f16"
    assert out["flash_attention_forced"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b.update(status="FAIL_INFRA"),
        lambda b: b["runtime"].update(ollama_version="0.34.1"),
        lambda b: b["runtime_environment"].update(OLLAMA_KV_CACHE_TYPE="q4_0"),
        lambda b: b["runtime_environment"].update(OLLAMA_FLASH_ATTENTION_forced=True),
    ],
)
def test_binding_rejects_scope_drift(mutation):
    b = qualified_binding()
    mutation(b)
    with pytest.raises(ContractError):
        validate_owrq_binding(b)


def test_visible_content_exposes_outcome():
    assert response_exposes_outcome({"message": {"content": "x"}}) is True


def test_native_thinking_alone_exposes_outcome():
    assert response_exposes_outcome({"message": {"content": "", "thinking": "hidden"}}) is True


def test_empty_response_does_not_expose_outcome():
    assert response_exposes_outcome({"message": {"content": "", "thinking": ""}}) is False


def test_preoutcome_infra_failure_is_not_scientific_fail_or_consumed():
    r = classify_failure(outcome_exposed=False, positive_infra_failure=True)
    assert r == {
        "classification": "INVALID_INFRA_PREOUTCOME",
        "attempt_consumed": False,
        "scientific_fail": False,
    }


def test_binding_failure_is_not_scientific_attempt():
    r = classify_failure(outcome_exposed=False, positive_infra_failure=False, binding_failed=True)
    assert r["classification"] == "BLOCKED_INFRA_BINDING"
    assert r["attempt_consumed"] is False
    assert r["scientific_fail"] is False


def test_postoutcome_infra_failure_consumes_attempt_but_is_not_scientific_fail():
    r = classify_failure(outcome_exposed=True, positive_infra_failure=True)
    assert r["classification"] == "INVALID_INFRA_POSTOUTCOME"
    assert r["attempt_consumed"] is True
    assert r["scientific_fail"] is False


def test_unknown_preoutcome_failure_fails_closed_as_provenance():
    r = classify_failure(outcome_exposed=False, positive_infra_failure=False)
    assert r["classification"] == "INVALID_PROVENANCE"
    assert r["attempt_consumed"] is False


def test_frozen_parent_vector_can_pass_parity_even_when_answers_are_wrong():
    tasks = [
        {"id": "arith-1", "type": "exact_answer", "expected": "42"},
        {"id": "compare-1", "type": "exact_answer", "expected": "9.9"},
    ]
    responses = [
        {"message": {"content": "wrong-a"}},
        {"message": {"content": "wrong-b"}},
    ]
    rows = [row_from_response(t, r) for t, r in zip(tasks, responses)]
    out = adjudicate_completed_rows(rows)
    assert out["task_vector"] == [False, False]
    assert out["accuracy"] == 0.0
    assert out["scientific_verdict"] == "PASS_PARITY"


def test_different_task_vector_fails_parity():
    tasks = [
        {"id": "arith-1", "type": "exact_answer", "expected": "42"},
        {"id": "compare-1", "type": "exact_answer", "expected": "9.9"},
    ]
    responses = [
        {"message": {"content": "42"}},
        {"message": {"content": "wrong"}},
    ]
    rows = [row_from_response(t, r) for t, r in zip(tasks, responses)]
    assert adjudicate_completed_rows(rows)["scientific_verdict"] == "FAIL_PARITY"


def test_native_thinking_fails_reasoning_mapping():
    tasks = [
        {"id": "arith-1", "type": "exact_answer", "expected": "42"},
        {"id": "compare-1", "type": "exact_answer", "expected": "9.9"},
    ]
    responses = [
        {"message": {"content": "wrong-a", "thinking": "secret"}},
        {"message": {"content": "wrong-b"}},
    ]
    rows = [row_from_response(t, r) for t, r in zip(tasks, responses)]
    out = adjudicate_completed_rows(rows)
    assert out["attempt_consumed"] is True
    assert out["scientific_verdict"] == "FAIL_REASONING_MAPPING"


def test_prior_response_is_recovered_as_exposure(tmp_path):
    (tmp_path / "request-01-arith-1-start.json").write_text("{}", encoding="utf-8")
    (tmp_path / "request-01-arith-1-response.json").write_text(
        json.dumps({"message": {"content": "", "thinking": "seen"}}), encoding="utf-8"
    )
    state = scan_prior_outcome_directory(tmp_path)
    assert state["outcome_exposed"] is True
    assert state["ambiguous_pending_request"] is False


def test_dangling_request_marker_is_ambiguous_and_fail_closed(tmp_path):
    (tmp_path / "request-01-arith-1-start.json").write_text("{}", encoding="utf-8")
    state = scan_prior_outcome_directory(tmp_path)
    assert state["outcome_exposed"] is False
    assert state["ambiguous_pending_request"] is True


def test_no_current_s2_or_s3_execution_authorization_exists():
    assert not S2.exists()
    assert not S3.exists()


def test_runner_fails_closed_on_future_auth_before_runtime_actions():
    t = SCRIPT.read_text(encoding="utf-8")
    main = t.index("# MAIN")
    auth = t.index("$FutureAuth = Assert-FutureExecutionAuthorized", main)
    binding = t.index("$Binding = Read-And-VerifyQualifiedRuntime", auth)
    runtime = t.index("$ServerProc = Start-Process", binding)
    api = t.index("Invoke-RestMethod -Method Get", runtime)
    assert main < auth < binding < runtime < api


def test_runner_has_no_upgrade_pull_or_global_env_mutation():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "OllamaSetup.exe" not in t
    assert " ollama pull " not in t.lower()
    assert "SetEnvironmentVariable" not in t
    assert "OLLAMA_FLASH_ATTENTION =" not in t


def test_runner_restores_process_scoped_environment():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "$OldHost = $env:OLLAMA_HOST" in t
    assert "$OldKv = $env:OLLAMA_KV_CACHE_TYPE" in t
    assert "$env:OLLAMA_HOST=$OldHost" in t
    assert "$env:OLLAMA_KV_CACHE_TYPE=$OldKv" in t


def test_runner_persists_response_before_exposure_state():
    t = SCRIPT.read_text(encoding="utf-8")
    response_write = t.index("Write-AtomicJson $ResponsePath $Response")
    exposure_test = t.index("$ThisExposes=Test-ResponseExposure $Response", response_write)
    consume = t.index("Save-ExposureState", exposure_test)
    assert response_write < exposure_test < consume


def test_runner_science_verdict_vocabulary_is_separate_from_infra():
    t = SCRIPT.read_text(encoding="utf-8")
    assert '"PASS_PARITY"' in t
    assert '"BLOCKED_INFRA_BINDING"' in t
    assert '"INVALID_INFRA_PREOUTCOME"' in t
    assert '"INVALID_INFRA_POSTOUTCOME"' in t
    assert 'scientific_fail=$false' in t
    assert '"FAIL_PACKAGE"' not in t
    assert '"FAIL_RUNTIME"' not in t
