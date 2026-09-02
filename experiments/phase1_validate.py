"""Bounded Phase-1 validation runner.

This is evidence tooling, not part of the reusable kernel.  It exercises the
frozen CPU/XPU/parity gates without adding extension points to ``mindforge``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import statistics
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import psutil
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mindforge.checkpoint import read_checkpoint
from mindforge.config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from mindforge.data import deterministic_text_split, load_token_array, prepare_data
from mindforge.device import resolve_device
from mindforge.evaluate import evaluate_checkpoint, evaluate_tokens
from mindforge.generate import generate_checkpoint
from mindforge.model import TransformerLM, parameter_count
from mindforge.tokenizer import load_tokenizer, metadata, sha256_file, train_tokenizer
from mindforge.train import set_seed, train


RESULTS = ROOT / "experiments" / "results"
WORK = ROOT / "experiments" / "phase1_validation_work"
FIXTURE = ROOT / "tests" / "fixtures" / "phase1-corpus.txt"
PHASE0_DATA = ROOT / "experiments" / "data" / "phase0_real_language"
PHASE0_CHECKPOINT = ROOT / "experiments" / "checkpoints" / "phase0_real_language" / "baseline0-final.pt"
PHASE0_RESULT = RESULTS / "phase0_baseline0.json"
BASE_COMMIT = "bba9360b87c947202115386a3c6ea1f68b9735b9"


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    root_text = str(ROOT)

    def scrub(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: scrub(child) for key, child in item.items()}
        if isinstance(item, list):
            return [scrub(child) for child in item]
        if isinstance(item, str):
            return item.replace(root_text + "\\", "").replace(root_text + "/", "")
        return item

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(scrub(value), indent=2, sort_keys=True) + "\n")


def software() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "tokenizers": __import__("tokenizers").__version__,
    }


def hardware() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "ram_bytes": psutil.virtual_memory().total,
        "xpu_available": bool(hasattr(torch, "xpu") and torch.xpu.is_available()),
        "xpu_name": torch.xpu.get_device_name(0) if hasattr(torch, "xpu") and torch.xpu.is_available() else None,
    }


def common() -> dict[str, Any]:
    return {
        "base_commit": BASE_COMMIT,
        "git_commit": git_commit(),
        "hardware": hardware(),
        "software": software(),
    }


def cpu_smoke() -> dict[str, Any]:
    work = WORK / "cpu"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    text = FIXTURE.read_text(encoding="utf-8")
    train_text, validation_text = deterministic_text_split(text, 0.25)
    train_path = work / "train.txt"
    validation_path = work / "validation.txt"
    train_path.write_text(train_text * 12, encoding="utf-8")
    validation_path.write_text(validation_text * 12, encoding="utf-8")
    tokenizer_path = work / "tokenizer.json"
    tokenizer = train_tokenizer([train_path, validation_path], tokenizer_path, vocab_size=512)
    manifest = prepare_data(tokenizer_path, train_path, validation_path, work / "data")
    training = TrainingConfig(
        steps=4,
        micro_batch=1,
        accumulation=2,
        learning_rate=1e-3,
        eval_interval=2,
        checkpoint_interval=2,
        eval_windows=2,
        seed=123,
        device="cpu",
        dtype="float32",
    )
    model = ModelConfig(
        vocab_size=tokenizer.get_vocab_size(), d_model=32, n_heads=4,
        n_layers=1, max_context=16,
    )
    continuous_cfg = KernelConfig(
        data=DataConfig(
            str(work / "data" / "train.npy"), str(work / "data" / "validation.npy"),
            str(tokenizer_path), str(work / "continuous"),
        ),
        model=model,
        training=training,
    )
    continuous = train(continuous_cfg)
    resumed_cfg = KernelConfig(
        data=DataConfig(
            continuous_cfg.data.train_tokens, continuous_cfg.data.validation_tokens,
            continuous_cfg.data.tokenizer, str(work / "resumed"),
        ),
        model=model,
        training=training,
    )
    midpoint = work / "continuous" / "checkpoint-step-2.pt"
    resumed = train(resumed_cfg, resume=midpoint)
    left = read_checkpoint(work / "continuous" / "checkpoint-step-4.pt")
    right = read_checkpoint(work / "resumed" / "checkpoint-step-4.pt")
    exact_parameters = all(torch.equal(left["model_state"][name], right["model_state"][name]) for name in left["model_state"])
    exact_loss = continuous["final_train_loss"] == resumed["final_train_loss"]
    exact_eval = continuous["final_evaluation"] == resumed["final_evaluation"]
    checkpoint = work / "resumed" / "checkpoint-step-4.pt"
    evaluated = evaluate_checkpoint(checkpoint, tokenizer_path, work / "data" / "validation.npy", device="cpu", max_windows=2)
    generated = generate_checkpoint(checkpoint, tokenizer_path, "Xin chào", device="cpu", max_new_tokens=4, seed=42)
    status = "PASS" if all([
        continuous["status"] == "PASS", resumed["status"] == "PASS", exact_parameters,
        exact_loss, exact_eval, evaluated["status"] == "PASS", bool(generated["text"]),
    ]) else "REVISE"
    result = {
        **common(),
        "status": status,
        "config": continuous_cfg.to_dict(),
        "dataset_fingerprint": manifest["dataset_fingerprint"],
        "tokenizer_fingerprint": metadata(tokenizer_path, tokenizer)["sha256"],
        "checkpoint_hash": sha256_file(checkpoint),
        "training": continuous,
        "resume": {
            "status": "PASS" if exact_parameters and exact_loss and exact_eval else "REVISE",
            "exact_parameters": exact_parameters,
            "loss_delta": abs(continuous["final_train_loss"] - resumed["final_train_loss"]),
            "exact_evaluation": exact_eval,
        },
        "evaluation": evaluated,
        "generation": generated,
    }
    write_json(RESULTS / "phase1_cpu_smoke.json", result)
    return result


def xpu_validation() -> dict[str, Any]:
    spec = resolve_device("xpu", "bfloat16")
    if spec.name != "xpu" or spec.dtype != torch.bfloat16:
        raise RuntimeError("Phase-1 XPU validation requires XPU/BF16")
    work = WORK / "xpu"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    tokenizer_path = PHASE0_DATA / "mindforge-tokenizer.json"
    train_path = PHASE0_DATA / "mindforge.train.npy"
    validation_path = PHASE0_DATA / "mindforge.validation.npy"
    tokenizer = load_tokenizer(tokenizer_path)
    tokenizer_info = metadata(tokenizer_path, tokenizer)
    manifest = json.loads((PHASE0_DATA / "manifest.json").read_text(encoding="utf-8"))
    model_cfg = ModelConfig(vocab_size=tokenizer.get_vocab_size())
    training_cfg = TrainingConfig(
        steps=100, micro_batch=1, accumulation=2, learning_rate=3e-4,
        weight_decay=0.1, gradient_clip=1.0, warmup_fraction=0.05,
        min_lr_fraction=0.1, eval_interval=50, checkpoint_interval=50,
        eval_windows=8, seed=2026, device="xpu", dtype="bfloat16",
    )
    cfg = KernelConfig(
        data=DataConfig(str(train_path), str(validation_path), str(tokenizer_path), str(work / "continuous")),
        model=model_cfg,
        training=training_cfg,
    )
    set_seed(training_cfg.seed)
    initial_model = TransformerLM(model_cfg).to(device="xpu", dtype=torch.bfloat16)
    initial_eval = evaluate_tokens(
        initial_model, load_token_array(validation_path), tokenizer, device="xpu", max_windows=training_cfg.eval_windows
    )
    del initial_model
    continuous = train(cfg)
    midpoint = work / "continuous" / "checkpoint-step-50.pt"
    resumed_cfg = KernelConfig(
        data=DataConfig(str(train_path), str(validation_path), str(tokenizer_path), str(work / "resumed")),
        model=model_cfg,
        training=training_cfg,
    )
    resumed = train(resumed_cfg, resume=midpoint)
    checkpoint = work / "resumed" / "checkpoint-step-100.pt"
    evaluated = evaluate_checkpoint(
        checkpoint, tokenizer_path, validation_path, device="xpu", dtype="bfloat16", max_windows=8
    )
    prompts = ["Việt Nam", "The model", "Năm 2026, A-42"]
    generations = [
        generate_checkpoint(checkpoint, tokenizer_path, prompt, device="xpu", dtype="bfloat16", max_new_tokens=4, seed=2026)
        for prompt in prompts
    ]
    learning_direction = continuous["final_evaluation"]["bits_per_byte"] < initial_eval["bits_per_byte"]
    finite = math.isfinite(continuous["final_train_loss"]) and math.isfinite(resumed["final_train_loss"])
    status = "PASS" if all([
        continuous["status"] == "PASS", resumed["status"] == "PASS", finite,
        learning_direction, evaluated["status"] == "PASS", all(item["text"] for item in generations),
    ]) else "REVISE"
    result = {
        **common(),
        "status": status,
        "config": cfg.to_dict(),
        "dataset_fingerprint": manifest["corpus_fingerprint"],
        "tokenizer_fingerprint": tokenizer_info["sha256"],
        "checkpoint_hash": sha256_file(checkpoint),
        "initial_evaluation": initial_eval,
        "training": continuous,
        "resume": {
            "status": resumed["status"],
            "from_step": 50,
            "to_step": 100,
            "final_train_loss": resumed["final_train_loss"],
            "final_evaluation": resumed["final_evaluation"],
        },
        "evaluation": evaluated,
        "generation": generations,
        "learning_direction_improved": learning_direction,
    }
    write_json(RESULTS / "phase1_xpu_validation.json", result)
    return result


def parity() -> dict[str, Any]:
    legacy = torch.load(PHASE0_CHECKPOINT, map_location="cpu", weights_only=False)
    cfg = ModelConfig(**legacy["config"])
    model = TransformerLM(cfg).to(device="xpu", dtype=torch.bfloat16)
    model.load_state_dict(legacy["model"])
    tokenizer = load_tokenizer(PHASE0_DATA / "mindforge-tokenizer.json")
    validation = load_token_array(PHASE0_DATA / "mindforge.validation.npy")
    phase1_eval = evaluate_tokens(model, validation, tokenizer, device="xpu", max_windows=24)
    phase0 = json.loads(PHASE0_RESULT.read_text(encoding="utf-8"))
    phase0_bpb = phase0["final_eval"]["bits_per_byte"]
    bpb_relative = abs(phase1_eval["bits_per_byte"] - phase0_bpb) / phase0_bpb
    xpu = json.loads((RESULTS / "phase1_xpu_validation.json").read_text(encoding="utf-8"))
    phase0_tps = phase0["throughput_tokens_per_second"]["median"]
    phase1_tps = xpu["training"]["throughput_tokens_per_second"]["median"]
    throughput_change = (phase1_tps - phase0_tps) / phase0_tps
    phase0_mem = phase0["peak_xpu_memory_bytes"]
    phase1_mem = xpu["training"]["peak_device_memory_bytes"]
    memory_change = (phase1_mem - phase0_mem) / phase0_mem
    status = "PASS" if bpb_relative <= 0.10 and throughput_change >= -0.25 and memory_change <= 0.25 else "REVISE"
    result = {
        **common(),
        "status": status,
        "comparison_basis": "same tokenizer, token arrays, 10.3392M architecture, context/batch, XPU/BF16; exact Phase-0 final checkpoint for BPB; per-step sustained throughput/memory against frozen Baseline-0",
        "phase0_checkpoint_hash": sha256_file(PHASE0_CHECKPOINT),
        "phase0_metric": {
            "bits_per_byte": phase0_bpb,
            "median_tokens_per_second": phase0_tps,
            "peak_memory_bytes": phase0_mem,
        },
        "phase1_metric": {
            "bits_per_byte_on_phase0_checkpoint": phase1_eval["bits_per_byte"],
            "median_tokens_per_second": phase1_tps,
            "peak_memory_bytes": phase1_mem,
        },
        "relative_bpb_difference": bpb_relative,
        "throughput_relative_change": throughput_change,
        "memory_relative_change": memory_change,
        "thresholds": {"bpb_relative_max": 0.10, "throughput_relative_min": -0.25, "memory_relative_max": 0.25},
        "phase1_evaluator_metrics": phase1_eval,
    }
    write_json(RESULTS / "phase1_parity.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen Phase-1 validation evidence")
    parser.add_argument("mode", choices=("cpu", "xpu", "parity", "all"))
    args = parser.parse_args()
    outputs = []
    if args.mode in {"cpu", "all"}:
        outputs.append(cpu_smoke())
    if args.mode in {"xpu", "all"}:
        outputs.append(xpu_validation())
    if args.mode in {"parity", "all"}:
        outputs.append(parity())
    print(json.dumps([{"status": item["status"]} for item in outputs], indent=2))
    return 0 if all(item["status"] == "PASS" for item in outputs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
