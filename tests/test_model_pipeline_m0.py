from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from pipeline.baseline import BaselineRegistry
from pipeline.canonical import sha256_object
from pipeline.errors import FreshnessViolation, SemanticValidationError, StateTransitionError
from pipeline.freshness import FreshnessRegistry
from pipeline.loader import load_experiment_config, load_model_profile, validate_mapping
from pipeline.models import PhaseState, RunClass, RunState
from pipeline.preflight import run_preflight
from pipeline.resolver import ResolverContext, resolve_config
from pipeline.semantic import validate_semantics
from pipeline.state import PhaseMachine, RunMachine

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/model-training-pipeline"
EXAMPLE = DOCS / "examples/end_to_end_small.yaml"


def _load_reference():
    config = load_experiment_config(EXAMPLE, ROOT)
    profile = load_model_profile(config, ROOT)
    return config, profile


def test_all_schemas_are_valid_draft_2020_12():
    for path in sorted((DOCS / "schemas").glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_all_shipped_examples_validate_schema_and_semantics():
    for path in sorted((DOCS / "examples").glob("*.yaml")):
        config = load_experiment_config(path, ROOT)
        profile = load_model_profile(config, ROOT)
        validate_semantics(config, profile, ROOT)


def test_reference_model_profile_validates():
    config, profile = _load_reference()
    schema = json.loads((DOCS / "schemas/model_profile.schema.json").read_text(encoding="utf-8"))
    validate_mapping(profile, schema, "ModelProfile")
    assert profile["model_id"] == config.model.id
    assert profile["revision"] == config.model.revision


def test_typed_loader_builds_phase_graph():
    config, _ = _load_reference()
    assert config.run_class is RunClass.SMOKE
    assert [phase.id for phase in config.phases] == ["domain_cpt", "reasoning_sft"]
    assert config.phases[1].parent_ref == "phase:domain_cpt"
    assert config.phases[0].token_stream.packing["cross_document"] is True
    assert config.phases[1].token_stream.packing["cross_document"] is False


def test_semantic_validator_rejects_forward_parent(tmp_path: Path):
    raw = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    raw["phases"][0]["parent_ref"] = "phase:reasoning_sft"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    config = load_experiment_config(path, ROOT)
    profile = load_model_profile(config, ROOT)
    with pytest.raises(SemanticValidationError, match="earlier phase"):
        validate_semantics(config, profile, ROOT)


def test_semantic_validator_rejects_unknown_metric_baseline(tmp_path: Path):
    raw = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    raw["evaluation"]["metrics"][0]["baseline_id"] = "missing"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    config = load_experiment_config(path, ROOT)
    profile = load_model_profile(config, ROOT)
    with pytest.raises(SemanticValidationError, match="unknown baseline"):
        validate_semantics(config, profile, ROOT)


def test_canonical_hash_is_order_independent_for_mappings():
    left = {"b": 2, "a": {"y": 2, "x": 1}}
    right = {"a": {"x": 1, "y": 2}, "b": 2}
    assert sha256_object(left) == sha256_object(right)


def test_resolver_replaces_auto_precision_without_training_backend():
    config = load_experiment_config(DOCS / "examples/train_wikipedia_cpt.yaml", ROOT)
    profile = load_model_profile(config, ROOT)
    resolved, evidence = resolve_config(
        config,
        profile,
        ROOT,
        ResolverContext(backend="test", device_class="cpu", auto_precision="fp32"),
    )
    assert resolved["phases"][0]["training"]["requested_precision"] == "auto"
    assert resolved["phases"][0]["training"]["precision"] == "fp32"
    assert resolved["phases"][0]["resolved_resource"]["resolution_scope"] == "m0_zero_training"
    assert evidence["resolver_context"]["backend"] == "test"


def test_baseline_registry_is_stable_and_resolves_phase_parent():
    config, _ = _load_reference()
    first = BaselineRegistry.compile(config)
    second = BaselineRegistry.compile(config)
    assert first.sha256 == second.sha256
    entry = next(item for item in first.entries if item["id"] == "reasoning_parent")
    assert entry["reference"] == "phase:reasoning_sft:parent"


def test_freshness_guard_blocks_development_access():
    registry = FreshnessRegistry(
        seed_ids=frozenset({999}),
        dataset_ids=frozenset({"fresh-data"}),
        fixture_set_ids=frozenset({"fresh-fixtures"}),
    )
    with pytest.raises(FreshnessViolation):
        registry.assert_access(RunClass.DEVELOPMENT, "seed", 999)
    registry.assert_access(RunClass.CONFIRMATORY, "seed", 999)


def test_run_state_machine_allows_only_registered_transitions():
    machine = RunMachine()
    machine.advance(RunState.PREPARED)
    machine.advance(RunState.PREFLIGHT_PASS)
    assert machine.state is RunState.PREFLIGHT_PASS
    with pytest.raises(StateTransitionError):
        machine.advance(RunState.PROMOTED)


def test_phase_state_machine_allows_happy_path():
    machine = PhaseMachine()
    for state in (
        PhaseState.INPUT_READY,
        PhaseState.TRAINING,
        PhaseState.TRAINED,
        PhaseState.CHECKPOINT_SELECTED,
        PhaseState.PHASE_EVALUATED,
        PhaseState.PHASE_PASS,
    ):
        machine.advance(state)
    assert machine.state is PhaseState.PHASE_PASS


def test_preflight_is_zero_training_and_idempotent(tmp_path: Path):
    first = run_preflight(
        EXAMPLE,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    second = run_preflight(
        EXAMPLE,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    assert first.run_id == second.run_id
    assert first.config_hash == second.config_hash
    assert first.preflight_contract_hash == second.preflight_contract_hash
    contract = json.loads((first.run_dir / "frozen/preflight_contract.json").read_text(encoding="utf-8"))
    assert contract["zero_training_assertions"] == {
        "dataset_download_started": False,
        "fresh_evidence_accessed": False,
        "model_weights_loaded": False,
        "training_backend_initialized": False,
    }
    assert (first.run_dir / "frozen/run_config.yaml").is_file()
    assert (first.run_dir / "frozen/baseline_registry.json").is_file()
    assert first.run_state is RunState.PREFLIGHT_PASS


def test_preflight_hash_file_matches_contract(tmp_path: Path):
    result = run_preflight(
        EXAMPLE,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    asserted = (result.run_dir / "frozen/preflight_contract.sha256").read_text(encoding="utf-8").strip()
    assert asserted == result.preflight_contract_hash


def test_model_profile_mismatch_is_rejected(tmp_path: Path):
    config, profile = _load_reference()
    bad = copy.deepcopy(profile)
    bad["revision"] = "0" * 40
    with pytest.raises(SemanticValidationError, match="profile revision"):
        validate_semantics(config, bad, ROOT)
