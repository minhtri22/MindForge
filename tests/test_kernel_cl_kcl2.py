from __future__ import annotations

import math

from experiments.kernel_cl import kcl2_baseline as kcl2


def test_kcl2_final_seeds_are_disjoint_from_kcl1_qualification() -> None:
    assert set(kcl2.FINAL_SEEDS).isdisjoint({404, 505})
    assert len(kcl2.FINAL_SEEDS) == 5
    assert len(set(kcl2.FINAL_SEEDS)) == 5


def test_kcl2_candidate_is_frozen_kcl1_winner() -> None:
    assert kcl2.CANDIDATE == "C1_TASK_PREFIX_CYCLIC"


def test_population_stats_are_finite_and_exact_for_constant_values() -> None:
    result = kcl2._stats([1.0, 1.0, 1.0, 1.0, 1.0])
    assert result == {"mean": 1.0, "pstdev": 0.0, "min": 1.0, "max": 1.0}
    assert all(math.isfinite(value) for value in result.values())


def test_kcl2_reuses_frozen_kcl1_config_and_gates() -> None:
    config = kcl2.KCL1Config()
    gates = kcl2.Gates()
    assert config.stage_steps == 250
    assert config.learning_rate == 3e-3
    assert config.batch_size == 16
    assert gates.independent_accuracy_min == 0.95
    assert gates.forgetting_min == 0.50
    assert gates.control_drift_abs_max == 0.10
