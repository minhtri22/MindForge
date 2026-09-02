"""Local Phase 0 validation harness for MindForge.

This file intentionally lives under experiments/.  It is evidence-gathering code,
not the Phase 1 training kernel.  The harness is small enough to inspect and is
designed to run on CPU and Intel XPU without backend-specific model code.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import psutil
import torch
from torch import nn
from torch.nn import functional as F


BASE_COMMIT = "5d95db1"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass(frozen=True)
class ModelConfig:
    name: str
    vocab_size: int
    d_model: int
    n_heads: int
    n_layers: int
    ff_mult: int = 4
    max_context: int = 2048


ENVELOPE_CONFIGS = (
    ModelConfig("~10M", 2048, 352, 8, 6, max_context=2048),
    ModelConfig("~25M", 2048, 512, 8, 8, max_context=2048),
    ModelConfig("~50M", 2048, 640, 10, 10, max_context=2048),
    ModelConfig("~100M", 2048, 768, 12, 14, max_context=2048),
)

TINY_CONFIG = ModelConfig("tiny", 64, 64, 4, 2, max_context=64)


class TransformerLM(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
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
            raise ValueError(f"context {context} > max_context {self.config.max_context}")
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
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


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


def machine_snapshot() -> dict[str, Any]:
    os_info = powershell_json(
        "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture"
    )
    cpu_info = powershell_json(
        "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors"
    )
    gpu_info = powershell_json(
        "Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM,VideoProcessor"
    )
    memory = psutil.virtual_memory()
    xpu_name = None
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        xpu_name = torch.xpu.get_device_name(0)
    return {
        "os": os_info or {
            "platform": platform.platform(),
            "architecture": platform.machine(),
        },
        "cpu": cpu_info or {"processor": platform.processor(), "logical_cores": os.cpu_count()},
        "ram": {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
        },
        "gpu": gpu_info,
        "torch_xpu_name": xpu_name,
    }


def software_snapshot() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "python_executable": os.path.abspath(os.sys.executable),
        "torch": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "xpu_attribute": hasattr(torch, "xpu"),
        "xpu_available": bool(hasattr(torch, "xpu") and torch.xpu.is_available()),
        "xpu_count": torch.xpu.device_count() if hasattr(torch, "xpu") else 0,
    }


def common_record() -> dict[str, Any]:
    return {
        "timestamp": utc_now(),
        "git_commit": git_commit(),
        "base_commit": BASE_COMMIT,
        "hardware": machine_snapshot(),
        "software": software_snapshot(),
    }


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


def model_parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def make_random_batch(
    *, vocab_size: int, batch_size: int, context: int, seed: int, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    tokens = torch.randint(vocab_size, (batch_size, context), generator=generator)
    targets = torch.randint(vocab_size, (batch_size, context), generator=generator)
    return tokens.to(device), targets.to(device)


def make_domain_batch(
    *, offset: int, vocab_size: int, batch_size: int, context: int, seed: int, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    starts = torch.randint(vocab_size, (batch_size, 1), generator=generator)
    positions = torch.arange(context + 1).view(1, -1)
    sequence = (starts + positions * offset) % vocab_size
    return sequence[:, :-1].to(device), sequence[:, 1:].to(device)


def build_model(config: ModelConfig, *, seed: int, device: str, dtype: torch.dtype) -> TransformerLM:
    torch.manual_seed(seed)
    model = TransformerLM(config)
    return model.to(device=device, dtype=dtype)


def training_step(
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    tokens: torch.Tensor,
    targets: torch.Tensor,
) -> tuple[float, torch.Tensor]:
    optimizer.zero_grad(set_to_none=True)
    logits = model(tokens)
    loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
    loss.backward()
    optimizer.step()
    return float(loss.detach().float().cpu()), logits


@torch.no_grad()
def eval_loss(model: TransformerLM, batches: Iterable[tuple[torch.Tensor, torch.Tensor]]) -> float:
    model.eval()
    losses: list[float] = []
    for tokens, targets in batches:
        logits = model(tokens)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        losses.append(float(loss.float().cpu()))
    model.train()
    return sum(losses) / len(losses)


def dtype_from_name(name: str) -> torch.dtype:
    return {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }[name]


def matmul_benchmark(device: str, dtype: torch.dtype, size: int = 2048, reps: int = 3) -> dict[str, Any]:
    try:
        torch.manual_seed(7)
        a = torch.randn(size, size, device=device, dtype=dtype)
        b = torch.randn(size, size, device=device, dtype=dtype)
        _ = a @ b
        sync(device)
        timings = []
        for _ in range(reps):
            start = time.perf_counter()
            out = a @ b
            sync(device)
            timings.append(time.perf_counter() - start)
        seconds = sum(timings) / len(timings)
        flops = 2 * size**3
        return {
            "status": "PASS",
            "device": str(out.device),
            "dtype": str(out.dtype),
            "size": size,
            "seconds_mean": seconds,
            "gflops": flops / seconds / 1e9,
        }
    except Exception as exc:  # evidence capture must preserve the real backend error
        return {"status": "FAIL", "error": repr(exc), "device": device, "dtype": str(dtype)}


def full_step_probe(device: str, dtype_name: str) -> dict[str, Any]:
    dtype = dtype_from_name(dtype_name)
    config = ModelConfig("dtype-probe", 128, 128, 4, 2, max_context=128)
    try:
        model = build_model(config, seed=11, device=device, dtype=dtype)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        tokens, targets = make_random_batch(
            vocab_size=config.vocab_size, batch_size=4, context=64, seed=12, device=device
        )
        reset_peak_memory(device)
        start = time.perf_counter()
        loss, logits = training_step(model, optimizer, tokens, targets)
        sync(device)
        seconds = time.perf_counter() - start
        first_parameter = next(model.parameters())
        return {
            "status": "PASS",
            "device_requested": device,
            "device_observed": str(logits.device),
            "parameter_device": str(first_parameter.device),
            "dtype_requested": dtype_name,
            "dtype_observed": str(logits.dtype),
            "parameter_dtype": str(first_parameter.dtype),
            "loss": loss,
            "step_seconds": seconds,
            "tokens_per_second": 4 * 64 / seconds,
            "peak_memory_bytes": peak_memory(device),
        }
    except Exception as exc:
        return {
            "status": "FAIL",
            "device_requested": device,
            "dtype_requested": dtype_name,
            "error": repr(exc),
        }


def checkpoint_roundtrip(device: str) -> dict[str, Any]:
    config = ModelConfig("checkpoint-probe", 128, 128, 4, 2, max_context=64)
    try:
        model = build_model(config, seed=21, device=device, dtype=torch.float32)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        tokens, targets = make_random_batch(
            vocab_size=config.vocab_size, batch_size=2, context=32, seed=22, device=device
        )
        training_step(model, optimizer, tokens, targets)
        sync(device)
        model.eval()
        with torch.no_grad():
            before = model(tokens).detach().float().cpu()
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "roundtrip.pt"
            torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict()}, checkpoint)
            restored = build_model(config, seed=999, device=device, dtype=torch.float32)
            restored_optimizer = torch.optim.AdamW(restored.parameters(), lr=1e-3)
            payload = torch.load(checkpoint, map_location=device, weights_only=True)
            restored.load_state_dict(payload["model"])
            restored_optimizer.load_state_dict(payload["optimizer"])
            restored.eval()
            with torch.no_grad():
                after = restored(tokens).detach().float().cpu()
            max_abs = float((before - after).abs().max())
            return {
                "status": "PASS" if max_abs <= 1e-6 else "FAIL",
                "max_abs_output_difference": max_abs,
                "tolerance": 1e-6,
                "checkpoint_bytes": checkpoint.stat().st_size,
            }
    except Exception as exc:
        return {"status": "FAIL", "error": repr(exc)}


def cpu_xpu_numerical_probe() -> dict[str, Any]:
    if not (hasattr(torch, "xpu") and torch.xpu.is_available()):
        return {"status": "SKIP", "reason": "XPU unavailable"}
    config = ModelConfig("numerical-probe", 64, 64, 4, 2, max_context=32)
    try:
        cpu_model = build_model(config, seed=31, device="cpu", dtype=torch.float32).eval()
        xpu_model = build_model(config, seed=999, device="xpu", dtype=torch.float32).eval()
        xpu_model.load_state_dict(cpu_model.state_dict())
        tokens, _ = make_random_batch(
            vocab_size=config.vocab_size, batch_size=2, context=32, seed=32, device="cpu"
        )
        with torch.no_grad():
            cpu_logits = cpu_model(tokens).float().cpu()
            xpu_logits = xpu_model(tokens.to("xpu")).float().cpu()
        delta = (cpu_logits - xpu_logits).abs()
        max_abs = float(delta.max())
        mean_abs = float(delta.mean())
        tolerance = 2e-3
        return {
            "status": "PASS" if max_abs <= tolerance else "FAIL",
            "max_abs_difference": max_abs,
            "mean_abs_difference": mean_abs,
            "tolerance": tolerance,
        }
    except Exception as exc:
        return {"status": "FAIL", "error": repr(exc)}


def run_hardware_probe() -> dict[str, Any]:
    # On this target, initializing torch.xpu before a large CPU matmul can
    # drastically distort CPU throughput in the same process. Capture CPU
    # controls before any XPU availability/name query in common_record().
    cpu_matmul = matmul_benchmark("cpu", torch.float32)
    cpu_steps = [full_step_probe("cpu", dtype_name) for dtype_name in ("float32", "float16", "bfloat16")]

    record = common_record()
    available_devices = ["cpu"]
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        available_devices.append("xpu")
    if torch.cuda.is_available():
        available_devices.append("cuda")

    record["available_devices"] = available_devices
    record["matmul"] = [cpu_matmul]
    record["full_steps"] = cpu_steps
    for device in [item for item in available_devices if item != "cpu"]:
        record["matmul"].append(matmul_benchmark(device, torch.float32))
        for dtype_name in ("float32", "float16", "bfloat16"):
            record["full_steps"].append(full_step_probe(device, dtype_name))
    checkpoint_device = "xpu" if "xpu" in available_devices else "cpu"
    record["checkpoint"] = checkpoint_roundtrip(checkpoint_device)
    record["cpu_xpu_numerical"] = cpu_xpu_numerical_probe()
    record["status"] = (
        "PASS"
        if record["checkpoint"]["status"] == "PASS"
        and all(item["status"] == "PASS" for item in record["matmul"])
        and record["cpu_xpu_numerical"]["status"] in {"PASS", "SKIP"}
        else "REVISE"
    )
    return record


def envelope_step(
    config: ModelConfig,
    *,
    context: int,
    device: str,
    dtype: torch.dtype,
    seed: int,
) -> dict[str, Any]:
    process = psutil.Process()
    rss_before = process.memory_info().rss
    try:
        model = build_model(config, seed=seed, device=device, dtype=dtype)
        parameters = model_parameter_count(model)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        tokens, targets = make_random_batch(
            vocab_size=config.vocab_size, batch_size=1, context=context, seed=seed + 1, device=device
        )
        reset_peak_memory(device)
        # One untimed warm-up at <=512 tokens removes first-dispatch overhead while
        # avoiding doubling the cost of the largest configurations.
        if context <= 512:
            training_step(model, optimizer, tokens, targets)
            sync(device)
        start = time.perf_counter()
        loss, logits = training_step(model, optimizer, tokens, targets)
        sync(device)
        step_seconds = time.perf_counter() - start
        rss_after = process.memory_info().rss
        return {
            "status": "PASS",
            "model_name": config.name,
            "parameter_count": parameters,
            "context_length": context,
            "micro_batch_size": 1,
            "effective_batch_size": 1,
            "device_requested": device,
            "device_observed": str(logits.device),
            "dtype": str(logits.dtype),
            "forward_success": True,
            "backward_success": True,
            "optimizer_step_success": True,
            "loss": loss,
            "step_seconds": step_seconds,
            "tokens_per_second": context / step_seconds,
            "peak_memory_bytes": peak_memory(device),
            "process_rss_before_bytes": rss_before,
            "process_rss_after_bytes": rss_after,
        }
    except Exception as exc:
        return {
            "status": "FAIL",
            "model_name": config.name,
            "context_length": context,
            "micro_batch_size": 1,
            "effective_batch_size": 1,
            "device_requested": device,
            "dtype": str(dtype),
            "forward_success": False,
            "backward_success": False,
            "optimizer_step_success": False,
            "error": repr(exc),
            "process_rss_before_bytes": rss_before,
            "process_rss_after_bytes": process.memory_info().rss,
        }


def run_model_envelope() -> dict[str, Any]:
    # Run CPU controls before *any* XPU runtime initialization. On this machine,
    # merely querying XPU availability before a large CPU workload materially
    # depresses CPU throughput in the same process.
    cpu_controls = [
        envelope_step(
            ENVELOPE_CONFIGS[0], context=context, device="cpu", dtype=torch.float32, seed=2000 + context
        )
        for context in (256, 512)
    ]
    record = common_record()
    device = "xpu" if record["software"]["xpu_available"] else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    results: list[dict[str, Any]] = []
    for config_index, config in enumerate(ENVELOPE_CONFIGS):
        for context in (256, 512, 1024, 2048):
            result = envelope_step(
                config,
                context=context,
                device=device,
                dtype=dtype,
                seed=1000 + config_index * 10 + int(math.log2(context)),
            )
            results.append(result)
            # A real failure at a shorter context is sufficient evidence to stop
            # increasing context for this scale; repeated OOM attempts add no value.
            if result["status"] == "FAIL":
                break

    record["primary_device"] = device
    record["primary_dtype"] = str(dtype)
    record["results"] = results
    record["cpu_controls"] = cpu_controls
    record["status"] = "PASS" if any(item["status"] == "PASS" for item in results) else "REVISE"
    return record


def fixed_eval_batches(
    *, offset: int, seed: int, device: str, count: int = 4, batch_size: int = 8, context: int = 32
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    return [
        make_domain_batch(
            offset=offset,
            vocab_size=TINY_CONFIG.vocab_size,
            batch_size=batch_size,
            context=context,
            seed=seed + index,
            device=device,
        )
        for index in range(count)
    ]


def train_domain(
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    *,
    offset: int,
    steps: int,
    seed: int,
    device: str,
    replay_offset: int | None = None,
) -> list[float]:
    losses: list[float] = []
    for step in range(steps):
        if replay_offset is None:
            tokens, targets = make_domain_batch(
                offset=offset,
                vocab_size=TINY_CONFIG.vocab_size,
                batch_size=16,
                context=32,
                seed=seed + step,
                device=device,
            )
        else:
            current_tokens, current_targets = make_domain_batch(
                offset=offset,
                vocab_size=TINY_CONFIG.vocab_size,
                batch_size=8,
                context=32,
                seed=seed + step,
                device=device,
            )
            replay_tokens, replay_targets = make_domain_batch(
                offset=replay_offset,
                vocab_size=TINY_CONFIG.vocab_size,
                batch_size=8,
                context=32,
                seed=seed + 100_000 + step,
                device=device,
            )
            tokens = torch.cat([current_tokens, replay_tokens], dim=0)
            targets = torch.cat([current_targets, replay_targets], dim=0)
        loss, _ = training_step(model, optimizer, tokens, targets)
        losses.append(loss)
    sync(device)
    return losses


def reproducibility_seed(seed: int, device: str) -> dict[str, Any]:
    model = build_model(TINY_CONFIG, seed=seed, device=device, dtype=torch.float32)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-3)
    eval_batches = fixed_eval_batches(offset=1, seed=50_000, device=device)
    before = eval_loss(model, eval_batches)
    curve = train_domain(model, optimizer, offset=1, steps=20, seed=seed * 1000, device=device)
    after = eval_loss(model, eval_batches)
    return {
        "seed": seed,
        "eval_loss_before": before,
        "eval_loss_after": after,
        "loss_reduction": before - after,
        "train_loss_first": curve[0],
        "train_loss_last": curve[-1],
        "status": "PASS" if after < before else "FAIL",
    }


def checkpoint_resume_probe(device: str) -> dict[str, Any]:
    seed = 777
    total_steps = 8
    split = 4

    def train_range(model: TransformerLM, optimizer: torch.optim.Optimizer, start: int, stop: int) -> None:
        for step in range(start, stop):
            tokens, targets = make_domain_batch(
                offset=1,
                vocab_size=TINY_CONFIG.vocab_size,
                batch_size=8,
                context=32,
                seed=90_000 + step,
                device=device,
            )
            training_step(model, optimizer, tokens, targets)
        sync(device)

    continuous = build_model(TINY_CONFIG, seed=seed, device=device, dtype=torch.float32)
    continuous_optimizer = torch.optim.AdamW(continuous.parameters(), lr=3e-3)
    train_range(continuous, continuous_optimizer, 0, total_steps)

    staged = build_model(TINY_CONFIG, seed=seed, device=device, dtype=torch.float32)
    staged_optimizer = torch.optim.AdamW(staged.parameters(), lr=3e-3)
    train_range(staged, staged_optimizer, 0, split)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "resume.pt"
        torch.save(
            {
                "model": staged.state_dict(),
                "optimizer": staged_optimizer.state_dict(),
                "step": split,
            },
            path,
        )
        resumed = build_model(TINY_CONFIG, seed=1234, device=device, dtype=torch.float32)
        resumed_optimizer = torch.optim.AdamW(resumed.parameters(), lr=3e-3)
        payload = torch.load(path, map_location=device, weights_only=True)
        resumed.load_state_dict(payload["model"])
        resumed_optimizer.load_state_dict(payload["optimizer"])
        train_range(resumed, resumed_optimizer, int(payload["step"]), total_steps)

    max_abs = 0.0
    for left, right in zip(continuous.parameters(), resumed.parameters(), strict=True):
        max_abs = max(max_abs, float((left.detach().float().cpu() - right.detach().float().cpu()).abs().max()))
    tolerance = 1e-6
    return {
        "status": "PASS" if max_abs <= tolerance else "FAIL",
        "max_abs_parameter_difference": max_abs,
        "tolerance": tolerance,
        "total_steps": total_steps,
        "resume_step": split,
    }


def run_reproducibility() -> dict[str, Any]:
    record = common_record()
    device = "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available() else "cpu"
    seeds = [101, 202, 303]
    results = [reproducibility_seed(seed, device) for seed in seeds]
    record["device"] = device
    record["config"] = asdict(TINY_CONFIG)
    record["seeds"] = results
    record["checkpoint_resume"] = checkpoint_resume_probe(device)
    record["status"] = (
        "PASS"
        if all(item["status"] == "PASS" for item in results)
        and record["checkpoint_resume"]["status"] == "PASS"
        else "REVISE"
    )
    return record


def continual_seed(seed: int, device: str, replay: bool) -> dict[str, Any]:
    model = build_model(TINY_CONFIG, seed=seed, device=device, dtype=torch.float32)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-3)
    eval_a = fixed_eval_batches(offset=1, seed=70_000, device=device)
    eval_b = fixed_eval_batches(offset=2, seed=80_000, device=device)

    train_domain(model, optimizer, offset=1, steps=30, seed=seed * 1000, device=device)
    a_before_b = eval_loss(model, eval_a)
    b_before_b = eval_loss(model, eval_b)
    train_domain(
        model,
        optimizer,
        offset=2,
        steps=30,
        seed=seed * 1000 + 40_000,
        device=device,
        replay_offset=1 if replay else None,
    )
    a_after_b = eval_loss(model, eval_a)
    b_after_b = eval_loss(model, eval_b)
    return {
        "seed": seed,
        "treatment": "50% replay A during B" if replay else "none",
        "a_before_b": a_before_b,
        "b_before_b": b_before_b,
        "a_after_b": a_after_b,
        "b_after_b": b_after_b,
        "forgetting": a_after_b - a_before_b,
        "b_acquisition": b_before_b - b_after_b,
    }


def mean_metric(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def run_continual() -> dict[str, Any]:
    record = common_record()
    device = "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available() else "cpu"
    seeds = [101, 202, 303]
    baseline = [continual_seed(seed, device, replay=False) for seed in seeds]
    replay = [continual_seed(seed, device, replay=True) for seed in seeds]
    baseline_mean = {key: mean_metric(baseline, key) for key in ("a_before_b", "a_after_b", "b_after_b", "forgetting")}
    replay_mean = {key: mean_metric(replay, key) for key in ("a_before_b", "a_after_b", "b_after_b", "forgetting")}
    record["device"] = device
    record["config"] = asdict(TINY_CONFIG)
    record["protocol"] = {
        "domain_a_offset": 1,
        "domain_b_offset": 2,
        "train_a_steps": 30,
        "train_b_steps": 30,
        "batch_size": 16,
        "context": 32,
        "optimizer": "AdamW",
        "learning_rate": 0.003,
        "treatment": "fixed 50/50 B/A replay batch during B; no hyperparameter tuning",
    }
    record["baseline"] = baseline
    record["baseline_mean"] = baseline_mean
    record["replay"] = replay
    record["replay_mean"] = replay_mean
    record["forgetting_improvement"] = baseline_mean["forgetting"] - replay_mean["forgetting"]
    record["status"] = "PASS" if baseline_mean["forgetting"] > 0 else "REVISE"
    return record


def write_result(filename: str, payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("hardware", "envelope", "repro", "continual", "all"),
        nargs="?",
        default="all",
    )
    args = parser.parse_args()

    if args.command in {"hardware", "all"}:
        write_result("phase0_hardware_probe.json", run_hardware_probe())
    if args.command in {"envelope", "all"}:
        write_result("phase0_model_envelope.json", run_model_envelope())
    if args.command in {"repro", "all"}:
        write_result("phase0_reproducibility.json", run_reproducibility())
    if args.command in {"continual", "all"}:
        write_result("phase0_continual_local.json", run_continual())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
