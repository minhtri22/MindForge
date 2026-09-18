from __future__ import annotations

from experiments.kernel_cl import kcl65_specificity_ab as k65


def test_fresh_confirmatory_seeds() -> None:
    prior = {
        404,505,101,202,303,707,909,606,808,111,222,333,777,999,
        1212,1414,1313,1515,1717,1919,2121,2323,2525,2727,2929,3131,
        3333,3535,3737,3939,4141,5151,
    }
    assert k65.FINAL_SEEDS == (4343,4545,4747,4949,5353)
    assert set(k65.FINAL_SEEDS).isdisjoint(prior)


def test_qualification_anchor_valid() -> None:
    anchor = k65._load_q_anchor()
    assert anchor["valid"]
    assert anchor["verdict"] == "MATCHED_QUERY_CONTROL_QUALIFIED"


def test_strict_gate_not_relaxed() -> None:
    assert k65.STRICT_T4_MIN == 0.95
    assert k65.MEAN_SPECIFICITY_GAIN_MIN == 0.10


def test_query_schedule_and_budget_frozen() -> None:
    assert k65.EXPECTED_QUERY_SCHEDULE == {
        "after_T2":0,
        "after_T3":1,
        "after_T4":2,
    }
    assert k65.EXPECTED_TOTAL_QUERIES == 3
    assert k65.CURRENT_PER_BATCH == 15
    assert k65.REPLAY_PER_BATCH == 1
    assert k65.BATCH_SIZE == 16
    assert k65.REPLAY_FRACTION == 0.0625


def test_persistent_storage_frozen() -> None:
    assert k65.FINAL_PERSISTENT_BYTES == 143


def test_placebo_cue_is_current_task_tuple() -> None:
    config = k65.KCL1Config()
    tasks = k65.task_sequence(config)
    cue = k65._placebo_cue(tasks[2][1])
    assert len(cue) == 3
    fuzzy = k65.k63.FuzzyMemory.from_exact(
        k65.k63.ExactMemory.from_task(tasks[0][1])
    )
    try:
        fuzzy.reactivate_from_cue(cue)
    except ValueError:
        pass
    else:
        raise AssertionError("placebo cue unexpectedly resolved prior fuzzy memory")
