from __future__ import annotations

import inspect

from experiments.kernel_cl import kcl656_boundary_health_signal as k656


def test_protocol_constants_frozen() -> None:
    assert k656.STRICT_CURRENT_MIN == 0.95
    assert k656.PLASTICITY_BENEFIT_MIN == 0.01
    assert k656.RETENTION_MARGIN == 1 / 24
    assert k656.DISCOVERY_BA_MIN == 0.65
    assert k656.DISCOVERY_SENS_MIN == 0.60
    assert k656.DISCOVERY_SPEC_MIN == 0.60
    assert k656.STAGE_SUPERIORITY_MIN == 0.05
    assert k656.BOOTSTRAP_RESAMPLES == 20000
    assert k656.BOOTSTRAP_SEED == 656656


def test_candidate_signal_order_is_frozen() -> None:
    assert k656.SIGNAL_ORDER == (
        "H1_M1_RMS",
        "H2_SQRT_M2_RMS",
        "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS",
        "H4_TASK_DRIFT_RELATIVE_L2",
        "H5_PRESSURE_TO_DRIFT_RATIO",
        "H6_DRIFT_PRESSURE_COSINE",
        "H7_PRIOR_MEAN_ACCURACY",
        "H8_PRIOR_WORST_ACCURACY",
        "H9_CURRENT_TASK_LOSS",
    )


def test_discovery_and_confirm_cohorts_are_disjoint() -> None:
    assert len(k656.DISCOVERY_SEEDS) == 20
    assert len(k656.CONFIRM_SEEDS) == 20
    assert set(k656.DISCOVERY_SEEDS).isdisjoint(k656.CONFIRM_SEEDS)


def test_anchor_is_valid() -> None:
    anchor = k656._load_anchor()
    assert anchor["valid"]
    assert anchor["adjudicated_status"] == "FAIL"
    assert anchor["adjudicated_verdict"] == "BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION"


def test_feature_extractor_has_no_future_task_argument() -> None:
    params = set(inspect.signature(k656.extract_boundary_features).parameters)
    assert "next_task" not in params
    assert "future_task" not in params


def test_safe_beneficial_requires_retention_and_absolute_gate() -> None:
    a = {"auc": 0.70, "retention": 0.70, "final_accuracy": 0.90}
    p = {"auc": 0.75, "retention": 0.69, "final_accuracy": 0.96}
    assert k656._safe_beneficial(p, a)

    p_bad_ret = {"auc": 0.80, "retention": 0.60, "final_accuracy": 1.0}
    assert not k656._safe_beneficial(p_bad_ret, a)

    p_bad_abs = {"auc": 0.80, "retention": 0.70, "final_accuracy": 0.90}
    assert not k656._safe_beneficial(p_bad_abs, a)


def _record(seed: int, x: float, y: bool) -> dict:
    return {
        "seed": seed,
        "features": {"X": x},
        "labels": {"SAFE_RESET_OPPORTUNITY": y},
    }


def test_threshold_fit_finds_separable_rule() -> None:
    rows = [
        _record(1, 0.1, False),
        _record(2, 0.2, False),
        _record(3, 0.8, True),
        _record(4, 0.9, True),
    ]
    rule = k656.fit_threshold(rows, "X")
    assert rule["valid"]
    assert rule["training_metrics"]["balanced_accuracy"] == 1.0


def test_loso_holds_out_whole_seed() -> None:
    rows = []
    for seed in range(10):
        rows.append(_record(seed, 0.1, False))
        rows.append(_record(seed, 0.9, True))
    out = k656.loso_evaluate(rows, "X")
    assert out["valid"]
    assert len(out["fold_rules"]) == 10
    assert out["metrics"]["balanced_accuracy"] == 1.0


def test_binary_metrics() -> None:
    m = k656._metrics([True, True, False, False], [True, False, False, False])
    assert m["tp"] == 1
    assert m["fn"] == 1
    assert m["tn"] == 2
    assert m["fp"] == 0
    assert m["sensitivity"] == 0.5
    assert m["specificity"] == 1.0
    assert m["balanced_accuracy"] == 0.75


def test_task_drift_snapshot_is_nonzero_on_real_seed() -> None:
    config = k656.KCL1Config()
    rows = k656.build_boundary_records(k656.DISCOVERY_SEEDS[0], config)
    assert len(rows) == 3
    assert all(r["features"]["H4_TASK_DRIFT_RELATIVE_L2"] > 0 for r in rows)
    assert all(r["integrity"]["valid"] for r in rows)
