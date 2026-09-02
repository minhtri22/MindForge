from __future__ import annotations

from pathlib import Path

import torch

from mindforge.checkpoint import read_checkpoint
from mindforge.config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from mindforge.data import deterministic_text_split, prepare_data
from mindforge.evaluate import evaluate_checkpoint
from mindforge.generate import generate_checkpoint
from mindforge.tokenizer import train_tokenizer
from mindforge.train import train


FIXTURE = Path(__file__).parent / "fixtures" / "phase1-corpus.txt"


def test_cpu_end_to_end_and_exact_resume(tmp_path: Path) -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    train_text, validation_text = deterministic_text_split(text, 0.25)
    train_path = tmp_path / "train.txt"
    validation_path = tmp_path / "validation.txt"
    train_path.write_text(train_text * 12, encoding="utf-8")
    validation_path.write_text(validation_text * 12, encoding="utf-8")
    tokenizer_path = tmp_path / "tokenizer.json"
    tokenizer = train_tokenizer([train_path, validation_path], tokenizer_path, 512)
    prepare_data(tokenizer_path, train_path, validation_path, tmp_path / "data")
    training = TrainingConfig(
        steps=4, micro_batch=1, accumulation=2, learning_rate=1e-3,
        eval_interval=2, checkpoint_interval=2, eval_windows=2,
        seed=123, device="cpu", dtype="float32",
    )
    model = ModelConfig(
        vocab_size=tokenizer.get_vocab_size(), d_model=32, n_heads=4,
        n_layers=1, max_context=16,
    )
    continuous_config = KernelConfig(
        data=DataConfig(
            str(tmp_path / "data" / "train.npy"), str(tmp_path / "data" / "validation.npy"),
            str(tokenizer_path), str(tmp_path / "continuous"),
        ),
        model=model,
        training=training,
    )
    continuous = train(continuous_config)
    midpoint = tmp_path / "continuous" / "checkpoint-step-2.pt"
    resumed_config = KernelConfig(
        data=DataConfig(
            continuous_config.data.train_tokens, continuous_config.data.validation_tokens,
            continuous_config.data.tokenizer, str(tmp_path / "resumed"),
        ),
        model=model,
        training=training,
    )
    resumed = train(resumed_config, resume=midpoint)
    assert continuous["status"] == resumed["status"] == "PASS"
    left = read_checkpoint(tmp_path / "continuous" / "checkpoint-step-4.pt")
    right = read_checkpoint(tmp_path / "resumed" / "checkpoint-step-4.pt")
    for name in left["model_state"]:
        assert torch.equal(left["model_state"][name], right["model_state"][name])
    assert continuous["final_train_loss"] == resumed["final_train_loss"]
    assert continuous["final_evaluation"] == resumed["final_evaluation"]
    evaluated = evaluate_checkpoint(
        tmp_path / "resumed" / "checkpoint-step-4.pt", tokenizer_path,
        tmp_path / "data" / "validation.npy", device="cpu", max_windows=2,
    )
    generated = generate_checkpoint(
        tmp_path / "resumed" / "checkpoint-step-4.pt", tokenizer_path,
        "Xin chào", device="cpu", max_new_tokens=3, seed=42,
    )
    assert evaluated["status"] == "PASS"
    assert generated["text"]
    assert (tmp_path / "continuous" / "run.json").is_file()
    assert (tmp_path / "continuous" / "metrics.jsonl").is_file()
