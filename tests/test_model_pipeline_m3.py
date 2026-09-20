from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pipeline.baseline import BaselineRegistry
from pipeline.errors import (
    AdjudicationTerminalError,
    EvaluationEvidenceError,
    ExecutionLockViolation,
)
from pipeline.loader import load_experiment_config, load_model_profile
from pipeline.m1 import run_m1_qualification
from pipeline.m3 import run_m3_qualification
from pipeline.m3_adjudicator import adjudicate_once, validate_observation_context
from pipeline.m3_contracts import (
    build_evaluation_contract,
    build_execution_contract,
    verify_execution_lock,
    write_execution_lock,
)
from pipeline.resolver import ResolverContext
from pipeline.semantic import validate_semantics
from pipeline.io import atomic_write_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "docs/model-training-pipeline/examples/m3_governance_fixture.yaml"
PASS_OBS = ROOT / "tests/fixtures/m3_eval_v1/pass_observation.json"
FAIL_OBS = ROOT / "tests/fixtures/m3_eval_v1/fail_observation.json"


@pytest.fixture(scope="module")
def foundation(tmp_path_factory):
    runs_root = tmp_path_factory.mktemp("m3-foundation")
    context = ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32")
    m1 = run_m1_qualification(CONFIG, ROOT, runs_root, context=context)
    config = load_experiment_config(CONFIG, ROOT)
    baseline = BaselineRegistry.compile(config)
    evaluation = build_evaluation_contract(config, baseline, ROOT)
    preflight = json.loads((m1.run_dir / "preflight_result.json").read_text(encoding="utf-8"))
    return {
        "m1": m1,
        "config": config,
        "baseline": baseline,
        "evaluation": evaluation,
        "config_hash": preflight["config_hash"],
    }


def _execution(foundation, run_id: str):
    return build_execution_contract(
        config=foundation["config"],
        repo_root=ROOT,
        run_id=run_id,
        frozen_config_hash=foundation["config_hash"],
        data_manifest_hash=foundation["m1"].data_manifest_hash,
        baseline_registry=foundation["baseline"],
        evaluation_contract=foundation["evaluation"],
    )


def test_m3_fixture_config_schema_and_semantics():
    config = load_experiment_config(CONFIG, ROOT)
    profile = load_model_profile(config, ROOT)
    validate_semantics(config, profile, ROOT)
    assert {baseline.id for baseline in config.baselines} == {"root_parent", "matched_control_fixture"}
    assert len(config.metrics) == 3


def test_evaluation_contract_binds_parent_matched_control_and_inference(foundation):
    evaluation = foundation["evaluation"]
    assert evaluation["baseline_registry_hash"] == foundation["baseline"].sha256
    assert evaluation["inference_contract"]["seed"] == 11
    assert [metric["metric_id"] for metric in evaluation["metrics"]] == [
        "domain_retention",
        "answer_accuracy",
        "protected_accuracy",
    ]


def test_execution_lock_roundtrip_and_hash_binding(foundation, tmp_path: Path):
    execution = _execution(foundation, "m3-lock-roundtrip")
    info = write_execution_lock(tmp_path / "lock", ROOT, execution, foundation["evaluation"])
    verified = verify_execution_lock(tmp_path / "lock", ROOT)
    assert verified["execution_contract_hash"] == info["execution_contract_hash"]
    assert verified["evaluation_contract_hash"] == info["evaluation_contract_hash"]
    assert verified["execution_contract"]["retry_policy"]["scientific_retry"] == "forbidden_without_new_contract"


def test_threshold_mutation_after_lock_is_rejected(foundation, tmp_path: Path):
    execution = _execution(foundation, "m3-threshold-mutation")
    lock = tmp_path / "lock"
    write_execution_lock(lock, ROOT, execution, foundation["evaluation"])
    evaluation = json.loads((lock / "evaluation_contract.json").read_text(encoding="utf-8"))
    evaluation["metrics"][0]["threshold"] += 1.0
    atomic_write_json(lock / "evaluation_contract.json", evaluation)
    with pytest.raises(ExecutionLockViolation, match="mutated after lock"):
        verify_execution_lock(lock, ROOT)


def test_seed_replacement_is_rejected(foundation):
    observation = json.loads(PASS_OBS.read_text(encoding="utf-8"))
    observation["seed_id"] = 12
    observation["matched_control"]["seed_id"] = 12
    with pytest.raises(EvaluationEvidenceError, match="not frozen"):
        validate_observation_context(
            observation=observation,
            config=foundation["config"],
            baseline_registry=foundation["baseline"],
            evaluation=foundation["evaluation"],
        )


