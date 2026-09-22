import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import importlib.util
import subprocess

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "m6r2_contract.py"
SPEC = importlib.util.spec_from_file_location("m6r2_contract_s1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
m6r2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m6r2)

ADAPTER_CONTRACT_VERSION = m6r2.ADAPTER_CONTRACT_VERSION
ContractError = m6r2.ContractError
EXPECTED_MODELFILE_SHA256 = m6r2.EXPECTED_MODELFILE_SHA256
EXPECTED_Q4_SHA256 = m6r2.EXPECTED_Q4_SHA256
FROZEN_PARENT_VECTOR = m6r2.FROZEN_PARENT_VECTOR
adjudicate_completed_rows = m6r2.adjudicate_completed_rows
classify_failure = m6r2.classify_failure
response_exposes_outcome = m6r2.response_exposes_outcome
row_from_response = m6r2.row_from_response
scan_prior_outcome_directory = m6r2.scan_prior_outcome_directory
validate_owrq_binding = m6r2.validate_owrq_binding

SCRIPT = ROOT / "scripts" / "m6r2_parity_oneclick.ps1"
PREREG = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "PREREGISTRATION.json"
INTERFACE = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "S1_INFRA_ADAPTER_INTERFACE.json"
S2 = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "S2_INFRA_BINDING_AUTHORIZATION.json"
S3 = ROOT / "artifacts" / "model-training-pipeline" / "m6r2" / "S3_EXECUTION_AUTHORIZATION.json"


def qualified_binding():
    return {
        "schema": "mindforge-owrq-qualified-runtime-scope-v1",
        "status": "QUALIFIED_RUNTIME_SCOPE",
        "runtime": {
            "ollama_version": "0.34.2",
            "ollama_executable_sha256": "b" * 64,
        },
        "runtime_environment": {
            "OLLAMA_KV_CACHE_TYPE": "f16",
            "OLLAMA_FLASH_ATTENTION_forced": False,
            "OLLAMA_FLASH_ATTENTION_observed_value": None,
        },
        "target_scope": {"local_machine_fingerprint_sha256": "c" * 64},
        "adapter": {
            "contract_version": ADAPTER_CONTRACT_VERSION,
            "entrypoint": "pipeline/ollama_windows_adapter.py",
            "runtime_adapter_git_blob_sha1": "d" * 40,
        },
        "api_contract": {"host": "127.0.0.1:11468", "chat_endpoint": "/api/chat"},
        "backend_resolution": {"flash_attention_mode": "off"},
    }


def test_frozen_science_identity():
    p = json.loads(PREREG.read_text(encoding="utf-8"))
    assert p["study_type"] == "FRESH_NO_TREATMENT_PARITY_REPLICATION"
    assert p["frozen_artifact"]["sha256"] == EXPECTED_Q4_SHA256
    assert p["frozen_modelfile_sha256"] == EXPECTED_MODELFILE_SHA256
    assert p["frozen_parent"]["task_vector"] == FROZEN_PARENT_VECTOR
    assert p["infrastructure"]["kv_cache_repair_is_scientific_treatment"] is False


def test_adapter_interface_is_explicitly_external_to_science_lane():
    i = json.loads(INTERFACE.read_text(encoding="utf-8"))
    assert i["contract_version"] == ADAPTER_CONTRACT_VERSION
    assert set(i["commands"]) == {"session-open", "chat", "session-close"}
    assert "direct ollama.exe invocation" in i["science_lane_forbidden_runtime_primitives"]


def test_binding_accepts_only_qualified_scope():
    out = validate_owrq_binding(qualified_binding())
    assert out["ollama_version"] == "0.34.2"
    assert out["kv_cache_type"] == "f16"
    assert out["flash_attention_forced"] is False
    assert out["runtime_adapter_contract_version"] == ADAPTER_CONTRACT_VERSION


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b.update(status="FAIL_INFRA"),
        lambda b: b["runtime"].update(ollama_version="0.34.1"),
        lambda b: b["runtime_environment"].update(OLLAMA_KV_CACHE_TYPE="q4_0"),
        lambda b: b["runtime_environment"].update(OLLAMA_FLASH_ATTENTION_forced=True),
        lambda b: b["adapter"].update(contract_version="wrong"),
        lambda b: b["backend_resolution"].update(flash_attention_mode=""),
    ],
)
def test_binding_rejects_scope_drift(mutation):
    b = qualified_binding()
    mutation(b)
    with pytest.raises(ContractError):
        validate_owrq_binding(b)


