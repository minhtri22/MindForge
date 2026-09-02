"""Phase 2 experiment system tests."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest
import torch

from mindforge.config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from mindforge.experiment import (
    ArmConfig,
    ExperimentManifest,
    MetricsConfig,
    _aggregate_arm,
    _paired_effects,
    _source_tree_hash,
    check_regression,
    execute_runs,
    summarize,
    validate_manifest,
)


def test_manifest_roundtrip(tmp_path: Path) -> None:
    manifest = ExperimentManifest(
        experiment_id="test-exp",
        description="Test experiment",
        baseline=ArmConfig(config="configs/baseline.json", seeds=[101, 202]),
        treatment=ArmConfig(config="configs/treatment.json", seeds=[101, 202]),
    )
    path = tmp_path / "manifest.json"
    manifest.save(path)
    loaded = ExperimentManifest.load(path)
    assert loaded.experiment_id == "test-exp"
    assert loaded.baseline.seeds == [101, 202]
    assert loaded.treatment.config == "configs/treatment.json"


def test_manifest_rejects_unknown_fields(tmp_path: Path) -> None:
    data = {
        "experiment_id": "test",
        "description": "",
        "baseline": {"config": "a.json", "seeds": [1]},
        "treatment": {"config": "b.json", "seeds": [1]},
        "unknown_field": "value",
    }
    with pytest.raises(ValueError, match="unknown manifest fields"):
        ExperimentManifest.from_dict(data)


def test_manifest_requires_matching_seeds(tmp_path: Path) -> None:
    manifest = ExperimentManifest(
        experiment_id="test-exp",
        description="",
        baseline=ArmConfig(config="a.json", seeds=[101]),
        treatment=ArmConfig(config="b.json", seeds=[202]),
    )
    path = tmp_path / "manifest.json"
    manifest.save(path)
    result = validate_manifest(path)
    assert not result["valid"]
    assert any("seeds must be identical" in e for e in result["errors"])


def test_manifest_validates_configs_exist(tmp_path: Path) -> None:
    manifest = ExperimentManifest(
        experiment_id="test-exp",
        description="",
        baseline=ArmConfig(config="configs/missing.json", seeds=[101]),
        treatment=ArmConfig(config="configs/also_missing.json", seeds=[101]),
    )
    path = tmp_path / "manifest.json"
    manifest.save(path)
    result = validate_manifest(path)
    assert not result["valid"]
    assert any("not found" in e for e in result["errors"])


def test_source_tree_hash_deterministic() -> None:
    hash1 = _source_tree_hash()
    hash2 = _source_tree_hash()
    assert hash1 == hash2
    # In test environment without git, hash may be fallback
    assert len(hash1) >= 24


def test_aggregate_arm() -> None:
    metrics = [
        {"seed": 101, "bits_per_byte": 10.0},
        {"seed": 202, "bits_per_byte": 11.0},
        {"seed": 303, "bits_per_byte": 12.0},
    ]
    agg = _aggregate_arm(metrics, "bits_per_byte")
    assert agg is not None
    assert agg["mean"] == pytest.approx(11.0)
    assert agg["median"] == pytest.approx(11.0)
    assert agg["std"] == pytest.approx(1.0, abs=1e-6)
    assert agg["count"] == 3


def test_aggregate_arm_handles_missing() -> None:
    metrics = [
        {"seed": 101, "bits_per_byte": 10.0},
        {"seed": 202, "other": 5.0},
        {"seed": 303, "bits_per_byte": 12.0},
    ]
    agg = _aggregate_arm(metrics, "bits_per_byte")
    assert agg is not None
    assert agg["count"] == 2
    assert agg["mean"] == pytest.approx(11.0)


def test_aggregate_arm_empty_returns_none() -> None:
    assert _aggregate_arm([], "bits_per_byte") is None


def test_paired_effects() -> None:
    baseline = [
        {"seed": 101, "bits_per_byte": 10.0},
        {"seed": 202, "bits_per_byte": 11.0},
        {"seed": 303, "bits_per_byte": 12.0},
    ]
    treatment = [
        {"seed": 101, "bits_per_byte": 9.5},
        {"seed": 202, "bits_per_byte": 10.8},
        {"seed": 303, "bits_per_byte": 12.5},
    ]
    paired = _paired_effects(baseline, treatment, "bits_per_byte")
    assert len(paired) == 3
    assert paired[0]["absolute_effect"] == pytest.approx(-0.5)
    assert paired[0]["relative_effect"] == pytest.approx(-0.05)
    assert paired[1]["absolute_effect"] == pytest.approx(-0.2)
    assert paired[2]["absolute_effect"] == pytest.approx(0.5)


def test_paired_effects_unaligned_seeds() -> None:
    baseline = [{"seed": 101, "bits_per_byte": 10.0}]
    treatment = [{"seed": 999, "bits_per_byte": 9.0}]
    paired = _paired_effects(baseline, treatment, "bits_per_byte")
    assert len(paired) == 0


def test_check_regression_passes_clean(tmp_path: Path) -> None:
    # Create a mock manifest and summary
    manifest = ExperimentManifest(
        experiment_id="test-regression",
        description="",
        baseline=ArmConfig(config="configs/phase2_baseline.json", seeds=[101, 202, 303]),
        treatment=ArmConfig(config="configs/phase2_treatment.json", seeds=[101, 202, 303]),
    )
    manifest_path = tmp_path / "manifest.json"
    manifest.save(manifest_path)

    summary = {
        "experiment_id": "test-regression",
        "status": "PASS",
        "manifest_hash": manifest.manifest_hash(),
        "baseline": {
            "primary": {"mean": 10.0, "std": 0.5, "values": [9.5, 10.0, 10.5]}
        },
        "treatment": {
            "primary": {"mean": 9.8, "std": 0.4, "values": [9.4, 9.8, 10.2]}
        },
    }

    # Mock the summarize function to return our summary
    import mindforge.experiment as exp_module
    original_summarize = exp_module.summarize
    exp_module.summarize = lambda _: summary
    try:
        result = check_regression(manifest_path, thresholds={"baseline_bpb_cv_max": 0.10})
        assert result["status"] == "PASS"
        assert result["checks"]["baseline_bpb_cv"]["passed"]
    finally:
        exp_module.summarize = original_summarize


def test_check_regression_fails_high_variance(tmp_path: Path) -> None:
    manifest = ExperimentManifest(
        experiment_id="test-regression-high",
        description="",
        baseline=ArmConfig(config="configs/phase2_baseline.json", seeds=[101, 202, 303]),
        treatment=ArmConfig(config="configs/phase2_treatment.json", seeds=[101, 202, 303]),
    )
    manifest_path = tmp_path / "manifest.json"
    manifest.save(manifest_path)

    summary = {
        "experiment_id": "test-regression-high",
        "status": "PASS",
        "manifest_hash": manifest.manifest_hash(),
        "baseline": {
            "primary": {"mean": 10.0, "std": 2.0, "values": [8.0, 10.0, 12.0]}  # CV = 20% > 10%
        },
        "treatment": {"primary": {"mean": 9.8, "std": 0.4, "values": [9.4, 9.8, 10.2]}},
    }

    import mindforge.experiment as exp_module
    original_summarize = exp_module.summarize
    exp_module.summarize = lambda _: summary
    try:
        result = check_regression(manifest_path, thresholds={"baseline_bpb_cv_max": 0.10})
        assert result["status"] == "REVISE"
        assert not result["checks"]["baseline_bpb_cv"]["passed"]
    finally:
        exp_module.summarize = original_summarize


def test_duplicate_run_protection(tmp_path: Path) -> None:
    """Test that existing run directories are protected by default."""
    manifest = ExperimentManifest(
        experiment_id="test-dup",
        description="",
        baseline=ArmConfig(config="configs/phase2_baseline.json", seeds=[101]),
        treatment=ArmConfig(config="configs/phase2_treatment.json", seeds=[101]),
    )
    path = tmp_path / "manifest.json"
    manifest.save(path)

    # Create a dummy run directory with PASS status in the expected location
    run_dir = Path("runs/test-dup/baseline/seed-101")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps({"status": "PASS", "seed": 101}))

    # The execute_runs function uses ROOT / "runs" / manifest.experiment_id
    # ROOT is Path(__file__).resolve().parents[2] which is the repo root
    try:
        result = execute_runs(path, allow_dirty=True, force_new=False)
        # Should skip the existing run, not fail
        assert result["skipped"] >= 1
    finally:
        if run_dir.exists():
            shutil.rmtree(run_dir)


def test_missing_run_detected(tmp_path: Path) -> None:
    """Test that missing runs are detected in summarize."""
    manifest = ExperimentManifest(
        experiment_id="test-missing",
        description="",
        baseline=ArmConfig(config="configs/phase2_baseline.json", seeds=[101, 202]),
        treatment=ArmConfig(config="configs/phase2_treatment.json", seeds=[101, 202]),
    )
    manifest_path = tmp_path / "manifest.json"
    manifest.save(manifest_path)

    # Don't create any runs - summarize should return INCOMPLETE
    result = summarize(manifest_path)
    assert result["status"] == "INCOMPLETE"
    assert "missing" in result


def test_config_hash_stability() -> None:
    """Test that config hash is stable for same content."""
    from mindforge.experiment import _config_hash
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"a": 1, "b": 2}, f, sort_keys=True)
        path = f.name

    try:
        h1 = _config_hash(path)
        h2 = _config_hash(path)
        assert h1 == h2
        assert len(h1) == 64
    finally:
        Path(path).unlink()


def test_experiment_manifest_hash() -> None:
    """Test manifest hash is deterministic."""
    manifest = ExperimentManifest(
        experiment_id="hash-test",
        description="",
        baseline=ArmConfig(config="a.json", seeds=[101]),
        treatment=ArmConfig(config="b.json", seeds=[101]),
    )
    h1 = manifest.manifest_hash()
    h2 = manifest.manifest_hash()
    assert h1 == h2
    assert len(h1) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])