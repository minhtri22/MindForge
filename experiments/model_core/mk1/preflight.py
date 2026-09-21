"""Zero-fresh MK-1 implementation preflight.

Uses only synthetic fixtures and disposable tokenizer data.
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import torch

from mindforge.config import ModelConfig
from mindforge.model import create_model, parameter_count as b0_parameter_count
from mindforge.tokenizer import metadata, train_tokenizer

from .contracts import (
    B0_PARAMETER_COUNT,
    C1_FIELDS,
    C5_FIELDS,
    C_SLICES,
    COMPARATORS,
    DIRECT_PARAMETER_COUNT,
    D_C,
    D_Z,
    M1Z_PARAMETER_COUNT,
    SCIENTIFIC_TRAINING_SEEDS,
    SCOPES,
    SCOPE_RELATIONS,
    TEMPORAL_PRECISIONS,
    Z1_LABELS,
    Z4_FIELDS,
    Z_SLICES,
)
from .data_contract import build_fixture_scene, render_surface
from .losses import direct_loss, m1z_loss
from .modeling import build_arm, frozen_backbone_state, parameter_count
from .recompose import canonical_equal, recompose_gold_z
from .trainer import deterministic_sample_indices, target_tensors


FIXTURE_SEED = 12345


def _legacy_forward_reference(model: torch.nn.Module, tokens: torch.Tensor) -> torch.Tensor:
    if tokens.ndim != 2:
        raise ValueError("tokens must have shape [batch, context]")
    _, context = tokens.shape
    positions = torch.arange(context, device=tokens.device)
    hidden = model.token_embedding(tokens) + model.position_embedding(positions)[None, :, :]
    mask = torch.triu(torch.ones(context, context, dtype=torch.bool, device=tokens.device), diagonal=1)
    for layer in model.layers:
        hidden = layer(hidden, src_mask=mask, is_causal=True)
    return model.lm_head(model.norm(hidden))


def _blank_gold_z() -> dict[str, object]:
    return {
        "z1": [0] * len(Z1_LABELS),
        "z2_comparator": 0,
        "z2_temporal_precision": 0,
        "z2_scalars": [0.0, 0.0, 0.0, 0.0],
        "z2_scalar_mask": [0, 0, 0, 0],
        "z3_evidence_scope": 0,
        "z3_asserted_scope": 0,
        "z3_scope_relation": 0,
        "z4": [0] * len(Z4_FIELDS),
    }


def _exercise_recomposer() -> None:
    z1_index = {name: i for i, name in enumerate(Z1_LABELS)}
    z4_index = {name: i for i, name in enumerate(Z4_FIELDS)}

    z = _blank_gold_z()
    z["z4"][z4_index["conflict_present"]] = 1
    assert recompose_gold_z(z)["c1"][0] == 1

    z = _blank_gold_z()
    z["z1"][z1_index["EXPLICIT_SUPERSESSION"]] = 1
    assert recompose_gold_z(z)["c1"][1] == 0
    z["z4"][z4_index["conflict_present"]] = 1
    assert recompose_gold_z(z)["c1"][1] == 1

    for label, c1_index in (
        ("EXACT_THRESHOLD", 2),
        ("EXACT_DURATION", 3),
        ("FALLBACK_IF_UNKNOWN", 4),
        ("ABSTAINS", 5),
        ("REQUESTS_CLARIFICATION", 6),
        ("OPERATIONAL_SIGNAL", 7),
    ):
        z = _blank_gold_z()
        z["z1"][z1_index[label]] = 1
        assert recompose_gold_z(z)["c1"][c1_index] == 1

    z = _blank_gold_z()
    z["z3_evidence_scope"] = 2
    z["z3_asserted_scope"] = 5
    z["z3_scope_relation"] = 3
    c = recompose_gold_z(z)
    assert (c["c2"], c["c3"], c["c4"]) == (2, 5, 3)

    for offset, name in enumerate(Z4_FIELDS[1:]):
        z = _blank_gold_z()
        z["z4"][z4_index[name]] = 1
        c = recompose_gold_z(z)
        assert c["c5"][offset] == 1


def _finite_backward(arm_name: str, arm: torch.nn.Module, input_ids: torch.Tensor, record: dict[str, object]) -> float:
    arm.zero_grad(set_to_none=True)
    z_target, c_target = target_tensors(record, torch.device("cpu"))
    logits = arm(input_ids)
    loss, _ = direct_loss(logits, c_target) if arm_name == "direct" else m1z_loss(logits, z_target)
    if not bool(torch.isfinite(loss)):
        raise AssertionError(f"{arm_name} loss is not finite")
    loss.backward()
    for parameter in arm.parameters():
        if parameter.grad is not None and not bool(torch.isfinite(parameter.grad).all()):
            raise AssertionError(f"{arm_name} has non-finite gradient")
    return float(loss.detach().cpu())


def _projected_generator_qa() -> dict[str, object]:
    """Fixture-only projection of Amendment-003 support/integrity gates."""
    train_ordinals = range(0, 2_000)
    confirm_ordinals = range(2_400, 3_000)
    all_ordinals = range(0, 3_000)

    train_scenes = [build_fixture_scene(i) for i in train_ordinals]
    confirm_scenes = [build_fixture_scene(i) for i in confirm_ordinals]
    all_scenes = [build_fixture_scene(i) for i in all_ordinals]

    def positive_counts(scenes, key: str, names: tuple[str, ...]) -> dict[str, int]:
        counts = {name: 0 for name in names}
        for scene in scenes:
            values = scene.gold_z[key]
            for name, value in zip(names, values):
                counts[name] += int(bool(value))
        return counts

    def binary_counts(scenes, source: str, names: tuple[str, ...]) -> dict[str, dict[str, int]]:
        counts = {name: {"positive": 0, "negative": 0} for name in names}
        for scene in scenes:
            values = scene.gold_z[source] if source.startswith("z") else scene.gold_c[source]
            for name, value in zip(names, values):
                counts[name]["positive" if bool(value) else "negative"] += 1
        return counts

    def categorical_counts(scenes, source: str, names: tuple[str, ...], *, canonical: bool = False) -> dict[str, int]:
        counts = Counter()
        for scene in scenes:
            value = scene.gold_c[source] if canonical else scene.gold_z[source]
            counts[names[int(value)]] += 1
        return {name: int(counts[name]) for name in names}

    z1_train = positive_counts(train_scenes, "z1", tuple(Z1_LABELS))
    z1_confirm = positive_counts(confirm_scenes, "z1", tuple(Z1_LABELS))
    comparator_train = categorical_counts(train_scenes, "z2_comparator", tuple(COMPARATORS))
    comparator_confirm = categorical_counts(confirm_scenes, "z2_comparator", tuple(COMPARATORS))
    precision_train = categorical_counts(train_scenes, "z2_temporal_precision", tuple(TEMPORAL_PRECISIONS))
    precision_confirm = categorical_counts(confirm_scenes, "z2_temporal_precision", tuple(TEMPORAL_PRECISIONS))

    scalar_names = ("numeric_value", "ordinal_index", "duration_seconds", "period_seconds")
    scalar_train = {name: 0 for name in scalar_names}
    scalar_confirm = {name: 0 for name in scalar_names}
    for scene in train_scenes:
        for name, present in zip(scalar_names, scene.gold_z["z2_scalar_mask"]):
            scalar_train[name] += int(bool(present))
    for scene in confirm_scenes:
        for name, present in zip(scalar_names, scene.gold_z["z2_scalar_mask"]):
            scalar_confirm[name] += int(bool(present))

    z3_ev_train = categorical_counts(train_scenes, "z3_evidence_scope", tuple(SCOPES))
    z3_ev_confirm = categorical_counts(confirm_scenes, "z3_evidence_scope", tuple(SCOPES))
    z3_as_train = categorical_counts(train_scenes, "z3_asserted_scope", tuple(SCOPES))
    z3_as_confirm = categorical_counts(confirm_scenes, "z3_asserted_scope", tuple(SCOPES))
    z3_rel_train = categorical_counts(train_scenes, "z3_scope_relation", tuple(SCOPE_RELATIONS))
    z3_rel_confirm = categorical_counts(confirm_scenes, "z3_scope_relation", tuple(SCOPE_RELATIONS))

    z4_train = binary_counts(train_scenes, "z4", tuple(Z4_FIELDS))
    z4_confirm = binary_counts(confirm_scenes, "z4", tuple(Z4_FIELDS))
    c1_train = binary_counts(train_scenes, "c1", tuple(C1_FIELDS))
    c1_confirm = binary_counts(confirm_scenes, "c1", tuple(C1_FIELDS))
    c5_train = binary_counts(train_scenes, "c5", tuple(C5_FIELDS))
    c5_confirm = binary_counts(confirm_scenes, "c5", tuple(C5_FIELDS))

    c2_train = categorical_counts(train_scenes, "c2", tuple(SCOPES), canonical=True)
    c2_confirm = categorical_counts(confirm_scenes, "c2", tuple(SCOPES), canonical=True)
    c3_train = categorical_counts(train_scenes, "c3", tuple(SCOPES), canonical=True)
    c3_confirm = categorical_counts(confirm_scenes, "c3", tuple(SCOPES), canonical=True)
    c4_train = categorical_counts(train_scenes, "c4", tuple(SCOPE_RELATIONS), canonical=True)
    c4_confirm = categorical_counts(confirm_scenes, "c4", tuple(SCOPE_RELATIONS), canonical=True)

    def require_minimum(counts: dict[str, int], minimum: int, label: str) -> None:
        bad = {name: count for name, count in counts.items() if count < minimum}
        if bad:
            raise AssertionError(f"{label} support below {minimum}: {bad}")

    def require_binary_minimum(counts: dict[str, dict[str, int]], minimum: int, label: str) -> None:
        bad = {
            name: values
            for name, values in counts.items()
            if values["positive"] < minimum or values["negative"] < minimum
        }
        if bad:
            raise AssertionError(f"{label} binary support below {minimum}: {bad}")

    for label, train_counts, confirm_counts in (
        ("Z1", z1_train, z1_confirm),
        ("Z2 comparator", comparator_train, comparator_confirm),
        ("Z2 temporal precision", precision_train, precision_confirm),
        ("Z2 scalar presence", scalar_train, scalar_confirm),
        ("Z3 evidence scope", z3_ev_train, z3_ev_confirm),
        ("Z3 asserted scope", z3_as_train, z3_as_confirm),
        ("Z3 scope relation", z3_rel_train, z3_rel_confirm),
        ("C2 evidence scope", c2_train, c2_confirm),
        ("C3 asserted scope", c3_train, c3_confirm),
        ("C4 scope relation", c4_train, c4_confirm),
    ):
        require_minimum(train_counts, 100, f"{label} TRAIN")
        require_minimum(confirm_counts, 40, f"{label} confirmatory")

    for label, train_counts, confirm_counts in (
        ("Z4", z4_train, z4_confirm),
        ("C1", c1_train, c1_confirm),
        ("C5", c5_train, c5_confirm),
    ):
        require_binary_minimum(train_counts, 100, f"{label} TRAIN")
        require_binary_minimum(confirm_counts, 40, f"{label} confirmatory")

    signatures = {
        json.dumps(scene.gold_z, sort_keys=True, separators=(",", ":"))
        for scene in all_scenes
    }
    if len(signatures) != 3_000:
        raise AssertionError("projected canonical Z signatures are not unique")

    if any(not any(scene.gold_z["z2_scalar_mask"]) for scene in all_scenes):
        raise AssertionError("projected scene without a continuous scalar")

    family_slices = (
        slice(0, 6),
        slice(6, 11),
        slice(11, 16),
        slice(16, 19),
        slice(19, 23),
        slice(31, 32),
    )
    multifactor = 0
    for scene in confirm_scenes:
        z1 = scene.gold_z["z1"]
        active_families = sum(int(any(z1[sl])) for sl in family_slices)
        multifactor += int(active_families >= 2)
    multifactor_fraction = multifactor / len(confirm_scenes)
    if multifactor_fraction < 0.30:
        raise AssertionError("projected confirmatory multi-factor fraction below 30%")

    contextual = SCOPES.index("CONTEXTUAL")
    h1c_relation_covered = sum(
        int(
            scene.gold_z["z3_evidence_scope"] != contextual
            and scene.gold_z["z3_asserted_scope"] != contextual
        )
        for scene in all_scenes
    )
    h1c_scope_relation_coverage = h1c_relation_covered / len(all_scenes)

    return {
        "status": "PASS",
        "projected_train_scenes": len(train_scenes),
        "projected_confirmatory_scenes": len(confirm_scenes),
        "projected_total_scenes": len(all_scenes),
        "canonical_z_unique": len(signatures) == 3_000,
        "all_scenes_have_scalar": True,
        "confirmatory_multifactor_fraction": multifactor_fraction,
        "h1c_scope_relation_coverage": h1c_scope_relation_coverage,
        "minimum_train_z1_support": min(z1_train.values()),
        "minimum_confirmatory_z1_support": min(z1_confirm.values()),
        "minimum_train_scalar_presence": min(scalar_train.values()),
        "minimum_confirmatory_scalar_presence": min(scalar_confirm.values()),
        "minimum_train_scope_relation_support": min(z3_rel_train.values()),
        "minimum_confirmatory_scope_relation_support": min(z3_rel_confirm.values()),
        "minimum_train_z4_binary_cell": min(
            min(v["positive"], v["negative"]) for v in z4_train.values()
        ),
        "minimum_confirmatory_z4_binary_cell": min(
            min(v["positive"], v["negative"]) for v in z4_confirm.values()
        ),
        "minimum_train_c1_binary_cell": min(
            min(v["positive"], v["negative"]) for v in c1_train.values()
        ),
        "minimum_confirmatory_c1_binary_cell": min(
            min(v["positive"], v["negative"]) for v in c1_confirm.values()
        ),
        "minimum_train_c5_binary_cell": min(
            min(v["positive"], v["negative"]) for v in c5_train.values()
        ),
        "minimum_confirmatory_c5_binary_cell": min(
            min(v["positive"], v["negative"]) for v in c5_confirm.values()
        ),
        "threshold_margin_gate": "NOT_APPLICABLE_NO_THRESHOLD_DERIVED_PRIMARY_HARD_TARGETS",
    }


def run_preflight(output_path: str | Path) -> dict[str, object]:
    torch.set_num_threads(1)
    config = ModelConfig()

    torch.manual_seed(FIXTURE_SEED)
    b0 = create_model(config).float().eval()
    if b0_parameter_count(b0) != B0_PARAMETER_COUNT:
        raise AssertionError("B0 parameter count changed")

    tokens = torch.tensor([[1, 7, 11, 19, 23, 29]], dtype=torch.long)
    with torch.no_grad():
        before = _legacy_forward_reference(b0, tokens)
        after = b0(tokens)
    parity = bool(torch.equal(before, after))
    if not parity:
        raise AssertionError("B0 hidden-state refactor changed logits")

    state = frozen_backbone_state(FIXTURE_SEED, config)
    direct = build_arm("direct", state, config).float()
    m1z = build_arm("m1z", state, config).float()
    direct_count = parameter_count(direct)
    m1z_count = parameter_count(m1z)
    if direct_count != DIRECT_PARAMETER_COUNT or m1z_count != M1Z_PARAMETER_COUNT:
        raise AssertionError("representation arm parameter count mismatch")
    gap_fraction = abs(m1z_count - direct_count) / max(m1z_count, direct_count)
    if gap_fraction > 0.01:
        raise AssertionError("parameter gap exceeds frozen 1% limit")
    if bool(direct.readout.weight.any()) or bool(direct.readout.bias.any()):
        raise AssertionError("direct readout is not zero initialized")
    if bool(m1z.readout.weight.any()) or bool(m1z.readout.bias.any()):
        raise AssertionError("M1-Z readout is not zero initialized")

    expected_z = {
        "z1": (0, 32),
        "z2_comparator": (32, 36),
        "z2_temporal_precision": (36, 39),
        "z2_scalars": (39, 43),
        "z3_evidence_scope": (43, 51),
        "z3_asserted_scope": (51, 59),
        "z3_scope_relation": (59, 63),
        "z4": (63, 70),
    }
    expected_c = {"c1": (0, 8), "c2": (8, 16), "c3": (16, 24), "c4": (24, 28), "c5": (28, 34)}
    if {k: (v.start, v.stop) for k, v in Z_SLICES.items()} != expected_z:
        raise AssertionError("Z tensor slices drifted")
    if {k: (v.start, v.stop) for k, v in C_SLICES.items()} != expected_c:
        raise AssertionError("C tensor slices drifted")
    if D_Z != 70 or D_C != 34:
        raise AssertionError("output dimension drift")

    _exercise_recomposer()
    fixture_scenes = [build_fixture_scene(i) for i in range(24)]
    for scene in fixture_scenes:
        if not canonical_equal(scene.gold_c, recompose_gold_z(scene.gold_z)):
            raise AssertionError("fixture gold C != R(gold Z)")
        surface = render_surface(scene, "A")
        if any(label in surface for label in Z1_LABELS):
            raise AssertionError("renderer leaked exact target label name")

    order_a = deterministic_sample_indices(17, FIXTURE_SEED)
    order_b = deterministic_sample_indices(17, FIXTURE_SEED)
    paired_schedule = [next(order_a) for _ in range(64)] == [next(order_b) for _ in range(64)]
    if not paired_schedule:
        raise AssertionError("paired sample schedule is not deterministic")

    with tempfile.TemporaryDirectory(prefix="mk1-zero-fresh-") as temp:
        root = Path(temp)
        fixture_text = root / "fixture.txt"
        fixture_text.write_text(
            "\n".join(render_surface(scene, "A") + "\n" + render_surface(scene, "B") for scene in fixture_scenes),
            encoding="utf-8",
        )
        tokenizer_path = root / "fixture-tokenizer.json"
        tokenizer = train_tokenizer([fixture_text], tokenizer_path, vocab_size=16_384)
        info = metadata(tokenizer_path, tokenizer)
        actual_vocab = int(info["vocab_size"])
        if not 258 <= actual_vocab <= 16_384:
            raise AssertionError("synthetic tokenizer cardinality outside amended gate")

        record = {
            "gold_z": fixture_scenes[0].gold_z,
            "gold_c": fixture_scenes[0].gold_c,
        }
        text_ids = tokenizer.encode(render_surface(fixture_scenes[0], "A")).ids
        if not text_ids or max(text_ids) >= 16_384:
            raise AssertionError("synthetic tokenizer emitted invalid B0 token ID")
        input_ids = torch.tensor([text_ids], dtype=torch.long)
        direct_loss_value = _finite_backward("direct", direct, input_ids, record)
        m1z_loss_value = _finite_backward("m1z", m1z, input_ids, record)

    forbidden_paths = [
        Path("experiments/model_core/mk1/materialized"),
        Path("runs/model_core/mk1"),
    ]
    if any(path.exists() for path in forbidden_paths):
        raise AssertionError("zero-fresh preflight found a scientific data/run directory")

    projected_generator = _projected_generator_qa()

    result: dict[str, object] = {
        "schema": "MK1-ZERO-FRESH-PREFLIGHT-v0.2",
        "status": "PASS",
        "b0_parameter_count": B0_PARAMETER_COUNT,
        "hidden_state_logit_parity": parity,
        "direct_parameter_count": direct_count,
        "m1z_parameter_count": m1z_count,
        "parameter_gap_fraction": gap_fraction,
        "tensor_slices": "PASS",
        "zero_readout_initialization": "PASS",
        "recomposer_identities": "PASS",
        "fixture_gold_recomposition": "PASS",
        "direct_synthetic_loss_finite": math.isfinite(direct_loss_value),
        "m1z_synthetic_loss_finite": math.isfinite(m1z_loss_value),
        "paired_synthetic_schedule": paired_schedule,
        "synthetic_tokenizer_contract": "PASS",
        "scientific_namespace_touched": False,
        "scientific_seed_touched": False,
        "scientific_data_created": False,
        "amendment_003_projected_generator_qa": projected_generator,
    }
    serialized = json.dumps(result, sort_keys=True)
    if "710" in serialized or any(str(seed) in serialized for seed in SCIENTIFIC_TRAINING_SEEDS):
        raise AssertionError("preflight artifact contains a reserved scientific identifier")
    destination = Path(output_path)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="mk1_zero_fresh_preflight_result.json")
    args = parser.parse_args()
    result = run_preflight(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