def test_visible_or_native_thinking_exposes_outcome():
    assert response_exposes_outcome({"message": {"content": "x"}}) is True
    assert response_exposes_outcome({"message": {"content": "", "thinking": "hidden"}}) is True
    assert response_exposes_outcome({"message": {"content": "", "thinking": ""}}) is False


def test_failure_domain_semantics():
    assert classify_failure(outcome_exposed=False, positive_infra_failure=True) == {
        "classification": "INVALID_INFRA_PREOUTCOME",
        "attempt_consumed": False,
        "scientific_fail": False,
    }
    assert classify_failure(outcome_exposed=False, positive_infra_failure=False, binding_failed=True)["classification"] == "BLOCKED_INFRA_BINDING"
    assert classify_failure(outcome_exposed=True, positive_infra_failure=True) == {
        "classification": "INVALID_INFRA_POSTOUTCOME",
        "attempt_consumed": True,
        "scientific_fail": False,
    }
    assert classify_failure(outcome_exposed=False, positive_infra_failure=False)["classification"] == "INVALID_PROVENANCE"


def test_frozen_parent_vector_parity_and_reasoning():
    tasks = [
        {"id": "arith-1", "type": "exact_answer", "expected": "42"},
        {"id": "compare-1", "type": "exact_answer", "expected": "9.9"},
    ]
    rows = [
        row_from_response(tasks[0], {"message": {"content": "wrong-a"}}),
        row_from_response(tasks[1], {"message": {"content": "wrong-b"}}),
    ]
    out = adjudicate_completed_rows(rows)
    assert out["task_vector"] == [False, False]
    assert out["accuracy"] == 0.0
    assert out["scientific_verdict"] == "PASS_PARITY"

    rows[0] = row_from_response(tasks[0], {"message": {"content": "42"}})
    assert adjudicate_completed_rows(rows)["scientific_verdict"] == "FAIL_PARITY"

    rows = [
        row_from_response(tasks[0], {"message": {"content": "wrong-a", "thinking": "secret"}}),
        row_from_response(tasks[1], {"message": {"content": "wrong-b"}}),
    ]
    assert adjudicate_completed_rows(rows)["scientific_verdict"] == "FAIL_REASONING_MAPPING"


def test_prior_durable_response_recovers_exposure(tmp_path):
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


