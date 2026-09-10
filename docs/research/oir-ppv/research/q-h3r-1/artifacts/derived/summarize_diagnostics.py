from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def corr(rows: list[dict], x: str, y: str) -> dict:
    pairs = []
    for row in rows:
        try:
            a, b = float(row[x]), float(row[y])
        except (TypeError, ValueError):
            continue
        if np.isfinite(a) and np.isfinite(b):
            pairs.append((a, b))
    if len(pairs) < 3:
        return {"n": len(pairs), "pearson": None}
    a = np.asarray([p[0] for p in pairs], dtype=float)
    b = np.asarray([p[1] for p in pairs], dtype=float)
    if np.std(a) == 0 or np.std(b) == 0:
        return {"n": len(pairs), "pearson": None}
    return {"n": len(pairs), "pearson": float(np.corrcoef(a, b)[0, 1])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.analysis_root.resolve()
    with (root / "diagnostics/qh3r1_diagnostic_cells.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_learner = defaultdict(list)
    by_environment = defaultdict(list)
    for row in rows:
        by_learner[row["learner"]].append(row)
        by_environment[row["environment"]].append(row)

    learner = {}
    fields = [
        "task_probe_clean_accuracy",
        "task_probe_noisy_accuracy",
        "task_probe_degradation",
        "task_variable_clean_recoverability",
        "task_variable_noisy_recoverability",
        "relevant_Z_clean_recoverability",
        "relevant_Z_noisy_recoverability",
        "nuisance_clean_recoverability",
        "nuisance_noisy_recoverability",
        "latent_absolute_drift",
        "support_shift",
        "interaction_probe_clean_accuracy",
        "interaction_probe_noisy_accuracy",
        "interaction_clean_uplift",
        "interaction_noisy_uplift",
    ]
    for name, items in sorted(by_learner.items()):
        learner[name] = {}
        for field in fields:
            vals = np.asarray([float(row[field]) for row in items], dtype=float)
            vals = vals[np.isfinite(vals)]
            learner[name][field] = {
                "mean": float(np.mean(vals)) if vals.size else None,
                "median": float(np.median(vals)) if vals.size else None,
                "std": float(np.std(vals, ddof=0)) if vals.size else None,
            }

    environment = {}
    for name, items in sorted(by_environment.items()):
        environment[name] = {
            field: float(np.mean([float(row[field]) for row in items if np.isfinite(float(row[field]))]))
            for field in (
                "task_probe_clean_accuracy",
                "task_probe_degradation",
                "latent_absolute_drift",
                "support_shift",
            )
        }

    candidate = [r for r in rows if r["learner"] != "L0"]
    l0 = learner["L0"]
    nonlinear_remaining_gaps = {}
    for name in ("L1", "L2", "L3", "L4"):
        nonlinear_remaining_gaps[name] = (
            learner[name]["interaction_probe_clean_accuracy"]["mean"]
            - l0["interaction_probe_clean_accuracy"]["mean"]
        )

    summary = {
        "analysis_id": "QH3R1_DIAGNOSTIC_SYNTHESIS_V1",
        "learner": learner,
        "environment": environment,
        "candidate_correlations": {
            "latent_drift_vs_task_degradation": corr(candidate, "latent_absolute_drift", "task_probe_degradation"),
            "support_shift_vs_task_degradation": corr(candidate, "support_shift", "task_probe_degradation"),
            "clean_accuracy_vs_task_degradation": corr(candidate, "task_probe_clean_accuracy", "task_probe_degradation"),
            "nuisance_recoverability_vs_task_degradation": corr(candidate, "nuisance_clean_recoverability", "task_probe_degradation"),
            "task_variable_recoverability_vs_clean_accuracy": corr(candidate, "task_variable_clean_recoverability", "task_probe_clean_accuracy"),
            "interaction_uplift_vs_clean_accuracy": corr(candidate, "interaction_clean_uplift", "task_probe_clean_accuracy"),
        },
        "nonlinear_remaining_clean_accuracy_gap_vs_L0": nonlinear_remaining_gaps,
    }
    (root / "derived/diagnostic_synthesis.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
