"""MK-1 paired initialization and exact sample/token-budget audit.

This module may instantiate the frozen scientific model seeds, but it never
constructs an optimizer and never executes a model forward/backward pass.
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import torch

from mindforge.config import ModelConfig
from mindforge.tokenizer import load_tokenizer, sha256_file

from .contracts import (
    DIRECT_PARAMETER_COUNT,
    M1Z_PARAMETER_COUNT,
    SCIENTIFIC_TRAINING_SEEDS,
    TRAINING_LOCK,
)
from .modeling import build_arm, parameter_count, state_dict_sha256
from .trainer import (
    deterministic_sample_indices,
    load_paired_initialization,
    load_surface_records,
    prepare_paired_initialization,
)

MATERIALIZATION_RUN_ID = 35_553_551_910
MATERIALIZATION_ARTIFACT_ID = 10_619_711_251
MATERIALIZATION_ARTIFACT_DIGEST = "b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997"

TOKENIZER_RUN_ID = 35_562_370_974
TOKENIZER_ARTIFACT_ID = 10_622_602_143
TOKENIZER_ARTIFACT_DIGEST = "3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6"

TRAIN_SOURCE_SHA256 = "5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a"
TOKENIZER_SHA256 = "e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829"
TOKENIZED_TRAIN_SHA256 = "7be5c48156329e2239ac7345845f705a9b934d7bcc7e940e7dd128c0603a934e"

TRAIN_SURFACES = 4_000
TRAIN_ONE_PASS_TOKENS = 645_726
EXPECTED_SAMPLES_PER_SEED = TRAINING_LOCK.steps * TRAINING_LOCK.accumulation
EXPECTED_COMPLETE_CYCLES = EXPECTED_SAMPLES_PER_SEED // TRAIN_SURFACES
EXPECTED_TOKENS_PER_SEED = EXPECTED_COMPLETE_CYCLES * TRAIN_ONE_PASS_TOKENS

if EXPECTED_SAMPLES_PER_SEED != 40_000:
    raise AssertionError("frozen scientific sample count drift")
if EXPECTED_COMPLETE_CYCLES != 10:
    raise AssertionError("frozen complete-cycle count drift")
if EXPECTED_TOKENS_PER_SEED != 6_457_260:
    raise AssertionError("frozen exact token budget drift")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _input_text_sha256(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"JSONL is empty: {path}")
    return rows


def verify_and_align_train_inputs(
    materialization_root: Path,
    tokenizer_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train_source = materialization_root / "mk1_materialized_v0_1" / "train.jsonl"
    tokenizer_path = tokenizer_root / "mk1_tokenizer_freeze_v0_1" / "mk1-tokenizer.json"
    tokenized_train = tokenizer_root / "mk1_tokenizer_freeze_v0_1" / "tokenized_train.jsonl"

    if sha256_file(train_source) != TRAIN_SOURCE_SHA256:
        raise ValueError("TRAIN source SHA-256 mismatch")
    if sha256_file(tokenizer_path) != TOKENIZER_SHA256:
        raise ValueError("scientific tokenizer SHA-256 mismatch")
    if sha256_file(tokenized_train) != TOKENIZED_TRAIN_SHA256:
        raise ValueError("tokenized TRAIN manifest SHA-256 mismatch")

    source_rows = load_surface_records(train_source)
    manifest_rows = _load_jsonl(tokenized_train)
    if len(source_rows) != TRAIN_SURFACES or len(manifest_rows) != TRAIN_SURFACES:
        raise ValueError("TRAIN surface count mismatch")

    tokenizer = load_tokenizer(tokenizer_path)
    if tokenizer.get_vocab_size() != 3261:
        raise ValueError("frozen tokenizer actual vocabulary mismatch")

    aligned: list[dict[str, Any]] = []
    total_tokens = 0
    maximum_token_id = -1
    for source, frozen in zip(source_rows, manifest_rows):
        source_key = (str(source["scene_id"]), str(source["renderer_family"]))
        frozen_key = (str(frozen["scene_id"]), str(frozen["renderer_family"]))
        if source_key != frozen_key:
            raise ValueError(f"TRAIN index alignment mismatch: {source_key} != {frozen_key}")
        text = str(source["input_text"])
        if _input_text_sha256(text) != frozen["input_text_sha256"]:
            raise ValueError(f"TRAIN input-text hash mismatch: {source_key}")
        token_ids = tokenizer.encode(text).ids
        if token_ids != frozen["token_ids"]:
            raise ValueError(f"TRAIN exact token-ID mismatch: {source_key}")
        if len(token_ids) != int(frozen["token_count"]):
            raise ValueError(f"TRAIN token-count mismatch: {source_key}")
        if not token_ids:
            raise ValueError(f"TRAIN empty encoded input: {source_key}")
        total_tokens += len(token_ids)
        maximum_token_id = max(maximum_token_id, max(token_ids))
        aligned.append(
            {
                "scene_id": source_key[0],
                "renderer_family": source_key[1],
                "sample_key": f"{source_key[0]}:{source_key[1]}",
                "token_count": len(token_ids),
            }
        )

    if total_tokens != TRAIN_ONE_PASS_TOKENS:
        raise ValueError(f"TRAIN one-pass token total mismatch: {total_tokens}")

    return aligned, {
        "train_source_sha256": TRAIN_SOURCE_SHA256,
        "tokenizer_sha256": TOKENIZER_SHA256,
        "tokenized_train_sha256": TOKENIZED_TRAIN_SHA256,
        "surface_records": len(aligned),
        "one_pass_tokens": total_tokens,
        "maximum_token_id": maximum_token_id,
        "index_alignment": "EXACT",
        "exact_token_ids_reencoded": True,
    }


def write_schedule(
    rows: list[dict[str, Any]],
    *,
    seed: int,
    output_path: Path,
    steps: int,
    accumulation: int,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite schedule: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schedule = deterministic_sample_indices(len(rows), seed)
    counts: Counter[str] = Counter()
    cumulative_tokens = 0
    consumed = 0
    with output_path.open("x", encoding="utf-8", newline="\n") as handle:
        for step in range(1, steps + 1):
            sample_keys: list[str] = []
            token_counts: list[int] = []
            for _ in range(accumulation):
                index = next(schedule)
                row = rows[index]
                key = str(row["sample_key"])
                tokens = int(row["token_count"])
                sample_keys.append(key)
                token_counts.append(tokens)
                counts[key] += 1
                consumed += 1
            step_tokens = sum(token_counts)
            cumulative_tokens += step_tokens
            record = {
                "step": step,
                "sample_keys": sample_keys,
                "token_counts": token_counts,
                "step_input_tokens": step_tokens,
                "cumulative_input_tokens": cumulative_tokens,
            }
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    multiplicities = list(counts.values())
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "bytes": output_path.stat().st_size,
        "steps": steps,
        "accumulation": accumulation,
        "sample_count": consumed,
        "total_tokens": cumulative_tokens,
        "unique_sample_keys": len(counts),
        "minimum_multiplicity": min(multiplicities),
        "maximum_multiplicity": max(multiplicities),
    }


def derive_paired_schedule(
    rows: list[dict[str, Any]],
    seed: int,
    output_root: Path,
) -> dict[str, Any]:
    canonical = output_root / f"schedule_seed_{seed}.jsonl"
    with tempfile.TemporaryDirectory(prefix=f"mk1-schedule-{seed}-") as temp:
        temp_root = Path(temp)
        direct_path = temp_root / "direct.jsonl"
        m1z_path = temp_root / "m1z.jsonl"
        direct = write_schedule(
            rows,
            seed=seed,
            output_path=direct_path,
            steps=TRAINING_LOCK.steps,
            accumulation=TRAINING_LOCK.accumulation,
        )
        m1z = write_schedule(
            rows,
            seed=seed,
            output_path=m1z_path,
            steps=TRAINING_LOCK.steps,
            accumulation=TRAINING_LOCK.accumulation,
        )
        if direct["sha256"] != m1z["sha256"]:
            raise AssertionError(f"paired schedule SHA mismatch for seed {seed}")
        if not filecmp.cmp(direct_path, m1z_path, shallow=False):
            raise AssertionError(f"paired schedule bytes differ for seed {seed}")
        shutil.copyfile(direct_path, canonical)

    canonical_sha = sha256_file(canonical)
    if canonical_sha != direct["sha256"]:
        raise AssertionError("canonical schedule copy changed bytes")
    if direct["sample_count"] != EXPECTED_SAMPLES_PER_SEED:
        raise AssertionError("scientific sample count mismatch")
    if direct["unique_sample_keys"] != TRAIN_SURFACES:
        raise AssertionError("scientific schedule does not cover all TRAIN surfaces")
    if direct["minimum_multiplicity"] != EXPECTED_COMPLETE_CYCLES:
        raise AssertionError("minimum TRAIN multiplicity mismatch")
    if direct["maximum_multiplicity"] != EXPECTED_COMPLETE_CYCLES:
        raise AssertionError("maximum TRAIN multiplicity mismatch")
    if direct["total_tokens"] != EXPECTED_TOKENS_PER_SEED:
        raise AssertionError("scientific exact token budget mismatch")

    return {
        **direct,
        "path": str(canonical),
        "sha256": canonical_sha,
        "paired_arm_sha_equal": True,
        "paired_arm_bytes_equal": True,
        "direct_total_tokens": direct["total_tokens"],
        "m1z_total_tokens": m1z["total_tokens"],
        "absolute_token_gap": abs(int(direct["total_tokens"]) - int(m1z["total_tokens"])),
        "relative_token_gap": 0.0,
    }


def paired_initialization_audit(seed: int, output_root: Path) -> dict[str, Any]:
    init_path = output_root / f"paired_init_seed_{seed}.pt"
    prepared = prepare_paired_initialization(seed, init_path)
    file_sha = sha256_file(init_path)
    state, loaded_digest = load_paired_initialization(init_path, seed)
    if loaded_digest != prepared["sha256"]:
        raise AssertionError("paired initialization digest changed after reload")

    direct = build_arm("direct", state, ModelConfig())
    m1z = build_arm("m1z", state, ModelConfig())
    direct_backbone = state_dict_sha256(direct.backbone.state_dict())
    m1z_backbone = state_dict_sha256(m1z.backbone.state_dict())
    if direct_backbone != loaded_digest or m1z_backbone != loaded_digest:
        raise AssertionError("paired arm backbone identity failed")

    direct_zero = bool(
        torch.count_nonzero(direct.readout.weight).item() == 0
        and torch.count_nonzero(direct.readout.bias).item() == 0
    )
    m1z_zero = bool(
        torch.count_nonzero(m1z.readout.weight).item() == 0
        and torch.count_nonzero(m1z.readout.bias).item() == 0
    )
    if not direct_zero or not m1z_zero:
        raise AssertionError("frozen readout zero initialization failed")

    direct_params = parameter_count(direct)
    m1z_params = parameter_count(m1z)
    if direct_params != DIRECT_PARAMETER_COUNT:
        raise AssertionError("DIRECT parameter count mismatch")
    if m1z_params != M1Z_PARAMETER_COUNT:
        raise AssertionError("M1-Z parameter count mismatch")

    return {
        "seed": seed,
        "file_path": str(init_path),
        "file_sha256": file_sha,
        "state_dict_sha256": loaded_digest,
        "direct_backbone_sha256": direct_backbone,
        "m1z_backbone_sha256": m1z_backbone,
        "direct_parameter_count": direct_params,
        "m1z_parameter_count": m1z_params,
        "direct_readout_zero": direct_zero,
        "m1z_readout_zero": m1z_zero,
        "model_config": ModelConfig().__dict__,
    }


def run(
    materialization_root: Path,
    tokenizer_root: Path,
    output_root: Path,
    result_path: Path,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite pretraining audit output: {output_root}")
    if result_path.exists():
        raise FileExistsError(f"refusing to overwrite pretraining audit result: {result_path}")
    output_root.mkdir(parents=True)

    train_rows, input_alignment = verify_and_align_train_inputs(
        materialization_root,
        tokenizer_root,
    )

    seed_results: dict[str, Any] = {}
    schedule_hashes: list[str] = []
    for seed in SCIENTIFIC_TRAINING_SEEDS:
        init = paired_initialization_audit(seed, output_root)
        schedule = derive_paired_schedule(train_rows, seed, output_root)
        if schedule["absolute_token_gap"] != 0:
            raise AssertionError("paired token budget gap must be exactly zero")
        seed_results[str(seed)] = {
            "paired_initialization": init,
            "schedule": schedule,
        }
        schedule_hashes.append(str(schedule["sha256"]))

    result = {
        "schema": "MK1-PAIRED-INIT-TOKEN-BUDGET-AUDIT-v0.1",
        "status": "PAIRED_INIT_AND_TOKEN_BUDGET_PASS",
        "source_provenance": {
            "materialization_run_id": MATERIALIZATION_RUN_ID,
            "materialization_artifact_id": MATERIALIZATION_ARTIFACT_ID,
            "materialization_artifact_zip_sha256": MATERIALIZATION_ARTIFACT_DIGEST,
            "tokenizer_run_id": TOKENIZER_RUN_ID,
            "tokenizer_artifact_id": TOKENIZER_ARTIFACT_ID,
            "tokenizer_artifact_zip_sha256": TOKENIZER_ARTIFACT_DIGEST,
        },
        "input_alignment": input_alignment,
        "training_lock": {
            "steps": TRAINING_LOCK.steps,
            "micro_batch": TRAINING_LOCK.micro_batch,
            "accumulation": TRAINING_LOCK.accumulation,
            "expected_samples_per_seed": EXPECTED_SAMPLES_PER_SEED,
            "expected_complete_cycles": EXPECTED_COMPLETE_CYCLES,
            "expected_tokens_per_seed": EXPECTED_TOKENS_PER_SEED,
        },
        "scientific_seeds": list(SCIENTIFIC_TRAINING_SEEDS),
        "seed_results": seed_results,
        "schedule_hash_collision_count": len(schedule_hashes) - len(set(schedule_hashes)),
        "execution_boundary": {
            "optimizer_constructed": False,
            "model_forward_executed": False,
            "model_backward_executed": False,
            "training_executed": False,
            "validation_model_outcome_used": False,
            "pristine_confirmatory_model_inference": False,
        },
    }
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialization-root", required=True)
    parser.add_argument("--tokenizer-root", required=True)
    parser.add_argument("--output-root", default="mk1_pretraining_audit_v0_1")
    parser.add_argument("--result", default="PAIRED_INIT_AND_TOKEN_BUDGET_RESULT.json")
    args = parser.parse_args()
    run(
        Path(args.materialization_root),
        Path(args.tokenizer_root),
        Path(args.output_root),
        Path(args.result),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
