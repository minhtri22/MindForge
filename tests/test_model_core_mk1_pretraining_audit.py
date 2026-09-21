from __future__ import annotations

import filecmp

from experiments.model_core.mk1.pretraining_audit import write_schedule


def _fixture_rows(count: int) -> list[dict[str, object]]:
    return [
        {
            "scene_id": f"fixture-{index:03d}",
            "renderer_family": "A",
            "sample_key": f"fixture-{index:03d}:A",
            "token_count": 3 + (index % 11),
        }
        for index in range(count)
    ]


def test_schedule_writer_is_byte_deterministic_for_fixture_seed(tmp_path) -> None:
    rows = _fixture_rows(23)
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    a = write_schedule(
        rows,
        seed=12345,
        output_path=left,
        steps=17,
        accumulation=4,
    )
    b = write_schedule(
        rows,
        seed=12345,
        output_path=right,
        steps=17,
        accumulation=4,
    )
    assert a["sha256"] == b["sha256"]
    assert a["sample_count"] == b["sample_count"] == 68
    assert a["total_tokens"] == b["total_tokens"]
    assert filecmp.cmp(left, right, shallow=False)


def test_fixture_seed_change_changes_schedule_hash(tmp_path) -> None:
    rows = _fixture_rows(23)
    first = write_schedule(
        rows,
        seed=12345,
        output_path=tmp_path / "seed-a.jsonl",
        steps=17,
        accumulation=4,
    )
    second = write_schedule(
        rows,
        seed=12346,
        output_path=tmp_path / "seed-b.jsonl",
        steps=17,
        accumulation=4,
    )
    assert first["sha256"] != second["sha256"]
