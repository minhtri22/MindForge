from __future__ import annotations

import copy

import torch

from experiments.kernel_cl import kcl3_replay as kcl3


def test_kcl3_treatment_is_exactly_frozen_12_5_percent_replay() -> None:
    assert kcl3.TREATMENT_A_PER_BATCH == 2
    assert kcl3.TREATMENT_B_PER_BATCH == 14
    assert kcl3.CONTROL_B_PER_BATCH == 16
    assert kcl3.REPLAY_FRACTION == 0.125


def test_kcl3_uses_exact_kcl2_final_seeds() -> None:
    assert tuple(kcl3.FINAL_SEEDS) == (101, 202, 303, 707, 909)


def test_post_a_copy_has_identical_model_and_optimizer_state() -> None:
    config = kcl3.KCL1Config()
    model = kcl3.build_model(config, 101)
    optimizer = kcl3.optimizer_for(model, config)

    clone = copy.deepcopy(model)
    clone_optimizer = kcl3.optimizer_for(clone, config)
    clone_optimizer.load_state_dict(copy.deepcopy(optimizer.state_dict()))

    for name, value in model.state_dict().items():
        assert torch.equal(value, clone.state_dict()[name])
    assert optimizer.param_groups[0]["lr"] == clone_optimizer.param_groups[0]["lr"]


def test_equal_example_budget_is_structurally_locked() -> None:
    config = kcl3.KCL1Config()
    assert kcl3.CONTROL_B_PER_BATCH == config.batch_size
    assert (
        kcl3.TREATMENT_A_PER_BATCH + kcl3.TREATMENT_B_PER_BATCH
        == config.batch_size
    )
    assert config.stage_steps * config.batch_size == 4000


def test_kcl3_frozen_effect_gates() -> None:
    assert kcl3.RETENTION_GAIN_PER_SEED_MIN == 0.30
    assert kcl3.RETENTION_GAIN_MEAN_MIN == 0.50
    assert kcl3.TREATMENT_FORGETTING_MEAN_MAX == 0.50
    assert kcl3.TREATMENT_B_ACCURACY_MIN == 0.95
