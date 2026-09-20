from __future__ import annotations

import copy

from experiments.kernel_cl.kcl1_substrate import KCL1Config, build_model, optimizer_for, train_stage
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl6597_temporal_mechanistic_representation as k6597


def test_frozen_cohort_hashes_and_disjointness() -> None:
    assert len(k6597.TRAIN_SEEDS) == 720
    assert len(k6597.VALIDATION_SEEDS) == 360
    assert set(k6597.TRAIN_SEEDS).isdisjoint(k6597.VALIDATION_SEEDS)
    assert k6597.sha_seed_list(k6597.TRAIN_SEEDS) == k6597.TRAIN_SEED_SHA256
    assert (
        k6597.sha_seed_list(k6597.VALIDATION_SEEDS)
        == k6597.VALIDATION_SEED_SHA256
    )
    assert (
        k6597.sha_seed_list(
            tuple(list(k6597.TRAIN_SEEDS) + list(k6597.VALIDATION_SEEDS))
        )
        == k6597.ALL_SEED_SHA256
    )
    assert k6597.prior_overlap_absent(k6597.TRAIN_SEEDS)
    assert k6597.prior_overlap_absent(k6597.VALIDATION_SEEDS)


def test_representation_contract_is_exact() -> None:
    assert k6597.FEATURE_SETS["S3"] == k6597.k6596.S3_FEATURES
    assert k6597.FEATURE_SETS["S4"] == (
        k6597.k6596.S3_FEATURES + k6597.TRIG_FEATURES
    )
    assert len(k6597.TRIG_FEATURES) == 12
    assert len(set(k6597.TRIG_FEATURES)) == 12
    assert not any("_NEXT_" in x for x in k6597.TRIG_FEATURES)


def _synthetic_bundle(seed: int, boundary: int, swap: bool = False):
    torch = k6597.torch
    updates = {
        "A_CARRY_ALL": torch.tensor([0.1, -0.2, 0.3]),
        "B_RESET_ALL": torch.tensor([0.2, -0.1, 0.4]),
        "C_CARRY_STEP_RESET_MOMENTS": torch.tensor([-0.1, 0.3, 0.2]),
    }
    if swap:
        updates["B_RESET_ALL"], updates["C_CARRY_STEP_RESET_MOMENTS"] = (
            updates["C_CARRY_STEP_RESET_MOMENTS"],
            updates["B_RESET_ALL"],
        )
    return {
        "seed": seed,
        "boundary_index": boundary,
        "g_cur": torch.tensor([0.4, 0.2, -0.1]) + boundary * 0.01,
        "g_ret": torch.tensor([-0.2, 0.5, 0.1]) + boundary * 0.01,
        "updates": updates,
        "mrig_features": {
            "M6_PLASTICITY_CONTRAST_GAP": 0.1 * boundary,
            "M7_RETENTION_CONTRAST_GAP": 0.2 * boundary,
            "M8_BOTH_RETENTION_BADNESS": 0.03 * boundary,
            "M10_STEP_SCALE_LOG_GAP": 0.04 * boundary,
        },
    }


def test_temporal_features_are_bc_exchange_symmetric() -> None:
    prev = _synthetic_bundle(1, 1)
    cur = _synthetic_bundle(1, 2)
    a = k6597.temporal_features(prev, cur)
    swapped = _synthetic_bundle(1, 1, swap=True)
    b = k6597.temporal_features(swapped, cur)
    assert a == b
    assert k6597.temporal_exchange_symmetric(prev, cur)


def test_temporal_lineage_rejects_wrong_seed_or_gap() -> None:
    prev = _synthetic_bundle(1, 1)
    cur_wrong_seed = _synthetic_bundle(2, 2)
    try:
        k6597.temporal_features(prev, cur_wrong_seed)
        assert False
    except RuntimeError:
        pass

    cur_gap = _synthetic_bundle(1, 3)
    try:
        k6597.temporal_features(prev, cur_gap)
        assert False
    except RuntimeError:
        pass


def test_probe_does_not_mutate_original_state() -> None:
    cfg = KCL1Config()
    seed = k6597.TRAIN_SEEDS[0]
    tasks = task_sequence(cfg)
    model = build_model(cfg, seed)
    opt = optimizer_for(model, cfg)
    train_stage(
        model,
        opt,
        tasks[0][1],
        steps=250,
        batch_size=16,
        seed=seed + 101,
    )
    model_before = copy.deepcopy(model.state_dict())
    opt_before = copy.deepcopy(opt.state_dict())

    probe = k6597.build_probe_bundle(
        seed=seed,
        boundary_index=1,
        model=model,
        optimizer=opt,
        config=cfg,
        current_task=tasks[0][1],
        observed_tasks=[tasks[0]],
    )
    assert all(probe["integrity"].values())
    assert all(
        k6597.torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    assert k655._deep_equal(opt_before, opt.state_dict())
    assert all(p.grad is None for p in model.parameters())


def test_one_seed_produces_only_history_eligible_boundaries() -> None:
    rows = k6597.build_records((k6597.TRAIN_SEEDS[1],))
    assert len(rows) == 2
    assert {int(r["boundary_index"]) for r in rows} == {2, 3}
    assert all(r["integrity"]["history_lineage_valid"] for r in rows)
    assert all(r["integrity"]["temporal_exchange_symmetric"] for r in rows)
    assert all(r["integrity"]["no_previous_counterfactual_history_used"] for r in rows)
    assert all(
        r["labels"]["Y_PR"] <= r["labels"]["Y_A"]
        and r["labels"]["Y_PRR"] <= r["labels"]["Y_A"]
        for r in rows
    )
    assert all(
        all(name in r["features"] for name in k6597.TRIG_FEATURES)
        for r in rows
    )


def test_primary_gate_is_frozen() -> None:
    assert k6597.TARGET_PRR == "Y_PRR"
    assert k6597.GAIN_POINT_MIN == 0.10
    assert k6597.GAIN_CI_LOWER_MIN == 0.03
    assert k6597.BOOTSTRAP_RESAMPLES == 20_000
    assert k6597.BOOTSTRAP_SEED == 6597
    assert k6597.TRAIN_MIN_COUNT == 50
    assert k6597.TRAIN_MIN_SEEDS == 40
    assert k6597.VAL_MIN_COUNT == 25
    assert k6597.VAL_MIN_SEEDS == 20


def test_adjudication_requires_qualification_gain_and_ci() -> None:
    def metric(mr: float):
        return {
            "macro_recall": mr,
            "macro_f1": 0.60,
            "per_class": {
                "NEG": {"recall": 0.70, "f1": 0.60},
                "POS": {"recall": 0.70, "f1": 0.60},
            },
        }

    metrics = {
        "Y_PRR": {
            "S3": metric(0.55),
            "S4": metric(0.70),
        }
    }
    bootstrap = {
        "arms": {
            "Y_PRR": {
                "S3": {"macro_recall": {"ci_lower": 0.46, "ci_upper": 0.64}},
                "S4": {"macro_recall": {"ci_lower": 0.60, "ci_upper": 0.80}},
            }
        },
        "deltas": {
            "D_TRIG": {"ci_lower": 0.05, "ci_upper": 0.25}
        },
    }
    out = k6597.adjudicate(metrics, bootstrap)
    assert out["status"] == "PASS"
    assert out["primary"]["route_pass"] is True

    metrics["Y_PRR"]["S4"] = metric(0.63)
    out = k6597.adjudicate(metrics, bootstrap)
    assert out["status"] == "NEGATIVE"
    assert out["verdict"] == "TRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S3"
