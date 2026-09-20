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
