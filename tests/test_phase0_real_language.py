from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import torch
from tokenizers import Tokenizer, decoders, normalizers, pre_tokenizers
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer


EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"
sys.path.insert(0, str(EXPERIMENTS))

import phase0_real_language as real  # noqa: E402
import phase0_real_language_common as common  # noqa: E402


def tiny_tokenizer() -> Tokenizer:
    tokenizer = Tokenizer(BPE(unk_token="<|unk|>"))
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = BpeTrainer(
        vocab_size=300,
        min_frequency=1,
        special_tokens=["<|endoftext|>", "<|unk|>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    tokenizer.train_from_iterator(
        [
            "Xin chào Việt Nam. Đây là dữ liệu thử nghiệm.",
            "Hello world. This is deterministic test data.",
            "Hôm nay deploy model mới, validation loss giảm.",
        ],
        trainer=trainer,
    )
    return tokenizer


def test_dataset_split_is_deterministic_and_language_scoped() -> None:
    assert real.split_for_article("vi", "123") == real.split_for_article("vi", "123")
    assert real.split_for_article("en", "123") == real.split_for_article("en", "123")
    values = {real.split_for_article("vi", str(index)) for index in range(1000)}
    assert values == {"train", "validation"}


def test_fingerprint_is_deterministic() -> None:
    payload = "Tiếng Việt + English".encode("utf-8")
    assert common.sha256_bytes(payload) == common.sha256_bytes(payload)
    assert common.sha256_bytes(payload) != common.sha256_bytes(payload + b"!")


def test_tokenizer_roundtrip_and_valid_ids() -> None:
    tokenizer = tiny_tokenizer()
    text = "Tiếng Việt có dấu — English 2026, 12.5%!"
    ids = tokenizer.encode(text).ids
    assert ids
    assert min(ids) >= 0
    assert max(ids) < tokenizer.get_vocab_size()
    assert tokenizer.decode(ids, skip_special_tokens=False) == text
    unk_id = tokenizer.token_to_id("<|unk|>")
    assert unk_id is not None
    assert ids.count(unk_id) == 0


def test_staged_pool_and_batch_are_deterministic() -> None:
    tokens = np.arange(20_000, dtype=np.int32) % 257
    first = common.staged_pool(tokens, 10_000)
    second = common.staged_pool(tokens, 10_000)
    assert np.array_equal(first, second)
    x1, y1 = common.deterministic_batch(
        first, context=32, batch_size=2, seed=7, step=11, device="cpu"
    )
    x2, y2 = common.deterministic_batch(
        first, context=32, batch_size=2, seed=7, step=11, device="cpu"
    )
    assert torch.equal(x1, x2)
    assert torch.equal(y1, y2)
    assert torch.equal(x1[:, 1:], y1[:, :-1])


def test_bpb_calculation_for_uniform_model() -> None:
    tokenizer = tiny_tokenizer()
    ids = np.asarray(
        tokenizer.encode("Hello world. Xin chào Việt Nam. " * 50).ids,
        dtype=np.int32,
    )

    class UniformModel(torch.nn.Module):
        def __init__(self, vocab_size: int) -> None:
            super().__init__()
            self.vocab_size = vocab_size

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return torch.zeros((*x.shape, self.vocab_size), dtype=torch.float32)

    model = UniformModel(tokenizer.get_vocab_size())
    result = common.evaluate_tokens(
        model, ids, tokenizer, context=32, device="cpu", max_windows=4
    )
    expected_bits_per_token = math.log2(tokenizer.get_vocab_size())
    expected_bpb = (
        expected_bits_per_token * result["predicted_tokens"] / result["represented_utf8_bytes"]
    )
    assert result["status"] == "PASS"
    assert math.isclose(result["bits_per_token"], expected_bits_per_token, rel_tol=1e-6)
    assert math.isclose(result["bits_per_byte"], expected_bpb, rel_tol=1e-6)


def test_bpb_uses_actual_vietnamese_utf8_byte_count() -> None:
    text = "Việt"
    byte_count = len(text.encode("utf-8"))
    expected_bpb = 3.25
    total_nll = expected_bpb * math.log(2) * byte_count
    assert byte_count == 6
    assert math.isclose(
        common.bits_per_byte_from_nll(total_nll, byte_count),
        expected_bpb,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


def test_eval_and_generation_are_deterministic() -> None:
    tokenizer = tiny_tokenizer()
    config = common.LMConfig(
        vocab_size=tokenizer.get_vocab_size(), d_model=32, n_heads=4, n_layers=1, max_context=32
    )
    model = common.build_model(config, seed=9, device="cpu", dtype=torch.float32)
    tokens = np.asarray(tokenizer.encode("Hello world. Xin chào Việt Nam. " * 60).ids, dtype=np.int32)
    first = common.evaluate_tokens(model, tokens, tokenizer, context=32, device="cpu", max_windows=3)
    second = common.evaluate_tokens(model, tokens, tokenizer, context=32, device="cpu", max_windows=3)
    assert first == second
    generation = common.generation_sanity(
        model, tokenizer, ["Xin chào", "Hello"], device="cpu", seed=123, max_new_tokens=4
    )
    assert generation["status"] == "PASS"
    assert generation["deterministic_same_seed"] is True


def test_checkpoint_can_be_loaded_and_evaluated(tmp_path: Path) -> None:
    tokenizer = tiny_tokenizer()
    config = common.LMConfig(
        vocab_size=tokenizer.get_vocab_size(), d_model=32, n_heads=4, n_layers=1, max_context=32
    )
    model = common.build_model(config, seed=10, device="cpu", dtype=torch.float32)
    optimizer = common.build_optimizer(model)
    checkpoint_path = tmp_path / "checkpoint.pt"
    metadata = {"purpose": "unit-test"}
    saved = common.save_checkpoint(
        checkpoint_path, model, optimizer, step=3, config=config, metadata=metadata
    )
    restored, _, payload = common.load_checkpoint(
        checkpoint_path, device="cpu", dtype=torch.float32
    )
    tokens = np.asarray(tokenizer.encode("Hello world. Xin chào. " * 50).ids, dtype=np.int32)
    before = common.evaluate_tokens(model, tokens, tokenizer, context=32, device="cpu", max_windows=2)
    after = common.evaluate_tokens(restored, tokens, tokenizer, context=32, device="cpu", max_windows=2)
    assert saved["sha256"]
    assert payload["step"] == 3
    assert before == after
