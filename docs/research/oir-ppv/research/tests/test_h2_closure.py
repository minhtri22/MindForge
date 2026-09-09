import json
import shutil
from pathlib import Path

import pytest

import pipeline.run_h2_closure as h2


def test_frozen_constants():
    assert h2.BASELINE == "L0"
    assert h2.ELIGIBLE_ENVS == ["ENV-1", "ENV-3", "ENV-4"]
    assert h2.INAPPLICABLE_ENV == "ENV-2"
    assert h2.SEEDS == [42, 123, 456, 789, 1011]
    assert h2.TIE_TOLERANCE == 1e-12
    assert h2.CATASTROPHIC_THRESHOLD == -0.20
    assert h2.BOOTSTRAP_SEED == 20260909


def test_env2_reference_is_null_and_never_imputed():
    for learner in [h2.BASELINE, *h2.LEARNERS]:
        for seed in h2.SEEDS:
            _, result, _ = h2._reference_cell(learner, "ENV-2", seed)
            assert result["evaluation"]["generalization"]["unseen_environment_score"] is None


def test_unknown_identities_fail_visibly():
    with pytest.raises(ValueError):
        h2._reference_cell("L999", "ENV-1", 42)
    with pytest.raises(ValueError):
        h2._reference_cell("L1", "ENV-999", 42)
    with pytest.raises(ValueError):
        h2._reference_cell("L1", "ENV-1", 999)


def test_pair_identity_same_environment_seed():
    manifest = h2._load_manifest()
    for pair in manifest["pairs"]:
        assert pair["environment"] in h2.ELIGIBLE_ENVS
        assert pair["seed"] in h2.SEEDS
        assert pair["baseline"] == h2.BASELINE
        assert pair["pair_id"] == f"{pair['learner']}-vs-L0-{pair['environment']}-S{pair['seed']}"


def test_manifest_counts_and_no_seed_replacement():
    manifest = h2._load_manifest()
    assert len(manifest["pairs"]) == 60
    assert len(manifest["inapplicable_pairs"]) == 20
    for learner in h2.LEARNERS:
        for env in h2.ELIGIBLE_ENVS:
            assert sorted(p["seed"] for p in manifest["pairs"] if p["learner"] == learner and p["environment"] == env) == sorted(h2.SEEDS)


def test_wlt_tolerance_and_catastrophic_rule():
    assert h2._wlt([1e-13, -1e-13, 0.1, -0.1]) == {"wins": 1, "losses": 1, "ties": 2}
    assert (-0.2000001 < h2.CATASTROPHIC_THRESHOLD) is True
    assert (-0.20 < h2.CATASTROPHIC_THRESHOLD) is False


def test_bootstrap_ci_deterministic():
    values = [-0.4, -0.2, 0.1, 0.2, 0.3]
    assert h2._bootstrap_ci(values) == h2._bootstrap_ci(values)


def test_raw_comparison_requires_proven_split_identity():
    _, baseline, _ = h2._reference_cell("L0", "ENV-1", 42)
    raw, identity = h2._raw_cell("ENV-1", 42, baseline)
    assert raw is not None
    altered = json.loads(json.dumps(baseline))
    altered["shift_assertions"]["ood_split"] = "different"
    raw2, identity2 = h2._raw_cell("ENV-1", 42, altered)
    assert raw2 is None
    assert "not provably equivalent" in identity2["reason"]


def test_pair_artifacts_reconcile_and_hashes_match():
    manifest = h2._load_manifest()
    complete = 0
    for pair in manifest["pairs"]:
        pair_dir = h2.ARTIFACT_ROOT / "pairs" / pair["pair_id"]
        result = h2._read_json(pair_dir / "pair_result.json")
        prov = h2._read_json(pair_dir / "provenance.json")
        assert result["status"] == "complete"
        assert prov["protocol_freeze_sha256"] == h2._sha(h2.FREEZE_PATH)
        assert prov["matrix_manifest_sha256"] == h2._sha(h2.MANIFEST_PATH)
        assert all(key in result["source_hashes"] for key in ["learner_results", "learner_provenance", "baseline_results", "baseline_provenance", "raw"])
        complete += 1
    assert complete == 60


def test_aggregate_counts_reconcile():
    comparison = h2._read_json(h2.COMPARISON_PATH)
    assert comparison["expected_primary_pairs"] == 60
    assert comparison["completed_primary_pairs"] == 60
    assert comparison["failed_or_missing_primary_pairs"] == 0
    assert comparison["inapplicable_env2_pairs"] == 20
    assert sum(c["complete_pairs"] for c in comparison["comparisons"]) == 60


def test_protocol_and_manifest_hash_mismatch_refused(monkeypatch):
    test_dir = Path("artifacts") / "h2_test_tmp" / "hash_mismatch"
    shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True)
    try:
        freeze = test_dir / "freeze.json"
        freeze_hash = test_dir / "freeze.sha256"
        freeze.write_text('{"status":"frozen_before_decisive_analysis"}', encoding="utf-8")
        freeze_hash.write_text("0" * 64, encoding="utf-8")
        monkeypatch.setattr(h2, "FREEZE_PATH", freeze)
        monkeypatch.setattr(h2, "FREEZE_HASH_PATH", freeze_hash)
        with pytest.raises(RuntimeError, match="identity mismatch"):
            h2._load_freeze()
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
