"""Minimal deterministic autoregressive generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from .checkpoint import load_checkpoint, read_checkpoint
from .device import resolve_device
from .model import TransformerLM
from .tokenizer import decode, encode, load_tokenizer, metadata


@torch.no_grad()
def generate(
    model: TransformerLM,
    tokenizer: Any,
    prompt: str,
    *,
    device: torch.device | str,
    max_new_tokens: int = 32,
    temperature: float = 0.0,
    top_k: int | None = None,
    seed: int = 2026,
) -> dict[str, Any]:
    if max_new_tokens < 0:
        raise ValueError("max_new_tokens cannot be negative")
    if temperature < 0:
        raise ValueError("temperature cannot be negative")
    if top_k is not None and top_k <= 0:
        raise ValueError("top_k must be positive")
    ids = encode(tokenizer, prompt)
    if not ids:
        raise ValueError("prompt produced no tokens")
    generator = torch.Generator(device="cpu").manual_seed(seed)
    model.eval()
    for _ in range(max_new_tokens):
        x = torch.tensor([ids[-model.config.max_context :]], dtype=torch.long, device=device)
        logits = model(x)[0, -1].float().cpu()
        if not torch.isfinite(logits).all():
            raise FloatingPointError("non-finite generation logits")
        if temperature == 0:
            next_id = int(torch.argmax(logits))
        else:
            scaled = logits / temperature
            if top_k is not None:
                k = min(top_k, scaled.numel())
                values, indices = torch.topk(scaled, k)
                choice = int(torch.multinomial(torch.softmax(values, dim=-1), 1, generator=generator))
                next_id = int(indices[choice])
            else:
                next_id = int(torch.multinomial(torch.softmax(scaled, dim=-1), 1, generator=generator))
        ids.append(next_id)
    return {"prompt": prompt, "seed": seed, "token_ids": ids, "text": decode(tokenizer, ids)}


def generate_checkpoint(
    checkpoint_path: str | Path,
    tokenizer_path: str | Path,
    prompt: str,
    **options: Any,
) -> dict[str, Any]:
    device_name = options.pop("device", "auto")
    dtype_name = options.pop("dtype", "auto")
    spec = resolve_device(device_name, dtype_name)
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
    result = generate(model, tokenizer, prompt, device=spec.device, **options)
    return {"device": spec.name, "dtype": str(spec.dtype), **result}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate with a MindForge checkpoint")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--device", choices=("auto", "xpu", "cuda", "cpu"), default="auto")
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto")
    args = parser.parse_args()
    result = generate_checkpoint(
        args.checkpoint, args.tokenizer, args.prompt,
        max_new_tokens=args.max_new_tokens, temperature=args.temperature,
        top_k=args.top_k, seed=args.seed, device=args.device, dtype=args.dtype,
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
