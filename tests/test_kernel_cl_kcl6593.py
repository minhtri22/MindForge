from __future__ import annotations

import random

from experiments.kernel_cl import kcl6593_action_identifiability as k6593


def test_frozen_cohorts_match_generator_and_are_disjoint() -> None:
    seeds = random.Random(6593).sample(range(1_000_001, 2_000_000), 450)
    assert tuple(seeds[:300]) == k6593.TRAIN_SEEDS
    assert tuple(seeds[300:]) == k6593.VALIDATION_SEEDS
    assert len(k6593.TRAIN_SEEDS) == 300
    assert len(k6593.VALIDATION_SEEDS) == 150
    assert set(k6593.TRAIN_SEEDS).isdisjoint(k6593.VALIDATION_SEEDS)
    assert k6593.prior_overlap_absent(k6593.TRAIN_SEEDS)
    assert k6593.prior_overlap_absent(k6593.VALIDATION_SEEDS)


def test_information_sets_are_strictly_nested() -> None:
    assert k6593.S0_FEATURES == ("STAGE_2", "STAGE_3")
    assert k6593.S1_FEATURES[:2] == k6593.S0_FEATURES
    assert k6593.S2_FEATURES[: len(k6593.S1_FEATURES)] == k6593.S1_FEATURES
    assert k6593.O_FEATURES[: len(k6593.S2_FEATURES)] == k6593.S2_FEATURES
    assert len(k6593.S2_FEATURES) == len(k6593.S1_FEATURES) + 13
    assert len(k6593.O_FEATURES) == len(k6593.S2_FEATURES) + 8


def test_probe_contract_has_no_counterfactual_outcome_inputs() -> None:
    forbidden = (
        "AUC",
        "FINAL_ACCURACY",
        "SAFE_B",
        "SAFE_C",
        "BEST_SAFE_ACTION",
    )
    for name in k6593.PROBE_FEATURES:
        assert not any(token in name for token in forbidden)
    assert k6593.PROBE_FEATURES == (
        "P1_NEXT_TASK_LOSS",
        "P2_NEXT_GRAD_NORM",
        "P3_NEXT_GRAD_DRIFT_COSINE",
        "P4_NEXT_GRAD_PRESSURE_COSINE",
        "P5_NEXT_GRAD_RETENTION_COSINE",
        "P6_NEXT_GRAD_DRIFT_SHARE_OVERLAP",
        "P7_NEXT_GRAD_PRESSURE_SHARE_OVERLAP",
        "P8_NEXT_GRAD_RETENTION_SHARE_OVERLAP",
    )


def _metric(mr: float, mf1: float, class_recall: float, class_f1: float):
    return {
        "macro_recall": mr,
        "macro_f1": mf1,
        "per_class": {
            c: {"recall": class_recall, "f1": class_f1}
            for c in k6593.CLASS_ORDER
        },
    }


def _boot(s0: float, s1: float, s2: float, oracle: float, d10: float, d21: float, do2: float):
    def arm(x: float):
        return {
            "macro_recall": {"ci_lower": x, "ci_upper": min(1.0, x + 0.1)},
            "macro_f1": {"ci_lower": x, "ci_upper": min(1.0, x + 0.1)},
        }
    return {
        "arms": {
            "S0": arm(s0),
            "S1": arm(s1),
            "S2": arm(s2),
            "O": arm(oracle),
        },
        "deltas": {
            "D10": {"ci_lower": d10, "ci_upper": d10 + 0.1},
            "D21": {"ci_lower": d21, "ci_upper": d21 + 0.1},
            "DO2": {"ci_lower": do2, "ci_upper": do2 + 0.1},
        },
    }


def test_route_r_identifies_preboundary_representation_gap() -> None:
    metrics = {
        "S0": _metric(0.45, 0.40, 0.45, 0.40),
        "S1": _metric(0.47, 0.42, 0.45, 0.40),
        "S2": _metric(0.65, 0.58, 0.60, 0.50),
        "O": _metric(0.66, 0.59, 0.61, 0.51),
    }
    boot = _boot(0.35, 0.36, 0.50, 0.51, 0.00, 0.08, 0.00)
    d = k6593.adjudicate(metrics, boot)
    assert d["status"] == "PASS"
    assert d["verdict"] == "PREBOUNDARY_REPRESENTATION_GAP_IDENTIFIED"
    assert d["routes"]["R_PREBOUNDARY_REPRESENTATION_GAP"]


def test_route_i_identifies_future_interaction_gap() -> None:
    metrics = {
        "S0": _metric(0.45, 0.40, 0.45, 0.40),
        "S1": _metric(0.47, 0.42, 0.45, 0.40),
        "S2": _metric(0.48, 0.43, 0.45, 0.40),
        "O": _metric(0.72, 0.62, 0.65, 0.55),
    }
    boot = _boot(0.35, 0.36, 0.37, 0.55, 0.00, 0.00, 0.10)
    d = k6593.adjudicate(metrics, boot)
    assert d["status"] == "PASS"
    assert d["verdict"] == "FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED"
    assert d["routes"]["I_FUTURE_INTERACTION_GAP"]


def test_inconclusive_if_neither_preboundary_nor_oracle_qualifies() -> None:
    metrics = {
        name: _metric(0.48, 0.40, 0.45, 0.35)
        for name in ("S0", "S1", "S2", "O")
    }
    boot = _boot(0.35, 0.35, 0.35, 0.35, 0.0, 0.0, 0.0)
    d = k6593.adjudicate(metrics, boot)
    assert d["status"] == "NEGATIVE"
    assert d["verdict"] == "BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE"


def test_one_fresh_seed_builds_three_integrity_valid_nested_records() -> None:
    rows = k6593.build_records((k6593.TRAIN_SEEDS[0],))
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    for r in rows:
        assert r["target"] in k6593.CLASS_ORDER
        assert all(r["integrity"].values())
        for name in k6593.O_FEATURES:
            if name not in {"STAGE_2", "STAGE_3"}:
                assert name in r["features"]
