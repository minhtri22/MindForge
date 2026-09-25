import copy

from experiments.clrm.clrm1_loss_response_support import (
    FRESH_SEEDS,
    POLICIES,
    adjudicate_records,
    regenerate_fresh_seeds,
    support_integrity,
    validate_seed_manifest,
)


def _synthetic_records(span: float = 0.20):
    rows = []
    for i, seed in enumerate(FRESH_SEEDS):
        for stage in (1, 2, 3):
            responses = {}
            for pi, policy in enumerate(POLICIES):
                base = 0.10 + 0.03 * stage + 0.01 * pi
                delta = span * (i / (len(FRESH_SEEDS) - 1))
                responses[policy] = {
                    "current_loss": base + delta,
                    "prior_mean_loss": base + 0.05 + delta,
                    "step": 250,
                    "prior_task_losses": {
                        f"T{k}": base + 0.05 + delta
                        for k in range(1, stage + 1)
                    },
                    "accuracy_sentinel": {
                        "current_terminal_accuracy": 1.0,
                        "min_prior_terminal_accuracy": 1.0,
                        "prior_task_accuracies": {
                            f"T{k}": 1.0 for k in range(1, stage + 1)
                        },
                    },
                    "same_terminal_state_verified": True,
                    "current_curve_point_exact": True,
                }
            rows.append({
                "seed": seed,
                "boundary_index": stage,
                "after_task": f"T{stage}",
                "next_task": f"T{stage+1}",
                "prior_task_count": stage,
                "responses": responses,
                "integrity": {
                    "fork_models_equal": True,
                    "boundary_model_unchanged": True,
                    "exact_replay_match": True,
                    "same_terminal_state_for_both_loss_axes": True,
                    "current_curve_point_exact": True,
                    "valid": True,
                },
            })
    return rows


def _reliability():
    return [
        {
            "seed": seed,
            "max_abs_diff": 0.0,
            "same_structure": True,
            "exact": True,
        }
        for seed in FRESH_SEEDS[:6]
    ]


def test_seed_manifest_static_freshness_contract():
    r = validate_seed_manifest()
    assert r["valid"], r
    assert regenerate_fresh_seeds() == FRESH_SEEDS
    assert not any(r["collisions"].values()), r


def test_support_integrity_exact_72x3():
    r = support_integrity(_synthetic_records())
    assert r["valid"], r
    assert r["per_stage"] == {1: 72, 2: 72, 3: 72}
    assert r["policy_response_count"] == 648


def test_one_shot_adjudicator_pass_shape():
    r = adjudicate_records(_synthetic_records(), _reliability())
    assert r["status"] == "PASS", r
    assert r["verdict"] == "PASS_LOSS_RESPONSE_SUPPORT", r
    assert r["response_geometry"]["all_six_qualified"] is True


def test_one_shot_adjudicator_negative_geometry():
    rows = _synthetic_records()
    for row in rows:
        row["responses"]["A_CARRY_ALL"]["prior_mean_loss"] = 0.2
        for k in row["responses"]["A_CARRY_ALL"]["prior_task_losses"]:
            row["responses"]["A_CARRY_ALL"]["prior_task_losses"][k] = 0.2
    r = adjudicate_records(rows, _reliability())
    assert r["status"] == "NEGATIVE", r
    assert r["verdict"] == "NEGATIVE_LOSS_RESPONSE_GEOMETRY", r


def test_one_shot_adjudicator_stops_on_reliability_failure():
    rel = copy.deepcopy(_reliability())
    rel[0]["exact"] = False
    rel[0]["max_abs_diff"] = 1e-9
    r = adjudicate_records(_synthetic_records(), rel)
    assert r["status"] == "STOP", r
    assert r["verdict"] == "STOP_INTEGRITY_OR_SUPPORT", r
