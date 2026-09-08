"""
M3 OIR-PPV Pipeline Package
Interfaces for Invariant Extraction, Manifestation Generation, and Evaluation.
"""

from .invariant_extractor import (
    InvariantExtractor,
    InvariantExtractionResult,
    PlaceholderInvariantExtractor,
    OIRInvariantExtractor
)

from .generator import (
    ManifestationGenerator,
    GenerationResult,
    PlaceholderManifestationGenerator,
    OIRManifestationGenerator,
    PipelineRunner
)

from .evaluation import (
    InvariantEvaluator,
    GenerationEvaluator,
    PipelineEvaluator,
    InvariantMetrics,
    GenerationMetrics,
    PipelineEvaluationResult
)

from .learners import (
    LearnerRegistry,
    create_learner_from_config,
    EncoderLearner,
    PredictorLearner,
    DecoderLearner,
    PCAEncoder,
    MLPEncoder,
    AutoencoderEncoder,
    LogisticPredictor,
    LinearDecoder,
    MLPDecoder
)

__all__ = [
    "InvariantExtractor",
    "InvariantExtractionResult", 
    "PlaceholderInvariantExtractor",
    "OIRInvariantExtractor",
    "ManifestationGenerator",
    "GenerationResult",
    "PlaceholderManifestationGenerator",
    "OIRManifestationGenerator",
    "PipelineRunner",
    "InvariantEvaluator",
    "GenerationEvaluator",
    "PipelineEvaluator",
    "InvariantMetrics",
    "GenerationMetrics",
    "PipelineEvaluationResult",
    "LearnerRegistry",
    "create_learner_from_config",
    "EncoderLearner",
    "PredictorLearner",
    "DecoderLearner",
    "PCAEncoder",
    "MLPEncoder",
    "AutoencoderEncoder",
    "LogisticPredictor",
    "LinearDecoder",
    "MLPDecoder",
    "AutoencoderEncoder",
]

# Pipeline stages for reference
PIPELINE_STAGES = [
    "Experience (S,A,Y,Z,N)",
    "Invariant Extractor -> I",
    "Generator G(I,Z,N) -> Manifestation",
    "Intervention Engine",
    "Counterfactual Evaluator"
]