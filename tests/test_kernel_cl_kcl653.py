from __future__ import annotations

from experiments.kernel_cl import kcl653_sequential_trajectory_isolation as k653


def test_seed_and_gate_are_frozen() -> None:
    assert k653.SEED == 9393
    assert k653.STRICT_T4_MIN == 0.95
    assert k653.T4_STREAM_SEED == 13700


def test_anchor_is_valid() -> None:
    anchor = k653._load_anchor()
    assert anchor["valid"]
    assert anchor["status"] == "PASS"
    assert anchor["verdict"] == "SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE"


def test_first_failing_transition_locator() -> None:
    rows = [
        {"final_accuracy": 1.0},
        {"final_accuracy": 1.0},
        {"final_accuracy": 0.875},
        {"final_accuracy": 0.75},
    ]
    assert k653.find_first_failing_transition(rows) == 2


def test_state_factor_optimizer_dominant() -> None:
    assert (
        k653.state_factor_class(1.0, 0.90, 0.90)
        == "OPTIMIZER_STATE_DOMINANT"
    )


def test_state_factor_model_dominant() -> None:
    assert (
        k653.state_factor_class(0.90, 1.0, 0.90)
        == "MODEL_STATE_DOMINANT"
    )


def test_state_factor_both() -> None:
    assert (
        k653.state_factor_class(0.90, 0.90, 0.90)
        == "BOTH_STATES_INDEPENDENTLY_SUFFICIENT"
    )


def test_state_factor_interaction_only() -> None:
    assert (
        k653.state_factor_class(1.0, 1.0, 0.90)
        == "MODEL_OPTIMIZER_INTERACTION_ONLY"
    )


def test_parameter_groups_cover_model() -> None:
    config = k653.KCL1Config()
    model = k653.build_model(config, k653.SEED)
    groups = k653.parameter_groups(model)
    assert k653.group_coverage_valid(model, groups)
    assert set(groups) == set(k653.GROUP_ORDER)


def test_group_localization_strong_transformer() -> None:
    result = {}
    for g in k653.GROUP_ORDER:
        result[g] = {"sufficient": False, "necessary": False}
    result[k653.GROUP_TRANSFORMER] = {
        "sufficient": True,
        "necessary": True,
    }
    assert (
        k653.classify_group_localization(result)
        == f"STRONG_LOCALIZATION_{k653.GROUP_TRANSFORMER}"
    )


def test_architecture_gap_mapping() -> None:
    assert (
        k653.architecture_gap_candidate(
            "MODEL_STATE_DOMINANT",
            f"STRONG_LOCALIZATION_{k653.GROUP_TRANSFORMER}",
        )
        == "BACKBONE_REPRESENTATION_PLASTICITY_CONTROL"
    )
    assert (
        k653.architecture_gap_candidate(
            "OPTIMIZER_STATE_DOMINANT",
            None,
        )
        == "TASK_BOUNDARY_OPTIMIZER_STATE_LIFECYCLE"
    )
