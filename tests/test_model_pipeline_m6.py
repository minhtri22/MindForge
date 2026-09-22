from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.m6 import (
    FROZEN_ACCURACY,
    FROZEN_INFERENCE,
    FROZEN_Q4_MANIFEST,
    FROZEN_Q4_SHA256,
    FROZEN_Q4_SIZE,
    FROZEN_TASK_VECTOR,
    M6ContractError,
    build_chat_request,
    build_cleanup_command,
    build_create_command,
    cleanup_is_authorized,
    ephemeral_model_name,
    evaluate_ollama_parity,
    load_ollama_lock,
    mark_created,
    modelfile_contract,
    ownership_manifest,
    reasoning_mapping,
    render_modelfile,
    terminal_boundary,
    verify_frozen_q4_identity,
)

ROOT = Path(__file__).resolve().parents[1]


def test_ollama_lock_is_exact_and_zero_runtime():
    lock = load_ollama_lock(ROOT / "docs/model-training-pipeline/runtime/ollama.lock.json")
    assert lock["version"] == "0.34.2"
    assert lock["tag"] == "v0.34.2"
    assert lock["release_id"] == 389486962
    assert lock["implementation_stage"]["executable_invocation_authorized"] is False
    assert lock["implementation_stage"]["version_probe_authorized"] is False
    assert lock["implementation_stage"]["install_update_authorized"] is False
    assert lock["implementation_stage"]["download_authorized"] is False


def test_frozen_q4_identity_requires_all_fields():
    identity = {
        "target_key": "q4_k_m",
        "quantizer_type": "Q4_K_M",
        "sha256": FROZEN_Q4_SHA256,
        "aggregate_manifest_hash": FROZEN_Q4_MANIFEST,
        "size": FROZEN_Q4_SIZE,
    }
    assert verify_frozen_q4_identity(identity) is True
    assert verify_frozen_q4_identity({**identity, "size": FROZEN_Q4_SIZE + 1}) is False


def test_modelfile_bytes_are_deterministic_and_contract_derived():
    first = render_modelfile()
    second = render_modelfile()
    assert first == second
    assert first == (
        "FROM ./model-q4_k_m.gguf\n"
        "PARAMETER num_ctx 2048\n"
        "PARAMETER num_predict 128\n"
        "PARAMETER temperature 0\n"
        "PARAMETER top_p 1\n"
        "PARAMETER top_k 0\n"
        "PARAMETER seed 42\n"
    )
    contract = modelfile_contract()
    assert contract["parameters_derived_from_frozen_inference"] is True
    assert contract["independent_generation_defaults_added"] is False
    assert len(contract["sha256"]) == 64


def test_modelfile_rejects_inference_drift():
    drifted = dict(FROZEN_INFERENCE)
    drifted["temperature"] = 0.1
    with pytest.raises(M6ContractError):
        render_modelfile(inference=drifted)


def test_namespace_is_deterministic_and_hash_scoped():
    name = ephemeral_model_name("run-001")
    assert name == f"pipeline-test-run-001-{FROZEN_Q4_SHA256[:12]}"
    assert ephemeral_model_name("run-001") == name
    with pytest.raises(M6ContractError):
        ephemeral_model_name("../unsafe")


def test_cleanup_refuses_unowned_model_and_allows_owned_only():
    name = ephemeral_model_name("run-001")
    manifest = ownership_manifest("run-001", name)
    assert cleanup_is_authorized(name, manifest) is False
    with pytest.raises(M6ContractError):
        build_cleanup_command("ollama", name, manifest)

    created = mark_created(manifest)
    assert cleanup_is_authorized(name, created) is True
    assert build_cleanup_command("ollama", name, created) == ["ollama", "rm", name]
    assert cleanup_is_authorized("other-model", created) is False


def test_create_command_never_targets_non_ephemeral_namespace():
    name = ephemeral_model_name("run-001")
    assert build_create_command("ollama", name, "Modelfile") == [
        "ollama", "create", name, "-f", "Modelfile"
    ]
    with pytest.raises(M6ContractError):
        build_create_command("ollama", "user-model", "Modelfile")


def test_reasoning_mapping_is_deterministic_and_capability_aware():
    assert reasoning_mapping("visible") == {
        "mode": "visible",
        "think": True,
        "postprocess_hide": False,
        "supported": True,
    }
    assert reasoning_mapping("hidden")["postprocess_hide"] is True
    assert reasoning_mapping("off", supports_disable=False)["supported"] is False
    assert reasoning_mapping("off", supports_disable=True)["think"] is False


def test_chat_request_uses_frozen_parameters_and_stream_false():
    name = ephemeral_model_name("run-001")
    req = build_chat_request(name, "hello", reasoning_mode="visible")
    assert req["stream"] is False
    assert req["think"] is True
    assert req["options"] == {
        "num_ctx": 2048,
        "num_predict": 128,
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": 0,
        "seed": 42,
    }


def test_parity_uses_task_and_format_not_exact_text():
    parent = {
        "task_vector": list(FROZEN_TASK_VECTOR),
        "accuracy": FROZEN_ACCURACY,
        "all_outputs_nonempty": True,
    }
    runtime = {
        "task_vector": list(FROZEN_TASK_VECTOR),
        "accuracy": FROZEN_ACCURACY,
        "all_outputs_nonempty": True,
    }
    result = evaluate_ollama_parity(parent, runtime)
    assert result["pass"] is True
    assert result["exact_text_required"] is False
    assert result["absolute_capability_claimed"] is False


def test_parity_rejects_task_or_format_drift():
    parent = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    assert evaluate_ollama_parity(parent, {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
    })["pass"] is False
    assert evaluate_ollama_parity(parent, {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": False,
    })["pass"] is False


def test_no_runtime_or_downstream_authorization_in_source():
    source = (ROOT / "pipeline/m6.py").read_text(encoding="utf-8")
    assert "import subprocess" not in source
    assert "subprocess.run" not in source
    assert "subprocess.Popen" not in source
    boundary = terminal_boundary()
    assert boundary == {
        "m7_authorized": False,
        "m7_auto_open": False,
        "bulk_training_authorized": False,
        "m6_pass_claim_authorized": False,
    }


def test_preflight_helper_is_runtime_isolated():
    source = (ROOT / "tools/m6_ollama_preflight.py").read_text(encoding="utf-8")
    compile(source, "tools/m6_ollama_preflight.py", "exec")
    assert "from pipeline.m6" not in source
    assert "import pipeline.m6" not in source
