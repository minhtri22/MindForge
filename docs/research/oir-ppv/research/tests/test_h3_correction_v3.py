from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

from pipeline import run_h3_correction_v3 as v3


def test_v1_preservation_inventory_and_hashes_match():
    status = v3._preservation_status()
    assert status["file_count"] >= 208
    assert status["mismatch_count"] == 0
    manifest = v3._read_json(v3.PRESERVATION)
    assert manifest["paired_evidence_count"] == 100
    assert manifest["effective_config_count"] == 100


def test_freeze_refuses_overwrite():
    assert v3.EXEC_MANIFEST.exists() and v3.EXEC_MANIFEST_HASH.exists()
    with pytest.raises(FileExistsError):
        v3.freeze()


def test_frozen_source_drift_fails_fast(monkeypatch):
    original = v3._sha
    monkeypatch.setattr(v3, "_sha", lambda p: "0" * 64 if Path(p).name == "run_h3_closure.py" else original(p))
    with pytest.raises(v3.CorrectionStop, match="CORRECTION_FREEZE_INVALIDATED"):
        v3._verify_frozen_identity()


def test_canonical_hash_is_deterministic_and_sensitive():
    a = {"b": np.array([1, 2], dtype=np.int32), "a": {"x": 1}}
    b = {"a": {"x": 1}, "b": np.array([1, 2], dtype=np.int32)}
    assert v3.canonical_hash(a) == v3.canonical_hash(b)
    assert v3.canonical_hash(a) != v3.canonical_hash({"b": np.array([1, 2], dtype=np.int64), "a": {"x": 1}})
    assert v3.canonical_hash(a) != v3.canonical_hash({"b": np.array([[1, 2]], dtype=np.int32), "a": {"x": 1}})
    assert v3.canonical_hash(a) != v3.canonical_hash({"b": np.array([1, 3], dtype=np.int32), "a": {"x": 1}})


@pytest.mark.parametrize("env_id", ["ENV-1", "ENV-2", "ENV-4"])
def test_all_five_seeds_have_full_causal_isolation(env_id):
    for seed in v3.SEEDS:
        cell = v3._load_v3_cell("L0", env_id, seed)
        assert cell and cell["status"] == "complete"
        for row in cell["interventions"]:
            c = row["causal_isolation"]
            assert all(c[k] for k in ("task_state_same","context_same","labels_same","target_nuisance_changed","non_target_nuisance_same","observations_changed"))


def test_env3_changes_labels_and_remains_inapplicable_all_seeds():
    for seed in v3.SEEDS:
        cell = v3._load_v3_cell("L0", "ENV-3", seed)
        assert cell["status"] == "inapplicable"
        assert all(r["causal_isolation"]["task_state_same"] and r["causal_isolation"]["context_same"] for r in cell["interventions"])
        assert any(not r["causal_isolation"]["labels_same"] for r in cell["interventions"])


def test_all_60_pairs_have_full_factual_identity():
    count = 0
    for learner in v3.CANDIDATES:
        for env in v3.ELIGIBLE_ENVS:
            for seed in v3.SEEDS:
                base = v3._load_v3_cell("L0", env, seed); cand = v3._load_v3_cell(learner, env, seed)
                assert cand["factual_sample_sha256"] == base["factual_sample_sha256"]
                assert cand["task_label_sha256"] == base["task_label_sha256"]
                assert cand["nuisance_target"] == base["nuisance_target"] and cand["nuisance_values"] == base["nuisance_values"]
                for k in ("task_state_sha256","context_sha256"):
                    assert cand["causal_isolation_factual"][k] == base["causal_isolation_factual"][k]
                count += 1
    assert count == 60


def test_all_100_cells_have_v2_schema_and_provenance():
    count = 0
    for learner in v3.LEARNERS:
        for env in v3.ENVS:
            for seed in v3.SEEDS:
                c = v3._load_v3_cell(learner, env, seed)
                assert c and "causal_isolation_factual" in c and "provenance" in c
                assert c["raw_latent_shift_role"] == "SCALE_SENSITIVE_DIAGNOSTIC_ONLY"
                assert c["provenance"]["canonical_hash_algorithm"] == v3.CANONICAL_HASH_ALGORITHM
                count += 1
    assert count == 100


def test_reconciliation_diff_detects_deliberate_scientific_change():
    a = {"x": 1.0, "nested": {"y": 2}}
    b = copy.deepcopy(a); b["nested"]["y"] = 3
    diffs = v3._diff(a, b)
    assert diffs and diffs[0]["path"] == "$.nested.y"


def test_aggregation_recomputed_and_labels_not_copied():
    s = v3._compute_summary()
    assert s["matrix_counts"] == {"complete":75,"failed":0,"inapplicable":25}
    assert all(c["developer_candidate_h3"] == "NOT_SUPPORTED" for c in s["comparisons"])
    assert s["global_developer_candidate_h3"] == "NOT_SUPPORTED"


def test_raw_latent_shift_is_diagnostic_only_not_success_rule():
    m = v3._read_json(v3.EXEC_MANIFEST)
    assert m["raw_latent_shift_role"] == "SCALE_SENSITIVE_DIAGNOSTIC_ONLY"
    rule = m["v1_scientific_identity"]["closure_rule"]["SUPPORTED"]
    assert "invariance" not in rule.lower()


def test_report_enumerates_exact_values_for_every_environment_seed():
    report = v3.REPORT.read_text(encoding="utf-8")
    expected_rows = 0
    for env in v3.ENVS:
        for seed in v3.SEEDS:
            cell = v3._load_v3_cell("L0", env, seed)
            assert cell is not None
            row = f"| {env} | {seed} | `{v3.TARGETS[env]}` | `{cell['nuisance_values']}` |"
            assert row in report
            expected_rows += 1
    assert expected_rows == 20
