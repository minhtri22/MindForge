from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from mindforge.checkpoint import load_checkpoint, read_checkpoint, save_checkpoint
from mindforge.config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from mindforge.data import deterministic_batch, deterministic_text_split, load_token_array, prepare_data
from mindforge.device import resolve_device
from mindforge.evaluate import bits_per_byte, evaluate_checkpoint, evaluate_tokens
from mindforge.generate import generate
from mindforge.model import TransformerLM, parameter_count
from mindforge.tokenizer import decode, encode, load_tokenizer, metadata, train_tokenizer


FIXTURE = Path(__file__).parent / "fixtures" / "phase1-corpus.txt"


@pytest.fixture()
def prepared(tmp_path: Path) -> dict[str, object]:
    text = FIXTURE.read_text(encoding="utf-8")
    train_text, validation_text = deterministic_text_split(text, 0.25)
    train_path = tmp_path / "train.txt"
    validation_path = tmp_path / "validation.txt"
    train_path.write_text(train_text * 8, encoding="utf-8")
    validation_path.write_text(validation_text * 8, encoding="utf-8")
    tokenizer_path = tmp_path / "tokenizer.json"
    tokenizer = train_tokenizer([train_path, validation_path], tokenizer_path, vocab_size=512)
    manifest = prepare_data(tokenizer_path, train_path, validation_path, tmp_path / "data")
    return {
        "tokenizer": tokenizer,
        "tokenizer_path": tokenizer_path,
        "train_tokens": tmp_path / "data" / "train.npy",
        "validation_tokens": tmp_path / "data" / "validation.npy",
        "manifest": manifest,
    }


def tiny_model(vocab_size: int, seed: int = 7) -> TransformerLM:
    torch.manual_seed(seed)
    return TransformerLM(ModelConfig(vocab_size=vocab_size, d_model=32, n_heads=4, n_layers=1, max_context=16))


def test_default_model_parameter_contract() -> None:
    assert parameter_count(TransformerLM(ModelConfig())) == 10_339_200


