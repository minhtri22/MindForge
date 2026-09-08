"""Integration coverage for DEV_TASK_008_FIX_03 gates."""

from pathlib import Path

import pytest

from environments import EnvironmentRegistry
from pipeline.controlled_comparison import run_comparison
from pipeline.learners import AutoencoderEncoder, MLPDecoder
from pipeline.run_m3_experiment import (
    DecoderWrapper,
    EncoderWrapper,
    create_extractor,
    create_generator,
)


def test_runner_factories_reject_unknown_types():
    with pytest.raises(ValueError, match="Unknown extractor type"):
        create_extractor({"type": "unknown-encoder"}, 42)
    with pytest.raises(ValueError, match="Unknown generator type"):
        create_generator({"type": "unknown-decoder"}, 42)


def test_runner_factories_expose_actual_real_learner_types():
    extractor = create_extractor(
        {"type": "Autoencoder", "output_dim": 4, "hidden_dim": 8,
         "epochs": 2, "seed": 42},
        42,
    )
    generator = create_generator(
        {"type": "MLPDecoder", "output_dim": 6, "hidden_dims": [8],
         "epochs": 2, "seed": 42},
        42,
    )
    assert isinstance(extractor, EncoderWrapper)
    assert isinstance(extractor.encoder, AutoencoderEncoder)
    assert isinstance(generator, DecoderWrapper)
    assert isinstance(generator.decoder, MLPDecoder)


def test_controlled_comparison_smoke_writes_truthful_artifacts(tmp_path: Path):
    result = run_comparison(
        tmp_path, max_train=120, max_test=60, epochs=3, seed=42
    )
    assert (tmp_path / "controlled_comparison.json").is_file()
    assert (tmp_path / "controlled_comparison.md").is_file()
    assert set(result["metrics"]) == {"placeholder", "untrained", "trained"}
    assert isinstance(result["learning_demonstrated"], bool)
    assert result["metrics"]["trained"]["encoder_initial_loss"] > 0
    assert result["metrics"]["trained"]["decoder_initial_loss"] > 0


@pytest.mark.parametrize(
    ("config_path", "target", "value"),
    [
        ("environments/env1_config.yaml", "identity", "id_1"),
        ("environments/env4_config.yaml", "domain", "domain_A"),
    ],
)
def test_categorical_context_intervention_preserves_schema_and_changes_data(
    config_path: str, target: str, value: str
):
    environment = EnvironmentRegistry.create_from_config_path(config_path, 42)
    data = environment.generate()
    intervened = environment.intervene(data, target, value)
    assert intervened.observations.shape == data.observations.shape
    assert not (intervened.observations == data.observations).all()
