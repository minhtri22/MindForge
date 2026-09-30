"""Minimal PyTorch runtime-facing learned-model contract v0.

The contract intentionally exposes only behavior already required by current
MindForge evaluation/generation paths. It excludes Transformer internals,
training/optimizer semantics, checkpoint format, PPF, hosts, plugins, and
speculative capability enums.

This is a bounded PyTorch v0 contract for current proven runtime consumers,
not a universal permanent model ABI. See docs/research/model-contract-adr.md.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import torch


@runtime_checkable
class TokenModel(Protocol):
    """Smallest proven PyTorch runtime contract for current token-LM use cases."""

    @property
    def context_limit(self) -> int: ...

    @property
    def training(self) -> bool: ...

    def __call__(self, tokens: torch.Tensor) -> torch.Tensor: ...

    def train(self, mode: bool = True) -> "TokenModel": ...

    def eval(self) -> "TokenModel": ...