def git_blob_sha1(path):
    cp = subprocess.run(
        ["git", "hash-object", "--", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return cp.stdout.strip()


def test_s2_binding_and_s3_v2_one_attempt_authorization_present():
    assert S2.exists()
    s2 = json.loads(S2.read_text(encoding="utf-8"))
    assert s2["status"] == "AUTHORIZED_ONE_CONSOLIDATED_INFRA_BINDING"
    assert s2["binding_status"] == "BINDING_PASS"
    assert s2["s1_implementation_lock_git_blob_sha1"] == "124b21063675e6d37202a81b88c04efc4aa2254e"
    assert s2["qualified_runtime_artifact_sha256"] == "4c15da27c2087b14d9c48689e5e811520c422b4b45eaddc3838bd4432ceb0370"
    assert s2["required_scope"]["runtime_adapter_git_blob_sha1"] == "075b3b354bbd0c7674d629070d99769d201ad619"
    assert s2["required_scope"]["ollama_version"] == "0.34.2"
    assert s2["required_scope"]["kv_cache_type"] == "f16"
    assert s2["required_scope"]["flash_attention_forced"] is False

    adapter_path = ROOT / "tools" / "ollama_windows_adapter.py"
    assert adapter_path.exists()
    assert git_blob_sha1(adapter_path) == "075b3b354bbd0c7674d629070d99769d201ad619"

    assert S3.exists()
    s3 = json.loads(S3.read_text(encoding="utf-8"))
    assert s3["status"] == "AUTHORIZED_ONE_FRESH_M6R2_OUTCOME_EXECUTION"
    assert s3["schema"] == "mindforge-model-pipeline-m6r2-s3-execution-authorization-v2"
    assert s3["attempts_authorized"] == 1
    assert s3["s1_implementation_lock_git_blob_sha1"] == "124b21063675e6d37202a81b88c04efc4aa2254e"
    assert s3["s2_authorization_git_blob_sha1"] == "281b79a4482ed3df57c84c5a138cd00df7d72842"
    assert s3["qualified_runtime_artifact_sha256"] == "4c15da27c2087b14d9c48689e5e811520c422b4b45eaddc3838bd4432ceb0370"
    assert s3["exact_runtime_adapter"]["path"] == "tools/ollama_windows_adapter.py"
    assert s3["exact_runtime_adapter"]["git_blob_sha1"] == "075b3b354bbd0c7674d629070d99769d201ad619"
    assert s3["exact_runtime_adapter"]["materialized_on_execution_branch"] is True
    assert s3["execution_performed"] is False
    assert s3["m7_authorized"] is False
    assert s3["bulk_training_authorized"] is False


def test_runner_requires_lock_and_future_authorizations_before_binding_or_adapter():
    t = SCRIPT.read_text(encoding="utf-8")
    main = t.index("# MAIN")
    auth = t.index("$FutureAuth=Assert-FutureExecutionAuthorized", main)
    binding = t.index("$BindingInfo=Read-And-VerifyQualifiedRuntime", auth)
    adapter = t.index("$Open=Invoke-QualifiedAdapter", binding)
    assert main < auth < binding < adapter
    assert "$S1LockPath" in t
    assert "s1_implementation_lock_git_blob_sha1" in t
    assert "s2_authorization_git_blob_sha1" in t


def test_science_lane_contains_no_direct_ollama_runtime_implementation():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "Invoke-RestMethod" not in t
    assert "Start-Process -FilePath $OllamaExe" not in t
    assert '@("create"' not in t
    assert '@("serve"' not in t
    assert "OllamaSetup.exe" not in t
    assert "SetEnvironmentVariable" not in t
    assert "$env:OLLAMA_KV_CACHE_TYPE" not in t
    assert "$env:OLLAMA_FLASH_ATTENTION" not in t


def test_runner_uses_only_qualified_adapter_operations():
    t = SCRIPT.read_text(encoding="utf-8")
    assert '"session-open"' in t
    assert '"chat"' in t
    assert '"session-close"' in t
    assert "qualified adapter blob drift" in t
    assert "qualified OWRQ artifact hash mismatch" in t


def test_generic_preoutcome_chat_failure_is_not_assumed_infrastructure():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "chat failed before outcome exposure without positive infra evidence" in t
    assert "positive_infra_failure" in t


def test_runner_persists_response_before_exposure_state():
    t = SCRIPT.read_text(encoding="utf-8")
    response_read = t.index("$Response=Get-Content $ResponsePath")
    exposure_test = t.index("$ThisExposes=Test-ResponseExposure $Response", response_read)
    consume = t.index("Save-ExposureState", exposure_test)
    assert response_read < exposure_test < consume


def test_cleanup_can_invalidate_but_never_create_scientific_fail():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "owned_cleanup_pass" in t
    assert "initial_final_model_sets_match" in t
    assert '$Classification="INVALID_INFRA_POSTOUTCOME"' in t
    assert '$Classification="INVALID_INFRA_PREOUTCOME"' in t
    assert 'scientific_fail=($Classification -eq "FAIL_PARITY" -or $Classification -eq "FAIL_REASONING_MAPPING")' in t


def test_science_verdict_vocabulary_has_no_legacy_package_runtime_failures():
    t = SCRIPT.read_text(encoding="utf-8")
    assert '"PASS_PARITY"' in t
    assert '"BLOCKED_INFRA_BINDING"' in t
    assert '"INVALID_INFRA_PREOUTCOME"' in t
    assert '"INVALID_INFRA_POSTOUTCOME"' in t
    assert '"FAIL_PACKAGE"' not in t
    assert '"FAIL_RUNTIME"' not in t


def test_contract_module_is_stdlib_isolated_from_pipeline_package():
    t = SCRIPT.read_text(encoding="utf-8")
    assert "tools/m6r2_contract.py" in t
    assert "pipeline/m6r2_contract.py" not in t
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "import yaml" not in source
    assert "from pipeline" not in source
