from __future__ import annotations

import json
from pathlib import Path

from pipeline.m5 import high_fidelity_identity_matches, single_file_gguf_identity

ROOT = Path(__file__).resolve().parents[1]


def test_quantization_lock_is_exact_closed_f16_parent():
    lock = json.loads(
        (ROOT / "docs/model-training-pipeline/quantization/m5_quantization.lock.json").read_text(
            encoding="utf-8"
        )
    )
    assert lock["parent"]["qualified_scientific_commit"] == (
        "2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719"
    )
    assert lock["parent"]["result_hash"] == (
        "0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57"
    )
    assert lock["parent"]["f16"]["sha256"] == (
        "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b"
    )
    assert [row["id"] for row in lock["targets"]] == ["q8_0", "q4_k_m"]
    assert [row["llama_mode"] for row in lock["targets"]] == ["Q8_0", "Q4_K_M"]
    assert all(row["source"] == "f16_parent" for row in lock["targets"])
    assert lock["required_boundaries"]["m6_authorized"] is False
    assert lock["required_boundaries"]["bulk_training_authorized"] is False


def test_quantization_config_freezes_both_targets():
    text = (
        ROOT / "docs/model-training-pipeline/quantization/end_to_end_small_q8_q4.yaml"
    ).read_text(encoding="utf-8")
    assert "quantize: [q8_0, q4_k_m]" in text


def test_single_file_identity_and_parent_match():
    manifest = {
        "topology": "single_file",
        "files": [
            {
                "name": "model-f16.gguf",
                "size": 10,
                "sha256": "a" * 64,
            }
        ],
        "aggregate_hash": "b" * 64,
    }
    expected = {
        "name": "model-f16.gguf",
        "size": 10,
        "sha256": "a" * 64,
        "aggregate_hash": "b" * 64,
    }
    assert single_file_gguf_identity(manifest) == expected
    assert high_fidelity_identity_matches(manifest, expected) is True
    assert high_fidelity_identity_matches(manifest, {**expected, "size": 11}) is False


def test_parent_guard_precedes_quantizer_loop():
    source = (ROOT / "pipeline/m5.py").read_text(encoding="utf-8")
    guard = source.index("high-fidelity parent identity mismatch; quantization is forbidden")
    quantizer = source.index("quant_targets = tuple")
    assert guard < quantizer


def test_quantization_harness_compiles_and_keeps_m6_closed():
    path = ROOT / "tools/m5_quantization_qualification.py"
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    assert 'EXPECTED_TARGETS = ("q8_0", "q4_k_m")' in source
    assert '"m6_authorized": False' in source
    assert '"absolute_capability_claimed": False' in source
    assert "POST_QUANTIZATION_GOVERNANCE_DECISION" in source
