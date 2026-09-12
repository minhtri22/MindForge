from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "run_h3r2r_prospective.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("h3r2r_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_frozen_seed_derivation_matches_registry_anchor():
    runner = load_runner()
    assert runner.derive_prospective_seed("ENV-1", 223691) == 832813
    registry = runner.load_json(ROOT / "PROSPECTIVE_SEED_REGISTRY_v1.json")
    mappings = runner.validate_seed_registry(registry)
    assert len(mappings) == 20
    assert len({int(item["prospective_test_seed"]) for item in mappings}) == 20


def test_runner_source_has_no_representation_fit_route():
    runner = load_runner()
    result = runner.validate_runner_source_contract()
    assert result["status"] == "PASS"
    assert all(result["checks"].values())


class _FakeTableEncoder:
    _fitted = True

    def transform(self, observations):
        return np.asarray(observations, dtype=float)


class _FakeEncoder:
    def encode(self, observations):
        return np.asarray(observations, dtype=float) * 2.0


class _FakeExtractor:
    _fitted = True
    table_encoder = _FakeTableEncoder()
    encoder = _FakeEncoder()


def test_frozen_transform_uses_transform_and_encode_only():
    runner = load_runner()
    observations = np.asarray([[1.0, 2.0], [3.0, 4.0]])
    actual = runner.frozen_transform(_FakeExtractor(), observations)
    np.testing.assert_allclose(actual, observations * 2.0)


def test_readout_families_share_fixed_logistic_contract():
    runner = load_runner()
    linear = runner.readout_spec("linear", 223691)
    degree2 = runner.readout_spec("degree2", 223691)
    assert linear["logistic_regression"] == degree2["logistic_regression"]
    assert degree2["polynomial_degree"] == 2
    assert degree2["include_bias"] is False

    x = np.asarray([[0.0], [1.0], [2.0], [3.0]])
    y = np.asarray([0, 0, 1, 1])
    for family in runner.READOUT_FAMILIES:
        model = runner.build_readout(family, 223691)
        model.fit(x, y)
        assert len(model.predict(x)) == len(y)


def test_unknown_readout_is_rejected():
    runner = load_runner()
    with pytest.raises(runner.H3R2RError):
        runner.build_readout("posthoc", 223691)
