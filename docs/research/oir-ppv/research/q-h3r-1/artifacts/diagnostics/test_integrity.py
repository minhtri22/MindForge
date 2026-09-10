from __future__ import annotations

import json
from pathlib import Path


QH3R_ROOT = Path(__file__).resolve().parents[2]


def qh3r_path(relative: str) -> Path:
    return QH3R_ROOT / relative


def test_diagnostic_never_uses_frozen_test_split():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    assert summary["test_split_accessed"] is False
    assert summary["h3r_execute_decisive_called"] is False


def test_access_log_unchanged():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    assert summary["access_log_sha256_before"] == summary["access_log_sha256_after"]


def test_raw_h3r_evidence_unchanged():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    assert summary["h3r_raw_tree_sha256_before"] == summary["h3r_raw_tree_sha256_after"]


def test_seeds_disjoint():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    assert summary["seed_disjoint"] is True


def test_shared_probe_contract_frozen():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    contract = summary["shared_probe_contract"]
    assert contract == {
        "C": 1.0,
        "family": "LogisticRegression",
        "max_iter": 1000,
        "penalty": "l2",
        "same_config_across_representations_within_seed": True,
        "solver": "lbfgs",
    }


def test_dataset_manifest_is_train_val_only():
    manifest = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_dataset_manifest.json").read_text(encoding="utf-8"))
    assert manifest
    assert all(row["splits_accessed"] == ["train", "val"] for row in manifest)
    assert all(row["test_split_accessed"] is False for row in manifest)


def test_noise_contract_guards_passed():
    summary = json.loads(qh3r_path("artifacts/diagnostics/qh3r1_diagnostic_summary.json").read_text(encoding="utf-8"))
    assert summary["categorical_channels_preserved"] is True
    assert summary["numeric_noise_within_delta"] is True
    assert summary["noise_delta"] == 0.1


def test_cross_analysis_joins_are_explicit():
    summary = json.loads(qh3r_path("artifacts/derived/published_forensic_summary.json").read_text(encoding="utf-8"))
    assert summary["h2_h3r"]["join_key"] == "learner+environment"
    assert summary["h1_h3r"]["join_key"] == "learner+environment"
    assert summary["h2_h3r"]["matched"] == 12
    assert summary["h1_h3r"]["matched"] == 16


def test_no_decisive_execution_call_in_diagnostic_source():
    source = qh3r_path("artifacts/diagnostics/run_diagnostics.py").read_text(encoding="utf-8")
    assert "execute_decisive(" not in source
