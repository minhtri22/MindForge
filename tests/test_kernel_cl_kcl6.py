from __future__ import annotations

import torch

from experiments.kernel_cl import kcl6_long_horizon as kcl6


def test_kcl6_task_order_is_exactly_u1_then_u3() -> None:
    assert kcl6.TASK_ORDER == (
        "T1_U1_A",
        "T2_U1_B",
        "T3_U3_A",
        "T4_U3_B",
    )


def test_kcl6_task_definitions_are_inherited() -> None:
    config = kcl6.KCL1Config()
    tasks = kcl6.task_sequence(config)
    assert [name for name, _ in tasks] == list(kcl6.TASK_ORDER)

    t1 = tasks[0][1]
    t2 = tasks[1][1]
    t3 = tasks[2][1]
    t4 = tasks[3][1]

    assert torch.all(t1[0][:, 0] == 4)
    assert torch.all(t2[0][:, 0] == 5)
    assert torch.all(t3[0][:, 0] == 8)
    assert torch.all(t4[0][:, 1] == 9)


def test_kcl6_final_seeds_are_fresh() -> None:
    prior = {
        404, 505,
        101, 202, 303, 707, 909,
        606, 808,
        111, 222, 333, 777, 999,
        1212, 1414,
        1313, 1515, 1717, 1919, 2121,
    }
    assert kcl6.FINAL_SEEDS == (2323, 2525, 2727, 2929, 3131)
    assert set(kcl6.FINAL_SEEDS).isdisjoint(prior)


def test_kcl6_replay_budget_stays_one_item_per_update() -> None:
    assert kcl6.CONTROL_CURRENT_PER_BATCH == 16
    assert kcl6.TREATMENT_CURRENT_PER_BATCH == 15
    assert kcl6.TREATMENT_REPLAY_PER_BATCH == 1
    assert kcl6.REPLAY_FRACTION == 0.0625


def test_round_robin_replay_allocation() -> None:
    assert [kcl6.replay_task_index(i, 1) for i in range(6)] == [0, 0, 0, 0, 0, 0]
    assert [kcl6.replay_task_index(i, 2) for i in range(6)] == [0, 1, 0, 1, 0, 1]
    assert [kcl6.replay_task_index(i, 3) for i in range(7)] == [0, 1, 2, 0, 1, 2, 0]


def test_replay_storage_accounting_is_linear_in_tasks() -> None:
    config = kcl6.KCL1Config()
    tasks = kcl6.task_sequence(config)
    per_task = kcl6.logical_task_storage(tasks[0][1])
    assert per_task["examples"] == 24
    assert per_task["tensor_bytes"] > 0
    assert 3 * per_task["examples"] == 72


def test_kcl6_historical_anchor_is_valid() -> None:
    anchor = kcl6._load_anchor()
    assert anchor["valid"]
    assert anchor["verdict"] == "REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS"
    assert anchor["families"] == ["U1_AFFINE_PREFIX", "U3_MIXED_POSITION"]
    assert anchor["replay_fraction"] == 0.0625


def test_kcl6_gates_are_frozen() -> None:
    assert kcl6.CURRENT_TASK_ACCURACY_MIN == 0.95
    assert kcl6.FINAL_WORST_PRIOR_ACCURACY_MIN == 0.25
    assert kcl6.FINAL_MEAN_PRIOR_ACCURACY_MIN_PER_SEED == 0.50
    assert kcl6.FINAL_MEAN_PRIOR_ACCURACY_MEAN_MIN == 0.60
    assert kcl6.FINAL_RETENTION_GAIN_MEAN_MIN == 0.30
    assert kcl6.FINAL_WORST_PRIOR_ACCURACY_MEAN_MIN == 0.30
    assert kcl6.STABILITY_RATIO_MIN == 0.50
