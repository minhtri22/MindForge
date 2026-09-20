"""Cross-field semantic graph validation beyond JSON Schema."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from .errors import SemanticValidationError
from .models import ExperimentConfig, RunClass


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_INTRINSIC_CHECKPOINT_METRICS = {"validation_loss", "train_loss"}


def validate_semantics(config: ExperimentConfig, profile: Mapping[str, Any], repo_root: Path) -> None:
    errors: list[str] = []
    phase_ids = [phase.id for phase in config.phases]
    if len(phase_ids) != len(set(phase_ids)):
        errors.append("phase ids must be unique")

    seen: set[str] = set()
    for index, phase in enumerate(config.phases):
        for dataset_id in phase.datasets:
            if dataset_id not in config.datasets:
                errors.append(f"phase {phase.id} references unknown dataset {dataset_id}")
        if phase.parent_ref == "model":
            if index != 0:
                errors.append(f"only root phase may use parent_ref=model: {phase.id}")
        elif phase.parent_ref.startswith("phase:"):
            parent = phase.parent_ref.removeprefix("phase:")
            if parent not in seen:
                errors.append(f"phase {phase.id} parent must reference an earlier phase: {parent}")
        elif not phase.parent_ref.startswith("artifact:"):
            errors.append(f"phase {phase.id} has unsupported parent_ref {phase.parent_ref}")
        seen.add(phase.id)

        selection = phase.checkpoint_selection
        if selection.rule in {"metric_best", "early_stopping"}:
            if not selection.metric_id:
                errors.append(f"phase {phase.id} requires checkpoint metric_id")
            elif selection.metric_id not in _INTRINSIC_CHECKPOINT_METRICS:
                known = {metric.metric_id for metric in config.metrics}
                if selection.metric_id not in known:
                    errors.append(
                        f"phase {phase.id} checkpoint metric {selection.metric_id} is neither intrinsic nor declared"
                    )

    baseline_ids = [baseline.id for baseline in config.baselines]
    if len(baseline_ids) != len(set(baseline_ids)):
        errors.append("baseline ids must be unique")
    baseline_set = set(baseline_ids)
    for metric in config.metrics:
        if metric.baseline_id not in baseline_set:
            errors.append(f"metric {metric.metric_id} references unknown baseline {metric.baseline_id}")
    for baseline in config.baselines:
        raw = baseline.raw
        if baseline.source == "phase_parent" and raw.get("phase_id") not in phase_ids:
            errors.append(f"baseline {baseline.id} references unknown phase {raw.get('phase_id')}")
        if baseline.role == "matched_control":
            if raw.get("parent_baseline") not in baseline_set:
                errors.append(f"matched control {baseline.id} has unknown parent_baseline")
            if raw.get("matched_to") not in baseline_set:
                errors.append(f"matched control {baseline.id} has unknown matched_to")

    if config.model.require_resolved_sha and not _SHA40.fullmatch(config.model.revision):
        errors.append("model revision must be an immutable 40-hex SHA before preflight")
    if profile.get("model_id") != config.model.id:
        errors.append("model profile model_id does not match config.model.id")
    if profile.get("revision") != config.model.revision:
        errors.append("model profile revision does not match config.model.revision")

    _validate_local_dataset_paths(config, repo_root, errors)
    fixture_freshness = _validate_fixture(config.fixture_set, repo_root, errors)
    if config.run_class not in {RunClass.CONFIRMATORY, RunClass.RELEASE}:
        active_fresh = [name for name, ds in config.datasets.items() if ds.freshness_class == "fresh_confirmatory"]
        if active_fresh:
            errors.append(f"{config.run_class.value} config actively references fresh datasets: {active_fresh}")
        if fixture_freshness == "fresh_confirmatory":
            errors.append(f"{config.run_class.value} config actively references fresh fixture set")

    if errors:
        raise SemanticValidationError("; ".join(errors))


def _validate_local_dataset_paths(config: ExperimentConfig, repo_root: Path, errors: list[str]) -> None:
    for name, dataset in config.datasets.items():
        path = dataset.raw.get("path")
        if path is not None and not (repo_root / str(path)).is_file():
            errors.append(f"dataset {name} local path does not exist: {path}")


def _validate_fixture(fixture_set: str, repo_root: Path, errors: list[str]) -> str | None:
    if not fixture_set.startswith("tests/"):
        return None
    path = repo_root / fixture_set
    manifest = path / "manifest.json" if path.is_dir() else path
    if not manifest.is_file():
        errors.append(f"evaluation fixture manifest does not exist: {fixture_set}")
        return None
    try:
        raw = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"evaluation fixture manifest unreadable: {fixture_set}: {error}")
        return None
    return raw.get("freshness_class")
