import tempfile
from pathlib import Path

import pytest

from tools.research.ppf_l3 import e2, e3, e4


@pytest.fixture(scope="module")
def e4_artifacts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "ppf_l3"
        e2_result = e2.run_e2(root)
        e3_result = e3.run_e3(root)
        e4_result = e4.run_e4(root)
        yield root, e2_result, e3_result, e4_result


def test_e4_exact_allocation_and_replication(e4_artifacts):
    _, _, _, result = e4_artifacts
    assert result["status"] == "PASS"
    assert result["persons"] == 18
    assert result["truth_configs"] == 18
    assert result["standard_configs"] == 10
    assert result["high_risk_configs"] == 8
    assert result["histories"] == 112
    assert result["standard_histories"] == 40
    assert result["high_risk_histories"] == 72
    assert result["reroll_count"] == 0


def test_e4_split_disjoint_and_immutability(e4_artifacts):
    _, _, _, result = e4_artifacts
    assert all(value == 0 for value in result["split_overlap_counts"].values())
    assert result["dev_hash_comparison"]["canonical_unchanged"]
    assert result["validation_hash_comparison"]["canonical_unchanged"]
    assert result["dev_hash_comparison"]["changed_artifacts"] == []
    assert result["validation_hash_comparison"]["changed_artifacts"] == []


def test_e4_structural_holdouts_and_family_coverage(e4_artifacts):
    _, _, _, result = e4_artifacts
    assert result["structural_holdout_count"] >= 3
    holdout_ids = {item["truth_config_id"] for item in result["structural_holdouts"]}
    assert {"final-h02", "final-h04", "final-h07", "final-h08"}.issubset(holdout_ids)
    assert all(result["qa"]["family_evidence"].values())


def test_e4_counterfactual_contracts_and_l2_validity(e4_artifacts):
    _, _, _, result = e4_artifacts
    assert result["counterfactual_template_count"] == 14
    assert result["pair_instance_count"] == 14
    assert result["paired_history_count"] == 28
    assert result["pair_qa_summary"]["pair_pass_count"] == 14
    assert result["pair_qa_summary"]["held_constant_violations"] == 0
    assert result["pair_qa_summary"]["unexpected_changed_paths"] == 0
    assert result["pair_qa_summary"]["missing_required_changes"] == 0
    assert result["visible_events"] == result["l2_valid_events"]
    assert not any(result["qa"]["l2_errors"].values())


def test_e4_identifiability_negative_denominator_and_leakage(e4_artifacts):
    _, _, _, result = e4_artifacts
    assert set(result["identifiability_distribution"]) == {"YES", "PARTIAL", "NO"}
    assert all(result["identifiability_distribution"].values())
    assert result["negative_denominator_count"] > 0
    assert result["future_leak_count"] == 0
    assert result["truth_leak_count"] == 0
    assert result["final_evaluator_protection"]


def test_e4_scope_and_all_gates(e4_artifacts):
    root, e2_result, e3_result, result = e4_artifacts
    assert e2_result["status"] == "PASS"
    assert e3_result["status"] == "PASS"
    assert result["qa"]["regression_checks"] == {
        "l2_60_and_8": True,
        "e0": True,
        "e1": True,
        "e2": True,
        "e2_cf_a": True,
        "e3": True,
    }
    assert all(result["e4_gates"].values())
    assert not (root / "evaluator" / "final").exists()
    assert (root / "evaluator_private" / "final" / "truth").exists()
    assert not result["qa"]["forbidden_paths"]
    assert result["qa"]["scope_violations"] == []
