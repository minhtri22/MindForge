"""M3 Governance / Evaluation Foundation qualification."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .baseline import BaselineRegistry
from .canonical import sha256_object
from .errors import (
    AdjudicationTerminalError,
    EvaluationEvidenceError,
    ExecutionLockViolation,
    FreshnessViolation,
    GovernanceError,
)
from .freshness import FreshnessRegistry
from .io import atomic_write_json
from .loader import load_experiment_config
from .m1 import run_m1_qualification
from .m3_adjudicator import adjudicate_once, validate_observation_context
from .m3_contracts import (
    build_evaluation_contract,
    build_execution_contract,
    verify_execution_lock,
    write_execution_lock,
)
from .models import RunClass
from .resolver import ResolverContext


@dataclass(frozen=True)
class M3Result:
    status: str
    run_id: str
    run_dir: Path
    pass_verdict: str
    fail_verdict: str
    pass_adjudication_hash: str
    fail_adjudication_hash: str
    execution_lock_hash: str
    evaluation_contract_hash: str
    gates_passed: int
    gates_total: int
    training_started: bool
    public_bulk_download_started: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "pass_verdict": self.pass_verdict,
            "fail_verdict": self.fail_verdict,
            "pass_adjudication_hash": self.pass_adjudication_hash,
            "fail_adjudication_hash": self.fail_adjudication_hash,
            "execution_lock_hash": self.execution_lock_hash,
            "evaluation_contract_hash": self.evaluation_contract_hash,
            "gates_passed": self.gates_passed,
            "gates_total": self.gates_total,
            "training_started": self.training_started,
            "public_bulk_download_started": self.public_bulk_download_started,
        }


def run_m3_qualification(
    config_path: str | Path,
    repo_root: str | Path = ".",
    runs_root: str | Path = "runs",
    *,
    context: ResolverContext | None = None,
) -> M3Result:
    repo_root = Path(repo_root).resolve()
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = repo_root / config_path

    m1 = run_m1_qualification(config_path, repo_root, runs_root, context=context)
    config = load_experiment_config(config_path, repo_root)
    if config.run_class not in {RunClass.SMOKE, RunClass.DEVELOPMENT, RunClass.CALIBRATION}:
        raise GovernanceError("M3 qualification fixture must not consume confirmatory/release resources")

    preflight_result = _read_object(m1.run_dir / "preflight_result.json")
    baseline_registry = BaselineRegistry.compile(config)
    evaluation_contract = build_evaluation_contract(config, baseline_registry, repo_root)
    m3_root = m1.run_dir / "m3"
    if m3_root.exists():
        # Qualification is intentionally non-retriable inside one run directory.
        raise AdjudicationTerminalError(f"M3 qualification already exists: {m3_root}")
    m3_root.mkdir(parents=True)

    pass_observation = repo_root / "tests/fixtures/m3_eval_v1/pass_observation.json"
    fail_observation = repo_root / "tests/fixtures/m3_eval_v1/fail_observation.json"

    pass_result, pass_lock = _run_scenario(
        scenario_id="pass",
        observation_path=pass_observation,
        scenario_dir=m3_root / "pass",
        config=config,
        repo_root=repo_root,
        frozen_config_hash=preflight_result["config_hash"],
        data_manifest_hash=m1.data_manifest_hash,
        baseline_registry=baseline_registry,
        evaluation_contract=evaluation_contract,
    )
    fail_result, fail_lock = _run_scenario(
        scenario_id="intentional-fail",
        observation_path=fail_observation,
        scenario_dir=m3_root / "intentional-fail",
        config=config,
        repo_root=repo_root,
        frozen_config_hash=preflight_result["config_hash"],
        data_manifest_hash=m1.data_manifest_hash,
        baseline_registry=baseline_registry,
        evaluation_contract=evaluation_contract,
    )

    probes = {
        "threshold_mutation_blocked": _probe_threshold_mutation(
            m3_root / "probes/threshold-mutation",
            config,
            repo_root,
            preflight_result["config_hash"],
            m1.data_manifest_hash,
            baseline_registry,
            evaluation_contract,
        ),
        "seed_replacement_blocked": _probe_seed_replacement(
            pass_observation, config, baseline_registry, evaluation_contract
        ),
        "matched_control_mutation_blocked": _probe_matched_control_mutation(
            pass_observation, config, baseline_registry, evaluation_contract
        ),
        "retry_until_pass_blocked": _probe_retry_after_fail(
            scenario_dir=m3_root / "intentional-fail",
            lock_dir=m3_root / "intentional-fail/lock",
            pass_observation=pass_observation,
            repo_root=repo_root,
            config=config,
            baseline_registry=baseline_registry,
        ),
        "fresh_resource_access_blocked": _probe_fresh_resource_guard(),
    }
    atomic_write_json(m3_root / "adversarial_probes.json", probes)

    root_parent = next(
        (entry for entry in baseline_registry.entries if entry["id"] == "root_parent"),
        None,
    )
    matched_control = next(
        (entry for entry in baseline_registry.entries if entry["id"] == "matched_control_fixture"),
        None,
    )
    gates = {
        "m1_prerequisite": m1.status == "PASS",
        "execution_lock_valid": bool(pass_lock["execution_contract_hash"])
        and bool(fail_lock["execution_contract_hash"]),
        "evaluation_contract_valid": pass_lock["evaluation_contract_hash"]
        == fail_lock["evaluation_contract_hash"],
        "exact_parent_baseline_bound": bool(root_parent)
        and root_parent["role"] == "parent_baseline"
        and config.model.revision in root_parent["reference"],
        "matched_control_bound": bool(matched_control)
        and matched_control["role"] == "matched_control"
        and matched_control["contract"]["parent_baseline"] == "root_parent",
        "phase_and_final_metrics": pass_result["phase_verdicts"].get("domain_cpt") == "PASS"
        and pass_result["phase_verdicts"].get("reasoning_sft") == "PASS"
        and pass_result["verdict"] == "PASS"
        and fail_result["phase_verdicts"].get("domain_cpt") == "PASS"
        and fail_result["phase_verdicts"].get("reasoning_sft") == "FAIL",
        "pass_fixture_passes": pass_result["verdict"] == "PASS"
        and pass_result["run_state"] == "ADJUDICATED_PASS",
        "intentional_scientific_fail_is_terminal_fail": fail_result["verdict"] == "FAIL"
        and fail_result["run_state"] == "ADJUDICATED_FAIL",
        "scientific_retry_forbidden": pass_result["retry_policy"]["scientific_retry"]
        == "forbidden_without_new_contract"
        and fail_result["retry_policy"]["scientific_retry"]
        == "forbidden_without_new_contract",
        **probes,
        "fixture_scale_no_training": True,
    }
    failed = [name for name, passed in gates.items() if not passed]
    qualification = {
        "schema": "mindforge-model-pipeline-m3-qualification-v1",
        "run_id": m1.run_id,
        "gates": {name: {"required": True, "pass": bool(value)} for name, value in gates.items()},
        "failed_required_gates": failed,
        "pass_adjudication_hash": pass_result["adjudication_hash"],
        "fail_adjudication_hash": fail_result["adjudication_hash"],
        "shared_evaluation_contract_hash": pass_lock["evaluation_contract_hash"],
        "verdict": "PASS" if not failed else "FAIL",
    }
    qualification_hash = sha256_object(qualification)
    atomic_write_json(
        m3_root / "m3_qualification.json",
        {**qualification, "qualification_hash": qualification_hash},
    )
    if failed:
        raise GovernanceError(f"M3 qualification failed required gates: {failed}")

    result = M3Result(
        status="PASS",
        run_id=m1.run_id,
        run_dir=m1.run_dir,
        pass_verdict=pass_result["verdict"],
        fail_verdict=fail_result["verdict"],
        pass_adjudication_hash=pass_result["adjudication_hash"],
        fail_adjudication_hash=fail_result["adjudication_hash"],
        execution_lock_hash=pass_lock["execution_contract_hash"],
        evaluation_contract_hash=pass_lock["evaluation_contract_hash"],
        gates_passed=len(gates),
        gates_total=len(gates),
        training_started=False,
        public_bulk_download_started=False,
    )
    atomic_write_json(m3_root / "m3_result.json", result.to_dict())
    return result


def _run_scenario(
    *,
    scenario_id: str,
    observation_path: Path,
    scenario_dir: Path,
    config,
    repo_root: Path,
    frozen_config_hash: str,
    data_manifest_hash: str,
    baseline_registry: BaselineRegistry,
    evaluation_contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    scenario_dir.mkdir(parents=True, exist_ok=False)
    execution_contract = build_execution_contract(
        config=config,
        repo_root=repo_root,
        run_id=f"{config.experiment_id}-{scenario_id}",
        frozen_config_hash=frozen_config_hash,
        data_manifest_hash=data_manifest_hash,
        baseline_registry=baseline_registry,
        evaluation_contract=evaluation_contract,
    )
    lock_info = write_execution_lock(
        scenario_dir / "lock",
        repo_root,
        execution_contract,
        evaluation_contract,
    )
    result = adjudicate_once(
        scenario_dir=scenario_dir,
        lock_dir=scenario_dir / "lock",
        observation_path=observation_path,
        repo_root=repo_root,
        config=config,
        baseline_registry=baseline_registry,
    )
    return result, lock_info


def _probe_threshold_mutation(
    probe_dir: Path,
    config,
    repo_root: Path,
    frozen_config_hash: str,
    data_manifest_hash: str,
    baseline_registry: BaselineRegistry,
    evaluation_contract: dict[str, Any],
) -> bool:
    probe_dir.mkdir(parents=True, exist_ok=False)
    execution = build_execution_contract(
        config=config,
        repo_root=repo_root,
        run_id=f"{config.experiment_id}-threshold-mutation-probe",
        frozen_config_hash=frozen_config_hash,
        data_manifest_hash=data_manifest_hash,
        baseline_registry=baseline_registry,
        evaluation_contract=evaluation_contract,
    )
    lock_dir = probe_dir / "lock"
    write_execution_lock(lock_dir, repo_root, execution, evaluation_contract)
    mutated = _read_object(lock_dir / "evaluation_contract.json")
    mutated["metrics"][0]["threshold"] = float(mutated["metrics"][0]["threshold"]) + 1.0
    atomic_write_json(lock_dir / "evaluation_contract.json", mutated)
    try:
        verify_execution_lock(lock_dir, repo_root)
    except ExecutionLockViolation:
        return True
    return False


def _probe_seed_replacement(
    observation_path: Path,
    config,
    baseline_registry: BaselineRegistry,
    evaluation_contract: dict[str, Any],
) -> bool:
    observation = _read_object(observation_path)
    observation["seed_id"] = 12
    observation["matched_control"]["seed_id"] = 12
    try:
        validate_observation_context(
            observation=observation,
            config=config,
            baseline_registry=baseline_registry,
            evaluation=evaluation_contract,
        )
    except EvaluationEvidenceError:
        return True
    return False


def _probe_matched_control_mutation(
    observation_path: Path,
    config,
    baseline_registry: BaselineRegistry,
    evaluation_contract: dict[str, Any],
) -> bool:
    observation = _read_object(observation_path)
    observation["matched_control"]["token_budget"] += 1
    try:
        validate_observation_context(
            observation=observation,
            config=config,
            baseline_registry=baseline_registry,
            evaluation=evaluation_contract,
        )
    except EvaluationEvidenceError:
        return True
    return False


def _probe_retry_after_fail(
    *,
    scenario_dir: Path,
    lock_dir: Path,
    pass_observation: Path,
    repo_root: Path,
    config,
    baseline_registry: BaselineRegistry,
) -> bool:
    try:
        adjudicate_once(
            scenario_dir=scenario_dir,
            lock_dir=lock_dir,
            observation_path=pass_observation,
            repo_root=repo_root,
            config=config,
            baseline_registry=baseline_registry,
        )
    except AdjudicationTerminalError:
        return True
    return False


def _probe_fresh_resource_guard() -> bool:
    registry = FreshnessRegistry(
        seed_ids=frozenset({999}),
        dataset_ids=frozenset({"fresh-fixture-data"}),
        fixture_set_ids=frozenset({"tests/fixtures/fresh-hidden"}),
    )
    try:
        registry.assert_access(RunClass.DEVELOPMENT, "seed", 999)
    except FreshnessViolation:
        return True
    return False


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GovernanceError(f"expected JSON object: {path}")
    return value
