from __future__ import annotations

import itertools
import json

from experiments.kernel_cl import kcl659_boundary_regime_decomposition as k659


def _outcome(auc: float, final: float, retention: float) -> dict[str, float]:
    return {
        "auc": auc,
        "final_accuracy": final,
        "max_accuracy": final,
        "retention": retention,
    }


def _case(
    *,
    a_auc: float = 0.80,
    a_final: float = 1.00,
    a_ret: float = 0.80,
    b_auc: float = 0.80,
    b_final: float = 1.00,
    b_ret: float = 0.80,
    c_auc: float = 0.80,
    c_final: float = 1.00,
    c_ret: float = 0.80,
) -> dict[str, dict[str, float]]:
    return {
        k659.A: _outcome(a_auc, a_final, a_ret),
        k659.B: _outcome(b_auc, b_final, b_ret),
        k659.C: _outcome(c_auc, c_final, c_ret),
    }


def test_frozen_constants_match_protocol_contract() -> None:
    assert k659.STRICT_CURRENT_MIN == 0.95
    assert k659.PLASTICITY_BENEFIT_MIN == 0.01
    assert k659.RETENTION_MARGIN == 1 / 24
    assert k659.MIN_INSTANCES == 5
    assert k659.MIN_UNIQUE_SEEDS == 3
    assert k659.BOOTSTRAP_RESAMPLES == 20_000
    assert k659.BOOTSTRAP_SEED == 659659


def test_primary_truth_table_both_safe() -> None:
    x = _case(b_auc=0.82, c_auc=0.83)
    d = k659.decompose_outcomes(x)
    assert d["primary_regime"] == k659.REGIME_BOTH
    assert d["reconstructed_SAFE_RESET_OPPORTUNITY"] is True


def test_primary_truth_table_b_only() -> None:
    x = _case(b_auc=0.82, c_auc=0.80)
    d = k659.decompose_outcomes(x)
    assert d["primary_regime"] == k659.REGIME_B


def test_primary_truth_table_c_only() -> None:
    x = _case(b_auc=0.80, c_auc=0.82)
    d = k659.decompose_outcomes(x)
    assert d["primary_regime"] == k659.REGIME_C


def test_primary_truth_table_carry_failure_when_no_safe_reset() -> None:
    x = _case(
        a_final=0.90,
        b_final=0.90,
        c_final=0.90,
    )
    d = k659.decompose_outcomes(x)
    assert d["primary_regime"] == k659.REGIME_CARRY_FAIL
    assert d["reconstructed_SAFE_RESET_OPPORTUNITY"] is False


def test_primary_truth_table_a_sufficient_when_no_safe_reset() -> None:
    d = k659.decompose_outcomes(_case())
    assert d["primary_regime"] == k659.REGIME_A
    assert d["reconstructed_SAFE_RESET_OPPORTUNITY"] is False


def test_retention_cost_is_secondary_not_overlapping_primary_taxonomy() -> None:
    x = _case(
        b_auc=0.82,
        b_ret=0.70,  # plasticity gain + absolute OK, but retention cost > margin
    )
    d = k659.decompose_outcomes(x)
    assert d["primary_regime"] == k659.REGIME_A
    assert (
        d["secondary_flags"]["RESET_PLASTICITY_GAIN_RETENTION_COST"]
        is True
    )


def test_assignment_is_invariant_to_policy_mapping_order() -> None:
    x = _case(b_auc=0.82, c_auc=0.83)
    expected = k659.decompose_outcomes(x)
    items = list(x.items())
    for perm in itertools.permutations(items):
        got = k659.decompose_outcomes(dict(perm))
        assert got["primary_regime"] == expected["primary_regime"]
        assert (
            got["reconstructed_SAFE_RESET_OPPORTUNITY"]
            == expected["reconstructed_SAFE_RESET_OPPORTUNITY"]
        )


def test_support_gate_requires_both_instance_and_seed_support() -> None:
    assert not k659.supported(4, 4)
    assert not k659.supported(5, 2)
    assert k659.supported(5, 3)


def test_canonical_source_contract_is_valid_and_confirmatory_absent() -> None:
    raw = json.loads(k659.SOURCE.read_text(encoding="utf-8"))
    src = k659._source_contract(raw)
    assert src["valid"], src["checks"]
    seeds = {int(r["seed"]) for r in src["records"]}
    assert seeds == set(k659.DISCOVERY_SEEDS)
    assert seeds.isdisjoint(k659.CONFIRM_SEEDS)


def test_canonical_binary_label_reconstructs_recordwise_without_aggregation() -> None:
    raw = json.loads(k659.SOURCE.read_text(encoding="utf-8"))
    rows = raw["records"]
    assert len(rows) == 60
    for r in rows:
        d = k659.decompose_outcomes(r["counterfactual_outcomes"])
        assert (
            d["reconstructed_SAFE_RESET_OPPORTUNITY"]
            is bool(r["labels"]["SAFE_RESET_OPPORTUNITY"])
        )
        assert d["primary_regime"] in k659.REGIME_ORDER


def test_entropy_identity_for_deterministic_binary_collapse() -> None:
    rows = [
        {"primary_regime": k659.REGIME_B, "safe_reset": True},
        {"primary_regime": k659.REGIME_C, "safe_reset": True},
        {"primary_regime": k659.REGIME_A, "safe_reset": False},
        {"primary_regime": k659.REGIME_A, "safe_reset": False},
    ]
    h_r = k659.entropy_bits([r["primary_regime"] for r in rows])
    h_b = k659.entropy_bits([r["safe_reset"] for r in rows])
    h_cond = k659.conditional_regime_entropy(rows)
    assert abs(h_r - (h_b + h_cond)) < 1e-12
