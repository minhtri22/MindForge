"""Scientific MK-1 trainer implementation. Execution remains separately gated."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Literal

import numpy as np
import torch
from tokenizers import Tokenizer

from mindforge.config import ModelConfig, TrainingConfig
from mindforge.device import resolve_device
from mindforge.tokenizer import load_tokenizer, sha256_file
from mindforge.train import learning_rate_multiplier

from .contracts import (
    DIRECT_PARAMETER_COUNT,
    M1Z_PARAMETER_COUNT,
    SCIENTIFIC_TRAINING_SEEDS,
    TRAINING_LOCK,
)
from .losses import direct_loss, m1z_loss
from .metrics import canonical_metrics, canonical_to_python, decode_direct_logits
from .modeling import build_arm, frozen_backbone_state, parameter_count, state_dict_sha256
from .recompose import recompose_logits


def load_surface_records(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError("surface record file is empty")
    rows.sort(key=lambda row: (str(row["scene_id"]), str(row["renderer_family"])))
    return rows


def deterministic_sample_indices(count: int, seed: int) -> Iterator[int]:
    if count <= 0:
        raise ValueError("count must be positive")
    cycle = 0
    while True:
        rng = np.random.default_rng(seed + cycle * 1_000_003)
        order = rng.permutation(count)
        for index in order.tolist():
            yield int(index)
        cycle += 1


def encoded_input(tokenizer: Tokenizer, text: str, device: torch.device) -> torch.Tensor:
    ids = tokenizer.encode(text).ids
    if not ids:
        raise ValueError("encoded scientific sample cannot be empty")
    if len(ids) > TRAINING_LOCK.max_context:
        raise ValueError("INPUT_LENGTH_CONTRACT_FAIL")
    if min(ids) < 0 or max(ids) >= ModelConfig().vocab_size:
        raise ValueError("token ID exceeds frozen B0 vocabulary")
    return torch.tensor([ids], dtype=torch.long, device=device)


def target_tensors(record: dict[str, Any], device: torch.device) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    z = record["gold_z"]
    c = record["gold_c"]
    z_target = {
        "z1": torch.tensor([z["z1"]], dtype=torch.float32, device=device),
        "z2_comparator": torch.tensor([z["z2_comparator"]], dtype=torch.long, device=device),
        "z2_temporal_precision": torch.tensor([z["z2_temporal_precision"]], dtype=torch.long, device=device),
        "z2_scalars": torch.tensor([z["z2_scalars"]], dtype=torch.float32, device=device),
        "z2_scalar_mask": torch.tensor([z["z2_scalar_mask"]], dtype=torch.bool, device=device),
        "z3_evidence_scope": torch.tensor([z["z3_evidence_scope"]], dtype=torch.long, device=device),
        "z3_asserted_scope": torch.tensor([z["z3_asserted_scope"]], dtype=torch.long, device=device),
        "z3_scope_relation": torch.tensor([z["z3_scope_relation"]], dtype=torch.long, device=device),
        "z4": torch.tensor([z["z4"]], dtype=torch.float32, device=device),
    }
    c_target = {
        "c1": torch.tensor([c["c1"]], dtype=torch.float32, device=device),
        "c2": torch.tensor([c["c2"]], dtype=torch.long, device=device),
        "c3": torch.tensor([c["c3"]], dtype=torch.long, device=device),
        "c4": torch.tensor([c["c4"]], dtype=torch.long, device=device),
        "c5": torch.tensor([c["c5"]], dtype=torch.float32, device=device),
    }
    return z_target, c_target


def prepare_paired_initialization(seed: int, output_path: str | Path) -> dict[str, Any]:
    if seed not in SCIENTIFIC_TRAINING_SEEDS:
        raise ValueError("paired scientific initialization requires a frozen scientific seed")
    path = Path(output_path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite paired initialization: {path}")
    state = frozen_backbone_state(seed, ModelConfig())
    digest = state_dict_sha256(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"seed": seed, "model_config": ModelConfig().__dict__, "state_dict": state, "sha256": digest}, path)
    return {"seed": seed, "sha256": digest, "path": str(path)}


def load_paired_initialization(path: str | Path, expected_seed: int) -> tuple[dict[str, torch.Tensor], str]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if int(payload["seed"]) != expected_seed:
        raise ValueError("paired initialization seed mismatch")
    if payload["model_config"] != ModelConfig().__dict__:
        raise ValueError("paired initialization model config mismatch")
    state = payload["state_dict"]
    digest = state_dict_sha256(state)
    if digest != payload["sha256"]:
        raise ValueError("paired initialization state hash mismatch")
    return state, digest


@torch.no_grad()
def evaluate_canonical(
    model: torch.nn.Module,
    arm: Literal["direct", "m1z"],
    tokenizer: Tokenizer,
    records: list[dict[str, Any]],
    device: torch.device,
) -> dict[str, Any]:
    model.eval()
    gold_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for record in records:
        logits = model(encoded_input(tokenizer, record["input_text"], device))
        decoded = decode_direct_logits(logits) if arm == "direct" else recompose_logits(logits)
        pred_rows.extend(canonical_to_python(decoded))
        gold_rows.append(record["gold_c"])
    metrics = canonical_metrics(gold_rows, pred_rows)
    return {"metrics": metrics, "predictions": pred_rows}


def _save_checkpoint(
    path: Path,
    *,
    arm: str,
    seed: int,
    step: int,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    tokenizer_sha256: str,
    paired_init_sha256: str,
    best_validation_score: float,
    best_step: int | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "schema": "MK1-TRAIN-CHECKPOINT-v0.1",
            "arm": arm,
            "seed": seed,
            "step": step,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "tokenizer_sha256": tokenizer_sha256,
            "paired_init_sha256": paired_init_sha256,
            "best_validation_score": best_validation_score,
            "best_step": best_step,
        },
        path,
    )


def train_arm(
    *,
    arm: Literal["direct", "m1z"],
    seed: int,
    paired_initialization_path: str | Path,
    tokenizer_path: str | Path,
    train_records_path: str | Path,
    validation_records_path: str | Path,
    run_dir: str | Path,
    resume_path: str | Path | None = None,
) -> dict[str, Any]:
    if seed not in SCIENTIFIC_TRAINING_SEEDS:
        raise ValueError("scientific training seed is not in the frozen set")
    tokenizer = load_tokenizer(tokenizer_path)
    vocab_actual = tokenizer.get_vocab_size()
    if not 258 <= vocab_actual <= ModelConfig().vocab_size:
        raise ValueError("TOKENIZER_CONTRACT_FAIL")
    tokenizer_sha = sha256_file(tokenizer_path)
    train_rows = load_surface_records(train_records_path)
    validation_rows = load_surface_records(validation_records_path)
    if {row["split"] for row in train_rows} != {"TRAIN"}:
        raise ValueError("training file contains non-TRAIN records")
    if {row["split"] for row in validation_rows} != {"VALIDATION"}:
        raise ValueError("validation file contains non-VALIDATION records")

    paired_state, paired_sha = load_paired_initialization(paired_initialization_path, seed)
    model = build_arm(arm, paired_state, ModelConfig())
    expected = DIRECT_PARAMETER_COUNT if arm == "direct" else M1Z_PARAMETER_COUNT
    if parameter_count(model) != expected:
        raise AssertionError("arm parameter count violates implementation lock")

    spec = resolve_device(TRAINING_LOCK.device, TRAINING_LOCK.dtype)
    model = model.to(device=spec.device, dtype=spec.dtype)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=TRAINING_LOCK.learning_rate,
        weight_decay=TRAINING_LOCK.weight_decay,
    )
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    start_step = 0
    best_score = float("-inf")
    best_step: int | None = None
    if resume_path is not None:
        payload = torch.load(resume_path, map_location=spec.device, weights_only=False)
        if payload["arm"] != arm or int(payload["seed"]) != seed:
            raise ValueError("resume checkpoint arm/seed mismatch")
        if payload["tokenizer_sha256"] != tokenizer_sha or payload["paired_init_sha256"] != paired_sha:
            raise ValueError("resume checkpoint provenance mismatch")
        model.load_state_dict(payload["model_state"], strict=True)
        optimizer.load_state_dict(payload["optimizer_state"])
        start_step = int(payload["step"])
        best_score = float(payload["best_validation_score"])
        best_step = payload["best_step"]

    schedule = deterministic_sample_indices(len(train_rows), seed)
    for _ in range(start_step * TRAINING_LOCK.accumulation):
        next(schedule)

    lr_config = TrainingConfig(
        steps=TRAINING_LOCK.steps,
        micro_batch=TRAINING_LOCK.micro_batch,
        accumulation=TRAINING_LOCK.accumulation,
        learning_rate=TRAINING_LOCK.learning_rate,
        weight_decay=TRAINING_LOCK.weight_decay,
        gradient_clip=TRAINING_LOCK.gradient_clip,
        warmup_fraction=TRAINING_LOCK.warmup_fraction,
        min_lr_fraction=TRAINING_LOCK.min_lr_fraction,
        eval_interval=TRAINING_LOCK.validation_interval,
        checkpoint_interval=TRAINING_LOCK.validation_interval,
        eval_windows=1,
        seed=seed,
        device=TRAINING_LOCK.device,
        dtype=TRAINING_LOCK.dtype,
    )

    metrics_path = run_path / "metrics.jsonl"
    if start_step == 0 and metrics_path.exists():
        raise FileExistsError("refusing to overwrite an existing scientific run")

    for step in range(start_step, TRAINING_LOCK.steps):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        accumulated = 0.0
        sample_ids: list[str] = []
        for _micro in range(TRAINING_LOCK.accumulation):
            record = train_rows[next(schedule)]
            sample_ids.append(f"{record['scene_id']}:{record['renderer_family']}")
            x = encoded_input(tokenizer, record["input_text"], spec.device)
            z_target, c_target = target_tensors(record, spec.device)
            logits = model(x)
            loss, _ = direct_loss(logits, c_target) if arm == "direct" else m1z_loss(logits, z_target)
            (loss / TRAINING_LOCK.accumulation).backward()
            accumulated += float(loss.detach().cpu()) / TRAINING_LOCK.accumulation

        torch.nn.utils.clip_grad_norm_(model.parameters(), TRAINING_LOCK.gradient_clip)
        lr = TRAINING_LOCK.learning_rate * learning_rate_multiplier(step, lr_config)
        for group in optimizer.param_groups:
            group["lr"] = lr
        optimizer.step()
        completed = step + 1

        row: dict[str, Any] = {
            "step": completed,
            "train_loss": accumulated,
            "learning_rate": lr,
            "sample_ids": sample_ids,
            "validation_balanced_score": None,
        }
        if completed % TRAINING_LOCK.validation_interval == 0:
            validation = evaluate_canonical(model, arm, tokenizer, validation_rows, spec.device)
            score = float(validation["metrics"]["balanced_score"])
            row["validation_balanced_score"] = score
            latest = run_path / "latest.pt"
            if score > best_score:
                best_score = score
                best_step = completed
                _save_checkpoint(
                    run_path / "best.pt",
                    arm=arm,
                    seed=seed,
                    step=completed,
                    model=model,
                    optimizer=optimizer,
                    tokenizer_sha256=tokenizer_sha,
                    paired_init_sha256=paired_sha,
                    best_validation_score=best_score,
                    best_step=best_step,
                )
            _save_checkpoint(
                latest,
                arm=arm,
                seed=seed,
                step=completed,
                model=model,
                optimizer=optimizer,
                tokenizer_sha256=tokenizer_sha,
                paired_init_sha256=paired_sha,
                best_validation_score=best_score,
                best_step=best_step,
            )

        with metrics_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    result = {
        "schema": "MK1-TRAIN-RESULT-v0.1",
        "status": "COMPLETE",
        "arm": arm,
        "seed": seed,
        "steps": TRAINING_LOCK.steps,
        "best_validation_balanced_score": best_score,
        "best_step": best_step,
        "tokenizer_sha256": tokenizer_sha,
        "paired_init_sha256": paired_sha,
        "parameter_count": expected,
    }
    (run_path / "run.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
