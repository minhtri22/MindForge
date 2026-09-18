from __future__ import annotations

import copy

from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655


def test_frozen_seed_cohort_is_fresh() -> None:
    prior = {
        101,111,202,222,303,333,404,505,606,707,777,808,909,999,
        1212,1313,1414,1515,1717,1919,2121,2323,2525,2727,2929,3131,
        3333,3535,3737,3939,4141,4343,4545,4747,4949,5151,5353,
        5555,5757,5959,6161,6363,6565,6767,6969,7171,7373,7575,7777,
        7979,8181,8383,8585,8787,8989,9191,9393,
    }
    assert len(k655.FRESH_SEEDS) == 20
    assert len(set(k655.FRESH_SEEDS)) == 20
    assert set(k655.FRESH_SEEDS).isdisjoint(prior)
    assert k655.SENTINEL_SEED == 9393


def test_upstream_anchors_valid() -> None:
    anchors = k655._load_anchors()
    assert anchors["valid"]
    assert anchors["kcl654"]["verdict"] == "MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT"
    assert anchors["sentinel_expected"]["A_T4"] == 0.75


def test_policy_names_are_frozen() -> None:
    assert k655.POLICIES == (
        "A_CARRY_ALL",
        "B_RESET_ALL",
        "C_CARRY_STEP_RESET_MOMENTS",
    )


def test_margins_and_bootstrap_are_frozen() -> None:
    assert k655.STRICT_CURRENT_MIN == 0.95
    assert k655.RETENTION_MARGIN == 1 / 24
    assert k655.PLASTICITY_EQ_MARGIN == 0.01
    assert k655.BOOTSTRAP_RESAMPLES == 20000
    assert k655.BOOTSTRAP_SEED == 655655


def test_auc_definition() -> None:
    curve = [
        {"step": s, "accuracy": 1.0, "loss": 0.0}
        for s in k655.CHECKPOINTS
    ]
    assert k655.normalized_auc(curve) == 1.0


def _post_t1_pair():
    config = k655.KCL1Config()
    tasks = k655.task_sequence(config)
    model = k655.build_model(config, 202020)
    opt = k655.optimizer_for(model, config)
    k655.train_stage(
        model, opt, tasks[0][1],
        steps=250, batch_size=16, seed=202121
    )
    return config, model, opt


def test_A_carry_all_keeps_optimizer_state() -> None:
    config, model, opt = _post_t1_pair()
    before = copy.deepcopy(opt.state_dict())
    out, info = k655._policy_boundary("A_CARRY_ALL", model, opt, config)
    assert out is opt
    assert k655._deep_equal(before, out.state_dict())
    assert info["optimizer_state_unchanged"]
    assert info["model_unchanged"]


def test_B_reset_all_has_empty_state() -> None:
    config, model, opt = _post_t1_pair()
    out, info = k655._policy_boundary("B_RESET_ALL", model, opt, config)
    assert len(out.state_dict()["state"]) == 0
    assert info["state_count_after"] == 0
    assert info["model_unchanged"]


def test_C_preserves_step_and_zeros_moments() -> None:
    config, model, opt = _post_t1_pair()
    before_steps = [
        float(s["step"].item())
        for s in opt.state_dict()["state"].values()
    ]
    out, info = k655._policy_boundary(
        "C_CARRY_STEP_RESET_MOMENTS", model, opt, config
    )
    after = k655._moment_zero_and_steps(out)
    assert after["steps"] == before_steps
    assert after["moment_zero"]
    assert info["step_values_preserved"]
    assert info["model_unchanged"]


def test_bootstrap_constant_series() -> None:
    result = k655.paired_bootstrap([0.1] * 20)
    assert result["mean"] == 0.1
    assert result["ci_lower"] == 0.1
    assert result["ci_upper"] == 0.1


def test_BC_equivalence_classifier() -> None:
    p = {"bootstrap": {"ci_lower": -0.005, "ci_upper": 0.005}}
    r = {"bootstrap": {"ci_lower": -0.02, "ci_upper": 0.02}}
    assert k655._bc_classification(p, r) == "B_C_PRACTICALLY_EQUIVALENT"
