"""Subprocess worker used by M2 to prove process-boundary interruption/resume."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

from .canonical import sha256_object
from .errors import DataIntegrityError
from .loader import load_experiment_config
from .m2_checkpoint import (
    apply_trainable_state,
    create_incomplete_checkpoint_sentinel,
    restore_checkpoint,
    trainable_state,
    trainable_state_hash,
    verify_checkpoint,
    write_checkpoint,
)
from .m2_model import (
    M2_STEPS_PER_PHASE,
    build_optimizer_scheduler,
    load_phase_batches,
    load_training_model,
    model_probe,
    save_full_canonical,
    train_step,
)

INTENTIONAL_INTERRUPT_EXIT = 75


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline.m2_worker")
    parser.add_argument("--mode", choices=["reference", "interrupt", "resume", "reload"], required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--config", required=False)
    parser.add_argument("--phase-id")
    parser.add_argument("--snapshot")
    parser.add_argument("--parent-delta")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--config-hash")
    parser.add_argument("--data-manifest-hash")
    parser.add_argument("--parent-artifact-hash")
    parser.add_argument("--checkpoint-dir")
    parser.add_argument("--canonical-dir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "reload":
        if not args.canonical_dir:
            raise DataIntegrityError("reload mode requires --canonical-dir")
        return _reload(Path(args.canonical_dir).resolve(), output_dir)

    required = {
        "--config": args.config,
        "--phase-id": args.phase_id,
        "--snapshot": args.snapshot,
        "--run-id": args.run_id,
        "--config-hash": args.config_hash,
        "--data-manifest-hash": args.data_manifest_hash,
        "--parent-artifact-hash": args.parent_artifact_hash,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise DataIntegrityError(f"M2 worker missing required args: {missing}")

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    config = load_experiment_config(config_path, repo_root)
    phase = next((item for item in config.phases if item.id == args.phase_id), None)
    if phase is None:
        raise DataIntegrityError(f"unknown phase {args.phase_id}")

    snapshot = Path(args.snapshot).resolve()
    model, tokenizer = load_training_model(snapshot)
    if args.parent_delta:
        state = torch.load(Path(args.parent_delta), map_location="cpu", weights_only=True)
        apply_trainable_state(model, state)

    optimizer, scheduler = build_optimizer_scheduler(model, phase)
    batches = load_phase_batches(phase, tokenizer, repo_root)

    if args.mode == "reference":
        return _reference(model, optimizer, scheduler, batches, phase.id, output_dir)
    if args.mode == "interrupt":
        return _interrupt(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            batches=batches,
            phase_id=phase.id,
            output_dir=output_dir,
            repo_root=repo_root,
            run_id=args.run_id,
            config_hash=args.config_hash,
            data_manifest_hash=args.data_manifest_hash,
            parent_artifact_hash=args.parent_artifact_hash,
        )
    if args.mode == "resume":
        if not args.checkpoint_dir:
            raise DataIntegrityError("resume mode requires --checkpoint-dir")
        return _resume(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            batches=batches,
            phase_id=phase.id,
            output_dir=output_dir,
            repo_root=repo_root,
            checkpoint_dir=Path(args.checkpoint_dir).resolve(),
            canonical_dir=Path(args.canonical_dir).resolve() if args.canonical_dir else None,
            tokenizer=tokenizer,
            source_snapshot=snapshot,
        )
    raise AssertionError(args.mode)


def _reference(model, optimizer, scheduler, batches, phase_id: str, output_dir: Path) -> int:
    metrics = []
    consumed_tokens = 0
    for index in range(M2_STEPS_PER_PHASE):
        metric = train_step(model, optimizer, scheduler, batches[index])
        consumed_tokens += int(batches[index]["input_ids"].numel())
        metrics.append({"step": index + 1, "consumed_tokens": consumed_tokens, **metric})
    final_path = output_dir / "final_trainable.pt"
    torch.save(trainable_state(model), final_path)
    result = {
        "mode": "reference",
        "phase_id": phase_id,
        "steps": M2_STEPS_PER_PHASE,
        "metrics": metrics,
        "final_state_hash": trainable_state_hash(model),
        "final_learning_rate": float(optimizer.param_groups[0]["lr"]),
        "scheduler_last_epoch": int(scheduler.last_epoch),
    }
    _write_json(output_dir / "result.json", result)
    return 0


def _interrupt(
    *,
    model,
    optimizer,
    scheduler,
    batches,
    phase_id: str,
    output_dir: Path,
    repo_root: Path,
    run_id: str,
    config_hash: str,
    data_manifest_hash: str,
    parent_artifact_hash: str,
) -> int:
    metric = train_step(model, optimizer, scheduler, batches[0])
    consumed_tokens = int(batches[0]["input_ids"].numel())
    checkpoints_root = output_dir / "checkpoints"
    sampler_state = {
        "resume_fidelity": "exact",
        "dataset_or_shard_id": f"m2-fixture:{phase_id}",
        "document_index": 1,
        "token_offset": 0,
        "packed_sequence_index": 1,
        "shuffle_state": {"algorithm": "fixed-two-batch-v1", "order": [0, 1], "next_index": 1},
        "worker_states": [],
        "mixture_state": {"phase_id": phase_id, "batch_count": M2_STEPS_PER_PHASE},
    }
    checkpoint = write_checkpoint(
        checkpoints_root=checkpoints_root,
        repo_root=repo_root,
        run_id=run_id,
        phase_id=phase_id,
        checkpoint_id="checkpoint-step-000001",
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        step=1,
        consumed_tokens=consumed_tokens,
        sampler_state=sampler_state,
        config_hash=config_hash,
        data_manifest_hash=data_manifest_hash,
        parent_artifact_hash=parent_artifact_hash,
    )
    verify_checkpoint(checkpoint, repo_root)
    partial = create_incomplete_checkpoint_sentinel(checkpoints_root, "checkpoint-step-000002")
    result = {
        "mode": "interrupt",
        "phase_id": phase_id,
        "status": "INTENTIONAL_INTERRUPT_AFTER_COMMIT",
        "step": 1,
        "metric": metric,
        "checkpoint_dir": str(checkpoint),
        "partial_sentinel": str(partial),
        "state_hash_at_interrupt": trainable_state_hash(model),
    }
    _write_json(output_dir / "result.json", result)
    return INTENTIONAL_INTERRUPT_EXIT


def _resume(
    *,
    model,
    optimizer,
    scheduler,
    batches,
    phase_id: str,
    output_dir: Path,
    repo_root: Path,
    checkpoint_dir: Path,
    canonical_dir: Path | None,
    tokenizer,
    source_snapshot: Path,
) -> int:
    manifest = restore_checkpoint(checkpoint_dir, repo_root, model, optimizer, scheduler)
    next_index = int(manifest["sampler_state"]["shuffle_state"]["next_index"])
    if next_index != 1:
        raise DataIntegrityError(f"expected M2 resume next_index=1, got {next_index}")
    metrics = []
    consumed_tokens = int(manifest["consumed_tokens"])
    for index in range(next_index, M2_STEPS_PER_PHASE):
        metric = train_step(model, optimizer, scheduler, batches[index])
        consumed_tokens += int(batches[index]["input_ids"].numel())
        metrics.append({"step": index + 1, "consumed_tokens": consumed_tokens, **metric})

    final_path = output_dir / "final_trainable.pt"
    torch.save(trainable_state(model), final_path)
    result = {
        "mode": "resume",
        "phase_id": phase_id,
        "restored_step": int(manifest["step"]),
        "restored_resume_fidelity": manifest["sampler_state"]["resume_fidelity"],
        "metrics": metrics,
        "final_state_hash": trainable_state_hash(model),
        "final_learning_rate": float(optimizer.param_groups[0]["lr"]),
        "scheduler_last_epoch": int(scheduler.last_epoch),
    }
    if canonical_dir is not None:
        canonical = save_full_canonical(model, source_snapshot, canonical_dir)
        probe = model_probe(model, tokenizer)
        result["canonical"] = canonical
        result["pre_reload_probe"] = probe
    _write_json(output_dir / "result.json", result)
    return 0


def _reload(canonical_dir: Path, output_dir: Path) -> int:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(canonical_dir, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        canonical_dir,
        local_files_only=True,
        trust_remote_code=False,
        dtype=torch.float32,
    )
    probe = model_probe(model, tokenizer)
    result = {
        "mode": "reload",
        "canonical_dir": str(canonical_dir),
        "probe": probe,
        "model_type": getattr(model.config, "model_type", None),
        "architectures": list(getattr(model.config, "architectures", []) or []),
    }
    _write_json(output_dir / "result.json", result)
    return 0


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
