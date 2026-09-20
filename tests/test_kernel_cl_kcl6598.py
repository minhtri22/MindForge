from __future__ import annotations

import copy

from experiments.kernel_cl.kcl1_substrate import KCL1Config, build_model, optimizer_for, train_stage
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl6593_action_identifiability as k6593
from experiments.kernel_cl import kcl6598_future_interaction as k6598


def test_frozen_cohort_hashes_and_disjointness() -> None:
    assert len(k6598.TRAIN_SEEDS) == 480
    assert len(k6598.VALIDATION_SEEDS) == 240
    assert set(k6598.TRAIN_SEEDS).isdisjoint(k6598.VALIDATION_SEEDS)
    assert k6598.sha_seed_list(k6598.TRAIN_SEEDS) == k6598.TRAIN_SEED_SHA256
    assert (
        k6598.sha_seed_list(k6598.VALIDATION_SEEDS)
        == k6598.VALIDATION_SEED_SHA256
    )
    assert (
        k6598.sha_seed_list(
            tuple(list(k6598.TRAIN_SEEDS) + list(k6598.VALIDATION_SEEDS))
        )
        == k6598.ALL_SEED_SHA256
    )
    assert k6598.prior_overlap_absent(k6598.TRAIN_SEEDS)
    assert k6598.prior_overlap_absent(k6598.VALIDATION_SEEDS)


def test_future_probe_contract_is_exact_reuse() -> None:
    assert k6598.PROBE_FEATURES == k6593.PROBE_FEATURES
    assert len(k6598.PROBE_FEATURES) == 8
    assert k6598.FEATURE_SETS["S2"] == k6598.k6595.S2_FEATURES
    assert k6598.FEATURE_SETS["FUT"] == (
        k6598.k6595.S2_FEATURES + k6593.PROBE_FEATURES
    )
    assert k6598.GAIN_POINT_MIN == 0.15
    assert k6598.GAIN_CI_LOWER_MIN == 0.05
    assert k6598.BOOTSTRAP_RESAMPLES == 20_000
    assert k6598.BOOTSTRAP_SEED == 6598


def test_exact_future_probe_is_zero_step_and_nonmutating() -> None:
    cfg = KCL1Config()
    seed = k6598.TRAIN_SEEDS[0]
    tasks = task_sequence(cfg)
    model = build_model(cfg, seed)
    opt = optimizer_for(model, cfg)
    pre = copy.deepcopy(model.state_dict())

    train_stage(
        model,
        opt,
        tasks[0][1],
        steps=250,
        batch_size=16,
        seed=seed + 101,
    )
    boundary_pre = copy.deepcopy(pre)
    model_before = copy.deepcopy(model.state_dict())
    opt_before = copy.deepcopy(opt.state_dict())

    probe = k6593.extract_future_probe(
        model=model,
        optimizer=opt,
        pre_task_model_state=boundary_pre,
        observed_tasks=[tasks[0]],
        next_task=tasks[1][1],
    )

    assert tuple(probe["features"]) == k6598.PROBE_FEATURES
    assert probe["details"]["model_unchanged"]
    assert probe["details"]["optimizer_unchanged"]
    assert probe["details"]["gradients_cleared"]
    assert all(
        k6598.torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    assert k6593._recursive_equal(opt_before, opt.state_dict())
    assert all(p.grad is None for p in model.parameters())


def test_one_seed_produces_three_valid_records() -> None:
    rows = k6598.build_records((k6598.TRAIN_SEEDS[1],))
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    assert all(
        all(name in r["features"] for name in k6598.PROBE_FEATURES)
        for r in rows
    )
    assert all(r["integrity"]["probe_model_unchanged"] for r in rows)
    assert all(r["integrity"]["probe_optimizer_unchanged"] for r in rows)
    assert all(r["integrity"]["probe_gradients_cleared"] for r in rows)
    assert all(r["integrity"]["counterfactual_valid"] for r in rows)
    assert all(
        (not r["labels"]["Y_PR"] or r["labels"]["Y_A"])
        and (not r["labels"]["Y_PRR"] or r["labels"]["Y_A"])
        for r in rows
    )


def test_primary_support_gate_is_only_y_prr() -> None:
    table = {
        "Y_PRR": {
            "NEG": {"count": 100, "unique_seed_count": 80},
            "POS": {"count": 60, "unique_seed_count": 50},
        }
    }
    assert k6598.primary_support_pass(
        table, min_count=50, min_seeds=40
    )
    table["Y_PRR"]["POS"]["count"] = 49
    assert not k6598.primary_support_pass(
        table, min_count=50, min_seeds=40
    )


def _metric(mr: float, f1: float = 0.60):
    return {
        "macro_recall": mr,
        "macro_f1": f1,
        "per_class": {
            "NEG": {"recall": 0.70, "f1": 0.60},
            "POS": {"recall": 0.70, "f1": 0.60},
        },
    }


def test_adjudication_strict_future_gap_route() -> None:
    metrics = {
        "Y_PRR": {
            "S2": _metric(0.50),
            "FUT": _metric(0.70),
        }
    }
    bootstrap = {
        "arms": {
            "Y_PRR": {
                "S2": {"macro_recall": {"ci_lower": 0.40, "ci_upper": 0.60}},
                "FUT": {"macro_recall": {"ci_lower": 0.60, "ci_upper": 0.80}},
            }
        },
        "deltas": {
            "D_FUTURE": {"ci_lower": 0.08, "ci_upper": 0.30}
        },
    }
    out = k6598.adjudicate(metrics, bootstrap)
    assert out["status"] == "PASS"
    assert out["verdict"] == (
        "FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED_FOR_MECH_PRR"
    )
    assert out["primary"]["route_pass"]


def test_adjudication_rejects_small_gain_even_when_fut_qualifies() -> None:
    metrics = {
        "Y_PRR": {
            "S2": _metric(0.55),
            "FUT": _metric(0.66),
        }
    }
    bootstrap = {
        "arms": {
            "Y_PRR": {
                "S2": {"macro_recall": {"ci_lower": 0.46, "ci_upper": 0.64}},
                "FUT": {"macro_recall": {"ci_lower": 0.55, "ci_upper": 0.75}},
            }
        },
        "deltas": {
            "D_FUTURE": {"ci_lower": 0.06, "ci_upper": 0.20}
        },
    }
    out = k6598.adjudicate(metrics, bootstrap)
    assert out["status"] == "NEGATIVE"
    assert out["verdict"] == (
        "FUTURE_INTERACTION_QUALIFIED_BUT_NO_MATERIAL_GAIN"
    )
