"""Pinned Qwen M2 model/tokenizer utilities and fixture batch construction."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from huggingface_hub import snapshot_download
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from .canonical import sha256_file, sha256_object
from .errors import DataIntegrityError
from .models import ExperimentConfig, PhaseSpec
from .reasoning import serialize_reasoning_sample

M2_TRAINABLE_PARAMETER = "model.norm.weight"
M2_STEPS_PER_PHASE = 2
M2_SEED = 20260920
M2_MAX_LENGTH = 48


def prepare_pinned_snapshot(
    config: ExperimentConfig,
    *,
    cache_dir: Path,
) -> tuple[Path, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    snapshot = Path(
        snapshot_download(
            repo_id=config.model.id,
            revision=config.model.revision,
            cache_dir=str(cache_dir),
            allow_patterns=[
                "*.json",
                "*.safetensors",
                "*.jinja",
                "tokenizer*",
                "vocab*",
                "merges*",
                "*.model",
            ],
        )
    ).resolve()
    files = []
    for path in sorted(snapshot.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(snapshot).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    if not files:
        raise DataIntegrityError("pinned model snapshot resolved zero files")

    hf_config = AutoConfig.from_pretrained(snapshot, local_files_only=True, trust_remote_code=False)
    if getattr(hf_config, "model_type", None) != "qwen2":
        raise DataIntegrityError(f"expected qwen2 model_type, got {getattr(hf_config, 'model_type', None)!r}")

    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True, trust_remote_code=False)
    if not getattr(tokenizer, "chat_template", None):
        raise DataIntegrityError("pinned Qwen tokenizer has no chat_template")
    identity = {
        "model_id": config.model.id,
        "revision": config.model.revision,
        "snapshot_path_tail": snapshot.name,
        "model_type": hf_config.model_type,
        "architectures": list(getattr(hf_config, "architectures", []) or []),
        "tokenizer_class": tokenizer.__class__.__name__,
        "tokenizer_vocab_size": int(len(tokenizer)),
        "chat_template_hash": sha256_object(tokenizer.chat_template),
        "files": files,
        "snapshot_manifest_hash": sha256_object(files),
    }
    return snapshot, identity


def load_training_model(snapshot: Path) -> tuple[torch.nn.Module, Any]:
    configure_determinism(M2_SEED)
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        snapshot,
        local_files_only=True,
        trust_remote_code=False,
        dtype=torch.float32,
    )
    model.config.use_cache = False
    model.train()

    found = False
    for name, parameter in model.named_parameters():
        parameter.requires_grad_(name == M2_TRAINABLE_PARAMETER)
        found = found or name == M2_TRAINABLE_PARAMETER
    if not found:
        candidates = [name for name, _ in model.named_parameters() if name.endswith(".norm.weight")]
        raise DataIntegrityError(
            f"required M2 trainable parameter {M2_TRAINABLE_PARAMETER!r} not found; norm candidates={candidates[-10:]}"
        )
    trainable = [name for name, parameter in model.named_parameters() if parameter.requires_grad]
    if trainable != [M2_TRAINABLE_PARAMETER]:
        raise DataIntegrityError(f"unexpected M2 trainable parameter set: {trainable}")
    return model, tokenizer


def configure_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def build_optimizer_scheduler(model: torch.nn.Module, phase: PhaseSpec) -> tuple[Any, Any]:
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not trainable:
        raise DataIntegrityError("M2 model has no trainable parameters")
    optimizer = torch.optim.SGD(trainable, lr=phase.training.learning_rate, momentum=0.9)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)
    return optimizer, scheduler


def load_phase_batches(
    phase: PhaseSpec,
    tokenizer: Any,
    repo_root: Path,
) -> list[dict[str, torch.Tensor]]:
    if phase.type == "cpt":
        records = []
        for dataset_id in phase.datasets:
            path = _dataset_fixture_path(dataset_id, repo_root)
            if path is None:
                continue
            for record in _read_jsonl(path):
                text = record.get("text")
                if text is None:
                    text = record.get("code")
                if isinstance(text, str) and text.strip():
                    records.append(text)
                if len(records) >= M2_STEPS_PER_PHASE:
                    break
            if len(records) >= M2_STEPS_PER_PHASE:
                break
        if len(records) < M2_STEPS_PER_PHASE:
            raise DataIntegrityError(f"phase {phase.id}: insufficient CPT fixture records")
        return [_cpt_batch(tokenizer, text) for text in records[:M2_STEPS_PER_PHASE]]

    if phase.type in {"sft", "reasoning_sft", "lora_sft"}:
        path = repo_root / "tests/fixtures/data/reasoning_mini.jsonl"
        records = _read_jsonl(path)
        if len(records) < M2_STEPS_PER_PHASE:
            raise DataIntegrityError(f"phase {phase.id}: insufficient reasoning fixture records")
        return [_reasoning_batch(tokenizer, record, repo_root) for record in records[:M2_STEPS_PER_PHASE]]

    raise DataIntegrityError(f"phase {phase.id}: unsupported M2 phase type {phase.type}")


def train_step(
    model: torch.nn.Module,
    optimizer: Any,
    scheduler: Any,
    batch: dict[str, torch.Tensor],
) -> dict[str, Any]:
    optimizer.zero_grad(set_to_none=True)
    outputs = model(**batch)
    loss = outputs.loss
    if loss is None or not torch.isfinite(loss).item():
        raise DataIntegrityError(f"non-finite M2 loss: {loss}")
    loss.backward()
    grad_norm = torch.nn.utils.clip_grad_norm_(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        max_norm=1.0,
    )
    optimizer.step()
    scheduler.step()
    active_loss_tokens = int((batch["labels"] != -100).sum().item())
    return {
        "loss": float(loss.detach().cpu().item()),
        "grad_norm": float(torch.as_tensor(grad_norm).detach().cpu().item()),
        "active_loss_tokens": active_loss_tokens,
        "learning_rate": float(optimizer.param_groups[0]["lr"]),
    }


def save_full_canonical(
    model: torch.nn.Module,
    tokenizer: Any,
    output_dir: Path,
) -> dict[str, Any]:
    if output_dir.exists():
        import shutil

        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    model.save_pretrained(output_dir, safe_serialization=True, max_shard_size="1GB")
    tokenizer.save_pretrained(output_dir)
    files = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(output_dir).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return {
        "files": files,
        "directory_hash": sha256_object(files),
        "chat_template_hash": sha256_object(tokenizer.chat_template),
    }


def model_probe(model: torch.nn.Module, tokenizer: Any) -> dict[str, Any]:
    model.eval()
    encoded = tokenizer(
        "M2 deterministic reload probe.",
        return_tensors="pt",
        add_special_tokens=False,
        truncation=True,
        max_length=24,
    )
    with torch.no_grad():
        logits = model(**encoded).logits[:, -1, :].float().cpu().contiguous()
    raw = logits.view(torch.uint8).numpy().tobytes()
    return {
        "logits_sha256": hashlib.sha256(raw).hexdigest(),
        "shape": list(logits.shape),
        "tokenizer_vocab_size": int(len(tokenizer)),
        "chat_template_hash": sha256_object(tokenizer.chat_template),
    }


def environment_versions() -> dict[str, str]:
    packages = [
        "torch",
        "transformers",
        "huggingface-hub",
        "safetensors",
        "tokenizers",
        "numpy",
    ]
    return {name: importlib.metadata.version(name) for name in packages}


def _cpt_batch(tokenizer: Any, text: str) -> dict[str, torch.Tensor]:
    ids = tokenizer(
        text + (tokenizer.eos_token or ""),
        return_tensors="pt",
        add_special_tokens=False,
        truncation=True,
        max_length=M2_MAX_LENGTH,
    )
    labels = ids["input_ids"].clone()
    return {
        "input_ids": ids["input_ids"],
        "attention_mask": ids.get("attention_mask", torch.ones_like(ids["input_ids"])),
        "labels": labels,
    }


def _reasoning_batch(tokenizer: Any, record: dict[str, Any], repo_root: Path) -> dict[str, torch.Tensor]:
    import yaml

    profile_path = (
        repo_root
        / "docs/model-training-pipeline/profiles/qwen2.5-0.5b-instruct-r0.yaml"
    )
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise DataIntegrityError("R0 reasoning model profile must be an object")
    serialized = serialize_reasoning_sample(
        tokenizer,
        profile,
        record,
        max_length=M2_MAX_LENGTH,
    )
    input_ids = torch.tensor([list(serialized.input_ids)], dtype=torch.long)
    labels = torch.tensor([list(serialized.labels)], dtype=torch.long)
    return {
        "input_ids": input_ids,
        "attention_mask": torch.ones_like(input_ids),
        "labels": labels,
    }


def _dataset_fixture_path(dataset_id: str, repo_root: Path) -> Path | None:
    mapping = {
        "wiki_mini": repo_root / "tests/fixtures/data/wiki_mini.jsonl",
        "code_mini": repo_root / "tests/fixtures/data/code_mini.jsonl",
        "reasoning_mini": repo_root / "tests/fixtures/data/reasoning_mini.jsonl",
    }
    return mapping.get(dataset_id)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise DataIntegrityError(f"fixture record must be object: {path}")
            records.append(value)
    return records
