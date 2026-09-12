from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

SOURCE_COMMIT = "e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51"
HISTORICAL_SEEDS = (223691, 965182, 537173, 538839, 124586)
SYSTEM_IDS = ("L0", "L1", "L2", "L3", "L4")
ENVIRONMENTS = ("ENV-1", "ENV-2", "ENV-3", "ENV-4")
LOCAL_AUDIT_MANIFEST_SHA256 = "aa0b534db0d5f7220f29e25d6e68e596f45735db8fa55b1a0e73bc0185d75d7c"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_array(value: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(value).tobytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def configure_historical_runtime(historical_root: Path):
    sys.path.insert(0, str(historical_root))
    import environments  # noqa: F401
    from environments.base import EnvironmentConfig, EnvironmentRegistry
    from pipeline.run_m3_experiment import TableEncoder, _apply_overrides, _metadata_table, create_extractor
    import pipeline.learners_extended  # noqa: F401
    from pipeline.run_h3r_v11 import _sha256_observation

    return EnvironmentConfig, EnvironmentRegistry, TableEncoder, _apply_overrides, _metadata_table, create_extractor, _sha256_observation


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_environment_config(environment_id: str, historical_root: Path, test_manifest: dict[str, Any], EnvironmentConfig, apply_overrides):
    config_path = historical_root / f"environments/env{environment_id[-1]}_config.yaml"
    base = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    effective = apply_overrides(base, test_manifest["environment_generation_overrides"][environment_id])
    env_section = effective.get("environment", effective)
    generation = env_section.get("generation", effective.get("generation", {}))
    return EnvironmentConfig(
        family=env_section.get("family", environment_id),
        name=env_section.get("name", environment_id),
        version=env_section.get("version", "1.0"),
        generation=generation,
        raw_config=effective,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    historical_root = args.historical_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    (
        EnvironmentConfig,
        EnvironmentRegistry,
        TableEncoder,
        apply_overrides,
        metadata_table,
        create_extractor,
        sha256_observation,
    ) = configure_historical_runtime(historical_root)

    learner_manifest_path = historical_root / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json"
    h3r_test_manifest_path = historical_root / "protocols/h3r/h3r_test_manifest_v1.1.json"
    learner_manifest = load_json(learner_manifest_path)
    test_manifest = load_json(h3r_test_manifest_path)
    learners = {entry["learner_id"]: entry for entry in learner_manifest["learners"]}

    if set(learners) != set(SYSTEM_IDS):
        raise RuntimeError(f"Unexpected learner set: {sorted(learners)}")
    if tuple(test_manifest["h3r_seeds"]) != HISTORICAL_SEEDS:
        raise RuntimeError("Historical H3R seed set drift")

    records: list[dict[str, Any]] = []
    dataset_records: list[dict[str, Any]] = []
    mismatch_count = 0

    states_dir = output_root / "model_states"
    repr_dir = output_root / "representations"
    labels_dir = output_root / "train_labels"
    identities_dir = output_root / "dataset_identities"
    for directory in (states_dir, repr_dir, labels_dir, identities_dir):
        directory.mkdir(parents=True, exist_ok=True)

    for environment_id in ENVIRONMENTS:
        config = build_environment_config(environment_id, historical_root, test_manifest, EnvironmentConfig, apply_overrides)
        for seed in HISTORICAL_SEEDS:
            env = EnvironmentRegistry.create(environment_id, config, int(seed))
            data = env.generate()
            train_idx = np.asarray(data.splits["train"], dtype=int)
            train_obs = np.asarray(data.observations[train_idx])
            train_labels = np.asarray(data.labels[train_idx])

            raw_context = metadata_table(data.metadata, "Z", "context_variables", len(data.labels))
            context_encoder = TableEncoder()
            train_context = context_encoder.fit_transform(np.asarray(raw_context)[train_idx])

            cell_path = historical_root / f"experiments/OIR_PPV/H3R/EXP-H3R-002/cells/{environment_id}-S{seed}.json"
            cell = load_json(cell_path)
            expected_metrics = cell["system_metrics"]

            label_path = labels_dir / f"{environment_id}-S{seed}.npy"
            np.save(label_path, train_labels, allow_pickle=False)
            identity = {
                "environment": environment_id,
                "historical_state_seed": int(seed),
                "train_rows": int(len(train_idx)),
                "train_index_sha256": sha256_array(train_idx),
                "train_observation_sha256": sha256_observation(train_obs),
                "train_label_sha256": sha256_array(train_labels),
                "train_label_artifact": str(label_path.relative_to(output_root)).replace("\\", "/"),
                "train_label_artifact_sha256": sha256_path(label_path),
            }
            identity_path = identities_dir / f"{environment_id}-S{seed}.json"
            write_json(identity_path, identity)
            dataset_records.append({**identity, "identity_artifact_sha256": sha256_path(identity_path)})

            for system_id in SYSTEM_IDS:
                learner = learners[system_id]
                extractor_config = {"type": learner["type"], **learner["params"], "seed": int(seed)}
                extractor = create_extractor(extractor_config, int(seed))
                result = extractor.extract(train_obs, train_context, train_labels)
                train_repr = np.asarray(result.invariant_representation, dtype=float)
                reconstructed_hash = sha256_array(train_repr)
                historical_hash = expected_metrics[system_id]["train_representation_sha256"]
                exact = reconstructed_hash == historical_hash
                mismatch_count += int(not exact)

                repr_path = repr_dir / f"{environment_id}-S{seed}-{system_id}.npy"
                np.save(repr_path, train_repr, allow_pickle=False)
                state_path = states_dir / f"{environment_id}-S{seed}-{system_id}.pkl"
                state_path.write_bytes(pickle.dumps(extractor, protocol=5))

                records.append({
                    "environment": environment_id,
                    "historical_state_seed": int(seed),
                    "learner_id": system_id,
                    "learner_type": learner["type"],
                    "learner_params": learner["params"],
                    "source_commit": SOURCE_COMMIT,
                    "historical_train_representation_sha256": historical_hash,
                    "reconstructed_train_representation_sha256": reconstructed_hash,
                    "exact_hash_match": exact,
                    "representation_artifact": str(repr_path.relative_to(output_root)).replace("\\", "/"),
                    "representation_artifact_sha256": sha256_path(repr_path),
                    "model_state_artifact": str(state_path.relative_to(output_root)).replace("\\", "/"),
                    "model_state_artifact_sha256": sha256_path(state_path),
                    "runtime_encoder_type": type(extractor.encoder).__name__,
                    "model_config_hash": extractor.get_config_hash(),
                })

    record_count = len(records)
    exact_matches = sum(int(record["exact_hash_match"]) for record in records)
    status = "ESTABLISHED" if record_count == 100 and mismatch_count == 0 else "FAILED"
    freeze = {
        "manifest_id": "H3R-RECONSTRUCTION-FREEZE-v1",
        "status": status,
        "source_commit": SOURCE_COMMIT,
        "local_audit_manifest_sha256": LOCAL_AUDIT_MANIFEST_SHA256,
        "scope": {"environments": list(ENVIRONMENTS), "historical_state_seeds": list(HISTORICAL_SEEDS), "learners": list(SYSTEM_IDS)},
        "record_count": record_count,
        "exact_hash_matches": exact_matches,
        "mismatch_count": mismatch_count,
        "learner_manifest_sha256": sha256_path(learner_manifest_path),
        "historical_h3r_test_manifest_sha256": sha256_path(h3r_test_manifest_path),
        "records": records,
        "dataset_identities": dataset_records,
    }
    freeze_path = output_root / "H3R_RECONSTRUCTION_FREEZE_v1.json"
    write_json(freeze_path, freeze)
    results = {
        "historical_reproducibility": status,
        "record_count": record_count,
        "exact_hash_matches": exact_matches,
        "mismatch_count": mismatch_count,
        "freeze_manifest_sha256": sha256_path(freeze_path),
        "source_commit": SOURCE_COMMIT,
    }
    write_json(output_root / "RECONSTRUCTION_RESULTS.json", results)
    print(json.dumps(results, sort_keys=True))
    return 0 if status == "ESTABLISHED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
