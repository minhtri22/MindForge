from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/m6_f16_parent_materialize.py"
AUTH_PATH = (
    ROOT
    / "artifacts/model-training-pipeline/m6/f16_parent/IMPLEMENTATION_AUTHORIZATION.json"
)
PREREG_PATH = (
    ROOT
    / "artifacts/model-training-pipeline/m6/f16_parent/PREREGISTRATION.json"
)
RECON_AUTH_PATH = (
    ROOT
    / "artifacts/model-training-pipeline/m6/parent_artifact/"
    "DETERMINISTIC_RECONSTRUCTION_AUTHORIZATION.json"
)

SPEC = importlib.util.spec_from_file_location("m6_f16_parent_materialize", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
MAT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MAT
SPEC.loader.exec_module(MAT)


def _fixture_identity(path: Path, label: str = "f16"):
    size = path.stat().st_size
    sha = MAT.sha256_file(path)
    rows = [{"name": path.name, "size": size, "sha256": sha}]
    return MAT.ArtifactIdentity(
        filename=path.name,
        size=size,
        sha256=sha,
        aggregate_manifest_hash=MAT.sha256_object(rows),
        label=label,
    )


def _future_auth(path: Path, identity: MAT.ArtifactIdentity):
    value = {
        "schema": MAT.FUTURE_EXECUTION_AUTH_SCHEMA,
        "status": MAT.FUTURE_EXECUTION_AUTH_STATUS,
        "program": MAT.PROGRAM,
        "expected_f16": {
            "filename": identity.filename,
            "size_bytes": identity.size,
            "sha256": identity.sha256,
            "aggregate_manifest_hash": identity.aggregate_manifest_hash,
        },
        "reconstruction_authorization_commit": MAT.RECONSTRUCTION_AUTH_COMMIT,
        "reconstruction_authorization_consumed": False,
        "boundaries": {
            "f16_regeneration": False,
            "hf_to_gguf_conversion": False,
            "llama_cli_evaluation": False,
            "fixture_evaluation": False,
            "model_inference": False,
            "scientific_adjudication": False,
            "q4_reconstruction_execution": False,
            "ollama_create": False,
            "ollama_chat": False,
        },
    }
    path.write_text(json.dumps(value), encoding="utf-8")


def test_frozen_f16_identity_matches_preregistration_and_scientific_evidence():
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    frozen = prereg["frozen_f16_identity"]
    assert MAT.F16_FILENAME == frozen["filename"] == "model-f16.gguf"
    assert MAT.F16_SIZE == frozen["size_bytes"] == 994156384
    assert MAT.F16_SHA256 == frozen["sha256"]
    assert MAT.F16_MANIFEST == frozen["aggregate_manifest_hash"]
    assert frozen["scientific_status"] == "PASS_CLOSED"


def test_candidate_requires_filename_size_hash_and_manifest(tmp_path: Path):
    path = tmp_path / "fixture.gguf"
    path.write_bytes(b"f16 fixture bytes")
    identity = _fixture_identity(path)
    assert MAT.inspect_artifact(path, identity)["admitted"] is True

    wrong_name = tmp_path / "other.gguf"
    wrong_name.write_bytes(path.read_bytes())
    result = MAT.inspect_artifact(wrong_name, identity)
    assert result["admitted"] is False
    assert result["checks"]["filename_exact"] is False

    path.write_bytes(b"changed")
    result = MAT.inspect_artifact(path, identity)
    assert result["admitted"] is False


def test_discovery_classifies_missing_and_mismatch(tmp_path: Path):
    missing = MAT.discover_existing([tmp_path / "missing.gguf"])
    assert missing["classification"] == "F16_EXISTING_BYTES_NOT_FOUND"

    present = tmp_path / MAT.F16_FILENAME
    present.write_bytes(b"not frozen f16")
    mismatch = MAT.discover_existing([present])
    assert mismatch["classification"] == "F16_EXISTING_BYTES_IDENTITY_MISMATCH"
    assert mismatch["f16_scientific_status"] == "PASS_CLOSED"


def test_real_execution_is_blocked_without_future_authorization(tmp_path: Path):
    source = tmp_path / "fixture.gguf"
    source.write_bytes(b"fixture")
    with pytest.raises(MAT.F16MaterializationError, match="authorization missing"):
        MAT.persist_existing_file(
            source,
            tmp_path / "out.gguf",
            execution_authorization=tmp_path / "missing.json",
        )


def test_copy_materialization_is_byte_preserving_and_reverified(tmp_path: Path):
    source = tmp_path / "fixture.gguf"
    source.write_bytes(b"byte preserving copy")
    identity = _fixture_identity(source)
    auth = tmp_path / "auth.json"
    _future_auth(auth, identity)

    old_identity = MAT.F16_IDENTITY
    try:
        MAT.F16_IDENTITY = identity
        result = MAT.persist_existing_file(
            source,
            tmp_path / "persisted" / source.name,
            execution_authorization=auth,
        )
    finally:
        MAT.F16_IDENTITY = old_identity

    assert result["classification"] == "ADMITTED_EXISTING_F16_BYTES"
    assert result["source"]["sha256"] == result["persisted"]["sha256"]
    assert result["f16_regeneration_executed"] is False
    assert result["scientific_adjudication_executed"] is False


def test_archive_extraction_is_byte_preserving(tmp_path: Path):
    payload = b"archive serialized f16 fixture"
    archive = tmp_path / "existing.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("model-f16.gguf", payload)

    destination = tmp_path / "model-f16.gguf"
    destination.write_bytes(payload)
    identity = _fixture_identity(destination)
    destination.unlink()

    auth = tmp_path / "auth.json"
    _future_auth(auth, identity)
    old_identity = MAT.F16_IDENTITY
    try:
        MAT.F16_IDENTITY = identity
        result = MAT.extract_existing_archive_member(
            archive,
            "model-f16.gguf",
            destination,
            execution_authorization=auth,
            archive_sha256=MAT.sha256_file(archive),
        )
    finally:
        MAT.F16_IDENTITY = old_identity

    assert destination.read_bytes() == payload
    assert result["persisted"]["admitted"] is True
    assert result["f16_regeneration_executed"] is False


def test_chunk_reassembly_is_concatenation_only(tmp_path: Path):
    pieces = [b"chunk-a-", b"chunk-b-", b"chunk-c"]
    chunks = []
    for index, payload in enumerate(pieces):
        path = tmp_path / f"part-{index:02d}"
        path.write_bytes(payload)
        chunks.append(path)

    destination = tmp_path / "model-f16.gguf"
    destination.write_bytes(b"".join(pieces))
    identity = _fixture_identity(destination)
    destination.unlink()

    auth = tmp_path / "auth.json"
    _future_auth(auth, identity)
    old_identity = MAT.F16_IDENTITY
    try:
        MAT.F16_IDENTITY = identity
        result = MAT.reassemble_existing_chunks(
            chunks,
            destination,
            execution_authorization=auth,
            expected_chunk_sha256=[MAT.sha256_file(path) for path in chunks],
        )
    finally:
        MAT.F16_IDENTITY = old_identity

    assert destination.read_bytes() == b"".join(pieces)
    assert result["persisted"]["admitted"] is True


def test_download_helper_requires_execution_authorization(tmp_path: Path):
    with pytest.raises(MAT.F16MaterializationError, match="authorization missing"):
        MAT.download_existing_object(
            "https://example.invalid/model-f16.gguf",
            tmp_path / MAT.F16_FILENAME,
            execution_authorization=tmp_path / "missing.json",
        )


def test_tool_contains_no_process_execution_or_pipeline_scientific_imports():
    source = TOOL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert "subprocess" not in imported
    assert not any(name.startswith("pipeline") for name in imported)

    call_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.append(node.func.attr)
    assert "Popen" not in call_names
    assert "run" not in call_names
    assert "check_call" not in call_names
    assert "check_output" not in call_names


def test_no_regeneration_or_scientific_entrypoints_exist():
    source = TOOL_PATH.read_text(encoding="utf-8")
    forbidden_symbols = [
        "run_m5_qualification",
        "run_q4_qualification",
        "run_llama_fixture",
        "llama_cli",
        "convert_hf",
        "convert_hf_to_gguf",
        "M5_F16_QUALIFICATION_RESULT",
    ]
    for symbol in forbidden_symbols:
        assert symbol not in source


def test_planning_cli_cannot_materialize_or_mutate():
    source = TOOL_PATH.read_text(encoding="utf-8")
    main = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    direct_names = {
        node.func.id
        for node in ast.walk(main)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "planning_report" in direct_names
    assert "persist_existing_file" not in direct_names
    assert "download_existing_object" not in direct_names
    assert "extract_existing_archive_member" not in direct_names
    assert "reassemble_existing_chunks" not in direct_names


def test_planning_report_keeps_all_scientific_and_downstream_boundaries_closed():
    report = MAT.planning_report([])
    assert report["execution_authorized_now"] is False
    assert report["requires_separate_execution_authorization"] is True
    assert report["frozen_f16"]["scientific_status"] == "PASS_CLOSED"
    assert report["protected_reconstruction_authorization"]["commit"] == (
        "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5"
    )
    assert report["protected_reconstruction_authorization"]["consumed"] is False
    assert all(value is False for value in report["boundaries"].values())


def test_reconstruction_authorization_file_is_unchanged_and_unconsumed():
    auth = json.loads(RECON_AUTH_PATH.read_text(encoding="utf-8"))
    assert auth["mode"] == "DETERMINISTIC_RECONSTRUCTION_ONLY"
    assert auth["execution_state"]["reconstruction_authorization_consumed"] is False
    assert auth["frozen_f16_parent"]["regeneration_authorized"] is False


def test_implementation_authorization_has_no_real_execution_permission():
    auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    assert auth["status"] == "AUTHORIZED_SPECIFICATION_IMPLEMENTATION_ZERO_SCIENCE_ONLY"
    denied = "\n".join(auth["explicitly_not_authorized_now"])
    assert "execute recovery/materialization" in denied
    assert "execute HF-to-GGUF converter" in denied
    assert "run Q4 reconstruction" in denied
