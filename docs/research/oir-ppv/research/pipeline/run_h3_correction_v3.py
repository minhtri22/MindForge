"""Versioned H3 provenance and causal-isolation correction replay (v3 retry identity)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import sklearn
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.run_h3_closure as h3v1
from pipeline.causal_validation import CausalValidator
from pipeline.dependency_analysis import DependencyAnalyzer


EXP_V1 = ROOT / "experiments/OIR_PPV/H3_Closure/EXP-H3-001"
ART_V1 = ROOT / "artifacts/h3_closure/EXP-H3-001"
EXP_V2 = EXP_V1 / "correction_v3"
ART_V2 = ART_V1 / "correction_v3"
PRESERVATION = EXP_V2 / "v1_preservation_manifest.json"
SOURCE_MANIFEST = EXP_V2 / "source_manifest_v3.json"
RUNTIME_MANIFEST = EXP_V2 / "runtime_environment_v3.json"
EXEC_MANIFEST = EXP_V2 / "h3_execution_manifest_v3.json"
EXEC_MANIFEST_HASH = EXP_V2 / "h3_execution_manifest_v3.sha256"
SMOKE = EXP_V2 / "h3_smoke_evidence_v3.json"
SUMMARY = EXP_V2 / "h3_summary_v3.json"
REPORT = EXP_V2 / "H3_CLOSURE_REPORT_v3.md"
RECONCILIATION = EXP_V2 / "artifact_reconciliation_v3.json"
MATRIX_EXECUTION = ART_V2 / "matrix_execution_v3.json"
EXECUTION_LOG = ART_V2 / "execution_log_v3.jsonl"

REFERENCE_MANIFEST = h3v1.REFERENCE_MANIFEST
REFERENCE_CONFIG_ROOT = h3v1.REFERENCE_CONFIG_ROOT
M3_PROTOCOL = h3v1.M3_PROTOCOL
LEARNERS = h3v1.LEARNERS
CANDIDATES = h3v1.CANDIDATES
ENVS = h3v1.ENVS
SEEDS = h3v1.SEEDS
BASELINE = h3v1.BASELINE
ELIGIBLE_ENVS = h3v1.TASK_PRESERVING_ENVS

CANONICAL_HASH_ALGORITHM = "H3-CANONICAL-NESTED-SHA256-v1"
EXPECTED_V1_MANIFEST_SHA = "045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad"
EXPECTED_M3_SHA = "f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a"
EXPECTED_REFERENCE_SHA = "f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656"
EXPECTED_COUNTS = {"complete": 75, "failed": 0, "inapplicable": 25}
TARGETS = {
    "ENV-1": "background_noise",
    "ENV-2": "occlusion",
    "ENV-3": "do(N)",
    "ENV-4": "spurious_feature",
}

COMMANDS = {
    "freeze": "python pipeline/run_h3_correction_v3.py freeze",
    "smoke": "python pipeline/run_h3_correction_v3.py smoke",
    "matrix": "python pipeline/run_h3_correction_v3.py run",
    "aggregate": "python pipeline/run_h3_correction_v3.py aggregate",
    "reconcile": "python pipeline/run_h3_correction_v3.py reconcile",
    "verify_v1_after": "python pipeline/run_h3_correction_v3.py verify-v1-after",
    "compile": "python -m py_compile pipeline/run_h3_closure.py pipeline/run_h3_correction_v3.py",
    "focused_tests": "python -m pytest tests/test_h3_correction_v3.py -q -p no:cacheprovider --basetemp artifacts/h3_v3_pytest_focused_20260909",
    "regression_tests": "python -m pytest tests/test_h3_closure.py tests/test_h2_closure.py tests/test_learner_contract.py tests/test_real_learners.py tests/test_h3_correction_v3.py -q -p no:cacheprovider --basetemp artifacts/h3_v3_pytest_regression_20260909",
}


class CorrectionStop(RuntimeError):
    pass


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any, *, refuse_overwrite: bool = False) -> None:
    if refuse_overwrite and path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _json_scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    return value


def canonical_hash(value: Any) -> str:
    """Hash nested metadata with explicit ndarray dtype/shape/bytes semantics."""
    h = hashlib.sha256()

    def emit(v: Any) -> None:
        if isinstance(v, np.ndarray):
            a = np.ascontiguousarray(v)
            h.update(b"A")
            h.update(str(a.dtype).encode())
            h.update(json.dumps(list(a.shape), separators=(",", ":")).encode())
            h.update(a.tobytes(order="C"))
        elif isinstance(v, np.generic):
            emit(v.item())
        elif isinstance(v, dict):
            h.update(b"D{")
            for key in sorted(v, key=lambda x: str(x)):
                emit(str(key))
                emit(v[key])
            h.update(b"}")
        elif isinstance(v, (list, tuple)):
            h.update(b"L[")
            for item in v:
                emit(item)
            h.update(b"]")
        elif v is None:
            h.update(b"N")
        elif isinstance(v, bool):
            h.update(b"B1" if v else b"B0")
        elif isinstance(v, int):
            h.update(f"I{v}".encode())
        elif isinstance(v, float):
            h.update(b"F" + np.asarray([v], dtype=np.float64).tobytes())
        elif isinstance(v, bytes):
            h.update(b"Y" + len(v).to_bytes(8, "big") + v)
        else:
            s = str(v).encode("utf-8")
            h.update(b"S" + len(s).to_bytes(8, "big") + s)

    emit(value)
    return h.hexdigest()


def _log(action: str, **fields: Any) -> None:
    EXECUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "action": action, **fields}
    with EXECUTION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=_json_scalar) + "\n")


def _preservation_status() -> dict:
    if not PRESERVATION.is_file():
        raise CorrectionStop("V1_EVIDENCE_INTEGRITY_FAILURE: preservation manifest missing")
    manifest = _read_json(PRESERVATION)
    mismatches = []
    for item in manifest["files"]:
        p = ROOT / item["path"]
        if not p.is_file():
            mismatches.append({"path": item["path"], "reason": "missing"})
            continue
        actual = _sha(p)
        if actual != item["sha256"] or p.stat().st_size != item["bytes"]:
            mismatches.append({"path": item["path"], "expected": item["sha256"], "actual": actual})
    return {"file_count": len(manifest["files"]), "mismatch_count": len(mismatches), "mismatches": mismatches}


def verify_v1_after() -> dict:
    status = _preservation_status()
    if status["mismatch_count"]:
        raise CorrectionStop("V1_EVIDENCE_INTEGRITY_FAILURE")
    _log("verify_v1_after", **status)
    return {"status": "VERIFIED_AFTER_CORRECTION", **status}


def _source_paths() -> list[Path]:
    paths = [
        ROOT / "pipeline/run_h3_closure.py",
        ROOT / "pipeline/run_h3_correction_v3.py",
        ROOT / "tests/test_h3_closure.py",
        ROOT / "tests/test_h3_correction_v3.py",
        ROOT / "pipeline/run_m3_experiment.py",
        ROOT / "pipeline/causal_validation.py",
        ROOT / "pipeline/dependency_analysis.py",
        ROOT / "pipeline/learners.py",
        ROOT / "pipeline/learners_extended.py",
        ROOT / "environments/base.py",
        ROOT / "environments/env1_generator.py",
        ROOT / "environments/env2_generator.py",
        ROOT / "environments/env3_generator.py",
        ROOT / "environments/env4_generator.py",
        M3_PROTOCOL,
        REFERENCE_MANIFEST,
    ]
    paths += [REFERENCE_CONFIG_ROOT / f"{learner}-{env}-S{seed}.yaml" for learner in LEARNERS for env in ENVS for seed in SEEDS]
    paths += [ROOT / f"environments/env{i}_config.yaml" for i in range(1, 5)]
    return paths


def _source_manifest_payload() -> dict:
    reference = _read_json(REFERENCE_MANIFEST)
    fidelity = {x["learner_id"]: x for x in reference["learners"]}
    files = []
    for p in _source_paths():
        if not p.is_file():
            raise CorrectionStop(f"CORRECTION_FREEZE_INVALIDATED: missing source {p}")
        files.append({"path": _rel(p), "sha256": _sha(p), "bytes": p.stat().st_size})
    learner_rows = []
    for learner in LEARNERS:
        example = yaml.safe_load((REFERENCE_CONFIG_ROOT / f"{learner}-ENV-1-S42.yaml").read_text(encoding="utf-8"))
        cfg = example["pipeline"]["invariant_extractor"]
        extractor = h3v1.create_extractor(cfg, 42)
        wrapped = getattr(extractor, "encoder", None)
        runtime_class = type(extractor).__name__
        wrapped_class = type(wrapped).__name__ if wrapped is not None else None
        learner_rows.append({
            "learner_id": learner,
            "fidelity": fidelity[learner]["fidelity"],
            "requested_type": cfg["type"],
            "runtime_extractor_class": runtime_class,
            "wrapped_learner_class": wrapped_class,
            "module_path": type(wrapped if wrapped is not None else extractor).__module__,
            "implementation_source_sha256": _sha(ROOT / ("pipeline/learners_extended.py" if learner in {"L1", "L2", "L3", "L4"} else "pipeline/learners.py")),
            "effective_hyperparameters_by_cell": [
                {
                    "environment": env,
                    "seed": seed,
                    "config": yaml.safe_load((REFERENCE_CONFIG_ROOT / f"{learner}-{env}-S{seed}.yaml").read_text(encoding="utf-8"))["pipeline"]["invariant_extractor"],
                }
                for env in ENVS for seed in SEEDS
            ],
        })
    return {"version": 3, "hash_algorithm": "SHA256", "files": files, "learners": learner_rows}


def _scoped_dirty_inventory(source_paths: list[str]) -> tuple[list[str], str]:
    status = _git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    needles = {str(Path(p).as_posix()) for p in source_paths}
    scoped = []
    prefix = "docs/research/oir-ppv/research/"
    for line in status:
        path = line[3:].replace("\\", "/") if len(line) > 3 else ""
        local = path[len(prefix):] if path.startswith(prefix) else path
        if local in needles:
            scoped.append(line)
    scoped.sort()
    return scoped, hashlib.sha256("\n".join(scoped).encode()).hexdigest()


def _runtime_payload(source_manifest: dict) -> dict:
    import sklearn as _sk
    source_rel = [x["path"] for x in source_manifest["files"]]
    inventory, inventory_hash = _scoped_dirty_inventory(source_rel)
    now_local = datetime.now().astimezone()
    return {
        "version": 3,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_local": now_local.isoformat(),
        "timezone": str(now_local.tzinfo),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "dependencies": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": _sk.__version__,
            "pyyaml": yaml.__version__,
        },
        "repository_root": str(ROOT),
        "branch": _git("branch", "--show-current"),
        "git_head": _git("rev-parse", "HEAD"),
        "dirty": bool(_git("status", "--porcelain")),
        "scoped_dirty_inventory": inventory,
        "scoped_dirty_inventory_sha256": inventory_hash,
        "commands": COMMANDS,
        "artifact_paths": {"coordination": _rel(EXP_V2), "raw": _rel(ART_V2)},
        "environment_secrets_recorded": False,
    }


def freeze() -> dict:
    if any(p.exists() for p in (SOURCE_MANIFEST, RUNTIME_MANIFEST, EXEC_MANIFEST, EXEC_MANIFEST_HASH)):
        raise FileExistsError("Refusing to overwrite v3 freeze files")
    preservation = _preservation_status()
    if preservation["mismatch_count"]:
        raise CorrectionStop("V1_EVIDENCE_INTEGRITY_FAILURE")
    if _sha(EXP_V1 / "h3_execution_manifest.json") != EXPECTED_V1_MANIFEST_SHA:
        raise CorrectionStop("V1_EVIDENCE_INTEGRITY_FAILURE: v1 execution manifest")
    if _sha(M3_PROTOCOL) != EXPECTED_M3_SHA or _sha(REFERENCE_MANIFEST) != EXPECTED_REFERENCE_SHA:
        raise CorrectionStop("PROTOCOL_AMENDMENT_REQUIRED")
    source = _source_manifest_payload()
    _write_json(SOURCE_MANIFEST, source, refuse_overwrite=True)
    runtime = _runtime_payload(source)
    _write_json(RUNTIME_MANIFEST, runtime, refuse_overwrite=True)
    cells = [{"cell_id": f"{l}-{e}-S{s}", "learner": l, "environment": e, "seed": s} for l in LEARNERS for e in ENVS for s in SEEDS]
    v1 = _read_json(EXP_V1 / "h3_execution_manifest.json")
    manifest = {
        "version": 3,
        "experiment_id": "EXP-H3-001",
        "correction_namespace": "correction_v3",
        "status": "frozen_before_v3_retry_replay",
        "v1_scientific_identity": v1,
        "v1_execution_manifest_sha256": EXPECTED_V1_MANIFEST_SHA,
        "v1_preservation_manifest_sha256": _sha(PRESERVATION),
        "source_manifest_sha256": _sha(SOURCE_MANIFEST),
        "runtime_manifest_sha256": _sha(RUNTIME_MANIFEST),
        "m3_protocol_sha256": EXPECTED_M3_SHA,
        "reference_manifest_sha256": EXPECTED_REFERENCE_SHA,
        "matrix": cells,
        "cell_count": 100,
        "one_attempt_no_retry_policy": True,
        "canonical_metadata_hash": {"algorithm": CANONICAL_HASH_ALGORITHM, "dictionary_keys": "sorted", "ndarray": "dtype+shape+C-order-bytes"},
        "scientific_reconciliation_rule": "project every v3 object onto v1 scientific keys, excluding provenance; exact JSON equality; additive v3 provenance/causal-isolation fields ignored",
        "numerical_comparison_policy": "exact emitted JSON scalar equality; no tolerance",
        "commands": COMMANDS,
        "expected_outputs": [
            _rel(SMOKE), _rel(MATRIX_EXECUTION), _rel(RECONCILIATION), _rel(SUMMARY), _rel(REPORT), _rel(EXECUTION_LOG)
        ],
        "raw_latent_shift_role": "SCALE_SENSITIVE_DIAGNOSTIC_ONLY",
        "selected_targets": TARGETS,
    }
    _write_json(EXEC_MANIFEST, manifest, refuse_overwrite=True)
    EXEC_MANIFEST_HASH.write_text(_sha(EXEC_MANIFEST), encoding="utf-8")
    _log("freeze", command=COMMANDS["freeze"], manifest_sha256=_sha(EXEC_MANIFEST))
    return {"status": "FROZEN", "source_manifest_sha256": _sha(SOURCE_MANIFEST), "runtime_manifest_sha256": _sha(RUNTIME_MANIFEST), "execution_manifest_sha256": _sha(EXEC_MANIFEST)}


def _verify_frozen_identity() -> None:
    if not EXEC_MANIFEST.is_file() or not EXEC_MANIFEST_HASH.is_file():
        raise CorrectionStop("CORRECTION_FREEZE_INVALIDATED: freeze missing")
    if EXEC_MANIFEST_HASH.read_text(encoding="utf-8").strip() != _sha(EXEC_MANIFEST):
        raise CorrectionStop("CORRECTION_FREEZE_INVALIDATED: execution manifest drift")
    manifest = _read_json(EXEC_MANIFEST)
    if _sha(SOURCE_MANIFEST) != manifest["source_manifest_sha256"] or _sha(RUNTIME_MANIFEST) != manifest["runtime_manifest_sha256"]:
        raise CorrectionStop("CORRECTION_FREEZE_INVALIDATED: source/runtime manifest drift")
    source = _read_json(SOURCE_MANIFEST)
    for item in source["files"]:
        p = ROOT / item["path"]
        if not p.is_file() or _sha(p) != item["sha256"]:
            raise CorrectionStop(f"CORRECTION_FREEZE_INVALIDATED: {item['path']}")
    runtime = _read_json(RUNTIME_MANIFEST)
    current = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "branch": _git("branch", "--show-current"),
        "git_head": _git("rev-parse", "HEAD"),
        "numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__, "pyyaml": yaml.__version__,
    }
    expected = {
        "python_executable": runtime["python_executable"], "python_version": runtime["python_version"],
        "branch": runtime["branch"], "git_head": runtime["git_head"],
        "numpy": runtime["dependencies"]["numpy"], "scipy": runtime["dependencies"]["scipy"],
        "scikit_learn": runtime["dependencies"]["scikit_learn"], "pyyaml": runtime["dependencies"]["pyyaml"],
    }
    if current != expected:
        raise CorrectionStop(f"CORRECTION_FREEZE_INVALIDATED: runtime identity {current} != {expected}")
    if _sha(M3_PROTOCOL) != EXPECTED_M3_SHA or _sha(REFERENCE_MANIFEST) != EXPECTED_REFERENCE_SHA:
        raise CorrectionStop("CORRECTION_FREEZE_INVALIDATED: protocol/reference drift")


def _metadata_views(metadata: dict, env_id: str) -> dict:
    if env_id == "ENV-1":
        task_state = metadata.get("structural_variables", {})
        context = metadata.get("context_variables", {})
        nuisance = metadata.get("nuisance_variables", {})
    elif env_id == "ENV-2":
        task_state = metadata.get("factor_values", {})
        context = metadata.get("context_variables", {})
        nuisance = metadata.get("nuisance_variables", {})
    elif env_id == "ENV-3":
        task_state = {k: metadata[k] for k in ("S", "A") if k in metadata}
        context = {"Z": metadata.get("Z")}
        nuisance = {"N": metadata.get("N")}
    elif env_id == "ENV-4":
        task_state = metadata.get("structural_variables", {})
        context = metadata.get("context_variables", {})
        nuisance = metadata.get("nuisance_variables", {})
    else:
        raise ValueError(env_id)
    return {"task_state": task_state, "context": context, "nuisance": nuisance}


def _target_key(env_id: str, target: str) -> str:
    return "N" if env_id == "ENV-3" and target == "do(N)" else target


def _causal_hashes(metadata: dict, labels: np.ndarray, observations: np.ndarray, env_id: str, target: str | None = None) -> dict:
    views = _metadata_views(metadata, env_id)
    nuisance = views["nuisance"]
    key = _target_key(env_id, target) if target else None
    separate = {str(k): canonical_hash(v) for k, v in nuisance.items()}
    non_target = {k: v for k, v in nuisance.items() if str(k) != str(key)} if key is not None else nuisance
    return {
        "observations_sha256": canonical_hash(observations),
        "labels_sha256": canonical_hash(labels),
        "task_state_sha256": canonical_hash(views["task_state"]),
        "context_sha256": canonical_hash(views["context"]),
        "full_nuisance_sha256": canonical_hash(nuisance),
        "nuisance_variables_sha256": separate,
        "target_nuisance_sha256": canonical_hash(nuisance.get(key)) if key in nuisance else None,
        "non_target_nuisance_sha256": canonical_hash(non_target),
    }


def _prepare_cell(learner: str, env_id: str, seed: int) -> dict:
    old_root = h3v1.ARTIFACT_ROOT
    try:
        h3v1.ARTIFACT_ROOT = ART_V2
        return h3v1._prepare_cell(learner, env_id, seed)
    finally:
        h3v1.ARTIFACT_ROOT = old_root


def _mock_data(prepared: dict, seed: int) -> Any:
    return type("H3V3PairData", (), {
        "observations": prepared["test_obs"], "labels": prepared["test_labels"], "metadata": prepared["metadata"],
        "splits": {}, "config_hash": "", "seed": seed, "timestamp": "",
    })()


def _paired_interventions_v3(prepared: dict, env_id: str, seed: int) -> tuple[str | None, list[Any], list[dict]]:
    target, values = CausalValidator._target_and_values(prepared["env"], prepared["metadata"], "nuisance")
    if target != TARGETS[env_id]:
        raise CorrectionStop(f"CAUSAL_ISOLATION_FAILURE: selected target {env_id}={target}, expected={TARGETS[env_id]}")
    factual_hash = _causal_hashes(prepared["metadata"], prepared["test_labels"], prepared["test_obs"], env_id, target)
    rows = []
    for index, value in enumerate(values):
        intervened = prepared["env"].intervene(_mock_data(prepared, seed), target, value)
        after_hash = _causal_hashes(intervened.metadata, intervened.labels, intervened.observations, env_id, target)
        checks = {
            "task_state_same": factual_hash["task_state_sha256"] == after_hash["task_state_sha256"],
            "context_same": factual_hash["context_sha256"] == after_hash["context_sha256"],
            "labels_same": factual_hash["labels_sha256"] == after_hash["labels_sha256"],
            "target_nuisance_changed": factual_hash["target_nuisance_sha256"] != after_hash["target_nuisance_sha256"],
            "non_target_nuisance_same": factual_hash["non_target_nuisance_sha256"] == after_hash["non_target_nuisance_sha256"],
            "observations_changed": factual_hash["observations_sha256"] != after_hash["observations_sha256"],
        }
        eligible = all(checks.values())
        additive = {"causal_isolation": {"before": factual_hash, "after": after_hash, **checks}}
        if not checks["labels_same"]:
            row = {"index": index, "target": target, "value": _json_scalar(value), "task_preserving": False, "reason": "environment intervention changed task labels", **additive}
            rows.append(row)
            continue
        if env_id in ELIGIBLE_ENVS and not eligible:
            raise CorrectionStop(f"CAUSAL_ISOLATION_FAILURE: {env_id} seed={seed} value={value} checks={checks}")
        intervened_i = prepared["extractor"].extract(intervened.observations, prepared["test_context"], None).invariant_representation
        accuracy = float(prepared["predictor"].score(intervened_i, prepared["test_labels"]))
        mean_shift = float(np.mean(np.abs(prepared["factual_i"] - intervened_i)))
        row = {
            "index": index, "target": target, "value": _json_scalar(value), "task_preserving": True,
            "factual_accuracy": prepared["factual_accuracy"], "intervened_accuracy": accuracy,
            "delta_n": prepared["factual_accuracy"] - accuracy, "abs_delta_n": abs(prepared["factual_accuracy"] - accuracy),
            "mean_shift": mean_shift, "invariance_score": 1.0 / (1.0 + mean_shift),
            "failure_below_frozen_0_5": (1.0 / (1.0 + mean_shift)) < 0.5,
            "intervened_observation_sha256": h3v1._array_hash(intervened.observations),
            "intervened_representation_sha256": h3v1._array_hash(intervened_i),
            **additive,
        }
        rows.append(row)
    return target, [_json_scalar(x) for x in values], rows


def _run_cell_v3(learner: str, env_id: str, seed: int, output_root: Path) -> dict:
    _verify_frozen_identity()
    cell_id = f"{learner}-{env_id}-S{seed}"
    out = output_root / cell_id
    evidence_path = out / "paired_evidence_v3.json"
    if evidence_path.exists():
        raise CorrectionStop(f"one-attempt policy: {cell_id} already exists")
    out.mkdir(parents=True, exist_ok=True)
    prepared = _prepare_cell(learner, env_id, seed)
    target, values, interventions = _paired_interventions_v3(prepared, env_id, seed)
    clean = [row for row in interventions if row.get("task_preserving")]
    dependency = DependencyAnalyzer(seed).analyze(prepared["factual_i"], prepared["test_context"], prepared["test_nuisance"], config_hash=prepared["extractor"].get_config_hash())
    leak_n = max((x.leakage_score for x in dependency.nuisance_sensitivities), default=0.0)
    task_preserving = bool(clean) and len(clean) == len(interventions)
    status = "complete" if task_preserving else ("inapplicable" if env_id == "ENV-3" else "failed")
    factual_causal = _causal_hashes(prepared["metadata"], prepared["test_labels"], prepared["test_obs"], env_id, target)
    result = {
        "cell_id": cell_id, "status": status, "learner": learner, "environment": env_id, "seed": seed,
        "factual_sample_sha256": h3v1._array_hash(prepared["test_obs"]), "task_label_sha256": h3v1._array_hash(prepared["test_labels"]),
        "nuisance_target": target, "nuisance_values": values, "factual_predictive_utility": prepared["factual_accuracy"],
        "leak_n": float(leak_n), "nuisance_leakage_detected": bool(dependency.nuisance_leakage_detected),
        "avg_nuisance_sensitivity": float(dependency.avg_nuisance_sensitivity),
        "shortcut_learning_score": float(dependency.shortcut_learning_score) if env_id == "ENV-4" else None,
        "interventions": interventions,
        "mean_abs_delta_n": float(np.mean([x["abs_delta_n"] for x in clean])) if clean else None,
        "mean_do_n_invariance": float(np.mean([x["invariance_score"] for x in clean])) if clean else None,
        "failure_count": sum(bool(x.get("failure_below_frozen_0_5")) for x in clean), "task_preserving": task_preserving,
        "causal_isolation_factual": factual_causal,
        "raw_latent_shift_role": "SCALE_SENSITIVE_DIAGNOSTIC_ONLY",
        "provenance": {
            "config_path": _rel(prepared["config_path"]), "config_sha256": _sha(prepared["config_path"]),
            "effective_config_sha256": _sha(prepared["effective_path"]), "h3_execution_manifest_sha256": EXPECTED_V1_MANIFEST_SHA,
            "reference_manifest_sha256": _sha(REFERENCE_MANIFEST), "m3_protocol_sha256": _sha(M3_PROTOCOL),
            "extractor_config_hash": prepared["extractor"].get_config_hash(),
            "h3_execution_manifest_v3_sha256": _sha(EXEC_MANIFEST), "source_manifest_v3_sha256": _sha(SOURCE_MANIFEST),
            "runtime_environment_v3_sha256": _sha(RUNTIME_MANIFEST), "canonical_hash_algorithm": CANONICAL_HASH_ALGORITHM,
        },
    }
    _write_json(evidence_path, result, refuse_overwrite=True)
    _log("cell_attempt", cell_id=cell_id, status=status, evidence_sha256=_sha(evidence_path))
    return result


def smoke() -> dict:
    _verify_frozen_identity()
    if SMOKE.exists():
        raise FileExistsError("Refusing to overwrite v3 smoke")
    smoke_root = ART_V2 / "smoke"
    baseline = _run_cell_v3("L0", "ENV-4", 42, smoke_root)
    candidate = _run_cell_v3("L1", "ENV-4", 42, smoke_root)
    identity_fields = ["factual_sample_sha256", "task_label_sha256", "nuisance_target", "nuisance_values"]
    checks = {f"same_{k}": baseline[k] == candidate[k] for k in identity_fields}
    checks.update({
        "same_task_state": baseline["causal_isolation_factual"]["task_state_sha256"] == candidate["causal_isolation_factual"]["task_state_sha256"],
        "same_context": baseline["causal_isolation_factual"]["context_sha256"] == candidate["causal_isolation_factual"]["context_sha256"],
        "task_preserving_both": baseline["task_preserving"] and candidate["task_preserving"],
        "all_interventions_causally_isolated": all(all(r["causal_isolation"][k] for k in ("task_state_same","context_same","labels_same","target_nuisance_changed","non_target_nuisance_same","observations_changed")) for cell in (baseline,candidate) for r in cell["interventions"]),
    })
    passed = all(checks.values())
    evidence = {"status": "PASS" if passed else "FAIL", "pair": "L1-vs-L0-ENV-4-S42", "checks": checks}
    _write_json(SMOKE, evidence, refuse_overwrite=True)
    _log("smoke", command=COMMANDS["smoke"], status=evidence["status"])
    if not passed:
        raise CorrectionStop("CAUSAL_ISOLATION_FAILURE: smoke")
    return evidence


def run_matrix() -> dict:
    _verify_frozen_identity()
    if not SMOKE.is_file() or _read_json(SMOKE).get("status") != "PASS":
        raise CorrectionStop("smoke PASS required")
    if MATRIX_EXECUTION.exists() or (ART_V2 / "full").exists():
        raise CorrectionStop("one-attempt policy: matrix already attempted")
    statuses = {"complete": 0, "failed": 0, "inapplicable": 0}
    failures = []
    for learner in LEARNERS:
        for env_id in ENVS:
            for seed in SEEDS:
                cell_id = f"{learner}-{env_id}-S{seed}"
                try:
                    result = _run_cell_v3(learner, env_id, seed, ART_V2 / "full")
                    statuses[result["status"]] += 1
                except Exception as exc:
                    statuses["failed"] += 1
                    failure = {"cell_id": cell_id, "status": "failed", "error": repr(exc)}
                    failures.append(failure)
                    fp = ART_V2 / "full" / cell_id / "failure_v3.json"
                    if not fp.exists():
                        _write_json(fp, failure, refuse_overwrite=True)
                    _log("cell_failure", **failure)
                    if isinstance(exc, CorrectionStop) and "CAUSAL_ISOLATION_FAILURE" in str(exc):
                        _write_json(MATRIX_EXECUTION, {"experiment_id":"EXP-H3-001","version":3,"counts":statuses,"failures":failures,"status":"CAUSAL_ISOLATION_FAILURE"}, refuse_overwrite=True)
                        raise
    result = {"experiment_id": "EXP-H3-001", "version": 3, "counts": statuses, "failures": failures, "attempted_cells": sum(statuses.values()), "one_attempt_no_retry": True}
    _write_json(MATRIX_EXECUTION, result, refuse_overwrite=True)
    _log("matrix_complete", command=COMMANDS["matrix"], **result)
    return result


def _load_v3_cell(learner: str, env_id: str, seed: int) -> dict | None:
    p = ART_V2 / "full" / f"{learner}-{env_id}-S{seed}" / "paired_evidence_v3.json"
    return _read_json(p) if p.is_file() else None


def _compute_summary() -> dict:
    learner_environment = []
    per_seed = []
    for learner in LEARNERS:
        for env_id in ENVS:
            cells = [_load_v3_cell(learner, env_id, seed) for seed in SEEDS]
            present = [x for x in cells if x]
            complete = [x for x in present if x["status"] == "complete"]
            for cell in present:
                per_seed.append({k: cell[k] for k in ("learner","environment","seed","status","nuisance_target","nuisance_values","factual_predictive_utility","leak_n","mean_abs_delta_n","mean_do_n_invariance","failure_count")})
            learner_environment.append({
                "learner": learner, "environment": env_id, "complete_seeds": len(complete),
                "inapplicable_seeds": sum(x["status"] == "inapplicable" for x in present),
                "failed_or_missing_seeds": len(SEEDS)-len(complete)-sum(x["status"] == "inapplicable" for x in present),
                "mean_abs_delta_n": float(np.mean([x["mean_abs_delta_n"] for x in complete])) if complete else None,
                "mean_leak_n": float(np.mean([x["leak_n"] for x in complete])) if complete else None,
                "mean_predictive_utility": float(np.mean([x["factual_predictive_utility"] for x in complete])) if complete else None,
                "mean_do_n_invariance": float(np.mean([x["mean_do_n_invariance"] for x in complete])) if complete else None,
                "mean_shortcut_learning_score": float(np.mean([x["shortcut_learning_score"] for x in complete])) if env_id == "ENV-4" and complete else None,
                "failure_count": sum(x["failure_count"] for x in complete),
            })
    comparisons=[]
    pair_rows=[]
    for learner in CANDIDATES:
        pairs=[]; missing=[]
        for env_id in ELIGIBLE_ENVS:
            for seed in SEEDS:
                cand=_load_v3_cell(learner,env_id,seed); base=_load_v3_cell(BASELINE,env_id,seed); pair_id=f"{learner}-vs-{BASELINE}-{env_id}-S{seed}"
                if not cand or not base or cand["status"]!="complete" or base["status"]!="complete": missing.append(pair_id); continue
                identity = all(cand["causal_isolation_factual"][k] == base["causal_isolation_factual"][k] for k in ("observations_sha256","labels_sha256","task_state_sha256","context_sha256")) and cand["nuisance_target"]==base["nuisance_target"] and cand["nuisance_values"]==base["nuisance_values"]
                if not identity: missing.append(pair_id+":pair_identity_mismatch"); continue
                row={"pair_id":pair_id,"environment":env_id,"seed":seed,"delta_task_degradation":cand["mean_abs_delta_n"]-base["mean_abs_delta_n"],"delta_leak_n":cand["leak_n"]-base["leak_n"],"delta_predictive_utility":cand["factual_predictive_utility"]-base["factual_predictive_utility"],"delta_do_n_invariance":cand["mean_do_n_invariance"]-base["mean_do_n_invariance"]}
                pairs.append(row); pair_rows.append({"learner":learner,**row})
        if missing: label="INCONCLUSIVE"; degenerate=False
        else:
            mt=float(np.mean([x["delta_task_degradation"] for x in pairs])); ml=float(np.mean([x["delta_leak_n"] for x in pairs])); mu=float(np.mean([x["delta_predictive_utility"] for x in pairs])); mi=float(np.mean([x["delta_do_n_invariance"] for x in pairs])); degenerate=mi>0 and mu<0; label="SUPPORTED" if mt<0 and ml<=0 and mu>=0 else "NOT_SUPPORTED"
        comparisons.append({"learner":learner,"complete_pairs":len(pairs),"missing_pairs":missing,"mean_delta_task_degradation":float(np.mean([x["delta_task_degradation"] for x in pairs])) if pairs else None,"mean_delta_leak_n":float(np.mean([x["delta_leak_n"] for x in pairs])) if pairs else None,"mean_delta_predictive_utility":float(np.mean([x["delta_predictive_utility"] for x in pairs])) if pairs else None,"mean_delta_do_n_invariance":float(np.mean([x["delta_do_n_invariance"] for x in pairs])) if pairs else None,"task_degradation_wins":sum(x["delta_task_degradation"]<0 for x in pairs),"leakage_wins_or_ties":sum(x["delta_leak_n"]<=0 for x in pairs),"utility_retained_pairs":sum(x["delta_predictive_utility"]>=0 for x in pairs),"task_degradation_wlt":{"wins":sum(x["delta_task_degradation"]<0 for x in pairs),"losses":sum(x["delta_task_degradation"]>0 for x in pairs),"ties":sum(x["delta_task_degradation"]==0 for x in pairs)},"leakage_wlt":{"wins":sum(x["delta_leak_n"]<0 for x in pairs),"losses":sum(x["delta_leak_n"]>0 for x in pairs),"ties":sum(x["delta_leak_n"]==0 for x in pairs)},"utility_wlt":{"wins":sum(x["delta_predictive_utility"]>0 for x in pairs),"losses":sum(x["delta_predictive_utility"]<0 for x in pairs),"ties":sum(x["delta_predictive_utility"]==0 for x in pairs)},"degenerate":degenerate,"developer_candidate_h3":label,"candidate_authority":"DEVELOPER_CANDIDATE_ONLY"})
    labels=[x["developer_candidate_h3"] for x in comparisons]
    global_label="INCONCLUSIVE" if "INCONCLUSIVE" in labels else ("SUPPORTED" if all(x=="SUPPORTED" for x in labels) else "NOT_SUPPORTED")
    counts={"complete":0,"failed":0,"inapplicable":0}
    for l in LEARNERS:
        for e in ENVS:
            for s in SEEDS:
                c=_load_v3_cell(l,e,s); counts[c["status"] if c else "failed"]+=1
    return {"experiment_id":"EXP-H3-001","version":2,"status":"READY_FOR_QA_REVIEW","matrix_counts":counts,"task_preserving_environments":ELIGIBLE_ENVS,"inapplicable_environment":{"environment":"ENV-3","reason":"existing do(N) recomputes Y and task labels"},"selected_targets":TARGETS,"per_seed_evidence":per_seed,"learner_environment_summaries":learner_environment,"pair_rows":pair_rows,"comparisons":comparisons,"global_developer_candidate_h3":global_label,"candidate_authority":"DEVELOPER_CANDIDATE_ONLY","raw_latent_shift_role":"SCALE_SENSITIVE_DIAGNOSTIC_ONLY","claim_boundary":"Selected targets background_noise in ENV-1, occlusion in ENV-2, spurious_feature in ENV-4; seeds 42/123/456/789/1011; tested L1-L4 adapted/surrogate configurations versus frozen L0/PCA. ENV-3 is inapplicable because do(N) changes Y and task labels."}


def aggregate() -> dict:
    _verify_frozen_identity()
    if not MATRIX_EXECUTION.is_file(): raise CorrectionStop("matrix execution missing")
    summary=_compute_summary()
    _write_json(SUMMARY,summary)
    _log("aggregate",command=COMMANDS["aggregate"],global_candidate=summary["global_developer_candidate_h3"])
    return summary


def _project_to_v1(v1: Any, v2: Any, path: str="") -> Any:
    if isinstance(v1, dict):
        return {k:_project_to_v1(v,v2[k],f"{path}.{k}") for k,v in v1.items() if k != "provenance"}
    if isinstance(v1, list):
        return [_project_to_v1(a,b,f"{path}[{i}]") for i,(a,b) in enumerate(zip(v1,v2))]
    return v2


def _diff(a: Any, b: Any, path: str="$") -> list[dict]:
    if type(a) is not type(b) and not (isinstance(a,(int,float)) and isinstance(b,(int,float))): return [{"path":path,"v1":a,"v2":b}]
    if isinstance(a,dict):
        out=[]
        for k in a:
            if k not in b: out.append({"path":f"{path}.{k}","v1":a[k],"v2":"<missing>"})
            else: out += _diff(a[k],b[k],f"{path}.{k}")
        return out
    if isinstance(a,list):
        if len(a)!=len(b): return [{"path":path,"v1_len":len(a),"v2_len":len(b)}]
        out=[]
        for i,(x,y) in enumerate(zip(a,b)): out += _diff(x,y,f"{path}[{i}]")
        return out
    return [] if a==b else [{"path":path,"v1":a,"v2":b}]


def reconcile() -> dict:
    _verify_frozen_identity()
    if not SUMMARY.is_file(): raise CorrectionStop("aggregate required before reconcile")
    records=[]; mismatch_total=0; compared=0; exact=0
    for l in LEARNERS:
        for e in ENVS:
            for s in SEEDS:
                v1p=ART_V1/"full"/f"{l}-{e}-S{s}"/"paired_evidence.json"; v2p=ART_V2/"full"/f"{l}-{e}-S{s}"/"paired_evidence_v3.json"
                v1=_read_json(v1p); v2=_read_json(v2p); projected=_project_to_v1(v1,v2); diffs=_diff({k:v for k,v in v1.items() if k!="provenance"},projected)
                count=len(json.dumps({k:v for k,v in v1.items() if k!="provenance"},sort_keys=True))
                compared+=count
                if not diffs: exact+=count
                mismatch_total+=len(diffs)
                records.append({"cell_id":f"{l}-{e}-S{s}","v1_path":_rel(v1p),"v1_sha256":_sha(v1p),"v3_path":_rel(v2p),"v3_sha256":_sha(v2p),"compared_field_encoding_bytes":count,"mismatch_count":len(diffs),"mismatches":diffs})
    v1s=_read_json(EXP_V1/"h3_summary.json"); v2s=_read_json(SUMMARY)
    for key in ("matrix_counts","learner_environment_summaries","comparisons","global_developer_candidate_h3"):
        diffs=_diff(v1s[key],v2s[key],f"$.summary.{key}"); mismatch_total+=len(diffs); records.append({"aggregate_field":key,"mismatch_count":len(diffs),"mismatches":diffs})
    result={"status":"EXACT_MATCH" if mismatch_total==0 else "REPLAY_MISMATCH_REQUIRES_QA","v1_summary_path":_rel(EXP_V1/"h3_summary.json"),"v1_summary_sha256":_sha(EXP_V1/"h3_summary.json"),"v3_summary_path":_rel(SUMMARY),"v3_summary_sha256":_sha(SUMMARY),"compared_field_encoding_bytes":compared,"exact_match_encoding_bytes":exact,"mismatch_count":mismatch_total,"records":records}
    _write_json(RECONCILIATION,result)
    _log("reconcile",command=COMMANDS["reconcile"],status=result["status"],mismatch_count=mismatch_total)
    if mismatch_total: raise CorrectionStop("REPLAY_MISMATCH_REQUIRES_QA")
    _write_report(result)
    return result


def _write_report(recon: dict) -> None:
    s=_read_json(SUMMARY); source=_read_json(SOURCE_MANIFEST); runtime=_read_json(RUNTIME_MANIFEST)
    vals={}
    for e in ENVS:
        c=_load_v3_cell("L0",e,42); vals[e]=c["nuisance_values"] if c else []
    lines=["# H3 Closure Report v3 — EXP-H3-001 correction retry","",f"Status: `READY_FOR_QA_REVIEW`  ","Authority: `DEVELOPER_CANDIDATE_ONLY`",f"Global developer candidate: `{s['global_developer_candidate_h3']}`","","## Exact intervention coverage","","The selected nuisance target is fixed per environment. ENV-1 and ENV-4 numeric intervention triplets are seed-dependent under the frozen target-selection algorithm, so the table enumerates the exact three values for every frozen environment/seed combination.","", "| Environment | Seed | Selected target | Exact three frozen values | Eligibility |","| --- | ---: | --- | --- | --- |"]
    for e in ENVS:
        for seed in SEEDS:
            cell = _load_v3_cell("L0", e, seed)
            values = cell["nuisance_values"] if cell else []
            lines.append(f"| {e} | {seed} | `{TARGETS[e]}` | `{values}` | {'inapplicable: do(N) changes Y/task labels' if e=='ENV-3' else 'task-preserving eligible'} |")
    lines += ["","Learner fidelity: L0=`faithful`; L1=`adapted`; L2=`adapted`; L3=`surrogate`; L4=`adapted`.","", "The dependency diagnostic is an **adapted sensitivity/leakage proxy**, not a canonical classifier of `N | I` and not a direct estimator of `predictive_information(N | I)`.","", "Raw latent mean shift / derived invariance is retained exactly as frozen but is `SCALE_SENSITIVE_DIAGNOSTIC_ONLY`. It is not an independent cross-learner success criterion. ENV-1 mean raw-invariance delta is negative for L1-L4 relative to L0; the aggregate positive delta is not scale-controlled.","", "`DEGENERATE` is only an indicative pattern: higher aggregate raw diagnostic coincides with utility loss. It does not establish causation or mechanism-level invariance.","", "## Candidate comparisons","","| Learner | task degradation W/L/T | leakage W/L/T | utility W/L/T | mean Δ task | mean Δ leak | mean Δ utility | Candidate |","| --- | --- | --- | --- | ---: | ---: | ---: | --- |"]
    for c in s["comparisons"]:
        lines.append(f"| {c['learner']} | {c['task_degradation_wlt']['wins']}/{c['task_degradation_wlt']['losses']}/{c['task_degradation_wlt']['ties']} | {c['leakage_wlt']['wins']}/{c['leakage_wlt']['losses']}/{c['leakage_wlt']['ties']} | {c['utility_wlt']['wins']}/{c['utility_wlt']['losses']}/{c['utility_wlt']['ties']} | {c['mean_delta_task_degradation']:.6f} | {c['mean_delta_leak_n']:.6f} | {c['mean_delta_predictive_utility']:.6f} | `{c['developer_candidate_h3']}` |")
    lines += ["",f"Matrix: `{s['matrix_counts']}`. v1/v3 reconciliation: `{recon['status']}`, mismatches=`{recon['mismatch_count']}`.","", "## Per-seed evidence","", "| Learner | Env | Seed | Status | Target | |Delta_N| | Leak_N | Utility |","| --- | --- | ---: | --- | --- | ---: | ---: | ---: |"]
    for r in s["per_seed_evidence"]:
        fmt=lambda x:"null" if x is None else f"{x:.6f}"
        lines.append(f"| {r['learner']} | {r['environment']} | {r['seed']} | {r['status']} | {r['nuisance_target']} | {fmt(r['mean_abs_delta_n'])} | {fmt(r['leak_n'])} | {fmt(r['factual_predictive_utility'])} |")
    lines += ["","## Frozen provenance", "", f"v1 preservation SHA256: `{_sha(PRESERVATION)}`  ",f"source manifest SHA256: `{_sha(SOURCE_MANIFEST)}`  ",f"runtime manifest SHA256: `{_sha(RUNTIME_MANIFEST)}`  ",f"v3 execution manifest SHA256: `{_sha(EXEC_MANIFEST)}`  ",f"M3 protocol SHA256: `{EXPECTED_M3_SHA}`  ",f"EXP-LRN-001 SHA256: `{EXPECTED_REFERENCE_SHA}`","", "Commands:", "```text", *COMMANDS.values(), "```", "", f"Runtime: `{runtime['python_version']}`; NumPy `{runtime['dependencies']['numpy']}`; SciPy `{runtime['dependencies']['scipy']}`; scikit-learn `{runtime['dependencies']['scikit_learn']}`; PyYAML `{runtime['dependencies']['pyyaml']}`.","", "## Claim boundary","", s["claim_boundary"],"", "No claim extends to untested nuisance targets, canonical external implementations, external environment families, MindForge, H4, or nuisance robustness in general."]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("command",choices=["freeze","smoke","run","aggregate","reconcile","verify-v1-after"]); args=parser.parse_args()
    actions={"freeze":freeze,"smoke":smoke,"run":run_matrix,"aggregate":aggregate,"reconcile":reconcile,"verify-v1-after":verify_v1_after}
    print(json.dumps(actions[args.command](),indent=2,ensure_ascii=False,default=_json_scalar)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
