from __future__ import annotations

from experiments.kernel_cl import kcl65q_specificity_qualification as q


def test_qualification_seed_is_separate() -> None:
    assert q.QUALIFICATION_SEED == 5151
    assert q.QUALIFICATION_SEED not in {3333,3535,3737,3939,4141}


def test_q1_targeted_cue_reduces_four_candidates_to_one() -> None:
    result = q.q1_targeted_identifiability(q.KCL1Config())
    assert result["pass"]
    assert all(r["candidate_count_before"] == 4 for r in result["rows"])
    assert all(r["candidate_count_after"] == 1 for r in result["rows"])


def test_q2_placebo_does_not_reduce_prior_uncertainty() -> None:
    result = q.q2_placebo_nonidentifiability(q.KCL1Config())
    assert result["pass"]
    assert all(r["candidate_count_before"] == 4 for r in result["rows"])
    assert all(r["candidate_count_after"] == 4 for r in result["rows"])
    assert all(r["placebo_rejected_by_prior_resolver"] for r in result["rows"])


def test_q3_equal_query_envelope() -> None:
    result = q.q3_equal_query_envelope()
    assert result["pass"]
    assert result["payload_arity_same"] == 3
    assert result["query_enters_gradient"] is False


def test_q5_blocks_cross_task_resolver() -> None:
    result = q.q5_no_hidden_cross_task_resolver()
    assert result["pass"]
    assert result["cross_task_offset_inference_used"] is False
    assert result["family_formula_used"] is False


def test_frozen_query_schedule() -> None:
    assert q.EXPECTED_QUERY_SCHEDULE == {
        "after_T2": 0,
        "after_T3": 1,
        "after_T4": 2,
    }
