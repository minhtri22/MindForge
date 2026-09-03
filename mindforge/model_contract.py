"""Minimal runtime-facing learned-model contract.

The contract intentionally exposes only behavior already required by current
MindForge evaluation/generation paths. It excludes Transformer internals,
training/optimizer semantics, checkpoint format, PPF, hosts, plugins, and
speculative capability enums.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import torch


@runtime_checkable
class TokenModel(Protocol):
    """Smallest proven runtime contract for the current token LM use cases."""

    @property
    def context_limit(self) -> int: ...

    @property
    def vocab_size(self) -> int: ...

    @property
    def training(self) -> bool: ...

    def __call__(self, tokens: torch.Tensor) -> torch.Tensor: ...

    def train(self, mode: bool = True) -> "TokenModel": ...

    def eval(self) -> "TokenModel": ...
