import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "tools" / "ollama_windows_adapter.py"
QUALIFIER_PATH = ROOT / "tools" / "owrq_qualify.py"
INTERFACE_PATH = ROOT / "artifacts" / "model-training-pipeline" / "infra" / "owrq" / "M6R2_CONSUMER_INTERFACE_SNAPSHOT.json"
WRAPPER_PATH = ROOT / "scripts" / "owrq_qualify_local.ps1"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


adapter = load_module(ADAPTER_PATH, "owrq_adapter")
qualifier = load_module(QUALIFIER_PATH, "owrq_qualifier")


def test_consumer_interface_exact_contract():
    i = json.loads(INTERFACE_PATH.read_text(encoding="utf-8"))
    assert i["contract_version"] == adapter.CONTRACT_VERSION
    assert set(i["commands"]) == {"session-open", "chat", "session-close"}


def test_qualification_is_science_firewalled_by_source():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert "tests/fixtures/eval_v1" not in q
    assert "llama.cpp" not in q
    assert "reasoning_sft" not in q.lower()
    assert '"eval_v1_accessed": False' in q
    assert "ollama pull" not in q.lower()
    assert '["create"' not in q
    assert '["rm"' not in q
    assert "model_quality_scored" in q
    assert "reasoning_scored" in q


def test_adapter_does_not_mutate_global_environment():
    a = ADAPTER_PATH.read_text(encoding="utf-8")
    assert 'os.environ["OLLAMA_HOST"] =' not in a
    assert 'os.environ["OLLAMA_KV_CACHE_TYPE"] =' not in a
    assert 'os.environ["OLLAMA_FLASH_ATTENTION"] =' not in a
    assert 'env["OLLAMA_HOST"] = host' in a
    assert 'env["OLLAMA_KV_CACHE_TYPE"] = kv_cache_type' in a


def test_flash_attention_is_observed_not_forced():
    a = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "Deliberately do not set or remove OLLAMA_FLASH_ATTENTION" in a
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert '"OLLAMA_FLASH_ATTENTION_forced": False' in q


def test_known_bad_launch_is_detected():
    text = 'runner cmd="llama-server --cache-type-k q4_0 --cache-type-v q4_0 --flash-attn off"\nquantized V cache requires flash_attn to be enabled'
    r = qualifier.parse_launch_evidence(text)
    assert r["cache_type_v_q4_0_observed"] is True
    assert r["cache_type_v_f16_observed"] is False
    assert r["flash_attention_mode"] == "off"
    assert r["known_conflict_error_observed"] is True


def test_repaired_launch_is_detected():
    text = 'runner cmd="llama-server --cache-type-k f16 --cache-type-v f16 --flash-attn off"'
    r = qualifier.parse_launch_evidence(text)
    assert r["cache_type_k_f16_observed"] is True
    assert r["cache_type_v_f16_observed"] is True
    assert r["cache_type_v_q4_0_observed"] is False
    assert r["flash_attention_mode"] == "off"
    assert r["known_conflict_error_observed"] is False


def test_child_environment_preserves_flash_attention_value(monkeypatch):
    monkeypatch.setenv("OLLAMA_FLASH_ATTENTION", "false")
    env = adapter.child_environment("127.0.0.1:11468", "f16")
    assert env["OLLAMA_HOST"] == "127.0.0.1:11468"
    assert env["OLLAMA_KV_CACHE_TYPE"] == "f16"
    assert env["OLLAMA_FLASH_ATTENTION"] == "false"


def test_fixture_is_existing_only_and_default_is_frozen():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert 'DEFAULT_FIXTURE = "llama3.2:1b"' in q
    assert 'reason="UNRESOLVED_INFRA_FIXTURE"' in q
    assert "find_model(tags, args.fixture_name)" in q


def test_plumbing_output_is_not_scored():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert "plumbing_request_completed" in q
    assert "expected" not in q
    assert "task_success" not in q
    assert "accuracy" not in q


def test_qualified_scope_has_m6r2_required_fields():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    for token in [
        '"schema": "mindforge-owrq-qualified-runtime-scope-v1"',
        '"status": "QUALIFIED_RUNTIME_SCOPE"',
        '"runtime_environment"',
        '"target_scope"',
        '"adapter"',
        '"api_contract"',
        '"backend_resolution"',
        '"runtime_adapter_git_blob_sha1"',
    ]:
        assert token in q


def test_system_11434_is_only_snapshotted():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert 'SYSTEM_HOST = "127.0.0.1:11434"' in q
    assert "snapshot_system_service()" in q
    assert 'start_server(ollama, TARGET_HOST' in q
    assert 'start_server(ollama, SYSTEM_HOST' not in q


def test_wrapper_requires_future_lock_and_auth_before_local_execution():
    p = WRAPPER_PATH.read_text(encoding="utf-8")
    lock = p.index("$LockPath")
    auth = p.index("$AuthPath")
    run = p.index('& python "tools/owrq_qualify.py"')
    assert lock < run and auth < run
    assert "AUTHORIZED_ONE_OWRQ_LOCAL_QUALIFICATION" in p


def test_adapter_contract_contains_durable_response_semantics():
    a = ADAPTER_PATH.read_text(encoding="utf-8")
    response_write = a.index("atomic_json(response_path, response)")
    transport_write = a.index("atomic_json(\n            transport_path", response_write)
    assert response_write < transport_write


def test_adapter_binds_supplied_q4_and_modelfile_package_identity():
    a = ADAPTER_PATH.read_text(encoding="utf-8")
    assert 'if not q4_path.is_file()' in a
    assert 'if not modelfile_path.is_file()' in a
    assert 'q4_path.parent.resolve() != modelfile_path.parent.resolve()' in a
    assert '"q4_sha256": sha256_file(q4_path)' in a
    assert '"modelfile_sha256": sha256_file(modelfile_path)' in a


def test_evidence_manifest_excludes_final_report_to_avoid_circular_hashing():
    q = QUALIFIER_PATH.read_text(encoding="utf-8")
    assert '"OWRQ_QUALIFICATION_REPORT.json"' in q
    assert '"evidence-manifest.json"' in q
