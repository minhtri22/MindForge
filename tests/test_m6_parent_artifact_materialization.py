from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/m6_parent_artifact_materialize.py"

SPEC = importlib.util.spec_from_file_location("m6_parent_materialize", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
MAT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MAT
SPEC.loader.exec_module(MAT)


def _identity_for(path: Path, label: str = "fixture"):
    size = path.stat().st_size
    sha = MAT.sha256_file(path)
    row = [{"name": path.name, "size": size, "sha256": sha}]
    return MAT.ArtifactIdentity(
        filename=path.name,
        size=size,
        sha256=sha,
        aggregate_manifest_hash=MAT.sha256_object(row),
        label=label,
    )


def test_frozen_q4_identity_is_exact():
    assert MAT.Q4_FILENAME == "model-q4_k_m.gguf"
    assert MAT.Q4_SIZE == 397807456
    assert MAT.Q4_SHA256 == (
        "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
    )
    assert MAT.Q4_MANIFEST == (
        "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
    )
    assert MAT.Q4_QUANTIZER_TYPE == "Q4_K_M"


def test_existing_candidate_requires_exact_size_hash_and_manifest(tmp_path: Path):
    candidate = tmp_path / "fixture.gguf"
    candidate.write_bytes(b"exact fixture bytes")
    identity = _identity_for(candidate)
    result = MAT.inspect_artifact(candidate, identity)
    assert result["admitted"] is True

    candidate.write_bytes(b"changed")
    changed = MAT.inspect_artifact(candidate, identity)
    assert changed["admitted"] is False
    assert changed["reason"] == "IDENTITY_MISMATCH"


def test_recovery_is_first_match_only_and_does_not_execute(tmp_path: Path):
    missing = tmp_path / "missing.gguf"
    exact = tmp_path / "fixture.gguf"
    exact.write_bytes(b"recovery")
    identity = _identity_for(exact)

    result = MAT.recover_existing([missing, exact], expected=identity)
    assert result["classification"] == "ADMITTED_EXISTING_BYTES"
    assert result["source"]["path"] == str(exact.resolve())
    assert result["q4_scientific_status"] == "PASS_CLOSED"
    assert result["q4_rerun_authorized"] is False


def test_reconstruction_command_is_exact_q4_k_m():
    command = MAT.build_reconstruction_command(
        Path("llama-quantize"),
        Path("model-f16.gguf"),
        Path("model-q4_k_m.gguf"),
    )
    assert command == [
        "llama-quantize",
        "model-f16.gguf",
        "model-q4_k_m.gguf",
        "Q4_K_M",
    ]


def test_execution_is_hard_blocked_without_separate_authorization(tmp_path: Path):
    with pytest.raises(MAT.MaterializationError, match="authorization file missing"):
        MAT.execute_reconstruction(
            frozen_f16=tmp_path / "model-f16.gguf",
            llama_quantize=tmp_path / "llama-quantize",
            output_q4=tmp_path / "model-q4_k_m.gguf",
            execution_authorization=tmp_path / "missing-authorization.json",
        )


def test_execution_authorization_cannot_reopen_q4_science(tmp_path: Path):
    auth = {
        "schema": "mindforge-model-pipeline-m6-parent-artifact-execution-authorization-v1",
        "status": "AUTHORIZED_ONE_MATERIALIZATION_EXECUTION",
        "program": MAT.PROGRAM,
        "expected_q4_sha256": MAT.Q4_SHA256,
        "expected_q4_size": MAT.Q4_SIZE,
        "boundaries": {
            "q4_scientific_rerun": True,
            "q4_fixture_evaluation": False,
            "scientific_adjudication": False,
            "ollama_create": False,
        },
    }
    path = tmp_path / "auth.json"
    path.write_text(json.dumps(auth), encoding="utf-8")
    with pytest.raises(MAT.MaterializationError, match="reopens Q4 science"):
        MAT.load_execution_authorization(path)


def test_plan_never_authorizes_execution(tmp_path: Path):
    result = MAT.plan([tmp_path / "missing.gguf"])
    assert result["recovery"]["classification"] == "NOT_FOUND_RECOVERY_EXHAUSTED"
    assert result["reconstruction"]["authorized_now"] is False
    assert result["reconstruction"]["requires_separate_execution_authorization"] is True
    assert result["boundaries"]["fixture_evaluation_authorized"] is False
    assert result["boundaries"]["model_inference_authorized"] is False
    assert result["boundaries"]["scientific_adjudication_authorized"] is False
    assert result["boundaries"]["ollama_create_authorized"] is False
    assert result["boundaries"]["ollama_chat_authorized"] is False


def test_tool_has_no_scientific_runner_import_or_fixture_execution():
    source = TOOL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert not any(name.startswith("pipeline") for name in imported_modules)
    assert "run_m2_qualification" not in source
    assert "run_q4_qualification" not in source
    assert "run_llama_fixture" not in source
    assert "M5Q_Q4_QUALIFICATION_RESULT" not in source


def test_subprocess_execution_exists_only_in_reconstruction_function():
    source = TOOL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node

    callers = []
    for name, fn in functions.items():
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr == "run"
            ):
                callers.append(name)
    assert callers == ["execute_reconstruction"]


def test_no_shell_execution_and_no_ollama_runtime_commands():
    source = TOOL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    shell_true = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    shell_true = True
    assert shell_true is False
    assert '"create"' not in source
    assert '"/api/chat"' not in source


def test_cli_main_is_planning_only():
    source = TOOL_PATH.read_text(encoding="utf-8")
    main = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    calls = {
        node.func.id
        for node in ast.walk(main)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "plan" in calls
    assert "execute_reconstruction" not in calls
    assert "persist_admitted_existing" not in calls


def test_manifest_hash_compatibility_with_canonical_json(tmp_path: Path):
    path = tmp_path / "fixture.gguf"
    path.write_bytes(b"manifest")
    manifest = MAT.single_file_manifest(path, "fixture")
    expected_row = [{
        "name": "fixture.gguf",
        "size": len(b"manifest"),
        "sha256": hashlib.sha256(b"manifest").hexdigest(),
    }]
    expected = hashlib.sha256(
        json.dumps(
            expected_row,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    assert manifest["aggregate_hash"] == expected
