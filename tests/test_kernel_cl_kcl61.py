from __future__ import annotations

from experiments.kernel_cl import kcl61_weighted_replay_ab as kcl61


def test_kcl61_seeds_are_fresh() -> None:
    prior = {
        404, 505,
        101, 202, 303, 707, 909,
        606, 808,
        111, 222, 333, 777, 999,
        1212, 1414,
        1313, 1515, 1717, 1919, 2121,
        2323, 2525, 2727, 2929, 3131,
    }
    assert kcl61.FINAL_SEEDS == (3333, 3535, 3737, 3939, 4141)
    assert set(kcl61.FINAL_SEEDS).isdisjoint(prior)


def test_weighted_store_consolidates_exact_repeats() -> None:
    store = kcl61.WeightedExactTaskStore({})
    obs = (4, 10, 41)
    store.ingest(obs)
    store.ingest(obs)
    store.ingest(obs, 2)
    assert store.unique_entries == 1
    assert store.total_multiplicity == 4
    assert store.counts[obs] == 4


def test_weighted_rank_lookup_matches_canonical_multiset() -> None:
    store = kcl61.WeightedExactTaskStore({})
    store.ingest((4, 10, 41), 2)
    store.ingest((4, 11, 42), 3)
    expanded = store.expand_canonical()
    assert len(expanded) == 5
    assert [store.observation_at_rank(i) for i in range(5)] == expanded


def test_repeat_mechanism_validation_passes() -> None:
    config = kcl61.KCL1Config()
    task = kcl61.task_sequence(config)[0][1]
    result = kcl61.exact_repeat_mechanism_validation(task)
    assert result["pass"]
    assert result["weighted_unique_entries"] == 24
    assert result["raw_expanded_count"] > result["weighted_unique_entries"]


def test_current_kcl6_tasks_have_no_exact_duplicates_within_task() -> None:
    config = kcl61.KCL1Config()
    for _, task in kcl61.task_sequence(config):
        raw = kcl61.RawTaskStore.from_task(task)
        weighted = kcl61.WeightedExactTaskStore.from_task(task)
        assert raw.total_multiplicity == 24
        assert raw.unique_entries == 24
        assert weighted.total_multiplicity == 24
        assert weighted.unique_entries == 24
        assert weighted.logical_accounting()["duplicate_consolidations"] == 0


def test_storage_accounting_penalizes_count_metadata_when_no_duplicates() -> None:
    config = kcl61.KCL1Config()
    raw_stores = []
    weighted_stores = []
    for _, task in kcl61.task_sequence(config):
        raw_stores.append(kcl61.RawTaskStore.from_task(task))
        weighted_stores.append(kcl61.WeightedExactTaskStore.from_task(task))

    snapshot = kcl61._storage_snapshot(raw_stores, weighted_stores)
    assert snapshot["A_raw"]["entries"] == 96
    assert snapshot["B_weighted_exact"]["unique_entries"] == 96
    assert snapshot["entry_compression_ratio_A_over_B"] == 1.0
    assert snapshot["A_raw"]["logical_bytes"] == 96 * 24
    assert snapshot["B_weighted_exact"]["logical_bytes"] == 96 * 28
    assert snapshot["byte_compression_ratio_A_over_B"] < 1.0


def test_kcl61_replay_budget_matches_kcl6() -> None:
    assert kcl61.CONTROL_CURRENT_PER_BATCH == 15
    assert kcl61.REPLAY_PER_BATCH == 1
    assert kcl61.BATCH_SIZE == 16
    assert kcl61.REPLAY_FRACTION == 0.0625


def test_kcl61_historical_anchor_is_valid() -> None:
    anchor = kcl61._load_anchor()
    assert anchor["valid"]
    assert anchor["verdict"] == "FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON"
    assert anchor["task_order"] == list(kcl61.TASK_ORDER)
    assert anchor["replay_fraction"] == 0.0625
