"""One plain decoder-only Transformer language model."""

from __future__ import annotations

import torch
from torch import nn

from .config import ModelConfig


class TransformerLM(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.position_embedding = nn.Embedding(config.max_context, config.d_model)
        self.layers = nn.ModuleList(
            nn.TransformerEncoderLayer(
                d_model=config.d_model,
                nhead=config.n_heads,
                dim_feedforward=config.ff_mult * config.d_model,
                dropout=config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            for _ in range(config.n_layers)
        )
        self.norm = nn.LayerNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight

    @property
    def context_limit(self) -> int:
        return self.config.max_context

    @property
    def vocab_size(self) -> int:
        return self.config.vocab_size

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        if tokens.ndim != 2:
            raise ValueError("tokens must have shape [batch, context]")
        _, context = tokens.shape
        if context <= 0:
            raise ValueError("context cannot be empty")
        if context > self.config.max_context:
            raise ValueError(f"context {context} exceeds max_context {self.config.max_context}")
        if tokens.numel() and (int(tokens.min()) < 0 or int(tokens.max()) >= self.config.vocab_size):
            raise ValueError("token ID is outside model vocabulary")
        positions = torch.arange(context, device=tokens.device)
        hidden = self.token_embedding(tokens) + self.position_embedding(positions)[None, :, :]
        mask = torch.triu(torch.ones(context, context, dtype=torch.bool, device=tokens.device), diagonal=1)
        for layer in self.layers:
            hidden = layer(hidden, src_mask=mask, is_causal=True)
        return self.lm_head(self.norm(hidden))


def create_model(config: ModelConfig) -> TransformerLM:
    """Construct the single proven learned model implementation.

    This is deliberately a plain function, not a registry/provider system.
    """
    return TransformerLM(config)


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())
