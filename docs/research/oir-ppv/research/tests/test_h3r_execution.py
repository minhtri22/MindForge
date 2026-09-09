import hashlib
import json

import numpy as np

from pipeline import run_h3r


def test_h3r_static_execution_contract_matches_freeze_package():
    result = run_h3r.validate_static_contract(require_pristine_access_log=True)
    assert result["status"] == "PASS"
    assert all(check["passed"] for check in result["checks"])


def test_h3r_uint32_sha256_binding_is_low_32_bits_and_deterministic():
    material = b"OIR-PPV-H3R|v1.0|ENV-1|271828|17|2"
    expected = int(hashlib.sha256(material).hexdigest(), 16) & 0xFFFFFFFF
    assert run_h3r.h3r_noise_seed("ENV-1", 271828, 17, 2) == expected
    assert run_h3r.h3r_noise_seed("ENV-1", 271828, 17, 2) == expected
    assert run_h3r.h3r_noise_seed("ENV-1", 271828, 17, 3) != expected


def test_h3r_noise_replicates_are_bounded_and_reproducible():
    train = np.array(
        [[0.0, 1.0, 2.0], [1.0, 3.0, 2.0], [2.0, 5.0, 2.0], [3.0, 7.0, 2.0]],
        dtype=float,
    )
    clean = np.array([[0.5, 2.0, 2.0], [1.5, 4.0, 2.0]], dtype=float)
    scale = run_h3r._train_scale(train)
    first, evidence_a = run_h3r.make_noisy_replicates(
        clean, scale, "ENV-2", 314159, np.array([10, 11])
    )
    second, evidence_b = run_h3r.make_noisy_replicates(
        clean, scale, "ENV-2", 314159, np.array([10, 11])
    )
    assert len(first) == 4
    assert evidence_a == evidence_b
    assert evidence_a["validator_passed"] is True
    assert evidence_a["max_train_scale_normalized_l_inf"] <= 0.1 + 1e-12
    for left, right in zip(first, second):
        np.testing.assert_array_equal(left, right)
        assert not np.array_equal(left, clean)


def test_h3r_bootstrap_is_deterministic_equal_environment_weighted():
    effects = {
        "ENV-1": [0.0] * 5,
        "ENV-2": [0.1] * 5,
        "ENV-3": [0.2] * 5,
        "ENV-4": [0.3] * 5,
    }
    indices = run_h3r._bootstrap_indices()
    first = run_h3r._stratified_bootstrap(effects, indices)
    second = run_h3r._stratified_bootstrap(effects, indices)
    assert first == second
    assert np.isclose(first["estimate"], 0.15)
    assert np.isclose(first["ci_low"], 0.15)
    assert np.isclose(first["ci_high"], 0.15)


def test_h3r_authorization_is_hash_bound(tmp_path):
    auth = {
        "execution_authorized": True,
        "protocol_sha256": run_h3r._sha256_path(run_h3r.PROTOCOL_MD),
        "test_manifest_sha256": run_h3r._sha256_path(run_h3r.TEST_MANIFEST),
    }
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(auth), encoding="utf-8")
    assert run_h3r._load_authorization(path)["execution_authorized"] is True


def test_h3r_runner_has_no_historical_intervention_path():
    source = run_h3r.Path(run_h3r.__file__).read_text(encoding="utf-8")
    assert "env.intervene(" not in source
    assert "run_h3_closure" not in source
