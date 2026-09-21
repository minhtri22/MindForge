from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_f16_requalification_harness_never_calls_quantization():
    path = ROOT / "tools/m5_f16_requalification.py"
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    assert "run_quantized_target" not in source
    assert "quantization_executed": False" in source
    assert "quantization_authorized": pass_f16" in source
    assert "OPEN_HIGH_FIDELITY_FAIL" in source
    assert "HIGH_FIDELITY_PASS_QUANTIZATION_NOT_EXECUTED" in source


def test_full_m5_workflow_is_manual_only_during_f16_repair_gate():
    source = (ROOT / ".github/workflows/model-pipeline-m5.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in source
    assert "push:" not in source
    assert "pull_request:" not in source
