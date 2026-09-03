from __future__ import annotations

import copy

import pytest
import torch

from mindforge.config import DataConfig, KernelConfig, ModelConfig, RunConfig
from mindforge.model import TransformerLM, create_model, parameter_count
from mindforge.model_contract import TokenModel


def _small_config() -> ModelConfig:
    return ModelConfig(vocab_size=32, d_model=16, n_heads=4, n_layers=1, max_context=8, ff_mult=2)


def test_mks_frozen_default_parameter_count() -> None:
    assert parameter_count(create_model(ModelConfig())) == 10_339_200


def test_mks_transformer_satisfies_runtime_contract() -> None:
    model = create_model(_small_config())
    assert isinstance(model, TokenModel)
    assert model.context_limit == 8
    # Concrete-model vocabulary metadata remains available but is not required
    # by the runtime TokenModel v0 contract.
    assert model.vocab_size == 32


def test_mks_forward_exact_parity_direct_vs_factory() -> None:
    config = _small_config()
    torch.manual_seed(7)
    legacy = TransformerLM(config)
    current = create_model(config)
    current.load_state_dict(copy.deepcopy(legacy.state_dict()))
    tokens = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
    legacy.eval()
    current.eval()
    assert torch.equal(legacy(tokens), current(tokens))


def test_mks_state_dict_keys_unchanged() -> None:
    config = _small_config()
    legacy = TransformerLM(config)
    current = create_model(config)
    assert list(legacy.state_dict()) == list(current.state_dict())


@pytest.mark.parametrize(
    "tokens",
    [
        torch.empty((1, 0), dtype=torch.long),
        torch.ones((1, 9), dtype=torch.long),
        torch.tensor([[32]], dtype=torch.long),
        torch.ones((1, 1, 1), dtype=torch.long),
    ],
)
def test_mks_validation_semantics_preserved(tokens: torch.Tensor) -> None:
    with pytest.raises(ValueError):
        create_model(_small_config())(tokens)


def test_mks_run_config_preserves_kernel_config_compatibility(tmp_path) -> None:
    legacy = KernelConfig(DataConfig("train.npy", "val.npy", "tokenizer.json"))
    path = tmp_path / "config.json"
    legacy.save(path)
    loaded = KernelConfig.load(path)
    assert type(loaded) is KernelConfig
    assert loaded == legacy
    assert isinstance(loaded, RunConfig)
    assert set(loaded.to_dict()) == {"data", "model", "training"}


def test_mks_one_step_training_parity_is_exact() -> None:
    config = _small_config()
    torch.manual_seed(3)
    legacy = TransformerLM(config)
    current = create_model(config)
    current.load_state_dict(copy.deepcopy(legacy.state_dict()))
    optimizer_legacy = torch.optim.AdamW(legacy.parameters(), lr=1e-3)
    optimizer_current = torch.optim.AdamW(current.parameters(), lr=1e-3)
    x = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
    y = torch.tensor([[2, 3, 4, 5]], dtype=torch.long)
    for model, optimizer in ((legacy, optimizer_legacy), (current, optimizer_current)):
        optimizer.zero_grad()
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, 32), y.reshape(-1))
        loss.backward()
        optimizer.step()
    for (left_key, left), (right_key, right) in zip(
        legacy.state_dict().items(), current.state_dict().items()
    ):
        assert left_key == right_key
        assert torch.equal(left, right)
    assert optimizer_legacy.state_dict()["param_groups"] == optimizer_current.state_dict()["param_groups"]
