from __future__ import annotations

import copy

import pytest
import torch

from mindforge.config import ModelConfig
from mindforge.model import TransformerLM, parameter_count


def _small_config() -> ModelConfig:
    return ModelConfig(vocab_size=32, d_model=16, n_heads=4, n_layers=1, max_context=8, ff_mult=2)


def test_mks_frozen_default_parameter_count() -> None:
    assert parameter_count(TransformerLM(ModelConfig())) == 10_339_200


def test_mks_frozen_forward_is_exact_for_same_state() -> None:
    config = _small_config()
    torch.manual_seed(7)
    left = TransformerLM(config)
    right = TransformerLM(config)
    right.load_state_dict(copy.deepcopy(left.state_dict()))
    tokens = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
    left.eval()
    right.eval()
    assert torch.equal(left(tokens), right(tokens))


def test_mks_frozen_state_dict_keys() -> None:
    config = _small_config()
    model = TransformerLM(config)
    clone = TransformerLM(config)
    clone.load_state_dict(copy.deepcopy(model.state_dict()))
    assert list(model.state_dict()) == list(clone.state_dict())


@pytest.mark.parametrize(
    "tokens",
    [
        torch.empty((1, 0), dtype=torch.long),
        torch.ones((1, 9), dtype=torch.long),
        torch.tensor([[32]], dtype=torch.long),
        torch.ones((1, 1, 1), dtype=torch.long),
    ],
)
def test_mks_frozen_validation_errors(tokens: torch.Tensor) -> None:
    with pytest.raises(ValueError):
        TransformerLM(_small_config())(tokens)
