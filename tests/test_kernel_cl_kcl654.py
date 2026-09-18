from __future__ import annotations

from experiments.kernel_cl import kcl654_adamw_boundary_state as k654


def test_anchor_and_frozen_constants() -> None:
    assert k654.SEED == 9393
    assert k654.STRICT_T4_MIN == 0.95
    assert k654.T4_STREAM_SEED == 13700
    anchor = k654._load_anchor()
    assert anchor["valid"]
    assert anchor["verdict"] == "MODEL_OPTIMIZER_INTERACTION_ONLY"


def test_factorial_has_all_eight_cells() -> None:
    assert set(k654.ARM_BITS) == {
        "000", "001", "010", "011",
        "100", "101", "110", "111",
    }


def test_component_bit_order() -> None:
    assert k654.COMPONENTS == ("S", "M", "V")
    assert k654.carried_set("101") == frozenset({"S", "V"})


def _arm(acc: float) -> dict[str, float]:
    return {"final_accuracy": acc}


def test_minimal_single_component() -> None:
    arms = {bits: _arm(1.0) for bits in k654.ARM_BITS}
    for bits in ("100", "110", "101", "111"):
        arms[bits] = _arm(0.9)
    minimal = k654.minimal_sufficient_sets(arms)
    assert minimal == [["S"]]
    assert k654.classify_pattern(minimal) == "STEP_ONLY_SUFFICIENT"


def test_minimal_pair_interaction() -> None:
    arms = {bits: _arm(1.0) for bits in k654.ARM_BITS}
    for bits in ("110", "111"):
        arms[bits] = _arm(0.9)
    minimal = k654.minimal_sufficient_sets(arms)
    assert minimal == [["M", "S"]]
    assert k654.classify_pattern(minimal) == "STEP_FIRST_MOMENT_INTERACTION"


def test_three_way_interaction() -> None:
    arms = {bits: _arm(1.0) for bits in k654.ARM_BITS}
    arms["111"] = _arm(0.9)
    minimal = k654.minimal_sufficient_sets(arms)
    assert minimal == [["M", "S", "V"]]
    assert k654.classify_pattern(minimal) == "THREE_WAY_ADAMW_INTERACTION_REQUIRED"


def test_multiple_pair_interactions() -> None:
    arms = {bits: _arm(1.0) for bits in k654.ARM_BITS}
    for bits in ("110", "101", "111"):
        arms[bits] = _arm(0.9)
    minimal = k654.minimal_sufficient_sets(arms)
    assert set(map(frozenset, minimal)) == {
        frozenset({"S", "M"}),
        frozenset({"S", "V"}),
    }
    assert k654.classify_pattern(minimal) == "MULTIPLE_PAIR_INTERACTIONS"


def test_architecture_mapping() -> None:
    assert (
        k654.architecture_mapping("FIRST_MOMENT_ONLY_SUFFICIENT")
        == "FIRST_MOMENT_BOUNDARY_GOVERNANCE"
    )
    assert (
        k654.architecture_mapping("THREE_WAY_ADAMW_INTERACTION_REQUIRED")
        == "FULL_ADAMW_BOUNDARY_STATE_COORDINATION"
    )


def test_post_t1_adamw_state_contract() -> None:
    config = k654.KCL1Config()
    model, state = k654._post_t1(config)
    validation = k654._validate_post_state(model, state)
    assert validation["all_steps_250"]
    assert validation["step_unique"] == [250.0]


def test_zero_variant_resets_all_components() -> None:
    config = k654.KCL1Config()
    model, state = k654._post_t1(config)
    zero = k654._variant_state(state, "000")
    mapping = k654._name_pid_map(model, zero)
    for pid in mapping.values():
        st = zero["state"][pid]
        assert float(st["step"].item()) == 0.0
        assert bool((st["exp_avg"] == 0).all())
        assert bool((st["exp_avg_sq"] == 0).all())
