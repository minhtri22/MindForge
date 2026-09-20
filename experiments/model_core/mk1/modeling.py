"""B0-DIRECT and M1-Z wrappers under the frozen MK-1 contract."""

from __future__ import annotations

import copy
import hashlib
import random
from typing import Literal

import numpy as np
import torch
from torch import nn

from mindforge.config import ModelConfig
from mindforge.model import TransformerLM, create_model
from .contracts import D_C, D_Z


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if hasattr(torch, "xpu") and torch.xpu.is_available() and hasattr(torch.xpu, "manual_seed_all"):
        torch.xpu.manual_seed_all(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def state_dict_sha256(state: dict[str, torch.Tensor]) -> str:
    h = hashlib.sha256()
    for name in sorted(state):
        tensor = state[name].detach().cpu().contiguous()
        h.update(name.encode("utf-8"))
        h.update(str(tensor.dtype).encode("ascii"))
        h.update(str(tuple(tensor.shape)).encode("ascii"))
        h.update(tensor.numpy().tobytes())
    return h.hexdigest()


def parameter_count(module: nn.Module) -> int:
    return sum(p.numel() for p in module.parameters())


def pool_final_hidden(backbone: TransformerLM, input_ids: torch.Tensor) -> torch.Tensor:
    if input_ids.ndim != 2 or input_ids.size(1) < 1:
        raise ValueError("input_ids must be non-empty [batch,time]")
    return backbone.hidden_states(input_ids)[:, -1, :]


class _RepresentationArm(nn.Module):
    def __init__(self, backbone: TransformerLM, output_dim: int) -> None:
        super().__init__()
        self.backbone = backbone
        self.readout = nn.Linear(backbone.config.d_model, output_dim, bias=True)
        nn.init.zeros_(self.readout.weight)
        nn.init.zeros_(self.readout.bias)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        return self.readout(pool_final_hidden(self.backbone, input_ids))


class B0DirectArm(_RepresentationArm):
    def __init__(self, backbone: TransformerLM) -> None:
        super().__init__(backbone, D_C)


class M1ZArm(_RepresentationArm):
    def __init__(self, backbone: TransformerLM) -> None:
        super().__init__(backbone, D_Z)


def frozen_backbone_state(seed: int, config: ModelConfig | None = None) -> dict[str, torch.Tensor]:
    set_seed(seed)
    model = create_model(config or ModelConfig())
    return copy.deepcopy(model.state_dict())


def build_arm(arm: Literal["direct", "m1z"], backbone_state: dict[str, torch.Tensor], config: ModelConfig | None = None) -> nn.Module:
    backbone = create_model(config or ModelConfig())
    backbone.load_state_dict(backbone_state, strict=True)
    if arm == "direct":
        return B0DirectArm(backbone)
    if arm == "m1z":
        return M1ZArm(backbone)
    raise ValueError(f"unknown arm: {arm}")
