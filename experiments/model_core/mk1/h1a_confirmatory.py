"""One-shot MK-1 H1a confirmatory evaluator.

This module evaluates only the five frozen M1-Z best checkpoints on the
frozen PRISTINE_CONFIRMATORY surfaces. It does not implement H1b or H1c.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
import tokenizers

from mindforge.config import ModelConfig
from mindforge.model import create_model
from mindforge.tokenizer import load_tokenizer, sha256_file

from .contracts import M1Z_PARAMETER_COUNT, Z1_LABELS, Z4_FIELDS
from .metrics import canonical_to_python, h1a_representation_summary
from .modeling import M1ZArm, parameter_count
from .recompose import decode_z_logits, recompose_decoded_z

PRISTINE_SHA256 = "5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6"
TOKENIZER_SHA256 = "e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829"
EXPECTED_PRISTINE_SURFACES = 1200
EXPECTED_PRISTINE_SCENES = 600
EXPECTED_PRISTINE_SCENE_IDS = {str(value) for value in range(7_104_000, 7_104_600)}

CHECKPOINTS = {
    71001: {
        "best_step": 5000,
        "best_pt_sha256": "84c5c163877afb74caf9de4c72945b3c801bc6ff7ebdd701f6f03d40d850b699",
        "paired_init_sha256": "c8a7fbf63e0df8a827ff7c9291d4955db9a59b14ad1d28387fffa00e0b7a2ad7",
        "artifact_id": 10635575980,
        "artifact_zip_sha256": "e413ce076530b7e47dfdd3ebaf518d8165f53d9e8a25ac05ea166a65dabf5a0f",
    },
    71002: {
        "best_step": 3500,
        "best_pt_sha256": "0ed0d152f27ea9e3f8219ae3f47c5c205507296ac47181761df03672755bf1e3",
        "paired_init_sha256": "04cd00ce71965649281c618212c120c165d6283519eab2d9f13beb22110f674d",
        "artifact_id": 10638036281,
        "artifact_zip_sha256": "0f9b483a5f8979a92ec330974e56564e292737b5ba4185f081d384f88ba4bf13",
    },
    71003: {
        "best_step": 5000,
        "best_pt_sha256": "def7b229623fbca317f064b3d4af6156323dbfb34497954a28456ec3b29c7d12",
        "paired_init_sha256": "f3ffadfa63e011bf691ac2e0f86a67eb023606d19a875104b77ea40d35577beb",
        "artifact_id": 10641678365,
        "artifact_zip_sha256": "0df985887c5d4c58704317c5885574abee69d8ef63312568896c40954cc6826b",
    },
    71004: {
        "best_step": 4750,
        "best_pt_sha256": "207a1443acb6266a699fe223b492bd2881857c3d2dbda0d21ee8b7e2b6087fd7",
        "paired_init_sha256": "2f1d93bf7119ffb67c939e3c6235054232854d59ab4151e5b95ae6e2828d931d",
        "artifact_id": 10644396601,
        "artifact_zip_sha256": "45d8c286954565cf0276105db87cebe01cbde14d1cb1446678f466f7d67b908a",
    },
    71005: {
        "best_step": 3000,
        "best_pt_sha256": "5f37529a4948948b0e5a362c46f455b87ff65b5fb4d63027d294365f08313282",
        "paired_init_sha256": "e553c8aa984a7b7040e392776f5a35aa6925658dbb932bc5777a0e5f35d326ab",
        "artifact_id": 10647387273,
        "artifact_zip_sha256": "d107361f967f8ace604ba6cc8d53b4d1b6055178ee296b3bbe51f5f5581c06f1",
    },
}

H1A_THRESHOLDS = {
    "z1_micro_precision_min": 0.95,
    "z1_micro_recall_min": 0.95,
    "z1_macro_f1_min": 0.90,
    "z3_scope_relation_accuracy_min": 0.95,
    "z4_pooled_precision_min": 0.95,
    "z4_pooled_recall_min": 0.90,
    "canonical_field_accuracy_min": 0.95,
    "invariance_cluster_consistency_min": 0.95,
    "supported_class_recall_min": 0.80,
    "scalar_mean_nae_max": 0.05,
    "scalar_p95_nae_max": 0.10,
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def verify_pristine(path: Path) -> list[dict[str, Any]]:
    if sha256_file(path) != PRISTINE_SHA256:
        raise ValueError("PRISTINE_CONFIRMATORY source SHA-256 mismatch")
    rows = _read_jsonl(path)
    if len(rows) != EXPECTED_PRISTINE_SURFACES:
        raise ValueError("PRISTINE_CONFIRMATORY surface count mismatch")
    if {str(row["split"]) for row in rows} != {"PRISTINE_CONFIRMATORY"}:
        raise ValueError("confirmatory file contains non-confirmatory row")
    scene_ids = {str(row["scene_id"]) for row in rows}
    if scene_ids != EXPECTED_PRISTINE_SCENE_IDS:
        raise ValueError("PRISTINE_CONFIRMATORY scene namespace mismatch")
    counts = Counter(str(row["scene_id"]) for row in rows)
    if set(counts.values()) != {2}:
        raise ValueError("confirmatory surface multiplicity must be exactly two")
    rows.sort(key=lambda row: (str(row["scene_id"]), str(row["renderer_family"])))
    return rows


def verify_tokenizer(path: Path):
    if sha256_file(path) != TOKENIZER_SHA256:
        raise ValueError("scientific tokenizer SHA-256 mismatch")
    tokenizer = load_tokenizer(path)
    actual_vocab = tokenizer.get_vocab_size()
    if not 258 <= actual_vocab <= ModelConfig().vocab_size:
        raise ValueError("scientific tokenizer vocabulary contract mismatch")
    return tokenizer


def _backbone_state_from_full_state(state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    prefix = "backbone."
    result = {
        key[len(prefix):]: value
        for key, value in state.items()
        if key.startswith(prefix)
    }
    if not result:
        raise ValueError("checkpoint has no backbone state")
    return result


def load_frozen_best_checkpoint(path: Path, seed: int) -> tuple[M1ZArm, dict[str, Any]]:
    expected = CHECKPOINTS[seed]
    if sha256_file(path) != expected["best_pt_sha256"]:
        raise ValueError(f"best.pt SHA-256 mismatch for seed {seed}")
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload.get("schema") != "MK1-TRAIN-CHECKPOINT-v0.1":
        raise ValueError("checkpoint schema mismatch")
    if payload.get("arm") != "m1z" or int(payload.get("seed", -1)) != seed:
        raise ValueError("checkpoint arm/seed mismatch")
    if int(payload.get("step", -1)) != expected["best_step"]:
        raise ValueError("checkpoint step is not frozen best step")
    if int(payload.get("best_step", -1)) != expected["best_step"]:
        raise ValueError("checkpoint best_step metadata mismatch")
    if payload.get("tokenizer_sha256") != TOKENIZER_SHA256:
        raise ValueError("checkpoint tokenizer provenance mismatch")
    if payload.get("paired_init_sha256") != expected["paired_init_sha256"]:
        raise ValueError("checkpoint paired-init provenance mismatch")
    if not math.isfinite(float(payload.get("best_validation_score", float("nan")))):
        raise ValueError("checkpoint best validation score is non-finite")

    state = payload["model_state"]
    backbone = create_model(ModelConfig())
    backbone.load_state_dict(_backbone_state_from_full_state(state), strict=True)
    model = M1ZArm(backbone)
    model.load_state_dict(state, strict=True)
    if parameter_count(model) != M1Z_PARAMETER_COUNT:
        raise ValueError("M1-Z parameter contract mismatch")
    model.to(device=torch.device("cpu"), dtype=torch.float32)
    model.eval()
    return model, {
        "seed": seed,
        "best_step": expected["best_step"],
        "best_pt_sha256": expected["best_pt_sha256"],
        "paired_init_sha256": expected["paired_init_sha256"],
        "artifact_id": expected["artifact_id"],
        "artifact_zip_sha256": expected["artifact_zip_sha256"],
    }


def _encode(tokenizer, text: str) -> torch.Tensor:
    ids = tokenizer.encode(text).ids
    if not ids:
        raise ValueError("confirmatory input encoded to empty sequence")
    if len(ids) > 512:
        raise ValueError("confirmatory input exceeds frozen context")
    if min(ids) < 0 or max(ids) >= ModelConfig().vocab_size:
        raise ValueError("confirmatory token ID outside B0 vocabulary")
    return torch.tensor([ids], dtype=torch.long)


def _decoded_z_to_python(decoded: dict[str, torch.Tensor]) -> dict[str, Any]:
    return {
        "z1": [int(v) for v in decoded["z1"][0].detach().cpu().tolist()],
        "z2_comparator": int(decoded["z2_comparator"][0].detach().cpu()),
        "z2_temporal_precision": int(decoded["z2_temporal_precision"][0].detach().cpu()),
        "z2_scalars": [float(v) for v in decoded["z2_scalars"][0].detach().cpu().tolist()],
        "z3_evidence_scope": int(decoded["z3_evidence_scope"][0].detach().cpu()),
        "z3_asserted_scope": int(decoded["z3_asserted_scope"][0].detach().cpu()),
        "z3_scope_relation": int(decoded["z3_scope_relation"][0].detach().cpu()),
        "z4": [int(v) for v in decoded["z4"][0].detach().cpu().tolist()],
    }


def _support_counts(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    z1 = {
        name: sum(int(row["gold_z"]["z1"][index]) for row in rows)
        for index, name in enumerate(Z1_LABELS)
    }
    z4 = {
        name: sum(int(row["gold_z"]["z4"][index]) for row in rows)
        for index, name in enumerate(Z4_FIELDS)
    }
    return {"z1_positive": z1, "z4_positive": z4}


def adjudicate_seed(summary: dict[str, Any], support: dict[str, dict[str, int]]) -> dict[str, Any]:
    low_recall: list[dict[str, Any]] = []
    for row in summary["z1"]["per_class"]:
        if support["z1_positive"][row["name"]] > 0 and float(row["recall"]) < H1A_THRESHOLDS["supported_class_recall_min"]:
            low_recall.append({"family": "z1", "name": row["name"], "recall": float(row["recall"])})
    for row in summary["z4"]["per_field"]:
        if support["z4_positive"][row["name"]] > 0 and float(row["recall"]) < H1A_THRESHOLDS["supported_class_recall_min"]:
            low_recall.append({"family": "z4", "name": row["name"], "recall": float(row["recall"])})

    scalar_gate_details: dict[str, dict[str, Any]] = {}
    for name, values in summary["z2"]["scalars"].items():
        supported = int(values["count"]) > 0
        passed = (
            supported
            and math.isfinite(float(values["mean_nAE"]))
            and math.isfinite(float(values["p95_nAE"]))
            and float(values["mean_nAE"]) <= H1A_THRESHOLDS["scalar_mean_nae_max"]
            and float(values["p95_nAE"]) <= H1A_THRESHOLDS["scalar_p95_nae_max"]
        )
        scalar_gate_details[name] = {
            "supported": supported,
            "count": int(values["count"]),
            "mean_nAE": float(values["mean_nAE"]),
            "p95_nAE": float(values["p95_nAE"]),
            "pass": passed,
        }

    gates = {
        "G01_z1_micro_precision": float(summary["z1"]["micro_precision"]) >= H1A_THRESHOLDS["z1_micro_precision_min"],
        "G02_z1_micro_recall": float(summary["z1"]["micro_recall"]) >= H1A_THRESHOLDS["z1_micro_recall_min"],
        "G03_z1_macro_f1": float(summary["z1"]["macro_f1"]) >= H1A_THRESHOLDS["z1_macro_f1_min"],
        "G04_z3_scope_relation_accuracy": float(summary["z3"]["scope_relation_accuracy"]) >= H1A_THRESHOLDS["z3_scope_relation_accuracy_min"],
        "G05_z4_pooled_precision": float(summary["z4"]["pooled_precision"]) >= H1A_THRESHOLDS["z4_pooled_precision_min"],
        "G06_z4_pooled_recall": float(summary["z4"]["pooled_recall"]) >= H1A_THRESHOLDS["z4_pooled_recall_min"],
        "G07_canonical_field_accuracy": float(summary["canonical"]["field_accuracy"]) >= H1A_THRESHOLDS["canonical_field_accuracy_min"],
        "G08_invariance_cluster_consistency": float(summary["invariance_cluster_consistency"]) >= H1A_THRESHOLDS["invariance_cluster_consistency_min"],
        "G09_supported_class_recall_floor": len(low_recall) == 0,
        "G10_target_stability_prerequisite": True,
        "G11_observable_identifiability_prerequisite": True,
        "G12_continuous_z2_scalars": all(item["pass"] for item in scalar_gate_details.values()),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "low_recall_classes": low_recall,
        "scalar_gate_details": scalar_gate_details,
    }


@torch.no_grad()
def evaluate_seed(
    *,
    seed: int,
    model: M1ZArm,
    tokenizer,
    pristine_rows: list[dict[str, Any]],
    predictions_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, int]]]:
    metric_rows: list[dict[str, Any]] = []
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    with predictions_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in pristine_rows:
            logits = model(_encode(tokenizer, record["input_text"]))
            decoded_z = decode_z_logits(logits)
            pred_z = _decoded_z_to_python(decoded_z)
            pred_c = canonical_to_python(recompose_decoded_z(decoded_z))[0]
            row = {
                "scene_id": str(record["scene_id"]),
                "renderer_family": str(record["renderer_family"]),
                "input_text_sha256": _sha256_bytes(str(record["input_text"]).encode("utf-8")),
                "gold_z": record["gold_z"],
                "gold_c": record["gold_c"],
                "pred_z": pred_z,
                "pred_c": pred_c,
            }
            metric_rows.append(row)
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    summary = h1a_representation_summary(metric_rows)
    support = _support_counts(metric_rows)
    return summary, support


def run_h1a(
    *,
    pristine_path: Path,
    tokenizer_path: Path,
    checkpoint_root: Path,
    output_dir: Path,
) -> dict[str, Any]:
    pristine_rows = verify_pristine(pristine_path)
    tokenizer = verify_tokenizer(tokenizer_path)
    output_dir.mkdir(parents=True, exist_ok=False)

    per_seed: dict[str, Any] = {}
    for seed in sorted(CHECKPOINTS):
        checkpoint_path = checkpoint_root / str(seed) / "best.pt"
        model, checkpoint_provenance = load_frozen_best_checkpoint(checkpoint_path, seed)
        summary, support = evaluate_seed(
            seed=seed,
            model=model,
            tokenizer=tokenizer,
            pristine_rows=pristine_rows,
            predictions_path=output_dir / f"predictions_m1z_{seed}.jsonl",
        )
        adjudication = adjudicate_seed(summary, support)
        seed_result = {
            "seed": seed,
            "checkpoint": checkpoint_provenance,
            "summary": summary,
            "support": support,
            "adjudication": adjudication,
        }
        (output_dir / f"h1a_seed_{seed}.json").write_text(
            json.dumps(seed_result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        per_seed[str(seed)] = seed_result
        del model

    all_pass = all(value["adjudication"]["status"] == "PASS" for value in per_seed.values())
    formal = {
        "schema": "MK1-H1A-CONFIRMATORY-ADJUDICATION-v0.1",
        "status": "H1A_PASS" if all_pass else "H1A_FAIL",
        "seed_rule": "ALL_FIVE_PREREGISTERED_M1Z_SEEDS_MUST_INDIVIDUALLY_PASS_ALL_H1A_GATES",
        "seeds": sorted(CHECKPOINTS),
        "per_seed_status": {seed: value["adjudication"]["status"] for seed, value in per_seed.items()},
        "pristine": {
            "sha256": PRISTINE_SHA256,
            "surfaces": EXPECTED_PRISTINE_SURFACES,
            "scenes": EXPECTED_PRISTINE_SCENES,
        },
        "tokenizer_sha256": TOKENIZER_SHA256,
        "thresholds": H1A_THRESHOLDS,
        "target_stability_prerequisite": "PASS",
        "observable_identifiability_prerequisite": "PASS",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "tokenizers": tokenizers.__version__,
            "device": "cpu",
            "dtype": "float32",
        },
        "h1b_computed": False,
        "h1c_computed": False,
    }
    (output_dir / "H1A_FORMAL_ADJUDICATION.json").write_text(
        json.dumps(formal, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return formal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pristine", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = run_h1a(
        pristine_path=Path(args.pristine),
        tokenizer_path=Path(args.tokenizer),
        checkpoint_root=Path(args.checkpoint_root),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
