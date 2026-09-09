import hashlib

import numpy as np

from pipeline import run_h3r as h3r_v10
from pipeline import run_h3r_v11 as h3r


def test_v11_noise_seed_binding_is_versioned_and_deterministic():
    material = b"OIR-PPV-H3R|v1.1|ENV-1|223691|17|2"
    expected = int(hashlib.sha256(material).hexdigest(), 16) & 0xFFFFFFFF
    assert h3r.h3r_noise_seed("ENV-1", 223691, 17, 2) == expected
    assert h3r.h3r_noise_seed("ENV-1", 223691, 17, 2) == expected
    assert h3r.h3r_noise_seed("ENV-1", 223691, 17, 3) != expected


def test_mixed_observation_hash_is_value_stable_not_object_pointer_based():
    left = np.array([["circle", 1.25], ["square", 2.5]], dtype=object)
    right = np.array([[str("circle"), float(1.25)], [str("square"), float(2.5)]], dtype=object)
    assert h3r._sha256_observation(left) == h3r._sha256_observation(right)
    right[0, 0] = "triangle"
    assert h3r._sha256_observation(left) != h3r._sha256_observation(right)


def test_numeric_mask_is_fit_from_train_and_noise_preserves_categorical_values():
    train = np.array(
        [
            ["circle", 0.0, 1.0],
            ["square", 1.0, 3.0],
            ["triangle", 2.0, 5.0],
            ["circle", 3.0, 7.0],
        ],
        dtype=object,
    )
    clean = np.array([["circle", 0.5, 2.0], ["square", 1.5, 4.0]], dtype=object)
    mask = h3r._numeric_channel_mask_from_train(train)
    np.testing.assert_array_equal(mask, np.array([False, True, True]))
    scale = h3r._train_scale(train, mask)
    first, evidence_a = h3r.make_noisy_replicates(
        clean, scale, mask, "ENV-1", 223691, np.array([10, 11])
    )
    second, evidence_b = h3r.make_noisy_replicates(
        clean, scale, mask, "ENV-1", 223691, np.array([10, 11])
    )
    assert evidence_a == evidence_b
    assert evidence_a["numeric_channel_indices"] == [1, 2]
    assert evidence_a["categorical_channel_indices"] == [0]
    assert evidence_a["numeric_mask_source"] == "train_observations_only"
    assert evidence_a["categorical_channels_preserved"] is True
    assert evidence_a["max_train_scale_normalized_l_inf"] <= 0.1 + 1e-12
    for left, right in zip(first, second):
        np.testing.assert_array_equal(left, right)
        np.testing.assert_array_equal(left[:, 0], clean[:, 0])
        assert not np.array_equal(np.asarray(left[:, 1:], dtype=float), np.asarray(clean[:, 1:], dtype=float))


def test_env1_mixed_schema_smoke_runs_all_frozen_learners_without_test_access():
    lineage = h3r_v10.load_frozen_inputs()
    data = h3r_v10.generate_frozen_cell("ENV-1", h3r.SMOKE_SEED, lineage)
    train_idx = np.asarray(data.splits["train"], dtype=int)
    val_idx = np.asarray(data.splits["val"], dtype=int)
    train_obs = np.asarray(data.observations[train_idx])
    val_obs = np.asarray(data.observations[val_idx])
    train_labels = np.asarray(data.labels[train_idx])
    mask = h3r._numeric_channel_mask_from_train(train_obs)
    assert mask.any()
    assert (~mask).any()
    scale = h3r._train_scale(train_obs, mask)
    noisy_replicates, validator = h3r.make_noisy_replicates(
        val_obs, scale, mask, "ENV-1", h3r.SMOKE_SEED, val_idx
    )
    assert validator["categorical_channels_preserved"] is True
    train_context, val_context = h3r._context_tables(data, train_idx, val_idx)
    learners = h3r_v10._learner_map(lineage)
    for system_id in h3r.SYSTEM_IDS:
        extractor, probe, train_repr = h3r._fit_representation_and_probe(
            learners[system_id], h3r.SMOKE_SEED, train_obs, train_context, train_labels
        )
        assert np.isfinite(train_repr).all()
        for noisy in noisy_replicates:
            noisy_repr = np.asarray(
                extractor.extract(noisy, val_context, None).invariant_representation,
                dtype=float,
            )
            prediction = np.asarray(probe.predict(noisy_repr))
            assert len(prediction) == len(val_idx)
            assert np.isfinite(noisy_repr).all()


def test_v11_runner_has_no_historical_intervention_or_v10_decisive_output_path():
    source = h3r.Path(h3r.__file__).read_text(encoding="utf-8")
    assert "env.intervene(" not in source
    assert "run_h3_closure" not in source
    assert "EXP-H3R-001" not in source
    assert "H3R_DECISIVE_ACCESS_001" not in source
