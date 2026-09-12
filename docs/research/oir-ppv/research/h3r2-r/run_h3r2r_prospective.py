"""Reconstruction-gated H3R2-R prospective execution.

The representation path is deliberately transform-only. Historical encoder
state is loaded from the committed H3R reconstruction freeze and prospective
observations are passed directly through the already-fitted table encoder and
encoder. Representation fitting is therefore absent from this runner.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import pickle
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


SOURCE_COMMIT = "e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51"
RECONSTRUCTION_MANIFEST_SHA256 = "aa0b534db0d5f7220f29e25d6e68e596f45735db8fa55b1a0e73bc0185d75d7c"
ENVIRONMENTS = ("ENV-1", "ENV-2", "ENV-3", "ENV-4")
HISTORICAL_STATE_SEEDS = (223691, 965182, 537173, 538839, 124586)
SYSTEM_IDS = ("L0", "L1", "L2", "L3", "L4")
READOUT_FAMILIES = ("linear", "degree2")

H3R2R_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_HISTORICAL_ROOT = (
    REPO_ROOT / "tmp_h3r_source_retry" / "docs" / "research" / "oir-ppv" / "research"
)
DEFAULT_RECONSTRUCTION_ROOT = H3R2R_ROOT / "h3r_reconstruction_v1"
DEFAULT_SEED_REGISTRY = H3R2R_ROOT / "PROSPECTIVE_SEED_REGISTRY_v1.json"
DEFAULT_IDENTITY_LOCK = H3R2R_ROOT / "PROSPECTIVE_IDENTITY_LOCK_v1.json"
DEFAULT_PRETEST_QA = H3R2R_ROOT / "PRETEST_QA_v1.json"
DEFAULT_EXECUTION_ROOT = H3R2R_ROOT / "prospective_execution_v1"


class H3R2RError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_array(value: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(value).tobytes())


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256_bytes(payload)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def rel_repo(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def configure_historical_runtime(historical_root: Path):
    historical_root = historical_root.resolve()
    if not (historical_root / "pipeline" / "run_h3r_v11.py").is_file():
        raise H3R2RError(f"Historical H3R source is missing: {historical_root}")
    sys.path.insert(0, str(historical_root))
    import environments  # noqa: F401
    from pipeline import run_h3r_v11 as h
    import pipeline.learners_extended  # noqa: F401

    return h


def derive_prospective_seed(environment: str, historical_state_seed: int) -> int:
    material = f"H3R2-R|{environment}|{int(historical_state_seed)}|prospective-v1".encode("utf-8")
    return 100000 + (int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 900000)


def validate_seed_registry(registry: dict[str, Any]) -> list[dict[str, int | str]]:
    mappings = list(registry.get("mappings", []))
    expected_pairs = {(env, seed) for env in ENVIRONMENTS for seed in HISTORICAL_STATE_SEEDS}
    actual_pairs = {
        (str(item["environment"]), int(item["historical_state_seed"])) for item in mappings
    }
    if actual_pairs != expected_pairs or len(mappings) != 20:
        raise H3R2RError("Prospective seed registry does not cover the frozen 4x5 matrix exactly")

    prospective = [int(item["prospective_test_seed"]) for item in mappings]
    if len(set(prospective)) != 20:
        raise H3R2RError("Prospective test seeds are not unique")
    if set(prospective) & set(HISTORICAL_STATE_SEEDS):
        raise H3R2RError("Prospective test seed overlaps a historical state seed")
    if registry.get("unique") is not True or registry.get("disjoint_from_historical") is not True:
        raise H3R2RError("Prospective registry self-declaration is inconsistent")

    for item in mappings:
        expected = derive_prospective_seed(str(item["environment"]), int(item["historical_state_seed"]))
        if int(item["prospective_test_seed"]) != expected:
            raise H3R2RError(
                f"Prospective seed derivation mismatch for {item['environment']}/"
                f"{item['historical_state_seed']}"
            )
    return sorted(
        mappings,
        key=lambda item: (
            ENVIRONMENTS.index(str(item["environment"])),
            HISTORICAL_STATE_SEEDS.index(int(item["historical_state_seed"])),
        ),
    )


def load_reconstruction(reconstruction_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    freeze_path = reconstruction_root / "H3R_RECONSTRUCTION_FREEZE_v1.json"
    results_path = reconstruction_root / "RECONSTRUCTION_RESULTS.json"
    if not freeze_path.is_file() or not results_path.is_file():
        raise H3R2RError("Committed reconstruction freeze is incomplete")

    results = load_json(results_path)
    freeze = load_json(freeze_path)
    actual_manifest_hash = sha256_path(freeze_path)
    if actual_manifest_hash != RECONSTRUCTION_MANIFEST_SHA256:
        raise H3R2RError(
            f"Reconstruction manifest hash drift: {actual_manifest_hash} != {RECONSTRUCTION_MANIFEST_SHA256}"
        )
    if results.get("manifest_sha256") != actual_manifest_hash:
        raise H3R2RError("RECONSTRUCTION_RESULTS manifest identity does not match the freeze file")
    if results.get("historical_reproducibility") != "ESTABLISHED":
        raise H3R2RError("Historical reproducibility is not established")
    if (int(results.get("record_count", -1)), int(results.get("exact_hash_matches", -1)), int(results.get("mismatch_count", -1))) != (100, 100, 0):
        raise H3R2RError("Historical reconstruction gate is not 100/100 exact")
    if freeze.get("source_commit") != SOURCE_COMMIT:
        raise H3R2RError("Reconstruction source commit drift")
    if freeze.get("historical_reproducibility") != "ESTABLISHED":
        raise H3R2RError("Freeze manifest does not establish historical reproducibility")
    if (int(freeze.get("record_count", -1)), int(freeze.get("exact_hash_matches", -1)), int(freeze.get("mismatch_count", -1))) != (100, 100, 0):
        raise H3R2RError("Freeze manifest record counts are inconsistent")
    return freeze, results


def record_map(freeze: dict[str, Any]) -> dict[tuple[str, int, str], dict[str, Any]]:
    records: dict[tuple[str, int, str], dict[str, Any]] = {}
    for record in freeze["records"]:
        key = (
            str(record["environment_id"]),
            int(record["seed"]),
            str(record["learner_id"]),
        )
        if key in records:
            raise H3R2RError(f"Duplicate reconstruction record: {key}")
        records[key] = record
    expected = {(env, seed, learner) for env in ENVIRONMENTS for seed in HISTORICAL_STATE_SEEDS for learner in SYSTEM_IDS}
    if set(records) != expected:
        raise H3R2RError("Reconstruction freeze record matrix is incomplete")
    return records


def resolve_frozen_artifact(relative_path: str) -> Path:
    path = (H3R2R_ROOT / relative_path).resolve()
    try:
        path.relative_to(H3R2R_ROOT.resolve())
    except ValueError as exc:
        raise H3R2RError(f"Frozen artifact escapes H3R2-R root: {relative_path}") from exc
    if not path.is_file():
        raise H3R2RError(f"Frozen artifact is missing: {path}")
    return path


def validate_dataset_identity_record(identity: dict[str, Any]) -> None:
    payload = {key: value for key, value in identity.items() if key != "dataset_hash"}
    if canonical_hash(payload) != identity.get("dataset_hash"):
        raise H3R2RError(
            f"Dataset identity hash drift for {identity.get('environment_id')}/S{identity.get('seed')}"
        )


def load_dataset_identity(reconstruction_root: Path, environment: str, seed: int) -> dict[str, Any]:
    path = reconstruction_root / "dataset_identities" / f"{environment}-S{int(seed)}.json"
    if not path.is_file():
        raise H3R2RError(f"Historical dataset identity is missing: {path}")
    identity = load_json(path)
    validate_dataset_identity_record(identity)
    return identity


def validate_frozen_record_files(
    reconstruction_root: Path,
    records: dict[tuple[str, int, str], dict[str, Any]],
) -> dict[str, Any]:
    checked_states = 0
    checked_representations = 0
    dataset_hashes: dict[tuple[str, int], str] = {}
    for environment in ENVIRONMENTS:
        for seed in HISTORICAL_STATE_SEEDS:
            identity = load_dataset_identity(reconstruction_root, environment, seed)
            dataset_hashes[(environment, seed)] = str(identity["dataset_hash"])
            for learner in SYSTEM_IDS:
                record = records[(environment, seed, learner)]
                if record.get("dataset_hash") != identity["dataset_hash"]:
                    raise H3R2RError(f"Dataset identity mismatch in freeze record: {environment}/{seed}/{learner}")
                if record.get("source_commit") != SOURCE_COMMIT:
                    raise H3R2RError(f"Source commit drift in freeze record: {environment}/{seed}/{learner}")
                if record.get("exact_hash_match") is not True:
                    raise H3R2RError(f"Non-exact reconstruction record: {environment}/{seed}/{learner}")

                state_path = resolve_frozen_artifact(str(record["model_state_path"]))
                if sha256_path(state_path) != record["model_state_hash"]:
                    raise H3R2RError(f"Frozen state hash mismatch: {environment}/{seed}/{learner}")
                checked_states += 1

                representation_path = resolve_frozen_artifact(str(record["representation_output_path"]))
                if sha256_path(representation_path) != record["representation_artifact_hash"]:
                    raise H3R2RError(f"Representation artifact hash mismatch: {environment}/{seed}/{learner}")
                representation = np.load(representation_path, allow_pickle=False)
                representation_hash = sha256_array(representation)
                if representation_hash != record["representation_output_hash"]:
                    raise H3R2RError(f"Representation array hash mismatch: {environment}/{seed}/{learner}")
                if representation_hash != record["historical_representation_hash"]:
                    raise H3R2RError(f"Historical representation hash mismatch: {environment}/{seed}/{learner}")
                checked_representations += 1

                preprocessing = dict(record.get("preprocessing", {}))
                stored_preprocessing_hash = preprocessing.pop("preprocessing_hash", None)
                if stored_preprocessing_hash != record.get("preprocessing_hash"):
                    raise H3R2RError(f"Preprocessing hash field mismatch: {environment}/{seed}/{learner}")
                if canonical_hash(preprocessing) != stored_preprocessing_hash:
                    raise H3R2RError(f"Preprocessing payload hash mismatch: {environment}/{seed}/{learner}")

    return {
        "status": "PASS",
        "checked_model_states": checked_states,
        "checked_representations": checked_representations,
        "checked_dataset_identities": len(dataset_hashes),
    }


def verify_historical_source_lineage(historical_root: Path, h) -> dict[str, Any]:
    frozen_inputs = h.load_frozen_inputs()
    checked: list[dict[str, Any]] = []
    for relative, expected in frozen_inputs.test_manifest.get("source_hashes", {}).items():
        path = historical_root / relative
        actual = sha256_path(path) if path.is_file() else None
        passed = actual == expected
        checked.append({"path": relative, "expected_sha256": expected, "actual_sha256": actual, "passed": passed})
        if not passed:
            raise H3R2RError(f"Historical source lineage mismatch: {relative}")
    return {"status": "PASS", "source_commit_declared": SOURCE_COMMIT, "checked_source_files": checked}


def historical_training_labels(
    environment: str,
    seed: int,
    reconstruction_root: Path,
    h,
    frozen_inputs,
) -> tuple[Any, np.ndarray, np.ndarray]:
    identity = load_dataset_identity(reconstruction_root, environment, seed)
    data = h.generate_frozen_cell(environment, int(seed), frozen_inputs)
    observations = np.asarray(data.observations)
    labels = np.asarray(data.labels)
    train_idx = np.asarray(data.splits["train"], dtype=int)
    val_idx = np.asarray(data.splits["val"], dtype=int)
    test_idx = np.asarray(data.splits["test"], dtype=int)
    actual = {
        "observation_sha256": h._sha256_observation(observations),
        "label_sha256": sha256_array(labels),
        "train_index_sha256": sha256_array(train_idx),
        "validation_index_sha256": sha256_array(val_idx),
        "historical_test_index_sha256": sha256_array(test_idx),
        "rows": int(len(labels)),
        "train_rows": int(len(train_idx)),
        "validation_rows": int(len(val_idx)),
        "historical_test_rows": int(len(test_idx)),
    }
    for key, value in actual.items():
        if identity.get(key) != value:
            raise H3R2RError(f"Historical dataset regeneration mismatch: {environment}/{seed}/{key}")
    return data, train_idx, labels[train_idx]


def load_frozen_extractor(record: dict[str, Any]):
    state_path = resolve_frozen_artifact(str(record["model_state_path"]))
    if sha256_path(state_path) != record["model_state_hash"]:
        raise H3R2RError("Frozen model state changed after preflight")
    extractor = pickle.loads(state_path.read_bytes())
    if getattr(extractor, "_fitted", None) is not True:
        raise H3R2RError("Loaded historical extractor is not marked fitted")
    table_encoder = getattr(extractor, "table_encoder", None)
    encoder = getattr(extractor, "encoder", None)
    if table_encoder is None or getattr(table_encoder, "_fitted", None) is not True:
        raise H3R2RError("Loaded historical table encoder is not frozen/fitted")
    if encoder is None or not callable(getattr(encoder, "encode", None)):
        raise H3R2RError("Loaded historical encoder has no transform-only encode path")
    expected_encoder_class = record.get("preprocessing", {}).get("encoder_class")
    if expected_encoder_class and type(encoder).__name__ != expected_encoder_class:
        raise H3R2RError("Loaded encoder class differs from reconstruction record")
    return extractor


def frozen_transform(extractor, observations: np.ndarray) -> np.ndarray:
    """Transform observations without any representation fit/update route."""
    if getattr(extractor, "_fitted", None) is not True:
        raise H3R2RError("Frozen extractor fit flag changed")
    numeric = extractor.table_encoder.transform(np.asarray(observations))
    representation = np.asarray(extractor.encoder.encode(numeric), dtype=float)
    if representation.ndim != 2 or not np.isfinite(representation).all():
        raise H3R2RError("Frozen encoder produced an invalid representation")
    return representation


def readout_spec(family: str, seed: int) -> dict[str, Any]:
    base = {
        "solver": "lbfgs",
        "penalty": "l2",
        "C": 1.0,
        "max_iter": 1000,
        "random_state": int(seed),
    }
    if family == "linear":
        return {"family": "linear", "polynomial_degree": None, "include_bias": None, "logistic_regression": base}
    if family == "degree2":
        return {"family": "degree2", "polynomial_degree": 2, "include_bias": False, "logistic_regression": base}
    raise H3R2RError(f"Unknown readout family: {family}")


def build_readout(family: str, seed: int):
    logistic = LogisticRegression(
        solver="lbfgs",
        penalty="l2",
        C=1.0,
        max_iter=1000,
        random_state=int(seed),
    )
    if family == "linear":
        return logistic
    if family == "degree2":
        return make_pipeline(PolynomialFeatures(degree=2, include_bias=False), logistic)
    raise H3R2RError(f"Unknown readout family: {family}")


def prediction_metrics(prediction: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    prediction = np.asarray(prediction)
    labels = np.asarray(labels)
    error_rate = float(np.mean(prediction != labels))
    return {"error_rate": error_rate, "accuracy": 1.0 - error_rate}


def prospective_observation_identity(mapping: dict[str, Any], h, frozen_inputs) -> tuple[dict[str, Any], Any, list[np.ndarray]]:
    environment = str(mapping["environment"])
    prospective_seed = int(mapping["prospective_test_seed"])
    data = h.generate_frozen_cell(environment, prospective_seed, frozen_inputs)
    train_idx = np.asarray(data.splits["train"], dtype=int)
    test_idx = np.asarray(data.splits["test"], dtype=int)
    observations = np.asarray(data.observations)
    train_obs = observations[train_idx]
    test_obs = observations[test_idx]
    numeric_mask = h._numeric_channel_mask_from_train(train_obs)
    train_scale = h._train_scale(train_obs, numeric_mask)
    noisy_replicates, validator = h.make_noisy_replicates(
        test_obs,
        train_scale,
        numeric_mask,
        environment,
        prospective_seed,
        test_idx,
    )
    identity = {
        "environment": environment,
        "historical_state_seed": int(mapping["historical_state_seed"]),
        "prospective_test_seed": prospective_seed,
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "train_index_sha256": sha256_array(train_idx),
        "test_index_sha256": sha256_array(test_idx),
        "train_observation_sha256": h._sha256_observation(train_obs),
        "test_observation_sha256": h._sha256_observation(test_obs),
        "numeric_channel_indices": np.flatnonzero(numeric_mask).astype(int).tolist(),
        "train_scale_sha256": sha256_array(train_scale),
        "noisy_observation_sha256": list(validator["replicate_hashes"]),
        "realized_shift_validator": validator,
        "prospective_labels_accessed": False,
    }
    identity["identity_sha256"] = canonical_hash(identity)
    return identity, data, noisy_replicates


def validate_runner_source_contract() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    violations = {
        "representation_constructor": False,
        "extractor_extract_route": False,
        "encoder_fit_route": False,
        "table_encoder_fit_route": False,
        "table_encoder_fit_transform_route": False,
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name) and function.id == "create_extractor":
            violations["representation_constructor"] = True
            continue
        if not isinstance(function, ast.Attribute) or not isinstance(function.value, ast.Name):
            continue
        owner = function.value.id
        method = function.attr
        if owner == "extractor" and method == "extract":
            violations["extractor_extract_route"] = True
        elif owner == "encoder" and method == "fit":
            violations["encoder_fit_route"] = True
        elif owner == "table_encoder" and method == "fit":
            violations["table_encoder_fit_route"] = True
        elif owner == "table_encoder" and method == "fit_transform":
            violations["table_encoder_fit_transform_route"] = True
    checks = {name: not present for name, present in violations.items()}
    if not all(checks.values()):
        raise H3R2RError(f"Runner exposes a prohibited representation-fit route: {checks}")
    return {"status": "PASS", "checks": checks, "transform_path": "table_encoder.transform -> encoder.encode"}


def git_frozen(paths: list[Path]) -> dict[str, Any]:
    checked = []
    for path in paths:
        relative = rel_repo(path)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        ).returncode == 0
        dirty = bool(git("status", "--porcelain", "--", relative))
        checked.append({"path": relative, "tracked": tracked, "dirty": dirty})
        if not tracked or dirty:
            raise H3R2RError(f"Pre-test artifact is not frozen in Git history: {relative}")
    return {"status": "PASS", "head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"), "files": checked}


def run_historical_smoke(
    historical_root: Path,
    reconstruction_root: Path,
    state_seed: int,
    output_path: Path,
) -> dict[str, Any]:
    h = configure_historical_runtime(historical_root)
    frozen_inputs = h.load_frozen_inputs()
    freeze, _ = load_reconstruction(reconstruction_root)
    records = record_map(freeze)
    validate_frozen_record_files(reconstruction_root, records)
    verify_historical_source_lineage(historical_root, h)

    comparisons: list[dict[str, Any]] = []
    for environment in ENVIRONMENTS:
        data, train_idx, train_labels = historical_training_labels(
            environment, state_seed, reconstruction_root, h, frozen_inputs
        )
        test_idx = np.asarray(data.splits["test"], dtype=int)
        observations = np.asarray(data.observations)
        train_obs = observations[train_idx]
        test_obs = observations[test_idx]
        numeric_mask = h._numeric_channel_mask_from_train(train_obs)
        train_scale = h._train_scale(train_obs, numeric_mask)
        noisy_replicates, validator = h.make_noisy_replicates(
            test_obs, train_scale, numeric_mask, environment, state_seed, test_idx
        )
        historical_cell = load_json(
            historical_root
            / "experiments"
            / "OIR_PPV"
            / "H3R"
            / "EXP-H3R-002"
            / "cells"
            / f"{environment}-S{state_seed}.json"
        )
        for learner in SYSTEM_IDS:
            record = records[(environment, state_seed, learner)]
            train_repr = np.load(resolve_frozen_artifact(record["representation_output_path"]), allow_pickle=False)
            extractor = load_frozen_extractor(record)
            readout = build_readout("linear", state_seed)
            readout.fit(train_repr, train_labels)
            clean_repr = frozen_transform(extractor, test_obs)
            clean_prediction = np.asarray(readout.predict(clean_repr))
            noisy_hashes = []
            for noisy_obs in noisy_replicates:
                noisy_prediction = np.asarray(readout.predict(frozen_transform(extractor, noisy_obs)))
                noisy_hashes.append(sha256_array(noisy_prediction))
            expected = historical_cell["system_metrics"][learner]
            clean_match = sha256_array(clean_prediction) == expected["clean_prediction_sha256"]
            noisy_match = noisy_hashes == list(expected["noisy_prediction_sha256"])
            comparisons.append(
                {
                    "environment": environment,
                    "state_seed": state_seed,
                    "learner": learner,
                    "clean_prediction_hash_match": clean_match,
                    "noisy_prediction_hashes_match": noisy_match,
                    "validator_passed": bool(validator["validator_passed"]),
                }
            )
            if not clean_match or not noisy_match or not validator["validator_passed"]:
                raise H3R2RError(f"Historical transform-only smoke mismatch: {environment}/{learner}")

    result = {
        "stage": "H3R2-R-HISTORICAL-SMOKE",
        "status": "PASS",
        "state_seed": state_seed,
        "historical_source_commit": SOURCE_COMMIT,
        "comparison_count": len(comparisons),
        "all_historical_prediction_hashes_reproduced": True,
        "comparisons": comparisons,
        "created_at_utc": utc_now(),
    }
    write_json(output_path, result)
    return result


def run_preflight(
    historical_root: Path,
    reconstruction_root: Path,
    registry_path: Path,
    identity_lock_path: Path,
    qa_path: Path,
) -> dict[str, Any]:
    h = configure_historical_runtime(historical_root)
    frozen_inputs = h.load_frozen_inputs()
    registry = load_json(registry_path)
    mappings = validate_seed_registry(registry)
    freeze, results = load_reconstruction(reconstruction_root)
    records = record_map(freeze)

    git_gate = git_frozen(
        [
            H3R2R_ROOT / "PROSPECTIVE_PROTOCOL_FREEZE_v1.md",
            registry_path,
            Path(__file__),
            H3R2R_ROOT / "RUNNER_CONTRACT_v1.md",
            H3R2R_ROOT / "test_h3r2r_runner.py",
            reconstruction_root / "H3R_RECONSTRUCTION_FREEZE_v1.json",
            reconstruction_root / "RECONSTRUCTION_RESULTS.json",
        ]
    )
    source_contract = validate_runner_source_contract()
    lineage = verify_historical_source_lineage(historical_root, h)
    frozen_artifacts = validate_frozen_record_files(reconstruction_root, records)

    identities = []
    for mapping in mappings:
        first, _, _ = prospective_observation_identity(mapping, h, frozen_inputs)
        second, _, _ = prospective_observation_identity(mapping, h, frozen_inputs)
        if first != second:
            raise H3R2RError(
                f"Prospective observation identity is non-deterministic: {mapping['environment']}/"
                f"{mapping['historical_state_seed']}"
            )
        identities.append(first)

    identity_lock = {
        "lock_id": "H3R2-R-PROSPECTIVE-IDENTITY-LOCK-v1",
        "status": "SEALED_WITHOUT_PROSPECTIVE_LABEL_ACCESS",
        "created_at_utc": utc_now(),
        "source_commit": SOURCE_COMMIT,
        "reconstruction_manifest_sha256": RECONSTRUCTION_MANIFEST_SHA256,
        "seed_registry_sha256": sha256_path(registry_path),
        "runner_sha256": sha256_path(Path(__file__)),
        "cell_count": len(identities),
        "prospective_label_access_count": 0,
        "cells": identities,
    }
    write_json(identity_lock_path, identity_lock)

    qa = {
        "stage": "H3R2-R-PRETEST-QA-v1",
        "status": "PASS",
        "created_at_utc": utc_now(),
        "prospective_labels_accessed": False,
        "git_freeze_gate": git_gate,
        "seed_registry_gate": {
            "status": "PASS",
            "mapping_count": len(mappings),
            "unique": True,
            "disjoint_from_historical": True,
            "derivation_verified": True,
        },
        "reconstruction_gate": {
            "status": "PASS",
            "historical_reproducibility": results["historical_reproducibility"],
            "record_count": results["record_count"],
            "exact_hash_matches": results["exact_hash_matches"],
            "mismatch_count": results["mismatch_count"],
            "manifest_sha256": results["manifest_sha256"],
        },
        "source_lineage_gate": lineage,
        "frozen_artifact_gate": frozen_artifacts,
        "runner_contract_gate": source_contract,
        "deterministic_prospective_observation_gate": {
            "status": "PASS",
            "cell_count": len(identities),
            "double_generation_exact_match": True,
            "prospective_labels_accessed": False,
        },
        "identity_lock_path": rel_repo(identity_lock_path),
        "identity_lock_sha256": sha256_path(identity_lock_path),
    }
    write_json(qa_path, qa)
    return qa


def validate_committed_pretest(
    reconstruction_root: Path,
    registry_path: Path,
    identity_lock_path: Path,
    qa_path: Path,
) -> dict[str, Any]:
    gate = git_frozen(
        [
            H3R2R_ROOT / "PROSPECTIVE_PROTOCOL_FREEZE_v1.md",
            registry_path,
            Path(__file__),
            H3R2R_ROOT / "RUNNER_CONTRACT_v1.md",
            H3R2R_ROOT / "test_h3r2r_runner.py",
            reconstruction_root / "H3R_RECONSTRUCTION_FREEZE_v1.json",
            reconstruction_root / "RECONSTRUCTION_RESULTS.json",
            identity_lock_path,
            qa_path,
        ]
    )
    qa = load_json(qa_path)
    if qa.get("status") != "PASS" or qa.get("prospective_labels_accessed") is not False:
        raise H3R2RError("Committed pre-test QA is not a clean PASS")
    if qa.get("identity_lock_sha256") != sha256_path(identity_lock_path):
        raise H3R2RError("Committed identity lock differs from pre-test QA binding")
    identity_lock = load_json(identity_lock_path)
    if identity_lock.get("status") != "SEALED_WITHOUT_PROSPECTIVE_LABEL_ACCESS":
        raise H3R2RError("Prospective identity lock status is invalid")
    if int(identity_lock.get("prospective_label_access_count", -1)) != 0:
        raise H3R2RError("Prospective identity lock reports prior label access")
    return gate


def identity_lock_map(identity_lock: dict[str, Any]) -> dict[tuple[str, int, int], dict[str, Any]]:
    result = {}
    for cell in identity_lock["cells"]:
        key = (
            str(cell["environment"]),
            int(cell["historical_state_seed"]),
            int(cell["prospective_test_seed"]),
        )
        result[key] = cell
    if len(result) != 20:
        raise H3R2RError("Prospective identity lock does not contain exactly 20 cells")
    return result


def cell_effects(system_metrics: dict[str, Any]) -> dict[str, Any]:
    effects: dict[str, Any] = {}
    for family in READOUT_FAMILIES:
        baseline = system_metrics["L0"][family]["metrics"]
        effects[family] = {}
        for learner in SYSTEM_IDS:
            current = system_metrics[learner][family]["metrics"]
            effects[family][learner] = {
                "clean_error_delta_vs_L0": current["clean_error_rate"] - baseline["clean_error_rate"],
                "noise_effect_delta_vs_L0": current["delta_error_noise"] - baseline["delta_error_noise"],
            }
    return effects


def aggregate_cells(cells: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}
    for family in READOUT_FAMILIES:
        aggregate[family] = {}
        for learner in SYSTEM_IDS:
            rows = []
            for cell in cells:
                metric = cell["system_metrics"][learner][family]["metrics"]
                rows.append((cell, metric))
            by_environment = {}
            for environment in ENVIRONMENTS:
                env_rows = [metric for cell, metric in rows if cell["environment"] == environment]
                by_environment[environment] = {
                    "cell_count": len(env_rows),
                    "mean_clean_error_rate": float(np.mean([r["clean_error_rate"] for r in env_rows])),
                    "mean_clean_accuracy": float(np.mean([r["clean_accuracy"] for r in env_rows])),
                    "mean_noisy_error_rate": float(np.mean([r["mean_noisy_error_rate"] for r in env_rows])),
                    "mean_delta_error_noise": float(np.mean([r["delta_error_noise"] for r in env_rows])),
                }
            total_rows = sum(int(cell["test_rows"]) for cell, _ in rows)
            weighted_clean = sum(float(metric["clean_error_rate"]) * int(cell["test_rows"]) for cell, metric in rows) / total_rows
            weighted_noisy = sum(float(metric["mean_noisy_error_rate"]) * int(cell["test_rows"]) for cell, metric in rows) / total_rows
            paired = [cell["paired_effects"][family][learner] for cell, _ in rows]
            aggregate[family][learner] = {
                "cell_count": len(rows),
                "total_test_rows": total_rows,
                "cell_mean_clean_error_rate": float(np.mean([m["clean_error_rate"] for _, m in rows])),
                "cell_mean_clean_accuracy": float(np.mean([m["clean_accuracy"] for _, m in rows])),
                "cell_mean_noisy_error_rate": float(np.mean([m["mean_noisy_error_rate"] for _, m in rows])),
                "cell_mean_delta_error_noise": float(np.mean([m["delta_error_noise"] for _, m in rows])),
                "row_weighted_clean_error_rate": float(weighted_clean),
                "row_weighted_noisy_error_rate": float(weighted_noisy),
                "row_weighted_delta_error_noise": float(weighted_noisy - weighted_clean),
                "paired_vs_L0": {
                    "mean_clean_error_delta": float(np.mean([p["clean_error_delta_vs_L0"] for p in paired])),
                    "mean_noise_effect_delta": float(np.mean([p["noise_effect_delta_vs_L0"] for p in paired])),
                },
                "by_environment": by_environment,
            }
    return aggregate


def render_results_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# H3R2-R Prospective Results v1",
        "",
        f"Execution status: `{summary['prospective_evidence_status']}`",
        "",
        "Historical reconstruction remains provenance evidence: `100/100` exact historical train-representation hashes. "
        "The prospective measurements below are new evidence and are reported separately for each frozen readout family.",
        "",
        "No support/falsification threshold was added after seeing prospective results. This run therefore reports measurements and paired effects without selecting a winning learner or readout family.",
        "",
        "| Readout | Learner | Clean error | Noisy error | Noise delta | Clean delta vs L0 | Noise-effect delta vs L0 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family in READOUT_FAMILIES:
        for learner in SYSTEM_IDS:
            row = summary["aggregate"][family][learner]
            lines.append(
                f"| {family} | {learner} | {row['cell_mean_clean_error_rate']:.6f} | "
                f"{row['cell_mean_noisy_error_rate']:.6f} | {row['cell_mean_delta_error_noise']:.6f} | "
                f"{row['paired_vs_L0']['mean_clean_error_delta']:.6f} | "
                f"{row['paired_vs_L0']['mean_noise_effect_delta']:.6f} |"
            )
    lines.extend(
        [
            "",
            "Interpretation boundary: this execution establishes that the frozen reconstructed states were evaluated on the pre-registered fresh seed matrix without representation refitting. It does not by itself upgrade the broader OIR-PPV architecture to an established claim.",
            "",
        ]
    )
    return "\n".join(lines)


def execute_prospective(
    historical_root: Path,
    reconstruction_root: Path,
    registry_path: Path,
    identity_lock_path: Path,
    qa_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    if output_root.exists():
        raise H3R2RError(f"Prospective output already exists; result-dependent rerun refused: {output_root}")

    committed_pretest = validate_committed_pretest(
        reconstruction_root, registry_path, identity_lock_path, qa_path
    )
    h = configure_historical_runtime(historical_root)
    frozen_inputs = h.load_frozen_inputs()
    registry = load_json(registry_path)
    mappings = validate_seed_registry(registry)
    freeze, reconstruction_results = load_reconstruction(reconstruction_root)
    records = record_map(freeze)
    validate_frozen_record_files(reconstruction_root, records)
    verify_historical_source_lineage(historical_root, h)
    identity_lock = load_json(identity_lock_path)
    locked_cells = identity_lock_map(identity_lock)

    output_root.mkdir(parents=True, exist_ok=False)
    access = {
        "event_id": "H3R2-R-PROSPECTIVE-ACCESS-001",
        "opened_at_utc": utc_now(),
        "prospective_label_access": True,
        "selection_access": False,
        "protocol_sha256": sha256_path(H3R2R_ROOT / "PROSPECTIVE_PROTOCOL_FREEZE_v1.md"),
        "seed_registry_sha256": sha256_path(registry_path),
        "identity_lock_sha256": sha256_path(identity_lock_path),
        "pretest_qa_sha256": sha256_path(qa_path),
        "runner_sha256": sha256_path(Path(__file__)),
        "git_head": committed_pretest["head"],
        "no_result_dependent_rerun": True,
    }
    write_json(output_root / "access.json", access)

    cells: list[dict[str, Any]] = []
    historical_cache: dict[tuple[str, int], tuple[np.ndarray, dict[str, np.ndarray]]] = {}

    try:
        for mapping in mappings:
            environment = str(mapping["environment"])
            state_seed = int(mapping["historical_state_seed"])
            prospective_seed = int(mapping["prospective_test_seed"])
            identity, data, noisy_replicates = prospective_observation_identity(mapping, h, frozen_inputs)
            locked = locked_cells[(environment, state_seed, prospective_seed)]
            if identity != locked:
                raise H3R2RError(f"Prospective observation identity drift: {environment}/{state_seed}/{prospective_seed}")

            test_idx = np.asarray(data.splits["test"], dtype=int)
            clean_test_obs = np.asarray(data.observations)[test_idx]
            test_labels = np.asarray(data.labels)[test_idx]

            cache_key = (environment, state_seed)
            if cache_key not in historical_cache:
                _, _, train_labels = historical_training_labels(
                    environment, state_seed, reconstruction_root, h, frozen_inputs
                )
                train_repr_by_learner = {
                    learner: np.load(
                        resolve_frozen_artifact(records[(environment, state_seed, learner)]["representation_output_path"]),
                        allow_pickle=False,
                    )
                    for learner in SYSTEM_IDS
                }
                historical_cache[cache_key] = (train_labels, train_repr_by_learner)
            train_labels, train_repr_by_learner = historical_cache[cache_key]

            system_metrics: dict[str, Any] = {}
            for learner in SYSTEM_IDS:
                record = records[(environment, state_seed, learner)]
                extractor = load_frozen_extractor(record)
                clean_repr = frozen_transform(extractor, clean_test_obs)
                noisy_repr = [frozen_transform(extractor, noisy_obs) for noisy_obs in noisy_replicates]
                train_repr = train_repr_by_learner[learner]
                if len(train_repr) != len(train_labels):
                    raise H3R2RError(f"Historical readout training rows mismatch: {environment}/{state_seed}/{learner}")

                learner_results: dict[str, Any] = {}
                for family in READOUT_FAMILIES:
                    readout = build_readout(family, state_seed)
                    readout.fit(train_repr, train_labels)
                    clean_prediction = np.asarray(readout.predict(clean_repr))
                    clean_metric = prediction_metrics(clean_prediction, test_labels)
                    noisy_predictions = [np.asarray(readout.predict(value)) for value in noisy_repr]
                    noisy_metrics = [prediction_metrics(pred, test_labels) for pred in noisy_predictions]
                    mean_noisy_error = float(np.mean([item["error_rate"] for item in noisy_metrics]))
                    learner_results[family] = {
                        "readout_spec": readout_spec(family, state_seed),
                        "metrics": {
                            "clean_error_rate": clean_metric["error_rate"],
                            "clean_accuracy": clean_metric["accuracy"],
                            "noisy_error_rates": [item["error_rate"] for item in noisy_metrics],
                            "noisy_accuracies": [item["accuracy"] for item in noisy_metrics],
                            "mean_noisy_error_rate": mean_noisy_error,
                            "mean_noisy_accuracy": 1.0 - mean_noisy_error,
                            "delta_error_noise": mean_noisy_error - clean_metric["error_rate"],
                        },
                        "clean_prediction_sha256": sha256_array(clean_prediction),
                        "noisy_prediction_sha256": [sha256_array(pred) for pred in noisy_predictions],
                    }
                system_metrics[learner] = {
                    "frozen_state_sha256": record["model_state_hash"],
                    "preprocessing_sha256": record["preprocessing_hash"],
                    "historical_train_representation_sha256": record["representation_output_hash"],
                    "clean_prospective_representation_sha256": sha256_array(clean_repr),
                    "noisy_prospective_representation_sha256": [sha256_array(value) for value in noisy_repr],
                    "representation_dim": int(clean_repr.shape[1]),
                    **learner_results,
                }

            cell = {
                "environment": environment,
                "historical_state_seed": state_seed,
                "prospective_test_seed": prospective_seed,
                "source_commit": SOURCE_COMMIT,
                "reconstruction_manifest_sha256": RECONSTRUCTION_MANIFEST_SHA256,
                "identity_lock_sha256": sha256_path(identity_lock_path),
                "test_rows": int(len(test_idx)),
                "prospective_test_label_sha256": sha256_array(test_labels),
                "prospective_identity_sha256": identity["identity_sha256"],
                "paired_noisy_observation_sha256": identity["noisy_observation_sha256"],
                "realized_shift_validator": identity["realized_shift_validator"],
                "system_metrics": system_metrics,
            }
            cell["paired_effects"] = cell_effects(system_metrics)
            cell["valid"] = bool(identity["realized_shift_validator"]["validator_passed"])
            if not cell["valid"]:
                raise H3R2RError(f"Prospective noise validator failed: {environment}/{state_seed}")
            cell_path = output_root / "cells" / f"{environment}-S{state_seed}-P{prospective_seed}.json"
            write_json(cell_path, cell)
            cells.append(cell)

        if len(cells) != 20:
            raise H3R2RError(f"Prospective matrix incomplete: {len(cells)}/20")

        aggregate = aggregate_cells(cells)
        summary = {
            "experiment_id": "H3R2-R-PROSPECTIVE-v1",
            "completed_at_utc": utc_now(),
            "historical_reproducibility": reconstruction_results["historical_reproducibility"],
            "historical_exact_hash_matches": reconstruction_results["exact_hash_matches"],
            "prospective_evidence_status": "COMPLETE_MEASURED",
            "prospective_cell_count": len(cells),
            "readout_families": list(READOUT_FAMILIES),
            "selection_policy": "NO_RESULT_DEPENDENT_LEARNER_OR_READOUT_SELECTION",
            "claim_verdict_policy": "MEASUREMENTS_ONLY_NO_POSTHOC_SUPPORT_THRESHOLD",
            "aggregate": aggregate,
            "scientific_boundary": (
                "Historical 100/100 reconstruction is provenance evidence only. Prospective metrics are new "
                "fresh-seed evidence. This run does not by itself establish the broader OIR-PPV architecture."
            ),
        }
        summary_path = output_root / "H3R2R_PROSPECTIVE_SUMMARY_v1.json"
        write_json(summary_path, summary)
        write_json(output_root / "cell_index.json", cells)
        (output_root / "RESULTS.md").write_text(render_results_markdown(summary), encoding="utf-8")

        artifact_hashes = {}
        for path in sorted(output_root.rglob("*")):
            if path.is_file() and path.name != "RUN_MANIFEST_v1.json":
                artifact_hashes[path.relative_to(output_root).as_posix()] = sha256_path(path)
        run_manifest = {
            "manifest_id": "H3R2-R-PROSPECTIVE-RUN-MANIFEST-v1",
            "status": "COMPLETE",
            "created_at_utc": utc_now(),
            "source_commit": SOURCE_COMMIT,
            "reconstruction_manifest_sha256": RECONSTRUCTION_MANIFEST_SHA256,
            "git_head_at_access": access["git_head"],
            "artifacts": artifact_hashes,
        }
        write_json(output_root / "RUN_MANIFEST_v1.json", run_manifest)
        return summary
    except Exception as exc:
        write_json(
            output_root / "failure.json",
            {
                "experiment_id": "H3R2-R-PROSPECTIVE-v1",
                "failed_at_utc": utc_now(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "prospective_label_access_occurred": True,
                "result_dependent_rerun_permitted": False,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="H3R2-R reconstruction-gated prospective runner")
    parser.add_argument("--mode", required=True, choices=("historical-smoke", "preflight", "execute"))
    parser.add_argument("--historical-root", type=Path, default=DEFAULT_HISTORICAL_ROOT)
    parser.add_argument("--reconstruction-root", type=Path, default=DEFAULT_RECONSTRUCTION_ROOT)
    parser.add_argument("--seed-registry", type=Path, default=DEFAULT_SEED_REGISTRY)
    parser.add_argument("--identity-lock", type=Path, default=DEFAULT_IDENTITY_LOCK)
    parser.add_argument("--pretest-qa", type=Path, default=DEFAULT_PRETEST_QA)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--state-seed", type=int, default=223691)
    args = parser.parse_args()

    if args.mode == "historical-smoke":
        output = args.output or H3R2R_ROOT / f"HISTORICAL_REPLAY_SMOKE_S{args.state_seed}.json"
        result = run_historical_smoke(
            args.historical_root,
            args.reconstruction_root,
            int(args.state_seed),
            output,
        )
        print(json.dumps({"stage": result["stage"], "status": result["status"], "output": str(output)}))
        return 0
    if args.mode == "preflight":
        result = run_preflight(
            args.historical_root,
            args.reconstruction_root,
            args.seed_registry,
            args.identity_lock,
            args.pretest_qa,
        )
        print(json.dumps({"stage": result["stage"], "status": result["status"], "qa": str(args.pretest_qa)}))
        return 0

    output_root = args.output or DEFAULT_EXECUTION_ROOT
    result = execute_prospective(
        args.historical_root,
        args.reconstruction_root,
        args.seed_registry,
        args.identity_lock,
        args.pretest_qa,
        output_root,
    )
    print(
        json.dumps(
            {
                "experiment_id": result["experiment_id"],
                "status": result["prospective_evidence_status"],
                "cells": result["prospective_cell_count"],
                "output": str(output_root),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
