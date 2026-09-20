"""YAML/JSON Schema loader for ExperimentConfig and ModelProfile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator

from .errors import ConfigLoadError, SchemaValidationError
from .models import ExperimentConfig


EXPERIMENT_SCHEMA = Path("docs/model-training-pipeline/schemas/experiment_config.schema.json")
MODEL_PROFILE_SCHEMA = Path("docs/model-training-pipeline/schemas/model_profile.schema.json")


def _read_yaml(path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ConfigLoadError(f"cannot load YAML {path}: {error}") from error
    if not isinstance(value, dict):
        raise ConfigLoadError(f"YAML root must be an object: {path}")
    return value


def _read_schema(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigLoadError(f"cannot load JSON Schema {path}: {error}") from error
    if not isinstance(value, dict):
        raise ConfigLoadError(f"schema root must be an object: {path}")
    Draft202012Validator.check_schema(value)
    return value


def _format_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"{path}: {error.message}"


def validate_mapping(value: Mapping[str, Any], schema: Mapping[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        detail = "; ".join(_format_error(error) for error in errors[:20])
        raise SchemaValidationError(f"{label} failed schema validation: {detail}")


def load_experiment_config(config_path: Path, repo_root: Path) -> ExperimentConfig:
    raw = _read_yaml(config_path)
    schema = _read_schema(repo_root / EXPERIMENT_SCHEMA)
    validate_mapping(raw, schema, "ExperimentConfig")
    return ExperimentConfig.from_mapping(raw)


def load_model_profile(config: ExperimentConfig, repo_root: Path) -> Mapping[str, Any]:
    profile_path = repo_root / "docs/model-training-pipeline" / config.model.profile
    if not profile_path.exists():
        raise ConfigLoadError(f"model profile does not exist: {profile_path}")
    raw = _read_yaml(profile_path)
    schema = _read_schema(repo_root / MODEL_PROFILE_SCHEMA)
    validate_mapping(raw, schema, "ModelProfile")
    return raw
