"""Zero-training contract compiler for the evidence-governed model pipeline."""

from .models import ExperimentConfig, PhaseSpec, RunClass, RunState, PhaseState
from .preflight import PreflightResult, run_preflight

__all__ = [
    "ExperimentConfig",
    "PhaseSpec",
    "RunClass",
    "RunState",
    "PhaseState",
    "PreflightResult",
    "run_preflight",
]

__version__ = "0.1.0-m0"
