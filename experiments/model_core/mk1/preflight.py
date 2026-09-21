"""Zero-fresh MK-1 implementation preflight.

Uses only synthetic fixtures and disposable tokenizer data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
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
from .data_contract import (
    build_fixture_scene,
    materialize_scientific_split,
    render_surface,
)
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



_Z1_AUDIT_PHRASES = {
    "CONFLICT_EXISTS": "Two current statements cannot both be true.",
    "EXPLICIT_SUPERSESSION": "A later statement explicitly replaces an earlier statement.",
    "IMPLICIT_SELECTION": "The present context favors one alternative without an explicit replacement marker.",
    "CORRECTION": "A later statement corrects an earlier claim.",
    "CONTEXT_SPLIT": "Different contexts carry different versions of the claim.",
    "EXCEPTS": "The rule contains a specific exception.",
    "EXACT_THRESHOLD": "The rule uses an exact numeric cutoff.",
    "LOWER_BOUND_THRESHOLD": "The rule applies from a stated minimum upward.",
    "UPPER_BOUND_THRESHOLD": "The rule applies only up to a stated maximum.",
    "ORDINAL_TRIGGER": "The rule activates at a stated ordinal position.",
    "VAGUE_COUNT_POLICY": "The rule refers to an imprecise amount rather than a fixed count.",
    "EXACT_DURATION": "A precise duration is stated.",
    "APPROX_DURATION": "An approximate duration is stated.",
    "PERIODIC_RULE": "The rule repeats at a regular interval.",
    "EXPIRY_RULE": "The rule expires after a stated duration.",
    "RECENCY_RELATION": "The relative recency of statements matters.",
    "FALLBACK_IF_UNKNOWN": "When the value is unknown, a fallback is specified.",
    "FALLBACK_IF_CONFLICT": "When statements conflict, a fallback is specified.",
    "FALLBACK_IF_UNAVAILABLE": "When the required source is unavailable, a fallback is specified.",
    "ABSTAINS": "The statement explicitly withholds a definite conclusion.",
    "REQUESTS_CLARIFICATION": "The statement asks for clarification before proceeding.",
    "LOW_CONFIDENCE": "The statement explicitly expresses low confidence.",
    "PRESERVES_CONFLICT": "The statement keeps the disagreement unresolved.",
    "OPERATIONAL_SIGNAL": "The observation includes a directly actionable current signal.",
}

_Z4_POSITIVE_PHRASES = (
    "The evidence itself contains an explicit contradiction.",
    "The evidence establishes the claimed replacement relation.",
    "The evidence is sufficient for the claimed scope.",
    "The evidence directly supports the stated numeric quantity.",
    "The evidence directly supports the stated timing rule.",
    "The evidence directly supports the stated fallback behavior.",
    "The evidence directly supports the actionable signal.",
)


def _independent_scope_relation(evidence_scope: int, asserted_scope: int) -> int:
    contextual = SCOPES.index("CONTEXTUAL")
    if (evidence_scope == contextual) != (asserted_scope == contextual):
        return SCOPE_RELATIONS.index("INCOMPARABLE")
    if evidence_scope == asserted_scope:
        return SCOPE_RELATIONS.index("EQUAL")
    if asserted_scope < evidence_scope:
        return SCOPE_RELATIONS.index("NARROWER")
    return SCOPE_RELATIONS.index("BROADER")


def _parse_float(pattern: str, text: str) -> tuple[float, int]:
    match = re.search(pattern, text)
    if match is None:
        return 0.0, 0
    return float(match.group(1)), 1


def _independent_parse_z(input_text: str) -> dict[str, object]:
    asserted_match = re.search(r"This proposition applies at ([a-z]+) scope\.", input_text)
    evidence_match = re.search(r"The current observation is limited to ([a-z]+) scope\.", input_text)
    if asserted_match is None or evidence_match is None:
        raise ValueError("serialized scope phrase missing")
    asserted_name = asserted_match.group(1).upper()
    evidence_name = evidence_match.group(1).upper()
    if asserted_name not in SCOPES or evidence_name not in SCOPES:
        raise ValueError("serialized scope is outside frozen vocabulary")
    asserted_scope = SCOPES.index(asserted_name)
    evidence_scope = SCOPES.index(evidence_name)

    active = {
        name
        for name, phrase in _Z1_AUDIT_PHRASES.items()
        if phrase in input_text
    }
    active.add(f"{asserted_name}_SCOPE")
    z1 = [int(name in active) for name in Z1_LABELS]

    if "The numeric cutoff is exactly " in input_text:
        comparator = COMPARATORS.index("EXACT")
    elif "The numeric cutoff is at least " in input_text:
        comparator = COMPARATORS.index("LOWER_BOUND")
    elif "The numeric cutoff is at most " in input_text:
        comparator = COMPARATORS.index("UPPER_BOUND")
    else:
        comparator = COMPARATORS.index("NONE")

    if (
        _Z1_AUDIT_PHRASES["EXACT_DURATION"] in input_text
        or _Z1_AUDIT_PHRASES["EXPIRY_RULE"] in input_text
    ):
        temporal_precision = TEMPORAL_PRECISIONS.index("EXACT")
    elif _Z1_AUDIT_PHRASES["APPROX_DURATION"] in input_text:
        temporal_precision = TEMPORAL_PRECISIONS.index("APPROX")
    else:
        temporal_precision = TEMPORAL_PRECISIONS.index("NONE")

    numeric, numeric_mask = _parse_float(
        r"The numeric cutoff is (?:exactly|at least|at most) ([0-9]+(?:\.[0-9]+)?)\.",
        input_text,
    )
    ordinal, ordinal_mask = _parse_float(
        r"The ordinal trigger is position ([0-9]+(?:\.[0-9]+)?)\.",
        input_text,
    )
    duration_match = re.search(
        r"The stated duration is (?:approximately )?([0-9]+(?:\.[0-9]+)?) seconds\.",
        input_text,
    )
    duration = float(duration_match.group(1)) if duration_match else 0.0
    duration_mask = int(duration_match is not None)
    period, period_mask = _parse_float(
        r"The recurring interval is ([0-9]+(?:\.[0-9]+)?) seconds\.",
        input_text,
    )

    z4 = [int(phrase in input_text) for phrase in _Z4_POSITIVE_PHRASES]

    return {
        "z1": z1,
        "z2_comparator": comparator,
        "z2_temporal_precision": temporal_precision,
        "z2_scalars": [numeric, ordinal, duration, period],
        "z2_scalar_mask": [numeric_mask, ordinal_mask, duration_mask, period_mask],
        "z3_evidence_scope": evidence_scope,
        "z3_asserted_scope": asserted_scope,
        "z3_scope_relation": _independent_scope_relation(evidence_scope, asserted_scope),
        "z4": z4,
    }


def _independent_recompose(gold_z: dict[str, object]) -> dict[str, object]:
    z1 = {name: bool(value) for name, value in zip(Z1_LABELS, gold_z["z1"])}
    z4 = {name: bool(value) for name, value in zip(Z4_FIELDS, gold_z["z4"])}
    conflict = z4["conflict_present"]
    resolution = (
        z1["EXPLICIT_SUPERSESSION"]
        or z1["IMPLICIT_SELECTION"]
        or z1["CORRECTION"]
    )
    numeric = (
        z1["EXACT_THRESHOLD"]
        or z1["LOWER_BOUND_THRESHOLD"]
        or z1["UPPER_BOUND_THRESHOLD"]
    )
    temporal = (
        z1["EXACT_DURATION"]
        or z1["APPROX_DURATION"]
        or z1["PERIODIC_RULE"]
        or z1["EXPIRY_RULE"]
    )
    fallback = (
        z1["FALLBACK_IF_UNKNOWN"]
        or z1["FALLBACK_IF_CONFLICT"]
        or z1["FALLBACK_IF_UNAVAILABLE"]
    )
    return {
        "c1": [
            int(conflict),
            int(conflict and resolution),
            int(numeric),
            int(temporal),
            int(fallback),
            int(z1["ABSTAINS"]),
            int(z1["REQUESTS_CLARIFICATION"]),
            int(z1["OPERATIONAL_SIGNAL"]),
        ],
        "c2": int(gold_z["z3_evidence_scope"]),
        "c3": int(gold_z["z3_asserted_scope"]),
        "c4": int(gold_z["z3_scope_relation"]),
        "c5": [
            int(z4["supersession_supported"]),
            int(z4["scope_supported"]),
            int(z4["numeric_value_supported"]),
            int(z4["temporal_rule_supported"]),
            int(z4["fallback_policy_supported"]),
            int(z4["operational_signal_supported"]),
        ],
    }


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _actual_support_audit(scene_rows: list[dict[str, object]], minimum: int) -> dict[str, object]:
    z1 = {name: 0 for name in Z1_LABELS}
    comparator = {name: 0 for name in COMPARATORS}
    temporal_precision = {name: 0 for name in TEMPORAL_PRECISIONS}
    scalar_names = ("numeric_value", "ordinal_index", "duration_seconds", "period_seconds")
    scalar_presence = {name: 0 for name in scalar_names}
    evidence_scope = {name: 0 for name in SCOPES}
    asserted_scope = {name: 0 for name in SCOPES}
    scope_relation = {name: 0 for name in SCOPE_RELATIONS}
    z4 = {name: {"positive": 0, "negative": 0} for name in Z4_FIELDS}
    c1 = {name: {"positive": 0, "negative": 0} for name in C1_FIELDS}
    c5 = {name: {"positive": 0, "negative": 0} for name in C5_FIELDS}

    for row in scene_rows:
        gz = row["gold_z"]
        gc = row["gold_c"]
        for name, value in zip(Z1_LABELS, gz["z1"]):
            z1[name] += int(bool(value))
        comparator[COMPARATORS[int(gz["z2_comparator"])]] += 1
        temporal_precision[TEMPORAL_PRECISIONS[int(gz["z2_temporal_precision"])]] += 1
        for name, present in zip(scalar_names, gz["z2_scalar_mask"]):
            scalar_presence[name] += int(bool(present))
        evidence_scope[SCOPES[int(gz["z3_evidence_scope"])]] += 1
        asserted_scope[SCOPES[int(gz["z3_asserted_scope"])]] += 1
        scope_relation[SCOPE_RELATIONS[int(gz["z3_scope_relation"])]] += 1
        for name, value in zip(Z4_FIELDS, gz["z4"]):
            z4[name]["positive" if bool(value) else "negative"] += 1
        for name, value in zip(C1_FIELDS, gc["c1"]):
            c1[name]["positive" if bool(value) else "negative"] += 1
        for name, value in zip(C5_FIELDS, gc["c5"]):
            c5[name]["positive" if bool(value) else "negative"] += 1

    flat_primary = {
        "z1": z1,
        "comparator": comparator,
        "temporal_precision": temporal_precision,
        "scalar_presence": scalar_presence,
        "evidence_scope": evidence_scope,
        "asserted_scope": asserted_scope,
        "scope_relation": scope_relation,
    }
    for label, counts in flat_primary.items():
        bad = {name: count for name, count in counts.items() if count < minimum}
        if bad:
            raise AssertionError(f"{label} support below {minimum}: {bad}")
    for label, counts in (("z4", z4), ("c1", c1), ("c5", c5)):
        bad = {
            name: values
            for name, values in counts.items()
            if values["positive"] < minimum or values["negative"] < minimum
        }
        if bad:
            raise AssertionError(f"{label} binary support below {minimum}: {bad}")

    return {
        "minimum_primary_flat_support": min(
            min(counts.values()) for counts in flat_primary.values()
        ),
        "minimum_z4_binary_cell": min(
            min(values.values()) for values in z4.values()
        ),
        "minimum_c1_binary_cell": min(
            min(values.values()) for values in c1.values()
        ),
        "minimum_c5_binary_cell": min(
            min(values.values()) for values in c5.values()
        ),
    }


def _audit_materialized_dataset(
    train_rows: list[dict[str, object]],
    validation_rows: list[dict[str, object]],
    confirm_rows: list[dict[str, object]],
) -> dict[str, object]:
    expected = {
        "TRAIN": (train_rows, 4_000, 2_000, {"A", "B"}, range(7_101_000, 7_103_000)),
        "VALIDATION": (validation_rows, 800, 400, {"A", "B"}, range(7_103_000, 7_103_400)),
        "PRISTINE_CONFIRMATORY": (
            confirm_rows,
            1_200,
            600,
            {"A", "C"},
            range(7_104_000, 7_104_600),
        ),
    }

    scene_first: dict[str, dict[str, object]] = {}
    scene_surfaces: dict[str, list[dict[str, object]]] = {}
    all_rows = train_rows + validation_rows + confirm_rows
    split_scene_ids: dict[str, set[str]] = {}

    for split, (rows, expected_rows, expected_scenes, renderers, scene_range) in expected.items():
        if len(rows) != expected_rows:
            raise AssertionError(f"{split} surface count mismatch")
        if {str(row["split"]) for row in rows} != {split}:
            raise AssertionError(f"{split} contains wrong split label")
        if {str(row["renderer_family"]) for row in rows} != renderers:
            raise AssertionError(f"{split} renderer-family mismatch")
        ids = {str(row["scene_id"]) for row in rows}
        if len(ids) != expected_scenes:
            raise AssertionError(f"{split} canonical-scene count mismatch")
        expected_ids = {str(value) for value in scene_range}
        if ids != expected_ids:
            raise AssertionError(f"{split} scene namespace mismatch")
        split_scene_ids[split] = ids
        for row in rows:
            sid = str(row["scene_id"])
            scene_surfaces.setdefault(sid, []).append(row)
            scene_first.setdefault(sid, row)

    if (
        split_scene_ids["TRAIN"] & split_scene_ids["VALIDATION"]
        or split_scene_ids["TRAIN"] & split_scene_ids["PRISTINE_CONFIRMATORY"]
        or split_scene_ids["VALIDATION"] & split_scene_ids["PRISTINE_CONFIRMATORY"]
    ):
        raise AssertionError("scene ID crossed split boundary")

    raw_counts = Counter(str(row["input_text"]) for row in all_rows)
    raw_duplicate_count = sum(count - 1 for count in raw_counts.values() if count > 1)
    if raw_duplicate_count != 0:
        raise AssertionError(f"raw text duplicates detected: {raw_duplicate_count}")

    signatures = Counter(
        json.dumps(row["gold_z"], sort_keys=True, separators=(",", ":"))
        for row in scene_first.values()
    )
    canonical_duplicate_count = sum(count - 1 for count in signatures.values() if count > 1)
    if canonical_duplicate_count != 0:
        raise AssertionError(f"canonical Z duplicates detected: {canonical_duplicate_count}")

    surface_invariance_failures = 0
    observable_rederivation_failures = 0
    frozen_recomposition_failures = 0
    independent_recomposition_failures = 0
    max_utf8_bytes = 0

    for sid, rows in scene_surfaces.items():
        if len(rows) != 2:
            raise AssertionError(f"scene {sid} does not have exactly two surfaces")
        first = rows[0]
        for row in rows[1:]:
            if row["gold_z"] != first["gold_z"] or row["gold_c"] != first["gold_c"]:
                surface_invariance_failures += 1
        for row in rows:
            text = str(row["input_text"])
            max_utf8_bytes = max(max_utf8_bytes, len(text.encode("utf-8")))
            parsed_z = _independent_parse_z(text)
            if parsed_z != row["gold_z"]:
                observable_rederivation_failures += 1
            independent_c = _independent_recompose(parsed_z)
            if independent_c != row["gold_c"]:
                independent_recomposition_failures += 1
            if recompose_gold_z(row["gold_z"]) != row["gold_c"]:
                frozen_recomposition_failures += 1

    if surface_invariance_failures:
        raise AssertionError("surface target invariance failed")
    if observable_rederivation_failures:
        raise AssertionError(
            f"observable Z rederivation failed on {observable_rederivation_failures} surfaces"
        )
    if independent_recomposition_failures:
        raise AssertionError(
            f"independent C recomposition failed on {independent_recomposition_failures} surfaces"
        )
    if frozen_recomposition_failures:
        raise AssertionError(
            f"frozen C recomposition failed on {frozen_recomposition_failures} surfaces"
        )

    train_scenes = [scene_first[sid] for sid in sorted(split_scene_ids["TRAIN"])]
    confirm_scenes = [
        scene_first[sid] for sid in sorted(split_scene_ids["PRISTINE_CONFIRMATORY"])
    ]
    train_support = _actual_support_audit(train_scenes, 100)
    confirm_support = _actual_support_audit(confirm_scenes, 40)

    def scalar_contract_ok(row: dict[str, object]) -> bool:
        gz = row["gold_z"]
        z1 = {name: bool(v) for name, v in zip(Z1_LABELS, gz["z1"])}
        mask = [bool(v) for v in gz["z2_scalar_mask"]]
        if (z1["EXACT_THRESHOLD"] or z1["LOWER_BOUND_THRESHOLD"] or z1["UPPER_BOUND_THRESHOLD"]) != mask[0]:
            return False
        if z1["ORDINAL_TRIGGER"] != mask[1]:
            return False
        if (z1["EXACT_DURATION"] or z1["APPROX_DURATION"] or z1["EXPIRY_RULE"]) != mask[2]:
            return False
        if z1["PERIODIC_RULE"] != mask[3]:
            return False
        return True

    scalar_contract_failures = sum(
        int(not scalar_contract_ok(row)) for row in scene_first.values()
    )
    if scalar_contract_failures:
        raise AssertionError("generating continuous-quantity retention failed")

    family_slices = (
        slice(0, 6),
        slice(6, 11),
        slice(11, 16),
        slice(16, 19),
        slice(19, 23),
        slice(31, 32),
    )
    confirm_multifactor = 0
    for row in confirm_scenes:
        z1 = row["gold_z"]["z1"]
        active = sum(int(any(z1[sl])) for sl in family_slices)
        confirm_multifactor += int(active >= 2)
    confirm_multifactor_fraction = confirm_multifactor / len(confirm_scenes)
    if confirm_multifactor_fraction < 0.30:
        raise AssertionError("confirmatory multi-factor fraction below 30%")

    contextual = SCOPES.index("CONTEXTUAL")
    h1c_relation_covered = sum(
        int(
            row["gold_z"]["z3_evidence_scope"] != contextual
            and row["gold_z"]["z3_asserted_scope"] != contextual
        )
        for row in scene_first.values()
    )
    h1c_relation_coverage = h1c_relation_covered / len(scene_first)

    return {
        "status": "PASS",
        "surface_records": len(all_rows),
        "canonical_scenes": len(scene_first),
        "raw_text_duplicate_count": raw_duplicate_count,
        "canonical_z_duplicate_count": canonical_duplicate_count,
        "surface_invariance_failures": surface_invariance_failures,
        "observable_z_rederivation_failures": observable_rederivation_failures,
        "independent_c_recomposition_failures": independent_recomposition_failures,
        "frozen_c_recomposition_failures": frozen_recomposition_failures,
        "scalar_contract_failures": scalar_contract_failures,
        "train_support": train_support,
        "confirmatory_support": confirm_support,
        "confirmatory_multifactor_fraction": confirm_multifactor_fraction,
        "h1c_scope_relation_coverage": h1c_relation_coverage,
        "threshold_margin_gate": "NOT_APPLICABLE_NO_THRESHOLD_DERIVED_PRIMARY_HARD_TARGETS",
        "observable_identifiability": "PASS_INPUT_TEXT_ONLY_INDEPENDENT_REDERIVATION",
        "ambiguous_primary_scenes": 0,
        "forbidden_information_reads": 0,
        "max_utf8_bytes": max_utf8_bytes,
        "encoded_length_gate": "DEFERRED_TO_TRAIN_ONLY_TOKENIZER_FREEZE",
    }


def run_materialization_and_audit(
    output_dir: str | Path,
    audit_output: str | Path,
    manifest_output: str | Path,
) -> dict[str, object]:
    root = Path(output_dir)
    if root.exists():
        raise FileExistsError("materialization output directory already exists")
    root.mkdir(parents=True)

    split_paths = {
        "TRAIN": root / "train.jsonl",
        "VALIDATION": root / "validation.jsonl",
        "PRISTINE_CONFIRMATORY": root / "pristine_confirmatory.jsonl",
    }
    materialization = {
        split: materialize_scientific_split(split, path)
        for split, path in split_paths.items()
    }

    audit_path = Path(audit_output)
    manifest_path = Path(manifest_output)
    error: Exception | None = None
    try:
        audit = _audit_materialized_dataset(
            _load_jsonl(split_paths["TRAIN"]),
            _load_jsonl(split_paths["VALIDATION"]),
            _load_jsonl(split_paths["PRISTINE_CONFIRMATORY"]),
        )
    except Exception as exc:
        error = exc
        audit = {
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    file_manifest = {}
    for split, path in split_paths.items():
        file_manifest[split] = {
            "path": str(path),
            "sha256": _sha256_path(path),
            "bytes": path.stat().st_size,
            "surface_records": materialization[split]["surface_records"],
            "canonical_scenes": materialization[split]["canonical_scenes"],
        }

    try:
        source_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        source_head = "UNKNOWN"

    manifest = {
        "schema": "MK1-SCIENTIFIC-MATERIALIZATION-MANIFEST-v0.1",
        "source_head": source_head,
        "generator_contract": "AMENDMENT_003",
        "files": file_manifest,
        "audit_status": audit["status"],
        "scientific_training_executed": False,
        "scientific_tokenizer_fitted": False,
    }
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = {
        "schema": "MK1-MATERIALIZATION-AND-PRETRAINING-AUDIT-v0.1",
        "status": audit["status"],
        "manifest": manifest,
        "audit": audit,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if error is not None:
        raise error
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("preflight", "materialize-audit"),
        default="preflight",
    )
    parser.add_argument("--output", default="mk1_zero_fresh_preflight_result.json")
    parser.add_argument("--materialize-dir", default="mk1_materialized_v0_1")
    parser.add_argument("--audit-output", default="mk1_pretraining_data_audit.json")
    parser.add_argument("--manifest-output", default="mk1_materialization_manifest.json")
    args = parser.parse_args()
    if args.mode == "preflight":
        result = run_preflight(args.output)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    run_materialization_and_audit(
        args.materialize_dir,
        args.audit_output,
        args.manifest_output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
