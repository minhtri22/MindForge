"""MindForge compact local language-model kernel."""

from .config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from .model import TransformerLM, parameter_count

__all__ = [
    "DataConfig",
    "KernelConfig",
    "ModelConfig",
    "TrainingConfig",
    "TransformerLM",
    "parameter_count",
]

__version__ = "0.1.0"
