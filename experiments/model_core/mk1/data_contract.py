"""Deterministic MK-1 canonical-scene and surface contract.

Scientific materialization remains externally gated. Fixture/projection QA may use
non-scientific ordinals without invoking any reserved scientific scene ID.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    COMPARATORS,
    CONFIRMATORY_SCENE_RANGE,
    FALLBACK_LABELS,
    QUANTIFIER_LABELS,
    RELATION_LABELS,
    RENDERER_HELDOUT_C,
    RENDERER_TRAIN_A,
    RENDERER_TRAIN_B,
    SCOPES,
    SCOPE_RELATIONS,
    TEMPORAL_LABELS,
    TEMPORAL_PRECISIONS,
    TRAIN_SCENE_RANGE,
    UNCERTAINTY_LABELS,
    VALIDATION_SCENE_RANGE,
    Z1_LABELS,
)
from .recompose import canonical_equal, recompose_gold_z

_Z1_INDEX = {name: i for i, name in enumerate(Z1_LABELS)}
_SCOPE_INDEX = {name: i for i, name in enumerate(SCOPES)}

_RELATION_MODIFIERS = (
    "EXPLICIT_SUPERSESSION",
    "IMPLICIT_SELECTION",
    "CORRECTION",
    "CONTEXT_SPLIT",
    "EXCEPTS",
    None,
)

_QUANTIFIER_SLOTS = tuple(QUANTIFIER_LABELS) + (None,)
_TEMPORAL_SLOTS = tuple(TEMPORAL_LABELS) + (None,)
_FALLBACK_SLOTS = tuple(FALLBACK_LABELS) + (None,)
_UNCERTAINTY_SLOTS = tuple(UNCERTAINTY_LABELS) + (None,)


@dataclass(frozen=True)
class CanonicalScene:
    scene_id: str
    split: str
    assertion: str
    evidence: str
    applicability_boundary: str
    revision_trigger: str
    gold_z: dict[str, Any]
    gold_c: dict[str, Any]


@dataclass(frozen=True)
class SurfaceRecord:
    scene_id: str
    split: str
    renderer_family: str
    input_text: str
    pit_evidence: dict[str, Any]
    pit_teaching_signal: dict[str, Any]
    gold_z: dict[str, Any]
    gold_c: dict[str, Any]


def split_for_scientific_scene_id(scene_id: int) -> str:
    if scene_id in TRAIN_SCENE_RANGE:
        return "TRAIN"
    if scene_id in VALIDATION_SCENE_RANGE:
        return "VALIDATION"
    if scene_id in CONFIRMATORY_SCENE_RANGE:
        return "PRISTINE_CONFIRMATORY"
    raise ValueError("scene id is outside the frozen scientific namespaces")


def scientific_ordinal(scene_id: int) -> int:
    split = split_for_scientific_scene_id(scene_id)
    if split == "TRAIN":
        return scene_id - TRAIN_SCENE_RANGE.start
    if split == "VALIDATION":
        return 2_000 + (scene_id - VALIDATION_SCENE_RANGE.start)
    return 2_400 + (scene_id - CONFIRMATORY_SCENE_RANGE.start)


def _scope_relation(evidence_scope: int, asserted_scope: int) -> int:
    contextual = _SCOPE_INDEX["CONTEXTUAL"]
    if (evidence_scope == contextual) != (asserted_scope == contextual):
        return SCOPE_RELATIONS.index("INCOMPARABLE")
    if evidence_scope == asserted_scope:
        return SCOPE_RELATIONS.index("EQUAL")
    if asserted_scope < evidence_scope:
        return SCOPE_RELATIONS.index("NARROWER")
    return SCOPE_RELATIONS.index("BROADER")


def _scope_pair(ordinal: int) -> tuple[int, int]:
    mode = ordinal % 4
    k = ordinal // 4
    contextual = _SCOPE_INDEX["CONTEXTUAL"]
    if mode == 0:
        scope = k % 8
        return scope, scope
    if mode == 1:
        evidence_scope = 1 + (k % 6)
        return evidence_scope, evidence_scope - 1
    if mode == 2:
        evidence_scope = k % 6
        return evidence_scope, evidence_scope + 1
    if k % 2 == 0:
        return contextual, (k // 2) % 7
    return (k // 2) % 7, contextual


def _scope_supported(evidence_scope: int, asserted_scope: int) -> bool:
    contextual = _SCOPE_INDEX["CONTEXTUAL"]
    if asserted_scope == contextual:
        return True
    if evidence_scope == contextual:
        return asserted_scope in {
            _SCOPE_INDEX["OBSERVATION"],
            _SCOPE_INDEX["TURN"],
            _SCOPE_INDEX["SESSION"],
            contextual,
        }
    return asserted_scope <= evidence_scope


def _support_bit(ordinal: int, salt: int) -> bool:
    return ((ordinal + 3 * salt) % 4) < 2


def scalar_permutation_value(ordinal: int) -> float:
    if ordinal < 0:
        raise ValueError("ordinal must be non-negative")
    return float(((7_919 * ordinal + 1_237) % 10_007) + 1)


def build_gold_z(ordinal: int) -> dict[str, Any]:
    if ordinal < 0:
        raise ValueError("scene ordinal must be non-negative")

    conflict_present = ordinal % 2 == 0
    relation_modifier = _RELATION_MODIFIERS[(ordinal // 2) % len(_RELATION_MODIFIERS)]
    quantifier = _QUANTIFIER_SLOTS[ordinal % len(_QUANTIFIER_SLOTS)]
    temporal = _TEMPORAL_SLOTS[(ordinal + 2) % len(_TEMPORAL_SLOTS)]
    fallback = _FALLBACK_SLOTS[(ordinal + 1) % len(_FALLBACK_SLOTS)]
    uncertainty = _UNCERTAINTY_SLOTS[(ordinal + 2) % len(_UNCERTAINTY_SLOTS)]

    evidence_scope, asserted_scope = _scope_pair(ordinal)
    scope_relation = _scope_relation(evidence_scope, asserted_scope)
    claim_operational = (ordinal // 2) % 2 == 0

    z1_names: list[str] = []
    if conflict_present:
        z1_names.append("CONFLICT_EXISTS")
    if relation_modifier is not None:
        z1_names.append(relation_modifier)
    for name in (quantifier, temporal, fallback, uncertainty):
        if name is not None:
            z1_names.append(name)
    z1_names.append(f"{SCOPES[asserted_scope]}_SCOPE")
    if claim_operational:
        z1_names.append("OPERATIONAL_SIGNAL")
    z1 = [int(name in z1_names) for name in Z1_LABELS]

    comparator_name = {
        "EXACT_THRESHOLD": "EXACT",
        "LOWER_BOUND_THRESHOLD": "LOWER_BOUND",
        "UPPER_BOUND_THRESHOLD": "UPPER_BOUND",
    }.get(quantifier, "NONE")
    temporal_precision_name = {
        "EXACT_DURATION": "EXACT",
        "EXPIRY_RULE": "EXACT",
        "APPROX_DURATION": "APPROX",
    }.get(temporal, "NONE")

    value = scalar_permutation_value(ordinal)
    scalars = [0.0, 0.0, 0.0, 0.0]
    scalar_mask = [0, 0, 0, 0]
    if quantifier in {"EXACT_THRESHOLD", "LOWER_BOUND_THRESHOLD", "UPPER_BOUND_THRESHOLD"}:
        scalars[0], scalar_mask[0] = value, 1
    if quantifier == "ORDINAL_TRIGGER":
        scalars[1], scalar_mask[1] = value, 1
    if temporal in {"EXACT_DURATION", "APPROX_DURATION", "EXPIRY_RULE"}:
        scalars[2], scalar_mask[2] = value, 1
    if temporal == "PERIODIC_RULE":
        scalars[3], scalar_mask[3] = value, 1

    resolution_present = relation_modifier in {
        "EXPLICIT_SUPERSESSION",
        "IMPLICIT_SELECTION",
        "CORRECTION",
    }
    numeric_value_asserted = quantifier in {
        "EXACT_THRESHOLD",
        "LOWER_BOUND_THRESHOLD",
        "UPPER_BOUND_THRESHOLD",
    }
    temporal_rule_asserted = temporal in {
        "EXACT_DURATION",
        "APPROX_DURATION",
        "PERIODIC_RULE",
        "EXPIRY_RULE",
    }
    fallback_asserted = fallback is not None

    z4 = [
        int(conflict_present),
        int(resolution_present and _support_bit(ordinal, 1)),
        int(_scope_supported(evidence_scope, asserted_scope)),
        int((not numeric_value_asserted) or _support_bit(ordinal, 2)),
        int((not temporal_rule_asserted) or _support_bit(ordinal, 3)),
        int((not fallback_asserted) or _support_bit(ordinal, 4)),
        int((not claim_operational) or _support_bit(ordinal, 5)),
    ]

    if not any(scalar_mask):
        raise AssertionError("Amendment 003 requires at least one present scalar per scene")

    return {
        "z1": z1,
        "z2_comparator": COMPARATORS.index(comparator_name),
        "z2_temporal_precision": TEMPORAL_PRECISIONS.index(temporal_precision_name),
        "z2_scalars": scalars,
        "z2_scalar_mask": scalar_mask,
        "z3_evidence_scope": evidence_scope,
        "z3_asserted_scope": asserted_scope,
        "z3_scope_relation": scope_relation,
        "z4": z4,
    }


def _semantic_sentences(gold_z: dict[str, Any]) -> list[str]:
    z1 = {name: bool(value) for name, value in zip(Z1_LABELS, gold_z["z1"])}
    phrases = {
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
    sentences = [phrases[name] for name in phrases if z1.get(name, False)]
    comparator = COMPARATORS[gold_z["z2_comparator"]]
    scalar_values = gold_z["z2_scalars"]
    scalar_mask = gold_z["z2_scalar_mask"]
    if scalar_mask[0]:
        wording = {
            "EXACT": "The numeric cutoff is exactly",
            "LOWER_BOUND": "The numeric cutoff is at least",
            "UPPER_BOUND": "The numeric cutoff is at most",
        }[comparator]
        sentences.append(f"{wording} {scalar_values[0]:g}.")
    if scalar_mask[1]:
        sentences.append(f"The ordinal trigger is position {int(scalar_values[1])}.")
    if scalar_mask[2]:
        precision = TEMPORAL_PRECISIONS[gold_z["z2_temporal_precision"]]
        prefix = "approximately " if precision == "APPROX" else ""
        sentences.append(f"The stated duration is {prefix}{scalar_values[2]:g} seconds.")
    if scalar_mask[3]:
        sentences.append(f"The recurring interval is {scalar_values[3]:g} seconds.")
    return sentences


def _support_sentences(gold_z: dict[str, Any]) -> list[str]:
    values = [bool(v) for v in gold_z["z4"]]
    return [
        "The evidence itself contains an explicit contradiction." if values[0] else "The evidence itself contains no explicit contradiction.",
        "The evidence establishes the claimed replacement relation." if values[1] else "The evidence does not establish a replacement relation.",
        "The evidence is sufficient for the claimed scope." if values[2] else "The evidence does not justify the claimed scope.",
        "The evidence directly supports the stated numeric quantity." if values[3] else "The evidence does not directly support a numeric quantity.",
        "The evidence directly supports the stated timing rule." if values[4] else "The evidence does not directly support a timing rule.",
        "The evidence directly supports the stated fallback behavior." if values[5] else "The evidence does not directly support a fallback behavior.",
        "The evidence directly supports the actionable signal." if values[6] else "The evidence does not directly support an actionable signal.",
    ]


def render_surface(scene: CanonicalScene, family: str) -> str:
    if family == RENDERER_TRAIN_A:
        return (
            f"Assertion: {scene.assertion}\nEvidence: {scene.evidence}\n"
            f"Boundary: {scene.applicability_boundary}\nRevision: {scene.revision_trigger}"
        )
    if family == RENDERER_TRAIN_B:
        return (
            f"Current statement — {scene.assertion} Observed record — {scene.evidence} "
            f"Use boundary — {scene.applicability_boundary} Reconsideration rule — {scene.revision_trigger}"
        )
    if family == RENDERER_HELDOUT_C:
        return (
            f"Proposition under review: {scene.assertion}\nAvailable observation: {scene.evidence}\n"
            f"Extent of applicability: {scene.applicability_boundary}\n"
            f"Condition for revision: {scene.revision_trigger}"
        )
    raise ValueError(f"unknown renderer family: {family}")


def build_scene_from_ordinal(ordinal: int, *, scene_id: str, split: str) -> CanonicalScene:
    gold_z = build_gold_z(ordinal)
    gold_c = recompose_gold_z(gold_z)
    asserted = SCOPES[gold_z["z3_asserted_scope"]].lower()
    evidence_scope = SCOPES[gold_z["z3_evidence_scope"]].lower()
    semantic = " ".join(_semantic_sentences(gold_z))
    support = " ".join(_support_sentences(gold_z))
    assertion = f"This proposition applies at {asserted} scope. {semantic}"
    evidence_text = f"The current observation is limited to {evidence_scope} scope. {support}"
    applicability_boundary = f"Apply the proposition only at {asserted} scope."
    revision_trigger = "Reconsider it only after materially new current evidence appears."
    scene = CanonicalScene(
        scene_id,
        split,
        assertion,
        evidence_text,
        applicability_boundary,
        revision_trigger,
        gold_z,
        gold_c,
    )
    if not canonical_equal(scene.gold_c, recompose_gold_z(scene.gold_z)):
        raise AssertionError("gold C must equal R(gold Z)")
    return scene


def build_scientific_scene(scene_id: int) -> CanonicalScene:
    split = split_for_scientific_scene_id(scene_id)
    return build_scene_from_ordinal(
        scientific_ordinal(scene_id),
        scene_id=str(scene_id),
        split=split,
    )


def build_fixture_scene(ordinal: int) -> CanonicalScene:
    return build_scene_from_ordinal(
        ordinal,
        scene_id=f"fixture-{ordinal:04d}",
        split="FIXTURE",
    )


def surfaces_for_scene(scene: CanonicalScene) -> list[SurfaceRecord]:
    families = (
        (RENDERER_TRAIN_A, RENDERER_HELDOUT_C)
        if scene.split == "PRISTINE_CONFIRMATORY"
        else (RENDERER_TRAIN_A, RENDERER_TRAIN_B)
    )
    return [
        SurfaceRecord(
            scene_id=scene.scene_id,
            split=scene.split,
            renderer_family=family,
            input_text=render_surface(scene, family),
            pit_evidence={"observations": [scene.evidence]},
            pit_teaching_signal={
                "inference": scene.assertion,
                "applicability_boundary": scene.applicability_boundary,
                "revision_trigger": scene.revision_trigger,
            },
            gold_z=scene.gold_z,
            gold_c=scene.gold_c,
        )
        for family in families
    ]


def iter_scientific_split(split: str) -> Iterable[SurfaceRecord]:
    ranges = {
        "TRAIN": TRAIN_SCENE_RANGE,
        "VALIDATION": VALIDATION_SCENE_RANGE,
        "PRISTINE_CONFIRMATORY": CONFIRMATORY_SCENE_RANGE,
    }
    if split not in ranges:
        raise ValueError("unknown scientific split")
    for scene_id in ranges[split]:
        yield from surfaces_for_scene(build_scientific_scene(scene_id))


def materialize_scientific_split(split: str, output_path: str | Path) -> dict[str, Any]:
    """Explicit later-stage materializer. Calling this is scientifically gated outside this module."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    scene_ids: set[str] = set()
    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        for record in iter_scientific_split(split):
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
            count += 1
            scene_ids.add(record.scene_id)
    return {
        "split": split,
        "surface_records": count,
        "canonical_scenes": len(scene_ids),
        "path": str(destination),
    }
