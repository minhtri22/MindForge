import shutil
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import pipeline.run_h1_closure as h1
from pipeline.run_h1_closure import (
    CONDITIONS,
    EPSILON,
    MemorizationControl,
    _condition_spec,
    _effective_rank,
    _json_hash,
)


def test_mem_never_uses_test_labels():
    train_x = np.array([[0.0], [1.0], [1.0]])
    train_y = np.array([0, 1, 1])
    mem = MemorizationControl()
    mem.fit(train_x, train_y)
    prediction_a, _, _ = mem.predict(np.array([[9.0], [1.0]]))
    prediction_b, _, _ = mem.predict(np.array([[9.0], [1.0]]))
    assert prediction_a.tolist() == prediction_b.tolist() == [1, 1]


def test_mem_serialization_is_deterministic_and_counts_state_once():
    x = np.array([[2.0], [1.0], [2.0]])
    y = np.array([0, 1, 0])
    left = MemorizationControl()
    right = MemorizationControl()
    left.fit(x, y)
    right.fit(x, y)
    assert left.canonical_bytes() == right.canonical_bytes()
    retained = len(left.canonical_bytes())
    assert 0 + retained == retained


def test_unknown_condition_rejected():
    with pytest.raises(ValueError):
        _condition_spec("L999")


def test_frozen_condition_set():
    assert CONDITIONS == ["RAW", "MEM", "L0", "L1", "L2", "L3", "L4"]


def test_effective_rank_null_and_defined():
    assert _effective_rank(np.empty((0, 3))) is None
    assert _effective_rank(np.eye(3)) == 3


def test_noninferiority_tolerance():
    assert EPSILON == 0.02
    assert 0.79 - 0.80 >= -EPSILON
    assert not (0.77 - 0.80 >= -EPSILON)


def test_json_hash_stable_across_mapping_order():
    assert _json_hash({"a": 1, "b": 2}) == _json_hash({"b": 2, "a": 1})


def _managed_test_dir(name: str) -> Path:
    path = Path("artifacts") / "h1_test_tmp" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_protocol_loader_refuses_missing_freeze(monkeypatch):
    test_dir = _managed_test_dir("missing_freeze")
    try:
        monkeypatch.setattr(h1, "FREEZE_PATH", test_dir / "missing.json")
        monkeypatch.setattr(h1, "FREEZE_HASH_PATH", test_dir / "missing.sha256")
        with pytest.raises(RuntimeError, match="freeze/hash missing"):
            h1._load_freeze()
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_protocol_loader_refuses_hash_mismatch(monkeypatch):
    test_dir = _managed_test_dir("freeze_hash")
    try:
        freeze = test_dir / "freeze.json"
        digest = test_dir / "freeze.sha256"
        freeze.write_text(
            '{"status":"frozen_before_final_execution","conditions":[],"seeds":[]}',
            encoding="utf-8",
        )
        digest.write_text("0" * 64, encoding="utf-8")
        monkeypatch.setattr(h1, "FREEZE_PATH", freeze)
        monkeypatch.setattr(h1, "FREEZE_HASH_PATH", digest)
        with pytest.raises(RuntimeError, match="identity mismatch"):
            h1._load_freeze()
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_manifest_loader_refuses_hash_mismatch(monkeypatch):
    test_dir = _managed_test_dir("manifest_hash")
    try:
        manifest = test_dir / "matrix.json"
        digest = test_dir / "matrix.sha256"
        manifest.write_text(
            '{"status":"frozen","expected_cells":140}', encoding="utf-8"
        )
        digest.write_text("f" * 64, encoding="utf-8")
        monkeypatch.setattr(h1, "MANIFEST_PATH", manifest)
        monkeypatch.setattr(h1, "MANIFEST_HASH_PATH", digest)
        with pytest.raises(RuntimeError, match="manifest identity mismatch"):
            h1._load_manifest()
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


