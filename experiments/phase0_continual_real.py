"""Phase-0-only untreated continual-learning feasibility experiment.

This script does not implement replay, memory, EWC, regularization treatments,
or any Phase-1 architecture. It reuses the frozen P0.8 model/tokenizer/data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from phase0_real_language_common import (
    CHECKPOINT_DIR,
    DATA_DIR,
    RESULTS_DIR,
    common_record,
    evaluate_tokens,
    load_checkpoint,
    load_json,
    load_tokenizer,
    save_checkpoint,
    sha256_bytes,
    sha256_file,
    train_optimizer_step,
    write_json,
)


BASE_COMMIT = "0c0fb52ac5ce214fdaa0e577b499066606cb1b5b"
DATASET_FINGERPRINT = "c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696"
BASELINE_CHECKPOINT = CHECKPOINT_DIR / "baseline0-final.pt"
BASELINE_SHA256 = "795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079"
TOKENIZER_KIND = "mindforge"

CONTEXT = 256
MICRO_BATCH = 1
ACCUMULATION = 2
STEP_TOKENS = CONTEXT * MICRO_BATCH * ACCUMULATION
QUALIFICATION_STEPS = 128
FINAL_STEPS = 384
QUALIFICATION_SEEDS = (404, 505)
FINAL_SEEDS = (101, 202, 303)
EVAL_WINDOWS = 16
LR = 3e-4
WEIGHT_DECAY = 0.1
A_LEARNING_THRESHOLD = 0.05
B_ACQUISITION_THRESHOLD = 0.05

HISTORY_TERMS = (
    "history", "war", "king", "queen", "empire", "city", "country", "state",
    "province", "battle", "dynasty", "president", "politic", "geography", "river", "mountain",
)
TECH_TERMS = (
    "algorithm", "computer", "software", "mathemat", "physics", "chemistry", "biology",
    "engineering", "technology", "network", "data", "programming", "theorem", "equation", "system",
)


def _sha_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _encode(tokenizer: Any, text: str) -> np.ndarray:
    ids = tokenizer.encode(text).ids
    if not ids:
        raise ValueError("domain text produced no tokens")
    values = np.asarray(ids, dtype=np.int32)
    if int(values.min()) < 0 or int(values.max()) >= tokenizer.get_vocab_size():
        raise ValueError("domain produced invalid token IDs")
    return values


def domain_fingerprint(train_text: str, validation_text: str, definition: str) -> str:
    payload = json.dumps(
        {
            "definition": definition,
            "train_sha256": _sha_text(train_text),
            "validation_sha256": _sha_text(validation_text),
        },
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256_bytes(payload)


def _domain_record(
    *,
    name: str,
    definition: str,
    train_text: str,
    validation_text: str,
    tokenizer: Any,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    train_tokens = _encode(tokenizer, train_text)
    validation_tokens = _encode(tokenizer, validation_text)
    if len(validation_tokens) <= CONTEXT + 1:
        raise ValueError(f"validation stream too small for {name}")
    record: dict[str, Any] = {
        "name": name,
        "definition": definition,
        "fingerprint": domain_fingerprint(train_text, validation_text, definition),
        "train_utf8_bytes": len(train_text.encode("utf-8")),
        "validation_utf8_bytes": len(validation_text.encode("utf-8")),
        "train_tokens": int(len(train_tokens)),
        "validation_tokens": int(len(validation_tokens)),
        "train_sha256": _sha_text(train_text),
        "validation_sha256": _sha_text(validation_text),
        "train_array": train_tokens,
        "validation_array": validation_tokens,
    }
    if extra:
        record.update(extra)
    return record


def _read_article_blocks(language: str, split: str) -> list[tuple[dict[str, Any], str]]:
    metadata = [
        json.loads(line)
        for line in (DATA_DIR / f"articles.{language}.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    selected_meta = [item for item in metadata if item["split"] == split]
    text = (DATA_DIR / f"{split}.{language}.txt").read_text(encoding="utf-8").strip()
    blocks = text.split("\n\n") if text else []
    if len(selected_meta) != len(blocks):
        raise RuntimeError(
            f"article/text alignment mismatch for {language}/{split}: {len(selected_meta)} != {len(blocks)}"
        )
    return list(zip(selected_meta, blocks, strict=True))


def _term_count(text: str, terms: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term) for term in terms)


def _candidate_c1(tokenizer: Any) -> dict[str, Any]:
    return {
        "id": "C1",
        "description": "Vietnamese Wikipedia -> English Wikipedia language specialization",
        "A": _domain_record(
            name="C1-A-VI",
            definition="Frozen Vietnamese Wikipedia article-level train/validation split",
            train_text=(DATA_DIR / "train.vi.txt").read_text(encoding="utf-8"),
            validation_text=(DATA_DIR / "validation.vi.txt").read_text(encoding="utf-8"),
            tokenizer=tokenizer,
        ),
        "B": _domain_record(
            name="C1-B-EN",
            definition="Frozen English Wikipedia article-level train/validation split",
            train_text=(DATA_DIR / "train.en.txt").read_text(encoding="utf-8"),
            validation_text=(DATA_DIR / "validation.en.txt").read_text(encoding="utf-8"),
            tokenizer=tokenizer,
        ),
        "integrity": {"source_article_overlap": 0, "same_sentence_overlap": "not applicable; frozen article split"},
    }


def _candidate_c2(tokenizer: Any) -> dict[str, Any]:
    selected: dict[str, dict[str, list[tuple[dict[str, Any], str]]]] = {
        "train": {"A": [], "B": []},
        "validation": {"A": [], "B": []},
    }
    for split in ("train", "validation"):
        for meta, text in _read_article_blocks("en", split):
            history_count = _term_count(text, HISTORY_TERMS)
            tech_count = _term_count(text, TECH_TERMS)
            if history_count >= 4 and tech_count <= 1:
                selected[split]["A"].append((meta, text))
            if tech_count >= 4 and history_count <= 3:
                selected[split]["B"].append((meta, text))

    all_a_ids = {item[0]["id"] for split in selected.values() for item in split["A"]}
    all_b_ids = {item[0]["id"] for split in selected.values() for item in split["B"]}
    overlap = all_a_ids & all_b_ids
    if overlap:
        raise RuntimeError(f"C2 A/B article selectors overlap: {len(overlap)}")

    def joined(split: str, domain: str) -> str:
        return "\n\n".join(text for _, text in selected[split][domain])

    a_train, a_val = joined("train", "A"), joined("validation", "A")
    b_train, b_val = joined("train", "B"), joined("validation", "B")
    return {
        "id": "C2",
        "description": "English history/geography-heavy -> science/technology-heavy Wikipedia specialization",
        "A": _domain_record(
            name="C2-A-HISTORY",
            definition="English Wikipedia: history/geography term count >=4 and technical term count <=1",
            train_text=a_train,
            validation_text=a_val,
            tokenizer=tokenizer,
            extra={
                "train_articles": len(selected["train"]["A"]),
                "validation_articles": len(selected["validation"]["A"]),
            },
        ),
        "B": _domain_record(
            name="C2-B-TECH",
            definition="English Wikipedia: technical term count >=4 and history/geography term count <=3",
            train_text=b_train,
            validation_text=b_val,
            tokenizer=tokenizer,
            extra={
                "train_articles": len(selected["train"]["B"]),
                "validation_articles": len(selected["validation"]["B"]),
            },
        ),
        "integrity": {
            "A_B_article_overlap": len(overlap),
            "train_validation_source_split": "frozen article-level SHA-256 split",
        },
    }


CONFLICT_TRAIN_TEMPLATES = (
    "Trong bảng phân loại thử nghiệm, thực thể {entity} thuộc nhóm {label}. Nhãn quy ước của {entity} là {label}. Khi đối chiếu hồ sơ, {entity} vẫn được ghi là {label}. Kết luận phân loại: {entity} thuộc nhóm {label}.",
    "Bộ dữ liệu quy ước {entity} ở nhóm {label}. Phiếu thứ hai cũng ghi {entity} là {label}. Mục kiểm tra nhắc lại rằng {entity} thuộc nhóm {label}. Nhãn cuối của {entity}: {label}.",
    "Theo danh mục của thí nghiệm, {entity} được xếp vào nhóm {label}. Hồ sơ của {entity} dùng nhãn {label}. Bản đối chiếu xác nhận {entity} thuộc {label}. Vì vậy mã phân loại của {entity} là {label}.",
    "Quy ước nội bộ ghi {entity} thuộc nhóm {label}. Bảng tra cứu gắn {entity} với nhãn {label}. Dòng kiểm chứng cho {entity} tiếp tục là {label}. Kết quả cuối: {entity} ở nhóm {label}.",
)
CONFLICT_VALIDATION_TEMPLATES = (
    "Khi kiểm tra {entity}, nhãn đúng theo quy ước là {label}. Bản ghi đánh giá cũng xếp {entity} vào nhóm {label}. Kết luận: {entity} thuộc {label}.",
    "Hồ sơ đánh giá hỏi nhóm của {entity}. Theo quy ước, câu trả lời là {label}. Phiếu xác nhận ghi {entity} thuộc nhóm {label}.",
)


def conflict_label(entity: str, domain: str) -> str:
    parity = hashlib.sha256(entity.encode("utf-8")).digest()[0] & 1
    a_label = "lam" if parity == 0 else "đỏ"
    if domain == "A":
        return a_label
    if domain == "B":
        return "đỏ" if a_label == "lam" else "lam"
    raise ValueError(domain)


def build_conflict_text(domain: str, *, split: str) -> tuple[str, list[str]]:
    if split not in {"train", "validation"}:
        raise ValueError(split)
    templates = CONFLICT_TRAIN_TEMPLATES if split == "train" else CONFLICT_VALIDATION_TEMPLATES
    sentences: list[str] = []
    for index in range(128):
        entity = f"Mục-{index:03d}"
        label = conflict_label(entity, domain)
        for template in templates:
            sentences.append(template.format(entity=entity, label=label))
    return "\n\n".join(sentences), sentences


def _candidate_c3(tokenizer: Any) -> dict[str, Any]:
    a_train, a_train_sentences = build_conflict_text("A", split="train")
    a_val, a_val_sentences = build_conflict_text("A", split="validation")
    b_train, b_train_sentences = build_conflict_text("B", split="train")
    b_val, b_val_sentences = build_conflict_text("B", split="validation")
    train_val_overlap = (set(a_train_sentences) | set(b_train_sentences)) & (
        set(a_val_sentences) | set(b_val_sentences)
    )
    if train_val_overlap:
        raise RuntimeError("C3 has exact train/validation sentence leakage")
    return {
        "id": "C3",
        "description": "Balanced contradictory entity-label mappings embedded in Vietnamese natural-language sentences",
        "A": _domain_record(
            name="C3-A-CONFLICT",
            definition="128 entities with SHA-256-balanced experimental lam/red labels; A assignment",
            train_text=a_train,
            validation_text=a_val,
            tokenizer=tokenizer,
            extra={"train_sentences": len(a_train_sentences), "validation_sentences": len(a_val_sentences)},
        ),
        "B": _domain_record(
            name="C3-B-CONFLICT",
            definition="Same 128 entities and opposite experimental labels; B assignment",
            train_text=b_train,
            validation_text=b_val,
            tokenizer=tokenizer,
            extra={"train_sentences": len(b_train_sentences), "validation_sentences": len(b_val_sentences)},
        ),
        "integrity": {
            "exact_train_validation_sentence_overlap": len(train_val_overlap),
            "entities": 128,
            "balanced_opposite_mapping": True,
            "factual_world_claim": False,
        },
    }


def build_candidates(tokenizer: Any) -> list[dict[str, Any]]:
    return [_candidate_c1(tokenizer), _candidate_c2(tokenizer), _candidate_c3(tokenizer)]


def _strip_arrays(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_arrays(item) for key, item in value.items() if key not in {"train_array", "validation_array"}}
    if isinstance(value, list):
        return [_strip_arrays(item) for item in value]
    return value


def meaningful_forgetting_threshold(a_after_a: float) -> float:
    return max(0.10, 0.05 * a_after_a)


def compute_seed_metrics(
    *,
    a_initial: float,
    a_after_a: float,
    a_after_a2: float,
    a_after_b: float,
    b_initial: float,
    b_before_b: float,
    b_after_b: float,
) -> dict[str, float | bool]:
    a_learning = a_initial - a_after_a
    a_learning_fraction = a_learning / a_initial
    b_acquisition = b_before_b - b_after_b
    b_acquisition_fraction = b_acquisition / b_before_b
    forgetting = a_after_b - a_after_a
    relative_forgetting = forgetting / a_after_a
    control_drift = a_after_a2 - a_after_a
    net_interference = a_after_b - a_after_a2
    delta_a = meaningful_forgetting_threshold(a_after_a)
    return {
        "A_learning": a_learning,
        "A_learning_fraction": a_learning_fraction,
        "B_acquisition": b_acquisition,
        "B_acquisition_fraction": b_acquisition_fraction,
        "forgetting": forgetting,
        "relative_forgetting": relative_forgetting,
        "control_drift": control_drift,
        "net_interference": net_interference,
        "delta_A": delta_a,
        "A_learned": a_learning_fraction >= A_LEARNING_THRESHOLD,
        "B_learned": b_acquisition_fraction >= B_ACQUISITION_THRESHOLD,
        "meaningful_forgetting": forgetting >= delta_a,
    }


def aggregate_values(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("cannot aggregate empty values")
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stddev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def aggregate_seed_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    fields = ("A_learning", "B_acquisition", "forgetting", "net_interference")
    return {
        field: aggregate_values([float(item["derived"][field]) for item in results])
        for field in fields
    }


def final_gate(results: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    if len(results) != 3:
        raise ValueError("final gate requires exactly three seeds")
    all_finite = all(item["finite"] for item in results)
    all_a = all(bool(item["derived"]["A_learned"]) for item in results)
    all_b = all(bool(item["derived"]["B_learned"]) for item in results)
    forgetting = [float(item["derived"]["forgetting"]) for item in results]
    deltas = [float(item["derived"]["delta_A"]) for item in results]
    net = [float(item["derived"]["net_interference"]) for item in results]
    seeds_meeting = sum(bool(item["derived"]["meaningful_forgetting"]) for item in results)
    mean_forgetting_gate = statistics.mean(forgetting) >= statistics.mean(deltas)
    mean_net_positive = statistics.mean(net) > 0.0
    passed = all_finite and all_a and all_b and mean_forgetting_gate and seeds_meeting >= 2 and mean_net_positive
    return (
        "PASS" if passed else "REVISE",
        {
            "all_finite": all_finite,
            "all_A_learned": all_a,
            "all_B_learned": all_b,
            "mean_forgetting": statistics.mean(forgetting),
            "mean_delta_A": statistics.mean(deltas),
            "mean_forgetting_gate": mean_forgetting_gate,
            "seeds_meeting_forgetting_threshold": seeds_meeting,
            "mean_net_interference": statistics.mean(net),
            "mean_net_interference_positive": mean_net_positive,
        },
    )


def qualification_gate(results: list[dict[str, Any]]) -> dict[str, Any]:
    if len(results) != 2:
        raise ValueError("qualification gate requires two dedicated seeds")
    learnable = all(
        item["independent_A_learning_fraction"] >= A_LEARNING_THRESHOLD
        and item["independent_B_learning_fraction"] >= B_ACQUISITION_THRESHOLD
        and item["finite"]
        for item in results
    )
    positive_net_both = all(item["derived"]["net_interference"] > 0 for item in results)
    meaningful_count = sum(bool(item["derived"]["meaningful_forgetting"]) for item in results)
    mean_forgetting = statistics.mean(float(item["derived"]["forgetting"]) for item in results)
    usable_interference = positive_net_both and meaningful_count >= 1 and mean_forgetting > 0
    return {
        "learnable": learnable,
        "positive_net_interference_both_seeds": positive_net_both,
        "meaningful_forgetting_seed_count": meaningful_count,
        "mean_forgetting": mean_forgetting,
        "usable_interference": usable_interference,
        "qualified": learnable and usable_interference,
    }


def control_protocol(stage_steps: int) -> dict[str, Any]:
    return {
        "A2_steps": stage_steps,
        "B_steps": stage_steps,
        "equal_second_stage_token_budget": True,
        "optimizer_state": "continue exact post-A optimizer state",
        "lr_schedule": "restart same frozen stage-local schedule",
    }


def _verify_starting_state() -> tuple[Any, dict[str, Any]]:
    manifest = load_json(DATA_DIR / "manifest.json")
    if manifest["corpus_fingerprint"] != DATASET_FINGERPRINT:
        raise RuntimeError("local corpus fingerprint differs from frozen P0.8 corpus")
    if not BASELINE_CHECKPOINT.exists():
        raise FileNotFoundError("missing ignored P0.8 final checkpoint; reconstruct P0.8 before P0.9")
    if sha256_file(BASELINE_CHECKPOINT) != BASELINE_SHA256:
        raise RuntimeError("P0.8 final checkpoint hash mismatch")
    baseline_record = load_json(RESULTS_DIR / "phase0_baseline0.json")
    if baseline_record["final_checkpoint"]["sha256"] != BASELINE_SHA256:
        raise RuntimeError("committed P0.8 evidence does not match required checkpoint")
    tokenizer = load_tokenizer(TOKENIZER_KIND)
    return tokenizer, manifest


def _load_branch() -> tuple[Any, Any, dict[str, Any], str, torch.dtype]:
    if not hasattr(torch, "xpu") or not torch.xpu.is_available():
        raise RuntimeError("P0.9 frozen protocol requires Intel XPU; CPU fallback is not evidence")
    device = "xpu"
    dtype = torch.bfloat16
    model, optimizer, payload = load_checkpoint(BASELINE_CHECKPOINT, device=device, dtype=dtype)
    return model, optimizer, payload, device, dtype


def _eval(model: Any, domain: dict[str, Any], tokenizer: Any, device: str) -> dict[str, Any]:
    return evaluate_tokens(
        model,
        domain["validation_array"],
        tokenizer,
        context=CONTEXT,
        device=device,
        max_windows=EVAL_WINDOWS,
    )


def _train_stage(
    model: Any,
    optimizer: Any,
    train_tokens: np.ndarray,
    *,
    seed: int,
    steps: int,
    device: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    finite = True
    last_loss = float("nan")
    for step in range(steps):
        last_loss = train_optimizer_step(
            model,
            optimizer,
            train_tokens,
            context=CONTEXT,
            micro_batch=MICRO_BATCH,
            accumulation=ACCUMULATION,
            seed=seed,
            step=step,
            device=device,
            lr=LR,
            total_steps=steps,
        )
        if not math.isfinite(last_loss):
            finite = False
            break
    return {
        "steps_completed": step + 1 if steps else 0,
        "training_tokens": (step + 1 if steps else 0) * STEP_TOKENS,
        "last_train_loss": last_loss,
        "finite": finite,
        "wall_clock_seconds": time.perf_counter() - started,
    }


def _save_after_a(model: Any, optimizer: Any, *, candidate_id: str, seed: int, payload: dict[str, Any]) -> Path:
    path = CHECKPOINT_DIR / "phase0_continual_tmp" / f"{candidate_id}-seed{seed}-afterA.pt"
    save_checkpoint(
        path,
        model,
        optimizer,
        step=0,
        config=model.config,
        metadata={
            "purpose": "P0.9 temporary post-A branch point",
            "candidate": candidate_id,
            "seed": seed,
            "starting_checkpoint_sha256": BASELINE_SHA256,
            "dataset_fingerprint": DATASET_FINGERPRINT,
            "source_checkpoint_step": int(payload["step"]),
        },
    )
    return path


def _run_qualification_seed(candidate: dict[str, Any], tokenizer: Any, seed: int) -> dict[str, Any]:
    # Independent A learnability branch.
    model_a, opt_a, payload, device, dtype = _load_branch()
    a_initial = _eval(model_a, candidate["A"], tokenizer, device)
    b_initial = _eval(model_a, candidate["B"], tokenizer, device)
    a_stage = _train_stage(
        model_a, opt_a, candidate["A"]["train_array"], seed=seed, steps=QUALIFICATION_STEPS, device=device
    )
    a_after_a = _eval(model_a, candidate["A"], tokenizer, device)
    b_before_b = _eval(model_a, candidate["B"], tokenizer, device)
    after_a_path = _save_after_a(model_a, opt_a, candidate_id=candidate["id"], seed=seed, payload=payload)

    # Independent B learnability branch from the exact same Baseline-0.
    model_b_only, opt_b_only, _, device_b, _ = _load_branch()
    b_only_stage = _train_stage(
        model_b_only,
        opt_b_only,
        candidate["B"]["train_array"],
        seed=seed,
        steps=QUALIFICATION_STEPS,
        device=device_b,
    )
    b_after_b_only = _eval(model_b_only, candidate["B"], tokenizer, device_b)

    # Equal-budget A→A control from exact post-A model+optimizer state.
    model_a2, opt_a2, _, = load_checkpoint(after_a_path, device=device, dtype=dtype)
    a2_stage = _train_stage(
        model_a2, opt_a2, candidate["A"]["train_array"], seed=seed, steps=QUALIFICATION_STEPS, device=device
    )
    a_after_a2 = _eval(model_a2, candidate["A"], tokenizer, device)

    # Untreated A→B branch from the exact same post-A model+optimizer state.
    model_ab, opt_ab, _ = load_checkpoint(after_a_path, device=device, dtype=dtype)
    b_stage = _train_stage(
        model_ab, opt_ab, candidate["B"]["train_array"], seed=seed, steps=QUALIFICATION_STEPS, device=device
    )
    a_after_b = _eval(model_ab, candidate["A"], tokenizer, device)
    b_after_b = _eval(model_ab, candidate["B"], tokenizer, device)
    after_a_path.unlink(missing_ok=True)

    derived = compute_seed_metrics(
        a_initial=a_initial["bits_per_byte"],
        a_after_a=a_after_a["bits_per_byte"],
        a_after_a2=a_after_a2["bits_per_byte"],
        a_after_b=a_after_b["bits_per_byte"],
        b_initial=b_initial["bits_per_byte"],
        b_before_b=b_before_b["bits_per_byte"],
        b_after_b=b_after_b["bits_per_byte"],
    )
    finite = all(
        metric["status"] == "PASS"
        for metric in (a_initial, b_initial, a_after_a, b_before_b, b_after_b_only, a_after_a2, a_after_b, b_after_b)
    ) and all(stage["finite"] for stage in (a_stage, b_only_stage, a2_stage, b_stage))
    return {
        "seed": seed,
        "device": device,
        "dtype": str(dtype),
        "finite": finite,
        "A_initial": a_initial,
        "A_after_A": a_after_a,
        "A_after_A2": a_after_a2,
        "A_after_B": a_after_b,
        "B_initial": b_initial,
        "B_before_B": b_before_b,
        "B_after_B": b_after_b,
        "B_after_B_independent": b_after_b_only,
        "independent_A_learning_fraction": (
            a_initial["bits_per_byte"] - a_after_a["bits_per_byte"]
        ) / a_initial["bits_per_byte"],
        "independent_B_learning_fraction": (
            b_initial["bits_per_byte"] - b_after_b_only["bits_per_byte"]
        ) / b_initial["bits_per_byte"],
        "derived": derived,
        "stages": {"A": a_stage, "B_independent": b_only_stage, "A2_control": a2_stage, "B_sequential": b_stage},
    }


def run_qualification() -> dict[str, Any]:
    tokenizer, manifest = _verify_starting_state()
    candidates = build_candidates(tokenizer)
    candidate_results: list[dict[str, Any]] = []
    for candidate in candidates:
        print(f"qualify {candidate['id']}")
        seed_results = [_run_qualification_seed(candidate, tokenizer, seed) for seed in QUALIFICATION_SEEDS]
        gate = qualification_gate(seed_results)
        candidate_results.append(
            {
                "candidate": _strip_arrays(candidate),
                "seeds": seed_results,
                "gate": gate,
            }
        )
        print(json.dumps({"candidate": candidate["id"], "gate": gate}, indent=2))

    selected = next(
        (item["candidate"]["id"] for item in candidate_results if item["gate"]["qualified"]),
        None,
    )
    record = common_record(DATASET_FINGERPRINT)
    record.update(
        {
            "base_commit": BASE_COMMIT,
            "status": "PASS" if selected else "STOP",
            "purpose": "bounded pre-registered P0.9 domain qualification; not final evidence",
            "starting_checkpoint": {"sha256": BASELINE_SHA256, "bytes": BASELINE_CHECKPOINT.stat().st_size},
            "tokenizer": TOKENIZER_KIND,
            "dataset_fingerprint": manifest["corpus_fingerprint"],
            "qualification_config": {
                "candidate_order": ["C1", "C2", "C3"],
                "seeds": list(QUALIFICATION_SEEDS),
                "steps_per_stage": QUALIFICATION_STEPS,
                "training_tokens_per_stage": QUALIFICATION_STEPS * STEP_TOKENS,
                "context": CONTEXT,
                "micro_batch": MICRO_BATCH,
                "gradient_accumulation": ACCUMULATION,
                "effective_batch_tokens": STEP_TOKENS,
                "optimizer": "AdamW",
                "learning_rate": LR,
                "weight_decay": WEIGHT_DECAY,
                "lr_schedule": "stage-local 5% linear warmup then cosine to 10% peak",
                "optimizer_state_policy": "continue baseline state; continue exact post-A state into A2/B",
                "evaluation_windows": EVAL_WINDOWS,
                "A_learning_threshold": A_LEARNING_THRESHOLD,
                "B_learning_threshold": B_ACQUISITION_THRESHOLD,
                "selection_rule": "first C1->C2->C3 with both-seed learnability and usable interference",
            },
            "candidates": candidate_results,
            "selected_candidate": selected,
        }
    )
    write_json(RESULTS_DIR / "phase0_continual_qualification.json", record)
    print(json.dumps({"status": record["status"], "selected_candidate": selected}, indent=2))
    return record


def _run_final_seed(candidate: dict[str, Any], tokenizer: Any, seed: int) -> dict[str, Any]:
    model_a, opt_a, payload, device, dtype = _load_branch()
    a_initial = _eval(model_a, candidate["A"], tokenizer, device)
    b_initial = _eval(model_a, candidate["B"], tokenizer, device)
    a_stage = _train_stage(model_a, opt_a, candidate["A"]["train_array"], seed=seed, steps=FINAL_STEPS, device=device)
    a_after_a = _eval(model_a, candidate["A"], tokenizer, device)
    b_before_b = _eval(model_a, candidate["B"], tokenizer, device)
    after_a_path = _save_after_a(model_a, opt_a, candidate_id=f"final-{candidate['id']}", seed=seed, payload=payload)

    model_a2, opt_a2, _ = load_checkpoint(after_a_path, device=device, dtype=dtype)
    a2_stage = _train_stage(model_a2, opt_a2, candidate["A"]["train_array"], seed=seed, steps=FINAL_STEPS, device=device)
    a_after_a2 = _eval(model_a2, candidate["A"], tokenizer, device)

    model_ab, opt_ab, _ = load_checkpoint(after_a_path, device=device, dtype=dtype)
    b_stage = _train_stage(model_ab, opt_ab, candidate["B"]["train_array"], seed=seed, steps=FINAL_STEPS, device=device)
    a_after_b = _eval(model_ab, candidate["A"], tokenizer, device)
    b_after_b = _eval(model_ab, candidate["B"], tokenizer, device)
    after_a_path.unlink(missing_ok=True)

    derived = compute_seed_metrics(
        a_initial=a_initial["bits_per_byte"],
        a_after_a=a_after_a["bits_per_byte"],
        a_after_a2=a_after_a2["bits_per_byte"],
        a_after_b=a_after_b["bits_per_byte"],
        b_initial=b_initial["bits_per_byte"],
        b_before_b=b_before_b["bits_per_byte"],
        b_after_b=b_after_b["bits_per_byte"],
    )
    finite = all(
        metric["status"] == "PASS"
        for metric in (a_initial, b_initial, a_after_a, b_before_b, a_after_a2, a_after_b, b_after_b)
    ) and all(stage["finite"] for stage in (a_stage, a2_stage, b_stage))
    return {
        "seed": seed,
        "device": device,
        "dtype": str(dtype),
        "finite": finite,
        "A_initial": a_initial,
        "A_after_A": a_after_a,
        "A_after_A2": a_after_a2,
        "A_after_B": a_after_b,
        "B_initial": b_initial,
        "B_before_B": b_before_b,
        "B_after_B": b_after_b,
        "derived": derived,
        "stages": {"A": a_stage, "A2_control": a2_stage, "B_sequential": b_stage},
        "result": "PASS" if finite and derived["A_learned"] and derived["B_learned"] else "REVISE",
    }


def run_final() -> dict[str, Any]:
    qualification = load_json(RESULTS_DIR / "phase0_continual_qualification.json")
    selected_id = qualification.get("selected_candidate")
    if qualification.get("status") != "PASS" or selected_id not in {"C1", "C2", "C3"}:
        raise RuntimeError("qualification did not select a final candidate; final run is not authorized")
    tokenizer, manifest = _verify_starting_state()
    candidates = {candidate["id"]: candidate for candidate in build_candidates(tokenizer)}
    candidate = candidates[selected_id]

    # Final run is authorized only after the protocol file has an explicit freeze marker.
    protocol_text = (Path(__file__).resolve().parents[1] / "docs" / "phases" / "phase-0-continual-protocol.md").read_text(encoding="utf-8")
    freeze_marker = f"FINAL_SELECTED_CANDIDATE={selected_id}"
    if freeze_marker not in protocol_text:
        raise RuntimeError(f"final protocol is not frozen; missing marker {freeze_marker}")
    for domain_key in ("A", "B"):
        marker = f"FINAL_{domain_key}_FINGERPRINT={candidate[domain_key]['fingerprint']}"
        if marker not in protocol_text:
            raise RuntimeError(f"final protocol fingerprint mismatch/missing: {marker}")

    results = []
    for seed in FINAL_SEEDS:
        print(f"final {selected_id} seed {seed}")
        result = _run_final_seed(candidate, tokenizer, seed)
        results.append(result)
        print(
            json.dumps(
                {
                    "seed": seed,
                    "A_learning_fraction": result["derived"]["A_learning_fraction"],
                    "B_acquisition_fraction": result["derived"]["B_acquisition_fraction"],
                    "forgetting": result["derived"]["forgetting"],
                    "delta_A": result["derived"]["delta_A"],
                    "net_interference": result["derived"]["net_interference"],
                },
                indent=2,
            )
        )

    status, gate = final_gate(results)
    aggregates = aggregate_seed_results(results)
    record = common_record(DATASET_FINGERPRINT)
    record.update(
        {
            "base_commit": BASE_COMMIT,
            "status": status,
            "research_question": "Can MindForge produce a reproducible controlled catastrophic-forgetting signal on real language modeling tasks?",
            "treatment": "NONE — untreated sequential training only",
            "starting_checkpoint": {"sha256": BASELINE_SHA256, "bytes": BASELINE_CHECKPOINT.stat().st_size},
            "model_config": asdict(load_checkpoint(BASELINE_CHECKPOINT, device="cpu", dtype=torch.float32)[0].config),
            "parameter_count": load_json(RESULTS_DIR / "phase0_baseline0.json")["parameter_count"],
            "tokenizer": TOKENIZER_KIND,
            "dataset_fingerprint": manifest["corpus_fingerprint"],
            "domain": _strip_arrays(candidate),
            "protocol": {
                "A_training_steps": FINAL_STEPS,
                "B_training_steps": FINAL_STEPS,
                "A2_control_steps": FINAL_STEPS,
                "training_tokens_per_stage": FINAL_STEPS * STEP_TOKENS,
                "context": CONTEXT,
                "micro_batch": MICRO_BATCH,
                "gradient_accumulation": ACCUMULATION,
                "effective_batch_tokens": STEP_TOKENS,
                "optimizer": "AdamW",
                "learning_rate": LR,
                "weight_decay": WEIGHT_DECAY,
                "lr_schedule": "stage-local 5% linear warmup then cosine to 10% peak",
                "optimizer_state_policy": "continue baseline state; continue exact post-A state into A2/B",
                "seeds": list(FINAL_SEEDS),
                "evaluation_windows": EVAL_WINDOWS,
                "control": control_protocol(FINAL_STEPS),
            },
            "thresholds": {
                "A_learning_fraction": A_LEARNING_THRESHOLD,
                "B_acquisition_fraction": B_ACQUISITION_THRESHOLD,
                "meaningful_forgetting": "max(0.10 BPB, 0.05 * A_after_A BPB) per seed",
                "seed_criterion": "at least 2/3 meaningful forgetting",
                "mean_forgetting": "mean forgetting >= mean per-seed delta_A",
                "net_interference": "mean > 0",
            },
            "seeds": results,
            "aggregate": aggregates,
            "gate": gate,
        }
    )
    write_json(RESULTS_DIR / "phase0_continual_real.json", record)
    print(json.dumps({"status": status, "gate": gate, "aggregate": aggregates}, indent=2))
    return record


def write_stop_record() -> dict[str, Any]:
    qualification_path = RESULTS_DIR / "phase0_continual_qualification.json"
    qualification = load_json(qualification_path)
    if qualification.get("status") != "STOP" or qualification.get("selected_candidate") is not None:
        raise RuntimeError("stop record is only valid after bounded qualification selects no candidate")
    baseline = load_json(RESULTS_DIR / "phase0_baseline0.json")
    record = common_record(DATASET_FINGERPRINT)
    record.update(
        {
            "base_commit": BASE_COMMIT,
            "status": "STOP",
            "research_question": "Can MindForge produce a reproducible controlled catastrophic-forgetting signal on real language modeling tasks?",
            "stop_reason": "None of the three pre-registered bounded candidate families satisfied the frozen qualification rule; final seeds were therefore not authorized.",
            "treatment": "NONE — untreated continual training only",
            "starting_checkpoint": {
                "sha256": BASELINE_SHA256,
                "bytes": BASELINE_CHECKPOINT.stat().st_size,
            },
            "model_config": baseline["model_config"],
            "parameter_count": baseline["parameter_count"],
            "tokenizer": TOKENIZER_KIND,
            "dataset_fingerprint": DATASET_FINGERPRINT,
            "domain_definitions": [item["candidate"] for item in qualification["candidates"]],
            "optimizer": {
                "name": "AdamW",
                "learning_rate": LR,
                "weight_decay": WEIGHT_DECAY,
                "lr_schedule": "stage-local 5% linear warmup then cosine to 10% peak",
                "optimizer_state_policy": "continue baseline state; continue exact post-A state into A2/B",
            },
            "qualification": {
                "seeds": list(QUALIFICATION_SEEDS),
                "training_tokens_per_stage": QUALIFICATION_STEPS * STEP_TOKENS,
                "candidate_gates": [
                    {"candidate": item["candidate"]["id"], "gate": item["gate"]}
                    for item in qualification["candidates"]
                ],
                "evidence_sha256": sha256_file(qualification_path),
            },
            "final_protocol": {
                "executed": False,
                "seeds": list(FINAL_SEEDS),
                "training_tokens_per_stage": FINAL_STEPS * STEP_TOKENS,
                "reason_not_executed": "No candidate qualified under the pre-registered bounded search; running final seeds would violate the protocol.",
            },
            "thresholds": {
                "A_learning_fraction": A_LEARNING_THRESHOLD,
                "B_acquisition_fraction": B_ACQUISITION_THRESHOLD,
                "meaningful_forgetting": "max(0.10 BPB, 0.05 * A_after_A BPB) per seed",
                "qualification_selection": "first C1->C2->C3 satisfying frozen learnability + usable-interference gate",
                "final_seed_criterion": "at least 2/3 meaningful forgetting; not reached",
                "final_net_interference": "mean > 0; not reached",
            },
            "metrics": {
                "qualification_candidate_gates": [item["gate"] for item in qualification["candidates"]],
                "final_seed_metrics": [],
            },
        }
    )
    write_json(RESULTS_DIR / "phase0_continual_real.json", record)
    print(json.dumps({"status": "STOP", "final_protocol_executed": False}, indent=2))
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("qualification", "final", "stop-record"))
    args = parser.parse_args()
    if args.command == "qualification":
        result = run_qualification()
        return 0 if result["status"] == "PASS" else 2
    if args.command == "stop-record":
        write_stop_record()
        return 0
    result = run_final()
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
