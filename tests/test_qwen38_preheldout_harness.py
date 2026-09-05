import argparse
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_qwen38_preheldout_harness import build_certification_workload, validate_sequence_rows
from run_qwen38_track_a_reference_eval import prompt_for


def _case(value: str, *, structured_gold: bool = False) -> dict:
    context = {"note": value}
    if structured_gold:
        context["gold"] = "forbidden truth"
    return {
        "case_id": "A5-D-TEST",
        "family": "A5",
        "input": {
            "user_utterance": value,
            "current_context": context,
            "personal_state": {},
            "available_actions": [],
            "available_local_capabilities": [],
            "external_capabilities": [],
        },
    }


@pytest.mark.parametrize("value", ["gold", "golden", "goldfish"])
def test_gold_substrings_do_not_trigger_leakage(value):
    prompt = prompt_for(_case(value))
    assert value in prompt


def test_structured_gold_key_still_triggers_leakage():
    with pytest.raises(AssertionError, match="forbidden truth/leakage key"):
        prompt_for(_case("ordinary", structured_gold=True))


def test_certification_workload_is_exact_two_passes_of_420():
    development = [{"case_id": f"case-{i}"} for i in range(1, 421)]
    workload = build_certification_workload(development)
    assert len(workload) == 840
    assert [item[2]["case_id"] for item in workload[:420]] == [f"case-{i}" for i in range(1, 421)]
    assert [item[2]["case_id"] for item in workload[420:]] == [f"case-{i}" for i in range(1, 421)]
    assert [item[1] for item in workload[:420]] == [1] * 420
    assert [item[1] for item in workload[420:]] == [2] * 420
    assert [item[0] for item in workload] == list(range(1, 841))


def test_sequence_validation_detects_missing_and_duplicate_indices():
    rows = [{"sequence_index": 1}, {"sequence_index": 2}, {"sequence_index": 2}, {"sequence_index": 4}]
    result = validate_sequence_rows(rows, 4)
    assert result["missing_indices"] == [3]
    assert result["duplicate_indices"] == [2]
    assert result["exact_order"] is False
