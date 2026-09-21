from __future__ import annotations

import ast
import inspect

from experiments.model_core.mk1 import trainer, training_execution


def _called_names(fn) -> set[str]:
    tree = ast.parse(inspect.getsource(fn))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                names.add(target.attr)
    return names


def test_scientific_train_path_consumes_frozen_schedule() -> None:
    called = _called_names(trainer.train_arm)
    assert "load_frozen_schedule" in called
    assert "deterministic_sample_indices" not in called


def test_execution_wrapper_has_no_regeneration_calls() -> None:
    called = _called_names(training_execution.execute)
    assert "train_arm" in called
    assert "prepare_paired_initialization" not in called
    assert "deterministic_sample_indices" not in called
    assert "train_tokenizer" not in called
    assert "materialize_scientific_split" not in called


def test_execution_contract_has_exact_five_seeds_and_bundle_files() -> None:
    assert set(training_execution.STATE_SHA256) == {71001, 71002, 71003, 71004, 71005}
    assert set(training_execution.SCHEDULE_SHA256) == {71001, 71002, 71003, 71004, 71005}
    assert len(training_execution.expected_bundle_names()) == 14
    assert "train.jsonl" in training_execution.expected_bundle_names()
    assert "validation.jsonl" in training_execution.expected_bundle_names()
    assert "mk1-tokenizer.json" in training_execution.expected_bundle_names()
