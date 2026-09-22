from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/m6_local_windows_preflight_oneclick.ps1"
PREREG = ROOT / "artifacts/model-training-pipeline/m6/local_windows/PREREGISTRATION.json"
AUTH = ROOT / "artifacts/model-training-pipeline/m6/local_windows/IMPLEMENTATION_AUTHORIZATION.json"


def test_prereg_frozen_identities_and_venue_independence():
    data = json.loads(PREREG.read_text(encoding="utf-8"))
    assert data["status"] == "FROZEN_PREOUTCOME"
    assert data["venue_independence_amendment_git_blob_sha1"] == (
        "5d67202f3103f36736cf0e7973c054cf6df658fd"
    )
    assert data["frozen_artifacts"]["f16"]["sha256"] == (
        "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b"
    )
    assert data["frozen_artifacts"]["q4"]["sha256"] == (
        "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
    )
    assert data["frozen_runtime"]["llama_cpp_commit"] == (
        "ce8caa6e60a03093351d6016a818720e0d46f0fb"
    )


def test_implementation_authorizes_static_qa_but_not_scientific_execution():
    data = json.loads(AUTH.read_text(encoding="utf-8"))
    assert data["status"] == "AUTHORIZED_IMPLEMENTATION_AND_ZERO_SCIENCE_STATIC_QA"
    assert data["static_qa_only"] is True
    assert data["artifact_regeneration_authorized"] is False
    assert data["q4_reconstruction_authorized_in_this_package"] is False
    assert data["ollama_scientific_execution_authorized"] is False


def test_script_is_preflight_only_and_has_required_terminal_classes():
    text = SCRIPT.read_text(encoding="utf-8")
    required = [
        "LOCAL_Q4_ADMITTED",
        "LOCAL_F16_ADMITTED",
        "LOCAL_Q4_AND_F16_ADMITTED",
        "LOCAL_PARENT_ARTIFACTS_NOT_FOUND",
        "LOCAL_PARENT_ARTIFACT_IDENTITY_MISMATCH_ONLY",
        "INVALID_LOCAL_PREFLIGHT_INFRASTRUCTURE",
        "M6_LOCAL_WINDOWS_PREFLIGHT_REPORT.json",
        "model-q4_k_m.gguf",
        "model-f16.gguf",
        "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5",
    ]
    for item in required:
        assert item in text

    forbidden = [
        "convert_hf_to_gguf.py",
        "ollama create",
        "ollama run",
        "ollama pull",
        "ollama rm",
        "/api/chat",
        "/api/generate",
    ]
    lowered = text.lower()
    for item in forbidden:
        assert item.lower() not in lowered


def test_script_does_not_invoke_quantizer_or_llama_cli():
    text = SCRIPT.read_text(encoding="utf-8")
    # Discovery of executable filenames is allowed; execution command shapes are not.
    assert "& $LlamaQuantize" not in text
    assert "& $LlamaCli" not in text
    assert "Start-Process" not in text


def test_bounded_search_not_whole_drive():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "whole_drive_scan = $false" in text
    assert "$SearchRoots += $RepoRoot" in text
    assert "$ParentRoot = Split-Path $RepoRoot -Parent" in text
    assert "Get-PSDrive" not in text


def test_report_keeps_scientific_boundaries_closed():
    text = SCRIPT.read_text(encoding="utf-8")
    for field in [
        "f16_regeneration_executed = $false",
        "hf_to_gguf_conversion_executed = $false",
        "llama_quantize_executed = $false",
        "llama_cli_inference_executed = $false",
        "ollama_create_executed = $false",
        "ollama_chat_executed = $false",
        "scientific_adjudication_executed = $false",
        "q4_reconstruction_authorization_consumed = $false",
    ]:
        assert field in text


def test_branch_name_is_informational_not_scientific_gate():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '$PreferredBranch = "research/model-pipeline-m6-ollama"' in text
    assert "branch_matches_preferred = $BranchMatchesPreferred" in text
    assert "Wrong branch." not in text
    assert "$Branch -ne $ExpectedBranch" not in text


def test_script_reads_exact_script_blob_from_lock_schema():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "$Lock.exact_blobs.script_git_blob_sha1" in text
    assert "$Lock.script_git_blob_sha1" not in text
