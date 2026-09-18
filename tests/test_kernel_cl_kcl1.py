from __future__ import annotations

import importlib.util
from pathlib import Path

import torch


MODULE_PATH = Path("experiments/kernel_cl/kcl1_substrate.py")
SPEC = importlib.util.spec_from_file_location("kcl1_substrate", MODULE_PATH)
assert SPEC and SPEC.loader
kcl1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kcl1)


def test_candidate_tasks_are_jointly_conditioned_and_deterministic() -> None:
    config = kcl1.KCL1Config()
    for candidate in kcl1.CANDIDATE_ORDER:
        first_a, first_b = kcl1.candidate_tasks(candidate, config)
        second_a, second_b = kcl1.candidate_tasks(candidate, config)
        assert torch.equal(first_a[0], second_a[0])
        assert torch.equal(first_a[1], second_a[1])
        assert torch.equal(first_b[0], second_b[0])
        assert torch.equal(first_b[1], second_b[1])
        assert len(torch.unique(first_a[1])) == config.relations
        assert len(torch.unique(first_b[1])) == config.relations
        assert torch.equal(first_a[0][:, 1], first_b[0][:, 1])
        assert torch.all(first_a[0][:, 0] == 2)
        assert torch.all(first_b[0][:, 0] == 3)
        assert not torch.equal(first_a[1], first_b[1])


def test_frozen_model_contract_is_small_and_unchanged() -> None:
    config = kcl1.KCL1Config()
    model = kcl1.build_model(config, seed=404)
    assert model.config.vocab_size == 96
    assert model.config.d_model == 16
    assert model.config.n_layers == 1
    assert model.config.max_context == 2
    assert kcl1.parameter_count(model) > 0


def test_evaluator_reports_exact_accuracy() -> None:
    config = kcl1.KCL1Config()
    model = kcl1.build_model(config, seed=404)
    task_a, _ = kcl1.candidate_tasks(kcl1.CANDIDATE_ORDER[0], config)
    result = kcl1.evaluate(model, task_a)
    assert set(result) == {"loss", "accuracy"}
    assert 0.0 <= result["accuracy"] <= 1.0
    assert result["loss"] > 0.0


def test_seed_gate_enforces_all_frozen_conditions() -> None:
    gates = kcl1.Gates()
    passing = {
        "independent_a": {"accuracy": 1.0},
        "independent_b": {"accuracy": 1.0},
        "sequential": {
            "a_after_a": {"accuracy": 1.0},
            "b_after_b": {"accuracy": 1.0},
            "forgetting_accuracy": 0.75,
            "control_drift_accuracy": 0.0,
        },
    }
    assert kcl1.seed_pass(passing, gates)
    failing = {
        **passing,
        "sequential": {**passing["sequential"], "forgetting_accuracy": 0.49},
    }
    assert not kcl1.seed_pass(failing, gates)
