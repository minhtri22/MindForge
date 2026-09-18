from __future__ import annotations

import torch

from experiments.kernel_cl import kcl51_substrate_reconstruction as kcl51


def test_candidate_order_is_frozen_and_diversity_first() -> None:
    assert kcl51.CANDIDATE_ORDER == (
        "U3_MIXED_POSITION",
        "U4_DISJOINT_OUTPUT_PREFIX",
        "U5_AFFINE_PREFIX_ALT",
    )


def test_u3_changes_task_token_position_between_a_and_b() -> None:
    config = kcl51.KCL1Config()
    a, b = kcl51.candidate_tasks("U3_MIXED_POSITION", config)
    assert torch.all(a[0][:, 0] == 8)
    assert torch.equal(a[0][:, 1], torch.arange(10, 34))
    assert torch.equal(b[0][:, 0], torch.arange(10, 34))
    assert torch.all(b[0][:, 1] == 9)
    assert len(torch.unique(a[1])) == 24
    assert len(torch.unique(b[1])) == 24


def test_u4_has_disjoint_output_bands() -> None:
    config = kcl51.KCL1Config()
    a, b = kcl51.candidate_tasks("U4_DISJOINT_OUTPUT_PREFIX", config)
    assert int(a[1].min()) >= 40
    assert int(a[1].max()) <= 63
    assert int(b[1].min()) >= 64
    assert int(b[1].max()) <= 87
    assert set(a[1].tolist()).isdisjoint(set(b[1].tolist()))


def test_u5_is_new_affine_prefix_family() -> None:
    config = kcl51.KCL1Config()
    a, b = kcl51.candidate_tasks("U5_AFFINE_PREFIX_ALT", config)
    assert torch.all(a[0][:, 0] == 12)
    assert torch.all(b[0][:, 0] == 13)
    assert len(torch.unique(a[1])) == 24
    assert len(torch.unique(b[1])) == 24
    assert not torch.equal(a[1], b[1])


def test_kcl51_seeds_are_new() -> None:
    prior = {
        404, 505,
        101, 202, 303, 707, 909,
        606, 808,
        111, 222, 333, 777, 999,
    }
    assert kcl51.QUALIFICATION_SEEDS == (1212, 1414)
    assert set(kcl51.QUALIFICATION_SEEDS).isdisjoint(prior)


def test_kcl51_uses_original_qualification_gates() -> None:
    assert kcl51.INDEPENDENT_ACCURACY_MIN == 0.95
    assert kcl51.SEQUENTIAL_ACQUISITION_MIN == 0.95
    assert kcl51.FORGETTING_MIN == 0.50
    assert kcl51.CONTROL_DRIFT_ABS_MAX == 0.10


def test_kcl5_historical_anchor_is_locked() -> None:
    anchor = kcl51._load_kcl5_anchor()
    assert anchor["valid"]
    assert anchor["u1_qualified"] is True
    assert anchor["u2_qualified"] is False
    assert anchor["kcl5_verdict"] == "UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED"
