"""KCL-6.5.1: independent stability–plasticity tradeoff confirmation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
from pathlib import Path
from typing import Any

import torch

from experiments.kernel_cl.kcl1_substrate import KCL1Config, build_model, parameter_count
from experiments.kernel_cl import kcl65_specificity_ab as k65

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl651-protocol.md")
KCL65_EVIDENCE = Path("experiments/kernel_cl/results/kcl65_summary.json")

FINAL_SEEDS = (
    5555, 5757, 5959, 6161, 6363,
    6565, 6767, 6969, 7171, 7373,
    7575, 7777, 7979, 8181, 8383,
    8585, 8787, 8989, 9191, 9393,
)

BOOTSTRAP_RESAMPLES = 20000
BOOTSTRAP_SEED = 651651
CONFIDENCE_LEVEL = 0.95

PRACTICAL_MARGIN = 1 / 24
STRICT_T4_MIN = 0.95
RETENTION_MEAN_GAIN_MIN = 0.10
RETENTION_POSITIVE_SEEDS_MIN = 16


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "pstdev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("empty percentile input")
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def paired_bootstrap_mean_ci(
    values: list[float],
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    if len(values) != len(FINAL_SEEDS):
        raise ValueError("bootstrap requires exactly the frozen N=20 cohort")
    rng = random.Random(seed)
    n = len(values)
    means: list[float] = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.fmean(sample))
    means.sort()
    alpha = (1 - CONFIDENCE_LEVEL) / 2
    return {
        "mean": statistics.fmean(values),
        "ci_lower": _percentile(means, alpha),
        "ci_upper": _percentile(means, 1 - alpha),
        "confidence_level": CONFIDENCE_LEVEL,
        "resamples": resamples,
        "bootstrap_seed": seed,
    }


def _load_kcl65_anchor() -> dict[str, Any]:
    raw = json.loads(KCL65_EVIDENCE.read_text(encoding="utf-8"))
    h = raw.get("hypotheses", {})
    valid = (
        raw.get("status") == "FAIL"
        and raw.get("verdict") == "TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS"
        and h.get("H_S1_target_specificity") is True
        and h.get("H_S2_matched_query_null") is True
        and h.get("H_S3_targeted_information_improves_CL") is True
        and h.get("H_S4_strict_plasticity_retained") is False
        and h.get("H_S5_query_storage_integrity") is True
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "hypotheses": h,
        "historical_mean_delta_R": raw.get("aggregates", {}).get("prior_gain_E_minus_F", {}).get("mean"),
        "historical_mean_delta_P": raw.get("aggregates", {}).get("T4_gain_E_minus_F", {}).get("mean"),
        "historical_seeds": raw.get("final_seeds"),
        "sha256": _sha256(KCL65_EVIDENCE),
    }


def classify_plasticity(ci: dict[str, Any]) -> str:
    lower = float(ci["ci_lower"])
    upper = float(ci["ci_upper"])

    if upper <= -PRACTICAL_MARGIN:
        return "MATERIAL_TRADEOFF_CONFIRMED"
    if upper < 0 and lower > -PRACTICAL_MARGIN:
        return "SMALL_SYSTEMATIC_TRADEOFF_WITHIN_MARGIN"
    if lower > -PRACTICAL_MARGIN and lower <= 0 <= upper:
        return "NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN"
    return "TRADEOFF_CONFIRMATION_INCONCLUSIVE"


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    anchor = _load_kcl65_anchor()
    config = KCL1Config()

    rows: list[dict[str, Any]] = []
    if anchor["valid"]:
        for seed in FINAL_SEEDS:
            row = k65.run_seed(seed, config)
            rows.append({
                "seed": seed,
                "E_mean_prior": row["E_mean_prior"],
                "F_mean_prior": row["F_mean_prior"],
                "DeltaR": row["prior_gain_E_minus_F"],
                "E_T4": row["E_T4"],
                "F_T4": row["F_T4"],
                "DeltaP": row["T4_gain_E_minus_F"],
                "E_worst_prior": row["E_worst_prior"],
                "F_worst_prior": row["F_worst_prior"],
                "total_queries_E": row["total_queries_E"],
                "total_queries_F": row["total_queries_F"],
                "E_exact_match_rates": row["E_exact_match_rates"],
                "F_exact_match_rates": row["F_exact_match_rates"],
                "persistent_storage": row["persistent_storage"],
                "integrity": row["integrity"],
            })

    integrity_valid = (
        anchor["valid"]
        and len(rows) == len(FINAL_SEEDS)
        and [r["seed"] for r in rows] == list(FINAL_SEEDS)
        and all(all(v is True for v in r["integrity"].values()) for r in rows)
        and all(
            r["total_queries_E"] == r["total_queries_F"] == k65.EXPECTED_TOTAL_QUERIES
            for r in rows
        )
    )

    delta_r = [float(r["DeltaR"]) for r in rows]
    delta_p = [float(r["DeltaP"]) for r in rows]

    retention_ci = paired_bootstrap_mean_ci(delta_r) if rows else None
    plasticity_ci = paired_bootstrap_mean_ci(delta_p) if rows else None

    retention_positive_count = sum(x > 0 for x in delta_r)
    retention_replicated = (
        integrity_valid
        and retention_ci is not None
        and retention_ci["mean"] >= RETENTION_MEAN_GAIN_MIN
        and retention_ci["ci_lower"] > 0
        and retention_positive_count >= RETENTION_POSITIVE_SEEDS_MIN
    )

    absolute_e_gate = (
        integrity_valid
        and all(r["E_T4"] >= STRICT_T4_MIN for r in rows)
    )

    classification = (
        classify_plasticity(plasticity_ci)
        if plasticity_ci is not None
        else "TRADEOFF_CONFIRMATION_INCONCLUSIVE"
    )

    if not integrity_valid:
        status = "REVISE"
        verdict = "TRADEOFF_CONFIRMATION_INVALID"
    elif not absolute_e_gate:
        status = "FAIL"
        verdict = "TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE"
    elif not retention_replicated:
        status = "NEGATIVE"
        verdict = "RETENTION_SPECIFICITY_NOT_REPLICATED"
    else:
        status = "PASS"
        verdict = classification

    sign_counts = {
        "negative": sum(x < 0 for x in delta_p),
        "zero": sum(x == 0 for x in delta_p),
        "positive": sum(x > 0 for x in delta_p),
    }

    pooled_secondary = None
    if rows:
        historical = json.loads(KCL65_EVIDENCE.read_text(encoding="utf-8"))
        historical_delta_r = [
            float(x["prior_gain_E_minus_F"]) for x in historical.get("per_seed", [])
        ]
        historical_delta_p = [
            float(x["T4_gain_E_minus_F"]) for x in historical.get("per_seed", [])
        ]
        pooled_secondary = {
            "note": "secondary descriptive only; not used for primary classification",
            "N": len(historical_delta_r) + len(delta_r),
            "mean_DeltaR": statistics.fmean(historical_delta_r + delta_r),
            "mean_DeltaP": statistics.fmean(historical_delta_p + delta_p),
        }

    return {
        "experiment": "KCL-6.5.1",
        "status": status,
        "verdict": verdict,
        "primary_cohort": {
            "N": len(FINAL_SEEDS),
            "seeds": list(FINAL_SEEDS),
            "independent_of_KCL65": True,
        },
        "historical_anchor": anchor,
        "policy": {
            "E_F_policy_changed_from_KCL65": False,
            "replay_budget_changed": False,
            "query_budget_changed": False,
            "fuzzy_representation_changed": False,
        },
        "primary_endpoints": {
            "DeltaR_definition": "E_final_mean_prior_accuracy - F_final_mean_prior_accuracy",
            "DeltaP_definition": "E_final_T4_accuracy - F_final_T4_accuracy",
            "DeltaR": {
                "stats": _stats(delta_r) if delta_r else None,
                "bootstrap": retention_ci,
                "positive_seed_count": retention_positive_count,
                "replication_gate_pass": retention_replicated,
            },
            "DeltaP": {
                "stats": _stats(delta_p) if delta_p else None,
                "bootstrap": plasticity_ci,
                "sign_counts": sign_counts,
                "practical_margin": PRACTICAL_MARGIN,
                "classification": classification,
            },
        },
        "absolute_E_plasticity": {
            "strict_T4_min": STRICT_T4_MIN,
            "pass": absolute_e_gate,
            "minimum_E_T4": min((r["E_T4"] for r in rows), default=None),
            "mean_E_T4": statistics.fmean([r["E_T4"] for r in rows]) if rows else None,
        },
        "per_seed": rows,
        "secondary_pooled_context": pooled_secondary,
        "bootstrap_contract": {
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
            "confidence_level": CONFIDENCE_LEVEL,
            "method": "paired nonparametric percentile bootstrap over fresh seeds",
        },
        "integrity": {
            "historical_anchor_valid": anchor["valid"],
            "paired_contract_valid": integrity_valid,
            "model_architecture_changed": False,
            "kcl7_started": False,
        },
        "model_parameter_count": parameter_count(build_model(config, FINAL_SEEDS[0])),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl651_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] in {"PASS", "NEGATIVE"}:
        return 0
    if result["status"] == "REVISE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
