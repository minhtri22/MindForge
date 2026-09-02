"""Phase 0 real-language evidence runner.

Commands:
    prepare    download/extract corpus, train MindForge BPE, cache token arrays
    tokenizer  compare existing vs MindForge tokenizer, including smoke-LM BPB
    dataset    run frozen 1M-vs-10M dataset viability sweep
    baseline-init  create the exact frozen step-0 Baseline-0 checkpoint
    baseline   train/evaluate the frozen Baseline-0
    all        execute the above in order

This file is intentionally experimental evidence code and must not be promoted
to the Phase 1 kernel before the Phase 0 gate is reviewed.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import math
import os
import re
import shutil
import time
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path
from typing import Any

import mwparserfromhell
import numpy as np
import requests
import torch
from tokenizers import Tokenizer, decoders, normalizers, pre_tokenizers
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer

from phase0_real_language_common import (
    BASE_COMMIT,
    CHECKPOINT_DIR,
    DATA_DIR,
    MF_TOKENIZER_PATH,
    QWEN_REPO,
    QWEN_REVISION,
    RESULTS_DIR,
    LMConfig,
    build_model,
    build_optimizer,
    common_record,
    current_memory,
    encode_text_file,
    evaluate_text_samples,
    evaluate_tokens,
    generation_sanity,
    git_commit,
    load_checkpoint,
    load_json,
    load_token_array,
    load_tokenizer,
    model_parameter_count,
    peak_memory,
    reset_peak_memory,
    save_checkpoint,
    save_token_array,
    sha256_bytes,
    sha256_file,
    staged_pool,
    summarize_throughput,
    sync,
    tokenizer_metadata,
    train_optimizer_step,
    write_json,
)


SOURCES = {
    "vi": {
        "url": "https://dumps.wikimedia.org/viwiki/20260801/viwiki-20260801-pages-articles-multistream1.xml-p1p832082.bz2",
        "filename": "viwiki-20260801-pages-articles-multistream1.xml-p1p832082.bz2",
        "license": "CC BY-SA (Wikipedia text; see Wikimedia Terms of Use/content licensing)",
    },
    "en": {
        "url": "https://dumps.wikimedia.org/enwiki/20260801/enwiki-20260801-pages-articles-multistream1.xml-p1p41242.bz2",
        "filename": "enwiki-20260801-pages-articles-multistream1.xml-p1p41242.bz2",
        "license": "CC BY-SA (Wikipedia text; see Wikimedia Terms of Use/content licensing)",
    },
}

TRAIN_TARGET_BYTES_PER_LANGUAGE = 32 * 1024 * 1024
VALIDATION_TARGET_BYTES_PER_LANGUAGE = 4 * 1024 * 1024
SPLIT_THRESHOLD = int(0.05 * 65536)
MIXED_PROBE_BYTES = 1024 * 1024
SMOKE_STEPS = 256
SMOKE_CONTEXT = 256
SMOKE_MICRO_BATCH = 2
SMOKE_SEED = 4242
DATASET_SWEEP_TRAIN_TOKENS = 1_000_000
DATASET_SWEEP_CONTEXT = 256
DATASET_SWEEP_MICRO_BATCH = 2
DATASET_SWEEP_SEED = 5151
BASELINE_STEPS = 1000
BASELINE_CONTEXT = 512
BASELINE_MICRO_BATCH = 1
BASELINE_ACCUMULATION = 2
BASELINE_SEED = 2026
BASE_LR = 3e-4
BASELINE_INITIAL_CHECKPOINT = CHECKPOINT_DIR / "baseline0-initial.pt"
BASELINE_INITIAL_EVAL = RESULTS_DIR / "phase0_real_language_initial_eval.json"

FROZEN_PROMPTS = [
    "Việt Nam là một quốc gia",
    "The purpose of scientific research is",
    "Hà Nội nằm ở",
    "Năm 2026, tỷ lệ 12.5% và mã A-42",
    "Trong machine learning, mô hình thường",
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    text = "".join(character for character in text if character in "\n\t" or ord(character) >= 32)
    lines: list[str] = []
    for line in text.split("\n"):
        line = re.sub(r"[\t ]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def split_for_article(language: str, article_id: str) -> str:
    digest = hashlib.sha256(f"{language}:{article_id}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:2], "big")
    return "validation" if value < SPLIT_THRESHOLD else "train"


def clean_wikitext(text: str) -> str:
    try:
        stripped = mwparserfromhell.parse(text).strip_code(normalize=True, collapse=True)
    except Exception:
        stripped = text
    return normalize_text(stripped)


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        print(f"reuse {path.name} ({path.stat().st_size / 1024 / 1024:.1f} MiB)")
        return
    temporary = path.with_suffix(path.suffix + ".part")
    if temporary.exists():
        temporary.unlink()
    headers = {"User-Agent": "MindForge-Phase0/0.1 (local research validation)"}
    with requests.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
        response.raise_for_status()
        expected = int(response.headers.get("content-length", "0"))
        written = 0
        last_report = 0
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=4 * 1024 * 1024):
                if not chunk:
                    continue
                handle.write(chunk)
                written += len(chunk)
                if written - last_report >= 64 * 1024 * 1024:
                    print(f"download {path.name}: {written / 1024 / 1024:.0f} MiB")
                    last_report = written
        if expected and written != expected:
            raise IOError(f"download size mismatch for {path.name}: {written} != {expected}")
    temporary.replace(path)


def _direct_child(element: ET.Element, local_name: str) -> ET.Element | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == local_name:
            return child
    return None


def _descendant(element: ET.Element, local_name: str) -> ET.Element | None:
    for child in element.iter():
        if child.tag.rsplit("}", 1)[-1] == local_name:
            return child
    return None


def extract_language(path: Path, language: str) -> dict[str, Any]:
    out_train = DATA_DIR / f"train.{language}.txt"
    out_validation = DATA_DIR / f"validation.{language}.txt"
    metadata_path = DATA_DIR / f"articles.{language}.jsonl"
    if out_train.exists() and out_validation.exists() and metadata_path.exists():
        return {
            "language": language,
            "train_bytes": out_train.stat().st_size,
            "validation_bytes": out_validation.stat().st_size,
            "train_sha256": sha256_file(out_train),
            "validation_sha256": sha256_file(out_validation),
            "article_manifest_sha256": sha256_file(metadata_path),
            "reused": True,
        }

    train_bytes = 0
    validation_bytes = 0
    train_articles = 0
    validation_articles = 0
    seen_train_ids: set[str] = set()
    seen_validation_ids: set[str] = set()
    with (
        bz2.open(path, "rb") as compressed,
        out_train.open("wb") as train_handle,
        out_validation.open("wb") as validation_handle,
        metadata_path.open("w", encoding="utf-8", newline="\n") as metadata_handle,
    ):
        for _, page in ET.iterparse(compressed, events=("end",)):
            if page.tag.rsplit("}", 1)[-1] != "page":
                continue
            ns = _direct_child(page, "ns")
            article_id = _direct_child(page, "id")
            title = _direct_child(page, "title")
            text_node = _descendant(page, "text")
            if ns is None or ns.text != "0" or article_id is None or not article_id.text or text_node is None:
                page.clear()
                continue
            cleaned = clean_wikitext(text_node.text or "")
            if len(cleaned) < 200:
                page.clear()
                continue
            payload = (cleaned + "\n\n").encode("utf-8")
            split = split_for_article(language, article_id.text)
            if split == "train" and train_bytes < TRAIN_TARGET_BYTES_PER_LANGUAGE:
                train_handle.write(payload)
                train_bytes += len(payload)
                train_articles += 1
                seen_train_ids.add(article_id.text)
                metadata_handle.write(
                    json.dumps(
                        {"language": language, "id": article_id.text, "title": title.text if title is not None else "", "split": split},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            elif split == "validation" and validation_bytes < VALIDATION_TARGET_BYTES_PER_LANGUAGE:
                validation_handle.write(payload)
                validation_bytes += len(payload)
                validation_articles += 1
                seen_validation_ids.add(article_id.text)
                metadata_handle.write(
                    json.dumps(
                        {"language": language, "id": article_id.text, "title": title.text if title is not None else "", "split": split},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            page.clear()
            if (
                train_bytes >= TRAIN_TARGET_BYTES_PER_LANGUAGE
                and validation_bytes >= VALIDATION_TARGET_BYTES_PER_LANGUAGE
            ):
                break

    if train_bytes < TRAIN_TARGET_BYTES_PER_LANGUAGE or validation_bytes < VALIDATION_TARGET_BYTES_PER_LANGUAGE:
        raise RuntimeError(
            f"insufficient {language} corpus: train={train_bytes} validation={validation_bytes}"
        )
    overlap = seen_train_ids.intersection(seen_validation_ids)
    if overlap:
        raise RuntimeError(f"article leakage detected for {language}: {len(overlap)} IDs")
    return {
        "language": language,
        "train_bytes": train_bytes,
        "validation_bytes": validation_bytes,
        "train_articles": train_articles,
        "validation_articles": validation_articles,
        "article_id_overlap": 0,
        "train_sha256": sha256_file(out_train),
        "validation_sha256": sha256_file(out_validation),
        "article_manifest_sha256": sha256_file(metadata_path),
        "reused": False,
    }


def combine_equal_byte_budget(split: str) -> dict[str, Any]:
    vi_path = DATA_DIR / f"{split}.vi.txt"
    en_path = DATA_DIR / f"{split}.en.txt"
    out_path = DATA_DIR / f"{split}.mixed.txt"
    vi = vi_path.read_bytes()
    en = en_path.read_bytes()
    byte_budget = min(len(vi), len(en))

    def utf8_safe_prefix(data: bytes, target: int) -> bytes:
        candidate = data[:target]
        while candidate:
            try:
                candidate.decode("utf-8")
                return candidate
            except UnicodeDecodeError as exc:
                candidate = candidate[: exc.start]
        return b""

    vi_part = utf8_safe_prefix(vi, byte_budget)
    en_part = utf8_safe_prefix(en, byte_budget)
    effective = min(len(vi_part), len(en_part))
    vi_part = utf8_safe_prefix(vi_part, effective)
    en_part = utf8_safe_prefix(en_part, effective)
    mixed = vi_part + b"\n\n" + en_part
    out_path.write_bytes(mixed)
    return {
        "path": out_path.name,
        "vi_bytes": len(vi_part),
        "en_bytes": len(en_part),
        "language_byte_ratio_vi": len(vi_part) / (len(vi_part) + len(en_part)),
        "sha256": sha256_bytes(mixed),
        "total_bytes": len(mixed),
    }


def train_mindforge_tokenizer() -> dict[str, Any]:
    tokenizer = Tokenizer(BPE(unk_token="<|unk|>"))
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = BpeTrainer(
        vocab_size=16_384,
        min_frequency=2,
        special_tokens=["<|endoftext|>", "<|unk|>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=True,
    )
    tokenizer.train(
        [str(DATA_DIR / "train.vi.txt"), str(DATA_DIR / "train.en.txt")], trainer=trainer
    )
    tokenizer.save(str(MF_TOKENIZER_PATH))
    return tokenizer_metadata(tokenizer, name="MindForge byte-level BPE")


def cache_token_arrays() -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for kind in ("existing", "mindforge"):
        tokenizer = load_tokenizer(kind)
        summary[kind] = {"vocab_size": tokenizer.get_vocab_size()}
        for split in ("train", "validation"):
            tokens = encode_text_file(tokenizer, DATA_DIR / f"{split}.mixed.txt")
            path = DATA_DIR / f"{kind}.{split}.npy"
            save_token_array(path, tokens)
            summary[kind][f"{split}_tokens"] = int(len(tokens))
            summary[kind][f"{split}_sha256"] = sha256_file(path)
    return summary


def prepare() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    source_results: dict[str, Any] = {}
    extract_results: dict[str, Any] = {}
    for language, source in SOURCES.items():
        dump_path = DATA_DIR / source["filename"]
        download_file(source["url"], dump_path)
        source_results[language] = {
            **source,
            "download_bytes": dump_path.stat().st_size,
            "sha256": sha256_file(dump_path),
        }
        extract_results[language] = extract_language(dump_path, language)

    mixed_train = combine_equal_byte_budget("train")
    mixed_validation = combine_equal_byte_budget("validation")
    mf_metadata = train_mindforge_tokenizer()
    token_arrays = cache_token_arrays()
    corpus_fingerprint = sha256_bytes(
        (
            mixed_train["sha256"]
            + mixed_validation["sha256"]
            + source_results["vi"]["sha256"]
            + source_results["en"]["sha256"]
        ).encode("ascii")
    )
    manifest = {
        "timestamp": common_record()["timestamp"],
        "base_commit": BASE_COMMIT,
        "git_commit": git_commit(),
        "corpus_fingerprint": corpus_fingerprint,
        "sources": source_results,
        "extraction": extract_results,
        "mixed_train": mixed_train,
        "mixed_validation": mixed_validation,
        "mindforge_tokenizer": mf_metadata,
        "qwen_revision": QWEN_REVISION,
        "token_arrays": token_arrays,
        "split": {
            "method": "SHA-256 first 16 bits of <language>:<article-id>",
            "validation_fraction_target": 0.05,
            "article_id_overlap": 0,
        },
    }
    write_json(DATA_DIR / "manifest.json", manifest)
    print(json.dumps({"corpus_fingerprint": corpus_fingerprint, "token_arrays": token_arrays}, indent=2))
    return manifest


def _sample_text(language: str, byte_limit: int = MIXED_PROBE_BYTES) -> str:
    data = (DATA_DIR / f"validation.{language}.txt").read_bytes()[:byte_limit]
    while data:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            data = data[: exc.start]
    return ""


def tokenizer_text_metrics(tokenizer: Tokenizer, text: str) -> dict[str, Any]:
    encoding = tokenizer.encode(text)
    ids = encoding.ids
    decoded = tokenizer.decode(ids, skip_special_tokens=False)
    words = re.findall(r"\S+", text)
    utf8_bytes = len(text.encode("utf-8"))
    unk_id = tokenizer.token_to_id("<|unk|>")
    unknown_count = ids.count(unk_id) if unk_id is not None else 0
    return {
        "characters": len(text),
        "utf8_bytes": utf8_bytes,
        "whitespace_words": len(words),
        "tokens": len(ids),
        "tokens_per_character": len(ids) / max(1, len(text)),
        "tokens_per_byte": len(ids) / max(1, utf8_bytes),
        "tokens_per_word": len(ids) / max(1, len(words)),
        "unique_token_ids": len(set(ids)),
        "vocab_utilization": len(set(ids)) / tokenizer.get_vocab_size(),
        "unknown_count": unknown_count,
        "roundtrip_exact": decoded == text,
        "valid_token_ids": bool(ids) and min(ids) >= 0 and max(ids) < tokenizer.get_vocab_size(),
    }


def tokenizer_probe_metrics(tokenizer: Tokenizer) -> dict[str, Any]:
    probes = {
        "vietnamese_diacritics": "Tiếng Việt có dấu: Trường Đại học Bách khoa, Nguyễn Huệ, phở bò.",
        "multisyllable": "trí tuệ nhân tạo và chuyển đổi số trong doanh nghiệp",
        "punctuation": "Xin chào! (Thử nghiệm) — đúng không? #AI; 100%.",
        "numbers": "2026-09-02 12.5% 1,024,000 3.14159 A-42",
        "code_switch": "Hôm nay deploy model mới, latency giảm nhưng validation loss tăng nhẹ.",
    }
    results: dict[str, Any] = {}
    for name, text in probes.items():
        ids = tokenizer.encode(text).ids
        unk_id = tokenizer.token_to_id("<|unk|>")
        results[name] = {
            "tokens": len(ids),
            "unknown_count": ids.count(unk_id) if unk_id is not None else 0,
            "roundtrip_exact": tokenizer.decode(ids, skip_special_tokens=False) == text,
            "valid_token_ids": bool(ids) and min(ids) >= 0 and max(ids) < tokenizer.get_vocab_size(),
        }
    return results


def _fair_smoke_eval_samples(count: int = 12, byte_span: int = 512) -> list[str]:
    """Return frozen exact-text snippets shared by both tokenizer smoke models."""
    data = (DATA_DIR / "validation.mixed.txt").read_bytes()
    if len(data) < byte_span:
        raise ValueError("validation corpus is too small for fair smoke samples")
    starts = np.linspace(0, len(data) - byte_span, num=count, dtype=np.int64)
    samples: list[str] = []
    for raw_start in starts:
        start = int(raw_start)
        chunk = data[start : start + byte_span]
        # Drop only incomplete UTF-8 code points at the two boundaries. The
        # resulting decoded text is then identical input for both tokenizers.
        text = chunk.decode("utf-8", errors="ignore")
        if not text:
            raise ValueError("empty fair-eval text sample")
        samples.append(text)
    return samples


def _train_smoke(kind: str, fair_eval_samples: list[str]) -> dict[str, Any]:
    tokenizer = load_tokenizer(kind)
    train_tokens = load_token_array(DATA_DIR / f"{kind}.train.npy")
    config = LMConfig(
        vocab_size=tokenizer.get_vocab_size(),
        d_model=192,
        n_heads=6,
        n_layers=4,
        max_context=SMOKE_CONTEXT,
    )
    device = "xpu" if torch.xpu.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    model = build_model(config, seed=SMOKE_SEED, device=device, dtype=dtype)
    optimizer = build_optimizer(model, lr=BASE_LR)
    initial_eval = evaluate_text_samples(model, tokenizer, fair_eval_samples, device=device)
    reset_peak_memory(device)
    throughput: list[float] = []
    losses: list[dict[str, Any]] = []
    start_wall = time.perf_counter()
    for step in range(SMOKE_STEPS):
        sync(device)
        started = time.perf_counter()
        loss = train_optimizer_step(
            model,
            optimizer,
            train_tokens,
            context=SMOKE_CONTEXT,
            micro_batch=SMOKE_MICRO_BATCH,
            accumulation=1,
            seed=SMOKE_SEED,
            step=step,
            device=device,
            lr=BASE_LR,
            total_steps=SMOKE_STEPS,
        )
        sync(device)
        elapsed = time.perf_counter() - started
        if step >= 10:
            throughput.append((SMOKE_CONTEXT * SMOKE_MICRO_BATCH) / elapsed)
        if step in {0, 63, 127, 191, 255}:
            losses.append({"step": step + 1, "train_loss": loss})
    wall = time.perf_counter() - start_wall
    final_eval = evaluate_text_samples(model, tokenizer, fair_eval_samples, device=device)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = CHECKPOINT_DIR / f"tokenizer-smoke-{kind}.pt"
    checkpoint = save_checkpoint(
        checkpoint_path,
        model,
        optimizer,
        step=SMOKE_STEPS,
        config=config,
        metadata={"tokenizer_kind": kind, "purpose": "P0.3 smoke comparison"},
    )
    return {
        "tokenizer": kind,
        "config": asdict(config),
        "parameter_count": model_parameter_count(model),
        "seed": SMOKE_SEED,
        "device": device,
        "dtype": str(dtype),
        "steps": SMOKE_STEPS,
        "training_tokens": SMOKE_STEPS * SMOKE_CONTEXT * SMOKE_MICRO_BATCH,
        "fair_eval": {
            "sample_count": len(fair_eval_samples),
            "sample_sha256": [sha256_bytes(text.encode("utf-8")) for text in fair_eval_samples],
            "total_utf8_bytes": sum(len(text.encode("utf-8")) for text in fair_eval_samples),
            "method": "same exact held-out UTF-8 text samples; BOS predicts every sample token",
        },
        "initial_eval": initial_eval,
        "final_eval": final_eval,
        "curve": losses,
        "wall_clock_seconds": wall,
        "throughput_tokens_per_second": summarize_throughput(throughput),
        "peak_xpu_memory_bytes": peak_memory(device),
        "checkpoint": checkpoint,
    }


def run_tokenizer_comparison() -> dict[str, Any]:
    manifest = load_json(DATA_DIR / "manifest.json")
    samples = {
        "vi": _sample_text("vi"),
        "en": _sample_text("en"),
    }
    half = MIXED_PROBE_BYTES // 2
    mixed_text = (
        samples["vi"].encode("utf-8")[:half].decode("utf-8", errors="ignore")
        + "\n\n"
        + samples["en"].encode("utf-8")[:half].decode("utf-8", errors="ignore")
    )
    text_metrics: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    probes: dict[str, Any] = {}
    for kind in ("existing", "mindforge"):
        tokenizer = load_tokenizer(kind)
        metadata[kind] = tokenizer_metadata(
            tokenizer,
            name=(QWEN_REPO if kind == "existing" else "MindForge byte-level BPE"),
            revision=(QWEN_REVISION if kind == "existing" else sha256_file(MF_TOKENIZER_PATH)),
        )
        text_metrics[kind] = {
            "vi": tokenizer_text_metrics(tokenizer, samples["vi"]),
            "en": tokenizer_text_metrics(tokenizer, samples["en"]),
            "mixed": tokenizer_text_metrics(tokenizer, mixed_text),
        }
        probes[kind] = tokenizer_probe_metrics(tokenizer)

    mf_mixed_tokens = text_metrics["mindforge"]["mixed"]["tokens"]
    for kind in ("existing", "mindforge"):
        text_metrics[kind]["mixed"]["sequence_expansion_ratio_vs_mindforge"] = (
            text_metrics[kind]["mixed"]["tokens"] / mf_mixed_tokens
        )

    fair_eval_samples = _fair_smoke_eval_samples()
    smoke = {kind: _train_smoke(kind, fair_eval_samples) for kind in ("existing", "mindforge")}
    existing_bpb = smoke["existing"]["final_eval"]["bits_per_byte"]
    mf_bpb = smoke["mindforge"]["final_eval"]["bits_per_byte"]
    existing_tpb = text_metrics["existing"]["mixed"]["tokens_per_byte"]
    mf_tpb = text_metrics["mindforge"]["mixed"]["tokens_per_byte"]
    safe = {
        kind: (
            all(item["roundtrip_exact"] and item["valid_token_ids"] and item["unknown_count"] == 0 for item in probes[kind].values())
            and text_metrics[kind]["vi"]["roundtrip_exact"]
            and text_metrics[kind]["en"]["roundtrip_exact"]
        )
        for kind in ("existing", "mindforge")
    }
    decision = "REVISE"
    rationale = "frozen tokenizer decision rule selected neither candidate"
    if safe["existing"] and existing_bpb <= 0.95 * mf_bpb and existing_tpb <= 1.10 * mf_tpb:
        decision = "USE EXISTING"
        rationale = "existing tokenizer met the frozen >=5% BPB advantage and compression rule"
    elif safe["mindforge"] and mf_bpb <= 1.05 * existing_bpb and mf_tpb <= 1.25 * existing_tpb:
        decision = "TRAIN MINDFORGE TOKENIZER"
        rationale = "MindForge tokenizer met frozen BPB/compression tolerances with much smaller project-local vocabulary"

    record = common_record(manifest["corpus_fingerprint"])
    record.update(
        {
            "status": "PASS" if decision != "REVISE" else "REVISE",
            "tokenizer_metadata": metadata,
            "heldout_metrics": text_metrics,
            "probes": probes,
            "smoke_language_models": smoke,
            "decision": decision,
            "decision_rationale": rationale,
            "decision_inputs": {
                "existing_final_bpb": existing_bpb,
                "mindforge_final_bpb": mf_bpb,
                "existing_mixed_tokens_per_byte": existing_tpb,
                "mindforge_mixed_tokens_per_byte": mf_tpb,
                "safe": safe,
            },
            "license": {
                "existing": "Apache-2.0 (Qwen2.5 model/tokenizer repository)",
                "mindforge": "project-generated tokenizer from CC BY-SA Wikipedia training text",
            },
            "comparison_warning": "perplexity is reported only as within-tokenizer context; cross-tokenizer decision uses BPB, compression, safety and implementation cost",
            "fair_bpb_contract": {
                "sample_count": len(fair_eval_samples),
                "sample_sha256": [sha256_bytes(text.encode("utf-8")) for text in fair_eval_samples],
                "total_utf8_bytes": sum(len(text.encode("utf-8")) for text in fair_eval_samples),
                "same_exact_text_for_both_tokenizers": True,
                "all_text_tokens_scored_via_bos_prefix": True,
            },
        }
    )
    write_json(RESULTS_DIR / "phase0_tokenizer_comparison.json", record)
    print(json.dumps(record["decision_inputs"], indent=2))
    print("decision", decision)
    return record


def selected_tokenizer_kind() -> str:
    result = load_json(RESULTS_DIR / "phase0_tokenizer_comparison.json")
    if result["decision"] == "USE EXISTING":
        return "existing"
    if result["decision"] == "TRAIN MINDFORGE TOKENIZER":
        return "mindforge"
    raise RuntimeError("P0.3 tokenizer decision is REVISE; dataset/baseline cannot proceed")


def _run_dataset_stage(kind: str, pool_size: int) -> dict[str, Any]:
    tokenizer = load_tokenizer(kind)
    full_train = load_token_array(DATA_DIR / f"{kind}.train.npy")
    validation = load_token_array(DATA_DIR / f"{kind}.validation.npy")
    if len(full_train) < pool_size:
        return {"pool_tokens": pool_size, "status": "NOT_AVAILABLE", "available_tokens": int(len(full_train))}
    pool = staged_pool(full_train, pool_size)
    config = LMConfig(
        vocab_size=tokenizer.get_vocab_size(),
        d_model=192,
        n_heads=6,
        n_layers=4,
        max_context=DATASET_SWEEP_CONTEXT,
    )
    device = "xpu" if torch.xpu.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    model = build_model(config, seed=DATASET_SWEEP_SEED, device=device, dtype=dtype)
    optimizer = build_optimizer(model, lr=BASE_LR)
    total_steps = math.ceil(DATASET_SWEEP_TRAIN_TOKENS / (DATASET_SWEEP_CONTEXT * DATASET_SWEEP_MICRO_BATCH))
    eval_steps = sorted(set([0, total_steps // 4, total_steps // 2, 3 * total_steps // 4, total_steps]))
    curve: list[dict[str, Any]] = []
    initial_eval = evaluate_tokens(
        model, validation, tokenizer, context=DATASET_SWEEP_CONTEXT, device=device, max_windows=12
    )
    curve.append({"step": 0, "validation": initial_eval})
    throughput: list[float] = []
    reset_peak_memory(device)
    wall_start = time.perf_counter()
    for step in range(total_steps):
        sync(device)
        started = time.perf_counter()
        train_loss = train_optimizer_step(
            model,
            optimizer,
            pool,
            context=DATASET_SWEEP_CONTEXT,
            micro_batch=DATASET_SWEEP_MICRO_BATCH,
            accumulation=1,
            seed=DATASET_SWEEP_SEED,
            step=step,
            device=device,
            lr=BASE_LR,
            total_steps=total_steps,
        )
        sync(device)
        elapsed = time.perf_counter() - started
        if step >= 10:
            throughput.append(DATASET_SWEEP_CONTEXT * DATASET_SWEEP_MICRO_BATCH / elapsed)
        completed = step + 1
        if completed in eval_steps:
            curve.append(
                {
                    "step": completed,
                    "train_loss": train_loss,
                    "validation": evaluate_tokens(
                        model,
                        validation,
                        tokenizer,
                        context=DATASET_SWEEP_CONTEXT,
                        device=device,
                        max_windows=12,
                    ),
                }
            )
    wall = time.perf_counter() - wall_start
    final_eval = curve[-1]["validation"]
    bpbs = [item["validation"]["bits_per_byte"] for item in curve]
    initial_bpb = initial_eval["bits_per_byte"]
    final_bpb = final_eval["bits_per_byte"]
    best_bpb = min(bpbs)
    improvement = (initial_bpb - final_bpb) / initial_bpb
    reversal = (final_bpb - best_bpb) / best_bpb
    viable = improvement >= 0.05 and reversal <= 0.02
    return {
        "pool_tokens": int(len(pool)),
        "requested_pool_tokens": pool_size,
        "pool_sha256": sha256_bytes(np.asarray(pool, dtype=np.int32).tobytes()),
        "status": "PASS" if viable else "REVISE",
        "viable": viable,
        "config": asdict(config),
        "parameter_count": model_parameter_count(model),
        "seed": DATASET_SWEEP_SEED,
        "training_token_budget": total_steps * DATASET_SWEEP_CONTEXT * DATASET_SWEEP_MICRO_BATCH,
        "steps": total_steps,
        "curve": curve,
        "initial_bpb": initial_bpb,
        "final_bpb": final_bpb,
        "best_bpb": best_bpb,
        "relative_bpb_improvement": improvement,
        "final_vs_best_reversal": reversal,
        "wall_clock_seconds": wall,
        "throughput_tokens_per_second": summarize_throughput(throughput),
        "peak_xpu_memory_bytes": peak_memory(device),
    }


def run_dataset_viability() -> dict[str, Any]:
    manifest = load_json(DATA_DIR / "manifest.json")
    kind = selected_tokenizer_kind()
    stages = {"1M": _run_dataset_stage(kind, 1_000_000), "10M": _run_dataset_stage(kind, 10_000_000)}
    decision = "REVISE"
    recommended = None
    reason = "10M stage did not establish viability; 50M required"
    one = stages["1M"]
    ten = stages["10M"]
    if ten.get("status") == "NOT_AVAILABLE":
        decision = "REVISE"
        reason = "prepared corpus did not yield 10M tokens for selected tokenizer"
    elif one.get("viable") and ten.get("viable"):
        relative_ten_gain = (one["final_bpb"] - ten["final_bpb"]) / one["final_bpb"]
        if relative_ten_gain >= 0.05:
            recommended = "10M tokens"
            reason = "both viable; 10M improved final BPB by >=5% at equal training budget"
        else:
            recommended = "1M tokens"
            reason = "both viable; 10M improved final BPB by <5%, so frozen smallest-corpus rule selects 1M"
        decision = "PASS"
    elif (not one.get("viable")) and ten.get("viable"):
        decision = "PASS"
        recommended = "10M tokens"
        reason = "1M failed frozen viability criteria while 10M passed"
    else:
        decision = "REVISE"
    record = common_record(manifest["corpus_fingerprint"])
    record.update(
        {
            "status": decision,
            "tokenizer": kind,
            "stages": stages,
            "recommended_development_corpus": recommended,
            "decision_reason": reason,
            "50M": "NOT_RUN unless 10M fails frozen gate",
            "100M": "NOT_RUN unless 50M justifies escalation",
            "split": manifest["split"],
            "mixed_train": manifest["mixed_train"],
            "mixed_validation": manifest["mixed_validation"],
            "sources": manifest["sources"],
        }
    )
    write_json(RESULTS_DIR / "phase0_dataset_viability.json", record)
    print(json.dumps({"status": decision, "recommended": recommended, "reason": reason}, indent=2))
    return record


def _baseline_config(vocab_size: int) -> LMConfig:
    # With the frozen 16k MindForge BPE this lands close to 10M params.
    # If another tokenizer was selected, actual count is reported rather than hidden.
    return LMConfig(vocab_size=vocab_size, d_model=320, n_heads=8, n_layers=4, max_context=BASELINE_CONTEXT)


def run_baseline_init() -> dict[str, Any]:
    manifest = load_json(DATA_DIR / "manifest.json")
    dataset_result = load_json(RESULTS_DIR / "phase0_dataset_viability.json")
    if dataset_result["status"] != "PASS":
        raise RuntimeError("P0.4 is not PASS; Baseline-0 initialization is not authorized")
    kind = selected_tokenizer_kind()
    tokenizer = load_tokenizer(kind)
    config = _baseline_config(tokenizer.get_vocab_size())
    device = "xpu" if torch.xpu.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    model = build_model(config, seed=BASELINE_SEED, device=device, dtype=dtype)
    optimizer = build_optimizer(model, lr=BASE_LR)
    checkpoint = save_checkpoint(
        BASELINE_INITIAL_CHECKPOINT,
        model,
        optimizer,
        step=0,
        config=config,
        metadata={
            "tokenizer_kind": kind,
            "dataset_fingerprint": manifest["corpus_fingerprint"],
            "seed": BASELINE_SEED,
            "purpose": "frozen Baseline-0 initial state; independently evaluate before training",
        },
    )
    result = {
        "checkpoint": checkpoint,
        "checkpoint_path": str(BASELINE_INITIAL_CHECKPOINT),
        "tokenizer": kind,
        "model_config": asdict(config),
        "parameter_count": model_parameter_count(model),
        "dataset_fingerprint": manifest["corpus_fingerprint"],
        "seed": BASELINE_SEED,
        "device": device,
        "dtype": str(dtype),
    }
    print(json.dumps(result, indent=2))
    return result


def _load_verified_baseline_initial_state(
    *,
    manifest: dict[str, Any],
    kind: str,
    config: LMConfig,
    device: str,
    dtype: torch.dtype,
) -> tuple[Any, Any, dict[str, Any], dict[str, Any]]:
    if not BASELINE_INITIAL_CHECKPOINT.exists():
        raise FileNotFoundError(
            "missing frozen step-0 Baseline-0 checkpoint; run the baseline-init command first"
        )
    if not BASELINE_INITIAL_EVAL.exists():
        raise FileNotFoundError(
            "missing independent step-0 evaluation evidence; evaluate baseline0-initial.pt before training"
        )
    initial_eval_record = load_json(BASELINE_INITIAL_EVAL)
    if initial_eval_record.get("status") != "PASS":
        raise RuntimeError("independent step-0 evaluation did not PASS")
    checkpoint_sha = sha256_file(BASELINE_INITIAL_CHECKPOINT)
    if initial_eval_record.get("checkpoint", {}).get("sha256") != checkpoint_sha:
        raise RuntimeError("step-0 checkpoint hash does not match independent evaluation evidence")
    if int(initial_eval_record.get("checkpoint", {}).get("step", -1)) != 0:
        raise RuntimeError("independent initial evaluation does not reference a step-0 checkpoint")
    if initial_eval_record.get("tokenizer") != kind:
        raise RuntimeError("initial evaluation tokenizer does not match frozen tokenizer decision")
    if initial_eval_record.get("dataset_fingerprint") != manifest["corpus_fingerprint"]:
        raise RuntimeError("initial evaluation dataset fingerprint does not match frozen corpus")
    if initial_eval_record.get("model_config") != asdict(config):
        raise RuntimeError("initial evaluation model config does not match frozen Baseline-0 config")

    model, optimizer, payload = load_checkpoint(BASELINE_INITIAL_CHECKPOINT, device=device, dtype=dtype)
    if int(payload["step"]) != 0:
        raise RuntimeError("frozen initial checkpoint is not step 0")
    if payload["config"] != asdict(config):
        raise RuntimeError("frozen initial checkpoint config changed")
    metadata = payload.get("metadata", {})
    if metadata.get("tokenizer_kind") != kind:
        raise RuntimeError("frozen initial checkpoint tokenizer metadata changed")
    if metadata.get("dataset_fingerprint") != manifest["corpus_fingerprint"]:
        raise RuntimeError("frozen initial checkpoint dataset fingerprint changed")
    if int(metadata.get("seed", -1)) != BASELINE_SEED:
        raise RuntimeError("frozen initial checkpoint seed changed")
    return model, optimizer, payload, initial_eval_record


def run_baseline() -> dict[str, Any]:
    manifest = load_json(DATA_DIR / "manifest.json")
    dataset_result = load_json(RESULTS_DIR / "phase0_dataset_viability.json")
    if dataset_result["status"] != "PASS":
        raise RuntimeError("P0.4 is not PASS; Baseline-0 is not authorized by the frozen slice protocol")
    kind = selected_tokenizer_kind()
    tokenizer = load_tokenizer(kind)
    train_tokens = load_token_array(DATA_DIR / f"{kind}.train.npy")
    validation_tokens = load_token_array(DATA_DIR / f"{kind}.validation.npy")
    recommended = dataset_result["recommended_development_corpus"]
    pool_size = 1_000_000 if recommended.startswith("1M") else 10_000_000
    train_pool = staged_pool(train_tokens, pool_size)
    config = _baseline_config(tokenizer.get_vocab_size())
    device = "xpu" if torch.xpu.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "xpu" else torch.float32
    model, optimizer, initial_payload, initial_eval_record = _load_verified_baseline_initial_state(
        manifest=manifest,
        kind=kind,
        config=config,
        device=device,
        dtype=dtype,
    )
    initial_eval = initial_eval_record["metrics"]
    curve: list[dict[str, Any]] = [{"step": 0, "tokens_seen": 0, "validation": initial_eval}]
    throughput: list[float] = []
    periodic: list[dict[str, Any]] = []
    initial_allocated_memory = current_memory(device)
    reset_peak_memory(device)
    wall_start = time.perf_counter()
    midpoint_checkpoint: dict[str, Any] | None = None
    resume_loaded = False
    last_loss = float("nan")
    for step in range(BASELINE_STEPS):
        sync(device)
        started = time.perf_counter()
        last_loss = train_optimizer_step(
            model,
            optimizer,
            train_pool,
            context=BASELINE_CONTEXT,
            micro_batch=BASELINE_MICRO_BATCH,
            accumulation=BASELINE_ACCUMULATION,
            seed=BASELINE_SEED,
            step=step,
            device=device,
            lr=BASE_LR,
            total_steps=BASELINE_STEPS,
        )
        sync(device)
        elapsed = time.perf_counter() - started
        step_tokens = BASELINE_CONTEXT * BASELINE_MICRO_BATCH * BASELINE_ACCUMULATION
        tps = step_tokens / elapsed
        if step >= 10:
            throughput.append(tps)
        completed = step + 1
        periodic.append(
            {
                "step": completed,
                "elapsed_seconds": time.perf_counter() - wall_start,
                "tokens_per_second": tps,
                "train_loss": last_loss,
                "xpu_peak_memory_bytes": peak_memory(device),
            }
        )
        if completed % 100 == 0 or completed == BASELINE_STEPS:
            validation = evaluate_tokens(
                model,
                validation_tokens,
                tokenizer,
                context=BASELINE_CONTEXT,
                device=device,
                max_windows=24,
            )
            curve.append(
                {
                    "step": completed,
                    "tokens_seen": completed * step_tokens,
                    "train_loss": last_loss,
                    "validation": validation,
                }
            )
        if completed == 500:
            checkpoint_path = CHECKPOINT_DIR / "baseline0-step500.pt"
            midpoint_checkpoint = save_checkpoint(
                checkpoint_path,
                model,
                optimizer,
                step=completed,
                config=config,
                metadata={
                    "tokenizer_kind": kind,
                    "dataset_fingerprint": manifest["corpus_fingerprint"],
                    "seed": BASELINE_SEED,
                },
            )
            model, optimizer, payload = load_checkpoint(checkpoint_path, device=device, dtype=dtype)
            resume_loaded = int(payload["step"]) == completed

    wall = time.perf_counter() - wall_start
    final_allocated_memory = current_memory(device)
    final_eval = curve[-1]["validation"]
    final_checkpoint_path = CHECKPOINT_DIR / "baseline0-final.pt"
    final_checkpoint = save_checkpoint(
        final_checkpoint_path,
        model,
        optimizer,
        step=BASELINE_STEPS,
        config=config,
        metadata={
            "tokenizer_kind": kind,
            "dataset_fingerprint": manifest["corpus_fingerprint"],
            "seed": BASELINE_SEED,
        },
    )
    generations = generation_sanity(model, tokenizer, FROZEN_PROMPTS, device=device)
    relative_bpb_improvement = (
        initial_eval["bits_per_byte"] - final_eval["bits_per_byte"]
    ) / initial_eval["bits_per_byte"]
    stable = (
        math.isfinite(last_loss)
        and all(item["validation"]["finite"] for item in curve)
        and final_eval["status"] == "PASS"
    )
    baseline_pass = (
        stable
        and relative_bpb_improvement >= 0.05
        and generations["status"] == "PASS"
        and resume_loaded
    )
    baseline_record = common_record(manifest["corpus_fingerprint"])
    first_sustained = [item["tokens_per_second"] for item in periodic[10:110]]
    last_sustained = [item["tokens_per_second"] for item in periodic[-100:]]
    first_sustained_summary = summarize_throughput(first_sustained)
    last_sustained_summary = summarize_throughput(last_sustained)
    first_last_median_ratio = (
        last_sustained_summary["median"] / first_sustained_summary["median"]
        if first_sustained_summary["median"]
        else None
    )
    baseline_record.update(
        {
            "status": "PASS" if baseline_pass else "REVISE",
            "tokenizer": kind,
            "tokenizer_metadata": tokenizer_metadata(
                tokenizer,
                name=(QWEN_REPO if kind == "existing" else "MindForge byte-level BPE"),
                revision=(QWEN_REVISION if kind == "existing" else sha256_file(MF_TOKENIZER_PATH)),
            ),
            "dataset_pool": recommended,
            "model_config": asdict(config),
            "parameter_count": model_parameter_count(model),
            "training": {
                "steps": BASELINE_STEPS,
                "training_tokens": BASELINE_STEPS * BASELINE_CONTEXT * BASELINE_MICRO_BATCH * BASELINE_ACCUMULATION,
                "context": BASELINE_CONTEXT,
                "micro_batch": BASELINE_MICRO_BATCH,
                "gradient_accumulation": BASELINE_ACCUMULATION,
                "effective_batch_contexts": BASELINE_MICRO_BATCH * BASELINE_ACCUMULATION,
                "optimizer": "AdamW",
                "learning_rate": BASE_LR,
                "weight_decay": 0.1,
                "schedule": "5% linear warmup then cosine decay to 10% peak",
                "gradient_clip": 1.0,
                "seed": BASELINE_SEED,
                "backend": device,
                "dtype": str(dtype),
            },
            "initial_eval": initial_eval,
            "initial_checkpoint": {
                "sha256": sha256_file(BASELINE_INITIAL_CHECKPOINT),
                "bytes": BASELINE_INITIAL_CHECKPOINT.stat().st_size,
                "step": int(initial_payload["step"]),
            },
            "initial_independent_eval": {
                "path": BASELINE_INITIAL_EVAL.name,
                "sha256": sha256_file(BASELINE_INITIAL_EVAL),
                "status": initial_eval_record["status"],
            },
            "final_eval": final_eval,
            "relative_bpb_improvement": relative_bpb_improvement,
            "curve": curve,
            "periodic_stability_samples": periodic,
            "wall_clock_seconds": wall,
            "throughput_tokens_per_second": summarize_throughput(throughput),
            "warmup_steps_excluded_from_summary": 10,
            "measured_steps": len(throughput),
            "initial_allocated_memory_bytes": initial_allocated_memory,
            "peak_xpu_memory_bytes": peak_memory(device),
            "final_allocated_memory_bytes": final_allocated_memory,
            "sustained_throughput_check": {
                "first_measured_100_steps": first_sustained_summary,
                "last_100_steps": last_sustained_summary,
                "last_to_first_median_ratio": first_last_median_ratio,
                "note": "descriptive stability evidence; no post-hoc pass threshold",
            },
            "midpoint_checkpoint": midpoint_checkpoint,
            "resume_loaded": resume_loaded,
            "final_checkpoint": final_checkpoint,
            "generation_sanity": generations,
            "xpu_long_run_stability": "PASS" if stable and device == "xpu" else "REVISE",
        }
    )
    write_json(RESULTS_DIR / "phase0_baseline0.json", baseline_record)
    print(
        json.dumps(
            {
                "baseline_status": baseline_record["status"],
                "initial_bpb": initial_eval["bits_per_byte"],
                "final_bpb": final_eval["bits_per_byte"],
                "relative_bpb_improvement": relative_bpb_improvement,
                "median_tokens_per_second": baseline_record["throughput_tokens_per_second"]["median"],
                "peak_xpu_memory_bytes": baseline_record["peak_xpu_memory_bytes"],
            },
            indent=2,
        )
    )
    return baseline_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("prepare", "tokenizer", "dataset", "baseline-init", "baseline", "all"),
        nargs="?",
        default="all",
    )
    args = parser.parse_args()
    if args.command in {"prepare", "all"}:
        prepare()
    if args.command in {"tokenizer", "all"}:
        run_tokenizer_comparison()
    if args.command in {"dataset", "all"}:
        run_dataset_viability()
    if args.command == "baseline-init":
        run_baseline_init()
    if args.command in {"baseline", "all"}:
        run_baseline()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
