from __future__ import annotations

import math
import sys
from pathlib import Path


EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"
sys.path.insert(0, str(EXPERIMENTS))

import phase0_continual_real as continual  # noqa: E402


def test_conflict_domain_split_is_deterministic_and_non_overlapping() -> None:
    a_train_1, a_train_sentences_1 = continual.build_conflict_text("A", split="train")
    a_train_2, a_train_sentences_2 = continual.build_conflict_text("A", split="train")
    a_val, a_val_sentences = continual.build_conflict_text("A", split="validation")
    assert a_train_1 == a_train_2
    assert a_train_sentences_1 == a_train_sentences_2
    assert set(a_train_sentences_1).isdisjoint(a_val_sentences)
    assert a_train_1 != a_val


def test_conflict_domain_assignments_are_exact_opposites() -> None:
    for index in range(128):
        entity = f"Mục-{index:03d}"
        assert continual.conflict_label(entity, "A") != continual.conflict_label(entity, "B")


def test_domain_fingerprint_is_deterministic_and_split_sensitive() -> None:
    first = continual.domain_fingerprint("train", "validation", "definition")
    second = continual.domain_fingerprint("train", "validation", "definition")
    changed = continual.domain_fingerprint("train!", "validation", "definition")
    assert first == second
    assert first != changed


def test_forgetting_metric_relative_forgetting_and_interference() -> None:
    result = continual.compute_seed_metrics(
        a_initial=10.0,
        a_after_a=8.0,
        a_after_a2=7.8,
        a_after_b=8.8,
        b_initial=12.0,
        b_before_b=11.0,
        b_after_b=9.0,
    )
    assert math.isclose(result["A_learning"], 2.0)
    assert math.isclose(result["A_learning_fraction"], 0.2)
    assert math.isclose(result["B_acquisition"], 2.0)
    assert math.isclose(result["B_acquisition_fraction"], 2.0 / 11.0)
    assert math.isclose(result["forgetting"], 0.8)
    assert math.isclose(result["relative_forgetting"], 0.1)
    assert math.isclose(result["control_drift"], -0.2)
    assert math.isclose(result["net_interference"], 1.0)
    assert math.isclose(result["delta_A"], 0.4)
    assert result["meaningful_forgetting"] is True


def _gate_seed(seed: int, *, forgetting: float, net: float, a_learned: bool = True, b_learned: bool = True):
    delta = 0.4
    return {
        "seed": seed,
        "finite": True,
        "derived": {
            "A_learning": 2.0,
            "B_acquisition": 2.0,
            "forgetting": forgetting,
            "net_interference": net,
            "delta_A": delta,
            "A_learned": a_learned,
            "B_learned": b_learned,
            "meaningful_forgetting": forgetting >= delta,
        },
    }


def test_final_gate_pass_and_revise_logic() -> None:
    passing = [
        _gate_seed(101, forgetting=0.5, net=0.3),
        _gate_seed(202, forgetting=0.45, net=0.2),
        _gate_seed(303, forgetting=0.35, net=0.1),
    ]
    status, details = continual.final_gate(passing)
    assert status == "PASS"
    assert details["seeds_meeting_forgetting_threshold"] == 2

    failing = list(passing)
    failing[0] = _gate_seed(101, forgetting=0.5, net=0.3, b_learned=False)
    assert continual.final_gate(failing)[0] == "REVISE"


def test_qualification_gate_requires_learnability_and_usable_interference() -> None:
    passing = [
        {
            "finite": True,
            "independent_A_learning_fraction": 0.10,
            "independent_B_learning_fraction": 0.08,
            "derived": {"net_interference": 0.2, "meaningful_forgetting": True, "forgetting": 0.4},
        },
        {
            "finite": True,
            "independent_A_learning_fraction": 0.09,
            "independent_B_learning_fraction": 0.07,
            "derived": {"net_interference": 0.1, "meaningful_forgetting": False, "forgetting": 0.2},
        },
    ]
    assert continual.qualification_gate(passing)["qualified"] is True

    failing = [dict(item) for item in passing]
    failing[0] = {**passing[0], "independent_B_learning_fraction": 0.01}
    assert continual.qualification_gate(failing)["qualified"] is False


def test_seed_aggregation() -> None:
    results = [
        _gate_seed(101, forgetting=0.4, net=0.1),
        _gate_seed(202, forgetting=0.5, net=0.2),
        _gate_seed(303, forgetting=0.6, net=0.3),
    ]
    aggregate = continual.aggregate_seed_results(results)
    assert math.isclose(aggregate["forgetting"]["mean"], 0.5)
    assert math.isclose(aggregate["net_interference"]["median"], 0.2)


def test_a_to_a_control_protocol_has_equal_second_stage_budget() -> None:
    protocol = continual.control_protocol(384)
    assert protocol["A2_steps"] == protocol["B_steps"] == 384
    assert protocol["equal_second_stage_token_budget"] is True
    assert "post-A" in protocol["optimizer_state"]
