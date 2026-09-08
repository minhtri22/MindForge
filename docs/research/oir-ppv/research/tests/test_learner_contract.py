"""Shared contract and fidelity tests for EXP-LRN-001 reference learners."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.learners import PCAEncoder, LearnerRegistry, create_learner_from_config
from pipeline.learners_extended import (
    DANNSurrogateEncoder,
    IRMStyleEncoderSurrogate,
    MLPEncoderTrainable,
    VAEEncoder,
)
from pipeline.run_m3_experiment import _apply_overrides


@pytest.fixture
def classification_data():
    rng = np.random.default_rng(1234)
    X = rng.normal(size=(160, 12)).astype(float)
    y = (X[:, 0] + 0.5 * X[:, 1] > 0).astype(int)
    context = np.column_stack([
        (X[:, 2] > 0).astype(int),
        (X[:, 3] > 0).astype(int),
    ])
    return X, y, context


def _assert_representation_contract(encoder, X, labels=None, context=None):
    fit_meta = encoder.fit(X, context=context, labels=labels)
    assert fit_meta["status"] == "fitted"
    encoded = encoder.encode(X[:16])
    assert encoded.shape == (16, encoder.get_output_dim())
    assert np.isfinite(encoded).all()
    assert encoder.get_config_hash() == encoder.get_config_hash()
    return fit_meta, encoded


def test_pca_contract(classification_data):
    X, _, _ = classification_data
    _assert_representation_contract(PCAEncoder(output_dim=8, seed=42), X)


def test_manifest_json_round_trip_preserves_numeric_override_identity():
    base = {"shortcut": {"test_conditional_means": {0: 0.0, 1: 0.0, 2: 0.0}}}
    override_after_json = {
        "shortcut": {
            "test_conditional_means": {"0": 1.5, "1": 0.0, "2": -1.5}
        }
    }
    effective = _apply_overrides(base, override_after_json)
    assert effective["shortcut"]["test_conditional_means"] == {
        0: 1.5,
        1: 0.0,
        2: -1.5,
    }


def test_mlp_is_supervised_and_trainable(classification_data):
    X, y, context = classification_data
    enc = MLPEncoderTrainable(output_dim=8, hidden_dims=[16], epochs=4, seed=42)
    meta, _ = _assert_representation_contract(enc, X, y, context)
    assert meta["fidelity"] == "adapted"
    assert meta["objective"] == "cross_entropy"
    assert np.isfinite(meta["final_loss"])
    with pytest.raises(ValueError):
        MLPEncoderTrainable(output_dim=8, epochs=1).fit(X)


def test_vae_has_reconstruction_and_kl(classification_data):
    X, _, _ = classification_data
    enc = VAEEncoder(output_dim=8, hidden_dim=16, epochs=4, seed=42)
    meta, _ = _assert_representation_contract(enc, X)
    assert meta["fidelity"] == "adapted"
    assert "KL" in meta["objective"]
    assert meta["final_kl"] >= 0.0
    assert np.isfinite(meta["final_reconstruction"])


def test_irm_consumes_domain_context(classification_data):
    X, y, context = classification_data
    enc = IRMStyleEncoderSurrogate(
        output_dim=8, hidden_dim=16, epochs=4, irm_penalty_weight=1.0, seed=42
    )
    meta, _ = _assert_representation_contract(enc, X, y, context)
    assert meta["fidelity"] == "surrogate"
    assert meta["canonical_irm"] is False
    assert meta["domain_count"] > 1
    assert meta["domain_signal_available"] is True


def test_dann_has_domain_signal_and_gradient_reversal_path(classification_data):
    X, y, context = classification_data
    enc = DANNSurrogateEncoder(
        output_dim=8, hidden_dim=16, epochs=4, domain_penalty_weight=0.5, seed=42
    )
    meta, _ = _assert_representation_contract(enc, X, y, context)
    assert meta["fidelity"] == "adapted"
    assert "gradient reversal" in meta["method"]
    assert meta["domain_count"] > 1
    assert meta["domain_signal_available"] is True


@pytest.mark.parametrize("learner_type", ["PCA", "MLPTrainable", "VAE", "IRMStyle", "DANN"])
def test_production_registry_contains_reference_learners(learner_type):
    # Importing the production runner must itself make L0-L4 available; tests
    # must not depend on an accidental prior import for registry side effects.
    import pipeline.run_m3_experiment  # noqa: F401
    assert learner_type in LearnerRegistry.list_encoders()


def test_factory_can_create_all_reference_learners():
    configs = [
        {"type": "PCA", "output_dim": 8},
        {"type": "MLPTrainable", "output_dim": 8, "epochs": 1},
        {"type": "VAE", "output_dim": 8, "epochs": 1},
        {"type": "IRMStyle", "output_dim": 8, "epochs": 1},
        {"type": "DANN", "output_dim": 8, "epochs": 1},
    ]
    for config in configs:
        learner = create_learner_from_config(config, "encoder", seed=42)
        assert learner.get_output_dim() == 8


def test_deterministic_seed42_for_all_trainable_learners(classification_data):
    X, y, context = classification_data
    factories = [
        lambda: MLPEncoderTrainable(output_dim=6, hidden_dims=[12], epochs=3, seed=42),
        lambda: VAEEncoder(output_dim=6, hidden_dim=12, epochs=3, seed=42),
        lambda: IRMStyleEncoderSurrogate(output_dim=6, hidden_dim=12, epochs=3, seed=42),
        lambda: DANNSurrogateEncoder(output_dim=6, hidden_dim=12, epochs=3, seed=42),
    ]
    for factory in factories:
        left, right = factory(), factory()
        if isinstance(left, VAEEncoder):
            left.fit(X)
            right.fit(X)
        else:
            left.fit(X, context=context, labels=y)
            right.fit(X, context=context, labels=y)
        np.testing.assert_allclose(left.encode(X[:20]), right.encode(X[:20]), rtol=1e-6, atol=1e-7)
