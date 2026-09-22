from __future__ import annotations

import inspect

from experiments.model_core.mk1 import h1a_confirmatory


def _passing_summary():
    return {
        "z1": {
            "micro_precision": 0.99,
            "micro_recall": 0.99,
            "macro_f1": 0.98,
            "per_class": [
                {"name": name, "precision": 0.99, "recall": 0.99, "f1": 0.99}
                for name in h1a_confirmatory.Z1_LABELS
            ],
        },
        "z2": {
            "scalars": {
                name: {"count": 10, "mean_nAE": 0.01, "p95_nAE": 0.02}
                for name in ("numeric_value", "ordinal_index", "duration_seconds", "period_seconds")
            }
        },
        "z3": {"scope_relation_accuracy": 0.99},
        "z4": {
            "pooled_precision": 0.99,
            "pooled_recall": 0.99,
            "per_field": [
                {"name": name, "precision": 0.99, "recall": 0.99, "f1": 0.99}
                for name in h1a_confirmatory.Z4_FIELDS
            ],
        },
        "canonical": {"field_accuracy": 0.99},
        "invariance_cluster_consistency": 0.99,
    }


def _support():
    return {
        "z1_positive": {name: 10 for name in h1a_confirmatory.Z1_LABELS},
        "z4_positive": {name: 10 for name in h1a_confirmatory.Z4_FIELDS},
    }


def test_h1a_gate_bundle_passes_only_when_all_absolute_gates_pass() -> None:
    result = h1a_confirmatory.adjudicate_seed(_passing_summary(), _support())
    assert result["status"] == "PASS"
    assert all(result["gates"].values())


def test_h1a_gate_bundle_fails_on_single_preregistered_gate() -> None:
    summary = _passing_summary()
    summary["z1"]["micro_recall"] = 0.949999
    result = h1a_confirmatory.adjudicate_seed(summary, _support())
    assert result["status"] == "FAIL"
    assert result["gates"]["G02_z1_micro_recall"] is False


def test_h1a_supported_class_recall_floor_is_enforced() -> None:
    summary = _passing_summary()
    summary["z4"]["per_field"][0]["recall"] = 0.79
    result = h1a_confirmatory.adjudicate_seed(summary, _support())
    assert result["status"] == "FAIL"
    assert result["gates"]["G09_supported_class_recall_floor"] is False


def test_h1a_confirmatory_module_has_no_training_or_later_hypothesis_path() -> None:
    source = inspect.getsource(h1a_confirmatory)
    forbidden = (
        "train_arm(",
        "optimizer.step(",
        ".backward(",
        "paired_h1b_bootstrap(",
        "h1c_common_field_summary(",
        "h1c_whole_scene_bootstrap(",
    )
    for term in forbidden:
        assert term not in source


def test_five_frozen_seeds_and_checkpoint_contract() -> None:
    assert set(h1a_confirmatory.CHECKPOINTS) == {71001, 71002, 71003, 71004, 71005}
    assert all(len(value["best_pt_sha256"]) == 64 for value in h1a_confirmatory.CHECKPOINTS.values())
