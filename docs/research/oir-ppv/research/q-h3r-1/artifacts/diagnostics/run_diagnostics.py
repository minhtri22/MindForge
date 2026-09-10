from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, balanced_accuracy_score, r2_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


DIAGNOSTIC_SEEDS = (610101, 610103, 610107)
NOISE_DELTA = 0.10
NOISE_REPLICATES = 3
NOISE_NAMESPACE = "QH3R1_DIAGNOSTIC_V1"


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


def stable_array_hash(value: np.ndarray) -> str:
    arr = np.asarray(value)
    if arr.dtype == object or arr.dtype.kind in "OUS":
        payload = json.dumps(arr.tolist(), sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    else:
        payload = np.ascontiguousarray(arr).tobytes()
    return hashlib.sha256(payload).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def diag_seed(environment: str, generator_seed: int, row_id: int, replicate: int) -> int:
    material = f"{NOISE_NAMESPACE}|{environment}|{generator_seed}|{row_id}|{replicate}".encode("utf-8")
    return int(hashlib.sha256(material).hexdigest(), 16) & 0xFFFFFFFF


def make_noisy_replicates(clean_obs, train_scale, numeric_mask, env, seed, row_ids):
    clean = np.asarray(clean_obs)
    clean = clean.reshape(-1, 1) if clean.ndim == 1 else clean
    mask = np.asarray(numeric_mask, dtype=bool)
    scale = np.asarray(train_scale, dtype=float)
    numeric = np.asarray(clean[:, mask], dtype=float)
    categorical = ~mask
    reps = []
    for rep in range(NOISE_REPLICATES):
        noisy = clean.copy()
        for offset, row_id in enumerate(row_ids):
            rng = np.random.default_rng(diag_seed(env, seed, int(row_id), rep))
            noisy[offset, mask] = numeric[offset] + NOISE_DELTA * scale * rng.uniform(-1, 1, size=int(mask.sum()))
        if categorical.any() and not np.array_equal(noisy[:, categorical], clean[:, categorical]):
            raise RuntimeError("categorical channel changed in QH3R1 diagnostic")
        normalized = np.abs(np.asarray(noisy[:, mask], dtype=float) - numeric) / scale
        if normalized.size and float(np.max(normalized)) > NOISE_DELTA + 1e-12:
            raise RuntimeError("numeric diagnostic noise exceeded frozen magnitude")
        reps.append(noisy)
    return reps


def is_categorical(values: np.ndarray) -> bool:
    arr = np.asarray(values)
    if arr.dtype.kind in "OUSb":
        return True
    unique = np.unique(arr)
    return arr.dtype.kind in "iu" and len(unique) <= 12


def recoverability(train_z, val_z, train_target, val_target, noisy_val_zs, seed: int) -> tuple[float, float]:
    train_target = np.asarray(train_target).ravel()
    val_target = np.asarray(val_target).ravel()
    if len(np.unique(train_target)) < 2:
        return float("nan"), float("nan")
    mean = np.mean(train_z, axis=0)
    scale_full = np.std(train_z, axis=0, ddof=0)
    floor = max(1e-6, float(np.max(scale_full)) * 1e-4)
    active = scale_full > floor
    if not np.any(active):
        active = np.ones(train_z.shape[1], dtype=bool)
    scale = np.maximum(scale_full[active], 1e-6)
    train_x = (train_z[:, active] - mean[active]) / scale
    val_x = (val_z[:, active] - mean[active]) / scale
    noisy_xs = [(z[:, active] - mean[active]) / scale for z in noisy_val_zs]
    if is_categorical(train_target):
        model = LogisticRegression(max_iter=1000, random_state=seed, class_weight="balanced")
        model.fit(train_x, train_target.astype(str))
        clean = balanced_accuracy_score(val_target.astype(str), model.predict(val_x))
        noisy = np.mean([
            balanced_accuracy_score(val_target.astype(str), model.predict(z)) for z in noisy_xs
        ])
        return float(clean), float(noisy)
    model = Ridge(alpha=1.0)
    model.fit(train_x, train_target.astype(float))
    clean = r2_score(val_target.astype(float), model.predict(val_x))
    noisy = np.mean([r2_score(val_target.astype(float), model.predict(z)) for z in noisy_xs])
    return float(clean), float(noisy)


def group_targets(data, env: str):
    meta = data.metadata
    task_vars = {}
    relevant_z = {}
    nuisance = {}
    if env == "ENV-1":
        task_vars = {"shape": meta["structural_variables"]["shape"]}
        nuisance = dict(meta.get("nuisance_variables", {}))
    elif env == "ENV-2":
        task_vars = {"character": meta["factor_values"]["character"]}
        nuisance = dict(meta.get("nuisance_variables", {}))
    elif env == "ENV-3":
        task_vars = {"S": meta["S"], "A": meta["A"]}
        relevant_z = {"Z": meta["Z"]}
        nuisance = {"N": meta["N"]}
    elif env == "ENV-4":
        task_vars = {"core_category": meta["structural_variables"]["core_category"]}
        nuisance = dict(meta.get("nuisance_variables", {}))
    return task_vars, relevant_z, nuisance


def average_group_scores(group, train_idx, val_idx, train_z, val_z, noisy_val_zs, seed):
    clean_scores, noisy_scores = [], []
    detail = {}
    for name, values in group.items():
        values = np.asarray(values)
        clean, noisy = recoverability(
            train_z, val_z, values[train_idx], values[val_idx], noisy_val_zs, seed
        )
        detail[name] = {"clean": clean, "noisy": noisy, "degradation": clean - noisy}
        if np.isfinite(clean):
            clean_scores.append(clean)
        if np.isfinite(noisy):
            noisy_scores.append(noisy)
    return (
        float(np.mean(clean_scores)) if clean_scores else float("nan"),
        float(np.mean(noisy_scores)) if noisy_scores else float("nan"),
        detail,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    src = args.source_root.resolve()
    out = args.output_root.resolve()
    sys.path.insert(0, str(src))

    import pipeline.run_h3r_v11 as h3r

    h3r_root = src / "experiments/OIR_PPV/H3R/EXP-H3R-002"
    access_log = src / "protocols/h3r/h3r_test_access_log_v1.1.md"
    access_before = sha256_path(access_log)
    raw_before = sha256_tree(h3r_root)
    frozen = h3r.load_frozen_inputs()
    learner_map = h3r._learner_map(frozen)

    forbidden = set(int(x) for x in frozen.test_manifest.get("historical_test_seeds_excluded", []))
    forbidden.update(int(x) for x in frozen.test_manifest.get("v1_0_test_seeds_excluded", []))
    forbidden.update(int(x) for x in frozen.test_manifest.get("h3r_seeds", []))
    forbidden.update(int(x) for x in frozen.learner_manifest.get("seeds", []))
    if forbidden.intersection(DIAGNOSTIC_SEEDS):
        raise RuntimeError("diagnostic seed overlaps historical/frozen seeds")

    rows = []
    dataset_manifest = []
    detail_records = []
    shared_probe_configs = set()
    for env in frozen.test_manifest["environments"]:
        for seed in DIAGNOSTIC_SEEDS:
            data = h3r.generate_frozen_cell(env, int(seed), frozen)
            train_idx = np.asarray(data.splits["train"], dtype=int)
            val_idx = np.asarray(data.splits["val"], dtype=int)
            if len(train_idx) == 0 or len(val_idx) == 0:
                raise RuntimeError(f"empty train/val split for {env}/{seed}")
            train_obs = np.asarray(data.observations[train_idx])
            val_obs = np.asarray(data.observations[val_idx])
            train_labels = np.asarray(data.labels[train_idx])
            val_labels = np.asarray(data.labels[val_idx])
            train_context, val_context = h3r._context_tables(data, train_idx, val_idx)
            numeric_mask = h3r._numeric_channel_mask_from_train(train_obs)
            scale = h3r._train_scale(train_obs, numeric_mask)
            noisy_obs_reps = make_noisy_replicates(val_obs, scale, numeric_mask, env, int(seed), val_idx)
            dataset_manifest.append({
                "environment": env,
                "seed": int(seed),
                "train_rows": int(len(train_idx)),
                "val_rows": int(len(val_idx)),
                "train_observation_sha256": stable_array_hash(train_obs),
                "val_observation_sha256": stable_array_hash(val_obs),
                "train_label_sha256": stable_array_hash(train_labels),
                "val_label_sha256": stable_array_hash(val_labels),
                "splits_accessed": ["train", "val"],
                "test_split_accessed": False,
            })
            task_vars, relevant_z, nuisance = group_targets(data, env)
            for learner in ("L0", "L1", "L2", "L3", "L4"):
                extractor, linear_probe, train_z = h3r._fit_representation_and_probe(
                    learner_map[learner], int(seed), train_obs, train_context, train_labels
                )
                val_z = np.asarray(extractor.extract(val_obs, val_context, None).invariant_representation, dtype=float)
                noisy_val_zs = [
                    np.asarray(extractor.extract(obs, val_context, None).invariant_representation, dtype=float)
                    for obs in noisy_obs_reps
                ]
                clean_pred = linear_probe.predict(val_z)
                noisy_accs = [accuracy_score(val_labels, linear_probe.predict(z)) for z in noisy_val_zs]
                task_clean = float(accuracy_score(val_labels, clean_pred))
                task_noisy = float(np.mean(noisy_accs))

                probe_scale_full = np.std(train_z, axis=0, ddof=0)
                probe_floor = max(1e-6, float(np.max(probe_scale_full)) * 1e-4)
                probe_active = probe_scale_full > probe_floor
                if not np.any(probe_active):
                    probe_active = np.ones(train_z.shape[1], dtype=bool)
                probe_mean = np.mean(train_z[:, probe_active], axis=0)
                probe_scale = np.maximum(np.std(train_z[:, probe_active], axis=0, ddof=0), 1e-6)
                train_probe_z = (train_z[:, probe_active] - probe_mean) / probe_scale
                val_probe_z = (val_z[:, probe_active] - probe_mean) / probe_scale
                noisy_probe_zs = [(z[:, probe_active] - probe_mean) / probe_scale for z in noisy_val_zs]
                poly_probe = make_pipeline(
                    PolynomialFeatures(degree=2, include_bias=False),
                    StandardScaler(),
                    LogisticRegression(max_iter=1000, random_state=int(seed)),
                )
                poly_probe.fit(train_probe_z, train_labels)
                poly_clean = float(accuracy_score(val_labels, poly_probe.predict(val_probe_z)))
                poly_noisy = float(np.mean([accuracy_score(val_labels, poly_probe.predict(z)) for z in noisy_probe_zs]))

                task_var_clean, task_var_noisy, task_var_detail = average_group_scores(
                    task_vars, train_idx, val_idx, train_z, val_z, noisy_val_zs, int(seed)
                )
                rz_clean, rz_noisy, rz_detail = average_group_scores(
                    relevant_z, train_idx, val_idx, train_z, val_z, noisy_val_zs, int(seed)
                )
                n_clean, n_noisy, n_detail = average_group_scores(
                    nuisance, train_idx, val_idx, train_z, val_z, noisy_val_zs, int(seed)
                )

                latent_mean_full = np.mean(train_z, axis=0)
                latent_scale_full = np.std(train_z, axis=0, ddof=0)
                active_floor = max(1e-6, float(np.max(latent_scale_full)) * 1e-4)
                active = latent_scale_full > active_floor
                if not np.any(active):
                    active = np.ones(train_z.shape[1], dtype=bool)
                latent_mean = latent_mean_full[active]
                latent_scale = np.maximum(latent_scale_full[active], 1e-6)
                train_std = (train_z[:, active] - latent_mean) / latent_scale
                val_std = (val_z[:, active] - latent_mean) / latent_scale
                noisy_std = [(z[:, active] - latent_mean) / latent_scale for z in noisy_val_zs]
                nn = NearestNeighbors(n_neighbors=1).fit(train_std)
                support_clean = float(np.mean(nn.kneighbors(val_std, return_distance=True)[0]))
                support_noisy = float(np.mean([
                    np.mean(nn.kneighbors(z, return_distance=True)[0]) for z in noisy_std
                ]))
                abs_drifts, rel_drifts, cosine_drifts, logit_drifts = [], [], [], []
                clean_norm = np.linalg.norm(val_std, axis=1)
                clean_logits = linear_probe.decision_function(val_z)
                clean_logits = np.asarray(clean_logits, dtype=float)
                for z_std, z_raw in zip(noisy_std, noisy_val_zs):
                    diff = np.linalg.norm(z_std - val_std, axis=1)
                    abs_drifts.append(float(np.mean(diff)))
                    rel_drifts.append(float(np.mean(diff / (clean_norm + 1e-8))))
                    denom = np.linalg.norm(val_std, axis=1) * np.linalg.norm(z_std, axis=1) + 1e-8
                    cosine = np.sum(val_std * z_std, axis=1) / denom
                    cosine_drifts.append(float(np.mean(1.0 - cosine)))
                    noisy_logits = np.asarray(linear_probe.decision_function(z_raw), dtype=float)
                    logit_drifts.append(float(np.mean(np.abs(noisy_logits - clean_logits))))

                probe_cfg = ("lbfgs", "l2", 1.0, 1000, int(seed))
                shared_probe_configs.add(probe_cfg)
                row = {
                    "environment": env,
                    "seed": int(seed),
                    "learner": learner,
                    "representation_dim": int(val_z.shape[1]),
                    "active_representation_dim": int(np.sum(active)),
                    "task_probe_clean_accuracy": task_clean,
                    "task_probe_noisy_accuracy": task_noisy,
                    "task_probe_degradation": task_clean - task_noisy,
                    "task_variable_clean_recoverability": task_var_clean,
                    "task_variable_noisy_recoverability": task_var_noisy,
                    "relevant_Z_clean_recoverability": rz_clean,
                    "relevant_Z_noisy_recoverability": rz_noisy,
                    "nuisance_clean_recoverability": n_clean,
                    "nuisance_noisy_recoverability": n_noisy,
                    "latent_absolute_drift": float(np.mean(abs_drifts)),
                    "latent_relative_drift": float(np.mean(rel_drifts)),
                    "latent_cosine_drift": float(np.mean(cosine_drifts)),
                    "task_logit_drift": float(np.mean(logit_drifts)),
                    "support_clean_nn_distance": support_clean,
                    "support_noisy_nn_distance": support_noisy,
                    "support_shift": support_noisy - support_clean,
                    "interaction_probe_clean_accuracy": poly_clean,
                    "interaction_probe_noisy_accuracy": poly_noisy,
                    "interaction_clean_uplift": poly_clean - task_clean,
                    "interaction_noisy_uplift": poly_noisy - task_noisy,
                }
                rows.append(row)
                detail_records.append({
                    "environment": env,
                    "seed": int(seed),
                    "learner": learner,
                    "task_variable_probes": task_var_detail,
                    "relevant_Z_probes": rz_detail,
                    "nuisance_probes": n_detail,
                })

    access_after = sha256_path(access_log)
    raw_after = sha256_tree(h3r_root)
    if access_after != access_before:
        raise RuntimeError("H3R access log changed during QH3R1 diagnostic")
    if raw_after != raw_before:
        raise RuntimeError("H3R raw evidence changed during QH3R1 diagnostic")

    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "diagnostics/qh3r1_diagnostic_cells.csv", rows)
    (out / "diagnostics/qh3r1_probe_details.json").write_text(
        json.dumps(detail_records, indent=2, sort_keys=True, allow_nan=True), encoding="utf-8"
    )
    (out / "diagnostics/qh3r1_dataset_manifest.json").write_text(
        json.dumps(dataset_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    def aggregate(key: str):
        grouped = defaultdict(list)
        for row in rows:
            grouped[row[key]].append(row)
        result = []
        metrics = [k for k in rows[0] if k not in {"environment", "seed", "learner"}]
        for value, items in sorted(grouped.items(), key=lambda x: str(x[0])):
            record = {key: value, "n": len(items)}
            for metric in metrics:
                vals = np.asarray([float(i[metric]) for i in items], dtype=float)
                finite = vals[np.isfinite(vals)]
                record[f"{metric}_mean"] = float(np.mean(finite)) if finite.size else None
                record[f"{metric}_median"] = float(np.median(finite)) if finite.size else None
                record[f"{metric}_std"] = float(np.std(finite, ddof=0)) if finite.size else None
            result.append(record)
        return result

    by_learner = aggregate("learner")
    by_environment = aggregate("environment")
    write_csv(out / "tables/diagnostic_by_learner.csv", by_learner)
    write_csv(out / "tables/diagnostic_by_environment.csv", by_environment)

    candidate_rows = [r for r in rows if r["learner"] != "L0"]
    baseline_map = {(r["environment"], r["seed"]): r for r in rows if r["learner"] == "L0"}
    contrasts = []
    for r in candidate_rows:
        b = baseline_map[(r["environment"], r["seed"])]
        contrasts.append({
            "environment": r["environment"],
            "seed": r["seed"],
            "learner": r["learner"],
            "clean_task_accuracy_gap_vs_L0": r["task_probe_clean_accuracy"] - b["task_probe_clean_accuracy"],
            "noise_degradation_gap_vs_L0": r["task_probe_degradation"] - b["task_probe_degradation"],
            "latent_drift_gap_vs_L0": r["latent_absolute_drift"] - b["latent_absolute_drift"],
            "support_shift_gap_vs_L0": r["support_shift"] - b["support_shift"],
            "interaction_clean_uplift_gap_vs_L0": r["interaction_clean_uplift"] - b["interaction_clean_uplift"],
            "interaction_noisy_uplift_gap_vs_L0": r["interaction_noisy_uplift"] - b["interaction_noisy_uplift"],
        })
    write_csv(out / "tables/diagnostic_candidate_contrasts.csv", contrasts)

    env_variance = {}
    seed_variance = {}
    for metric in ("task_probe_clean_accuracy", "task_probe_degradation", "latent_absolute_drift", "support_shift"):
        env_means = defaultdict(list)
        seed_means = defaultdict(list)
        for r in candidate_rows:
            env_means[r["environment"]].append(float(r[metric]))
            seed_means[r["seed"]].append(float(r[metric]))
        env_variance[metric] = float(np.var([np.mean(v) for v in env_means.values()], ddof=0))
        seed_variance[metric] = float(np.var([np.mean(v) for v in seed_means.values()], ddof=0))

    result = {
        "analysis_id": NOISE_NAMESPACE,
        "evidence_mode": "FRESH_NON_TEST_EXPLORATORY",
        "diagnostic_seeds": list(DIAGNOSTIC_SEEDS),
        "forbidden_seed_count": len(forbidden),
        "seed_disjoint": not bool(forbidden.intersection(DIAGNOSTIC_SEEDS)),
        "noise_delta": NOISE_DELTA,
        "noise_replicates": NOISE_REPLICATES,
        "splits_accessed": ["train", "val"],
        "test_split_accessed": False,
        "h3r_execute_decisive_called": False,
        "access_log_sha256_before": access_before,
        "access_log_sha256_after": access_after,
        "h3r_raw_tree_sha256_before": raw_before,
        "h3r_raw_tree_sha256_after": raw_after,
        "categorical_channels_preserved": True,
        "numeric_noise_within_delta": True,
        "shared_probe_contract": {
            "family": "LogisticRegression",
            "solver": "lbfgs",
            "penalty": "l2",
            "C": 1.0,
            "max_iter": 1000,
            "same_config_across_representations_within_seed": True,
        },
        "between_environment_variance": env_variance,
        "between_seed_variance": seed_variance,
        "rows": len(rows),
        "datasets": len(dataset_manifest),
    }
    (out / "diagnostics/qh3r1_diagnostic_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
