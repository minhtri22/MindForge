import json
from pathlib import Path

from tools.research.ppf_c1.generate import (
    BENCH_ROOT, DATA_ROOT, ROOT, canonical_preregistration_hash, file_hash,
)


def _prereg():
    return json.loads((DATA_ROOT / "c1-preregistration.json").read_text(encoding="utf-8"))


def test_preregistration_is_canonical_and_exact_size():
    p = _prereg()
    assert canonical_preregistration_hash(p) == p["canonical_preregistration_sha256"]
    assert len(p["persons"]) == 12
    assert len(p["truth_configurations"]) == 12
    assert len(p["history_specifications"]) == 64
    assert p["risk_allocation"] == {"STANDARD": 8, "HIGH-RISK": 4}
    assert len(p["structural_holdouts"]) == 4
    assert len(p["counterfactual_pairs"]) == 8
    paired = [x for x in p["history_specifications"] if x["pair_id"]]
    assert len(paired) == 16
    assert len({x["case_id"] for x in paired}) == 16


def test_only_frozen_t0_t1_are_registered_and_source_hashes_match():
    p = _prereg()
    assert set(p["treatments"]) == {"T0", "T1"}
    assert file_hash(ROOT / "tools/research/ppf_l4/baselines.py") == p["treatments"]["T0"]["baseline_source_sha256"]
    assert file_hash(ROOT / "tools/research/ppf_l5/mechanism.py") == p["treatments"]["T1"]["mechanism_source_sha256"]


def test_failed_generation_was_not_persisted_or_locked():
    assert not BENCH_ROOT.exists()
    assert not (DATA_ROOT / "c1-dataset-lock.json").exists()
    assert not (DATA_ROOT / "c1-run-lock.json").exists()
    assert not (DATA_ROOT / "c1-run-state.json").exists()
    assert not (DATA_ROOT / "c1-results.json").exists()


def test_failure_evidence_records_exact_l2_schema_defect():
    failure = json.loads((DATA_ROOT / "c1-generator-qa-failure.json").read_text(encoding="utf-8"))
    schema_text = (ROOT / "docs/research/data/ppf-l2/schema.json").read_text(encoding="utf-8")
    assert failure["generation_attempt_count"] == 1
    assert failure["visible_events"] == 650
    assert failure["l2_valid_events"] == 598
    assert failure["l2_invalid_events"] == 52
    assert "C1_OBSERVATION_LIMITATION" in failure["root_cause"]
    assert "C1_OBSERVATION_LIMITATION" not in schema_text
    assert failure["semantic_run_count"] == 0
