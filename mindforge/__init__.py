"""MindForge compact local language-model research package."""

from .config import DataConfig, KernelConfig, ModelConfig, RunConfig, TrainingConfig
from .model import TransformerLM, create_model, parameter_count
from .model_contract import TokenModel

__all__ = [
    "DataConfig",
    "KernelConfig",
    "ModelConfig",
    "RunConfig",
    "TrainingConfig",
    "TokenModel",
    "TransformerLM",
    "create_model",
    "parameter_count",
]

__version__ = "0.1.0"
