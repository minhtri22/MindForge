from __future__ import annotations

import numpy as np

from pipeline.run_h3_closure import _paired_interventions, _prepare_cell


def test_h3_supported_environments_preserve_task_labels_under_nuisance_intervention():
    for env_id in ["ENV-1", "ENV-2", "ENV-4"]:
        prepared = _prepare_cell("L0", env_id, 42)
        _, values, rows = _paired_interventions(prepared, 42)
        assert values
        assert rows
        assert all(row["task_preserving"] for row in rows)


def test_h3_env3_existing_do_n_is_not_task_preserving():
    prepared = _prepare_cell("L0", "ENV-3", 42)
    target, values, rows = _paired_interventions(prepared, 42)
    assert target == "do(N)"
    assert values == [-0.5, 0.0, 0.5]
    assert any(not row["task_preserving"] for row in rows)


def test_h3_baseline_and_candidate_use_identical_env4_factual_rows_and_values():
    baseline = _prepare_cell("L0", "ENV-4", 42)
    candidate = _prepare_cell("L1", "ENV-4", 42)
    assert np.array_equal(baseline["test_obs"], candidate["test_obs"])
    assert np.array_equal(baseline["test_labels"], candidate["test_labels"])
    base_target, base_values, _ = _paired_interventions(baseline, 42)
    cand_target, cand_values, _ = _paired_interventions(candidate, 42)
    assert base_target == cand_target
    assert base_values == cand_values
