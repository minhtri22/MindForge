from __future__ import annotations

import random

from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594


def test_frozen_cohorts_match_generator_and_are_disjoint() -> None:
    seeds = random.Random(6594).sample(range(2_000_001, 3_000_000), 480)
    assert tuple(seeds[:240]) == k6594.DISCOVERY_SEEDS
    assert tuple(seeds[240:]) == k6594.REPLICATION_SEEDS
    assert len(k6594.DISCOVERY_SEEDS) == 240
    assert len(k6594.REPLICATION_SEEDS) == 240
    assert set(k6594.DISCOVERY_SEEDS).isdisjoint(k6594.REPLICATION_SEEDS)
    assert k6594.prior_overlap_absent(k6594.DISCOVERY_SEEDS)
    assert k6594.prior_overlap_absent(k6594.REPLICATION_SEEDS)


def test_all_seven_per_policy_cause_codes() -> None:
    expected = {
        ("PLASTICITY_SHORTFALL",): "P",
        ("RETENTION_MARGIN_VIOLATION",): "R",
        ("STRICT_ACCURACY_FAILURE",): "A",
        ("PLASTICITY_SHORTFALL", "RETENTION_MARGIN_VIOLATION"): "P+R",
        ("PLASTICITY_SHORTFALL", "STRICT_ACCURACY_FAILURE"): "P+A",
        ("RETENTION_MARGIN_VIOLATION", "STRICT_ACCURACY_FAILURE"): "R+A",
        (
            "PLASTICITY_SHORTFALL",
            "RETENTION_MARGIN_VIOLATION",
            "STRICT_ACCURACY_FAILURE",
        ): "P+R+A",
    }
    assert all(k6594.cause_code(k) == v for k, v in expected.items())


def test_failure_reasons_are_exact_predicate_complements() -> None:
    comp = {"plasticity_gain": False, "retention_ok": True, "absolute_ok": False}
    assert k6594.failure_reasons(comp) == (
        k6594.P_REASON,
        k6594.A_REASON,
    )
    assert k6594.cause_code(k6594.failure_reasons(comp)) == "P+A"


def test_mechanism_signature_is_exchange_invariant() -> None:
    a = k6594.mechanism_signature("P", "R+A")
    b = k6594.mechanism_signature("R+A", "P")
    assert a == b
    assert k6594.ordered_signature("P", "R+A") != k6594.ordered_signature("R+A", "P")


def test_mode_support_gate_is_frozen() -> None:
    assert k6594.MODE_MIN_COUNT == 12
    assert k6594.MODE_MIN_SEEDS == 10
    assert k6594.MODE_MIN_PREVALENCE == 0.05
    assert k6594.A_ONLY_MIN_COUNT == 150
    assert k6594.A_ONLY_MIN_SEEDS == 100
    assert k6594.STABILITY_ABS_DELTA_MAX == 0.10


def test_one_fresh_seed_builds_three_integrity_valid_records() -> None:
    rows = k6594.build_phase_records((k6594.DISCOVERY_SEEDS[0],))
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    assert all(r["counterfactual_integrity_valid"] for r in rows)
    for r in rows:
        if r["target"] == "A_ONLY":
            assert all(r["failure_integrity"].values())
            assert r["failure_reasons"]["B"]
            assert r["failure_reasons"]["C"]
            assert (
                k6594.mechanism_signature(
                    r["cause_codes"]["C"],
                    r["cause_codes"]["B"],
                )
                == r["mechanism_signature"]
            )