def test_matched_control_budget_mutation_is_rejected(foundation):
    observation = json.loads(PASS_OBS.read_text(encoding="utf-8"))
    observation["matched_control"]["token_budget"] = 41
    with pytest.raises(EvaluationEvidenceError, match="differs from frozen contract"):
        validate_observation_context(
            observation=observation,
            config=foundation["config"],
            baseline_registry=foundation["baseline"],
            evaluation=foundation["evaluation"],
        )


def test_pass_case_is_adjudicated_pass_with_phase_metrics(foundation, tmp_path: Path):
    execution = _execution(foundation, "m3-pass-unit")
    lock = tmp_path / "lock"
    scenario = tmp_path / "scenario"
    write_execution_lock(lock, ROOT, execution, foundation["evaluation"])
    result = adjudicate_once(
        scenario_dir=scenario,
        lock_dir=lock,
        observation_path=PASS_OBS,
        repo_root=ROOT,
        config=foundation["config"],
        baseline_registry=foundation["baseline"],
    )
    assert result["verdict"] == "PASS"
    assert result["run_state"] == "ADJUDICATED_PASS"
    assert result["phase_verdicts"] == {"domain_cpt": "PASS", "reasoning_sft": "PASS"}
    assert result["final_metrics"]["required_pass"] == 3


def test_intentional_scientific_fail_stays_fail_and_cannot_retry_to_pass(foundation, tmp_path: Path):
    execution = _execution(foundation, "m3-fail-unit")
    lock = tmp_path / "lock"
    scenario = tmp_path / "scenario"
    write_execution_lock(lock, ROOT, execution, foundation["evaluation"])
    result = adjudicate_once(
        scenario_dir=scenario,
        lock_dir=lock,
        observation_path=FAIL_OBS,
        repo_root=ROOT,
        config=foundation["config"],
        baseline_registry=foundation["baseline"],
    )
    assert result["verdict"] == "FAIL"
    assert result["run_state"] == "ADJUDICATED_FAIL"
    assert result["phase_verdicts"]["domain_cpt"] == "PASS"
    assert result["phase_verdicts"]["reasoning_sft"] == "FAIL"
    with pytest.raises(AdjudicationTerminalError):
        adjudicate_once(
            scenario_dir=scenario,
            lock_dir=lock,
            observation_path=PASS_OBS,
            repo_root=ROOT,
            config=foundation["config"],
            baseline_registry=foundation["baseline"],
        )
    persisted = json.loads((scenario / "adjudication.json").read_text(encoding="utf-8"))
    assert persisted["verdict"] == "FAIL"


def test_observation_missing_required_metric_fails_not_passes(foundation, tmp_path: Path):
    execution = _execution(foundation, "m3-missing-metric")
    lock = tmp_path / "lock"
    scenario = tmp_path / "scenario"
    write_execution_lock(lock, ROOT, execution, foundation["evaluation"])
    observation = json.loads(PASS_OBS.read_text(encoding="utf-8"))
    observation["metrics"].pop("answer_accuracy")
    obs_path = tmp_path / "missing.json"
    obs_path.write_text(json.dumps(observation), encoding="utf-8")
    result = adjudicate_once(
        scenario_dir=scenario,
        lock_dir=lock,
        observation_path=obs_path,
        repo_root=ROOT,
        config=foundation["config"],
        baseline_registry=foundation["baseline"],
    )
    assert result["verdict"] == "FAIL"
    metric = next(item for item in result["metric_results"] if item["metric_id"] == "answer_accuracy")
    assert metric["status"] == "FAIL"


def test_full_m3_qualification_passes_all_adversarial_gates(tmp_path: Path):
    result = run_m3_qualification(
        CONFIG,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    assert result.status == "PASS"
    assert result.pass_verdict == "PASS"
    assert result.fail_verdict == "FAIL"
    assert result.gates_passed == result.gates_total
    assert result.training_started is False
    assert result.public_bulk_download_started is False

    qualification = json.loads((result.run_dir / "m3/m3_qualification.json").read_text(encoding="utf-8"))
    assert qualification["verdict"] == "PASS"
    assert all(gate["pass"] for gate in qualification["gates"].values())

    probes = json.loads((result.run_dir / "m3/adversarial_probes.json").read_text(encoding="utf-8"))
    assert probes == {
        "fresh_resource_access_blocked": True,
        "matched_control_mutation_blocked": True,
        "retry_until_pass_blocked": True,
        "seed_replacement_blocked": True,
        "threshold_mutation_blocked": True,
    }
