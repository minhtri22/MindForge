"""Versioned checkpoint save/load with deterministic resume state."""

from __future__ import annotations

import os
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .config import ModelConfig, TrainingConfig
from .model import TransformerLM
from .tokenizer import sha256_file


FORMAT_VERSION = 1
REQUIRED_FIELDS = {
    "format_version",
    "model_state",
    "optimizer_state",
    "step",
    "model_config",
    "training_config",
    "tokenizer_fingerprint",
    "dataset_fingerprint",
    "seed",
    "metadata",
    "rng_state",
}


def capture_rng_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
    }
    if hasattr(torch, "xpu") and torch.xpu.is_available() and hasattr(torch.xpu, "get_rng_state_all"):
        state["xpu"] = torch.xpu.get_rng_state_all()
    if torch.cuda.is_available():
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state


def restore_rng_state(state: dict[str, Any]) -> None:
    try:
        random.setstate(state["python"])
        np.random.set_state(state["numpy"])
        torch.set_rng_state(state["torch"])
        if "xpu" in state and hasattr(torch.xpu, "set_rng_state_all"):
            torch.xpu.set_rng_state_all(state["xpu"])
        if "cuda" in state and torch.cuda.is_available():
            torch.cuda.set_rng_state_all(state["cuda"])
    except (KeyError, TypeError, RuntimeError) as error:
        raise ValueError(f"invalid checkpoint RNG state: {error}") from error


def save_checkpoint(
    path: str | Path,
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    *,
    step: int,
    training_config: TrainingConfig,
    tokenizer_fingerprint: str,
    dataset_fingerprint: str,
    seed: int,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if step < 0:
        raise ValueError("checkpoint step cannot be negative")
    payload = {
        "format_version": FORMAT_VERSION,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "step": step,
        "model_config": asdict(model.config),
        "training_config": asdict(training_config),
        "tokenizer_fingerprint": tokenizer_fingerprint,
        "dataset_fingerprint": dataset_fingerprint,
        "seed": seed,
        "metadata": metadata or {},
        "rng_state": capture_rng_state(),
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, destination)
    return {"path": str(destination), "sha256": sha256_file(destination), "bytes": destination.stat().st_size}


def read_checkpoint(path: str | Path, map_location: torch.device | str = "cpu") -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"missing checkpoint: {source}")
    try:
        payload = torch.load(source, map_location=map_location, weights_only=False)
    except Exception as error:
        raise ValueError(f"cannot load checkpoint {source}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("checkpoint must contain a mapping")
    missing = REQUIRED_FIELDS - set(payload)
    if missing:
        raise ValueError(f"checkpoint missing fields: {sorted(missing)}")
    if payload["format_version"] != FORMAT_VERSION:
        raise ValueError(f"unsupported checkpoint format_version: {payload['format_version']}")
    if not isinstance(payload["step"], int) or payload["step"] < 0:
        raise ValueError("checkpoint step must be a non-negative integer")
    try:
        ModelConfig(**payload["model_config"])
        TrainingConfig(**payload["training_config"])
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid checkpoint configuration: {error}") from error
    return payload


def load_checkpoint(
    path: str | Path,
    *,
    device: torch.device | str,
    dtype: torch.dtype,
    model_config: ModelConfig | None = None,
    tokenizer_fingerprint: str | None = None,
    dataset_fingerprint: str | None = None,
    restore_rng: bool = False,
) -> tuple[TransformerLM, torch.optim.Optimizer, dict[str, Any]]:
    payload = read_checkpoint(path, map_location="cpu")
    saved_model_config = ModelConfig(**payload["model_config"])
    if model_config is not None and model_config != saved_model_config:
        raise ValueError("checkpoint model config does not match requested model config")
    if tokenizer_fingerprint is not None and payload["tokenizer_fingerprint"] != tokenizer_fingerprint:
        raise ValueError("checkpoint tokenizer fingerprint mismatch")
    if dataset_fingerprint is not None and payload["dataset_fingerprint"] != dataset_fingerprint:
        raise ValueError("checkpoint dataset fingerprint mismatch")
    training_config = TrainingConfig(**payload["training_config"])
    model = TransformerLM(saved_model_config).to(device=device, dtype=dtype)
    model.load_state_dict(payload["model_state"])
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=training_config.learning_rate, weight_decay=training_config.weight_decay
    )
    optimizer.load_state_dict(payload["optimizer_state"])
    for state in optimizer.state.values():
        for key, value in state.items():
            if isinstance(value, torch.Tensor):
                state[key] = value.to(device)
    if restore_rng:
        restore_rng_state(payload["rng_state"])
    return model, optimizer, payload