@pytest.mark.parametrize(
    "bad",
    [
        {"vocab_size": 0},
        {"d_model": 31, "n_heads": 4},
        {"dropout": 1.0},
    ],
)
def test_model_config_rejects_bad_values(bad: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ModelConfig(**bad)


def test_config_roundtrip_and_unknown_field(tmp_path: Path) -> None:
    config = KernelConfig(data=DataConfig("train.npy", "val.npy", "tokenizer.json"))
    path = tmp_path / "config.json"
    config.save(path)
    assert KernelConfig.load(path) == config
    with pytest.raises(ValueError, match="unknown config fields"):
        KernelConfig.from_dict({"data": {"train_tokens": "a", "validation_tokens": "b", "tokenizer": "c"}, "future": {}})


def test_tokenizer_roundtrip_metadata_and_bounds(prepared: dict[str, object]) -> None:
    tokenizer = load_tokenizer(prepared["tokenizer_path"])
    for text in (
        "Tiếng Việt có dấu — an toàn.",
        "English text stays intact!",
        "Mixed Việt-English 2026, 12.5%, A-42.",
    ):
        ids = encode(tokenizer, text)
        assert ids and min(ids) >= 0 and max(ids) < tokenizer.get_vocab_size()
        assert decode(tokenizer, ids) == text
    info = metadata(prepared["tokenizer_path"], tokenizer)
    assert info["normalizer"]["type"] == "NFC"
    assert info["special_tokens"] == ["<|endoftext|>", "<|unk|>"]
    with pytest.raises(ValueError, match="outside tokenizer vocabulary"):
        decode(tokenizer, [tokenizer.get_vocab_size()])


def test_data_manifest_and_batches_are_deterministic(prepared: dict[str, object]) -> None:
    tokens = load_token_array(prepared["train_tokens"])
    first = deterministic_batch(tokens, context=16, batch_size=2, seed=11, step=3, micro=1)
    second = deterministic_batch(tokens, context=16, batch_size=2, seed=11, step=3, micro=1)
    assert torch.equal(first[0], second[0])
    assert torch.equal(first[1], second[1])
    assert torch.equal(first[0][:, 1:], first[1][:, :-1])
    assert len(prepared["manifest"]["dataset_fingerprint"]) == 64


def test_short_dataset_and_invalid_device_fail_clearly() -> None:
    with pytest.raises(ValueError, match="too short"):
        deterministic_batch(np.arange(8), context=8, batch_size=1, seed=1, step=0)
    with pytest.raises(ValueError, match="device must"):
        resolve_device("tpu")


def test_model_context_and_token_bounds() -> None:
    model = tiny_model(64)
    with pytest.raises(ValueError, match="exceeds max_context"):
        model(torch.zeros((1, 17), dtype=torch.long))
    with pytest.raises(ValueError, match="outside model vocabulary"):
        model(torch.tensor([[64]], dtype=torch.long))


def test_bpb_uses_actual_vietnamese_utf8_bytes() -> None:
    byte_count = len("Việt".encode("utf-8"))
    total_nll = 3.25 * math.log(2) * byte_count
    assert byte_count == 6
    assert bits_per_byte(total_nll, byte_count) == pytest.approx(3.25, abs=1e-12)


def test_evaluation_and_generation_are_deterministic(prepared: dict[str, object]) -> None:
    tokenizer = prepared["tokenizer"]
    model = tiny_model(tokenizer.get_vocab_size())
    tokens = load_token_array(prepared["validation_tokens"])
    first = evaluate_tokens(model, tokens, tokenizer, device="cpu", max_windows=3)
    second = evaluate_tokens(model, tokens, tokenizer, device="cpu", max_windows=3)
    assert first == second
    for prompt in ("Việt Nam", "The model", "Năm 2026, A-42"):
        greedy_a = generate(model, tokenizer, prompt, device="cpu", max_new_tokens=3, seed=9)
        greedy_b = generate(model, tokenizer, prompt, device="cpu", max_new_tokens=3, seed=99)
        sampled_a = generate(model, tokenizer, prompt, device="cpu", max_new_tokens=3, temperature=0.8, top_k=20, seed=9)
        sampled_b = generate(model, tokenizer, prompt, device="cpu", max_new_tokens=3, temperature=0.8, top_k=20, seed=9)
        assert greedy_a["token_ids"] == greedy_b["token_ids"]
        assert sampled_a["token_ids"] == sampled_b["token_ids"]


def test_checkpoint_roundtrip_independent_eval_and_mismatch(prepared: dict[str, object], tmp_path: Path) -> None:
    tokenizer = prepared["tokenizer"]
    model = tiny_model(tokenizer.get_vocab_size())
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    training = TrainingConfig(steps=2, eval_interval=1, checkpoint_interval=1)
    info = metadata(prepared["tokenizer_path"], tokenizer)
    checkpoint = tmp_path / "model.pt"
    save_checkpoint(
        checkpoint,
        model,
        optimizer,
        step=1,
        training_config=training,
        tokenizer_fingerprint=info["sha256"],
        dataset_fingerprint=prepared["manifest"]["dataset_fingerprint"],
        seed=7,
    )
    restored, _, payload = load_checkpoint(
        checkpoint, device="cpu", dtype=torch.float32, model_config=model.config,
        tokenizer_fingerprint=info["sha256"], dataset_fingerprint=prepared["manifest"]["dataset_fingerprint"],
    )
    assert payload["format_version"] == 1 and parameter_count(restored) == parameter_count(model)
    for left, right in zip(model.parameters(), restored.parameters()):
        assert torch.equal(left, right)
    result = evaluate_checkpoint(
        checkpoint, prepared["tokenizer_path"], prepared["validation_tokens"], device="cpu", max_windows=2
    )
    assert result["status"] == "PASS" and result["repeat_delta"] == {"cross_entropy": 0.0, "bits_per_byte": 0.0}
    with pytest.raises(ValueError, match="model config"):
        load_checkpoint(checkpoint, device="cpu", dtype=torch.float32, model_config=replace(model.config, d_model=64))


def test_corrupt_and_missing_checkpoint_fields_fail(tmp_path: Path) -> None:
    corrupt = tmp_path / "corrupt.pt"
    corrupt.write_bytes(b"not a torch checkpoint")
    with pytest.raises(ValueError, match="cannot load checkpoint"):
        read_checkpoint(corrupt)
    incomplete = tmp_path / "incomplete.pt"
    torch.save({"format_version": 1}, incomplete)
    with pytest.raises(ValueError, match="missing fields"):
        read_checkpoint(incomplete)


def test_missing_tokenizer_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing tokenizer"):
        load_tokenizer(tmp_path / "missing.json")
