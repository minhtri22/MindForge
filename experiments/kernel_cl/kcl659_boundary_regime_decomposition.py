"""KCL-6.5.9: frozen boundary regime decomposition.

This milestone reads canonical KCL-6.5.8 discovery evidence only.
It does not train models, rerun counterfactuals, or touch confirmatory seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl659-protocol.md")
SOURCE = Path("experiments/kernel_cl/results/kcl658_discovery.json")

EXPECTED_SOURCE_BLOB_SHA = "0a956a70ddb65d12a413176f84910ce889359973"
EXPECTED_SOURCE_STATUS = "NEGATIVE"
EXPECTED_SOURCE_VERDICT = "LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED"

DISCOVERY_SEEDS = (
    9595, 9797, 9999, 10201, 10403,
    10605, 10807, 11009, 11211, 11413,
    11615, 11817, 12019, 12221, 12423,
    12625, 12827, 13029, 13231, 13433,
)
CONFIRM_SEEDS = (
    13635, 13837, 14039, 14241, 14443,
    14645, 14847, 15049, 15251, 15453,
    15655, 15857, 16059, 16261, 16463,
    16665, 16867, 17069, 17271, 17473,
)

A = "A_CARRY_ALL"
B = "B_RESET_ALL"
C = "C_CARRY_STEP_RESET_MOMENTS"

STRICT_CURRENT_MIN = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN = 1 / 24

REGIME_BOTH = "B_AND_C_SAFE"
REGIME_B = "B_SAFE_ONLY"
REGIME_C = "C_SAFE_ONLY"
REGIME_CARRY_FAIL = "CARRY_CATASTROPHIC_FAILURE"
REGIME_A = "A_SUFFICIENT"

REGIME_ORDER = (
    REGIME_BOTH,
    REGIME_B,
    REGIME_C,
    REGIME_CARRY_FAIL,
    REGIME_A,
)
POSITIVE_REGIMES = (REGIME_BOTH, REGIME_B, REGIME_C)
NEGATIVE_REGIMES = (REGIME_CARRY_FAIL, REGIME_A)

MIN_INSTANCES = 5
MIN_UNIQUE_SEEDS = 3
BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 659659


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "hash-object", str(path)],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def policy_components(p: dict[str, Any], a: dict[str, Any]) -> dict[str, Any]:
    auc_delta = float(p["auc"]) - float(a["auc"])
    final_delta = float(p["final_accuracy"]) - float(a["final_accuracy"])
    retention_delta = float(p["retention"]) - float(a["retention"])
    plasticity_gain = (
        auc_delta >= PLASTICITY_BENEFIT_MIN
        or (
            float(a["final_accuracy"]) < STRICT_CURRENT_MIN
            and float(p["final_accuracy"]) >= STRICT_CURRENT_MIN
        )
    )
    retention_ok = retention_delta >= -RETENTION_MARGIN
    absolute_ok = float(p["final_accuracy"]) >= STRICT_CURRENT_MIN
    return {
        "auc_delta_vs_A": auc_delta,
        "final_accuracy_delta_vs_A": final_delta,
        "retention_delta_vs_A": retention_delta,
        "plasticity_gain": bool(plasticity_gain),
        "retention_ok": bool(retention_ok),
        "absolute_ok": bool(absolute_ok),
        "safe_beneficial": bool(plasticity_gain and retention_ok and absolute_ok),
    }


def decompose_outcomes(outcomes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    # Explicit key lookup makes assignment invariant to mapping presentation order.
    a = outcomes[A]
    b = policy_components(outcomes[B], a)
    c = policy_components(outcomes[C], a)
    safe_b = bool(b["safe_beneficial"])
    safe_c = bool(c["safe_beneficial"])
    carry_failure = float(a["final_accuracy"]) < STRICT_CURRENT_MIN

    if safe_b and safe_c:
        regime = REGIME_BOTH
    elif safe_b and not safe_c:
        regime = REGIME_B
    elif safe_c and not safe_b:
        regime = REGIME_C
    elif carry_failure:
        regime = REGIME_CARRY_FAIL
    else:
        regime = REGIME_A

    old_binary = regime in POSITIVE_REGIMES
    reset_gain_retention_cost = any(
        x["plasticity_gain"] and x["absolute_ok"] and not x["retention_ok"]
        for x in (b, c)
    )
    reset_rescue_retention_cost = bool(
        carry_failure
        and any(
            float(outcomes[p]["final_accuracy"]) >= STRICT_CURRENT_MIN
            and not x["retention_ok"]
            for p, x in ((B, b), (C, c))
        )
    )

    return {
        "primary_regime": regime,
        "safe_B": safe_b,
        "safe_C": safe_c,
        "carry_failure": bool(carry_failure),
        "reconstructed_SAFE_RESET_OPPORTUNITY": bool(old_binary),
        "policy_components": {B: b, C: c},
        "secondary_flags": {
            "RESET_PLASTICITY_GAIN_RETENTION_COST": bool(
                reset_gain_retention_cost
            ),
            "RESET_RESCUES_CARRY_FAILURE_WITH_RETENTION_COST": bool(
                reset_rescue_retention_cost
            ),
        },
    }


def _source_contract(raw: dict[str, Any]) -> dict[str, Any]:
    records = raw.get("records", [])
    seeds = [int(r["seed"]) for r in records if "seed" in r]
    seed_counts = Counter(seeds)
    boundaries_by_seed: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries_by_seed[int(r["seed"])].add(int(r["boundary_index"]))

    source_blob = git_blob_sha(SOURCE)
    integrity_records = all(
        r.get("integrity", {}).get("valid") is True
        and r.get("integrity", {}).get("canonical_reproduction") is True
        for r in records
    )

    checks = {
        "source_blob_sha_matches": source_blob == EXPECTED_SOURCE_BLOB_SHA,
        "status_matches": raw.get("status") == EXPECTED_SOURCE_STATUS,
        "verdict_matches": raw.get("verdict") == EXPECTED_SOURCE_VERDICT,
        "root_integrity_valid": raw.get("integrity", {}).get("valid") is True,
        "record_count_60": len(records) == 60,
        "discovery_seed_set_exact": set(seeds) == set(DISCOVERY_SEEDS),
        "three_records_per_seed": all(
            seed_counts[s] == 3 for s in DISCOVERY_SEEDS
        ),
        "boundaries_1_2_3_per_seed": all(
            boundaries_by_seed[s] == {1, 2, 3} for s in DISCOVERY_SEEDS
        ),
        "confirmatory_seeds_absent": set(seeds).isdisjoint(CONFIRM_SEEDS),
        "record_integrity_valid": integrity_records,
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "source_blob_sha": source_blob,
        "source_sha256": sha256_file(SOURCE),
        "records": records,
    }


def supported(count: int, unique_seeds: int) -> bool:
    return count >= MIN_INSTANCES and unique_seeds >= MIN_UNIQUE_SEEDS


def percentile_linear(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("empty percentile input")
    xs = sorted(float(v) for v in values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def iqr_summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "median": None, "q1": None, "q3": None, "iqr": None}
    q1 = percentile_linear(values, 0.25)
    q3 = percentile_linear(values, 0.75)
    return {
        "n": len(values),
        "median": float(median(values)),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
    }


def entropy_bits(labels: list[str | bool]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    n = len(labels)
    return -sum(
        (c / n) * math.log2(c / n)
        for c in counts.values()
        if c
    )


def conditional_regime_entropy(rows: list[dict[str, Any]]) -> float:
    n = len(rows)
    out = 0.0
    for binary in (False, True):
        subset = [
            r["primary_regime"]
            for r in rows
            if r["safe_reset"] is binary
        ]
        if subset:
            out += (len(subset) / n) * entropy_bits(subset)
    return out


def bootstrap_prevalence(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    seeds = list(DISCOVERY_SEEDS)
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_seed[int(r["seed"])].append(r)

    rng = random.Random(BOOTSTRAP_SEED)
    draws: dict[str, list[float]] = {regime: [] for regime in REGIME_ORDER}
    for _ in range(BOOTSTRAP_RESAMPLES):
        sampled = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        sampled_rows = [r for seed in sampled for r in by_seed[seed]]
        counts = Counter(r["primary_regime"] for r in sampled_rows)
        denom = len(sampled_rows)
        for regime in REGIME_ORDER:
            draws[regime].append(counts[regime] / denom)

    return {
        regime: {
            "ci_lower": percentile_linear(vals, 0.025),
            "ci_upper": percentile_linear(vals, 0.975),
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
        }
        for regime, vals in draws.items()
    }


def run_decomposition() -> dict[str, Any]:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    source = _source_contract(raw)
    if not source["valid"]:
        return {
            "experiment": "KCL-6.5.9",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_DECOMPOSITION_INVALID",
            "reason": "canonical KCL-6.5.8 source contract failed",
            "integrity": source["checks"],
            "source": {
                "path": str(SOURCE),
                "git_blob_sha": source["source_blob_sha"],
                "sha256": source["source_sha256"],
            },
        }

    rows = []
    label_match = True
    key_order_invariance = True

    for r in source["records"]:
        outcomes = r["counterfactual_outcomes"]
        d = decompose_outcomes(outcomes)

        old = bool(r["labels"]["SAFE_RESET_OPPORTUNITY"])
        label_match = label_match and (
            old == d["reconstructed_SAFE_RESET_OPPORTUNITY"]
        )

        reversed_outcomes = dict(reversed(list(outcomes.items())))
        d_reversed = decompose_outcomes(reversed_outcomes)
        key_order_invariance = key_order_invariance and (
            d_reversed["primary_regime"] == d["primary_regime"]
            and d_reversed["reconstructed_SAFE_RESET_OPPORTUNITY"]
            == d["reconstructed_SAFE_RESET_OPPORTUNITY"]
        )

        rows.append({
            "seed": int(r["seed"]),
            "boundary_index": int(r["boundary_index"]),
            "after_task": r.get("after_task"),
            "primary_regime": d["primary_regime"],
            "safe_reset": d["reconstructed_SAFE_RESET_OPPORTUNITY"],
            "safe_B": d["safe_B"],
            "safe_C": d["safe_C"],
            "carry_failure": d["carry_failure"],
            "secondary_flags": d["secondary_flags"],
            "policy_components": d["policy_components"],
            "state_signature": {
                "H4_TASK_DRIFT_RELATIVE_L2": float(
                    r["features"]["H4_TASK_DRIFT_RELATIVE_L2"]
                ),
                "BOUNDARY_INDEX": float(r["features"]["BOUNDARY_INDEX"]),
            },
        })

    exactly_one = all(r["primary_regime"] in REGIME_ORDER for r in rows)
    collective = len(rows) == 60 and sum(
        Counter(r["primary_regime"] for r in rows).values()
    ) == 60

    integrity = {
        **source["checks"],
        "binary_labels_reproduced_60_of_60": bool(label_match),
        "primary_regime_exactly_one": bool(exactly_one),
        "taxonomy_collectively_exhaustive": bool(collective),
        "assignment_order_invariant": bool(key_order_invariance),
        "no_model_training_invoked": True,
        "confirmatory_workflow_created": False,
        "rule_artifact_created": False,
    }
    if not all(integrity.values()):
        return {
            "experiment": "KCL-6.5.9",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_DECOMPOSITION_INVALID",
            "reason": "decomposition integrity failed",
            "integrity": integrity,
            "source": {
                "path": str(SOURCE),
                "git_blob_sha": source["source_blob_sha"],
                "sha256": source["source_sha256"],
            },
        }

    counts = Counter(r["primary_regime"] for r in rows)
    support_table = {}
    for regime in REGIME_ORDER:
        rr = [r for r in rows if r["primary_regime"] == regime]
        by_boundary = Counter(r["boundary_index"] for r in rr)
        uniq = len({r["seed"] for r in rr})
        h4 = [r["state_signature"]["H4_TASK_DRIFT_RELATIVE_L2"] for r in rr]
        support_table[regime] = {
            "count": len(rr),
            "prevalence": len(rr) / len(rows),
            "unique_seed_count": uniq,
            "supported": supported(len(rr), uniq),
            "boundary_counts": {
                "1": by_boundary[1],
                "2": by_boundary[2],
                "3": by_boundary[3],
            },
            "H4_TASK_DRIFT_RELATIVE_L2": iqr_summary(h4),
        }

    action_supported = sum(
        bool(support_table[x]["supported"]) for x in POSITIVE_REGIMES
    ) >= 2
    negative_supported = all(
        bool(support_table[x]["supported"]) for x in NEGATIVE_REGIMES
    )
    binary_supported = bool(action_supported or negative_supported)

    status = "PASS" if binary_supported else "NEGATIVE"
    verdict = (
        "BINARY_SAFE_RESET_TARGET_HIDES_SUPPORTED_CAUSAL_REGIMES"
        if binary_supported
        else "NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY"
    )

    safe_labels = [bool(r["safe_reset"]) for r in rows]
    regime_labels = [r["primary_regime"] for r in rows]
    entropies = {
        "H_REGIME_bits": entropy_bits(regime_labels),
        "H_SAFE_RESET_bits": entropy_bits(safe_labels),
        "H_REGIME_given_SAFE_RESET_bits": conditional_regime_entropy(rows),
        "interpretation": (
            "conditional entropy is regime information discarded by binary "
            "SAFE_RESET collapse"
        ),
    }

    flag_counts = Counter()
    for r in rows:
        for name, value in r["secondary_flags"].items():
            if value:
                flag_counts[name] += 1

    return {
        "experiment": "KCL-6.5.9",
        "status": status,
        "verdict": verdict,
        "hypothesis": "H-BRD",
        "scientific_question": (
            "Does binary SAFE_RESET_OPPORTUNITY hide multiple supported "
            "counterfactual causal regimes?"
        ),
        "source": {
            "path": str(SOURCE),
            "git_blob_sha": source["source_blob_sha"],
            "sha256": source["source_sha256"],
            "records": len(rows),
            "discovery_seeds": list(DISCOVERY_SEEDS),
        },
        "protocol": {
            "path": str(PROTOCOL),
            "sha256": sha256_file(PROTOCOL),
            "min_instances": MIN_INSTANCES,
            "min_unique_seeds": MIN_UNIQUE_SEEDS,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "integrity": integrity,
        "heterogeneity": {
            "SUPPORTED_ACTION_HETEROGENEITY": action_supported,
            "SUPPORTED_NEGATIVE_HETEROGENEITY": negative_supported,
            "SUPPORTED_BINARY_HETEROGENEITY": binary_supported,
        },
        "support_table": support_table,
        "bootstrap_prevalence_95pct": bootstrap_prevalence(rows),
        "binary_compression_information": entropies,
        "secondary_flag_counts": dict(flag_counts),
        "records": rows,
        "environment": {
            "git_commit": git_commit(),
            "python_stdlib_only": True,
        },
        "governance": {
            "confirmatory_cohort_touched": False,
            "kcl7_started": False,
            "classifier_trained": False,
            "controller_implemented": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl659_decomposition.json"),
    )
    args = parser.parse_args()

    result = run_decomposition()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
