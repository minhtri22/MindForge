from __future__ import annotations

from experiments.kernel_cl import kcl62_reconstructive_memory_abc as k62


def test_reuses_same_abc_seeds() -> None:
    assert k62.FINAL_SEEDS == (3333, 3535, 3737, 3939, 4141)


def test_schema_infers_all_tasks_exactly() -> None:
    config = k62.KCL1Config()
    stores = [k62.ReconstructiveStore.from_task(task) for _, task in k62.task_sequence(config)]
    assert len(stores) == 4
    assert all(s.reconstructed() == s.canonical_original() for s in stores)
    assert all(len(s.residuals) == 0 for s in stores)
    assert all(s.coverage == 1.0 for s in stores)


def test_schema_discovers_prefix_and_suffix_positions() -> None:
    config = k62.KCL1Config()
    stores = [k62.ReconstructiveStore.from_task(task) for _, task in k62.task_sequence(config)]
    assert [s.schema.varying_position for s in stores] == [1, 1, 1, 0]


def test_schema_parameters_come_from_observations() -> None:
    config = k62.KCL1Config()
    stores = [k62.ReconstructiveStore.from_task(task) for _, task in k62.task_sequence(config)]
    assert [(s.schema.multiplier, s.schema.offset) for s in stores] == [
        (5, 1), (7, 3), (17, 4), (19, 7)
    ]


def test_reconstructive_store_is_smaller_on_current_workload() -> None:
    config = k62.KCL1Config()
    stores = [k62.ReconstructiveStore.from_task(task) for _, task in k62.task_sequence(config)]
    c_bytes = sum(s.logical_bytes for s in stores)
    assert c_bytes == 4 * 41
    assert 2304 / c_bytes >= 2.0


def test_kcl62_anchors_are_valid() -> None:
    anchors = k62._load_anchors()
    assert anchors["valid"]
    assert anchors["kcl6_valid"]
    assert anchors["kcl61_valid"]


def test_replay_budget_is_unchanged() -> None:
    assert k62.CURRENT_PER_BATCH == 15
    assert k62.REPLAY_PER_BATCH == 1
    assert k62.BATCH_SIZE == 16
    assert k62.REPLAY_FRACTION == 0.0625


def test_gates_are_frozen() -> None:
    assert k62.BEHAVIOR_TOLERANCE == 1 / 24
    assert k62.T4_ACCURACY_MIN == 0.95
    assert k62.A_OVER_C_BYTE_COMPRESSION_MIN == 2.0
    assert k62.C_RESIDUAL_RATE_MAX == 0.25
