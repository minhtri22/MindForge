"""M3 execution-lock and evaluation-contract compilation/verification."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .baseline import BaselineRegistry
from .canonical import sha256_file, sha256_object
from .errors import ExecutionLockViolation
from .io import atomic_write_json, atomic_write_text
from .loader import load_model_profile, validate_mapping
from .models import ExperimentConfig

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def build_evaluation_contract(
    config: ExperimentConfig,
    baseline_registry: BaselineRegistry,
    repo_root: Path,
) -> dict[str, Any]:
    fixture_manifest = _fixture_manifest_path(config.fixture_set, repo_root)
    metrics = []
    for metric in config.metrics:
        metrics.append(
            {
                "metric_id": metric.metric_id,
                "metric_version": metric.metric_version,
                "target_artifact": metric.target_artifact,
                "baseline_id": metric.baseline_id,
                "comparison_type": metric.comparison_type,
                "operator": metric.operator,
                "threshold": metric.threshold,
                "aggregation": dict(metric.aggregation),
                "required": metric.required,
                "missing_data_policy": metric.missing_data_policy,
            }
        )
    contract = {
        "fixture_set_id": config.fixture_set,
        "fixture_set_hash": sha256_file(fixture_manifest),
        "baseline_registry_hash": baseline_registry.sha256,
        "metrics": metrics,
        "inference_contract": dict(config.inference),
    }
    _validate_schema(
        contract,
        repo_root / "docs/model-training-pipeline/schemas/evaluation_contract.schema.json",
        "EvaluationContract",
    )
    return contract


def build_execution_contract(
    *,
    config: ExperimentConfig,
    repo_root: Path,
    run_id: str,
    frozen_config_hash: str,
    data_manifest_hash: str,
    baseline_registry: BaselineRegistry,
    evaluation_contract: dict[str, Any],
) -> dict[str, Any]:
    source_sha = source_git_sha(repo_root)
    profile = load_model_profile(config, repo_root)
    phase_rows = []
    raw_phases = {row["id"]: row for row in config.raw["phases"]}
    previous_identity = sha256_object(
        {"model_id": config.model.id, "revision": config.model.revision}
    )
    for phase in config.phases:
        raw = raw_phases[phase.id]
        phase_config_hash = sha256_object(raw)
        phase_rows.append(
            {
                "phase_id": phase.id,
                "parent_artifact_hash": previous_identity,
                "phase_config_hash": phase_config_hash,
                "token_stream_hash": sha256_object(raw["token_stream"]),
                "checkpoint_selection_hash": sha256_object(raw["checkpoint_selection"]),
                "phase_resource_hash": sha256_object(
                    {
                        "backend": "fixture-cpu",
                        "device_class": "cpu",
                        "device_count": 1,
                        "world_size": 1,
                        "precision": raw["training"]["precision"],
                    }
                ),
            }
        )
        # M3 does not execute training. This deterministic fixture identity means
        # "the selected output of this locked phase" for governance plumbing only.
        previous_identity = sha256_object(
            {
                "qualification_phase": phase.id,
                "phase_config_hash": phase_config_hash,
                "parent_artifact_hash": previous_identity,
            }
        )

    contract = {
        "run_id": run_id,
        "run_class": config.run_class.value,
        "software_git_sha": source_sha,
        "frozen_config_hash": frozen_config_hash,
        "data_manifest_hash": data_manifest_hash,
        "model_profile_hash": sha256_object(profile),
        "baseline_registry_hash": baseline_registry.sha256,
        "evaluation_contract_hash": sha256_object(evaluation_contract),
        "inference_contract_hash": sha256_object(config.inference),
        "resolved_model_revision": config.model.revision,
        "phases": phase_rows,
        "freshness_registry": {
            "seed_ids": sorted(config.seed_sets.get("fresh_confirmatory", ())),
            "split_ids": [],
            "fixture_set_ids": [],
        },
        "toolchain": {
            "trainer": {
                "m2_qualified_commit": "ca8e880d64aac081ddd659396241ee4798a7bc81",
                "mode": "m3_fixture_governance_no_training",
            },
            "llama_cpp": {"status": "not_invoked_in_m3"},
            "ollama": {"status": "not_invoked_in_m3"},
        },
        "resource_contract": {
            "backend": "fixture-governance",
            "device_class": "cpu",
            "device_count": 1,
            "world_size": 1,
        },
        "retry_policy": {
            "infra_retry": "exact_committed_state_only",
            "invalid_run_repair": "terminal_invalid_new_run_new_contract",
            "scientific_retry": "forbidden_without_new_contract",
        },
    }
    _validate_schema(
        contract,
        repo_root / "docs/model-training-pipeline/schemas/execution_contract.schema.json",
        "ExecutionContract",
    )
    return contract


def write_execution_lock(
    lock_dir: Path,
    repo_root: Path,
    execution_contract: dict[str, Any],
    evaluation_contract: dict[str, Any],
) -> dict[str, str]:
    lock_dir.mkdir(parents=True, exist_ok=False)
    execution_hash = sha256_object(execution_contract)
    evaluation_hash = sha256_object(evaluation_contract)
    if execution_contract["evaluation_contract_hash"] != evaluation_hash:
        raise ExecutionLockViolation("execution contract does not bind the provided evaluation contract")

    atomic_write_json(lock_dir / "evaluation_contract.json", evaluation_contract)
    atomic_write_text(lock_dir / "evaluation_contract.sha256", evaluation_hash + "\n")
    atomic_write_json(lock_dir / "execution_contract.json", execution_contract)
    atomic_write_text(lock_dir / "execution_contract.sha256", execution_hash + "\n")
    marker = {
        "state": "EXECUTION_LOCKED",
        "execution_contract_hash": execution_hash,
        "evaluation_contract_hash": evaluation_hash,
        "software_git_sha": execution_contract["software_git_sha"],
    }
    atomic_write_json(lock_dir / "EXECUTION_LOCKED.json", marker)
    verify_execution_lock(lock_dir, repo_root)
    return {
        "execution_contract_hash": execution_hash,
        "evaluation_contract_hash": evaluation_hash,
    }


def verify_execution_lock(lock_dir: Path, repo_root: Path) -> dict[str, Any]:
    required = [
        "execution_contract.json",
        "execution_contract.sha256",
        "evaluation_contract.json",
        "evaluation_contract.sha256",
        "EXECUTION_LOCKED.json",
    ]
    missing = [name for name in required if not (lock_dir / name).is_file()]
    if missing:
        raise ExecutionLockViolation(f"execution lock incomplete: missing {missing}")

    execution = _read_object(lock_dir / "execution_contract.json")
    evaluation = _read_object(lock_dir / "evaluation_contract.json")
    marker = _read_object(lock_dir / "EXECUTION_LOCKED.json")
    _validate_schema(
        execution,
        repo_root / "docs/model-training-pipeline/schemas/execution_contract.schema.json",
        "ExecutionContract",
    )
    _validate_schema(
        evaluation,
        repo_root / "docs/model-training-pipeline/schemas/evaluation_contract.schema.json",
        "EvaluationContract",
    )

    actual_execution = sha256_object(execution)
    actual_evaluation = sha256_object(evaluation)
    expected_execution = (lock_dir / "execution_contract.sha256").read_text(encoding="utf-8").strip()
    expected_evaluation = (lock_dir / "evaluation_contract.sha256").read_text(encoding="utf-8").strip()

    if actual_execution != expected_execution:
        raise ExecutionLockViolation("execution contract mutated after lock")
    if actual_evaluation != expected_evaluation:
        raise ExecutionLockViolation("evaluation contract mutated after lock")
    if execution["evaluation_contract_hash"] != actual_evaluation:
        raise ExecutionLockViolation("execution contract evaluation hash binding mismatch")
    if execution["inference_contract_hash"] != sha256_object(evaluation["inference_contract"]):
        raise ExecutionLockViolation("inference contract binding mismatch")
    if marker.get("state") != "EXECUTION_LOCKED":
        raise ExecutionLockViolation("execution lock marker state mismatch")
    if marker.get("execution_contract_hash") != actual_execution:
        raise ExecutionLockViolation("execution lock marker execution hash mismatch")
    if marker.get("evaluation_contract_hash") != actual_evaluation:
        raise ExecutionLockViolation("execution lock marker evaluation hash mismatch")

    return {
        "execution_contract": execution,
        "evaluation_contract": evaluation,
        "execution_contract_hash": actual_execution,
        "evaluation_contract_hash": actual_evaluation,
    }


def source_git_sha(repo_root: Path) -> str:
    explicit = os.environ.get("GITHUB_SHA") or os.environ.get("PIPELINE_SOURCE_SHA")
    if explicit and _SHA40.fullmatch(explicit):
        return explicit
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    value = completed.stdout.strip()
    if not _SHA40.fullmatch(value):
        raise ExecutionLockViolation(f"invalid Git SHA: {value!r}")
    return value


def _fixture_manifest_path(fixture_set: str, repo_root: Path) -> Path:
    path = repo_root / fixture_set
    manifest = path / "manifest.json" if path.is_dir() else path
    if not manifest.is_file():
        raise ExecutionLockViolation(f"fixture manifest missing: {fixture_set}")
    return manifest


def _validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = _read_object(schema_path)
    Draft202012Validator.check_schema(schema)
    validate_mapping(value, schema, label)


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExecutionLockViolation(f"expected JSON object: {path}")
    return value
