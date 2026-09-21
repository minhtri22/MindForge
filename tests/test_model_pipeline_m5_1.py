from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.m5_1_decomposition import (
    adjudicate,
    clone_with_hardlinks,
    file_manifest,
    git_blob_sha1,
    is_tokenizer_asset,
    replace_tokenizer_assets_from_source,
)

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "artifacts/model-training-pipeline/m5_1/PREREGISTRATION.json"


def _prereg():
    return json.loads(PREREG.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("a_pass", "b_pass", "case", "mechanism"),
    [
        (False, True, "A_FAIL_B_PASS", "M2_CANONICAL_TOKENIZER_EXPORT_FIDELITY_DEFECT"),
        (False, False, "A_FAIL_B_FAIL", "PINNED_LLAMA_CPP_CONVERTER_COMPATIBILITY_DEFECT"),
        (True, True, "A_PASS_B_PASS", "INVALID_ENVIRONMENTAL_PARENT_FAILURE_NOT_REPRODUCED"),
        (True, False, "A_PASS_B_FAIL", "INCONSISTENT_PROVENANCE_OR_ARTIFACT_MIXUP"),
    ],
)
def test_adjudication_matrix_is_frozen(a_pass, b_pass, case, mechanism):
    result = adjudicate(a_pass, b_pass, _prereg())
    assert result["case"] == case
    assert result["mechanism"] == mechanism


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("tokenizer.json", True),
        ("tokenizer_config.json", True),
        ("vocab.json", True),
        ("merges.txt", True),
        ("special_tokens_map.json", True),
        ("tokenizer.model", True),
        ("chat_template.jinja", True),
        ("config.json", False),
        ("generation_config.json", False),
        ("model.safetensors", False),
    ],
)
def test_tokenizer_asset_classifier(name, expected):
    assert is_tokenizer_asset(name) is expected


def test_git_blob_sha1_matches_git_known_value(tmp_path: Path):
    path = tmp_path / "x.txt"
    path.write_bytes(b"hello\n")
    assert git_blob_sha1(path) == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_arm_b_replacement_preserves_non_tokenizer_files(tmp_path: Path):
    arm_a = tmp_path / "a"
    arm_a.mkdir()
    (arm_a / "model.safetensors").write_bytes(b"weights")
    (arm_a / "config.json").write_text('{"model":"same"}', encoding="utf-8")
    (arm_a / "tokenizer.json").write_text('{"old":true}', encoding="utf-8")
    (arm_a / "tokenizer_config.json").write_text('{"source":"canonical"}', encoding="utf-8")

    source = tmp_path / "source"
    source.mkdir()
    (source / "tokenizer.json").write_text('{"raw":true}', encoding="utf-8")
    (source / "tokenizer_config.json").write_text('{"source":"pinned"}', encoding="utf-8")
    (source / "vocab.json").write_text('{"a":0}', encoding="utf-8")

    arm_b = tmp_path / "b"
    clone_with_hardlinks(arm_a, arm_b)
    before = file_manifest(arm_a, tokenizer_only=False)
    copied = replace_tokenizer_assets_from_source(arm_b=arm_b, source_snapshot=source)
    after = file_manifest(arm_b, tokenizer_only=False)

    assert before == after
    assert copied == file_manifest(source, tokenizer_only=True)
    assert file_manifest(arm_b, tokenizer_only=True) == copied


def test_preregistration_forbids_rescue_and_quantization():
    prereg = _prereg()
    assert prereg["parent_failure"]["implementation_sha"] == "8c8eba03d71ab4c4463b6811b2cc475465553304"
    assert prereg["parent_failure"]["workflow_run_id"] == 35565868782
    assert prereg["frozen_inputs"]["outtype"] == "f16"
    assert prereg["forbidden"]["production_code_rescue_before_adjudication"] is True
    assert prereg["forbidden"]["llama_cpp_commit_change"] is True
    assert prereg["forbidden"]["quantization_q8_q4"] is True


def test_tokenizer_probe_is_standalone_and_compiles():
    path = ROOT / "tools/m5_1_tokenizer_probe.py"
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    assert "pipeline" not in source
