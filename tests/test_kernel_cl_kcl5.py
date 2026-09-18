from __future__ import annotations

import torch

from experiments.kernel_cl import kcl5_unseen_generalization as kcl5


def test_kcl5_families_are_new_and_both_required() -> None:
    assert kcl5.FAMILIES == ("U1_AFFINE_PREFIX", "U2_STRIDE_SUFFIX")
    assert len(set(kcl5.FAMILIES)) == 2


def test_u1_is_affine_prefix_and_permutation() -> None:
    config = kcl5.KCL1Config()
    a, b = kcl5.unseen_tasks("U1_AFFINE_PREFIX", config)
    assert torch.all(a[0][:, 0] == 4)
    assert torch.all(b[0][:, 0] == 5)
    assert torch.equal(a[0][:, 1], torch.arange(10, 34))
    assert torch.equal(b[0][:, 1], torch.arange(10, 34))
    assert len(torch.unique(a[1])) == 24
    assert len(torch.unique(b[1])) == 24
    assert not torch.equal(a[1], b[1])


def test_u2_moves_task_identity_to_suffix_and_is_permutation() -> None:
    config = kcl5.KCL1Config()
    a, b = kcl5.unseen_tasks("U2_STRIDE_SUFFIX", config)
    assert torch.equal(a[0][:, 0], torch.arange(10, 34))
    assert torch.equal(b[0][:, 0], torch.arange(10, 34))
    assert torch.all(a[0][:, 1] == 6)
    assert torch.all(b[0][:, 1] == 7)
    assert len(torch.unique(a[1])) == 24
    assert len(torch.unique(b[1])) == 24
    assert not torch.equal(a[1], b[1])


def test_kcl5_replay_is_frozen_kcl4_minimum_boundary() -> None:
    assert kcl5.TREATMENT_A_PER_BATCH == 1
    assert kcl5.TREATMENT_B_PER_BATCH == 15
    assert kcl5.REPLAY_FRACTION == 0.0625


def test_kcl5_seed_sets_are_new_and_disjoint() -> None:
    prior = {404, 505, 101, 202, 303, 707, 909}
    assert set(kcl5.QUALIFICATION_SEEDS) == {606, 808}
    assert set(kcl5.FINAL_SEEDS) == {111, 222, 333, 777, 999}
    assert set(kcl5.QUALIFICATION_SEEDS).isdisjoint(kcl5.FINAL_SEEDS)
    assert set(kcl5.QUALIFICATION_SEEDS).isdisjoint(prior)
    assert set(kcl5.FINAL_SEEDS).isdisjoint(prior)


def test_kcl5_generalization_gates_are_frozen() -> None:
    assert kcl5.TREATMENT_B_ACCURACY_MIN == 0.95
    assert kcl5.CONTROL_B_ACCURACY_MIN == 0.95
    assert kcl5.CONTROL_FORGETTING_MIN == 0.50
    assert kcl5.RETENTION_GAIN_MEAN_MIN == 0.30
    assert kcl5.RELATIVE_FORGETTING_REDUCTION_MEAN_MIN == 0.50
    assert kcl5.TREATMENT_B_ACCURACY_MEAN_MIN == 0.95
