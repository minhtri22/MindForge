from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import torch


MODULE_PATH = Path(__file__).resolve().parents[1] / "experiments" / "phase0_local_validate.py"
SPEC = importlib.util.spec_from_file_location("phase0_local_validate", MODULE_PATH)
assert SPEC and SPEC.loader
phase0 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = phase0
SPEC.loader.exec_module(phase0)


def test_model_parameter_scales_are_near_targets() -> None:
    targets = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    for config, target in zip(phase0.ENVELOPE_CONFIGS, targets, strict=True):
        count = phase0.model_parameter_count(phase0.TransformerLM(config))
        assert abs(count - target) / target < 0.20


def test_domain_batch_has_expected_transition() -> None:
    tokens, targets = phase0.make_domain_batch(
        offset=3,
        vocab_size=phase0.TINY_CONFIG.vocab_size,
        batch_size=2,
        context=8,
        seed=1,
        device="cpu",
    )
    assert torch.equal(targets, (tokens + 3) % phase0.TINY_CONFIG.vocab_size)


def test_forward_backward_optimizer_step_cpu() -> None:
    model = phase0.build_model(
        phase0.TINY_CONFIG, seed=2, device="cpu", dtype=torch.float32
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    tokens, targets = phase0.make_random_batch(
        vocab_size=phase0.TINY_CONFIG.vocab_size,
        batch_size=2,
        context=16,
        seed=3,
        device="cpu",
    )
    before = [parameter.detach().clone() for parameter in model.parameters()]
    loss, logits = phase0.training_step(model, optimizer, tokens, targets)
    assert loss > 0
    assert logits.shape == (2, 16, phase0.TINY_CONFIG.vocab_size)
    assert any(not torch.equal(left, right.detach()) for left, right in zip(before, model.parameters(), strict=True))


def test_checkpoint_roundtrip_cpu() -> None:
    result = phase0.checkpoint_roundtrip("cpu")
    assert result["status"] == "PASS", result
