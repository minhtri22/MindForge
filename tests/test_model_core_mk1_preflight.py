from __future__ import annotations

from experiments.model_core.mk1.contracts import C_SLICES, D_C, D_Z, Z1_LABELS, Z_SLICES
from experiments.model_core.mk1.data_contract import build_fixture_scene, render_surface
from experiments.model_core.mk1.preflight import _projected_generator_qa
from experiments.model_core.mk1.recompose import canonical_equal, recompose_gold_z
from experiments.model_core.mk1.trainer import deterministic_sample_indices


def test_tensor_layout_is_frozen() -> None:
    assert D_Z == 70
    assert D_C == 34
    assert (Z_SLICES["z1"].start, Z_SLICES["z4"].stop) == (0, 70)
    assert (C_SLICES["c1"].start, C_SLICES["c5"].stop) == (0, 34)


def test_fixture_gold_c_is_exact_recomposition() -> None:
    for index in range(32):
        scene = build_fixture_scene(index)
        assert canonical_equal(scene.gold_c, recompose_gold_z(scene.gold_z))


def test_renderer_does_not_emit_exact_target_names() -> None:
    for index in range(16):
        scene = build_fixture_scene(index)
        for family in ("A", "B", "C"):
            text = render_surface(scene, family)
            assert not any(label in text for label in Z1_LABELS)


def test_deterministic_sample_schedule_matches() -> None:
    left = deterministic_sample_indices(23, 12345)
    right = deterministic_sample_indices(23, 12345)
    assert [next(left) for _ in range(128)] == [next(right) for _ in range(128)]



def test_amendment_003_projected_generator_qa_passes() -> None:
    result = _projected_generator_qa()
    assert result["status"] == "PASS"
    assert result["canonical_z_unique"] is True
    assert result["all_scenes_have_scalar"] is True
    assert result["confirmatory_multifactor_fraction"] >= 0.30
    assert result["minimum_train_z1_support"] >= 100
    assert result["minimum_confirmatory_z1_support"] >= 40
    assert result["minimum_train_scalar_presence"] >= 100
    assert result["minimum_confirmatory_scalar_presence"] >= 40
    assert result["minimum_train_scope_relation_support"] >= 100
    assert result["minimum_confirmatory_scope_relation_support"] >= 40
    assert result["minimum_train_z4_binary_cell"] >= 100
    assert result["minimum_confirmatory_z4_binary_cell"] >= 40
    assert result["minimum_train_c1_binary_cell"] >= 100
    assert result["minimum_confirmatory_c1_binary_cell"] >= 40
    assert result["minimum_train_c5_binary_cell"] >= 100
    assert result["minimum_confirmatory_c5_binary_cell"] >= 40
