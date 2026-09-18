from __future__ import annotations

from experiments.kernel_cl import kcl64_clarification_reactivation as k64


def test_kcl63_failure_anchor_is_frozen_and_valid() -> None:
    anchor = k64._load_kcl63_anchor()
    assert anchor["valid"]
    assert anchor["status"] == "FAIL"
    assert anchor["verdict"] == "FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY"
    assert anchor["hypotheses"]["H1_fuzzy_trace_recoverable"] is True
    assert anchor["hypotheses"]["H2_useful_CL_trace_and_plasticity"] is False
    assert anchor["hypotheses"]["H3_relearning_advantage"] is True
    assert anchor["hypotheses"]["H4_storage_below_exact_schema"] is True


def test_strict_t4_gate_is_not_relaxed() -> None:
    assert k64.STRICT_T4_MIN == 0.95


def test_e_uses_same_d_fuzzy_representation() -> None:
    assert k64.k63.OFFSET_BUCKET_WIDTH == 4
    assert k64.FINAL_PERSISTENT_BYTES == 143


def test_clarification_cue_reactivates_without_raw_retention() -> None:
    config = k64.KCL1Config()
    task = k64.task_sequence(config)[0][1]
    exact = k64.k63.ExactMemory.from_task(task)
    fuzzy = k64.k63.FuzzyMemory.from_exact(exact)
    cue = k64._clarification_cue(fuzzy, task)
    reactivated = fuzzy.reactivate_from_cue(cue)
    assert reactivated.schema.offset == exact.schema.offset
    assert not hasattr(fuzzy, "offset")
    assert fuzzy.logical_bytes == 34


def test_frozen_query_schedule() -> None:
    assert k64.EXPECTED_TOTAL_QUERIES == 3


def test_replay_compute_is_unchanged() -> None:
    assert k64.CURRENT_PER_BATCH == 15
    assert k64.REPLAY_PER_BATCH == 1
    assert k64.BATCH_SIZE == 16
    assert k64.REPLAY_FRACTION == 0.0625


def test_paired_seed_set_is_unchanged() -> None:
    assert k64.FINAL_SEEDS == (3333, 3535, 3737, 3939, 4141)


def test_causal_improvement_gate_is_frozen() -> None:
    assert k64.MEAN_PRIOR_GAIN_OVER_D_MIN == 0.10
    assert k64.D_REPRO_TOLERANCE == 1 / 24
