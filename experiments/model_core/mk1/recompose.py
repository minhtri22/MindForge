"""Frozen deterministic Z -> canonical C recomposition for MK-1."""

from __future__ import annotations

from typing import Any

import torch

from .contracts import C1_FIELDS, C5_FIELDS, Z1_LABELS, Z4_FIELDS, Z_SLICES

_Z1 = {name: i for i, name in enumerate(Z1_LABELS)}
_Z4 = {name: i for i, name in enumerate(Z4_FIELDS)}


def _binary_from_logits(values: torch.Tensor) -> torch.Tensor:
    return values >= 0


def decode_z_logits(logits: torch.Tensor) -> dict[str, torch.Tensor]:
    if logits.ndim != 2 or logits.size(1) != 70:
        raise ValueError("M1-Z logits must have shape [batch,70]")
    return {
        "z1": _binary_from_logits(logits[:, Z_SLICES["z1"]]),
        "z2_comparator": torch.argmax(logits[:, Z_SLICES["z2_comparator"]], dim=1),
        "z2_temporal_precision": torch.argmax(logits[:, Z_SLICES["z2_temporal_precision"]], dim=1),
        "z2_scalars": logits[:, Z_SLICES["z2_scalars"]],
        "z3_evidence_scope": torch.argmax(logits[:, Z_SLICES["z3_evidence_scope"]], dim=1),
        "z3_asserted_scope": torch.argmax(logits[:, Z_SLICES["z3_asserted_scope"]], dim=1),
        "z3_scope_relation": torch.argmax(logits[:, Z_SLICES["z3_scope_relation"]], dim=1),
        "z4": _binary_from_logits(logits[:, Z_SLICES["z4"]]),
    }


def recompose_decoded_z(decoded: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    z1 = decoded["z1"].bool()
    z4 = decoded["z4"].bool()
    conflict = z4[:, _Z4["conflict_present"]]
    resolution = (
        z1[:, _Z1["EXPLICIT_SUPERSESSION"]]
        | z1[:, _Z1["IMPLICIT_SELECTION"]]
        | z1[:, _Z1["CORRECTION"]]
    )
    numeric = (
        z1[:, _Z1["EXACT_THRESHOLD"]]
        | z1[:, _Z1["LOWER_BOUND_THRESHOLD"]]
        | z1[:, _Z1["UPPER_BOUND_THRESHOLD"]]
    )
    temporal = (
        z1[:, _Z1["EXACT_DURATION"]]
        | z1[:, _Z1["APPROX_DURATION"]]
        | z1[:, _Z1["PERIODIC_RULE"]]
        | z1[:, _Z1["EXPIRY_RULE"]]
    )
    fallback = (
        z1[:, _Z1["FALLBACK_IF_UNKNOWN"]]
        | z1[:, _Z1["FALLBACK_IF_CONFLICT"]]
        | z1[:, _Z1["FALLBACK_IF_UNAVAILABLE"]]
    )
    c1 = torch.stack(
        [
            conflict,
            conflict & resolution,
            numeric,
            temporal,
            fallback,
            z1[:, _Z1["ABSTAINS"]],
            z1[:, _Z1["REQUESTS_CLARIFICATION"]],
            z1[:, _Z1["OPERATIONAL_SIGNAL"]],
        ],
        dim=1,
    )
    c5 = torch.stack(
        [z4[:, _Z4[name]] for name in C5_FIELDS],
        dim=1,
    )
    return {
        "c1": c1,
        "c2": decoded["z3_evidence_scope"].long(),
        "c3": decoded["z3_asserted_scope"].long(),
        "c4": decoded["z3_scope_relation"].long(),
        "c5": c5,
    }


def recompose_logits(logits: torch.Tensor) -> dict[str, torch.Tensor]:
    return recompose_decoded_z(decode_z_logits(logits))


def recompose_gold_z(gold_z: dict[str, Any]) -> dict[str, Any]:
    z1_values = list(gold_z["z1"])
    z4_values = list(gold_z["z4"])
    if len(z1_values) != len(Z1_LABELS) or len(z4_values) != len(Z4_FIELDS):
        raise ValueError("gold Z dimensions do not match frozen contract")
    z1 = {name: bool(z1_values[i]) for i, name in enumerate(Z1_LABELS)}
    z4 = {name: bool(z4_values[i]) for i, name in enumerate(Z4_FIELDS)}
    conflict = z4["conflict_present"]
    resolution = z1["EXPLICIT_SUPERSESSION"] or z1["IMPLICIT_SELECTION"] or z1["CORRECTION"]
    numeric = z1["EXACT_THRESHOLD"] or z1["LOWER_BOUND_THRESHOLD"] or z1["UPPER_BOUND_THRESHOLD"]
    temporal = z1["EXACT_DURATION"] or z1["APPROX_DURATION"] or z1["PERIODIC_RULE"] or z1["EXPIRY_RULE"]
    fallback = z1["FALLBACK_IF_UNKNOWN"] or z1["FALLBACK_IF_CONFLICT"] or z1["FALLBACK_IF_UNAVAILABLE"]
    c1 = [
        conflict, conflict and resolution, numeric, temporal, fallback,
        z1["ABSTAINS"], z1["REQUESTS_CLARIFICATION"], z1["OPERATIONAL_SIGNAL"],
    ]
    return {
        "c1": [int(v) for v in c1],
        "c2": int(gold_z["z3_evidence_scope"]),
        "c3": int(gold_z["z3_asserted_scope"]),
        "c4": int(gold_z["z3_scope_relation"]),
        "c5": [int(z4[name]) for name in C5_FIELDS],
    }


def canonical_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(left[key] == right[key] for key in ("c1", "c2", "c3", "c4", "c5"))

assert tuple(C1_FIELDS) == (
    "evidence_has_conflict", "resolves_conflict", "asserts_numeric_threshold", "asserts_temporal_rule",
    "asserts_fallback_policy", "abstains", "requests_clarification", "has_operational_signal",
)
