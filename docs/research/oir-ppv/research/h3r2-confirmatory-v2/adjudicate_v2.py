from dataclasses import dataclass, field
from typing import Dict, List

SUPPORTED = "SUPPORTED_UNDER_TESTED_CONDITIONS"
PARTIAL = "PARTIALLY_SUPPORTED"
FALSIFIED = "FALSIFIED_UNDER_TESTED_CONDITIONS"
INCONCLUSIVE = "INCONCLUSIVE"
PROTOCOL_FAILURE = "PROTOCOL_FAILURE"

TH = {
    "baseline_gap_min": 0.05,
    "clean_margin_abs": 0.02,
    "relative_recovery_min": 0.25,
    "repro_fraction_min": 0.70,
    "env_success_min": 3,
    "noise_margin": 0.01,
    "validation_test_tolerance": 0.02,
    "min_valid_cells": 18,
    "min_valid_per_env": 4,
    "max_primary_ci_half_width": 0.02,
}

@dataclass
class Candidate:
    gap_ci_low: float
    gap_ci_high: float
    nr_point: float
    nr_ci_low: float
    nr_ci_high: float
    rr_point: float
    rr_ci_low: float
    rr_ci_high: float
    repro_fraction: float
    env_success_count: int
    noise_ci_low: float
    noise_ci_high: float
    gen_gap_ci_low: float
    gen_gap_ci_high: float
    valid_cells: int = 20
    valid_per_env: List[int] = field(default_factory=lambda: [5, 5, 5, 5])

def _tri_ge(low: float, high: float, threshold: float) -> str:
    if low >= threshold:
        return "PASS"
    if high < threshold:
        return "FAIL"
    return "UNCERTAIN"

def _tri_le(low: float, high: float, threshold: float) -> str:
    if high <= threshold:
        return "PASS"
    if low > threshold:
        return "FAIL"
    return "UNCERTAIN"

def classify_candidate(c: Candidate):
    if c.valid_cells < TH["min_valid_cells"] or min(c.valid_per_env) < TH["min_valid_per_env"]:
        return "UNCERTAIN", {"DATA": "INSUFFICIENT"}

    baseline = _tri_ge(c.gap_ci_low, c.gap_ci_high, TH["baseline_gap_min"])
    if baseline == "FAIL":
        return "NOT_ELIGIBLE", {"BASELINE": "ABSENT"}
    if baseline == "UNCERTAIN":
        return "UNCERTAIN", {"BASELINE": "UNCERTAIN"}

    half_width = (c.nr_ci_high - c.nr_ci_low) / 2.0
    precision = "PASS" if half_width <= TH["max_primary_ci_half_width"] else "UNCERTAIN"
    a_abs = _tri_ge(c.nr_ci_low, c.nr_ci_high, TH["clean_margin_abs"])
    a_rel = _tri_ge(c.rr_ci_low, c.rr_ci_high, TH["relative_recovery_min"])
    if a_abs == "PASS" and a_rel == "PASS" and precision == "PASS":
        A = "PASS"
    elif a_abs == "FAIL" or a_rel == "FAIL":
        A = "FAIL"
    else:
        A = "UNCERTAIN"

    B = "PASS" if c.repro_fraction >= TH["repro_fraction_min"] and c.env_success_count >= TH["env_success_min"] else "FAIL"
    C = _tri_le(c.noise_ci_low, c.noise_ci_high, TH["noise_margin"])
    D = _tri_le(c.gen_gap_ci_low, c.gen_gap_ci_high, TH["validation_test_tolerance"])
    E = _tri_ge(c.nr_ci_low, c.nr_ci_high, 0.0)
    criteria = {"A": A, "B": B, "C": C, "D": D, "E": E, "BASELINE": baseline, "PRECISION": precision}

    if "FAIL" in (A, D, E):
        return "DEFINITIVE_FAIL", criteria
    if "UNCERTAIN" in (A, D, E):
        return "UNCERTAIN", criteria
    if B == "PASS" and C == "PASS":
        return "FULL_SUPPORT", criteria
    if (B == "FAIL") ^ (C == "FAIL"):
        other = C if B == "FAIL" else B
        if other == "PASS":
            return "PARTIAL_SUPPORT", criteria
    if "UNCERTAIN" in (B, C):
        return "UNCERTAIN", criteria
    return "DEFINITIVE_FAIL", criteria

def adjudicate(protocol_ok: bool, access_count: int, rerun_count: int, representation_changed: bool, candidates: Dict[str, Candidate]):
    if (not protocol_ok) or access_count != 1 or rerun_count != 0 or representation_changed:
        return PROTOCOL_FAILURE, {}

    statuses = {name: classify_candidate(candidate) for name, candidate in candidates.items()}
    classes = [status[0] for status in statuses.values()]

    if "FULL_SUPPORT" in classes:
        return SUPPORTED, statuses
    if "PARTIAL_SUPPORT" in classes:
        return PARTIAL, statuses
    if "UNCERTAIN" in classes:
        return INCONCLUSIVE, statuses
    if classes and all(status == "NOT_ELIGIBLE" for status in classes):
        return INCONCLUSIVE, statuses
    return FALSIFIED, statuses
