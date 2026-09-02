"""Prepared UTF-8 text, token arrays, fingerprints, and deterministic batches."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .tokenizer import encode, load_tokenizer, metadata, sha256_file


def load_text(path: str | Path) -> str:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"missing UTF-8 text file: {source}")
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"text is not valid UTF-8: {source}") from error
    if not text:
        raise ValueError(f"text file is empty: {source}")
    return text


def deterministic_text_split(text: str, validation_fraction: float = 0.1) -> tuple[str, str]:
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be in (0, 1)")
    lines = text.splitlines(keepends=True)
    if len(lines) < 2:
        raise ValueError("deterministic split requires at least two lines")
    train: list[str] = []
    validation: list[str] = []
    threshold = int(validation_fraction * 10_000)
    for index, line in enumerate(lines):
        bucket = int.from_bytes(hashlib.sha256(f"{index}:".encode() + line.encode("utf-8")).digest()[:4], "big") % 10_000
        (validation if bucket < threshold else train).append(line)
    if not train or not validation:
        cut = max(1, min(len(lines) - 1, round(len(lines) * (1.0 - validation_fraction))))
        train, validation = lines[:cut], lines[cut:]
    return "".join(train), "".join(validation)


def save_token_array(path: str | Path, tokens: np.ndarray) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.save(destination, np.asarray(tokens, dtype=np.int32), allow_pickle=False)


def load_token_array(path: str | Path) -> np.ndarray:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"missing token array: {source}")
    tokens = np.load(source, mmap_mode="r", allow_pickle=False)
    if tokens.ndim != 1 or not np.issubdtype(tokens.dtype, np.integer):
        raise ValueError("token array must be one-dimensional integers")
    return tokens


def prepare_data(
    tokenizer_path: str | Path,
    train_text: str | Path,
    validation_text: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    tokenizer = load_tokenizer(tokenizer_path)
    train_ids = np.asarray(encode(tokenizer, load_text(train_text)), dtype=np.int32)
    validation_ids = np.asarray(encode(tokenizer, load_text(validation_text)), dtype=np.int32)
    if len(train_ids) < 2 or len(validation_ids) < 2:
        raise ValueError("each split must encode to at least two tokens")
    output = Path(output_dir)
    train_path = output / "train.npy"
    validation_path = output / "validation.npy"
    save_token_array(train_path, train_ids)
    save_token_array(validation_path, validation_ids)
    pieces = {
        "train_source_sha256": sha256_file(train_text),
        "validation_source_sha256": sha256_file(validation_text),
        "train_tokens_sha256": sha256_file(train_path),
        "validation_tokens_sha256": sha256_file(validation_path),
        "tokenizer": metadata(tokenizer_path, tokenizer),
    }
    canonical = json.dumps(pieces, sort_keys=True, separators=(",", ":")).encode()
    manifest = {
        **pieces,
        "train_tokens": len(train_ids),
        "validation_tokens": len(validation_ids),
        "dataset_fingerprint": hashlib.sha256(canonical).hexdigest(),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def deterministic_batch(
    tokens: np.ndarray,
    *,
    context: int,
    batch_size: int,
    seed: int,
    step: int,
    micro: int = 0,
    device: torch.device | str = "cpu",
) -> tuple[torch.Tensor, torch.Tensor]:
    if context <= 0 or batch_size <= 0:
        raise ValueError("context and batch_size must be positive")
    if len(tokens) <= context + 1:
        raise ValueError("token array is too short for context")
    rng = np.random.default_rng(seed + step * 1_000_003 + micro * 10_000_019)
    starts = rng.integers(0, len(tokens) - context - 1, size=batch_size)
    x = np.stack([tokens[start : start + context] for start in starts]).astype(np.int64)
    y = np.stack([tokens[start + 1 : start + context + 1] for start in starts]).astype(np.int64)
    return torch.from_numpy(x).to(device), torch.from_numpy(y).to(device)


def main() -> int:
    parser = argparse.ArgumentParser(description="MindForge prepared-data utility")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--tokenizer", required=True)
    prepare.add_argument("--train-text", required=True)
    prepare.add_argument("--validation-text", required=True)
    prepare.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = prepare_data(args.tokenizer, args.train_text, args.validation_text, args.output_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
