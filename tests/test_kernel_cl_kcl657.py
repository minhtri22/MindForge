from __future__ import annotations

import numpy as np

from experiments.kernel_cl import kcl657_relational_boundary_state as k657


def test_upstream_discovery_source_is_valid() -> None:
    source = k657._load_discovery()
    assert source["valid"]
    assert source["status"] == "NEGATIVE"
    assert source["verdict"] == "NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL"
    assert len(source["records"]) == 60


def test_confirmatory_seeds_remain_absent_from_discovery() -> None:
    source = k657._load_discovery()
    discovery_seeds = {int(r["seed"]) for r in source["records"]}
    assert discovery_seeds.isdisjoint(k657.CONFIRM_SEEDS)


def test_representation_contract_is_frozen() -> None:
    assert k657.BASE_ORDER == ("D", "M1", "M2", "P", "G", "R")
    assert len(k657.FEATURE_ORDER) == 11
    assert k657.RIDGE_LAMBDA == 1.0
    assert k657.MAX_NEWTON_ITERS == 100
    assert k657.NEWTON_TOL == 1e-10


def test_rbs_feature_map_has_exact_terms() -> None:
    source = k657._load_discovery()
    records = source["records"][:10]
    scaler = k657.fit_scaler(records)
    fmap = k657.full_feature_map(records[0], scaler)
    assert tuple(fmap.keys()) == k657.FEATURE_ORDER
    assert fmap["zD*zP"] == fmap["zD"] * fmap["zP"]
    assert fmap["zD*zR"] == fmap["zD"] * fmap["zR"]
    assert fmap["zM1*zM2"] == fmap["zM1"] * fmap["zM2"]


def test_scaler_is_fit_from_supplied_records_only() -> None:
    source = k657._load_discovery()
    records = source["records"]
    a = k657.fit_scaler(records[:30])
    b = k657.fit_scaler(records[30:])
    assert a != b


def test_logistic_solver_fits_simple_separable_problem() -> None:
    x = np.array(
        [[-2.0], [-1.0], [-0.5], [0.5], [1.0], [2.0]],
        dtype=np.float64,
    )
    y = np.array([0, 0, 0, 1, 1, 1], dtype=np.float64)
    model = k657.fit_logistic(x, y)
    p = k657.predict_prob(x, model)
    assert p[0] < p[-1]
    assert np.all(np.isfinite(p))


def test_score_threshold_can_separate_probabilities() -> None:
    scores = [0.1, 0.2, 0.8, 0.9]
    labels = [False, False, True, True]
    rule = k657.fit_score_threshold(scores, labels)
    preds = k657.apply_threshold(scores, rule["direction"], rule["threshold"])
    assert preds == labels
    assert rule["training_metrics"]["balanced_accuracy"] == 1.0


def test_loso_holds_out_whole_seed() -> None:
    source = k657._load_discovery()
    result = k657.loso_representation(source["records"])
    assert len(result["fold_models"]) == 20
    assert {f["held_seed"] for f in result["fold_models"]} == set(k657.DISCOVERY_SEEDS)


def test_discovery_gate_is_stricter_than_kcl656() -> None:
    assert k657.DISCOVERY_BA_MIN == 0.70
    assert k657.DISCOVERY_SENS_MIN == 0.65
    assert k657.DISCOVERY_SPEC_MIN == 0.65
    assert k657.BASELINE_SUPERIORITY_MIN == 0.03


def test_ablations_do_not_change_primary_feature_order() -> None:
    assert set(k657.ABLATIONS) == {"A_DP", "A_DR", "A_MOMENT", "A_NO_RETENTION"}
    assert set(k657.ABLATIONS["A_DP"]).issubset(k657.FEATURE_ORDER)
    assert set(k657.ABLATIONS["A_DR"]).issubset(k657.FEATURE_ORDER)
    assert set(k657.ABLATIONS["A_MOMENT"]).issubset(k657.FEATURE_ORDER)
