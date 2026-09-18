from __future__ import annotations

from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63


def test_kcl63_anchors_are_valid() -> None:
    anchors = k63._load_anchors()
    assert anchors["valid"]
    assert anchors["kcl61_valid"]
    assert anchors["kcl62_valid"]


def test_fuzzy_memory_removes_exact_offset_and_support() -> None:
    config = k63.KCL1Config()
    task = k63.task_sequence(config)[0][1]
    exact = k63.ExactMemory.from_task(task)
    fuzzy = k63.FuzzyMemory.from_exact(exact)
    assert not hasattr(fuzzy, "offset")
    assert not hasattr(fuzzy, "support_count")
    assert fuzzy.logical_bytes == 34
    assert exact.logical_bytes == 41


def test_fuzzy_bucket_is_frozen_width_four() -> None:
    config = k63.KCL1Config()
    for _, task in k63.task_sequence(config):
        exact = k63.ExactMemory.from_task(task)
        fuzzy = k63.FuzzyMemory.from_exact(exact)
        assert k63.OFFSET_BUCKET_WIDTH == 4
        assert fuzzy.offset_bucket_low <= exact.schema.offset < fuzzy.offset_bucket_low + 4


def test_one_cue_restores_exact_schema_for_all_tasks() -> None:
    config = k63.KCL1Config()
    for _, task in k63.task_sequence(config):
        exact = k63.ExactMemory.from_task(task)
        fuzzy = k63.FuzzyMemory.from_exact(exact)
        pre = k63.reconstruction_accuracy(fuzzy, task, representative=True)
        post = k63.one_cue_reactivate(fuzzy, task)
        assert pre < 1.0
        assert post["external_cue_count"] == 1
        assert post["reconstruction_accuracy"] == 1.0
        assert post["pass"]


def test_final_decay_storage_is_143_bytes() -> None:
    assert 3 * k63.FUZZY_SCHEMA_BYTES + k63.EXACT_SCHEMA_BYTES == 143
    assert k63.D_EXPECTED_FINAL_BYTES == 143
    assert k63.D_EXPECTED_FINAL_BYTES <= 0.90 * k63.C_EXACT_FINAL_BYTES
    assert k63.A_RAW_FINAL_BYTES / k63.D_EXPECTED_FINAL_BYTES >= 10.0


def test_replay_budget_is_unchanged() -> None:
    assert k63.CURRENT_PER_BATCH == 15
    assert k63.REPLAY_PER_BATCH == 1
    assert k63.BATCH_SIZE == 16
    assert k63.REPLAY_FRACTION == 0.0625


def test_seed_set_is_exactly_kcl61_kcl62_pairing() -> None:
    assert k63.FINAL_SEEDS == (3333, 3535, 3737, 3939, 4141)


def test_relearning_contract_is_frozen() -> None:
    assert k63.RELEARNING_THRESHOLD == 0.95
    assert k63.RELEARNING_MAX_STEPS == 250
    assert k63.RELEARNING_EVAL_INTERVAL == 10
    assert k63.RELEARNING_CENSORED_COST == 260
    assert k63.RELEARNING_ADVANTAGE_MEAN_MIN == 20.0
