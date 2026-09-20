"""Frozen MK-1 direct and structured representation losses."""

from __future__ import annotations

from collections.abc import Mapping

import torch
from torch.nn import functional as F

from .contracts import C_SLICES, D_C, D_Z, Z_SLICES


def _require_shape(logits: torch.Tensor, width: int) -> None:
    if logits.ndim != 2 or logits.size(1) != width:
        raise ValueError(f"logits must have shape [batch,{width}]")


def direct_loss(logits: torch.Tensor, target: Mapping[str, torch.Tensor]) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    _require_shape(logits, D_C)
    pieces = {
        "c1": F.binary_cross_entropy_with_logits(logits[:, C_SLICES["c1"]], target["c1"].float()),
        "c2": F.cross_entropy(logits[:, C_SLICES["c2"]], target["c2"].long()),
        "c3": F.cross_entropy(logits[:, C_SLICES["c3"]], target["c3"].long()),
        "c4": F.cross_entropy(logits[:, C_SLICES["c4"]], target["c4"].long()),
        "c5": F.binary_cross_entropy_with_logits(logits[:, C_SLICES["c5"]], target["c5"].float()),
    }
    total = torch.stack(tuple(pieces.values())).mean()
    return total, pieces


def m1z_loss(logits: torch.Tensor, target: Mapping[str, torch.Tensor]) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    _require_shape(logits, D_Z)
    z1 = F.binary_cross_entropy_with_logits(logits[:, Z_SLICES["z1"]], target["z1"].float())
    comparator = F.cross_entropy(logits[:, Z_SLICES["z2_comparator"]], target["z2_comparator"].long())
    temporal_precision = F.cross_entropy(
        logits[:, Z_SLICES["z2_temporal_precision"]], target["z2_temporal_precision"].long()
    )
    scalar_logits = logits[:, Z_SLICES["z2_scalars"]]
    scalar_gold = target["z2_scalars"].float()
    scalar_mask = target["z2_scalar_mask"].bool()
    z2_components = [comparator, temporal_precision]
    scalar_components: list[torch.Tensor] = []
    for index in range(4):
        mask = scalar_mask[:, index]
        if bool(mask.any()):
            gold = scalar_gold[mask, index]
            pred = scalar_logits[mask, index]
            scale = torch.maximum(gold.abs(), torch.ones_like(gold))
            error = (pred - gold) / scale
            component = F.smooth_l1_loss(error, torch.zeros_like(error), beta=1.0)
            z2_components.append(component)
            scalar_components.append(component)
    z2 = torch.stack(z2_components).mean()
    z3_parts = [
        F.cross_entropy(logits[:, Z_SLICES["z3_evidence_scope"]], target["z3_evidence_scope"].long()),
        F.cross_entropy(logits[:, Z_SLICES["z3_asserted_scope"]], target["z3_asserted_scope"].long()),
        F.cross_entropy(logits[:, Z_SLICES["z3_scope_relation"]], target["z3_scope_relation"].long()),
    ]
    z3 = torch.stack(z3_parts).mean()
    z4 = F.binary_cross_entropy_with_logits(logits[:, Z_SLICES["z4"]], target["z4"].float())
    total = torch.stack((z1, z2, z3, z4)).mean()
    pieces = {"z1": z1, "z2": z2, "z3": z3, "z4": z4}
    for i, value in enumerate(scalar_components):
        pieces[f"z2_scalar_active_{i}"] = value
    return total, pieces
