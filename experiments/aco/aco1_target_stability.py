"""ACO-1 target-stability qualification.

Zero-science preflight, lock-gated fresh collection, and deterministic
one-shot adjudication are deliberately separated. Preflight/tests never use
the ACO-1 fresh cohort.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import torch

from experiments.kernel_cl.kcl1_substrate import KCL1Config
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594

PROTOCOL = Path("docs/research/adaptive-continual-outcomes/aco1-target-stability-protocol.md")
ROOT_LINEAGE = Path("Lineage.md")
EXECUTION_LOCK = Path("docs/research/adaptive-continual-outcomes/ACO1_EXECUTION_LOCK.json")
DEFAULT_RECORDS = Path("experiments/aco/results/aco1_fresh_records.json")

POLICIES = ("A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS")
A_POLICY, B_POLICY, C_POLICY = POLICIES

STRICT_CURRENT_MIN = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN = 1 / 24
EPSILON_AUC = 0.01
EPSILON_RET = 1 / 24
EPSILON_ACC = 1 / 24

BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 71_001
MIN_Y_PRR_COUNT = 30
MIN_Y_PRR_STAGES = 2
NEAR_MARGIN_FLOOR = 0.20
LABEL_FLIP_FLOOR = 0.10

Y_PRR_MECHANISM = "MECH{P+R,R}"
Y_PRR_LABEL = f"A_ONLY|{Y_PRR_MECHANISM}"

FRESH_SEEDS = (
    714845,799297,471852,671302,797856,
    525370,494800,333039,618491,662800,
    265044,434671,501990,723350,393434,
    774787,806053,890854,613906,707487,
    415555,641958,505262,776960,428051,
    767077,464825,448672,416287,770416,
    596609,359597,454064,431281,705347,
    294795,641624,345481,326782,242385,
)
SEED_MANIFEST_SHA256 = "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91"
PROTECTED_KCL_SEEDS = tuple(k656.CONFIRM_SEEDS)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def seed_manifest_sha256(seeds: Iterable[int] = FRESH_SEEDS) -> str:
    raw = ",".join(str(int(s)) for s in seeds).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def historical_seed_numbers_from_lineage(path: Path = ROOT_LINEAGE) -> set[int]:
    if not path.exists():
        return set()
    out: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if "seed" in line.lower():
            out.update(int(x) for x in re.findall(r"\b\d{3,8}\b", line))
    return out


def validate_seed_manifest() -> dict[str, Any]:
    fresh = set(FRESH_SEEDS)
    manifest = seed_manifest_sha256()
    hist = historical_seed_numbers_from_lineage()
    protected = set(PROTECTED_KCL_SEEDS)
    valid = (
        len(FRESH_SEEDS) == 40
        and len(fresh) == 40
        and manifest == SEED_MANIFEST_SHA256
        and fresh.isdisjoint(hist)
        and fresh.isdisjoint(protected)
    )
    return {
        "count": len(FRESH_SEEDS),
        "unique_count": len(fresh),
        "manifest_sha256": manifest,
        "manifest_hash_matches": manifest == SEED_MANIFEST_SHA256,
        "historical_collisions": sorted(fresh & hist),
        "protected_collisions": sorted(fresh & protected),
        "valid": valid,
    }


def frozen_contract_snapshot() -> dict[str, Any]:
    checks = {
        "policy_identity": tuple(k655.POLICIES) == POLICIES,
        "strict_current_min": k656.STRICT_CURRENT_MIN == STRICT_CURRENT_MIN,
        "plasticity_benefit_min": k656.PLASTICITY_BENEFIT_MIN == PLASTICITY_BENEFIT_MIN,
        "retention_margin": k656.RETENTION_MARGIN == RETENTION_MARGIN,
        "failure_P": k6594.P_REASON == "PLASTICITY_SHORTFALL",
        "failure_R": k6594.R_REASON == "RETENTION_MARGIN_VIOLATION",
        "failure_A": k6594.A_REASON == "STRICT_ACCURACY_FAILURE",
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "policies": list(POLICIES),
        "thresholds": {
            "STRICT_CURRENT_MIN": STRICT_CURRENT_MIN,
            "PLASTICITY_BENEFIT_MIN": PLASTICITY_BENEFIT_MIN,
            "RETENTION_MARGIN": RETENTION_MARGIN,
        },
    }


def policy_components(
    p: dict[str, Any],
    a: dict[str, Any],
    *,
    strict_current_min: float = STRICT_CURRENT_MIN,
    plasticity_benefit_min: float = PLASTICITY_BENEFIT_MIN,
    retention_margin: float = RETENTION_MARGIN,
) -> dict[str, Any]:
    auc_delta = float(p["auc"]) - float(a["auc"])
    ret_delta = float(p["retention"]) - float(a["retention"])
    repair = (
        float(a["final_accuracy"]) < strict_current_min
        and float(p["final_accuracy"]) >= strict_current_min
    )
    plasticity = auc_delta >= plasticity_benefit_min or repair
    retention = ret_delta >= -retention_margin
    absolute = float(p["final_accuracy"]) >= strict_current_min
    return {
        "auc_delta_vs_A": auc_delta,
        "retention_delta_vs_A": ret_delta,
        "repair": repair,
        "plasticity_gain": plasticity,
        "retention_ok": retention,
        "absolute_ok": absolute,
        "safe": plasticity and retention and absolute,
    }


def hard_label(
    outcomes: dict[str, dict[str, Any]],
    *,
    strict_current_min: float = STRICT_CURRENT_MIN,
    plasticity_benefit_min: float = PLASTICITY_BENEFIT_MIN,
    retention_margin: float = RETENTION_MARGIN,
) -> dict[str, Any]:
    a = outcomes[A_POLICY]
    kwargs = {
        "strict_current_min": strict_current_min,
        "plasticity_benefit_min": plasticity_benefit_min,
        "retention_margin": retention_margin,
    }
    b = policy_components(outcomes[B_POLICY], a, **kwargs)
    c = policy_components(outcomes[C_POLICY], a, **kwargs)
    if b["safe"] and c["safe"]:
        safe_set = "B_AND_C_SAFE"
    elif b["safe"]:
        safe_set = "B_SAFE_ONLY"
    elif c["safe"]:
        safe_set = "C_SAFE_ONLY"
    else:
        safe_set = "A_ONLY"

    mechanism = None
    if safe_set == "A_ONLY":
        b_code = k6594.cause_code(k6594.failure_reasons(b))
        c_code = k6594.cause_code(k6594.failure_reasons(c))
        mechanism = k6594.mechanism_signature(b_code, c_code)
    label = safe_set if mechanism is None else f"{safe_set}|{mechanism}"
    return {
        "label": label,
        "safe_action_set": safe_set,
        "mechanism": mechanism,
        "components": {B_POLICY: b, C_POLICY: c},
        "is_Y_PRR": label == Y_PRR_LABEL,
    }


def margin_diagnostics(outcomes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    a = outcomes[A_POLICY]
    m_a = float(a["final_accuracy"]) - STRICT_CURRENT_MIN
    by_policy: dict[str, Any] = {}
    near_any = abs(m_a) <= EPSILON_ACC
    normalized = [abs(m_a) / EPSILON_ACC]

    for policy in (B_POLICY, C_POLICY):
        p = outcomes[policy]
        comp = policy_components(p, a)
        margins = {
            "m_auc": comp["auc_delta_vs_A"] - PLASTICITY_BENEFIT_MIN,
            "m_ret": comp["retention_delta_vs_A"] + RETENTION_MARGIN,
            "m_acc": float(p["final_accuracy"]) - STRICT_CURRENT_MIN,
            "m_repair": float(p["final_accuracy"]) - STRICT_CURRENT_MIN,
        }
        norms = {
            "m_auc": abs(margins["m_auc"]) / EPSILON_AUC,
            "m_ret": abs(margins["m_ret"]) / EPSILON_RET,
            "m_acc": abs(margins["m_acc"]) / EPSILON_ACC,
            "m_repair": abs(margins["m_repair"]) / EPSILON_ACC,
        }
        near = (
            abs(margins["m_auc"]) <= EPSILON_AUC
            or abs(margins["m_ret"]) <= EPSILON_RET
            or abs(margins["m_acc"]) <= EPSILON_ACC
            or abs(m_a) <= EPSILON_ACC
        )
        near_any = near_any or near
        normalized.extend(norms.values())
        by_policy[policy] = {
            "margins": margins,
            "normalized_abs_margins": norms,
            "near_margin": near,
        }

    return {
        "m_A_acc": m_a,
        "normalized_abs_m_A_acc": abs(m_a) / EPSILON_ACC,
        "policies": by_policy,
        "near_margin": near_any,
        "minimum_normalized_margin": min(normalized),
    }


def threshold_sensitivity(outcomes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    canonical = hard_label(outcomes)["label"]
    specs = {
        "plasticity_minus": (STRICT_CURRENT_MIN, PLASTICITY_BENEFIT_MIN - EPSILON_AUC, RETENTION_MARGIN),
        "plasticity_plus": (STRICT_CURRENT_MIN, PLASTICITY_BENEFIT_MIN + EPSILON_AUC, RETENTION_MARGIN),
        "retention_minus": (STRICT_CURRENT_MIN, PLASTICITY_BENEFIT_MIN, max(0.0, RETENTION_MARGIN - EPSILON_RET)),
        "retention_plus": (STRICT_CURRENT_MIN, PLASTICITY_BENEFIT_MIN, RETENTION_MARGIN + EPSILON_RET),
        "accuracy_minus": (STRICT_CURRENT_MIN - EPSILON_ACC, PLASTICITY_BENEFIT_MIN, RETENTION_MARGIN),
        "accuracy_plus": (STRICT_CURRENT_MIN + EPSILON_ACC, PLASTICITY_BENEFIT_MIN, RETENTION_MARGIN),
    }
    labels = {}
    for name, (strict, benefit, retention) in specs.items():
        labels[name] = hard_label(
            outcomes,
            strict_current_min=strict,
            plasticity_benefit_min=benefit,
            retention_margin=retention,
        )["label"]
    changed = {k: v != canonical for k, v in labels.items()}
    return {
        "canonical_label": canonical,
        "perturbed_labels": labels,
        "changed": changed,
        "label_flip": any(changed.values()),
    }


def transform_record(row: dict[str, Any]) -> dict[str, Any]:
    outcomes = row["counterfactual_outcomes"]
    return {
        "seed": int(row["seed"]),
        "boundary_index": int(row["boundary_index"]),
        "after_task": row.get("after_task"),
        "counterfactual_outcomes": outcomes,
        "hard_target": hard_label(outcomes),
        "margin_diagnostics": margin_diagnostics(outcomes),
        "threshold_sensitivity": threshold_sensitivity(outcomes),
        "integrity": dict(row.get("integrity", {})),
    }


def _percentile(values: list[float], q: float) -> float:
    xs = sorted(float(x) for x in values)
    if not xs:
        raise ValueError("empty percentile input")
    pos = (len(xs) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    f = pos - lo
    return xs[lo] * (1 - f) + xs[hi] * f


def whole_seed_bootstrap_rate(
    rows: list[dict[str, Any]],
    *,
    value_key: str,
    rng_seed: int,
) -> dict[str, float]:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(row)
    seeds = sorted(by_seed)
    point = sum(bool(r[value_key]) for r in rows) / len(rows)
    rng = random.Random(rng_seed)
    samples = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        sample = [r for s in drawn for r in by_seed[s]]
        samples.append(sum(bool(r[value_key]) for r in sample) / len(sample))
    return {
        "point": point,
        "ci_lower": _percentile(samples, 0.025),
        "ci_upper": _percentile(samples, 0.975),
    }


def adjudicate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    primary = [
        {
            "seed": int(r["seed"]),
            "boundary_index": int(r["boundary_index"]),
            "near_margin": bool(r["margin_diagnostics"]["near_margin"]),
            "label_flip": bool(r["threshold_sensitivity"]["label_flip"]),
            "minimum_normalized_margin": float(r["margin_diagnostics"]["minimum_normalized_margin"]),
        }
        for r in records
        if bool(r["hard_target"]["is_Y_PRR"])
    ]
    stages = sorted({r["boundary_index"] for r in primary})
    support_ok = len(primary) >= MIN_Y_PRR_COUNT and len(stages) >= MIN_Y_PRR_STAGES
    integrity_ok = (
        len(records) == 120
        and {int(r["seed"]) for r in records} == set(FRESH_SEEDS)
        and all(bool(r.get("integrity", {}).get("valid")) for r in records)
    )
    if not integrity_ok:
        return {
            "status": "STOP", "verdict": "STOP_INTEGRITY_OR_SUPPORT",
            "integrity_ok": False, "support_ok": support_ok,
            "primary_count": len(primary), "primary_stages": stages,
        }
    if not support_ok:
        return {
            "status": "STOP", "verdict": "TARGET_STABILITY_SUPPORT_INSUFFICIENT",
            "integrity_ok": True, "support_ok": False,
            "primary_count": len(primary), "primary_stages": stages,
        }

    near = whole_seed_bootstrap_rate(primary, value_key="near_margin", rng_seed=BOOTSTRAP_SEED)
    flip = whole_seed_bootstrap_rate(primary, value_key="label_flip", rng_seed=BOOTSTRAP_SEED + 1)
    if near["ci_lower"] >= NEAR_MARGIN_FLOOR and flip["ci_lower"] >= LABEL_FLIP_FLOOR:
        status, verdict = "PASS", "HARD_TARGET_MARGIN_INSTABILITY_SUPPORTED"
    elif near["ci_upper"] < NEAR_MARGIN_FLOOR and flip["ci_upper"] < LABEL_FLIP_FLOOR:
        status, verdict = "NEGATIVE", "HARD_TARGET_MARGIN_INSTABILITY_NOT_SUPPORTED"
    else:
        status, verdict = "INCONCLUSIVE", "TARGET_STABILITY_INCONCLUSIVE"
    mins = [r["minimum_normalized_margin"] for r in primary]
    return {
        "status": status, "verdict": verdict,
        "integrity_ok": True, "support_ok": True,
        "primary_count": len(primary), "primary_stages": stages,
        "near_margin_rate": near, "label_flip_rate": flip,
        "minimum_normalized_margin": {
            "min": min(mins), "max": max(mins), "mean": sum(mins) / len(mins)
        },
        "frozen_materiality_floors": {
            "near_margin_rate": NEAR_MARGIN_FLOOR,
            "label_flip_rate": LABEL_FLIP_FLOOR,
        },
    }


def _historical_harness_probe() -> dict[str, Any]:
    seed = int(k656.DISCOVERY_SEEDS[0])
    assert seed not in FRESH_SEEDS
    rows = k656.build_boundary_records(seed, KCL1Config())
    return {
        "seed": seed,
        "record_count": len(rows),
        "all_integrity_valid": len(rows) == 3 and all(r["integrity"]["valid"] for r in rows),
        "fresh_seed_used": seed in set(FRESH_SEEDS),
    }


def preflight() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    contract = frozen_contract_snapshot()
    seeds = validate_seed_manifest()
    harness = _historical_harness_probe()
    checks = {
        "protocol_exists": PROTOCOL.exists(),
        "frozen_contract_valid": contract["valid"],
        "seed_manifest_valid": seeds["valid"],
        "historical_harness_integrity": harness["all_integrity_valid"],
        "historical_probe_not_fresh": not harness["fresh_seed_used"],
        "fresh_result_absent": not DEFAULT_RECORDS.exists(),
        "execution_lock_absent": not EXECUTION_LOCK.exists(),
    }
    ok = all(checks.values())
    return {
        "experiment": "ACO-1",
        "phase": "ZERO_SCIENCE_PREFLIGHT",
        "status": "PASS" if ok else "FAIL",
        "verdict": "ACO1_ZERO_SCIENCE_PREFLIGHT_PASS" if ok else "ACO1_ZERO_SCIENCE_PREFLIGHT_FAIL",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL) if PROTOCOL.exists() else None,
        "seed_manifest": seeds,
        "contract": contract,
        "historical_harness_probe": harness,
        "checks": checks,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
    }


def _validate_execution_lock(lock: dict[str, Any]) -> None:
    expected = {
        "program": "ACO-1",
        "authorized": True,
        "seed_manifest_sha256": SEED_MANIFEST_SHA256,
        "protocol_sha256": sha256_file(PROTOCOL),
    }
    mismatch = {k: (v, lock.get(k)) for k, v in expected.items() if lock.get(k) != v}
    if mismatch:
        raise RuntimeError(f"ACO-1 execution lock invalid: {mismatch}")


def collect_fresh_records() -> dict[str, Any]:
    if not EXECUTION_LOCK.exists():
        raise RuntimeError("ACO-1 fresh execution is locked: ACO1_EXECUTION_LOCK.json is absent")
    _validate_execution_lock(json.loads(EXECUTION_LOCK.read_text(encoding="utf-8")))
    if not validate_seed_manifest()["valid"]:
        raise RuntimeError("ACO-1 seed manifest validation failed")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    records = []
    for seed in FRESH_SEEDS:
        source = k656.build_boundary_records(seed, KCL1Config())
        if len(source) != 3 or not all(r["integrity"]["valid"] for r in source):
            raise RuntimeError(f"counterfactual integrity failure on seed {seed}")
        records.extend(transform_record(r) for r in source)
    return {
        "experiment": "ACO-1",
        "phase": "FRESH_COLLECTION",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest_sha256": seed_manifest_sha256(),
        "records": records,
        "integrity": {
            "expected_records": 120,
            "actual_records": len(records),
            "all_source_integrity_valid": all(r["integrity"]["valid"] for r in records),
            "protected_seed_overlap": sorted(set(FRESH_SEEDS) & set(PROTECTED_KCL_SEEDS)),
        },
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phase", required=True, choices=("preflight", "collect", "adjudicate"))
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.phase == "preflight":
        out = preflight()
        _write(args.output, out)
        return 0 if out["status"] == "PASS" else 2
    if args.phase == "collect":
        _write(args.output, collect_fresh_records())
        return 0
    if args.input is None:
        p.error("--input is required for adjudicate")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    records = raw.get("records")
    if not isinstance(records, list):
        raise RuntimeError("adjudicate input must contain records list")
    _write(args.output, {
        "experiment": "ACO-1",
        "phase": "ONE_SHOT_ADJUDICATION",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL),
        "source_records_sha256": sha256_file(args.input),
        "adjudication": adjudicate_records(records),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
