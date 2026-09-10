from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def mean(values):
    vals = [float(v) for v in values]
    return float(np.mean(vals)) if vals else None


def median(values):
    vals = [float(v) for v in values]
    return float(np.median(vals)) if vals else None


def rankdata(values: list[float]) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j - 1) / 2.0 + 1.0
        i = j
    return ranks


def correlation(x: list[float], y: list[float]) -> dict:
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return {"n": int(len(a)), "pearson": None, "spearman": None}
    pearson = float(np.corrcoef(a, b)[0, 1])
    spearman = float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])
    return {"n": int(len(a)), "pearson": pearson, "spearman": spearman}


def bootstrap_corr(x: list[float], y: list[float], seed: int = 73191, n: int = 5000) -> dict:
    base = correlation(x, y)
    if base["pearson"] is None:
        return {**base, "pearson_ci95": None, "spearman_ci95": None}
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    pvals, svals = [], []
    for _ in range(n):
        idx = rng.integers(0, len(a), size=len(a))
        aa, bb = a[idx], b[idx]
        if np.std(aa) == 0 or np.std(bb) == 0:
            continue
        pvals.append(float(np.corrcoef(aa, bb)[0, 1]))
        svals.append(float(np.corrcoef(rankdata(aa.tolist()), rankdata(bb.tolist()))[0, 1]))
    return {
        **base,
        "pearson_ci95": [float(v) for v in np.quantile(pvals, [0.025, 0.975])] if pvals else None,
        "spearman_ci95": [float(v) for v in np.quantile(svals, [0.025, 0.975])] if svals else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    src = args.source_root.resolve()
    out = args.output_root.resolve()
    tables = out / "tables"
    derived = out / "derived"
    tables.mkdir(parents=True, exist_ok=True)
    derived.mkdir(parents=True, exist_ok=True)

    h3r_root = src / "experiments/OIR_PPV/H3R/EXP-H3R-002"
    access_log = src / "protocols/h3r/h3r_test_access_log_v1.1.md"
    summary = json.loads((h3r_root / "h3r_summary.json").read_text(encoding="utf-8"))

    rows = []
    candidate_rows = []
    for cell_path in sorted((h3r_root / "cells").glob("*.json")):
        cell = json.loads(cell_path.read_text(encoding="utf-8"))
        env, seed = cell["environment"], int(cell["seed"])
        for learner, metrics in cell["system_metrics"].items():
            row = {
                "learner": learner,
                "environment": env,
                "seed": seed,
                "R_clean": float(metrics["R_clean"]),
                "R_noisy": float(metrics["R_noisy"]),
                "DeltaR_noise": float(metrics["DeltaR_noise"]),
            }
            rows.append(row)
            if learner != "L0":
                eff = cell["candidate_effects"][learner]
                candidate_rows.append({
                    **row,
                    "E_noise": float(eff["E_noise"]),
                    "DeltaR_clean_vs_L0": float(eff["DeltaR_clean_vs_L0"]),
                    "cell_clean_guard_exceeds_0_02": float(eff["DeltaR_clean_vs_L0"]) > 0.02,
                    "cell_noise_practical_win_lt_minus_0_01": float(eff["E_noise"]) < -0.01,
                    "cell_noise_worse_gt_0": float(eff["E_noise"]) > 0.0,
                })
    write_csv(tables / "h3r_system_cells.csv", rows)
    write_csv(tables / "h3r_candidate_cells.csv", candidate_rows)

    def grouped(source, keys, metrics):
        groups = defaultdict(list)
        for row in source:
            groups[tuple(row[k] for k in keys)].append(row)
        out_rows = []
        for key, items in sorted(groups.items(), key=lambda pair: tuple(str(x) for x in pair[0])):
            record = dict(zip(keys, key))
            record["n"] = len(items)
            for metric in metrics:
                record[f"{metric}_mean"] = mean(i[metric] for i in items)
                record[f"{metric}_median"] = median(i[metric] for i in items)
                record[f"{metric}_std"] = float(np.std([float(i[metric]) for i in items], ddof=0))
            out_rows.append(record)
        return out_rows

    system_metrics = ["R_clean", "R_noisy", "DeltaR_noise"]
    write_csv(tables / "h3r_by_learner.csv", grouped(rows, ["learner"], system_metrics))
    write_csv(tables / "h3r_by_environment.csv", grouped(rows, ["environment"], system_metrics))
    write_csv(tables / "h3r_by_seed.csv", grouped(rows, ["seed"], system_metrics))
    write_csv(tables / "h3r_by_learner_environment.csv", grouped(rows, ["learner", "environment"], system_metrics))
    candidate_by_le = grouped(candidate_rows, ["learner", "environment"], ["E_noise", "DeltaR_clean_vs_L0"])
    write_csv(tables / "h3r_candidate_by_learner_environment.csv", candidate_by_le)

    failure_frequency = []
    for learner in ("L1", "L2", "L3", "L4"):
        items = [r for r in candidate_rows if r["learner"] == learner]
        failure_frequency.append({
            "learner": learner,
            "cells": len(items),
            "clean_guard_exceed_count": sum(bool(r["cell_clean_guard_exceeds_0_02"]) for r in items),
            "noise_practical_win_count": sum(bool(r["cell_noise_practical_win_lt_minus_0_01"]) for r in items),
            "noise_worse_count": sum(bool(r["cell_noise_worse_gt_0"]) for r in items),
        })
    write_csv(tables / "h3r_failure_frequency.csv", failure_frequency)

    clean_noise_corr = bootstrap_corr(
        [r["DeltaR_clean_vs_L0"] for r in candidate_rows],
        [r["E_noise"] for r in candidate_rows],
    )

    h2 = json.loads((src / "experiments/OIR_PPV/H2_Closure/EXP-H2-001/h2_comparison.json").read_text(encoding="utf-8"))
    h3r_map = {(r["learner"], r["environment"]): r for r in candidate_by_le}
    h2_cross = []
    for comp in h2["comparisons"]:
        learner = comp["learner"]
        for env, env_data in comp["per_environment"].items():
            key = (learner, env)
            if key not in h3r_map:
                continue
            h = h3r_map[key]
            h2_cross.append({
                "learner": learner,
                "environment": env,
                "h2_delta_ood_mean": float(env_data["delta_ood"]["mean"]),
                "h3r_E_noise_mean": float(h["E_noise_mean"]),
                "h3r_clean_gap_mean": float(h["DeltaR_clean_vs_L0_mean"]),
                "join_key": "learner+environment",
            })
    write_csv(tables / "h2_h3r_cross_analysis.csv", h2_cross)

    h1 = json.loads((src / "experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_comparison_v2.json").read_text(encoding="utf-8"))
    h1_cross = []
    for comp in h1["comparisons"]:
        learner = comp["condition"]
        if learner == "L0":
            continue
        for env, env_data in comp["per_environment"].items():
            key = (learner, env)
            if key not in h3r_map:
                continue
            h = h3r_map[key]
            v = env_data["vs_mem"]
            h1_cross.append({
                "learner": learner,
                "environment": env,
                "h1_c_total_ratio_vs_mem_mean": float(v["c_total_ratio"]["mean"]),
                "h1_compression_mem_over_learner_mean": float(v["compression_ratio_mem_over_learner"]["mean"]),
                "h1_utility_delta_vs_mem_mean": float(v["utility_delta"]["mean"]),
                "h3r_E_noise_mean": float(h["E_noise_mean"]),
                "h3r_clean_gap_mean": float(h["DeltaR_clean_vs_L0_mean"]),
                "join_key": "learner+environment",
            })
    write_csv(tables / "h1_h3r_cross_analysis.csv", h1_cross)

    h2_noise_corr = bootstrap_corr(
        [r["h2_delta_ood_mean"] for r in h2_cross], [r["h3r_E_noise_mean"] for r in h2_cross]
    )
    h2_clean_corr = bootstrap_corr(
        [r["h2_delta_ood_mean"] for r in h2_cross], [r["h3r_clean_gap_mean"] for r in h2_cross]
    )
    h1_compression_noise_corr = bootstrap_corr(
        [r["h1_compression_mem_over_learner_mean"] for r in h1_cross],
        [r["h3r_E_noise_mean"] for r in h1_cross],
    )
    h1_compression_clean_corr = bootstrap_corr(
        [r["h1_compression_mem_over_learner_mean"] for r in h1_cross],
        [r["h3r_clean_gap_mean"] for r in h1_cross],
    )

    result = {
        "analysis_id": "QH3R1_PUBLISHED_FORENSIC_V1",
        "evidence_mode": "POST_HOC_EXPLORATORY",
        "h3r_global_verdict_unchanged": summary["global_verdict"],
        "h3r_cells": len(list((h3r_root / "cells").glob("*.json"))),
        "candidate_cell_rows": len(candidate_rows),
        "access_log_sha256_before": sha256_path(access_log),
        "h3r_raw_tree_sha256_before": sha256_tree(h3r_root),
        "clean_gap_vs_noise_effect_correlation": clean_noise_corr,
        "h2_h3r": {
            "join_key": "learner+environment",
            "matched": len(h2_cross),
            "unmatched_reason": "H2 and H3R use disjoint seed sets; seed-level joins are forbidden. ENV-2 is inapplicable for H2 primary analysis.",
            "delta_ood_vs_E_noise": h2_noise_corr,
            "delta_ood_vs_clean_gap": h2_clean_corr,
        },
        "h1_h3r": {
            "join_key": "learner+environment",
            "matched": len(h1_cross),
            "compression_vs_E_noise": h1_compression_noise_corr,
            "compression_vs_clean_gap": h1_compression_clean_corr,
        },
        "published_candidate_summary": summary["candidate_results"],
    }
    (derived / "published_forensic_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
