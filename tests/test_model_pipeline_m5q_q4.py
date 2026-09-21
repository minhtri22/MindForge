from __future__ import annotations

import json
from pathlib import Path

from pipeline.m5q_q4 import (
    Q4_QUANTIZER_TYPE,
    Q4_TARGET_KEY,
    build_q4_quantize_command,
    evaluate_q4_preservation,
    load_q4_contract,
    total_manifest_size,
)

ROOT = Path(__file__).resolve().parents[1]


def test_q4_contract_is_pre_exposure_and_sequence_valid():
    contracts = load_q4_contract(ROOT)
    prereg = contracts["preregistration"]
    authorization = contracts["authorization"]
    exposure = contracts["exposure"]["q4_outcome_exposure"]

    assert prereg["claim_scope"]["targets"][1] == "q4_k_m"
    assert prereg["target_order"]["execution_order"][1] == "q4_k_m"
    assert authorization["execution_class"] == (
        "FORMAL_REPLICATION_QUALIFICATION_UNDER_PRE_EXPOSURE_PREREGISTERED_CONTRACT"
    )
    assert exposure["prior_out_of_protocol_outcome_exposure"] is True
    assert exposure["may_be_used_for_tuning"] is False
    assert exposure["may_define_new_q4_thresholds"] is False
    assert exposure["may_be_claimed_as_formal_q4_pass"] is False


def test_q4_target_is_frozen_exactly():
    assert Q4_TARGET_KEY == "q4_k_m"
    assert Q4_QUANTIZER_TYPE == "Q4_K_M"


def test_q4_quantizer_command_is_exact_and_single_target(tmp_path: Path):
    command = build_q4_quantize_command(
        Path("llama-quantize"),
        tmp_path / "model-f16.gguf",
        tmp_path / "model-q4_k_m.gguf",
    )
    assert command == [
        "llama-quantize",
        str(tmp_path / "model-f16.gguf"),
        str(tmp_path / "model-q4_k_m.gguf"),
        "Q4_K_M",
    ]


def test_q4_preservation_passes_only_on_f16_task_and_accuracy_identity():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q4 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    result = evaluate_q4_preservation(f16, q4)
    assert result["pass"] is True
    assert result["comparator"] == "qualified_f16_parent"
    assert result["absolute_capability_claimed"] is False
    assert result["exact_text_required"] is False


def test_q4_preservation_rejects_task_vector_drift():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q4 = {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
    }
    assert evaluate_q4_preservation(f16, q4)["pass"] is False


def test_q4_preservation_rejects_empty_runtime_output():
    f16 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": True,
    }
    q4 = {
        "task_vector": [False, False],
        "accuracy": 0.0,
        "all_outputs_nonempty": False,
    }
    assert evaluate_q4_preservation(f16, q4)["pass"] is False


def test_manifest_size_is_sum_of_files():
    assert total_manifest_size(
        {"files": [{"size": 3}, {"size": 4}, {"size": 5}]}
    ) == 12


def test_q4_scientific_module_is_target_specific_and_hard_blocks_downstream():
    source = (ROOT / "pipeline/m5q_q4.py").read_text(encoding="utf-8")
    assert "run_m5_qualification" not in source
    assert "run_q8_qualification" not in source
    assert '"q8_executed": False' in source
    assert '"m6_authorized": False' in source
    assert '"m6_auto_open": False' in source
    assert '"post_exposure_thresholds_added": False' in source
    assert "strict_compression_ordering" not in source


def test_q4_runner_is_target_specific():
    source = (ROOT / "tools/m5q_q4_qualification.py").read_text(encoding="utf-8")
    compile(source, "tools/m5q_q4_qualification.py", "exec")
    assert "run_q4_qualification" in source
    assert "run_m5_qualification" not in source
    assert "run_q8_qualification" not in source


def test_exposed_outcome_values_are_not_copied_into_q4_implementation():
    exposure = json.loads(
        (
            ROOT
            / "artifacts/model-training-pipeline/m5_quantization/Q4_OUTCOME_EXPOSURE.json"
        ).read_text(encoding="utf-8")
    )
    q4 = exposure["q4_outcome_exposure"]
    observed = q4["observed_artifact"]
    replay = q4["accidental_replay"]
    forbidden = [
        str(observed["sha256"]),
        str(observed["aggregate_manifest_hash"]),
        str(observed["size"]),
        str(replay["combined_result_hash"]),
    ]

    paths = [
        ROOT / "pipeline/m5q_q4.py",
        ROOT / "tools/m5q_q4_qualification.py",
        ROOT / ".github/workflows/model-pipeline-m5q-q4-preflight.yml",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert all(value not in combined for value in forbidden)
