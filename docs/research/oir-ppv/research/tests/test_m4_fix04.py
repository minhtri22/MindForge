"""Regression coverage for DEV_TASK_008_FIX_04 protocol closure."""

import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import yaml

from pipeline.causal_validation import InterventionResult, _collect_failure_cases
from pipeline.run_m3_experiment import (
    PROTOCOL_VERSION,
    _protocol_identity,
    run_m3_experiment,
)


def _intervention(score: float) -> InterventionResult:
    array = np.zeros((2, 1), dtype=float)
    return InterventionResult(
        intervention_target="do(Z)",
        intervention_value="ctx",
        I_before=array,
        I_after=array,
        mean_shift=0.0,
        correlation=1.0,
        invariance_score=score,
        config_hash="test",
        seed=42,
    )


def test_context_failure_uses_frozen_half_threshold():
    failures = _collect_failure_cases([], [_intervention(0.49)])
    assert len(failures) == 1
    assert failures[0]["type"] == "context_leakage"
    assert failures[0]["invariance_score"] == 0.49


def test_context_failure_boundary_at_half_is_not_failure():
    assert _collect_failure_cases([], [_intervention(0.5)]) == []


def test_protocol_identity_matches_frozen_protocol():
    config = yaml.safe_load(Path("pipeline/stress_nuisance.yaml").read_text(encoding="utf-8"))
    identity = _protocol_identity(config)
    assert identity["version"] == PROTOCOL_VERSION
    assert len(identity["sha256"]) == 64


def test_protocol_identity_mismatch_rejected():
    config = yaml.safe_load(Path("pipeline/stress_nuisance.yaml").read_text(encoding="utf-8"))
    config["protocol"]["version"] = "M3-Protocol-v0.invalid"
    with pytest.raises(ValueError, match="Protocol identity mismatch"):
        _protocol_identity(config)


def test_protocol_mismatch_rejected_before_output_creation(tmp_path: Path):
    config = yaml.safe_load(Path("pipeline/stress_nuisance.yaml").read_text(encoding="utf-8"))
    config["protocol"]["version"] = "M3-Protocol-v0.invalid"
    config_path = tmp_path / "bad_protocol.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    output = tmp_path / "should_not_exist"
    with pytest.raises(ValueError, match="Protocol identity mismatch"):
        run_m3_experiment(config_path, output)
    assert not output.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows console compatibility regression")
def test_m2_cli_runs_under_cp1252(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONUTF8"] = "0"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "benchmark.run_benchmark",
            "run",
            "--experiment-id",
            "FIX04-M2-CLI",
            "--env-config",
            "environments/env1_config.yaml",
            "--baseline",
            "B0",
            "--baseline-config",
            "experiments/baselines/b0_config.yaml",
            "--seed",
            "42",
            "--output",
            str(tmp_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        encoding="cp1252",
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("PASS FIX04-M2-CLI:")
    assert (tmp_path / "FIX04-M2-CLI").is_dir()