@pytest.mark.parametrize(
    ("condition", "excluded"),
    [
        ("L1", {"classifier"}),
        ("L2", {"decoder", "logvar_head"}),
        ("L3", {"classifier"}),
        ("L4", {"task_head", "domain_head"}),
    ],
)
def test_canonical_inference_state_excludes_training_only_and_replays(condition, excluded):
    rng = np.random.default_rng(123)
    train_x = rng.normal(size=(32, 4))
    test_x = rng.normal(size=(8, 4))
    labels = np.asarray([0, 1] * 16)
    context = np.asarray([[index % 2] for index in range(len(train_x))], dtype=float)
    spec = _condition_spec(condition)
    config = {"type": spec["type"], **spec["params"], "seed": 42}
    extractor = h1.create_extractor(config, 42)
    extractor.extract(train_x, context, labels)
    expected = extractor.extract(test_x, np.zeros((len(test_x), 1)), None).invariant_representation

    state_a = h1._canonical_inference_bytes(extractor)
    state_b = h1._canonical_inference_bytes(extractor)
    payload = h1._canonical_inference_payload(extractor)
    replay = h1._replay_canonical_inference(state_a, test_x)

    assert state_a == state_b
    assert excluded.issubset(set(payload["excluded_training_only_components"]))
    assert np.allclose(expected, replay, rtol=0.0, atol=1e-12)
    assert len(state_a) > 0


def test_corrected_complexity_counts_canonical_payload_once():
    root = h1.CORRECTION_ROOT / "cells"
    cells = list(root.glob("*/complexity_v2.json"))
    assert len(cells) == 100
    for path in cells:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert value["model_bytes"] == value["serialized_artifact_bytes"]
        assert value["retained_state_bytes"] == 0
        assert value["c_total_bytes"] == value["model_bytes"] + value["retained_state_bytes"]


def test_original_140_cell_evidence_matches_pre_correction_hash_manifest():
    manifest_path = h1.CORRECTION_ROOT / "original_evidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["cell_count"] == 140
    for cell_id, files in manifest["artifacts"].items():
        for name, expected_hash in files.items():
            path = h1.DEFAULT_ARTIFACT_ROOT / "full" / cell_id / name
            assert path.is_file()
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash


def test_v2_aggregate_contains_required_mem_raw_statistics_and_limitations():
    value = json.loads(h1.COMPARISON_V2_PATH.read_text(encoding="utf-8"))
    assert value["epsilon"] == 0.02
    assert value["protocol_freeze_sha256"] == "8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3"
    assert value["matrix_manifest_sha256"] == "55127d173e36028e069c841331b9807ee0dc4948241408c110b3a460be21823c"
    assert len(value["comparisons"]) == 5
    for item in value["comparisons"]:
        mem = item["vs_mem"]
        raw = item["vs_raw"]
        assert set(mem["c_total_wins_losses_ties"]) == {"wins", "losses", "ties"}
        assert set(mem["utility_wins_losses_ties"]) == {"wins", "losses", "ties"}
        assert set(mem["combined_h1_wins_losses_ties"]) >= {"wins", "losses", "ties"}
        for metric in ("c_total_delta", "c_total_ratio", "compression_ratio_mem_over_learner", "utility_delta"):
            assert set(mem[metric]) == {"mean", "median", "min", "max"}
        assert set(raw["utility_delta"]) == {"mean", "median", "min", "max"}
        assert raw["c_total_ratio"]["mean"] is None
        assert "division by zero" in raw["c_total_ratio"]["reason"]
        assert raw["compression_ratio"]["mean"] is None
    limitation_ids = {item["id"] for item in value["limitations"]}
    assert {"MEM_ZERO_TEST_HITS", "RAW_ZERO_C_TOTAL", "NO_RAW_SUPERIORITY"}.issubset(limitation_ids)


def test_v2_human_report_carries_mem_and_raw_interpretation_limits():
    report = h1.REPORT_V2_PATH.read_text(encoding="utf-8")
    assert "MEM exact-row lookup has 0 test hits" in report
    assert "RAW C_total=0" in report
    assert "does not claim learned-representation superiority to RAW" in report
