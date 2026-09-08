"""
Benchmark package init.
"""

from .core import (
    BenchmarkConfig,
    BenchmarkResult,
    BaseBaseline,
    BenchmarkRunner,
    run_baseline_experiment
)

from .metrics import (
    GeneralizationMetrics,
    InterventionStabilityMetrics,
    GenerationQualityMetrics,
    compute_generalization_metrics,
    compute_intervention_stability,
    compute_generation_quality,
    aggregate_metrics
)

from .baselines import (
    B0_ERM,
    B1_DomainGeneralization,
    B2_EncoderRepresentation,
    B3_InvariantOnly,
    B4_OIR_PPV,
    B5_OracleInvariant,
    BASELINE_MAP
)

__all__ = [
    # Core
    "BenchmarkConfig",
    "BenchmarkResult", 
    "BaseBaseline",
    "BenchmarkRunner",
    "run_baseline_experiment",
    # Metrics
    "GeneralizationMetrics",
    "InterventionStabilityMetrics",
    "GenerationQualityMetrics",
    "compute_generalization_metrics",
    "compute_intervention_stability",
    "compute_generation_quality",
    "aggregate_metrics",
    # Baselines
    "B0_ERM",
    "B1_DomainGeneralization",
    "B2_EncoderRepresentation",
    "B3_InvariantOnly",
    "B4_OIR_PPV",
    "B5_OracleInvariant",
    "BASELINE_MAP",
]