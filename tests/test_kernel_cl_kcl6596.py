from __future__ import annotations

import copy

from experiments.kernel_cl.kcl1_substrate import KCL1Config, build_model, optimizer_for, train_stage
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl6596_mechanistic_representation as k6596


def test_frozen_cohort_hashes_and_disjointness() -> None:
    assert len(k6596.TRAIN_SEEDS) == 480
    assert len(k6596.VALIDATION_SEEDS) == 240
    assert set(k6596.TRAIN_SEEDS).isdisjoint(k6596.VALIDATION_SEEDS)
    assert k6596.sha_seed_list(k6596.TRAIN_SEEDS) == k6596.TRAIN_SEED_SHA256
    assert (
        k6596.sha_seed_list(k6596.VALIDATION_SEEDS)
        == k6596.VALIDATION_SEED_SHA256
    )
    assert (
        k6596.sha_seed_list(
            tuple(list(k6596.TRAIN_SEEDS) + list(k6596.VALIDATION_SEEDS))
        )
        == k6596.ALL_SEED_SHA256
    )
    assert k6596.prior_overlap_absent(k6596.TRAIN_SEEDS)
    assert k6596.prior_overlap_absent(k6596.VALIDATION_SEEDS)


def test_representation_contract_is_exact() -> None:
    assert k6596.FEATURE_SETS["S2"] == k6596.k6595.S2_FEATURES
    assert k6596.FEATURE_SETS["S3"] == (
        k6596.k6595.S2_FEATURES + k6596.MRIG_FEATURES
    )
    assert len(k6596.MRIG_FEATURES) == 10
    assert len(set(k6596.MRIG_FEATURES)) == 10
    assert not any("_NEXT_" in x for x in k6596.MRIG_FEATURES)


def test_mrig_predictor_features_are_bc_exchange_symmetric() -> None:
    responses = {
        "A_CARRY_ALL": {
            "adaptation_response": 1.0,
            "retention_cost": 0.1,
            "step_scale": 0.01,
        },
        "B_RESET_ALL": {
            "adaptation_response": 0.6,
            "retention_cost": 0.5,
            "step_scale": 0.03,
        },
        "C_CARRY_STEP_RESET_MOMENTS": {
            "adaptation_response": 0.9,
            "retention_cost": 0.3,
            "step_scale": 0.02,
        },
    }
    a = k6596.mrigr_features_from_responses(0.25, responses)
    swapped = {
        "A_CARRY_ALL": responses["A_CARRY_ALL"],
        "B_RESET_ALL": responses["C_CARRY_STEP_RESET_MOMENTS"],
        "C_CARRY_STEP_RESET_MOMENTS": responses["B_RESET_ALL"],
    }
    b = k6596.mrigr_features_from_responses(0.25, swapped)
    assert a == b
    assert a["M8_BOTH_RETENTION_BADNESS"] > 0
    assert a["M9_MAX_JOINT_BADNESS"] > 0


def test_primary_gate_is_frozen() -> None:
    assert k6596.TARGET_PRR == "Y_PRR"
    assert k6596.GAIN_POINT_MIN == 0.10
    assert k6596.GAIN_CI_LOWER_MIN == 0.03
    assert k6596.BOOTSTRAP_RESAMPLES == 20_000
    assert k6596.BOOTSTRAP_SEED == 6596
    assert k6596.TRAIN_MIN_COUNT == 50
    assert k6596.TRAIN_MIN_SEEDS == 40
    assert k6596.VAL_MIN_COUNT == 25
    assert k6596.VAL_MIN_SEEDS == 20


def test_virtual_probe_does_not_mutate_original_boundary_state() -> None:
    cfg = KCL1Config()
    seed = k6596.TRAIN_SEEDS[0]
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

    out = k6596.extract_mrig(
        model=model,
        optimizer=opt,
        config=cfg,
        current_task=tasks[0][1],
        observed_tasks=[tasks[0]],
    )
    assert set(out["features"]) == set(k6596.MRIG_FEATURES)
    assert all(out["integrity"].values())
    assert all(
        k6596.torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    assert k655._deep_equal(opt_before, opt.state_dict())
    assert all(p.grad is None for p in model.parameters())


def test_one_fresh_seed_builds_three_valid_preboundary_records() -> None:
    rows = k6596.build_records((k6596.TRAIN_SEEDS[1],))
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    for row in rows:
        assert all(row["integrity"].values())
        assert row["labels"]["Y_PR"] <= row["labels"]["Y_A"]
        assert row["labels"]["Y_PRR"] <= row["labels"]["Y_A"]
        assert all(name in row["features"] for name in k6596.MRIG_FEATURES)


def test_adjudication_requires_qualification_point_gain_and_ci() -> None:
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
            "S2": metric(0.55),
            "S3": metric(0.70),
        }
    }
    bootstrap = {
        "arms": {
            "Y_PRR": {
                "S2": {"macro_recall": {"ci_lower": 0.46, "ci_upper": 0.64}},
                "S3": {"macro_recall": {"ci_lower": 0.60, "ci_upper": 0.80}},
            }
        },
        "deltas": {
            "D_MRIG": {"ci_lower": 0.05, "ci_upper": 0.25}
        },
    }
    out = k6596.adjudicate(metrics, bootstrap)
    assert out["status"] == "PASS"
    assert out["primary"]["route_pass"] is True

    metrics["Y_PRR"]["S3"] = metric(0.63)
    out = k6596.adjudicate(metrics, bootstrap)
    assert out["status"] == "NEGATIVE"
    assert out["verdict"] == "MRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S2"

    metrics["Y_PRR"]["S3"] = {
        "macro_recall": 0.70,
        "macro_f1": 0.30,
        "per_class": {
            "NEG": {"recall": 0.70, "f1": 0.50},
            "POS": {"recall": 0.70, "f1": 0.10},
        },
    }
    out = k6596.adjudicate(metrics, bootstrap)
    assert out["status"] == "NEGATIVE"
    assert out["verdict"] == "MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION"
