"""H1 compression / complexity-utility closure runner."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pickle
import subprocess
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
import yaml

from environments import EnvironmentRegistry
from pipeline.run_learner_benchmark import ENVIRONMENTS, LEARNERS, PROTOCOL, SEEDS
from pipeline.run_m3_experiment import (
    EncoderWrapper,
    TableEncoder,
    _apply_overrides,
    _classification_scores,
    _dependency_versions,
    _first_ood_split,
    _git_provenance,
    _metadata_table,
    _split_table,
    create_extractor,
    validate_shift_assertion,
)


ROOT = Path(__file__).parent.parent
EXPERIMENT_ROOT = ROOT / "experiments/OIR_PPV/H1_Closure/EXP-H1-001"
DEFAULT_ARTIFACT_ROOT = ROOT / "artifacts/h1_closure/EXP-H1-001"
REFERENCE_MANIFEST = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json"
REFERENCE_ARTIFACT_ROOT = ROOT / "artifacts/learner_benchmark/EXP-LRN-001"
FREEZE_PATH = EXPERIMENT_ROOT / "h1_protocol_freeze.json"
FREEZE_HASH_PATH = EXPERIMENT_ROOT / "h1_protocol_freeze.sha256"
MANIFEST_PATH = EXPERIMENT_ROOT / "matrix_manifest.json"
MANIFEST_HASH_PATH = EXPERIMENT_ROOT / "matrix_manifest.sha256"
CONDITIONS = ["RAW", "MEM", "L0", "L1", "L2", "L3", "L4"]
EPSILON = 0.02
CORRECTION_ROOT = DEFAULT_ARTIFACT_ROOT / "correction_v2"
COMPARISON_V2_PATH = EXPERIMENT_ROOT / "h1_comparison_v2.json"
REPORT_V2_PATH = EXPERIMENT_ROOT / "H1_CLOSURE_REPORT_v2.md"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return _sha256_bytes(payload.encode("utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _reference_identity() -> dict:
    manifest = _read_json(REFERENCE_MANIFEST)
    return {
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": _sha256_bytes(REFERENCE_MANIFEST.read_bytes()),
        "historical_source": manifest.get("source"),
        "artifact_root": str(REFERENCE_ARTIFACT_ROOT),
    }


def freeze_protocol() -> dict:
    if FREEZE_PATH.exists() or FREEZE_HASH_PATH.exists():
        raise FileExistsError("H1 protocol freeze already exists; refusing rewrite")
    protocol_path = ROOT / PROTOCOL["path"]
    freeze = {
        "experiment_id": "EXP-H1-001",
        "hypothesis_id": "H1",
        "status": "frozen_before_final_execution",
        "frozen_at": datetime.now().isoformat(),
        "base_protocol": {
            **PROTOCOL,
            "sha256": _sha256_bytes(protocol_path.read_bytes()),
        },
        "reference_benchmark": _reference_identity(),
        "source": {
            "branch": _git("branch", "--show-current"),
            "head": _git("rev-parse", "HEAD"),
            "dirty": bool(_git("status", "--porcelain")),
        },
        "environments": [item["environment_id"] for item in ENVIRONMENTS],
        "seeds": list(SEEDS),
        "conditions": list(CONDITIONS),
        "utility_metric": {
            item["environment_id"]: "seen_environment_score / classification accuracy"
            for item in ENVIRONMENTS
        },
        "ood_utility_metric": {
            item["environment_id"]: (
                "unseen_environment_score when frozen OOD split is non-empty; otherwise null"
            )
            for item in ENVIRONMENTS
        },
        "primary_complexity_formula": "C_total = model_bytes + retained_state_bytes",
        "byte_counting_rules": {
            "common_downstream_predictor": (
                "excluded from every condition as common task-head overhead"
            ),
            "RAW": "model_bytes=0; retained_state_bytes=0",
            "MEM": (
                "model_bytes=0; retained_state_bytes=pickle protocol 5 bytes of "
                "sorted exact lookup state plus fallback label"
            ),
            "L0-L4": (
                "model_bytes=pickle protocol 5 bytes of fitted EncoderWrapper "
                "required for representation inference; retained_state_bytes=0"
            ),
            "serialized_artifact_bytes": (
                "same canonical inference-state serialization; excludes reports/logs/temp artifacts"
            ),
            "mutual_exclusion": "model_bytes and retained_state_bytes never overlap",
        },
        "utility_noninferiority_tolerance": {
            "type": "absolute",
            "epsilon": EPSILON,
            "scale": "classification accuracy in [0,1]",
            "rule": "Delta_U >= -epsilon against MEM",
            "justification": (
                "Task default; all current downstream utility metrics are normalized accuracy."
            ),
        },
        "failed_run_handling": (
            "retain failed attempt; no seed replacement, tuning, or silent retry"
        ),
        "matrix": {
            "condition_count": 7,
            "environment_count": 4,
            "seed_count": 5,
            "nominal_cells": 140,
        },
        "mem_semantics": {
            "lookup_key": "float64 raw-observation row bytes from training split",
            "value": "majority training label per duplicate key; deterministic tie break",
            "fallback": "global majority training label; deterministic tie break",
            "test_labels_available_to_mem": False,
        },
        "config_hashes": {
            "learners": _json_hash(LEARNERS),
            "environments": _json_hash(ENVIRONMENTS),
            "seeds": _json_hash(SEEDS),
            "conditions": _json_hash(CONDITIONS),
        },
    }
    _write_json(FREEZE_PATH, freeze)
    FREEZE_HASH_PATH.write_text(
        _sha256_bytes(FREEZE_PATH.read_bytes()) + "\n", encoding="utf-8"
    )
    return freeze


def _load_freeze() -> dict:
    if not FREEZE_PATH.is_file() or not FREEZE_HASH_PATH.is_file():
        raise RuntimeError("H1 protocol freeze/hash missing; execution refused")
    expected = FREEZE_HASH_PATH.read_text(encoding="utf-8").strip()
    actual = _sha256_bytes(FREEZE_PATH.read_bytes())
    freeze = _read_json(FREEZE_PATH)
    if expected != actual or freeze.get("status") != "frozen_before_final_execution":
        raise RuntimeError("H1 protocol freeze identity mismatch")
    if freeze.get("conditions") != CONDITIONS or freeze.get("seeds") != list(SEEDS):
        raise RuntimeError("H1 protocol freeze condition/seed mismatch")
    return freeze


def _condition_spec(condition: str) -> dict:
    if condition == "RAW":
        return {"condition": "RAW", "kind": "raw", "display_name": "Raw control"}
    if condition == "MEM":
        return {
            "condition": "MEM",
            "kind": "memorization",
            "display_name": "Exact memorization control",
        }
    matches = [item for item in LEARNERS if item["learner_id"] == condition]
    if len(matches) != 1:
        raise ValueError(f"Unknown condition ID: {condition}")
    return {"condition": condition, "kind": "learner", **matches[0]}


def _environment_spec(environment_id: str) -> dict:
    matches = [item for item in ENVIRONMENTS if item["environment_id"] == environment_id]
    if len(matches) != 1:
        raise ValueError(f"Unknown environment ID: {environment_id}")
    return matches[0]


def _majority(values: np.ndarray) -> Any:
    counts = Counter(np.asarray(values).tolist())
    top = max(counts.values())
    return sorted(
        (value for value, count in counts.items() if count == top), key=str
    )[0]


class MemorizationControl:
    def __init__(self) -> None:
        self.lookup: dict[bytes, Any] = {}
        self.fallback: Any = None
        self.entry_count = 0

    @staticmethod
    def _key(row: np.ndarray) -> bytes:
        return np.ascontiguousarray(np.asarray(row, dtype=np.float64)).tobytes()

    def fit(self, observations: np.ndarray, labels: np.ndarray) -> None:
        buckets: dict[bytes, list[Any]] = defaultdict(list)
        for row, label in zip(observations, labels):
            value = label.item() if hasattr(label, "item") else label
            buckets[self._key(row)].append(value)
        self.lookup = {
            key: _majority(np.asarray(values))
            for key, values in sorted(buckets.items(), key=lambda item: item[0])
        }
        self.fallback = _majority(np.asarray(labels))
        self.entry_count = len(self.lookup)

    def predict(self, observations: np.ndarray) -> tuple[np.ndarray, int, int]:
        if self.fallback is None:
            raise RuntimeError("MEM control not fitted")
        predictions = []
        hits = 0
        for row in observations:
            key = self._key(row)
            if key in self.lookup:
                hits += 1
                predictions.append(self.lookup[key])
            else:
                predictions.append(self.fallback)
        return np.asarray(predictions), hits, len(predictions) - hits

    def canonical_bytes(self) -> bytes:
        state = {
            "entries": [(key, self.lookup[key]) for key in sorted(self.lookup)],
            "fallback": self.fallback,
        }
        return pickle.dumps(state, protocol=5)


def _effective_rank(values: np.ndarray) -> Optional[int]:
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or not len(values) or values.shape[1] == 0:
        return None
    singular = np.linalg.svd(values, compute_uv=False)
    if not len(singular) or singular[0] == 0:
        return 0
    return int(np.sum(singular > singular[0] * 0.01))


def _count_parameters(obj: Any) -> int:
    seen: set[int] = set()

    def walk(value: Any) -> int:
        if value is None or id(value) in seen:
            return 0
        seen.add(id(value))
        try:
            import torch

            if isinstance(value, torch.nn.Module):
                return int(sum(parameter.numel() for parameter in value.parameters()))
        except Exception:
            pass
        if isinstance(value, np.ndarray):
            return int(value.size)
        if isinstance(value, (str, bytes, int, float, bool, Path)):
            return 0
        if isinstance(value, dict):
            return sum(walk(key) + walk(item) for key, item in value.items())
        if isinstance(value, (list, tuple, set)):
            return sum(walk(item) for item in value)
        if hasattr(value, "__dict__"):
            return sum(walk(item) for item in vars(value).values())
        return 0

    return walk(obj)


def _torch_module_payload(module: Any) -> list[dict]:
    import torch

    modules = list(module.children()) if hasattr(module, "children") else []
    if not modules:
        modules = [module]
    payload = []
    for layer in modules:
        if isinstance(layer, torch.nn.Linear):
            payload.append(
                {
                    "type": "Linear",
                    "weight": layer.weight.detach().cpu().numpy().copy(),
                    "bias": (
                        layer.bias.detach().cpu().numpy().copy()
                        if layer.bias is not None
                        else None
                    ),
                }
            )
        elif isinstance(layer, torch.nn.ReLU):
            payload.append({"type": "ReLU"})
        elif isinstance(layer, torch.nn.Tanh):
            payload.append({"type": "Tanh"})
        else:
            raise TypeError(f"Unsupported canonical torch layer: {type(layer).__name__}")
    return payload


def _torch_module_from_payload(payload: list[dict]):
    import torch

    layers = []
    for spec in payload:
        kind = spec["type"]
        if kind == "Linear":
            weight = np.asarray(spec["weight"], dtype=np.float32)
            bias = spec["bias"]
            layer = torch.nn.Linear(weight.shape[1], weight.shape[0], bias=bias is not None)
            with torch.no_grad():
                layer.weight.copy_(torch.from_numpy(weight))
                if bias is not None:
                    layer.bias.copy_(torch.from_numpy(np.asarray(bias, dtype=np.float32)))
            layers.append(layer)
        elif kind == "ReLU":
            layers.append(torch.nn.ReLU())
        elif kind == "Tanh":
            layers.append(torch.nn.Tanh())
        else:
            raise ValueError(f"Unknown canonical torch layer type: {kind}")
    return torch.nn.Sequential(*layers)


def _canonical_inference_payload(extractor: Any) -> dict:
    """Return deterministic fitted state needed for the frozen representation path X -> I."""
    if not isinstance(extractor, EncoderWrapper):
        raise TypeError(f"Unsupported inference-state wrapper: {type(extractor).__name__}")
    encoder = extractor.encoder
    name = type(encoder).__name__
    table_state = {
        "columns": copy.deepcopy(extractor.table_encoder._columns),
        "fitted": bool(extractor.table_encoder._fitted),
    }
    if name == "PCAEncoder":
        state = {
            "kind": "pca",
            "components": np.asarray(encoder.pca.components_).copy(),
            "mean": np.asarray(encoder.pca.mean_).copy(),
        }
        included = ["table_encoder", "pca.components_", "pca.mean_"]
        excluded = ["rng", "seed", "output_dim", "fit_metadata", "PCA training diagnostics"]
    elif name in {"MLPEncoderTrainable", "IRMStyleEncoderSurrogate", "DANNSurrogateEncoder"}:
        state = {
            "kind": "torch_encoder",
            "mean": np.asarray(encoder._mean).copy(),
            "std": np.asarray(encoder._std).copy(),
            "encoder": _torch_module_payload(encoder.encoder),
        }
        included = ["table_encoder", "_mean", "_std", "encoder"]
        excluded = {
            "MLPEncoderTrainable": ["classifier", "learning_rate", "epochs", "seed", "hidden_dims"],
            "IRMStyleEncoderSurrogate": ["classifier", "learning_rate", "epochs", "seed", "irm_penalty_weight", "hidden_dim"],
            "DANNSurrogateEncoder": ["task_head", "domain_head", "learning_rate", "epochs", "seed", "domain_penalty_weight", "hidden_dim"],
        }[name]
    elif name == "VAEEncoder":
        state = {
            "kind": "vae_posterior_mean",
            "mean": np.asarray(encoder._mean).copy(),
            "std": np.asarray(encoder._std).copy(),
            "encoder_body": _torch_module_payload(encoder.encoder_body),
            "mu_head": _torch_module_payload(encoder.mu_head),
        }
        included = ["table_encoder", "_mean", "_std", "encoder_body", "mu_head"]
        excluded = ["decoder", "logvar_head", "learning_rate", "epochs", "seed", "beta", "hidden_dim"]
    else:
        raise ValueError(f"Unknown canonical inference-state learner: {name}")
    return {
        "format": "oir-ppv-h1-canonical-inference-state-v2",
        "learner_class": name,
        "table_encoder": table_state,
        "state": state,
        "included_components": included,
        "excluded_training_only_components": excluded,
    }


def _canonical_inference_bytes(extractor: Any) -> bytes:
    return pickle.dumps(_canonical_inference_payload(extractor), protocol=5)


def _replay_canonical_inference(state: bytes, observations: np.ndarray) -> np.ndarray:
    import torch

    payload = pickle.loads(state)
    table = TableEncoder()
    table._columns = copy.deepcopy(payload["table_encoder"]["columns"])
    table._fitted = bool(payload["table_encoder"]["fitted"])
    numeric = table.transform(observations)
    fitted = payload["state"]
    if fitted["kind"] == "pca":
        return (numeric - fitted["mean"]) @ fitted["components"].T
    normalized = (
        np.asarray(numeric, dtype=np.float32) - np.asarray(fitted["mean"], dtype=np.float32)
    ) / np.asarray(fitted["std"], dtype=np.float32)
    tensor = torch.from_numpy(normalized.astype(np.float32))
    with torch.no_grad():
        if fitted["kind"] == "torch_encoder":
            return _torch_module_from_payload(fitted["encoder"])(tensor).cpu().numpy()
        if fitted["kind"] == "vae_posterior_mean":
            hidden = _torch_module_from_payload(fitted["encoder_body"])(tensor)
            return _torch_module_from_payload(fitted["mu_head"])(hidden).cpu().numpy()
    raise ValueError(f"Unknown canonical inference payload kind: {fitted['kind']}")


def _prepare_dataset(environment: dict, seed: int, cell_dir: Path):
    base = yaml.safe_load((ROOT / environment["config_path"]).read_text(encoding="utf-8"))
    effective = _apply_overrides(base, environment["overrides"])
    effective_path = cell_dir / "effective_env_config.yaml"
    effective_path.write_text(yaml.safe_dump(effective, sort_keys=False), encoding="utf-8")
    env = EnvironmentRegistry.create_from_config_path(effective_path, seed)
    data = env.generate()
    assertion = validate_shift_assertion(data, environment["assertion"])
    if assertion.get("passed") is not True:
        raise RuntimeError(f"Frozen shift assertion failed: {assertion}")
    train = np.asarray(data.splits["train"], dtype=int)
    test = np.asarray(data.splits["test"], dtype=int)
    ood_name, ood = _first_ood_split(
        data.splits, environment["assertion"].get("ood_split")
    )
    return data, train, test, ood_name, ood, assertion


def _encode_raw(data: Any, train: np.ndarray, test: np.ndarray, ood: np.ndarray):
    encoder = TableEncoder()
    train_i = encoder.fit_transform(data.observations[train])
    test_i = encoder.transform(data.observations[test])
    ood_i = encoder.transform(data.observations[ood]) if len(ood) else None
    return train_i, test_i, ood_i


def _learner_representation(
    condition: str,
    data: Any,
    train: np.ndarray,
    test: np.ndarray,
    ood: np.ndarray,
    seed: int,
):
    spec = _condition_spec(condition)
    config = {"type": spec["type"], **spec["params"], "seed": seed}
    extractor = create_extractor(config, seed)
    context_raw = _metadata_table(
        data.metadata, "Z", "context_variables", len(data.labels)
    )
    context_encoder = TableEncoder()
    train_context = context_encoder.fit_transform(_split_table(context_raw, train))
    test_context = context_encoder.transform(_split_table(context_raw, test))
    ood_context = (
        context_encoder.transform(_split_table(context_raw, ood)) if len(ood) else None
    )
    started = time.process_time()
    train_result = extractor.extract(data.observations[train], train_context, data.labels[train])
    train_cpu = time.process_time() - started
    started = time.process_time()
    test_result = extractor.extract(data.observations[test], test_context, None)
    ood_i = (
        extractor.extract(data.observations[ood], ood_context, None).invariant_representation
        if len(ood)
        else None
    )
    inference_cpu = time.process_time() - started
    return (
        train_result.invariant_representation,
        test_result.invariant_representation,
        ood_i,
        extractor,
        train_cpu,
        inference_cpu,
        _canonical_inference_bytes(extractor),
    )


def _mem_scores(
    mem: MemorizationControl,
    train_x: np.ndarray,
    train_y: np.ndarray,
    test_x: np.ndarray,
    test_y: np.ndarray,
    ood_x: Optional[np.ndarray],
    ood_y: Optional[np.ndarray],
) -> tuple[dict, dict]:
    train_pred, train_hits, train_misses = mem.predict(train_x)
    test_pred, test_hits, test_misses = mem.predict(test_x)
    train_score = float(np.mean(train_pred == train_y))
    seen_score = float(np.mean(test_pred == test_y))
    metrics = {
        "train_environment_score": train_score,
        "seen_environment_score": seen_score,
        "unseen_environment_score": None,
        "generalization_delta": None,
        "generalization_delta_direction": "unseen_minus_train",
        "task_metrics": {
            "task_type": "classification",
            "accuracy": seen_score,
            "auroc": None,
            "auroc_missing_reason": "MEM emits hard labels only",
            "r2": None,
            "r2_missing_reason": "classification task",
        },
    }
    hits = {
        "train_hits": train_hits,
        "train_misses": train_misses,
        "test_hits": test_hits,
        "test_misses": test_misses,
        "ood_hits": 0,
        "ood_misses": 0,
    }
    if ood_x is not None and ood_y is not None and len(ood_x):
        ood_pred, ood_hits, ood_misses = mem.predict(ood_x)
        unseen = float(np.mean(ood_pred == ood_y))
        metrics["unseen_environment_score"] = unseen
        metrics["generalization_delta"] = unseen - train_score
        metrics["task_metrics"].update(
            {
                "unseen_accuracy": unseen,
                "unseen_auroc": None,
                "unseen_auroc_missing_reason": "MEM emits hard labels only",
            }
        )
        hits["ood_hits"], hits["ood_misses"] = ood_hits, ood_misses
    else:
        metrics["missing_reason"] = "no non-empty OOD split"
    return metrics, hits


def execute_cell(
    condition: str,
    environment_id: str,
    seed: int,
    output_root: Path,
    attempt: int = 1,
) -> dict:
    _load_freeze()
    spec = _condition_spec(condition)
    environment = _environment_spec(environment_id)
    cell_id = f"{condition}-{environment_id}-S{seed}"
    cell_dir = output_root / "full" / cell_id
    if attempt != 1:
        cell_dir = cell_dir / f"attempt_{attempt}"
    if cell_dir.exists():
        raise FileExistsError(f"Refusing to overwrite H1 evidence: {cell_dir}")
    cell_dir.mkdir(parents=True, exist_ok=False)
    command = (
        f"python -m pipeline.run_h1_closure cell --condition {condition} "
        f"--environment {environment_id} --seed {seed}"
    )
    config = {
        "condition": spec,
        "environment": environment,
        "seed": seed,
        "attempt": attempt,
    }
    _write_json(cell_dir / "condition_config.json", config)
    try:
        data, train, test, ood_name, ood, assertion = _prepare_dataset(
            environment, seed, cell_dir
        )
        train_y, test_y = data.labels[train], data.labels[test]
        ood_y = data.labels[ood] if len(ood) else None
        input_dimension = int(np.asarray(data.observations).shape[1])
        measurement = {
            "common_task_head": (
                "LogisticRegression(max_iter=1000, random_state=seed), excluded from C_total"
            )
        }
        train_cpu = inference_cpu = 0.0
        retained_bytes = model_bytes = serialized_bytes = 0
        retained_per_sample = 0.0
        mem_stats = None

        if condition == "RAW":
            started = time.process_time()
            train_i, test_i, ood_i = _encode_raw(data, train, test, ood)
            inference_cpu = time.process_time() - started
            scores = _classification_scores(
                train_i, train_y, test_i, test_y, ood_i, ood_y, seed
            )
            representation_dimension = int(train_i.shape[1])
            rank = _effective_rank(train_i)
            parameter_count = 0
            measurement["state"] = "no learned representation state"
        elif condition == "MEM":
            train_i, test_i, ood_i = _encode_raw(data, train, test, ood)
            mem = MemorizationControl()
            started = time.process_time()
            mem.fit(train_i, train_y)
            train_cpu = time.process_time() - started
            started = time.process_time()
            scores, mem_stats = _mem_scores(
                mem, train_i, train_y, test_i, test_y, ood_i, ood_y
            )
            inference_cpu = time.process_time() - started
            state = mem.canonical_bytes()
            retained_bytes = serialized_bytes = len(state)
            retained_per_sample = retained_bytes / max(1, len(train))
            representation_dimension = rank = None
            parameter_count = 0
            measurement["state"] = "pickle protocol 5 sorted lookup plus fallback"
            measurement["mem_entry_count"] = mem.entry_count
        else:
            (
                train_i,
                test_i,
                ood_i,
                extractor,
                train_cpu,
                inference_cpu,
                state,
            ) = _learner_representation(condition, data, train, test, ood, seed)
            scores = _classification_scores(
                train_i, train_y, test_i, test_y, ood_i, ood_y, seed
            )
            model_bytes = serialized_bytes = len(state)
            representation_dimension = int(train_i.shape[1])
            rank = _effective_rank(train_i)
            parameter_count = _count_parameters(extractor)
            measurement["state"] = "pickle protocol 5 fitted EncoderWrapper"
            measurement["runtime_class"] = type(extractor).__name__
            measurement["wrapped_runtime_class"] = (
                type(extractor.encoder).__name__
                if isinstance(extractor, EncoderWrapper)
                else type(extractor).__name__
            )

        c_total = int(model_bytes + retained_bytes)
        complexity = {
            "experiment_id": "EXP-H1-001",
            "cell_id": cell_id,
            "condition": condition,
            "environment": environment_id,
            "seed": seed,
            "input_dimension": input_dimension,
            "representation_dimension": representation_dimension,
            "effective_rank": rank,
            "trainable_parameter_count": parameter_count,
            "model_bytes": int(model_bytes),
            "retained_state_bytes": int(retained_bytes),
            "retained_state_bytes_per_training_sample": float(retained_per_sample),
            "c_total_bytes": c_total,
            "serialized_artifact_bytes": int(serialized_bytes),
            "train_cpu_seconds": float(train_cpu),
            "inference_cpu_seconds": float(inference_cpu),
            "peak_process_memory_bytes": None,
            "measurement_method": measurement,
            "limitations": [
                "peak process memory not measured reliably on this Windows run"
            ],
        }
        results = {
            "experiment_id": "EXP-H1-001",
            "cell_id": cell_id,
            "status": "complete",
            "condition": condition,
            "environment": environment_id,
            "seed": seed,
            "utility": scores,
            "mem_stats": mem_stats,
            "shift_assertion": assertion,
            "ood_split": ood_name,
            "train_count": int(len(train)),
            "test_count": int(len(test)),
            "ood_count": int(len(ood)),
        }
        provenance = {
            "experiment_id": "EXP-H1-001",
            "cell_id": cell_id,
            "timestamp": datetime.now().isoformat(),
            "git": _git_provenance(),
            "reference_benchmark": _reference_identity(),
            "command": command,
            "dependencies": _dependency_versions(),
            "config_hash": _json_hash(config),
            "protocol_freeze_hash": FREEZE_HASH_PATH.read_text(
                encoding="utf-8"
            ).strip(),
            "matrix_manifest_hash": (
                MANIFEST_HASH_PATH.read_text(encoding="utf-8").strip()
                if MANIFEST_HASH_PATH.is_file()
                else None
            ),
            "runtime_class_identity": measurement.get(
                "wrapped_runtime_class", condition
            ),
            "seed": seed,
            "artifact_path": str(cell_dir),
            "attempt": attempt,
        }
        _write_json(cell_dir / "results.json", results)
        _write_json(cell_dir / "complexity.json", complexity)
        _write_json(cell_dir / "provenance.json", provenance)
        return {
            "cell_id": cell_id,
            "status": "complete",
            "c_total_bytes": c_total,
            "utility": scores["seen_environment_score"],
        }
    except Exception as exc:
        failure = {
            "experiment_id": "EXP-H1-001",
            "cell_id": cell_id,
            "status": "failed",
            "attempt": attempt,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }
        _write_json(cell_dir / "failure.json", failure)
        return failure


def _scientific_projection(cell_dir: Path) -> dict:
    complexity = _read_json(cell_dir / "complexity.json")
    for key in ("train_cpu_seconds", "inference_cpu_seconds"):
        complexity.pop(key, None)
    return {
        "results": _read_json(cell_dir / "results.json"),
        "complexity": complexity,
    }


def run_smoke(artifact_root: Path) -> dict:
    _load_freeze()
    smoke_root = artifact_root / "smoke"
    records = []
    for repeat in ("run_a", "run_b"):
        for condition in CONDITIONS:
            result = execute_cell(
                condition, "ENV-1", 42, smoke_root / repeat
            )
            records.append({"repeat": repeat, **result})
    comparisons = []
    for condition in CONDITIONS:
        cell = f"{condition}-ENV-1-S42"
        left = smoke_root / "run_a" / "full" / cell
        right = smoke_root / "run_b" / "full" / cell
        passed = (
            (left / "results.json").is_file()
            and (right / "results.json").is_file()
            and _scientific_projection(left) == _scientific_projection(right)
        )
        comparisons.append({"condition": condition, "cell_id": cell, "passed": passed})
    report = {
        "phase": "smoke",
        "seed": 42,
        "expected_runs": 14,
        "complete_runs": sum(item["status"] == "complete" for item in records),
        "all_reproducible": all(item["passed"] for item in comparisons),
        "records": records,
        "comparisons": comparisons,
    }
    _write_json(smoke_root / "smoke_report.json", report)
    return report


def freeze_manifest(artifact_root: Path) -> dict:
    freeze = _load_freeze()
    smoke_path = artifact_root / "smoke/smoke_report.json"
    if not smoke_path.is_file():
        raise RuntimeError("Smoke report missing")
    smoke = _read_json(smoke_path)
    if (
        smoke["complete_runs"] != smoke["expected_runs"]
        or not smoke["all_reproducible"]
    ):
        raise RuntimeError("Smoke/reproducibility gate failed; matrix not frozen")
    if MANIFEST_PATH.exists() or MANIFEST_HASH_PATH.exists():
        raise FileExistsError("H1 matrix manifest already exists; refusing rewrite")
    cells = [
        {
            "cell_id": f"{condition}-{environment['environment_id']}-S{seed}",
            "condition": condition,
            "environment": environment["environment_id"],
            "seed": seed,
            "status": "planned",
        }
        for condition in CONDITIONS
        for environment in ENVIRONMENTS
        for seed in SEEDS
    ]
    manifest = {
        "experiment_id": "EXP-H1-001",
        "status": "frozen",
        "frozen_at": datetime.now().isoformat(),
        "protocol_freeze_sha256": _sha256_bytes(FREEZE_PATH.read_bytes()),
        "reference_manifest_sha256": _sha256_bytes(REFERENCE_MANIFEST.read_bytes()),
        "conditions": CONDITIONS,
        "environments": [item["environment_id"] for item in ENVIRONMENTS],
        "seeds": SEEDS,
        "expected_cells": len(cells),
        "cells": cells,
        "applicability": (
            "all 140 cells applicable for seen classification utility; OOD may be null"
        ),
        "failed_run_policy": freeze["failed_run_handling"],
        "smoke_evidence": str(smoke_path),
    }
    _write_json(MANIFEST_PATH, manifest)
    MANIFEST_HASH_PATH.write_text(
        _sha256_bytes(MANIFEST_PATH.read_bytes()) + "\n", encoding="utf-8"
    )
    return manifest


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file() or not MANIFEST_HASH_PATH.is_file():
        raise RuntimeError("Frozen H1 matrix manifest/hash missing")
    expected = MANIFEST_HASH_PATH.read_text(encoding="utf-8").strip()
    actual = _sha256_bytes(MANIFEST_PATH.read_bytes())
    manifest = _read_json(MANIFEST_PATH)
    if (
        expected != actual
        or manifest.get("status") != "frozen"
        or manifest.get("expected_cells") != 140
    ):
        raise RuntimeError("H1 matrix manifest identity mismatch")
    return manifest


def run_full(artifact_root: Path) -> dict:
    manifest = _load_manifest()
    records = [
        execute_cell(
            cell["condition"], cell["environment"], int(cell["seed"]), artifact_root
        )
        for cell in manifest["cells"]
    ]
    summary = {
        "experiment_id": "EXP-H1-001",
        "expected_cells": 140,
        "complete_cells": sum(item["status"] == "complete" for item in records),
        "failed_cells": sum(item["status"] == "failed" for item in records),
        "records": records,
    }
    _write_json(artifact_root / "full_run_summary.json", summary)
    return summary


def aggregate(artifact_root: Path) -> dict:
    manifest = _load_manifest()
    rows = []
    failures = []
    for cell in manifest["cells"]:
        cell_dir = artifact_root / "full" / cell["cell_id"]
        if not (cell_dir / "results.json").is_file():
            failures.append(
                {
                    "cell_id": cell["cell_id"],
                    "reason": (
                        _read_json(cell_dir / "failure.json")
                        if (cell_dir / "failure.json").is_file()
                        else "missing evidence"
                    ),
                }
            )
            continue
        result = _read_json(cell_dir / "results.json")
        complexity = _read_json(cell_dir / "complexity.json")
        rows.append(
            {
                "cell_id": cell["cell_id"],
                "condition": cell["condition"],
                "environment": cell["environment"],
                "seed": cell["seed"],
                "utility": result["utility"]["seen_environment_score"],
                "ood_utility": result["utility"].get("unseen_environment_score"),
                "c_total_bytes": complexity["c_total_bytes"],
                "model_bytes": complexity["model_bytes"],
                "retained_state_bytes": complexity["retained_state_bytes"],
                "representation_dimension": complexity["representation_dimension"],
                "effective_rank": complexity["effective_rank"],
            }
        )
    index = {
        (row["environment"], row["seed"], row["condition"]): row for row in rows
    }
    comparisons = []
    for condition in CONDITIONS:
        if condition == "MEM":
            continue
        pairs = []
        for environment in [item["environment_id"] for item in ENVIRONMENTS]:
            for seed in SEEDS:
                current = index.get((environment, seed, condition))
                mem = index.get((environment, seed, "MEM"))
                raw = index.get((environment, seed, "RAW"))
                if not current or not mem:
                    continue
                delta_u = current["utility"] - mem["utility"]
                pairs.append(
                    {
                        "environment": environment,
                        "seed": seed,
                        "c_total_delta_vs_mem": (
                            current["c_total_bytes"] - mem["c_total_bytes"]
                        ),
                        "c_total_ratio_vs_mem": (
                            current["c_total_bytes"] / mem["c_total_bytes"]
                            if mem["c_total_bytes"]
                            else None
                        ),
                        "compression_ratio_mem_over_condition": (
                            mem["c_total_bytes"] / current["c_total_bytes"]
                            if current["c_total_bytes"]
                            else None
                        ),
                        "utility_delta_vs_mem": delta_u,
                        "utility_noninferior_vs_mem": delta_u >= -EPSILON,
                        "utility_delta_vs_raw": (
                            current["utility"] - raw["utility"] if raw else None
                        ),
                    }
                )
        successful = [
            pair
            for pair in pairs
            if pair["c_total_delta_vs_mem"] < 0
            and pair["utility_noninferior_vs_mem"]
        ]
        comparisons.append(
            {
                "condition": condition,
                "pair_count": len(pairs),
                "supported_pair_count": len(successful),
                "all_pairs_meet_h1": bool(pairs) and len(successful) == len(pairs),
                "mean_c_total_delta_vs_mem": (
                    float(np.mean([p["c_total_delta_vs_mem"] for p in pairs]))
                    if pairs
                    else None
                ),
                "median_c_total_delta_vs_mem": (
                    float(np.median([p["c_total_delta_vs_mem"] for p in pairs]))
                    if pairs
                    else None
                ),
                "mean_utility_delta_vs_mem": (
                    float(np.mean([p["utility_delta_vs_mem"] for p in pairs]))
                    if pairs
                    else None
                ),
                "min_utility_delta_vs_mem": (
                    float(np.min([p["utility_delta_vs_mem"] for p in pairs]))
                    if pairs
                    else None
                ),
                "max_utility_delta_vs_mem": (
                    float(np.max([p["utility_delta_vs_mem"] for p in pairs]))
                    if pairs
                    else None
                ),
                "pairs": pairs,
            }
        )
    learners = [
        item for item in comparisons if item["condition"] in {"L0", "L1", "L2", "L3", "L4"}
    ]
    candidate = (
        "SUPPORTED"
        if any(item["all_pairs_meet_h1"] for item in learners) and not failures
        else ("INCONCLUSIVE" if failures else "NOT_SUPPORTED")
    )
    output = {
        "experiment_id": "EXP-H1-001",
        "protocol_freeze_sha256": _sha256_bytes(FREEZE_PATH.read_bytes()),
        "matrix_manifest_sha256": _sha256_bytes(MANIFEST_PATH.read_bytes()),
        "complete_cells": len(rows),
        "failed_cells": len(failures),
        "inapplicable_cells": 0,
        "epsilon": EPSILON,
        "rows": rows,
        "comparisons": comparisons,
        "failures": failures,
        "developer_candidate_h1": candidate,
    }
    _write_json(EXPERIMENT_ROOT / "h1_comparison.json", output)
    lines = [
        "# H1 Closure Report",
        "",
        f"Developer candidate: `{candidate}` (PM/QA owns final classification).",
        "",
        f"Completed cells: {len(rows)}/140; failed: {len(failures)}; epsilon: {EPSILON}.",
        "",
        "| Condition | Pairs | H1 pairs | All pairs | Mean C delta vs MEM | Mean utility delta vs MEM |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for item in comparisons:
        lines.append(
            f"| {item['condition']} | {item['pair_count']} | "
            f"{item['supported_pair_count']} | {item['all_pairs_meet_h1']} | "
            f"{item['mean_c_total_delta_vs_mem']} | {item['mean_utility_delta_vs_mem']} |"
        )
    lines += [
        "",
        "## Frozen interpretation",
        "",
        "A learner supports H1 only if every tested paired environment/seed cell has lower C_total than MEM and utility is non-inferior within epsilon=0.02.",
        "",
        "## Limitations",
        "",
        "- Common downstream LogisticRegression task-head storage is excluded from all conditions.",
        "- Pickle protocol 5 is the canonical inference-state serialization for this reference/control layer.",
        "- Peak process memory is not used because reliable per-cell Windows measurement was unavailable.",
        "- MindForge is intentionally excluded from DEV_TASK_009.",
    ]
    (EXPERIMENT_ROOT / "H1_CLOSURE_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return output



def _stat_summary(values: list[float]) -> dict:
    finite = [float(value) for value in values if value is not None]
    if not finite:
        return {"mean": None, "median": None, "min": None, "max": None}
    return {
        "mean": float(np.mean(finite)),
        "median": float(np.median(finite)),
        "min": float(np.min(finite)),
        "max": float(np.max(finite)),
    }


def _wlt(values: list[float], tolerance: float = 1e-12) -> dict:
    return {
        "wins": sum(value < -tolerance for value in values),
        "losses": sum(value > tolerance for value in values),
        "ties": sum(abs(value) <= tolerance for value in values),
    }


def _utility_wlt(values: list[float], tolerance: float = 1e-12) -> dict:
    return {
        "wins": sum(value > tolerance for value in values),
        "losses": sum(value < -tolerance for value in values),
        "ties": sum(abs(value) <= tolerance for value in values),
    }


def _hash_original_h1_evidence() -> dict:
    manifest = _load_manifest()
    artifact_hashes = {}
    required = ("results.json", "complexity.json", "provenance.json", "condition_config.json")
    for cell in manifest["cells"]:
        cell_id = cell["cell_id"]
        cell_dir = DEFAULT_ARTIFACT_ROOT / "full" / cell_id
        files = {}
        for name in required:
            path = cell_dir / name
            if not path.is_file():
                raise RuntimeError(f"Original H1 evidence missing: {path}")
            files[name] = _sha256_bytes(path.read_bytes())
        artifact_hashes[cell_id] = files
    if len(artifact_hashes) != 140:
        raise RuntimeError(f"Expected 140 original H1 cells, found {len(artifact_hashes)}")
    return {
        "experiment_id": "EXP-H1-001",
        "captured_at": datetime.now().isoformat(),
        "protocol_sha256": _sha256_bytes(FREEZE_PATH.read_bytes()),
        "matrix_sha256": _sha256_bytes(MANIFEST_PATH.read_bytes()),
        "original_comparison_sha256": _sha256_bytes((EXPERIMENT_ROOT / "h1_comparison.json").read_bytes()),
        "original_report_sha256": _sha256_bytes((EXPERIMENT_ROOT / "H1_CLOSURE_REPORT.md").read_bytes()),
        "cell_count": len(artifact_hashes),
        "required_files_per_cell": list(required),
        "artifacts": artifact_hashes,
    }


def correct_accounting() -> dict:
    freeze = _load_freeze()
    manifest = _load_manifest()
    if CORRECTION_ROOT.exists():
        raise FileExistsError(f"Refusing to overwrite correction evidence: {CORRECTION_ROOT}")
    CORRECTION_ROOT.mkdir(parents=True, exist_ok=False)
    original_manifest = _hash_original_h1_evidence()
    _write_json(CORRECTION_ROOT / "original_evidence_manifest.json", original_manifest)
    records = []
    for cell in manifest["cells"]:
        condition = cell["condition"]
        if condition not in {"L0", "L1", "L2", "L3", "L4"}:
            continue
        environment_id = cell["environment"]
        seed = int(cell["seed"])
        cell_id = cell["cell_id"]
        work_dir = CORRECTION_ROOT / "work" / cell_id
        work_dir.mkdir(parents=True, exist_ok=False)
        environment = _environment_spec(environment_id)
        data, train, test, _, ood, _ = _prepare_dataset(environment, seed, work_dir)
        train_i, test_i, ood_i, extractor, _, _, state = _learner_representation(
            condition, data, train, test, ood, seed
        )
        state_repeat = _canonical_inference_bytes(extractor)
        if state != state_repeat:
            raise RuntimeError(f"Non-deterministic canonical serialization: {cell_id}")
        replay_test = _replay_canonical_inference(state, data.observations[test])
        replay_max_abs_error = (
            float(np.max(np.abs(test_i - replay_test))) if test_i.size else 0.0
        )
        if not np.allclose(test_i, replay_test, rtol=0.0, atol=1e-12):
            raise RuntimeError(
                f"Canonical state cannot replay representation within 1e-12: {cell_id}; "
                f"max_abs_error={replay_max_abs_error}"
            )
        train_y, test_y = data.labels[train], data.labels[test]
        ood_y = data.labels[ood] if len(ood) else None
        reconstructed_scores = _classification_scores(
            train_i, train_y, test_i, test_y, ood_i, ood_y, seed
        )
        original_result_path = DEFAULT_ARTIFACT_ROOT / "full" / cell_id / "results.json"
        original_complexity_path = DEFAULT_ARTIFACT_ROOT / "full" / cell_id / "complexity.json"
        original_result = _read_json(original_result_path)
        original_complexity = _read_json(original_complexity_path)
        original_seen = original_result["utility"]["seen_environment_score"]
        if abs(float(reconstructed_scores["seen_environment_score"]) - float(original_seen)) > 1e-12:
            raise RuntimeError(f"Deterministic reconstruction changed utility: {cell_id}")
        payload = _canonical_inference_payload(extractor)
        corrected = dict(original_complexity)
        corrected.update(
            {
                "correction_version": "v2",
                "original_model_bytes": original_complexity["model_bytes"],
                "model_bytes": len(state),
                "c_total_bytes": len(state) + int(original_complexity["retained_state_bytes"]),
                "serialized_artifact_bytes": len(state),
                "measurement_method": {
                    **original_complexity.get("measurement_method", {}),
                    "state": "pickle protocol 5 canonical X->I inference payload",
                    "canonical_format": payload["format"],
                    "included_components": payload["included_components"],
                    "excluded_training_only_components": payload["excluded_training_only_components"],
                    "derived_from_frozen_cell": cell_id,
                },
            }
        )
        out_dir = CORRECTION_ROOT / "cells" / cell_id
        out_dir.mkdir(parents=True, exist_ok=False)
        _write_json(out_dir / "complexity_v2.json", corrected)
        provenance = {
            "experiment_id": "EXP-H1-001",
            "correction": "DEV_TASK_009_FIX_01",
            "correction_version": "v2",
            "mode": "derived_accounting_deterministic_reconstruction",
            "cell_id": cell_id,
            "condition": condition,
            "environment": environment_id,
            "seed": seed,
            "git": {"branch": _git("branch", "--show-current"), "head": _git("rev-parse", "HEAD"), "dirty": bool(_git("status", "--porcelain"))},
            "protocol_sha256": original_manifest["protocol_sha256"],
            "matrix_sha256": original_manifest["matrix_sha256"],
            "reference_manifest_sha256": freeze["reference_benchmark"]["manifest_sha256"],
            "original_results_sha256": _sha256_bytes(original_result_path.read_bytes()),
            "original_complexity_sha256": _sha256_bytes(original_complexity_path.read_bytes()),
            "canonical_serialization": {
                "method": "pickle protocol 5 over minimal replayable X->I payload",
                "included_components": payload["included_components"],
                "excluded_training_only_components": payload["excluded_training_only_components"],
                "deterministic_repeat_equal": True,
                "representation_replay_atol": 1e-12,
                "representation_replay_max_abs_error": replay_max_abs_error,
                "reconstructed_utility_matches_original": True,
            },
            "dependencies": _dependency_versions(),
            "corrected_complexity_path": str(out_dir / "complexity_v2.json"),
        }
        _write_json(out_dir / "provenance_v2.json", provenance)
        records.append(
            {
                "cell_id": cell_id,
                "condition": condition,
                "environment": environment_id,
                "seed": seed,
                "original_model_bytes": int(original_complexity["model_bytes"]),
                "corrected_model_bytes": len(state),
                "corrected_c_total_bytes": corrected["c_total_bytes"],
                "utility_preserved": True,
                "complexity_path": str(out_dir / "complexity_v2.json"),
            }
        )
    summary = {
        "experiment_id": "EXP-H1-001",
        "correction": "DEV_TASK_009_FIX_01",
        "mode": "derived_accounting_deterministic_reconstruction",
        "original_cells_verified": original_manifest["cell_count"],
        "corrected_learner_cells": len(records),
        "failed_cells": 0,
        "inapplicable_cells": 0,
        "epsilon": EPSILON,
        "protocol_sha256": original_manifest["protocol_sha256"],
        "matrix_sha256": original_manifest["matrix_sha256"],
        "records": records,
    }
    _write_json(CORRECTION_ROOT / "correction_summary.json", summary)
    return summary


def _corrected_rows() -> tuple[list[dict], list[dict]]:
    manifest = _load_manifest()
    rows, failures = [], []
    for cell in manifest["cells"]:
        cell_id = cell["cell_id"]
        raw_dir = DEFAULT_ARTIFACT_ROOT / "full" / cell_id
        if not (raw_dir / "results.json").is_file():
            failures.append({"cell_id": cell_id, "reason": "missing original results"})
            continue
        result = _read_json(raw_dir / "results.json")
        if cell["condition"] in {"L0", "L1", "L2", "L3", "L4"}:
            complexity_path = CORRECTION_ROOT / "cells" / cell_id / "complexity_v2.json"
        else:
            complexity_path = raw_dir / "complexity.json"
        if not complexity_path.is_file():
            failures.append({"cell_id": cell_id, "reason": f"missing complexity: {complexity_path}"})
            continue
        complexity = _read_json(complexity_path)
        rows.append(
            {
                "cell_id": cell_id,
                "condition": cell["condition"],
                "environment": cell["environment"],
                "seed": cell["seed"],
                "utility": result["utility"]["seen_environment_score"],
                "c_total_bytes": complexity["c_total_bytes"],
                "model_bytes": complexity["model_bytes"],
                "retained_state_bytes": complexity["retained_state_bytes"],
                "complexity_source": str(complexity_path),
            }
        )
    return rows, failures


def _group_summary(pairs: list[dict], prefix: str) -> dict:
    utility_key = f"utility_delta_vs_{prefix}"
    result = {
        "pair_count": len(pairs),
        "utility_wins_losses_ties": _utility_wlt([p[utility_key] for p in pairs]),
        "utility_delta": _stat_summary([p[utility_key] for p in pairs]),
        "utility_noninferior_count": sum(bool(p[f"utility_noninferior_vs_{prefix}"]) for p in pairs),
        "utility_noninferior_rate": (sum(bool(p[f"utility_noninferior_vs_{prefix}"]) for p in pairs) / len(pairs)) if pairs else None,
    }
    if prefix == "mem":
        result.update(
            {
                "c_total_wins_losses_ties": _wlt([p["c_total_delta_vs_mem"] for p in pairs]),
                "combined_h1_wins_losses_ties": {
                    "wins": sum(bool(p["meets_h1_vs_mem"]) for p in pairs),
                    "losses": sum(not bool(p["meets_h1_vs_mem"]) for p in pairs),
                    "ties": 0,
                    "semantics": "win=paired H1 criterion satisfied; loss=criterion not satisfied",
                },
                "c_total_delta": _stat_summary([p["c_total_delta_vs_mem"] for p in pairs]),
                "c_total_ratio": _stat_summary([p["c_total_ratio_vs_mem"] for p in pairs]),
                "compression_ratio_mem_over_learner": _stat_summary([p["compression_ratio_mem_over_learner"] for p in pairs]),
                "h1_success_count": sum(bool(p["meets_h1_vs_mem"]) for p in pairs),
                "h1_success_rate": (sum(bool(p["meets_h1_vs_mem"]) for p in pairs) / len(pairs)) if pairs else None,
            }
        )
    return result


def aggregate_v2() -> dict:
    _load_freeze()
    rows, failures = _corrected_rows()
    index = {(row["environment"], row["seed"], row["condition"]): row for row in rows}
    comparisons = []
    for condition in ("L0", "L1", "L2", "L3", "L4"):
        pairs = []
        for environment in [item["environment_id"] for item in ENVIRONMENTS]:
            for seed in SEEDS:
                learner = index.get((environment, seed, condition))
                mem = index.get((environment, seed, "MEM"))
                raw = index.get((environment, seed, "RAW"))
                if not learner or not mem or not raw:
                    continue
                du_mem = float(learner["utility"] - mem["utility"])
                du_raw = float(learner["utility"] - raw["utility"])
                c_delta_mem = int(learner["c_total_bytes"] - mem["c_total_bytes"])
                c_delta_raw = int(learner["c_total_bytes"] - raw["c_total_bytes"])
                pairs.append(
                    {
                        "environment": environment,
                        "seed": int(seed),
                        "learner_cell_id": learner["cell_id"],
                        "mem_cell_id": mem["cell_id"],
                        "raw_cell_id": raw["cell_id"],
                        "learner_c_total_bytes": learner["c_total_bytes"],
                        "mem_c_total_bytes": mem["c_total_bytes"],
                        "raw_c_total_bytes": raw["c_total_bytes"],
                        "c_total_delta_vs_mem": c_delta_mem,
                        "c_total_ratio_vs_mem": learner["c_total_bytes"] / mem["c_total_bytes"] if mem["c_total_bytes"] else None,
                        "compression_ratio_mem_over_learner": mem["c_total_bytes"] / learner["c_total_bytes"] if learner["c_total_bytes"] else None,
                        "utility_delta_vs_mem": du_mem,
                        "utility_noninferior_vs_mem": du_mem >= -EPSILON,
                        "meets_h1_vs_mem": c_delta_mem < 0 and du_mem >= -EPSILON,
                        "c_total_delta_vs_raw": c_delta_raw,
                        "c_total_ratio_vs_raw": None,
                        "c_total_ratio_vs_raw_reason": "RAW C_total is frozen at 0; learner/RAW ratio divides by zero",
                        "compression_ratio_vs_raw": None,
                        "compression_ratio_vs_raw_reason": "RAW has no retained inference state; storage compression ratio is not meaningful",
                        "utility_delta_vs_raw": du_raw,
                        "utility_noninferior_vs_raw": du_raw >= -EPSILON,
                    }
                )
        per_environment = {}
        for environment in [item["environment_id"] for item in ENVIRONMENTS]:
            env_pairs = [p for p in pairs if p["environment"] == environment]
            per_environment[environment] = {
                "vs_mem": _group_summary(env_pairs, "mem"),
                "vs_raw": _group_summary(env_pairs, "raw"),
            }
        comparisons.append(
            {
                "condition": condition,
                "vs_mem": _group_summary(pairs, "mem"),
                "vs_raw": {
                    **_group_summary(pairs, "raw"),
                    "c_total_delta": _stat_summary([p["c_total_delta_vs_raw"] for p in pairs]),
                    "c_total_ratio": {"mean": None, "median": None, "min": None, "max": None, "reason": "RAW C_total=0 causes division by zero"},
                    "compression_ratio": {"mean": None, "median": None, "min": None, "max": None, "reason": "RAW retained-state baseline is zero; compression ratio is not meaningful"},
                },
                "per_environment": per_environment,
                "pairs": pairs,
                "failed_or_inapplicable_cells": [],
            }
        )
    candidate = "SUPPORTED" if any(c["vs_mem"]["h1_success_count"] == c["vs_mem"]["pair_count"] and c["vs_mem"]["pair_count"] for c in comparisons) and not failures else ("INCONCLUSIVE" if failures else "NOT_SUPPORTED")
    limitations = [
        {"id": "MEM_ZERO_TEST_HITS", "detail": "MEM exact-row lookup has 0 test hits across all 20 MEM environment/seed cells; test utility uses the frozen global-majority fallback."},
        {"id": "RAW_ZERO_C_TOTAL", "detail": "RAW C_total=0 because raw input storage and the common downstream task head are excluded by the frozen accounting."},
        {"id": "MEM_COMPARATOR_SCOPE", "detail": "H1 evidence supports claims only relative to the frozen exact-row MEM comparator under ENV-1..ENV-4 and the five frozen seeds."},
        {"id": "NO_RAW_SUPERIORITY", "detail": "The evidence does not establish learned-representation superiority to RAW; negative RAW utility deltas are retained."},
        {"id": "FIDELITY_LABELS", "detail": "L3 remains IRM-style surrogate and L4 remains adapted DANN exactly as frozen in EXP-LRN-001."},
    ]
    output = {
        "experiment_id": "EXP-H1-001",
        "correction": "DEV_TASK_009_FIX_01",
        "version": "v2",
        "developer_candidate_h1": candidate,
        "candidate_authority": "DEVELOPER_CANDIDATE_ONLY",
        "epsilon": EPSILON,
        "protocol_freeze_sha256": _sha256_bytes(FREEZE_PATH.read_bytes()),
        "matrix_manifest_sha256": _sha256_bytes(MANIFEST_PATH.read_bytes()),
        "complete_cells": len(rows),
        "failed_cells": len(failures),
        "inapplicable_cells": 0,
        "comparisons": comparisons,
        "failures": failures,
        "limitations": limitations,
        "corrected_complexity_root": str(CORRECTION_ROOT / "cells"),
        "original_scientific_results_root": str(DEFAULT_ARTIFACT_ROOT / "full"),
    }
    _write_json(COMPARISON_V2_PATH, output)
    lines = [
        "# H1 Closure Report v2 - DEV_TASK_009_FIX_01",
        "",
        f"Developer candidate only: `{candidate}`. PM/QA owns final H1 acceptance.",
        "",
        f"Frozen epsilon: `{EPSILON}`. Original scientific matrix retained: {len(rows)}/140 cells; failures: {len(failures)}.",
        "",
        "Corrected complexity uses deterministic, replayable canonical `X -> I` inference state. Utility is read unchanged from the original 140-cell evidence.",
        "",
        "## Learner comparisons vs MEM",
        "",
        "| Learner | Pairs | H1 wins/losses/ties | C_total W/L/T | Utility W/L/T | H1 rate | C delta mean/median/min/max | Utility delta mean/median/min/max |",
        "|---|---:|---|---|---|---:|---|---|",
    ]
    for item in comparisons:
        mem = item["vs_mem"]
        h1w = mem["combined_h1_wins_losses_ties"]
        cw = mem["c_total_wins_losses_ties"]
        uw = mem["utility_wins_losses_ties"]
        cd, ud = mem["c_total_delta"], mem["utility_delta"]
        lines.append(f"| {item['condition']} | {mem['pair_count']} | {h1w['wins']}/{h1w['losses']}/{h1w['ties']} | {cw['wins']}/{cw['losses']}/{cw['ties']} | {uw['wins']}/{uw['losses']}/{uw['ties']} | {mem['h1_success_rate']:.3f} | {cd['mean']:.3f}/{cd['median']:.3f}/{cd['min']:.3f}/{cd['max']:.3f} | {ud['mean']:.6f}/{ud['median']:.6f}/{ud['min']:.6f}/{ud['max']:.6f} |")
    lines += [
        "",
        "## Learner comparisons vs RAW",
        "",
        "| Learner | Pairs | Utility W/L/T | Non-inferior | Utility delta mean/median/min/max | C_total delta mean/median/min/max | Ratio handling |",
        "|---|---:|---|---:|---|---|---|",
    ]
    for item in comparisons:
        raw = item["vs_raw"]
        uw, ud, cd = raw["utility_wins_losses_ties"], raw["utility_delta"], raw["c_total_delta"]
        lines.append(f"| {item['condition']} | {raw['pair_count']} | {uw['wins']}/{uw['losses']}/{uw['ties']} | {raw['utility_noninferior_count']}/{raw['pair_count']} | {ud['mean']:.6f}/{ud['median']:.6f}/{ud['min']:.6f}/{ud['max']:.6f} | {cd['mean']:.3f}/{cd['median']:.3f}/{cd['min']:.3f}/{cd['max']:.3f} | null: RAW C_total=0 |")
    lines += ["", "## Per-environment evidence", ""]
    for item in comparisons:
        lines.append(f"### {item['condition']}")
        lines.append("")
        lines.append("| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |")
        lines.append("|---|---:|---:|---:|---|")
        for environment, summary in item["per_environment"].items():
            mem, raw = summary["vs_mem"], summary["vs_raw"]
            ud = raw["utility_delta"]
            lines.append(f"| {environment} | {mem['h1_success_count']}/{mem['pair_count']} | {mem['utility_noninferior_count']}/{mem['pair_count']} | {raw['utility_noninferior_count']}/{raw['pair_count']} | {ud['mean']:.6f}/{ud['min']:.6f}/{ud['max']:.6f} |")
        lines.append("")
    lines += ["## Limitations", ""]
    lines.extend(f"- **{item['id']}**: {item['detail']}" for item in limitations)
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "The candidate H1 result is relative only to the frozen exact-row MEM comparator. RAW remains a control and materially constrains interpretation. This report does not claim learned-representation superiority to RAW.",
    ]
    REPORT_V2_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output

def main() -> int:
    parser = argparse.ArgumentParser(description="OIR-PPV H1 closure runner")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("freeze-protocol", "smoke", "freeze-matrix", "full", "aggregate", "correct-accounting", "aggregate-v2"):
        sub.add_parser(name)
    cell = sub.add_parser("cell")
    cell.add_argument("--condition", required=True)
    cell.add_argument("--environment", required=True)
    cell.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    EXPERIMENT_ROOT.mkdir(parents=True, exist_ok=True)
    if args.command == "freeze-protocol":
        result = freeze_protocol()
    elif args.command == "smoke":
        result = run_smoke(DEFAULT_ARTIFACT_ROOT)
    elif args.command == "freeze-matrix":
        result = freeze_manifest(DEFAULT_ARTIFACT_ROOT)
    elif args.command == "full":
        result = run_full(DEFAULT_ARTIFACT_ROOT)
    elif args.command == "aggregate":
        result = aggregate(DEFAULT_ARTIFACT_ROOT)
    elif args.command == "correct-accounting":
        result = correct_accounting()
    elif args.command == "aggregate-v2":
        result = aggregate_v2()
    else:
        if args.condition not in CONDITIONS:
            raise ValueError(f"Unknown condition ID: {args.condition}")
        if args.environment not in [item["environment_id"] for item in ENVIRONMENTS]:
            raise ValueError(f"Unknown environment ID: {args.environment}")
        result = execute_cell(
            args.condition, args.environment, args.seed, DEFAULT_ARTIFACT_ROOT
        )
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
