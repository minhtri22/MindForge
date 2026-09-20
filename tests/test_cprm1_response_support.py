from __future__ import annotations

import pytest

from experiments.cprm import cprm1_response_support as c


def _synthetic_records(*, degenerate: bool = False):
    rows = []
    seeds = tuple(range(200001, 200061))
    for i, seed in enumerate(seeds):
        for stage in (1,2,3):
            responses = {}
            sign = -1.0 if (i + stage) % 2 else 1.0
            for pi, policy in enumerate(c.POLICIES):
                if degenerate:
                    auc = 0.5
                    final = 0.75
                    prior = [0.5] * stage
                else:
                    auc = 0.35 + ((i + 3*pi + stage) % 18) / 120.0
                    final = 0.45 + ((i + 2*pi + stage) % 12) / 24.0
                    prior = [
                        0.35 + ((i + 2*j + pi + stage) % 14) / 24.0
                        for j in range(stage)
                    ]
                    if pi == 1:
                        auc += sign * (1/60)
                        final += sign * (1/24)
                    if pi == 2:
                        auc -= sign * (1/48)
                        final -= sign * (1/24)
                ret = sum(prior)/len(prior)
                worst = min(prior)
                responses[policy] = {
                    "response": {
                        "plasticity_auc": max(0.0,min(1.0,auc)),
                        "final_current_accuracy": max(0.0,min(1.0,final)),
                        "prior_task_retention": max(0.0,min(1.0,ret)),
                        "worst_prior_accuracy": max(0.0,min(1.0,worst)),
                    },
                    "prior_task_accuracies": prior,
                }
            rows.append({
                "seed": seed,
                "boundary_index": stage,
                "after_task": f"T{stage}",
                "next_task": f"T{stage+1}",
                "responses": responses,
                "integrity": {
                    "fork_models_equal": True,
                    "boundary_model_unchanged": True,
                    "exact_replay_match": True,
                    "valid": True,
                },
            })
    return seeds, rows


def _reliability():
    return [{"seed": s, "max_abs_diff": 0.0, "same_structure": True, "exact": True}
            for s in c.RELIABILITY_SEEDS]


def test_seed_manifest_is_frozen() -> None:
    assert len(c.FRESH_SEEDS) == 60
    assert len(set(c.FRESH_SEEDS)) == 60
    assert c.seed_manifest_sha256() == c.SEED_MANIFEST_SHA256
    assert set(c.FRESH_SEEDS).isdisjoint(c.SPENT_ACO_SEEDS)
    assert set(c.FRESH_SEEDS).isdisjoint(c.PROTECTED_KCL_SEEDS)


def test_synthetic_stop_on_integrity() -> None:
    seeds, rows = _synthetic_records()
    rows[0]["integrity"]["valid"] = False
    out = c.adjudicate_records(rows, _reliability(), expected_seeds=seeds)
    assert out["status"] == "STOP"


def test_synthetic_negative_on_degenerate_geometry() -> None:
    seeds, rows = _synthetic_records(degenerate=True)
    out = c.adjudicate_records(rows, _reliability(), expected_seeds=seeds)
    assert out["status"] == "NEGATIVE"


def test_no_predictor_api_exists() -> None:
    assert not hasattr(c, "fit_model")
    assert not hasattr(c, "train_predictor")
    assert not hasattr(c, "select_action")


def test_execution_is_blocked_without_independent_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(c, "LOCK_VERIFICATION", c.Path("/definitely/absent"))
    assert c.execution_authorized() is False
