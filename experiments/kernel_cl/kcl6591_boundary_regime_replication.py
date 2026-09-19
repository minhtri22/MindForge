"""KCL-6.5.9.1: fresh boundary-regime replication.

Runs the frozen KCL-6.5.6 A/B/C counterfactual harness on 66 fresh
non-confirmatory seeds, then applies the unchanged KCL-6.5.9 taxonomy.
No classifier or controller is trained.
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
from typing import Any

import torch

from experiments.kernel_cl.kcl1_substrate import KCL1Config
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl659_boundary_regime_decomposition as k659

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6591-protocol.md")
DISCOVERY_EVIDENCE = Path(
    "experiments/kernel_cl/results/kcl659_decomposition.json"
)

REPLICATION_SEEDS = tuple(200001 + 997 * i for i in range(66))
EXPECTED_RECORDS = 66 * 3

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6591

EXPECTED_TAXONOMY = (
    "B_AND_C_SAFE",
    "B_SAFE_ONLY",
    "C_SAFE_ONLY",
    "CARRY_CATASTROPHIC_FAILURE",
    "A_SUFFICIENT",
)
MIN_INSTANCES = 5
MIN_UNIQUE_SEEDS = 3


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _frozen_contract_matches() -> bool:
    return (
        k656.STRICT_CURRENT_MIN == 0.95
        and k656.PLASTICITY_BENEFIT_MIN == 0.01
        and k656.RETENTION_MARGIN == 1 / 24
        and tuple(k659.REGIME_ORDER) == EXPECTED_TAXONOMY
        and k659.MIN_INSTANCES == MIN_INSTANCES
        and k659.MIN_UNIQUE_SEEDS == MIN_UNIQUE_SEEDS
    )


def _load_discovery_reference() -> dict[str, Any]:
    raw = json.loads(DISCOVERY_EVIDENCE.read_text(encoding="utf-8"))
    valid = (
        raw.get("experiment") == "KCL-6.5.9"
        and raw.get("status") == "NEGATIVE"
        and raw.get("verdict")
        == "NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY"
        and raw.get("integrity", {}).get("confirmatory_seeds_absent") is True
        and len(raw.get("records", [])) == 60
    )
    return {
        "valid": valid,
        "raw": raw,
        "sha256": sha256_file(DISCOVERY_EVIDENCE),
    }


def percentile_linear(values: list[float], q: float) -> float:
    xs = sorted(float(v) for v in values)
    if not xs:
        raise ValueError("empty percentile input")
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def bootstrap_prevalence(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(row)

    seeds = list(REPLICATION_SEEDS)
    rng = random.Random(BOOTSTRAP_SEED)
    samples: dict[str, list[float]] = {
        regime: [] for regime in EXPECTED_TAXONOMY
    }

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        sampled_rows = [r for s in drawn for r in by_seed[s]]
        counts = Counter(r["primary_regime"] for r in sampled_rows)
        denom = len(sampled_rows)
        for regime in EXPECTED_TAXONOMY:
            samples[regime].append(counts[regime] / denom)

    return {
        regime: {
            "ci_lower": percentile_linear(values, 0.025),
            "ci_upper": percentile_linear(values, 0.975),
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
        }
        for regime, values in samples.items()
    }


def _support_table(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for regime in EXPECTED_TAXONOMY:
        rr = [r for r in rows if r["primary_regime"] == regime]
        by_boundary = Counter(int(r["boundary_index"]) for r in rr)
        unique_seeds = len({int(r["seed"]) for r in rr})
        out[regime] = {
            "count": len(rr),
            "prevalence": len(rr) / len(rows),
            "unique_seed_count": unique_seeds,
            "supported": (
                len(rr) >= MIN_INSTANCES
                and unique_seeds >= MIN_UNIQUE_SEEDS
            ),
            "boundary_counts": {
                "1": by_boundary[1],
                "2": by_boundary[2],
                "3": by_boundary[3],
            },
        }
    return out


def _comparison(
    replication: dict[str, dict[str, Any]],
    discovery: dict[str, Any],
) -> dict[str, Any]:
    disc = discovery["raw"]["support_table"]
    return {
        regime: {
            "discovery_prevalence": float(disc[regime]["prevalence"]),
            "replication_prevalence": float(replication[regime]["prevalence"]),
            "absolute_difference": (
                float(replication[regime]["prevalence"])
                - float(disc[regime]["prevalence"])
            ),
            "discovery_supported": bool(disc[regime]["supported"]),
            "replication_supported": bool(replication[regime]["supported"]),
        }
        for regime in EXPECTED_TAXONOMY
    }


def _cohort_integrity(rows: list[dict[str, Any]]) -> dict[str, bool]:
    seed_counts = Counter(int(r["seed"]) for r in rows)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in rows:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))

    fresh = set(REPLICATION_SEEDS)
    discovery = set(k656.DISCOVERY_SEEDS)
    confirm = set(k656.CONFIRM_SEEDS)

    return {
        "frozen_contract_matches": _frozen_contract_matches(),
        "replication_seed_count_66": len(REPLICATION_SEEDS) == 66,
        "replication_seeds_unique": len(fresh) == 66,
        "record_count_198": len(rows) == EXPECTED_RECORDS,
        "three_records_per_seed": all(
            seed_counts[s] == 3 for s in REPLICATION_SEEDS
        ),
        "boundaries_1_2_3_per_seed": all(
            boundaries[s] == {1, 2, 3} for s in REPLICATION_SEEDS
        ),
        "discovery_seed_overlap_absent": fresh.isdisjoint(discovery),
        "confirmatory_seed_overlap_absent": fresh.isdisjoint(confirm),
        "counterfactual_integrity_valid": all(
            r["counterfactual_integrity_valid"] for r in rows
        ),
        "primary_regime_exactly_one": all(
            r["primary_regime"] in EXPECTED_TAXONOMY for r in rows
        ),
        "assignment_order_invariant": all(
            r["assignment_order_invariant"] for r in rows
        ),
        "classifier_trained": False,
        "controller_implemented": False,
        "confirmatory_cohort_touched": False,
        "kcl7_started": False,
    }


def run_replication() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    discovery = _load_discovery_reference()
    if not discovery["valid"]:
        return {
            "experiment": "KCL-6.5.9.1",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_REPLICATION_INVALID",
            "reason": "canonical KCL-6.5.9 discovery reference invalid",
        }

    cfg = KCL1Config()
    rows: list[dict[str, Any]] = []

    for seed in REPLICATION_SEEDS:
        source_rows = k656.build_boundary_records(seed, cfg)
        for src in source_rows:
            outcomes = src["counterfactual_outcomes"]
            dec = k659.decompose_outcomes(outcomes)

            reversed_dec = k659.decompose_outcomes(
                dict(reversed(list(outcomes.items())))
            )
            assignment_order_invariant = (
                reversed_dec["primary_regime"] == dec["primary_regime"]
                and reversed_dec[
                    "reconstructed_SAFE_RESET_OPPORTUNITY"
                ]
                == dec["reconstructed_SAFE_RESET_OPPORTUNITY"]
            )

            rows.append({
                "seed": int(seed),
                "boundary_index": int(src["boundary_index"]),
                "after_task": src.get("after_task"),
                "primary_regime": dec["primary_regime"],
                "safe_reset": dec[
                    "reconstructed_SAFE_RESET_OPPORTUNITY"
                ],
                "safe_B": dec["safe_B"],
                "safe_C": dec["safe_C"],
                "carry_failure": dec["carry_failure"],
                "policy_components": dec["policy_components"],
                "secondary_flags": dec["secondary_flags"],
                "state_signature": {
                    "H4_TASK_DRIFT_RELATIVE_L2": float(
                        src["features"]["H4_TASK_DRIFT_RELATIVE_L2"]
                    ),
                    "BOUNDARY_INDEX": float(
                        src["features"]["BOUNDARY_INDEX"]
                    ),
                },
                "counterfactual_outcomes": outcomes,
                "counterfactual_integrity_valid": bool(
                    src["integrity"]["valid"]
                ),
                "assignment_order_invariant": bool(
                    assignment_order_invariant
                ),
            })

    integrity = _cohort_integrity(rows)
    # Negative-valued governance fields are checked semantically, not via all().
    required_true = {
        k: v for k, v in integrity.items()
        if k not in {
            "classifier_trained",
            "controller_implemented",
            "confirmatory_cohort_touched",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["classifier_trained"] is False
        and integrity["controller_implemented"] is False
        and integrity["confirmatory_cohort_touched"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(required_true.values()) or not governance_ok:
        return {
            "experiment": "KCL-6.5.9.1",
            "status": "REVISE",
            "verdict": "BOUNDARY_REGIME_REPLICATION_INVALID",
            "reason": "replication integrity failed",
            "integrity": integrity,
        }

    support = _support_table(rows)

    action_replication = bool(
        support[k659.REGIME_BOTH]["supported"]
        and support[k659.REGIME_C]["supported"]
    )
    negative_replication = bool(
        support[k659.REGIME_CARRY_FAIL]["supported"]
        and support[k659.REGIME_A]["supported"]
    )
    primary_replication = bool(
        action_replication or negative_replication
    )
    unexpected_b = bool(support[k659.REGIME_B]["supported"])

    status = "PASS" if primary_replication else "NEGATIVE"
    verdict = (
        "SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED"
        if primary_replication
        else "RARE_BOUNDARY_REGIMES_NOT_SUPPORT_REPLICATED"
    )

    return {
        "experiment": "KCL-6.5.9.1",
        "status": status,
        "verdict": verdict,
        "hypothesis": "H-REP",
        "replication_routes": {
            "H_REP_ACTION": action_replication,
            "H_REP_NEGATIVE": negative_replication,
            "PRIMARY_REPLICATION": primary_replication,
            "UNEXPECTED_SUPPORTED_B_SAFE_ONLY": unexpected_b,
        },
        "cohort": {
            "seed_count": len(REPLICATION_SEEDS),
            "seeds": list(REPLICATION_SEEDS),
            "boundary_instances": len(rows),
            "fresh_non_confirmatory": True,
        },
        "planning": {
            "original_B_AND_C_SAFE_seed_rate": 2 / 20,
            "original_CARRY_CATASTROPHIC_FAILURE_seed_rate": 3 / 20,
            "P_ge5_n66_p010": 0.8018986986838187,
            "P_ge5_n66_p015": 0.977382701353009,
            "note": "planning assumptions only; not adjudication evidence",
        },
        "support_table": support,
        "bootstrap_prevalence_95pct": bootstrap_prevalence(rows),
        "discovery_to_replication": _comparison(support, discovery),
        "secondary_flag_counts": dict(Counter(
            name
            for r in rows
            for name, value in r["secondary_flags"].items()
            if value
        )),
        "integrity": integrity,
        "protocol": {
            "path": str(PROTOCOL),
            "sha256": sha256_file(PROTOCOL),
            "min_instances": MIN_INSTANCES,
            "min_unique_seeds": MIN_UNIQUE_SEEDS,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "discovery_reference": {
            "path": str(DISCOVERY_EVIDENCE),
            "sha256": discovery["sha256"],
            "status": discovery["raw"]["status"],
            "verdict": discovery["raw"]["verdict"],
        },
        "records": rows,
        "environment": {
            "git_commit": git_commit(),
            "torch_version": torch.__version__,
            "deterministic_algorithms": True,
        },
        "governance": {
            "classifier_trained": False,
            "controller_implemented": False,
            "confirmatory_cohort_touched": False,
            "kcl7_started": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/kernel_cl/results/kcl6591_replication.json"
        ),
    )
    args = parser.parse_args()

    result = run_replication()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "replication_routes": result.get("replication_routes"),
        "support_table": result.get("support_table"),
        "secondary_flag_counts": result.get("secondary_flag_counts"),
        "integrity": result.get("integrity"),
        "protocol": result.get("protocol"),
        "discovery_reference": result.get("discovery_reference"),
        "environment": result.get("environment"),
    }, sort_keys=True))
    return 0 if result["status"] in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
