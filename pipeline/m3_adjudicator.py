"""M3 deterministic evaluator and one-shot adjudicator."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .baseline import BaselineRegistry
from .canonical import sha256_file, sha256_object
from .errors import (
    AdjudicationTerminalError,
    EvaluationEvidenceError,
)
from .io import atomic_write_json
from .m3_contracts import verify_execution_lock
from .models import ExperimentConfig, RunState
from .state import RunMachine


def adjudicate_once(
    *,
    scenario_dir: Path,
    lock_dir: Path,
    observation_path: Path,
    repo_root: Path,
    config: ExperimentConfig,
    baseline_registry: BaselineRegistry,
) -> dict[str, Any]:
    terminal_path = scenario_dir / "adjudication.json"
    if terminal_path.exists():
        raise AdjudicationTerminalError(
            f"run already terminally adjudicated: {terminal_path}"
        )

    locked = verify_execution_lock(lock_dir, repo_root)
    execution = locked["execution_contract"]
    evaluation = locked["evaluation_contract"]
    if execution["baseline_registry_hash"] != baseline_registry.sha256:
        raise EvaluationEvidenceError("baseline registry differs from execution lock")
    if evaluation["baseline_registry_hash"] != baseline_registry.sha256:
        raise EvaluationEvidenceError("evaluation contract baseline registry mismatch")

    observation = _read_object(observation_path)
    _validate_observation_context(
        observation=observation,
        config=config,
        baseline_registry=baseline_registry,
        evaluation=evaluation,
    )

    metric_results: list[dict[str, Any]] = []
    invalid_reasons: list[str] = []
    for contract in evaluation["metrics"]:
        result = _evaluate_metric(contract, observation)
        metric_results.append(result)
        if result["status"] == "INVALID":
            invalid_reasons.append(f"{result['metric_id']}: {result['reason']}")

    required = [item for item in metric_results if item["required"]]
    if invalid_reasons:
        verdict = "INVALID"
    elif all(item["status"] == "PASS" for item in required):
        verdict = "PASS"
    else:
        verdict = "FAIL"

    phase_verdicts: dict[str, str] = {}
    for item in metric_results:
        target = item["target_artifact"]
        if not target.startswith("phase:"):
            continue
        phase_id = target.removeprefix("phase:")
        current = phase_verdicts.get(phase_id, "PASS")
        if item["status"] == "INVALID":
            phase_verdicts[phase_id] = "INVALID"
        elif item["required"] and item["status"] == "FAIL" and current != "INVALID":
            phase_verdicts[phase_id] = "FAIL"
        else:
            phase_verdicts.setdefault(phase_id, "PASS")

    machine = RunMachine()
    machine.advance(RunState.PREPARED)
    machine.advance(RunState.PREFLIGHT_PASS)
    machine.advance(RunState.EXECUTION_LOCKED)
    machine.advance(RunState.RUNNING)
    machine.advance(RunState.EVALUATED)
    if verdict == "PASS":
        machine.advance(RunState.ADJUDICATED_PASS)
    elif verdict == "FAIL":
        machine.advance(RunState.ADJUDICATED_FAIL)
    else:
        machine.advance(RunState.INVALID)

    result = {
        "schema": "mindforge-model-pipeline-m3-adjudication-v1",
        "run_id": execution["run_id"],
        "scenario_id": observation.get("scenario_id"),
        "execution_contract_hash": locked["execution_contract_hash"],
        "evaluation_contract_hash": locked["evaluation_contract_hash"],
        "observation_hash": sha256_file(observation_path),
        "seed_id": observation["seed_id"],
        "metric_results": metric_results,
        "phase_verdicts": phase_verdicts,
        "final_metrics": {
            "required_count": len(required),
            "required_pass": sum(item["status"] == "PASS" for item in required),
            "required_fail": sum(item["status"] == "FAIL" for item in required),
            "invalid_count": sum(item["status"] == "INVALID" for item in metric_results),
        },
        "invalid_reasons": invalid_reasons,
        "verdict": verdict,
        "run_state": machine.state.value,
        "retry_policy": execution["retry_policy"],
    }
    result["adjudication_hash"] = sha256_object(result)
    scenario_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(terminal_path, result)
    return result


def validate_observation_context(
    *,
    observation: dict[str, Any],
    config: ExperimentConfig,
    baseline_registry: BaselineRegistry,
    evaluation: dict[str, Any],
) -> None:
    _validate_observation_context(
        observation=observation,
        config=config,
        baseline_registry=baseline_registry,
        evaluation=evaluation,
    )


def _validate_observation_context(
    *,
    observation: dict[str, Any],
    config: ExperimentConfig,
    baseline_registry: BaselineRegistry,
    evaluation: dict[str, Any],
) -> None:
    if observation.get("schema") != "m3-observation-v1":
        raise EvaluationEvidenceError("unsupported M3 observation schema")
    seed_id = observation.get("seed_id")
    if not isinstance(seed_id, int):
        raise EvaluationEvidenceError("observation seed_id must be integer")
    if seed_id in set(config.seed_sets.get("fresh_confirmatory", ())):
        raise EvaluationEvidenceError("development M3 observation attempted fresh-confirmatory seed access")
    development = set(config.seed_sets.get("development", ()))
    calibration = set(config.seed_sets.get("calibration", ()))
    allowed = development | calibration
    if seed_id not in allowed:
        raise EvaluationEvidenceError(
            f"observation seed {seed_id} is not frozen in the development/calibration seed contract"
        )
    if seed_id != int(evaluation["inference_contract"]["seed"]):
        raise EvaluationEvidenceError("observation seed does not match frozen inference seed")

    metrics = observation.get("metrics")
    if not isinstance(metrics, dict):
        raise EvaluationEvidenceError("observation metrics must be an object")

    matched = observation.get("matched_control")
    if not isinstance(matched, dict):
        raise EvaluationEvidenceError("matched_control evidence is required")
    baseline_id = matched.get("baseline_id")
    registry_entry = next(
        (entry for entry in baseline_registry.entries if entry["id"] == baseline_id),
        None,
    )
    if registry_entry is None or registry_entry["role"] != "matched_control":
        raise EvaluationEvidenceError("matched control baseline is not registered")

    contract = registry_entry["contract"]
    expected = {
        "baseline_id": registry_entry["id"],
        "seed_id": seed_id,
        "token_budget": contract["token_budget"],
        "resource_class": contract["resource_class"],
        "parent_baseline": contract["parent_baseline"],
        "matched_to": contract["matched_to"],
        "intervention": contract["intervention"],
    }
    if matched != expected:
        raise EvaluationEvidenceError(
            f"matched control evidence differs from frozen contract: expected={expected} actual={matched}"
        )
    if seed_id not in set(contract["seeds"]):
        raise EvaluationEvidenceError("matched control seed is not frozen in baseline contract")

    parent_id = contract["parent_baseline"]
    parent_entry = next(
        (entry for entry in baseline_registry.entries if entry["id"] == parent_id),
        None,
    )
    if parent_entry is None or parent_entry["role"] != "parent_baseline":
        raise EvaluationEvidenceError("matched control parent baseline is not an exact parent baseline")


def _evaluate_metric(contract: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    metric_id = contract["metric_id"]
    metric_obs = observation["metrics"].get(metric_id)
    if not isinstance(metric_obs, dict):
        return _missing_metric_result(contract)

    target = metric_obs.get("target")
    baseline_values = metric_obs.get("baselines")
    if not isinstance(target, (int, float)) or not isinstance(baseline_values, dict):
        return _invalid_metric_result(contract, "malformed metric observation")
    baseline = baseline_values.get(contract["baseline_id"])
    if not isinstance(baseline, (int, float)):
        return _missing_metric_result(contract)

    comparison_type = contract["comparison_type"]
    try:
        value = _comparison_value(comparison_type, float(target), float(baseline))
    except (ValueError, ZeroDivisionError) as error:
        return _invalid_metric_result(contract, str(error))
    if not math.isfinite(value):
        return _invalid_metric_result(contract, "comparison result is non-finite")

    passed = _compare(value, contract["operator"], float(contract["threshold"]))
    return {
        "metric_id": metric_id,
        "metric_version": contract["metric_version"],
        "target_artifact": contract["target_artifact"],
        "baseline_id": contract["baseline_id"],
        "comparison_type": comparison_type,
        "operator": contract["operator"],
        "threshold": contract["threshold"],
        "target_value": float(target),
        "baseline_value": float(baseline),
        "comparison_value": value,
        "required": bool(contract["required"]),
        "status": "PASS" if passed else "FAIL",
        "reason": None,
    }


def _missing_metric_result(contract: dict[str, Any]) -> dict[str, Any]:
    policy = contract["missing_data_policy"]
    if policy == "invalid":
        status = "INVALID"
    elif policy == "ignore_optional" and not contract["required"]:
        status = "SKIPPED"
    else:
        status = "FAIL"
    return {
        "metric_id": contract["metric_id"],
        "metric_version": contract["metric_version"],
        "target_artifact": contract["target_artifact"],
        "baseline_id": contract["baseline_id"],
        "comparison_type": contract["comparison_type"],
        "operator": contract["operator"],
        "threshold": contract["threshold"],
        "target_value": None,
        "baseline_value": None,
        "comparison_value": None,
        "required": bool(contract["required"]),
        "status": status,
        "reason": "required metric/baseline observation missing",
    }


def _invalid_metric_result(contract: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "metric_id": contract["metric_id"],
        "metric_version": contract["metric_version"],
        "target_artifact": contract["target_artifact"],
        "baseline_id": contract["baseline_id"],
        "comparison_type": contract["comparison_type"],
        "operator": contract["operator"],
        "threshold": contract["threshold"],
        "target_value": None,
        "baseline_value": None,
        "comparison_value": None,
        "required": bool(contract["required"]),
        "status": "INVALID",
        "reason": reason,
    }


def _comparison_value(kind: str, target: float, baseline: float) -> float:
    if kind == "absolute_value":
        return target
    if kind == "absolute_delta":
        return target - baseline
    if kind == "relative_delta":
        if baseline == 0:
            raise ZeroDivisionError("relative_delta baseline is zero")
        return (target - baseline) / abs(baseline)
    if kind == "ratio":
        if baseline == 0:
            raise ZeroDivisionError("ratio baseline is zero")
        return target / baseline
    if kind == "distribution_test":
        raise ValueError("distribution_test is not implemented by the M3 fixture evaluator")
    raise ValueError(f"unsupported comparison_type {kind}")


def _compare(value: float, operator: str, threshold: float) -> bool:
    if operator == ">":
        return value > threshold
    if operator == ">=":
        return value >= threshold
    if operator == "<":
        return value < threshold
    if operator == "<=":
        return value <= threshold
    if operator == "==":
        return value == threshold
    raise ValueError(f"unsupported operator {operator}")


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvaluationEvidenceError(f"expected JSON object: {path}")
    return value
