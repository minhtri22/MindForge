from __future__ import annotations

from pathlib import Path

from pipeline.m5q import (
    Q8_QUANTIZER_TYPE,
    Q8_TARGET_KEY,
    build_q8_quantize_command,
    evaluate_quantized_preservation,
    total_manifest_size,
)

ROOT = Path(__file__).resolve().parents[1]


def test_q8_target_is_frozen_exactly():
    assert Q8_TARGET_KEY == "q8_0"
    assert Q8_QUANTIZER_TYPE == "Q8_0"


def test_q8_quantizer_command_is_exact_and_single_target(tmp_path: Path):
    command = build_q8_quantize_command(
        Path("llama-quantize"),
        tmp_path / "model-f16.gguf",
        tmp_path / "model-q8_0.gguf",
    )
    assert command == [
        "llama-quantize",
        str(tmp_path / "model-f16.gguf"),
        str(tmp_path / "model-q8_0.gguf"),
        "Q8_0",
    ]


def test_quantized_preservation_passes_only_on_f16_task_and_accuracy_identity():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q8 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    result = evaluate_quantized_preservation(f16, q8)
    assert result["pass"] is True
    assert result["comparator"] == "qualified_f16_parent"
    assert result["absolute_capability_claimed"] is False
    assert result["exact_text_required"] is False


def test_quantized_preservation_rejects_task_vector_drift():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q8 = {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
    }
    assert evaluate_quantized_preservation(f16, q8)["pass"] is False


def test_quantized_preservation_rejects_empty_runtime_output():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q8 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": False,
    }
    assert evaluate_quantized_preservation(f16, q8)["pass"] is False


def test_manifest_size_is_sum_of_files():
    assert total_manifest_size(
        {"files": [{"size": 3}, {"size": 4}, {"size": 5}]}
    ) == 12


def test_q8_scientific_module_has_no_q4_execution_path_and_hard_blocks_m6():
    source = (ROOT / "pipeline/m5q.py").read_text(encoding="utf-8")
    assert "Q4_K_M" not in source
    assert "run_m5_qualification" not in source
    assert '"q4_executed": False' in source
    assert '"m6_authorized": False' in source
    assert '"m6_auto_open": False' in source


def test_q8_runner_is_target_specific():
    source = (ROOT / "tools/m5q_q8_qualification.py").read_text(encoding="utf-8")
    compile(source, "tools/m5q_q8_qualification.py", "exec")
    assert "run_q8_qualification" in source
    assert "run_m5_qualification" not in source
