from __future__ import annotations

import numpy as np

from experiments.kernel_cl import kcl6592_regime_predictability as k6592


def test_frozen_cohort_sizes_and_whole_seed_split() -> None:
    assert len(k6592.TRAIN_SEEDS) == 240
    assert len(k6592.VALIDATION_SEEDS) == 120
    assert len(set(k6592.TRAIN_SEEDS)) == 240
    assert len(set(k6592.VALIDATION_SEEDS)) == 120
    assert set(k6592.TRAIN_SEEDS).isdisjoint(k6592.VALIDATION_SEEDS)


def test_fresh_cohorts_do_not_touch_prior_or_protected_seeds() -> None:
    assert k6592.prior_overlap_absent(k6592.TRAIN_SEEDS)
    assert k6592.prior_overlap_absent(k6592.VALIDATION_SEEDS)
    assert set(k6592.TRAIN_SEEDS).isdisjoint(k6592.k656.CONFIRM_SEEDS)
    assert set(k6592.VALIDATION_SEEDS).isdisjoint(k6592.k656.CONFIRM_SEEDS)


def test_target_and_feature_contracts_are_frozen() -> None:
    assert k6592.CLASS_ORDER == (
        "A_ONLY",
        "C_ONLY",
        "B_AND_C_SAFE",
        "B_ONLY",
    )
    assert k6592.PRIMARY_FEATURES[:2] == ("STAGE_2", "STAGE_3")
    assert "H4_TASK_DRIFT_RELATIVE_L2" in k6592.PRIMARY_FEATURES
    assert "F1" not in k6592.PRIMARY_FEATURES
    assert set(k6592.BASELINE_FEATURES) == {
        "B_STAGE",
        "B_H4",
        "B_STAGE_H4",
    }


def test_support_gates_are_absolute_and_frozen() -> None:
    assert k6592.TRAIN_MIN_COUNT == 10
    assert k6592.TRAIN_MIN_SEEDS == 10
    assert k6592.VAL_MIN_COUNT == 5
    assert k6592.VAL_MIN_SEEDS == 5


def test_qualification_gates_are_frozen() -> None:
    assert k6592.QUAL_MACRO_RECALL == 0.60
    assert k6592.QUAL_MACRO_F1 == 0.50
    assert k6592.QUAL_CLASS_RECALL == 0.50
    assert k6592.QUAL_CLASS_F1 == 0.35
    assert k6592.QUAL_BASELINE_MARGIN == 0.05
    assert k6592.QUAL_BOOTSTRAP_LOWER == 0.45
    assert k6592.BOOTSTRAP_RESAMPLES == 20_000
    assert k6592.BOOTSTRAP_SEED == 6592


def test_stage_features_are_boundary_time_only() -> None:
    row = {
        "boundary_index": 3,
        "features": {"H4_TASK_DRIFT_RELATIVE_L2": 0.123},
    }
    assert k6592.feature_value(row, "STAGE_2") == 0.0
    assert k6592.feature_value(row, "STAGE_3") == 1.0
    assert k6592.feature_value(row, "H4_TASK_DRIFT_RELATIVE_L2") == 0.123


def test_metrics_are_multiclass_macro_not_accuracy_proxy() -> None:
    records = [
        {"target": "A_ONLY"},
        {"target": "A_ONLY"},
        {"target": "A_ONLY"},
        {"target": "C_ONLY"},
        {"target": "B_AND_C_SAFE"},
        {"target": "B_ONLY"},
    ]
    preds = ["A_ONLY"] * len(records)
    probs = np.full((len(records), 4), 0.25, dtype=np.float64)
    m = k6592.metrics(records, preds, probs)
    assert m["accuracy"] == 0.5
    assert m["per_class"]["B_AND_C_SAFE"]["recall"] == 0.0
    assert m["macro_recall"] == 0.25
    assert m["macro_recall"] < m["accuracy"]


def test_class_balanced_softmax_fits_deterministic_synthetic_problem() -> None:
    records = []
    for cls_i, cls in enumerate(k6592.CLASS_ORDER):
        for j in range(12):
            records.append({
                "target": cls,
                "boundary_index": 1 + (j % 3),
                "features": {
                    "H4_TASK_DRIFT_RELATIVE_L2": float(cls_i * 5 + j * 0.01),
                },
            })
    model = k6592.fit_softmax(
        records,
        ("H4_TASK_DRIFT_RELATIVE_L2",),
    )
    assert model["solver"]["finite"]
    assert model["solver"]["converged"]
    preds, probs = k6592.predict_model(records, model)
    assert probs.shape == (48, 4)
    assert k6592.metrics(records, preds, probs)["macro_recall"] > 0.95


def test_support_table_requires_unique_seeds_not_duplicate_boundaries() -> None:
    records = []
    for cls in k6592.CLASS_ORDER:
        for seed in range(10):
            records.append({
                "target": cls,
                "seed": seed + 1000 * k6592.CLASS_ORDER.index(cls),
                "boundary_index": 3,
            })
    table = k6592.support_table(records)
    assert k6592.support_pass(table, 10, 10)


def test_one_fresh_training_seed_produces_three_valid_boundary_records() -> None:
    rows = k6592.build_records((k6592.TRAIN_SEEDS[0],))
    assert len(rows) == 3
    assert {r["boundary_index"] for r in rows} == {1, 2, 3}
    assert all(r["counterfactual_integrity_valid"] for r in rows)
    assert all(r["target"] in k6592.CLASS_ORDER for r in rows)
    assert all(
        all(np.isfinite(float(v)) for v in r["features"].values())
        for r in rows
    )
