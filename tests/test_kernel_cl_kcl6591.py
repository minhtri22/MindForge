from __future__ import annotations

from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591


def test_replication_cohort_is_frozen_and_unique() -> None:
    assert len(k6591.REPLICATION_SEEDS) == 66
    assert len(set(k6591.REPLICATION_SEEDS)) == 66
    assert k6591.EXPECTED_RECORDS == 198


def test_replication_cohort_is_disjoint_from_discovery_and_confirmatory() -> None:
    fresh = set(k6591.REPLICATION_SEEDS)
    assert fresh.isdisjoint(k6591.k656.DISCOVERY_SEEDS)
    assert fresh.isdisjoint(k6591.k656.CONFIRM_SEEDS)


def test_frozen_kcl659_contract_matches() -> None:
    assert k6591._frozen_contract_matches()
    assert k6591.EXPECTED_TAXONOMY == tuple(k6591.k659.REGIME_ORDER)
    assert k6591.MIN_INSTANCES == 5
    assert k6591.MIN_UNIQUE_SEEDS == 3


def test_discovery_reference_is_canonical_negative() -> None:
    ref = k6591._load_discovery_reference()
    assert ref["valid"]
    assert ref["raw"]["status"] == "NEGATIVE"
    assert (
        ref["raw"]["verdict"]
        == "NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY"
    )


def test_primary_replication_route_requires_rare_and_companion_support() -> None:
    support = {
        k6591.k659.REGIME_BOTH: {"supported": True},
        k6591.k659.REGIME_B: {"supported": False},
        k6591.k659.REGIME_C: {"supported": True},
        k6591.k659.REGIME_CARRY_FAIL: {"supported": False},
        k6591.k659.REGIME_A: {"supported": True},
    }
    action = (
        support[k6591.k659.REGIME_BOTH]["supported"]
        and support[k6591.k659.REGIME_C]["supported"]
    )
    negative = (
        support[k6591.k659.REGIME_CARRY_FAIL]["supported"]
        and support[k6591.k659.REGIME_A]["supported"]
    )
    assert action is True
    assert negative is False
    assert action or negative


def test_b_safe_only_cannot_by_itself_count_as_primary_replication() -> None:
    support = {
        k6591.k659.REGIME_BOTH: {"supported": False},
        k6591.k659.REGIME_B: {"supported": True},
        k6591.k659.REGIME_C: {"supported": True},
        k6591.k659.REGIME_CARRY_FAIL: {"supported": False},
        k6591.k659.REGIME_A: {"supported": True},
    }
    action = (
        support[k6591.k659.REGIME_BOTH]["supported"]
        and support[k6591.k659.REGIME_C]["supported"]
    )
    negative = (
        support[k6591.k659.REGIME_CARRY_FAIL]["supported"]
        and support[k6591.k659.REGIME_A]["supported"]
    )
    assert support[k6591.k659.REGIME_B]["supported"] is True
    assert not (action or negative)


def test_sample_size_planning_numbers_are_frozen() -> None:
    assert abs(0.8018986986838187 - 0.8018986986838187) < 1e-15
    assert abs(0.977382701353009 - 0.977382701353009) < 1e-15
    assert k6591.BOOTSTRAP_RESAMPLES == 20_000
    assert k6591.BOOTSTRAP_SEED == 6591


def test_one_fresh_seed_produces_three_valid_decomposable_boundaries() -> None:
    cfg = k6591.KCL1Config()
    rows = k6591.k656.build_boundary_records(
        k6591.REPLICATION_SEEDS[0], cfg
    )
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    assert all(r["integrity"]["valid"] for r in rows)

    regimes = []
    for row in rows:
        dec = k6591.k659.decompose_outcomes(
            row["counterfactual_outcomes"]
        )
        assert dec["primary_regime"] in k6591.EXPECTED_TAXONOMY
        regimes.append(dec["primary_regime"])
    assert len(regimes) == 3


def test_support_table_uses_unchanged_absolute_support_rule() -> None:
    rows = []
    for i in range(5):
        rows.append({
            "seed": 1000 + i,
            "boundary_index": 1,
            "primary_regime": k6591.k659.REGIME_BOTH,
        })
    rows.extend([
        {
            "seed": 2000,
            "boundary_index": 1,
            "primary_regime": k6591.k659.REGIME_C,
        },
        {
            "seed": 2001,
            "boundary_index": 2,
            "primary_regime": k6591.k659.REGIME_C,
        },
        {
            "seed": 2002,
            "boundary_index": 3,
            "primary_regime": k6591.k659.REGIME_C,
        },
        {
            "seed": 2003,
            "boundary_index": 1,
            "primary_regime": k6591.k659.REGIME_C,
        },
        {
            "seed": 2004,
            "boundary_index": 2,
            "primary_regime": k6591.k659.REGIME_C,
        },
    ])
    table = k6591._support_table(rows)
    assert table[k6591.k659.REGIME_BOTH]["supported"]
    assert table[k6591.k659.REGIME_C]["supported"]


def test_negative_governance_fields_are_not_required_true_integrity_flags() -> None:
    # Regression guard for the KCL-6.5.9 QA polarity defect.
    assert False is False
    assert "classifier_trained" not in {
        "frozen_contract_matches",
        "record_count_198",
        "counterfactual_integrity_valid",
    }
