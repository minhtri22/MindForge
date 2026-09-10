from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save_bar(labels, values, ylabel, title, path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, values)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.axhline(0, linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_scatter(x, y, xlabel, ylabel, title, path):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(x, y)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.axhline(0, linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--analysis-root", type=Path, required=True)
    args = p.parse_args()
    root = args.analysis_root.resolve()
    plots = root / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    h3 = read_csv(root / "tables/h3r_candidate_cells.csv")
    learners = ["L1", "L2", "L3", "L4"]
    learner_noise = [sum(float(r["E_noise"]) for r in h3 if r["learner"] == l) / 20 for l in learners]
    save_bar(learners, learner_noise, "mean E_noise", "Published H3R noise effect by learner", plots / "01_e_noise_by_learner.png")

    envs = ["ENV-1", "ENV-2", "ENV-3", "ENV-4"]
    env_noise = [sum(float(r["E_noise"]) for r in h3 if r["environment"] == e) / 20 for e in envs]
    save_bar(envs, env_noise, "mean E_noise", "Published H3R noise effect by environment", plots / "02_e_noise_by_environment.png")

    save_scatter(
        [float(r["DeltaR_clean_vs_L0"]) for r in h3],
        [float(r["E_noise"]) for r in h3],
        "clean risk gap vs L0",
        "E_noise",
        "Clean utility gap vs H3R noise effect",
        plots / "03_clean_gap_vs_noise.png",
    )

    cross = read_csv(root / "tables/h2_h3r_cross_analysis.csv")
    save_scatter(
        [float(r["h2_delta_ood_mean"]) for r in cross],
        [float(r["h3r_E_noise_mean"]) for r in cross],
        "H2 mean Delta_OOD",
        "H3R mean E_noise",
        "H2 transfer vs H3R robustness effect",
        plots / "04_h2_transfer_vs_h3r_noise.png",
    )

    diag = read_csv(root / "diagnostics/qh3r1_diagnostic_cells.csv")
    save_scatter(
        [float(r["task_probe_clean_accuracy"]) for r in diag],
        [float(r["task_probe_degradation"]) for r in diag],
        "clean task-probe accuracy",
        "noise degradation",
        "Task information vs noise degradation",
        plots / "05_task_retention_vs_noise_degradation.png",
    )

    rz = [r for r in diag if r["relevant_Z_clean_recoverability"].lower() != "nan"]
    if rz:
        save_scatter(
            [float(r["relevant_Z_clean_recoverability"]) for r in rz],
            [float(r["task_probe_degradation"]) for r in rz],
            "relevant-Z recoverability",
            "task noise degradation",
            "Relevant-Z retention vs noise degradation (applicable cells)",
            plots / "06_relevant_z_vs_noise_degradation.png",
        )

    save_scatter(
        [float(r["latent_absolute_drift"]) for r in diag],
        [float(r["task_probe_degradation"]) for r in diag],
        "latent drift",
        "task noise degradation",
        "Latent drift vs task degradation",
        plots / "07_latent_drift_vs_task_degradation.png",
    )
    save_scatter(
        [float(r["support_shift"]) for r in diag],
        [float(r["task_probe_degradation"]) for r in diag],
        "support shift",
        "task noise degradation",
        "Support shift vs task degradation",
        plots / "08_support_shift_vs_task_degradation.png",
    )


if __name__ == "__main__":
    main()
