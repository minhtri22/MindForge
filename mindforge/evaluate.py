"""Independent checkpoint evaluation with exact UTF-8 BPB accounting."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch.nn import functional as F

from .checkpoint import load_checkpoint, read_checkpoint
from .data import load_token_array
from .device import resolve_device
from .model_contract import TokenModel
from .tokenizer import decode, load_tokenizer, metadata


def bits_per_byte(total_nll: float, utf8_bytes: int) -> float:
    if not math.isfinite(total_nll) or total_nll < 0:
        raise ValueError("total_nll must be finite and non-negative")
    if utf8_bytes <= 0:
        raise ValueError("utf8_bytes must be positive")
    return total_nll / (math.log(2) * utf8_bytes)


@torch.no_grad()
def evaluate_tokens(
    model: TokenModel,
    tokens: np.ndarray,
    tokenizer: Any,
    *,
    device: torch.device | str,
    max_windows: int = 24,
) -> dict[str, Any]:
    if max_windows <= 0:
        raise ValueError("max_windows must be positive")
    context = model.context_limit
    if len(tokens) < 2:
        raise ValueError("evaluation token array is too short")
    stride = context + 1
    max_start = max(0, len(tokens) - stride)
    if max_start == 0:
        starts: Sequence[int] = [0]
    else:
        count = min(max_windows, max_start // stride + 1)
        starts = np.linspace(0, max_start, num=count, dtype=np.int64)
    was_training = model.training
    model.eval()
    total_nll = 0.0
    predicted = 0
    represented_bytes = 0
    used: list[int] = []
    for raw_start in starts:
        start = int(raw_start)
        chunk = np.asarray(tokens[start : start + stride], dtype=np.int64)
        if len(chunk) < 2:
            continue
        x = torch.from_numpy(chunk[:-1].copy())[None, :].to(device)
        y = torch.from_numpy(chunk[1:].copy())[None, :].to(device)
        logits = model(x)
        if not torch.isfinite(logits).all():
            raise FloatingPointError("non-finite evaluation logits")
        nll = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum")
        target_ids = chunk[1:].tolist()
        total_nll += float(nll.float().cpu())
        predicted += len(target_ids)
        represented_bytes += len(decode(tokenizer, target_ids).encode("utf-8"))
        used.append(start)
    model.train(was_training)
    if predicted == 0 or represented_bytes == 0:
        raise ValueError("evaluation produced no represented tokens/bytes")
    ce = total_nll / predicted
    return {
        "status": "PASS",
        "window_starts": used,
        "total_nll": total_nll,
        "predicted_tokens": predicted,
        "represented_utf8_bytes": represented_bytes,
        "cross_entropy": ce,
        "bits_per_token": ce / math.log(2),
        "bits_per_byte": bits_per_byte(total_nll, represented_bytes),
    }


def evaluate_checkpoint(
    checkpoint_path: str | Path,
    tokenizer_path: str | Path,
    token_path: str | Path,
    *,
    device: str = "auto",
    dtype: str = "auto",
    max_windows: int = 24,
) -> dict[str, Any]:
    spec = resolve_device(device, dtype)
    tokenizer = load_tokenizer(tokenizer_path)
    tokenizer_info = metadata(tokenizer_path, tokenizer)
    payload = read_checkpoint(checkpoint_path)
    if payload["model_config"]["vocab_size"] != tokenizer.get_vocab_size():
        raise ValueError("checkpoint vocabulary does not match tokenizer")
    model, _, _ = load_checkpoint(
        checkpoint_path,
        device=spec.device,
        dtype=spec.dtype,
        tokenizer_fingerprint=str(tokenizer_info["sha256"]),
    )
    tokens = load_token_array(token_path)
    first = evaluate_tokens(model, tokens, tokenizer, device=spec.device, max_windows=max_windows)
    second = evaluate_tokens(model, tokens, tokenizer, device=spec.device, max_windows=max_windows)
    deltas = {
        "cross_entropy": abs(first["cross_entropy"] - second["cross_entropy"]),
        "bits_per_byte": abs(first["bits_per_byte"] - second["bits_per_byte"]),
    }
    return {
        "status": "PASS" if max(deltas.values()) <= 1e-6 else "REVISE",
        "device": spec.name,
        "dtype": str(spec.dtype),
        "checkpoint": str(checkpoint_path),
        "metrics": first,
        "repeat_delta": deltas,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a MindForge checkpoint")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--tokens", required=True)
    parser.add_argument("--device", choices=("auto", "xpu", "cuda", "cpu"), default="auto")
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto")
    parser.add_argument("--max-windows", type=int, default=24)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = evaluate_checkpoint(
        args.checkpoint, args.tokenizer, args.tokens,
        device=args.device, dtype=args.dtype, max_windows=args.max_windows,
    )
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
