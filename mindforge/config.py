"""Small serializable configuration objects for MindForge research/tooling."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeVar


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 16_384
    d_model: int = 320
    n_heads: int = 8
    n_layers: int = 4
    max_context: int = 512
    ff_mult: int = 4
    dropout: float = 0.0

    def __post_init__(self) -> None:
        for name in ("vocab_size", "d_model", "n_heads", "n_layers", "max_context", "ff_mult"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.d_model % self.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")


@dataclass(frozen=True)
class TrainingConfig:
    steps: int = 1_000
    micro_batch: int = 1
    accumulation: int = 2
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    gradient_clip: float = 1.0
    warmup_fraction: float = 0.05
    min_lr_fraction: float = 0.1
    eval_interval: int = 100
    checkpoint_interval: int = 500
    eval_windows: int = 24
    seed: int = 2026
    device: str = "auto"
    dtype: str = "auto"

    def __post_init__(self) -> None:
        for name in ("steps", "micro_batch", "accumulation", "eval_interval", "checkpoint_interval", "eval_windows"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.learning_rate <= 0 or self.weight_decay < 0 or self.gradient_clip <= 0:
            raise ValueError("learning_rate and gradient_clip must be positive; weight_decay cannot be negative")
        if not 0.0 <= self.warmup_fraction < 1.0:
            raise ValueError("warmup_fraction must be in [0, 1)")
        if not 0.0 < self.min_lr_fraction <= 1.0:
            raise ValueError("min_lr_fraction must be in (0, 1]")
        if self.device not in {"auto", "cpu", "xpu", "cuda"}:
            raise ValueError("device must be auto, cpu, xpu, or cuda")
        if self.dtype not in {"auto", "float32", "bfloat16"}:
            raise ValueError("dtype must be auto, float32, or bfloat16")


@dataclass(frozen=True)
class DataConfig:
    train_tokens: str
    validation_tokens: str
    tokenizer: str
    run_dir: str = "runs/default"

    def __post_init__(self) -> None:
        for name in ("train_tokens", "validation_tokens", "tokenizer", "run_dir"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} cannot be empty")


@dataclass(frozen=True)
class RunConfig:
    """Research/tooling composition, not a kernel-runtime ownership boundary."""

    data: DataConfig
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RunConfig":
        if not isinstance(value, dict) or "data" not in value:
            raise ValueError("config must be an object containing data")
        allowed = {"data", "model", "training"}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown config fields: {sorted(unknown)}")
        return cls(
            data=_construct(DataConfig, value["data"]),
            model=_construct(ModelConfig, value.get("model", {})),
            training=_construct(TrainingConfig, value.get("training", {})),
        )

    @classmethod
    def load(cls, path: str | Path) -> "RunConfig":
        try:
            value = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot load config {path}: {error}") from error
        return cls.from_dict(value)


@dataclass(frozen=True)
class KernelConfig(RunConfig):
    """Backward-compatible Phase-1/Phase-2 name for the research run config."""


T = TypeVar("T")


def _construct(kind: type[T], value: Any) -> T:
    if not isinstance(value, dict):
        raise ValueError(f"{kind.__name__} must be an object")
    try:
        return kind(**value)
    except TypeError as error:
        raise ValueError(f"invalid {kind.__name__}: {error}") from error
