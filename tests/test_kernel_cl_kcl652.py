from __future__ import annotations

from experiments.kernel_cl import kcl652_t4_failure_decomposition as k652


def test_seed_is_exact_anomaly_seed() -> None:
    assert k652.SEED == 9393


def test_gate_and_tolerance_are_frozen() -> None:
    assert k652.STRICT_T4_MIN == 0.95
    assert k652.TOLERANCE == 1 / 24


def test_checkpoints_are_frozen() -> None:
    assert k652.CHECKPOINTS == tuple(range(0, 251, 25))


def test_extra_current_generator_offset_is_frozen() -> None:
    assert k652.EXTRA_CURRENT_GEN_OFFSET == 4999


def test_anchor_is_valid() -> None:
    anchor = k652._load_anchor()
    assert anchor["valid"]
    assert anchor["status"] == "FAIL"
    assert anchor["verdict"] == "TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE"


def test_classification_independent_failure() -> None:
    r = {"G0":0.90,"G1":1.0,"G2_NR":1.0,"G2_XR":1.0,"G3":1.0,"G4":1.0}
    assert k652.classify(r) == "INDEPENDENT_T4_LEARNABILITY_FAILURE"


def test_classification_sequential_failure() -> None:
    r = {"G0":1.0,"G1":0.90,"G2_NR":1.0,"G2_XR":1.0,"G3":1.0,"G4":1.0}
    assert k652.classify(r) == "SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE"


def test_classification_exact_history_failure() -> None:
    r = {"G0":1.0,"G1":1.0,"G2_NR":0.90,"G2_XR":0.90,"G3":0.90,"G4":0.90}
    assert k652.classify(r) == "EXACT_HISTORY_STATE_ACQUISITION_FAILURE"


def test_classification_direct_exact_replay_interference() -> None:
    r = {"G0":1.0,"G1":1.0,"G2_NR":1.0,"G2_XR":0.90,"G3":0.90,"G4":0.95}
    assert k652.classify(r) == "DIRECT_EXACT_REPLAY_INTERFERENCE"


def test_classification_fuzzy_specific_failure() -> None:
    r = {"G0":1.0,"G1":1.0,"G2_NR":1.0,"G2_XR":1.0,"G3":1.0,"G4":0.90}
    assert k652.classify(r) == "FUZZY_REPLAY_SPECIFIC_FAILURE"
