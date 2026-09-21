"""MK-1 TRAIN-only scientific tokenizer freeze and tokenized-input audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from mindforge.config import ModelConfig
from mindforge.tokenizer import (
    SPECIAL_TOKENS,
    load_tokenizer,
    metadata,
    sha256_file,
    train_tokenizer,
)

SOURCE_ARTIFACT_ID = 10_619_711_251
SOURCE_RUN_ID = 35_553_551_910
SOURCE_ARTIFACT_DIGEST = "b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997"

SOURCE_SPLITS = {
    "TRAIN": {
        "relative_path": "mk1_materialized_v0_1/train.jsonl",
        "sha256": "5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a",
        "surface_records": 4_000,
    },
    "VALIDATION": {
        "relative_path": "mk1_materialized_v0_1/validation.jsonl",
        "sha256": "8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495",
        "surface_records": 800,
    },
    "PRISTINE_CONFIRMATORY": {
        "relative_path": "mk1_materialized_v0_1/pristine_confirmatory.jsonl",
        "sha256": "5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6",
        "surface_records": 1_200,
    },
}

MODEL_VOCAB_SIZE = ModelConfig().vocab_size
REQUESTED_TOKENIZER_VOCAB_SIZE = 16_384
MAX_CONTEXT = ModelConfig().max_context


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _count_nonempty_lines(path: Path) -> int:
    count = 0
    with path.open("rb") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def verify_source_files(root: Path, events: list[str]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for split, contract in SOURCE_SPLITS.items():
        path = root / str(contract["relative_path"])
        if not path.is_file():
            raise FileNotFoundError(f"missing frozen source split: {path}")
        digest = sha256_file(path)
        if digest != contract["sha256"]:
            raise ValueError(f"{split} SHA-256 mismatch: {digest}")
        count = _count_nonempty_lines(path)
        if count != contract["surface_records"]:
            raise ValueError(f"{split} surface count mismatch: {count}")
        evidence[split] = {
            "path": str(path),
            "sha256": digest,
            "bytes": path.stat().st_size,
            "surface_records": count,
        }
    events.append("SOURCE_SPLIT_HASHES_AND_COUNTS_VERIFIED")
    return evidence


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def extract_train_corpus(
    train_path: Path,
    corpus_path: Path,
    events: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = _read_jsonl(train_path)
    if len(rows) != SOURCE_SPLITS["TRAIN"]["surface_records"]:
        raise ValueError("TRAIN row count changed during corpus extraction")
    if {str(row.get("split")) for row in rows} != {"TRAIN"}:
        raise ValueError("TRAIN source contains non-TRAIN rows")

    corpus_path.parent.mkdir(parents=True, exist_ok=False)
    with corpus_path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            text = row.get("input_text")
            if not isinstance(text, str) or not text:
                raise ValueError("TRAIN input_text must be a non-empty string")
            handle.write(text)
            handle.write("\n")

    corpus = {
        "source": "TRAIN[*].input_text_only",
        "surface_records": len(rows),
        "bytes": corpus_path.stat().st_size,
        "sha256": sha256_file(corpus_path),
        "path": str(corpus_path),
    }
    events.append("TRAIN_INPUT_TEXT_ONLY_CORPUS_FROZEN")
    return rows, corpus


def fit_and_freeze_tokenizer(
    corpus_path: Path,
    tokenizer_path: Path,
    events: list[str],
) -> tuple[Any, dict[str, Any]]:
    events.append("TOKENIZER_FIT_STARTED_TRAIN_ONLY")
    tokenizer = train_tokenizer(
        [corpus_path],
        tokenizer_path,
        vocab_size=REQUESTED_TOKENIZER_VOCAB_SIZE,
    )
    events.append("TOKENIZER_JSON_SAVED")
    tokenizer_sha = sha256_file(tokenizer_path)
    events.append("TOKENIZER_SHA256_FROZEN")

    info = metadata(tokenizer_path, tokenizer)
    if info["sha256"] != tokenizer_sha:
        raise AssertionError("tokenizer metadata hash mismatch")
    vocab_actual = int(info["vocab_size"])
    if not 258 <= vocab_actual <= MODEL_VOCAB_SIZE:
        raise ValueError("TOKENIZER_CONTRACT_FAIL: actual vocabulary outside frozen range")

    normalizer = info.get("normalizer") or {}
    pre_tokenizer = info.get("pre_tokenizer") or {}
    decoder = info.get("decoder") or {}
    if info.get("model") != "BPE":
        raise ValueError("TOKENIZER_CONTRACT_FAIL: model is not BPE")
    if normalizer.get("type") != "NFC":
        raise ValueError("TOKENIZER_CONTRACT_FAIL: normalizer is not NFC")
    if pre_tokenizer.get("type") != "ByteLevel":
        raise ValueError("TOKENIZER_CONTRACT_FAIL: pre-tokenizer is not ByteLevel")
    if decoder.get("type") != "ByteLevel":
        raise ValueError("TOKENIZER_CONTRACT_FAIL: decoder is not ByteLevel")
    if tuple(info.get("special_tokens") or ()) != SPECIAL_TOKENS:
        raise ValueError("TOKENIZER_CONTRACT_FAIL: special token list changed")
    special_ids = {token: tokenizer.token_to_id(token) for token in SPECIAL_TOKENS}
    if any(value is None for value in special_ids.values()):
        raise ValueError("TOKENIZER_CONTRACT_FAIL: missing frozen special token")

    frozen = {
        **info,
        "requested_vocab_size": REQUESTED_TOKENIZER_VOCAB_SIZE,
        "model_vocab_size": MODEL_VOCAB_SIZE,
        "max_context": MAX_CONTEXT,
        "special_token_ids": special_ids,
        "path": str(tokenizer_path),
    }
    events.append("TOKENIZER_METADATA_VALIDATED")
    return tokenizer, frozen


def _token_ids_sha256(token_ids: list[int]) -> str:
    payload = b"".join(struct.pack("<I", int(token_id)) for token_id in token_ids)
    return _sha256_bytes(payload)


def encode_split(
    split: str,
    rows: list[dict[str, Any]],
    tokenizer: Any,
    output_path: Path,
) -> dict[str, Any]:
    expected_count = int(SOURCE_SPLITS[split]["surface_records"])
    if len(rows) != expected_count:
        raise ValueError(f"{split} row count mismatch before encoding")
    if {str(row.get("split")) for row in rows} != {split}:
        raise ValueError(f"{split} rows contain another split")

    rows = sorted(rows, key=lambda row: (int(row["scene_id"]), str(row["renderer_family"])))
    lengths: list[int] = []
    maximum_id = -1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            text = row.get("input_text")
            if not isinstance(text, str) or not text:
                raise ValueError(f"{split} contains empty input_text")
            token_ids = tokenizer.encode(text).ids
            if not token_ids:
                raise ValueError(f"{split} produced an empty encoded sequence")
            if min(token_ids) < 0 or max(token_ids) >= MODEL_VOCAB_SIZE:
                raise ValueError(f"{split} produced token ID outside B0 vocabulary")
            token_count = len(token_ids)
            if token_count > MAX_CONTEXT:
                raise ValueError(
                    f"INPUT_LENGTH_CONTRACT_FAIL: {split} scene={row['scene_id']} "
                    f"renderer={row['renderer_family']} length={token_count}"
                )
            lengths.append(token_count)
            maximum_id = max(maximum_id, max(token_ids))
            manifest_row = {
                "scene_id": str(row["scene_id"]),
                "renderer_family": str(row["renderer_family"]),
                "split": split,
                "input_text_sha256": _sha256_bytes(text.encode("utf-8")),
                "token_ids": token_ids,
                "token_count": token_count,
                "token_ids_sha256_le_u32": _token_ids_sha256(token_ids),
            }
            handle.write(json.dumps(manifest_row, sort_keys=True, separators=(",", ":")) + "\n")

    lengths_sorted = sorted(lengths)
    return {
        "split": split,
        "surface_records": len(rows),
        "manifest_path": str(output_path),
        "manifest_sha256": sha256_file(output_path),
        "manifest_bytes": output_path.stat().st_size,
        "minimum_tokens": min(lengths),
        "maximum_tokens": max(lengths),
        "mean_tokens": sum(lengths) / len(lengths),
        "p95_tokens": lengths_sorted[min(len(lengths_sorted) - 1, int(0.95 * len(lengths_sorted)))],
        "total_tokens": sum(lengths),
        "maximum_token_id": maximum_id,
        "empty_sequences": 0,
        "over_context_sequences": 0,
    }


def run(
    source_root: Path,
    output_root: Path,
    result_path: Path,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite tokenizer output directory: {output_root}")
    if result_path.exists():
        raise FileExistsError(f"refusing to overwrite tokenizer result: {result_path}")

    events: list[str] = ["TOKENIZER_GATE_STARTED"]
    source = verify_source_files(source_root, events)

    train_source_path = source_root / str(SOURCE_SPLITS["TRAIN"]["relative_path"])
    corpus_path = output_root / "train_input_text.txt"
    train_rows, corpus = extract_train_corpus(train_source_path, corpus_path, events)

    tokenizer_path = output_root / "mk1-tokenizer.json"
    tokenizer, tokenizer_info = fit_and_freeze_tokenizer(corpus_path, tokenizer_path, events)

    # Freeze barrier: only now may VALIDATION / PRISTINE input_text be parsed.
    events.append("POST_TOKENIZER_FREEZE_SPLIT_PARSE_STARTED")
    validation_rows = _read_jsonl(
        source_root / str(SOURCE_SPLITS["VALIDATION"]["relative_path"])
    )
    pristine_rows = _read_jsonl(
        source_root / str(SOURCE_SPLITS["PRISTINE_CONFIRMATORY"]["relative_path"])
    )
    events.append("VALIDATION_AND_PRISTINE_OPENED_AFTER_TOKENIZER_FREEZE")

    manifests = {
        "TRAIN": encode_split(
            "TRAIN",
            train_rows,
            tokenizer,
            output_root / "tokenized_train.jsonl",
        ),
        "VALIDATION": encode_split(
            "VALIDATION",
            validation_rows,
            tokenizer,
            output_root / "tokenized_validation.jsonl",
        ),
        "PRISTINE_CONFIRMATORY": encode_split(
            "PRISTINE_CONFIRMATORY",
            pristine_rows,
            tokenizer,
            output_root / "tokenized_pristine_confirmatory.jsonl",
        ),
    }
    events.append("ALL_SPLITS_TOKENIZED_AND_MANIFESTS_FROZEN")

    max_length = max(int(item["maximum_tokens"]) for item in manifests.values())
    max_token_id = max(int(item["maximum_token_id"]) for item in manifests.values())
    if max_length > MAX_CONTEXT:
        raise AssertionError("encoded context gate violated after manifest creation")
    if max_token_id >= MODEL_VOCAB_SIZE:
        raise AssertionError("token ID gate violated after manifest creation")

    result = {
        "schema": "MK1-TOKENIZER-FREEZE-v0.1",
        "status": "TOKENIZER_FREEZE_PASS",
        "source_artifact": {
            "run_id": SOURCE_RUN_ID,
            "artifact_id": SOURCE_ARTIFACT_ID,
            "artifact_zip_sha256": SOURCE_ARTIFACT_DIGEST,
        },
        "source_splits": source,
        "fit_contract": {
            "fit_source": "TRAIN.input_text_only",
            "fit_surface_records": len(train_rows),
            "validation_used_for_fit": False,
            "pristine_confirmatory_used_for_fit": False,
            "requested_vocab_size": REQUESTED_TOKENIZER_VOCAB_SIZE,
        },
        "train_corpus": corpus,
        "tokenizer": tokenizer_info,
        "tokenized_manifests": manifests,
        "global_audit": {
            "maximum_encoded_length": max_length,
            "maximum_token_id": max_token_id,
            "all_sequences_nonempty": True,
            "all_lengths_le_512": max_length <= MAX_CONTEXT,
            "all_token_ids_lt_16384": max_token_id < MODEL_VOCAB_SIZE,
            "scientific_model_seed_instantiated": False,
            "model_forward_executed": False,
            "optimizer_constructed": False,
            "training_executed": False,
        },
        "event_sequence": events,
    }
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output-root", default="mk1_tokenizer_freeze_v0_1")
    parser.add_argument("--result", default="TOKENIZER_FREEZE_RESULT.json")
    args = parser.parse_args()
    result = run(Path(args.source_root), Path(args.output_root), Path(args.result))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
