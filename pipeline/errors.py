"""Typed error hierarchy for M0 contract compilation."""


class PipelineError(Exception):
    """Base class for expected pipeline failures."""

    code = "PIPELINE_ERROR"


class ConfigLoadError(PipelineError):
    code = "CONFIG_LOAD_ERROR"


class SchemaValidationError(PipelineError):
    code = "SCHEMA_VALIDATION_ERROR"


class SemanticValidationError(PipelineError):
    code = "SEMANTIC_VALIDATION_ERROR"


class FreshnessViolation(PipelineError):
    code = "FRESHNESS_VIOLATION"


class StateTransitionError(PipelineError):
    code = "STATE_TRANSITION_ERROR"


class PreflightIOError(PipelineError):
    code = "PREFLIGHT_IO_ERROR"


class DataPlaneError(PipelineError):
    code = "DATA_PLANE_ERROR"


class DataIntegrityError(DataPlaneError):
    code = "DATA_INTEGRITY_ERROR"


class DataPolicyError(DataPlaneError):
    code = "DATA_POLICY_ERROR"


class GovernanceError(PipelineError):
    code = "GOVERNANCE_ERROR"


class ExecutionLockViolation(GovernanceError):
    code = "EXECUTION_LOCK_VIOLATION"


class EvaluationEvidenceError(GovernanceError):
    code = "EVALUATION_EVIDENCE_ERROR"


class AdjudicationTerminalError(GovernanceError):
    code = "ADJUDICATION_TERMINAL"


class ReasoningLayerError(PipelineError):
    code = "REASONING_LAYER_ERROR"


class ReasoningSerializationError(ReasoningLayerError):
    code = "REASONING_SERIALIZATION_ERROR"


class ReasoningParseError(ReasoningLayerError):
    code = "REASONING_PARSE_ERROR"


class UnsupportedReasoningMode(ReasoningLayerError):
    code = "UNSUPPORTED_REASONING_MODE"
