from __future__ import annotations

import copy
import json
from pathlib import Path

from tools.aco import verify_aco1_execution_lock as v


def test_lock_is_valid_json_and_frozen_schema() -> None:
    d=json.loads(v.LOCK_PATH.read_text(encoding="utf-8"))
    assert d["schema"] == "ACO1-EXECUTION-LOCK-v1"
    assert d["program"] == "ACO-1"
    assert d["status"] == "LOCKED_PENDING_INDEPENDENT_VERIFICATION"
    assert d["independent_verification"]["required"] is True


def test_seed_manifest_and_protected_cohort_are_disjoint() -> None:
    d=json.loads(v.LOCK_PATH.read_text(encoding="utf-8"))
    seeds=d["seed_manifest"]["seeds"]
    protected=d["protected_kcl_cohort"]["seeds"]
    assert len(seeds) == 40
    assert len(set(seeds)) == 40
    assert v.seed_hash(seeds) == v.EXPECTED_SEED_SHA256
    assert set(seeds).isdisjoint(protected)


def test_commands_are_exact_and_adjudication_is_one_shot() -> None:
    d=json.loads(v.LOCK_PATH.read_text(encoding="utf-8"))
    e=d["execution"]
    assert e["collection_command"] == v.EXPECTED_COLLECTION_CMD
    assert e["adjudication_command"] == v.EXPECTED_ADJUDICATION_CMD
    assert e["expected_records"] == 120
    assert e["one_shot_adjudication"] is True
    assert e["no_scientific_metric_inspection_between_collection_and_adjudication"] is True


def test_retry_policy_forbids_scientific_reruns() -> None:
    d=json.loads(v.LOCK_PATH.read_text(encoding="utf-8"))
    p=d["technical_failure_retry_policy"]
    assert p["collection"]["retry_must_use_exact_same_lock"] is True
    assert p["collection"]["outcome_inspection_before_retry"] is False
    assert p["collection"]["complete_valid_collection_must_not_be_rerun"] is True
    assert p["adjudication"]["exactly_one_valid_adjudication"] is True
    assert p["adjudication"]["valid_formal_result_must_not_be_rerun"] is True
    assert p["any_source_protocol_seed_or_dependency_change_invalidates_lock"] is True
    assert p["invalidated_lock_requires_return_to_zero_science_preflight"] is True


def test_no_scientific_outputs_exist_before_verification() -> None:
    assert not Path(v.EXPECTED_COLLECTION).exists()
    assert not Path(v.EXPECTED_RESULT).exists()
