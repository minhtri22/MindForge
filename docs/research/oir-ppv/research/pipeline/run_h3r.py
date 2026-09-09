"""OIR-PPV H3R v1.0 preflight and one-shot decisive execution.

This runner is intentionally separate from the historical H3 closure path.  It
implements only the frozen H3R observation-noise contract and refuses to reuse
historical trained artifacts as scientific evidence.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import environments  # noqa: F401 -- register frozen generators
from environments.base import EnvironmentConfig, EnvironmentRegistry
from pipeline.run_m3_experiment import TableEncoder, _apply_overrides, _metadata_table, create_extractor
import pipeline.learners_extended  # noqa: F401 -- register L1-L4 encoders


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_MD = ROOT / "protocols/h3r/H3R_PROTOCOL_v1.0.md"
PROTOCOL_JSON = ROOT / "protocols/h3r/h3r_protocol_v1.0.json"
TEST_MANIFEST = ROOT / "protocols/h3r/h3r_test_manifest_v1.0.json"
FREEZE_MANIFEST = ROOT / "governance/v1.0_source_of_truth_manifest.json"
LEARNER_MANIFEST = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json"
PLAN_PATH = ROOT / "PLAN.md"
ACCESS_LOG = ROOT / "protocols/h3r/h3r_test_access_log.md"
DEFAULT_EXECUTION_ROOT = ROOT / "experiments/OIR_PPV/H3R/EXP-H3R-001"
SMOKE_SEED = 424242
BOOTSTRAP_SEED = 20260909
BOOTSTRAP_RESAMPLES = 10_000
CI_LEVEL = 0.9875
CI_TAIL = (1.0 - CI_LEVEL) / 2.0
NOISE_DELTA = 0.10
NOISE_REPLICATES = 4
NOISE_MARGIN = 0.01
UTILITY_MARGIN = 0.02
WORST_ENV_VETO = 0.02
SYSTEM_IDS = ("L0", "L1", "L2", "L3", "L4")
CANDIDATE_IDS = ("L1", "L2", "L3", "L4")


class H3RProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class FrozenInputs:
    protocol: dict[str, Any]
    test_manifest: dict[str, Any]
    freeze_manifest: dict[str, Any]
    learner_manifest: dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_array(value: np.ndarray) -> str:
    return _sha256_bytes(np.ascontiguousarray(value).tobytes())


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def load_frozen_inputs() -> FrozenInputs:
    return FrozenInputs(
        protocol=_load_json(PROTOCOL_JSON),
        test_manifest=_load_json(TEST_MANIFEST),
        freeze_manifest=_load_json(FREEZE_MANIFEST),
        learner_manifest=_load_json(LEARNER_MANIFEST),
    )


def _learner_map(frozen: FrozenInputs) -> dict[str, dict[str, Any]]:
    return {entry["learner_id"]: entry for entry in frozen.learner_manifest["learners"]}


def validate_static_contract(*, require_pristine_access_log: bool = True) -> dict[str, Any]:
    frozen = load_frozen_inputs()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise H3RProtocolError(f"Static H3R contract check failed: {name}: {detail}")

    canonical = frozen.freeze_manifest["canonical"]
    for key in ("h3r_protocol_frozen", "h3r_protocol_instance", "h3r_test_manifest"):
        entry = canonical[key]
        path = ROOT / entry["path"]
        check(f"freeze_hash:{key}", _sha256_path(path) == entry["sha256"], str(path))
    if require_pristine_access_log:
        entry = canonical["h3r_test_access_log"]
        check(
            "freeze_hash:h3r_test_access_log",
            _sha256_path(ROOT / entry["path"]) == entry["sha256"],
            entry["path"],
        )

    protocol = frozen.protocol
    check("protocol_status", protocol["identity"]["status"] == "FROZEN")
    check("execution_status_at_freeze", protocol["identity"]["execution_status"] == "NOT_EXECUTED")
    check("test_access_count_at_freeze", protocol["test_lock"]["test_access_count"] == 0)
    check("test_manifest_hash", _sha256_path(TEST_MANIFEST) == protocol["test_lock"]["test_hash"])
    check("protocol_markdown_hash", _sha256_path(PROTOCOL_MD) == protocol["provenance"]["protocol_sha256"])
    check("h3r_seed_set", frozen.test_manifest["h3r_seeds"] == [271828, 314159, 161803, 141421, 173205])
    check("cell_count", frozen.test_manifest["cell_count"] == 20)
    check("total_test_rows", frozen.test_manifest["total_test_rows"] == 6131)
    check("noise_replicates", frozen.test_manifest["noise_contract"]["replicates_per_test_row"] == NOISE_REPLICATES)
    check("noise_delta", float(frozen.test_manifest["noise_contract"]["delta"]) == NOISE_DELTA)

    for relative, expected in frozen.test_manifest["source_hashes"].items():
        path = ROOT / relative
        check(f"source_hash:{relative}", path.is_file() and _sha256_path(path) == expected, relative)

    learners = _learner_map(frozen)
    check("learner_ids", set(learners) == set(SYSTEM_IDS), sorted(learners))
    check(
        "learner_manifest_hash",
        _sha256_path(LEARNER_MANIFEST)
        == frozen.protocol["provenance"]["learner_artifact_hashes"]["historical_definition_manifest_sha256"],
    )
    check("h4_not_opened_plan", "H4  NOT_OPENED / DEFERRED_BY_OWNER" in PLAN_PATH.read_text(encoding="utf-8"))

    return {"status": "PASS", "checks": checks}


def _environment_config(environment_id: str, seed: int, frozen: FrozenInputs) -> EnvironmentConfig:
    config_path = ROOT / f"environments/env{environment_id[-1]}_config.yaml"
    import yaml

    base = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    overrides = frozen.test_manifest["environment_generation_overrides"][environment_id]
    effective = _apply_overrides(base, overrides)
    env_section = effective.get("environment", effective)
    generation = env_section.get("generation", effective.get("generation", {}))
    return EnvironmentConfig(
        family=env_section.get("family", environment_id),
        name=env_section.get("name", environment_id),
        version=env_section.get("version", "1.0"),
        generation=generation,
        raw_config=effective,
    )


def generate_frozen_cell(environment_id: str, seed: int, frozen: FrozenInputs):
    config = _environment_config(environment_id, seed, frozen)
    env = EnvironmentRegistry.create(environment_id, config, seed)
    return env.generate()


def validate_test_identity_hashes() -> dict[str, Any]:
    """Hash-only validation. It deliberately computes no model prediction or metric."""
    frozen = load_frozen_inputs()
    evidence = []
    cells = {(c["environment"], int(c["seed"])): c for c in frozen.test_manifest["cells"]}
    for environment_id in frozen.test_manifest["environments"]:
        for seed in frozen.test_manifest["h3r_seeds"]:
            expected = cells[(environment_id, int(seed))]
            data = generate_frozen_cell(environment_id, int(seed), frozen)
            idx = np.asarray(data.splits["test"])
            obs = np.asarray(data.observations[idx])
            labels = np.asarray(data.labels[idx])
            actual = {
                "count": int(len(idx)),
                "test_index_sha256": _sha256_array(idx),
                "test_observation_sha256": _sha256_array(obs),
                "test_label_sha256": _sha256_array(labels),
            }
            passed = (
                actual["count"] == int(expected["test_count"])
                and actual["test_index_sha256"] == expected["test_index_sha256"]
                and actual["test_observation_sha256"] == expected["test_observation_sha256"]
                and actual["test_label_sha256"] == expected["test_label_sha256"]
            )
            evidence.append({"environment": environment_id, "seed": int(seed), "passed": passed, **actual})
            if not passed:
                raise H3RProtocolError(f"Frozen test identity mismatch for {environment_id} seed {seed}")
    return {"status": "PASS", "cell_count": len(evidence), "cells": evidence}


def _context_tables(data, train_idx: np.ndarray, other_idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    raw = _metadata_table(data.metadata, "Z", "context_variables", len(data.labels))
    encoder = TableEncoder()
    train = encoder.fit_transform(np.asarray(raw)[train_idx])
    other = encoder.transform(np.asarray(raw)[other_idx])
    return train, other


def _fit_representation_and_probe(
    learner: dict[str, Any],
    seed: int,
    train_obs: np.ndarray,
    train_context: np.ndarray,
    train_labels: np.ndarray,
):
    extractor_config = {"type": learner["type"], **learner["params"], "seed": int(seed)}
    extractor = create_extractor(extractor_config, int(seed))
    train_result = extractor.extract(train_obs, train_context, train_labels)
    train_repr = np.asarray(train_result.invariant_representation, dtype=float)
    probe = LogisticRegression(
        solver="lbfgs",
        penalty="l2",
        C=1.0,
        max_iter=1000,
        random_state=int(seed),
    )
    probe.fit(train_repr, train_labels)
    return extractor, probe, train_repr


def runtime_smoke_preflight() -> dict[str, Any]:
    """Train/evaluate shapes on a non-frozen seed using train+validation only."""
    frozen = load_frozen_inputs()
    learners = _learner_map(frozen)
    evidence = []
    for environment_id in frozen.test_manifest["environments"]:
        data = generate_frozen_cell(environment_id, SMOKE_SEED, frozen)
        train_idx = np.asarray(data.splits["train"], dtype=int)
        val_idx = np.asarray(data.splits["val"], dtype=int)
        if len(train_idx) == 0 or len(val_idx) == 0:
            raise H3RProtocolError(f"Empty smoke train/val support for {environment_id}")
        train_context, val_context = _context_tables(data, train_idx, val_idx)
        train_obs = np.asarray(data.observations[train_idx])
        val_obs = np.asarray(data.observations[val_idx])
        train_labels = np.asarray(data.labels[train_idx])
        for system_id in SYSTEM_IDS:
            extractor, probe, train_repr = _fit_representation_and_probe(
                learners[system_id], SMOKE_SEED, train_obs, train_context, train_labels
            )
            val_repr = np.asarray(extractor.extract(val_obs, val_context, None).invariant_representation)
            pred = np.asarray(probe.predict(val_repr))
            passed = (
                len(pred) == len(val_idx)
                and train_repr.ndim == 2
                and val_repr.ndim == 2
                and np.isfinite(train_repr).all()
                and np.isfinite(val_repr).all()
            )
            evidence.append({
                "environment": environment_id,
                "system": system_id,
                "passed": bool(passed),
                "train_rows": int(len(train_idx)),
                "val_rows": int(len(val_idx)),
                "representation_dim": int(val_repr.shape[1]),
            })
            if not passed:
                raise H3RProtocolError(f"Runtime smoke failed for {environment_id}/{system_id}")
    return {"status": "PASS", "smoke_seed": SMOKE_SEED, "checks": evidence}


def h3r_noise_seed(environment_id: str, generator_seed: int, row_identity: int, replicate_index: int) -> int:
    material = (
        f"OIR-PPV-H3R|v1.0|{environment_id}|{int(generator_seed)}|"
        f"{int(row_identity)}|{int(replicate_index)}"
    ).encode("utf-8")
    # Frozen contract says uint32(SHA256(...)); casting the digest integer to
    # uint32 is modulo 2^32, i.e. the low 32 bits.
    return int(hashlib.sha256(material).hexdigest(), 16) & 0xFFFFFFFF


def _train_scale(train_obs: np.ndarray) -> np.ndarray:
    numeric = np.asarray(train_obs, dtype=float)
    scale = np.std(numeric, axis=0, ddof=0)
    return np.maximum(scale, 1e-6)


def make_noisy_replicates(
    clean_obs: np.ndarray,
    train_scale: np.ndarray,
    environment_id: str,
    generator_seed: int,
    row_identities: np.ndarray,
) -> tuple[list[np.ndarray], dict[str, Any]]:
    clean = np.asarray(clean_obs, dtype=float)
    scale = np.asarray(train_scale, dtype=float)
    noisy_replicates: list[np.ndarray] = []
    replicate_hashes = []
    max_normalized = 0.0
    for replicate_index in range(NOISE_REPLICATES):
        noisy = clean.copy()
        for row_offset, row_identity in enumerate(row_identities):
            rng = np.random.default_rng(
                h3r_noise_seed(environment_id, generator_seed, int(row_identity), replicate_index)
            )
            eta = NOISE_DELTA * scale * rng.uniform(-1.0, 1.0, size=clean.shape[1])
            noisy[row_offset] = clean[row_offset] + eta
        normalized = np.abs(noisy - clean) / scale
        current = float(np.max(normalized)) if normalized.size else 0.0
        max_normalized = max(max_normalized, current)
        if current > NOISE_DELTA + 1e-12:
            raise H3RProtocolError(
                f"Realized-shift validator failed: normalized L_inf={current} > {NOISE_DELTA}"
            )
        replicate_hashes.append(_sha256_array(noisy))
        noisy_replicates.append(noisy)
    return noisy_replicates, {
        "replicate_hashes": replicate_hashes,
        "max_train_scale_normalized_l_inf": max_normalized,
        "same_environment_seed_row_label_metadata": True,
        "env_intervene_called": False,
        "regeneration_between_pair_members": False,
        "label_dependent_noise": False,
        "same_noisy_observation_shared_across_systems": True,
        "validator_passed": True,
    }


def _risk(prediction: np.ndarray, labels: np.ndarray) -> float:
    return float(np.mean(np.asarray(prediction) != np.asarray(labels)))


def _bootstrap_indices() -> np.ndarray:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    return rng.integers(0, 5, size=(BOOTSTRAP_RESAMPLES, 4, 5), endpoint=False)


def _stratified_bootstrap(cell_effects: dict[str, list[float]], indices: np.ndarray) -> dict[str, Any]:
    envs = ("ENV-1", "ENV-2", "ENV-3", "ENV-4")
    matrix = np.vstack([np.asarray(cell_effects[env], dtype=float) for env in envs])
    if matrix.shape != (4, 5):
        raise H3RProtocolError(f"Expected 4x5 paired cell effects, got {matrix.shape}")
    point = float(matrix.mean(axis=1).mean())
    boot = np.empty(BOOTSTRAP_RESAMPLES, dtype=float)
    for i in range(BOOTSTRAP_RESAMPLES):
        env_means = [float(matrix[e, indices[i, e]].mean()) for e in range(4)]
        boot[i] = float(np.mean(env_means))
    low, high = np.quantile(boot, [CI_TAIL, 1.0 - CI_TAIL])
    return {
        "estimate": point,
        "ci_level": CI_LEVEL,
        "ci_low": float(low),
        "ci_high": float(high),
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "quantile_method": "numpy_default_linear",
    }


def _runtime_manifest() -> dict[str, Any]:
    try:
        git = {
            "head": _git("rev-parse", "HEAD"),
            "branch": _git("branch", "--show-current"),
            "status_scientific_scope": _git(
                "status", "--porcelain", "--", "docs/research/oir-ppv/research"
            ).splitlines(),
        }
    except Exception as exc:  # pragma: no cover - provenance fallback only
        git = {"error": str(exc)}
    return {
        "created_at_utc": _utc_now(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "git": git,
        "implementation_bindings": {
            "std_train": "numpy.std(axis=0, ddof=0)",
            "uint32_sha256": "int(SHA256_hex, 16) mod 2^32",
            "bootstrap_quantile": "numpy.quantile default linear method",
        },
        "source_hashes": {
            "pipeline/run_h3r.py": _sha256_path(Path(__file__)),
            "pipeline/run_m3_experiment.py": _sha256_path(ROOT / "pipeline/run_m3_experiment.py"),
            "pipeline/learners.py": _sha256_path(ROOT / "pipeline/learners.py"),
            "pipeline/learners_extended.py": _sha256_path(ROOT / "pipeline/learners_extended.py"),
        },
    }


def run_preflight(output_path: Path | None = None) -> dict[str, Any]:
    result = {
        "stage": "H3R-E0",
        "status": "PASS",
        "created_at_utc": _utc_now(),
        "static_contract": validate_static_contract(require_pristine_access_log=True),
        "hash_only_test_identity": validate_test_identity_hashes(),
        "runtime_smoke": runtime_smoke_preflight(),
        "scientific_test_metric_access": False,
        "scientific_test_access_count_increment": 0,
    }
    if output_path is not None:
        _write_json(output_path, result)
    return result


def _load_authorization(path: Path) -> dict[str, Any]:
    auth = _load_json(path)
    if auth.get("execution_authorized") is not True:
        raise H3RProtocolError("H3R decisive execution authorization is absent")
    if auth.get("protocol_sha256") != _sha256_path(PROTOCOL_MD):
        raise H3RProtocolError("Authorization protocol hash does not match frozen H3R protocol")
    if auth.get("test_manifest_sha256") != _sha256_path(TEST_MANIFEST):
        raise H3RProtocolError("Authorization test-manifest hash does not match frozen H3R test lock")
    return auth


def _append_scientific_access_event(authorization: dict[str, Any]) -> str:
    current = ACCESS_LOG.read_text(encoding="utf-8")
    if "H3R_DECISIVE_ACCESS_001" in current:
        raise H3RProtocolError("Decisive scientific test access is already recorded; rerun refused")
    timestamp = _utc_now()
    line = (
        f"\n| {timestamp} | H3R_DECISIVE_ACCESS_001; owner-authorized one-shot H3R v1.0 "
        f"decisive execution | yes | no | yes |\n"
    )
    ACCESS_LOG.write_text(current.rstrip() + "\n" + line, encoding="utf-8")
    return timestamp


def execute_decisive(authorization_path: Path, output_root: Path = DEFAULT_EXECUTION_ROOT) -> dict[str, Any]:
    if output_root.exists():
        raise H3RProtocolError(f"Refusing H3R rerun/overwrite: {output_root}")
    frozen = load_frozen_inputs()
    static = validate_static_contract(require_pristine_access_log=True)
    auth = _load_authorization(authorization_path)
    identity = validate_test_identity_hashes()
    output_root.mkdir(parents=True, exist_ok=False)
    _write_json(output_root / "authorization_snapshot.json", auth)
    _write_json(output_root / "pre_execution_identity.json", identity)
    _write_json(output_root / "runtime_manifest.json", _runtime_manifest())
    access_timestamp = _append_scientific_access_event(auth)

    learners = _learner_map(frozen)
    expected_cells = {(c["environment"], int(c["seed"])): c for c in frozen.test_manifest["cells"]}
    all_cells: list[dict[str, Any]] = []
    bootstrap_indices = _bootstrap_indices()

    try:
        for environment_id in frozen.test_manifest["environments"]:
            for seed in frozen.test_manifest["h3r_seeds"]:
                seed = int(seed)
                data = generate_frozen_cell(environment_id, seed, frozen)
                train_idx = np.asarray(data.splits["train"], dtype=int)
                test_idx = np.asarray(data.splits["test"], dtype=int)
                clean_test_obs = np.asarray(data.observations[test_idx], dtype=float)
                test_labels = np.asarray(data.labels[test_idx])
                expected = expected_cells[(environment_id, seed)]
                if (
                    _sha256_array(test_idx) != expected["test_index_sha256"]
                    or _sha256_array(clean_test_obs) != expected["test_observation_sha256"]
                    or _sha256_array(test_labels) != expected["test_label_sha256"]
                ):
                    raise H3RProtocolError(f"Decisive identity mismatch for {environment_id}/{seed}")

                train_obs = np.asarray(data.observations[train_idx], dtype=float)
                train_labels = np.asarray(data.labels[train_idx])
                train_context, test_context = _context_tables(data, train_idx, test_idx)
                scale = _train_scale(train_obs)
                noisy_replicates, validator = make_noisy_replicates(
                    clean_test_obs, scale, environment_id, seed, test_idx
                )
                system_metrics: dict[str, Any] = {}

                for system_id in SYSTEM_IDS:
                    extractor, probe, train_repr = _fit_representation_and_probe(
                        learners[system_id], seed, train_obs, train_context, train_labels
                    )
                    clean_repr = np.asarray(
                        extractor.extract(clean_test_obs, test_context, None).invariant_representation,
                        dtype=float,
                    )
                    clean_prediction = np.asarray(probe.predict(clean_repr))
                    clean_risk = _risk(clean_prediction, test_labels)
                    noisy_losses = []
                    noisy_prediction_hashes = []
                    for noisy_obs in noisy_replicates:
                        noisy_repr = np.asarray(
                            extractor.extract(noisy_obs, test_context, None).invariant_representation,
                            dtype=float,
                        )
                        noisy_prediction = np.asarray(probe.predict(noisy_repr))
                        noisy_losses.append(_risk(noisy_prediction, test_labels))
                        noisy_prediction_hashes.append(_sha256_array(noisy_prediction))
                    noisy_risk = float(np.mean(noisy_losses))
                    system_metrics[system_id] = {
                        "R_clean": clean_risk,
                        "R_noisy": noisy_risk,
                        "DeltaR_noise": noisy_risk - clean_risk,
                        "train_representation_sha256": _sha256_array(train_repr),
                        "clean_prediction_sha256": _sha256_array(clean_prediction),
                        "noisy_prediction_sha256": noisy_prediction_hashes,
                        "runtime_encoder_type": type(extractor.encoder).__name__,
                        "probe": {
                            "id": "H3R-LR-v1",
                            "solver": "lbfgs",
                            "penalty": "l2",
                            "C": 1.0,
                            "max_iter": 1000,
                            "seed": seed,
                        },
                    }

                baseline = system_metrics["L0"]
                candidate_effects = {}
                for candidate_id in CANDIDATE_IDS:
                    candidate = system_metrics[candidate_id]
                    candidate_effects[candidate_id] = {
                        "E_noise": candidate["DeltaR_noise"] - baseline["DeltaR_noise"],
                        "DeltaR_clean_vs_L0": candidate["R_clean"] - baseline["R_clean"],
                    }

                cell = {
                    "environment": environment_id,
                    "seed": seed,
                    "train_rows": int(len(train_idx)),
                    "test_rows": int(len(test_idx)),
                    "test_identity": {
                        "index_sha256": _sha256_array(test_idx),
                        "observation_sha256": _sha256_array(clean_test_obs),
                        "label_sha256": _sha256_array(test_labels),
                    },
                    "train_scale_sha256": _sha256_array(scale),
                    "realized_shift_validator": validator,
                    "system_metrics": system_metrics,
                    "candidate_effects": candidate_effects,
                    "valid": bool(validator["validator_passed"]),
                }
                all_cells.append(cell)
                _write_json(output_root / "cells" / f"{environment_id}-S{seed}.json", cell)

        if len(all_cells) != 20 or not all(cell["valid"] for cell in all_cells):
            raise H3RProtocolError("H3R decisive matrix is incomplete or contains invalid cells")

        candidate_results = {}
        for candidate_id in CANDIDATE_IDS:
            noise_by_env: dict[str, list[float]] = {env: [] for env in frozen.test_manifest["environments"]}
            utility_by_env: dict[str, list[float]] = {env: [] for env in frozen.test_manifest["environments"]}
            for cell in all_cells:
                effect = cell["candidate_effects"][candidate_id]
                noise_by_env[cell["environment"]].append(float(effect["E_noise"]))
                utility_by_env[cell["environment"]].append(float(effect["DeltaR_clean_vs_L0"]))
            noise_ci = _stratified_bootstrap(noise_by_env, bootstrap_indices)
            utility_ci = _stratified_bootstrap(utility_by_env, bootstrap_indices)
            env_means = {env: float(np.mean(values)) for env, values in noise_by_env.items()}
            worst_case_pass = all(value <= WORST_ENV_VETO for value in env_means.values())
            support = (
                noise_ci["ci_high"] < -NOISE_MARGIN
                and utility_ci["ci_high"] <= UTILITY_MARGIN
                and worst_case_pass
            )
            falsified = (
                noise_ci["ci_low"] > -NOISE_MARGIN
                or utility_ci["ci_low"] > UTILITY_MARGIN
            )
            verdict = (
                "SUPPORTED_UNDER_TESTED_CONDITIONS"
                if support
                else "FALSIFIED_UNDER_TESTED_CONDITIONS"
                if falsified
                else "INCONCLUSIVE"
            )
            candidate_results[candidate_id] = {
                "E_noise": noise_ci,
                "DeltaR_clean_vs_L0": utility_ci,
                "environment_mean_E_noise": env_means,
                "worst_case_support_veto_passed": worst_case_pass,
                "verdict": verdict,
            }

        verdicts = [candidate_results[c]["verdict"] for c in CANDIDATE_IDS]
        if "SUPPORTED_UNDER_TESTED_CONDITIONS" in verdicts:
            global_verdict = "SUPPORTED_UNDER_TESTED_CONDITIONS"
        elif all(v == "FALSIFIED_UNDER_TESTED_CONDITIONS" for v in verdicts):
            global_verdict = "FALSIFIED_UNDER_TESTED_CONDITIONS"
        else:
            global_verdict = "INCONCLUSIVE"

        summary = {
            "protocol_id": "OIR-PPV-H3R",
            "protocol_version": "v1.0",
            "experiment_id": "EXP-H3R-001",
            "execution_started_by_access_event_utc": access_timestamp,
            "completed_at_utc": _utc_now(),
            "static_contract": static,
            "matrix": {"valid_cells": 20, "expected_cells": 20, "total_test_rows": 6131},
            "candidate_results": candidate_results,
            "global_verdict": global_verdict,
            "claim_boundary": frozen.protocol["claim_boundary"],
            "no_retry_policy": "ONE_SHOT_COMPLETE; NO RESULT-DEPENDENT RETRY",
        }
        _write_json(output_root / "h3r_summary.json", summary)
        _write_json(output_root / "cell_index.json", all_cells)
        return summary
    except Exception as exc:
        failure = {
            "protocol_id": "OIR-PPV-H3R",
            "protocol_version": "v1.0",
            "experiment_id": "EXP-H3R-001",
            "failed_at_utc": _utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "scientific_test_access_count": 1,
            "rerun_permitted": False,
        }
        _write_json(output_root / "failure.json", failure)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="OIR-PPV H3R v1.0 runner")
    parser.add_argument("--mode", choices=("preflight", "execute"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()

    if args.mode == "preflight":
        output = args.output or ROOT / "artifacts/h3r_e0/preflight.json"
        result = run_preflight(output)
        print(json.dumps({"stage": result["stage"], "status": result["status"]}))
        return 0
    if args.authorization is None:
        parser.error("--authorization is required for --mode execute")
    output = args.output or DEFAULT_EXECUTION_ROOT
    result = execute_decisive(args.authorization, output)
    print(json.dumps({"global_verdict": result["global_verdict"], "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
