from __future__ import annotations

import torch

from experiments.kernel_cl import kcl52_replay_generalization as kcl52


def test_kcl52_families_are_exactly_u1_and_u3() -> None:
    assert kcl52.FAMILIES == ("U1_AFFINE_PREFIX", "U3_MIXED_POSITION")


def test_kcl52_final_seeds_are_fresh() -> None:
    prior = {
        404, 505,
        101, 202, 303, 707, 909,
        606, 808,
        111, 222, 333, 777, 999,
        1212, 1414,
    }
    assert kcl52.FINAL_SEEDS == (1313, 1515, 1717, 1919, 2121)
    assert set(kcl52.FINAL_SEEDS).isdisjoint(prior)


def test_kcl52_replay_is_frozen_at_kcl4_boundary() -> None:
    assert kcl52.TREATMENT_A_PER_BATCH == 1
    assert kcl52.TREATMENT_B_PER_BATCH == 15
    assert kcl52.CONTROL_B_PER_BATCH == 16
    assert kcl52.REPLAY_FRACTION == 0.0625


def test_kcl52_u1_definition_is_inherited_exactly() -> None:
    config = kcl52.KCL1Config()
    a, b = kcl52.family_tasks("U1_AFFINE_PREFIX", config)
    assert torch.all(a[0][:, 0] == 4)
    assert torch.all(b[0][:, 0] == 5)
    assert torch.equal(a[0][:, 1], torch.arange(10, 34))
    assert torch.equal(b[0][:, 1], torch.arange(10, 34))


def test_kcl52_u3_definition_is_inherited_exactly() -> None:
    config = kcl52.KCL1Config()
    a, b = kcl52.family_tasks("U3_MIXED_POSITION", config)
    assert torch.all(a[0][:, 0] == 8)
    assert torch.equal(a[0][:, 1], torch.arange(10, 34))
    assert torch.equal(b[0][:, 0], torch.arange(10, 34))
    assert torch.all(b[0][:, 1] == 9)


def test_kcl52_historical_anchors_are_valid() -> None:
    anchors = kcl52._load_anchors()
    assert anchors["valid"]
    assert anchors["kcl5_valid"]
    assert anchors["kcl51_valid"]
    assert anchors["u1_qualified"] is True
    assert anchors["u3_selected"] == "U3_MIXED_POSITION"


def test_kcl52_effect_gates_are_frozen() -> None:
    assert kcl52.CONTROL_B_ACCURACY_MIN == 0.95
    assert kcl52.CONTROL_FORGETTING_MIN == 0.50
    assert kcl52.TREATMENT_B_ACCURACY_MIN == 0.95
    assert kcl52.RETENTION_GAIN_MEAN_MIN == 0.30
    assert kcl52.RELATIVE_FORGETTING_REDUCTION_MEAN_MIN == 0.50
    assert kcl52.TREATMENT_B_ACCURACY_MEAN_MIN == 0.95
