"""Shared Phase-0-only primitives for the real-language evidence slice.

This is deliberately experiment code, not the Phase 1 kernel.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import psutil
import torch
from tokenizers import Tokenizer
from torch import nn
from torch.nn import functional as F


BASE_COMMIT = "1b0d9b016c2eaff8922693f7f6d496b597f29927"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "experiments" / "data" / "phase0_real_language"
CHECKPOINT_DIR = ROOT / "experiments" / "checkpoints" / "phase0_real_language"
RESULTS_DIR = ROOT / "experiments" / "results"
QWEN_REPO = "Qwen/Qwen2.5-0.5B"
QWEN_REVISION = "060db6499f32faf8b98477b0a26969ef7d8b9987"
MF_TOKENIZER_PATH = DATA_DIR / "mindforge-tokenizer.json"


@dataclass(frozen=True)
class LMConfig:
    vocab_size: int
    d_model: int
    n_heads: int
    n_layers: int
    max_context: int
    ff_mult: int = 4


class TransformerLM(nn.Module):
    def __init__(self, config: LMConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.position_embedding = nn.Embedding(config.max_context, config.d_model)
        self.layers = nn.ModuleList(
            nn.TransformerEncoderLayer(
                d_model=config.d_model,
                nhead=config.n_heads,
                dim_feedforward=config.ff_mult * config.d_model,
                dropout=0.0,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            for _ in range(config.n_layers)
        )
        self.norm = nn.LayerNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        batch, context = tokens.shape
        if context > self.config.max_context:
            raise ValueError(f"context {context} exceeds max_context {self.config.max_context}")
        positions = torch.arange(context, device=tokens.device)
        hidden = self.token_embedding(tokens) + self.position_embedding(positions)[None, :, :]
        causal_mask = torch.triu(
            torch.ones(context, context, dtype=torch.bool, device=tokens.device), diagonal=1
        )
        for layer in self.layers:
            hidden = layer(hidden, src_mask=causal_mask, is_causal=True)
        return self.lm_head(self.norm(hidden))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def powershell_json(expression: str) -> Any:
    command = f"{expression} | ConvertTo-Json -Compress"
    try:
        raw = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", command],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return json.loads(raw) if raw else None
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None


def hardware_snapshot() -> dict[str, Any]:
    memory = psutil.virtual_memory()
    return {
        "os": powershell_json(
            "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture"
        ),
        "cpu": powershell_json(
            "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors"
        ),
        "gpu": powershell_json(
            "Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM,VideoProcessor"
        ),
        "ram": {"total_bytes": memory.total, "available_bytes": memory.available},
        "xpu_name": (
            torch.xpu.get_device_name(0)
            if hasattr(torch, "xpu") and torch.xpu.is_available()
            else None
        ),
    }


def software_snapshot() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "python_executable": "<venv>/Scripts/python.exe",
        "torch": torch.__version__,
        "tokenizers": __import__("tokenizers").__version__,
        "numpy": np.__version__,
        "xpu_available": bool(hasattr(torch, "xpu") and torch.xpu.is_available()),
        "cuda_available": torch.cuda.is_available(),
    }


def common_record(dataset_fingerprint: str | None = None) -> dict[str, Any]:
    return {
        "timestamp": utc_now(),
        "base_commit": BASE_COMMIT,
        "git_commit": git_commit(),
        "hardware": hardware_snapshot(),
        "software": software_snapshot(),
        "dataset_fingerprint": dataset_fingerprint,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    path.write_bytes((text + "\n").encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def model_parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def sync(device: str) -> None:
    if device.startswith("xpu"):
        torch.xpu.synchronize()
    elif device.startswith("cuda"):
        torch.cuda.synchronize()


def reset_peak_memory(device: str) -> None:
    if device.startswith("xpu") and hasattr(torch.xpu, "reset_peak_memory_stats"):
        torch.xpu.reset_peak_memory_stats()
    elif device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()


def peak_memory(device: str) -> int | None:
    if device.startswith("xpu") and hasattr(torch.xpu, "max_memory_allocated"):
        return int(torch.xpu.max_memory_allocated())
    if device.startswith("cuda"):
        return int(torch.cuda.max_memory_allocated())
    return None


def current_memory(device: str) -> int | None:
    if device.startswith("xpu") and hasattr(torch.xpu, "memory_allocated"):
        return int(torch.xpu.memory_allocated())
    if device.startswith("cuda"):
        return int(torch.cuda.memory_allocated())
    return None


def build_model(config: LMConfig, *, seed: int, device: str, dtype: torch.dtype) -> TransformerLM:
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    return TransformerLM(config).to(device=device, dtype=dtype)


def lr_multiplier(step: int, total_steps: int, warmup_fraction: float = 0.05) -> float:
    warmup_steps = max(1, int(total_steps * warmup_fraction))
    if step < warmup_steps:
        return (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps - 1)
    return 0.1 + 0.9 * 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))


def build_optimizer(model: nn.Module, lr: float = 3e-4, weight_decay: float = 0.1) -> torch.optim.Optimizer:
    return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)


def bits_per_byte_from_nll(total_nll: float, utf8_byte_count: int) -> float:
    """Convert summed natural-log NLL to bits per actual represented UTF-8 byte."""
    if not math.isfinite(total_nll) or total_nll < 0:
        raise ValueError("total_nll must be finite and non-negative")
    if utf8_byte_count <= 0:
        raise ValueError("utf8_byte_count must be positive")
    return total_nll / (math.log(2) * utf8_byte_count)


def tokenizer_metadata(tokenizer: Tokenizer, *, name: str, revision: str | None = None) -> dict[str, Any]:
    config = json.loads(tokenizer.to_str())
    added = config.get("added_tokens", [])
    return {
        "name": name,
        "revision": revision,
        "vocab_size": tokenizer.get_vocab_size(),
        "normalizer": config.get("normalizer"),
        "pre_tokenizer": config.get("pre_tokenizer"),
        "decoder": config.get("decoder"),
        "special_tokens": [item.get("content") for item in added if item.get("special")],
    }


def load_tokenizer(kind: str) -> Tokenizer:
    if kind == "existing":
        return Tokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)
    if kind == "mindforge":
        if not MF_TOKENIZER_PATH.exists():
            raise FileNotFoundError(f"missing MindForge tokenizer: {MF_TOKENIZER_PATH}")
        return Tokenizer.from_file(str(MF_TOKENIZER_PATH))
    raise ValueError(f"unknown tokenizer kind: {kind}")


def encode_text_file(tokenizer: Tokenizer, path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8")
    ids = tokenizer.encode(text).ids
    if not ids:
        raise ValueError(f"tokenizer produced no tokens for {path.name}")
    if min(ids) < 0 or max(ids) >= tokenizer.get_vocab_size():
        raise ValueError("invalid token ID produced")
    return np.asarray(ids, dtype=np.int32)


def save_token_array(path: Path, tokens: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, tokens, allow_pickle=False)


def load_token_array(path: Path) -> np.ndarray:
    return np.load(path, mmap_mode="r", allow_pickle=False)


def staged_pool(tokens: np.ndarray, target_tokens: int, blocks: int = 64) -> np.ndarray:
    """Build a deterministic pool from evenly spaced contiguous blocks."""
    if target_tokens >= len(tokens):
        return np.asarray(tokens, dtype=np.int32).copy()
    block_len = max(2, target_tokens // blocks)
    usable = block_len * blocks
    max_start = len(tokens) - block_len
    starts = np.linspace(0, max_start, num=blocks, dtype=np.int64)
    pieces = [np.asarray(tokens[start : start + block_len], dtype=np.int32) for start in starts]
    pool = np.concatenate(pieces)
    return pool[:usable]


def deterministic_batch(
    tokens: np.ndarray,
    *,
    context: int,
    batch_size: int,
    seed: int,
    step: int,
    device: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    if len(tokens) <= context + 1:
        raise ValueError("token pool too small for context")
    rng = np.random.default_rng(seed + step * 1_000_003)
    starts = rng.integers(0, len(tokens) - context - 1, size=batch_size)
    x = np.stack([tokens[start : start + context] for start in starts]).astype(np.int64)
    y = np.stack([tokens[start + 1 : start + context + 1] for start in starts]).astype(np.int64)
    return torch.from_numpy(x).to(device), torch.from_numpy(y).to(device)


def train_optimizer_step(
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    tokens: np.ndarray,
    *,
    context: int,
    micro_batch: int,
    accumulation: int,
    seed: int,
    step: int,
    device: str,
    lr: float,
    total_steps: int,
) -> float:
    optimizer.zero_grad(set_to_none=True)
    total_loss = 0.0
    for micro in range(accumulation):
        x, y = deterministic_batch(
            tokens,
            context=context,
            batch_size=micro_batch,
            seed=seed + micro * 10_000_019,
            step=step,
            device=device,
        )
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1)) / accumulation
        loss.backward()
        total_loss += float(loss.detach().float().cpu())
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    multiplier = lr_multiplier(step, total_steps)
    for group in optimizer.param_groups:
        group["lr"] = lr * multiplier
    optimizer.step()
    return total_loss


@torch.no_grad()
def evaluate_tokens(
    model: TransformerLM,
    tokens: np.ndarray,
    tokenizer: Tokenizer,
    *,
    context: int,
    device: str,
    max_windows: int = 32,
) -> dict[str, Any]:
    model.eval()
    total_nll = 0.0
    total_predicted_tokens = 0
    total_bytes = 0
    finite = True
    windows = 0
    stride = context + 1
    max_start = max(0, len(tokens) - stride)
    if max_start == 0:
        starts: Sequence[int] = [0]
    else:
        starts = np.linspace(0, max_start, num=min(max_windows, max_start // stride + 1), dtype=np.int64)
    for start in starts:
        chunk = np.asarray(tokens[int(start) : int(start) + stride], dtype=np.int64)
        if len(chunk) < 2:
            continue
        x = torch.from_numpy(chunk[:-1][None, :]).to(device)
        y = torch.from_numpy(chunk[1:][None, :]).to(device)
        logits = model(x)
        if not torch.isfinite(logits).all():
            finite = False
            break
        nll = F.cross_entropy(
            logits.reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum"
        )
        target_ids = chunk[1:].tolist()
        decoded = tokenizer.decode(target_ids, skip_special_tokens=False)
        total_bytes += len(decoded.encode("utf-8"))
        total_nll += float(nll.float().cpu())
        total_predicted_tokens += len(target_ids)
        windows += 1
    model.train()
    if not finite or total_predicted_tokens == 0 or total_bytes == 0:
        return {"finite": finite, "windows": windows, "status": "FAIL"}
    cross_entropy = total_nll / total_predicted_tokens
    bits_per_token = cross_entropy / math.log(2)
    bpb = bits_per_byte_from_nll(total_nll, total_bytes)
    return {
        "status": "PASS",
        "finite": True,
        "windows": windows,
        "window_starts": [int(start) for start in starts[:windows]],
        "total_nll": total_nll,
        "predicted_tokens": total_predicted_tokens,
        "represented_utf8_bytes": total_bytes,
        "cross_entropy": cross_entropy,
        "bits_per_token": bits_per_token,
        "bits_per_byte": bpb,
        "perplexity": math.exp(min(cross_entropy, 20.0)),
        "perplexity_note": "tokenizer-dependent; never used for cross-tokenizer ranking",
    }


@torch.no_grad()
def evaluate_text_samples(
    model: TransformerLM,
    tokenizer: Tokenizer,
    texts: Sequence[str],
    *,
    device: str,
    bos_token: str = "<|endoftext|>",
) -> dict[str, Any]:
    """Score the exact same UTF-8 text bytes across tokenizers.

    A frozen BOS token is prepended as model input so every tokenizer predicts all
    tokens representing each sample; BPB therefore uses the complete original
    sample byte count rather than token-count approximations or tokenizer-specific
    window boundaries.
    """
    bos_id = tokenizer.token_to_id(bos_token)
    if bos_id is None:
        raise ValueError(f"missing required BOS scoring token: {bos_token}")
    model.eval()
    total_nll = 0.0
    total_predicted_tokens = 0
    total_bytes = 0
    finite = True
    sample_records: list[dict[str, Any]] = []
    for index, text in enumerate(texts):
        ids = tokenizer.encode(text).ids
        if not ids:
            raise ValueError(f"sample {index} produced no tokens")
        if len(ids) > model.config.max_context:
            raise ValueError(
                f"sample {index} tokenized to {len(ids)} tokens, exceeding context {model.config.max_context}"
            )
        x_ids = [bos_id] + ids[:-1]
        x = torch.tensor([x_ids], dtype=torch.long, device=device)
        y = torch.tensor([ids], dtype=torch.long, device=device)
        logits = model(x)
        if not torch.isfinite(logits).all():
            finite = False
            break
        nll = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum")
        sample_nll = float(nll.float().cpu())
        sample_bytes = len(text.encode("utf-8"))
        total_nll += sample_nll
        total_predicted_tokens += len(ids)
        total_bytes += sample_bytes
        sample_records.append(
            {
                "index": index,
                "tokens": len(ids),
                "utf8_bytes": sample_bytes,
                "nll": sample_nll,
            }
        )
    model.train()
    if not finite or total_predicted_tokens == 0 or total_bytes == 0:
        return {"status": "FAIL", "finite": finite, "samples": sample_records}
    cross_entropy = total_nll / total_predicted_tokens
    return {
        "status": "PASS",
        "finite": True,
        "samples": sample_records,
        "total_nll": total_nll,
        "predicted_tokens": total_predicted_tokens,
        "represented_utf8_bytes": total_bytes,
        "cross_entropy": cross_entropy,
        "bits_per_token": cross_entropy / math.log(2),
        "bits_per_byte": bits_per_byte_from_nll(total_nll, total_bytes),
        "perplexity": math.exp(min(cross_entropy, 20.0)),
        "perplexity_note": "tokenizer-dependent; never used for cross-tokenizer ranking",
        "byte_accounting": "exact original UTF-8 bytes of the frozen text samples",
    }


@torch.no_grad()
def generate_ids(
    model: TransformerLM,
    tokenizer: Tokenizer,
    prompt: str,
    *,
    seed: int,
    max_new_tokens: int,
    device: str,
    temperature: float = 0.8,
) -> dict[str, Any]:
    prompt_ids = tokenizer.encode(prompt).ids
    if not prompt_ids:
        raise ValueError("prompt produced no tokens")
    ids = list(prompt_ids)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    finite = True
    for _ in range(max_new_tokens):
        context_ids = ids[-model.config.max_context :]
        x = torch.tensor([context_ids], dtype=torch.long, device=device)
        logits = model(x)[:, -1, :].float().cpu().squeeze(0)
        if not torch.isfinite(logits).all():
            finite = False
            break
        probs = torch.softmax(logits / temperature, dim=-1)
        next_id = int(torch.multinomial(probs, 1, generator=generator).item())
        if next_id < 0 or next_id >= tokenizer.get_vocab_size():
            raise ValueError(f"invalid generated token id {next_id}")
        ids.append(next_id)
    return {
        "prompt": prompt,
        "seed": seed,
        "finite": finite,
        "valid_token_ids": all(0 <= item < tokenizer.get_vocab_size() for item in ids),
        "token_ids": ids,
        "text": tokenizer.decode(ids, skip_special_tokens=False),
    }


def generation_sanity(
    model: TransformerLM,
    tokenizer: Tokenizer,
    prompts: Sequence[str],
    *,
    device: str,
    seed: int = 12345,
    max_new_tokens: int = 24,
) -> dict[str, Any]:
    model.eval()
    first = [
        generate_ids(
            model,
            tokenizer,
            prompt,
            seed=seed + index,
            max_new_tokens=max_new_tokens,
            device=device,
        )
        for index, prompt in enumerate(prompts)
    ]
    second = [
        generate_ids(
            model,
            tokenizer,
            prompt,
            seed=seed + index,
            max_new_tokens=max_new_tokens,
            device=device,
        )
        for index, prompt in enumerate(prompts)
    ]
    deterministic = all(a["token_ids"] == b["token_ids"] for a, b in zip(first, second, strict=True))
    valid = all(item["finite"] and item["valid_token_ids"] for item in first)
    model.train()
    return {
        "status": "PASS" if deterministic and valid else "FAIL",
        "deterministic_same_seed": deterministic,
        "finite_and_valid": valid,
        "generations": first,
    }


def save_checkpoint(
    path: Path,
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    *,
    step: int,
    config: LMConfig,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "step": step,
            "config": asdict(config),
            "metadata": metadata,
        },
        path,
    )
    return {"sha256": sha256_file(path), "bytes": path.stat().st_size, "step": step}


def load_checkpoint(
    path: Path, *, device: str, dtype: torch.dtype
) -> tuple[TransformerLM, torch.optim.Optimizer, dict[str, Any]]:
    payload = torch.load(path, map_location=device, weights_only=True)
    config = LMConfig(**payload["config"])
    model = build_model(config, seed=0, device=device, dtype=dtype)
    optimizer = build_optimizer(model)
    model.load_state_dict(payload["model"])
    optimizer.load_state_dict(payload["optimizer"])
    return model, optimizer, payload


def summarize_throughput(samples: Iterable[float]) -> dict[str, float | int]:
    values = list(samples)
    if not values:
        return {"count": 0, "mean": 0.0, "median": 0.0, "stddev": 0.0}
    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stddev": statistics.pstdev(values) if len(values) > 1 else 0.0,
    }
