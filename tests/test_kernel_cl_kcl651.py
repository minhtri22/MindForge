from __future__ import annotations

from experiments.kernel_cl import kcl651_tradeoff_confirmation as k651


def test_fresh_n20_cohort_is_disjoint() -> None:
    prior = {
        404,505,101,202,303,707,909,606,808,111,222,333,777,999,
        1212,1414,1313,1515,1717,1919,2121,2323,2525,2727,2929,3131,
        3333,3535,3737,3939,4141,5151,4343,4545,4747,4949,5353,
    }
    assert len(k651.FINAL_SEEDS) == 20
    assert len(set(k651.FINAL_SEEDS)) == 20
    assert set(k651.FINAL_SEEDS).isdisjoint(prior)


def test_kcl65_mixed_anchor_is_valid() -> None:
    anchor = k651._load_kcl65_anchor()
    assert anchor["valid"]
    assert anchor["status"] == "FAIL"
    assert anchor["hypotheses"]["H_S3_targeted_information_improves_CL"] is True
    assert anchor["hypotheses"]["H_S4_strict_plasticity_retained"] is False


def test_bootstrap_contract_is_frozen() -> None:
    assert k651.BOOTSTRAP_RESAMPLES == 20000
    assert k651.BOOTSTRAP_SEED == 651651
    assert k651.CONFIDENCE_LEVEL == 0.95


def test_practical_margin_is_one_task_item() -> None:
    assert k651.PRACTICAL_MARGIN == 1 / 24
    assert k651.STRICT_T4_MIN == 0.95


def test_retention_replication_gate_is_frozen() -> None:
    assert k651.RETENTION_MEAN_GAIN_MIN == 0.10
    assert k651.RETENTION_POSITIVE_SEEDS_MIN == 16


def test_plasticity_classifier_material_tradeoff() -> None:
    ci = {"ci_lower": -0.08, "ci_upper": -0.05}
    assert k651.classify_plasticity(ci) == "MATERIAL_TRADEOFF_CONFIRMED"


def test_plasticity_classifier_small_tradeoff() -> None:
    ci = {"ci_lower": -0.03, "ci_upper": -0.005}
    assert k651.classify_plasticity(ci) == "SMALL_SYSTEMATIC_TRADEOFF_WITHIN_MARGIN"


def test_plasticity_classifier_no_reproducible_tradeoff() -> None:
    ci = {"ci_lower": -0.02, "ci_upper": 0.01}
    assert k651.classify_plasticity(ci) == "NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN"


def test_bootstrap_is_deterministic() -> None:
    values = [0.1] * 20
    a = k651.paired_bootstrap_mean_ci(values)
    b = k651.paired_bootstrap_mean_ci(values)
    assert a == b
    assert a["mean"] == 0.1
    assert a["ci_lower"] == 0.1
    assert a["ci_upper"] == 0.1
