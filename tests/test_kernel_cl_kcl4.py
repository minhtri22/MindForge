from __future__ import annotations

import json

from experiments.kernel_cl import kcl4_boundary as kcl4


def test_low_dose_is_minimum_positive_integer_replay_at_batch16() -> None:
    config = kcl4.KCL1Config()
    assert config.batch_size == 16
    assert kcl4.LOW_DOSE_A_PER_BATCH == 1
    assert kcl4.LOW_DOSE_B_PER_BATCH == 15
    assert kcl4.LOW_DOSE_REPLAY_FRACTION == 0.0625
    assert 1 / config.batch_size == 0.0625


def test_kcl4_uses_exact_kcl2_kcl3_final_seeds() -> None:
    assert tuple(kcl4.FINAL_SEEDS) == (101, 202, 303, 707, 909)


def test_kcl4_reuses_exact_kcl3_effectiveness_gates() -> None:
    assert kcl4.RETENTION_GAIN_PER_SEED_MIN == 0.30
    assert kcl4.RETENTION_GAIN_MEAN_MIN == 0.50
    assert kcl4.LOW_DOSE_FORGETTING_MEAN_MAX == 0.50
    assert kcl4.LOW_DOSE_B_ACCURACY_MIN == 0.95


def test_historical_anchors_are_frozen_and_valid() -> None:
    anchors = kcl4._validate_historical_anchors()
    assert anchors["kcl2_anchor_valid"]
    assert anchors["kcl3_anchor_valid"]


def test_no_intermediate_replay_ratio_exists_at_batch16() -> None:
    representable = [count / 16 for count in range(17)]
    assert 0.0625 in representable
    assert 0.125 in representable
    assert not any(0.0625 < ratio < 0.125 for ratio in representable)


def test_boundary_inputs_do_not_authorize_kcl5() -> None:
    assert kcl4.LOW_DOSE_A_PER_BATCH == 1
