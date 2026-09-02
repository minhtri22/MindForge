"""Explicit single-device training loop for the compact MindForge kernel."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import statistics
import subprocess
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import psutil
import torch
from torch.nn import functional as F

from .checkpoint import FORMAT_VERSION, load_checkpoint, save_checkpoint
from .config import KernelConfig, TrainingConfig
from .data import deterministic_batch, load_token_array
from .device import peak_memory, reset_peak_memory, resolve_device, synchronize
from .evaluate import evaluate_tokens
from .model import TransformerLM, parameter_count
from .tokenizer import load_tokenizer, metadata, sha256_file


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if hasattr(torch, "xpu") and torch.xpu.is_available() and hasattr(torch.xpu, "manual_seed_all"):
        torch.xpu.manual_seed_all(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def learning_rate_multiplier(step: int, config: TrainingConfig) -> float:
    warmup_steps = max(1, int(config.steps * config.warmup_fraction))
    if step < warmup_steps:
        return (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, config.steps - warmup_steps - 1)
    cosine = 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))
    return config.min_lr_fraction + (1.0 - config.min_lr_fraction) * cosine


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")


def _dataset_fingerprint(config: KernelConfig) -> str:
    manifest = Path(config.data.train_tokens).parent / "manifest.json"
    if manifest.is_file():
        try:
            value = json.loads(manifest.read_text(encoding="utf-8"))
            fingerprint = value["dataset_fingerprint"]
            if isinstance(fingerprint, str) and fingerprint:
                return fingerprint
        except (OSError, json.JSONDecodeError, KeyError):
            pass
    import hashlib

    joined = f"{sha256_file(config.data.train_tokens)}:{sha256_file(config.data.validation_tokens)}"
    return hashlib.sha256(joined.encode()).hexdigest()


def train(config: KernelConfig, *, resume: str | Path | None = None) -> dict[str, Any]:
    spec = resolve_device(config.training.device, config.training.dtype)
    tokenizer = load_tokenizer(config.data.tokenizer)
    tokenizer_info = metadata(config.data.tokenizer, tokenizer)
    if tokenizer.get_vocab_size() != config.model.vocab_size:
        raise ValueError(
            f"model vocab_size {config.model.vocab_size} does not match tokenizer {tokenizer.get_vocab_size()}"
        )
    train_tokens = load_token_array(config.data.train_tokens)
    validation_tokens = load_token_array(config.data.validation_tokens)
    if len(train_tokens) <= config.model.max_context + 1:
        raise ValueError("training dataset is too short for model context")
    if min(int(train_tokens.min()), int(validation_tokens.min())) < 0:
        raise ValueError("token arrays contain negative IDs")
    if max(int(train_tokens.max()), int(validation_tokens.max())) >= config.model.vocab_size:
        raise ValueError("token arrays contain IDs outside model vocabulary")

    dataset_fingerprint = _dataset_fingerprint(config)
    tokenizer_fingerprint = str(tokenizer_info["sha256"])
    run_dir = Path(config.data.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = run_dir / "metrics.jsonl"
    if resume is None and metrics_path.exists():
        metrics_path.unlink()
    set_seed(config.training.seed)

    if resume is None:
        model = TransformerLM(config.model).to(device=spec.device, dtype=spec.dtype)
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=config.training.learning_rate, weight_decay=config.training.weight_decay
        )
        start_step = 0
    else:
        model, optimizer, payload = load_checkpoint(
            resume,
            device=spec.device,
            dtype=spec.dtype,
            model_config=config.model,
            tokenizer_fingerprint=tokenizer_fingerprint,
            dataset_fingerprint=dataset_fingerprint,
            restore_rng=True,
        )
        if payload["training_config"] != asdict(config.training):
            raise ValueError("checkpoint training config does not match requested training config")
        if payload["seed"] != config.training.seed:
            raise ValueError("checkpoint seed does not match requested seed")
        start_step = payload["step"]
    if start_step >= config.training.steps:
        raise ValueError("checkpoint step must be less than configured total steps")

    run_record: dict[str, Any] = {
        "format_version": 1,
        "status": "RUNNING",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "seed": config.training.seed,
        "model_config": asdict(config.model),
        "training_config": asdict(config.training),
        "data_config": asdict(config.data),
        "parameter_count": parameter_count(model),
        "dataset_fingerprint": dataset_fingerprint,
        "tokenizer_fingerprint": tokenizer_fingerprint,
        "device": spec.name,
        "dtype": str(spec.dtype),
        "software": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "tokenizers": __import__("tokenizers").__version__,
        },
        "hardware": {
            "platform": platform.platform(),
            "cpu": platform.processor(),
            "ram_bytes": psutil.virtual_memory().total,
            "xpu_name": torch.xpu.get_device_name(0) if spec.name == "xpu" else None,
        },
        "resume_from": str(resume) if resume else None,
        "start_step": start_step,
    }
    _write_json(run_dir / "run.json", run_record)

    reset_peak_memory(spec.device)
    model.train()
    wall_start = time.perf_counter()
    throughput: list[float] = []
    final_loss = float("nan")
    final_eval: dict[str, Any] | None = None
    latest_checkpoint: dict[str, Any] | None = None
    for step in range(start_step, config.training.steps):
        synchronize(spec.device)
        step_start = time.perf_counter()
        optimizer.zero_grad(set_to_none=True)
        train_loss = 0.0
        for micro in range(config.training.accumulation):
            x, y = deterministic_batch(
                train_tokens,
                context=config.model.max_context,
                batch_size=config.training.micro_batch,
                seed=config.training.seed,
                step=step,
                micro=micro,
                device=spec.device,
            )
            logits = model(x)
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
            (loss / config.training.accumulation).backward()
            train_loss += float(loss.detach().float().cpu()) / config.training.accumulation
        torch.nn.utils.clip_grad_norm_(model.parameters(), config.training.gradient_clip)
        lr = config.training.learning_rate * learning_rate_multiplier(step, config.training)
        for group in optimizer.param_groups:
            group["lr"] = lr
        optimizer.step()
        synchronize(spec.device)
        elapsed = time.perf_counter() - step_start
        step_tokens = config.model.max_context * config.training.micro_batch * config.training.accumulation
        tokens_per_second = step_tokens / elapsed
        throughput.append(tokens_per_second)
        completed = step + 1
        final_loss = train_loss
        validation = None
        if completed % config.training.eval_interval == 0 or completed == config.training.steps:
            validation = evaluate_tokens(
                model,
                validation_tokens,
                tokenizer,
                device=spec.device,
                max_windows=config.training.eval_windows,
            )
            final_eval = validation
        metric = {
            "step": completed,
            "tokens_seen": completed * step_tokens,
            "train_loss": train_loss,
            "validation_loss": validation["cross_entropy"] if validation else None,
            "bits_per_token": validation["bits_per_token"] if validation else None,
            "bits_per_byte": validation["bits_per_byte"] if validation else None,
            "elapsed_seconds": time.perf_counter() - wall_start,
            "step_seconds": elapsed,
            "tokens_per_second": tokens_per_second,
            "learning_rate": lr,
            "device": spec.name,
            "dtype": str(spec.dtype),
            "peak_device_memory_bytes": peak_memory(spec.device),
        }
        _append_jsonl(metrics_path, metric)
        if completed % config.training.checkpoint_interval == 0 or completed == config.training.steps:
            checkpoint_path = run_dir / f"checkpoint-step-{completed}.pt"
            latest_checkpoint = save_checkpoint(
                checkpoint_path,
                model,
                optimizer,
                step=completed,
                training_config=config.training,
                tokenizer_fingerprint=tokenizer_fingerprint,
                dataset_fingerprint=dataset_fingerprint,
                seed=config.training.seed,
                metadata={"run_dir": str(run_dir), "format_version": FORMAT_VERSION},
            )

    if final_eval is None:
        final_eval = evaluate_tokens(
            model, validation_tokens, tokenizer, device=spec.device, max_windows=config.training.eval_windows
        )
    wall = time.perf_counter() - wall_start
    run_record.update(
        {
            "status": "PASS" if math.isfinite(final_loss) and final_eval["status"] == "PASS" else "REVISE",
            "completed_steps": config.training.steps,
            "training_tokens": (config.training.steps - start_step)
            * config.model.max_context
            * config.training.micro_batch
            * config.training.accumulation,
            "wall_clock_seconds": wall,
            "final_train_loss": final_loss,
            "final_evaluation": final_eval,
            "throughput_tokens_per_second": {
                "mean": statistics.fmean(throughput),
                "median": statistics.median(throughput),
                "min": min(throughput),
                "max": max(throughput),
                "samples": len(throughput),
            },
            "peak_device_memory_bytes": peak_memory(spec.device),
            "checkpoint": latest_checkpoint,
        }
    )
    _write_json(run_dir / "run.json", run_record)
    return run_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the MindForge compact language model")
    parser.add_argument("--config", required=True)
    parser.add_argument("--resume")
    args = parser.parse_args()
    result = train(KernelConfig.load(args.config), resume=args.resume)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
