"""Independent Phase-0 evaluator for a real-language checkpoint.

This module intentionally has no dependency on the training entry point. It loads
checkpoint, tokenizer, dataset metadata and its frozen evaluation config directly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch

from phase0_real_language_common import (
    DATA_DIR,
    common_record,
    evaluate_tokens,
    generation_sanity,
    load_checkpoint,
    load_json,
    load_token_array,
    load_tokenizer,
    sha256_file,
    write_json,
)


FROZEN_PROMPTS = [
    "Việt Nam là một quốc gia",
    "The purpose of scientific research is",
    "Hà Nội nằm ở",
    "Năm 2026, tỷ lệ 12.5% và mã A-42",
    "Trong machine learning, mô hình thường",
]
FROZEN_MAX_WINDOWS = 24
FROZEN_ABS_TOLERANCE = 1e-6


def evaluate_checkpoint(checkpoint: Path, tokenizer_kind: str | None = None) -> dict[str, Any]:
    device = "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    model, _, payload = load_checkpoint(checkpoint, device=device, dtype=dtype)
    metadata = payload.get("metadata", {})
    kind = tokenizer_kind or metadata.get("tokenizer_kind")
    if kind not in {"existing", "mindforge"}:
        raise ValueError("tokenizer kind must be provided or recorded in checkpoint metadata")

    manifest = load_json(DATA_DIR / "manifest.json")
    if metadata.get("dataset_fingerprint") != manifest["corpus_fingerprint"]:
        raise ValueError("checkpoint dataset fingerprint does not match local frozen manifest")

    tokenizer = load_tokenizer(kind)
    tokens = load_token_array(DATA_DIR / f"{kind}.validation.npy")
    first = evaluate_tokens(
        model,
        tokens,
        tokenizer,
        context=model.config.max_context,
        device=device,
        max_windows=FROZEN_MAX_WINDOWS,
    )
    second = evaluate_tokens(
        model,
        tokens,
        tokenizer,
        context=model.config.max_context,
        device=device,
        max_windows=FROZEN_MAX_WINDOWS,
    )
    ce_delta = abs(first["cross_entropy"] - second["cross_entropy"])
    bpb_delta = abs(first["bits_per_byte"] - second["bits_per_byte"])
    deterministic_eval = ce_delta <= FROZEN_ABS_TOLERANCE and bpb_delta <= FROZEN_ABS_TOLERANCE
    generation = generation_sanity(model, tokenizer, FROZEN_PROMPTS, device=device)
    status = (
        "PASS"
        if first["status"] == "PASS"
        and second["status"] == "PASS"
        and deterministic_eval
        and generation["status"] == "PASS"
        else "REVISE"
    )
    record = common_record(manifest["corpus_fingerprint"])
    record.update(
        {
            "status": status,
            "checkpoint": {
                "path": f"<ignored-checkpoint>/{checkpoint.name}",
                "sha256": sha256_file(checkpoint),
                "bytes": checkpoint.stat().st_size,
                "step": int(payload["step"]),
            },
            "device": device,
            "dtype": str(dtype),
            "tokenizer": kind,
            "model_config": payload["config"],
            "dataset_manifest_sha256": sha256_file(DATA_DIR / "manifest.json"),
            "evaluation_config": {
                "max_windows": FROZEN_MAX_WINDOWS,
                "window_selection": "evenly spaced across held-out token stream",
                "absolute_repeat_tolerance": FROZEN_ABS_TOLERANCE,
                "prompts": FROZEN_PROMPTS,
            },
            "metrics": first,
            "repeat_metrics": second,
            "repeat_delta": {"cross_entropy": ce_delta, "bits_per_byte": bpb_delta},
            "deterministic_evaluation": deterministic_eval,
            "generation_sanity": generation,
            "contract": [
                "validation cross entropy",
                "bits/token",
                "bits/byte",
                "deterministic repeated evaluation",
                "deterministic bounded generation",
            ],
        }
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--tokenizer", choices=("existing", "mindforge"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate_checkpoint(args.checkpoint, args.tokenizer)
    if args.output:
        write_json(args.output, result)
    # Keep the standalone CLI portable across Windows consoles whose active
    # encoding cannot represent Vietnamese text. The evidence file itself stays
    # UTF-8 via write_json(); only terminal rendering is ASCII-escaped.
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
