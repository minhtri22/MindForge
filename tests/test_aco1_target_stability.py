from __future__ import annotations
from pathlib import Path

import pytest

from experiments.aco import aco1_target_stability as aco1


def _y_prr_outcomes() -> dict:
    return {
        aco1.A_POLICY: {"auc": 0.70, "retention": 0.80, "final_accuracy": 0.96, "max_accuracy": 1.0},
        aco1.B_POLICY: {"auc": 0.70, "retention": 0.70, "final_accuracy": 0.96, "max_accuracy": 1.0},
        aco1.C_POLICY: {"auc": 0.72, "retention": 0.70, "final_accuracy": 0.96, "max_accuracy": 1.0},
    }


def _records(near: bool, flip: bool) -> list[dict]:
    rows = []
    for seed in aco1.FRESH_SEEDS:
        for boundary in (1, 2, 3):
            rows.append({
                "seed": seed,
                "boundary_index": boundary,
                "hard_target": {"is_Y_PRR": True},
                "margin_diagnostics": {
                    "near_margin": near,
                    "minimum_normalized_margin": 0.25 if near else 3.0,
                },
                "threshold_sensitivity": {"label_flip": flip},
                "integrity": {"valid": True},
            })
    return rows


def test_seed_manifest_frozen_and_disjoint() -> None:
    x = aco1.validate_seed_manifest()
    assert x["count"] == 40
    assert x["unique_count"] == 40
    assert x["manifest_sha256"] == aco1.SEED_MANIFEST_SHA256
    assert x["historical_collisions"] == []
    assert x["protected_collisions"] == []
    assert x["valid"]


def test_parent_contract_identity() -> None:
    x = aco1.frozen_contract_snapshot()
    assert x["valid"]
    assert tuple(x["policies"]) == aco1.POLICIES
    assert x["thresholds"]["STRICT_CURRENT_MIN"] == 0.95
    assert x["thresholds"]["PLASTICITY_BENEFIT_MIN"] == 0.01
    assert x["thresholds"]["RETENTION_MARGIN"] == 1 / 24


def test_y_prr_reconstructed_from_continuous_outcomes() -> None:
    x = aco1.hard_label(_y_prr_outcomes())
    assert x["safe_action_set"] == "A_ONLY"
    assert x["mechanism"] == "MECH{P+R,R}"
    assert x["label"] == aco1.Y_PRR_LABEL
    assert x["is_Y_PRR"]


def test_margin_diagnostic_includes_reference_accuracy() -> None:
    x = aco1.margin_diagnostics(_y_prr_outcomes())
    assert x["m_A_acc"] == pytest.approx(0.01)
    assert x["near_margin"]
    assert x["minimum_normalized_margin"] >= 0


def test_threshold_sensitivity_is_one_at_a_time() -> None:
    x = aco1.threshold_sensitivity(_y_prr_outcomes())
    assert x["canonical_label"] == aco1.Y_PRR_LABEL
    assert set(x["perturbed_labels"]) == {
        "plasticity_minus", "plasticity_plus",
        "retention_minus", "retention_plus",
        "accuracy_minus", "accuracy_plus",
    }
    assert x["label_flip"]


def test_one_shot_adjudicator_all_outcomes() -> None:
    x = aco1.adjudicate_records(_records(True, True))
    assert (x["status"], x["verdict"]) == ("PASS", "HARD_TARGET_MARGIN_INSTABILITY_SUPPORTED")
    x = aco1.adjudicate_records(_records(False, False))
    assert (x["status"], x["verdict"]) == ("NEGATIVE", "HARD_TARGET_MARGIN_INSTABILITY_NOT_SUPPORTED")
    x = aco1.adjudicate_records(_records(True, False))
    assert (x["status"], x["verdict"]) == ("INCONCLUSIVE", "TARGET_STABILITY_INCONCLUSIVE")


def test_support_failure_stops() -> None:
    rows = _records(True, True)
    for row in rows:
        row["hard_target"]["is_Y_PRR"] = row["seed"] == aco1.FRESH_SEEDS[0] and row["boundary_index"] == 1
    x = aco1.adjudicate_records(rows)
    assert (x["status"], x["verdict"]) == ("STOP", "TARGET_STABILITY_SUPPORT_INSUFFICIENT")


def test_fresh_collection_requires_explicit_lock(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(aco1, "EXECUTION_LOCK", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="fresh execution is locked"):
        aco1.collect_fresh_records()


def test_historical_probe_never_uses_fresh_seed() -> None:
    x = aco1._historical_harness_probe()
    assert x["record_count"] == 3
    assert x["all_integrity_valid"]
    assert not x["fresh_seed_used"]
    assert x["seed"] not in set(aco1.FRESH_SEEDS)


def test_preflight_is_zero_science(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(aco1, "DEFAULT_RECORDS", tmp_path / "none.json")
    monkeypatch.setattr(aco1, "EXECUTION_LOCK", tmp_path / "no-lock.json")
    x = aco1.preflight()
    assert x["status"] == "PASS"
    assert x["fresh_seed_execution_attempted"] is False
    assert x["scientific_outcome_generated"] is False
    assert x["checks"]["fresh_result_absent"]
    assert x["checks"]["execution_lock_absent"]


def test_execution_lock_guard_accepts_canonical_nested_schema(tmp_path: Path) -> None:
    lock = {
        "program": "ACO-1",
        "authorized": True,
        "seed_manifest": {"sha256": aco1.SEED_MANIFEST_SHA256},
        "protocol": {"sha256": aco1.sha256_file(aco1.PROTOCOL)},
    }
    aco1._validate_execution_lock(lock)


def test_execution_lock_guard_rejects_missing_nested_hashes() -> None:
    with pytest.raises(RuntimeError, match="execution lock invalid"):
        aco1._validate_execution_lock({"program": "ACO-1", "authorized": True})
