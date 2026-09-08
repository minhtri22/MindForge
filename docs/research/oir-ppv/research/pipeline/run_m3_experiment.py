"""Execute an OIR-PPV pipeline experiment with auditable M4 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import numpy as np
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent))

from environments import EnvironmentRegistry
from pipeline import (
    OIRInvariantExtractor,
    OIRManifestationGenerator,
    PipelineEvaluator,
    PipelineRunner,
    PlaceholderInvariantExtractor,
    PlaceholderManifestationGenerator,
)
from pipeline.causal_validation import run_causal_validation_experiment
from pipeline.dependency_analysis import run_dependency_analysis
from pipeline.generator import GenerationResult
from pipeline.invariant_extractor import InvariantExtractionResult
from pipeline.learners import LearnerRegistry, create_learner_from_config
import pipeline.learners_extended  # noqa: F401 -- production registry side effects


RESEARCH_ROOT = Path(__file__).parent.parent
PROTOCOL_NAME = "M3_PROTOCOL"
PROTOCOL_VERSION = "M3-Protocol-v1.0"
PROTOCOL_PATH = Path("benchmark/M3_PROTOCOL.md")
SOURCE_SNAPSHOT_PATHS = ("benchmark", "environments", "pipeline")


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_json(value: Any) -> str:
    return _hash_bytes(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    )


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


class TableEncoder:
    """Fit-on-train numeric conversion for mixed numeric/categorical tables."""

    def __init__(self) -> None:
        self._columns: list[tuple[str, Any]] = []
        self._fitted = False

    @staticmethod
    def _as_2d(values: np.ndarray) -> np.ndarray:
        values = np.asarray(values)
        return values.reshape(-1, 1) if values.ndim == 1 else values

    def fit(self, values: np.ndarray) -> "TableEncoder":
        values = self._as_2d(values)
        self._columns = []
        for index in range(values.shape[1]):
            column = values[:, index]
            try:
                column.astype(float)
                self._columns.append(("numeric", None))
            except (TypeError, ValueError):
                categories = {
                    value: position
                    for position, value in enumerate(
                        sorted({str(v) for v in column})
                    )
                }
                self._columns.append(("categorical", categories))
        self._fitted = True
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("TableEncoder not fitted")
        values = self._as_2d(values)
        if values.shape[1] != len(self._columns):
            raise ValueError("Input column count differs from fitted table")
        output = np.zeros(values.shape, dtype=float)
        for index, (kind, metadata) in enumerate(self._columns):
            if kind == "numeric":
                output[:, index] = values[:, index].astype(float)
            else:
                output[:, index] = [
                    metadata.get(str(value), -1) for value in values[:, index]
                ]
        if not np.isfinite(output).all():
            raise ValueError("Non-finite value after table encoding")
        return output

    def fit_transform(self, values: np.ndarray) -> np.ndarray:
        return self.fit(values).transform(values)


class EncoderWrapper:
    """Adapt EncoderLearner to the InvariantExtractor contract."""

    def __init__(self, encoder: Any, requested_type: str):
        self.encoder = encoder
        self.requested_type = requested_type
        self.table_encoder = TableEncoder()
        self._fitted = False

    def extract(
        self,
        observations: np.ndarray,
        context: np.ndarray = None,
        labels: np.ndarray = None,
        metadata: Dict[str, Any] = None,
    ) -> InvariantExtractionResult:
        if not self._fitted:
            if labels is None:
                raise RuntimeError("EncoderWrapper not fitted")
            numeric = self.table_encoder.fit_transform(observations)
            self.fit_metadata = self.encoder.fit(numeric, context, labels, metadata)
            self._fitted = True
        else:
            numeric = self.table_encoder.transform(observations)
        invariant = self.encoder.encode(numeric)
        if not np.isfinite(invariant).all():
            raise ValueError("Encoder produced non-finite representation")
        return InvariantExtractionResult(
            invariant_representation=invariant,
            metadata={
                "method": type(self.encoder).__name__,
                "requested_type": self.requested_type,
                "runtime_wrapper": type(self).__name__,
                "fit": _json_ready(getattr(self, "fit_metadata", {})),
            },
            config_hash=self.get_config_hash(),
        )

    def get_config_hash(self) -> str:
        return self.encoder.get_config_hash()

    def get_invariant_dim(self) -> int:
        return self.encoder.get_output_dim()


class DecoderWrapper:
    """Adapt DecoderLearner to the ManifestationGenerator contract."""

    def __init__(self, decoder: Any, requested_type: str):
        self.decoder = decoder
        self.requested_type = requested_type
        self.fit_metadata: Dict[str, Any] = {}

    def fit(
        self,
        invariant: np.ndarray,
        context: np.ndarray,
        nuisance: np.ndarray,
        targets: np.ndarray,
    ) -> Dict[str, Any]:
        self.fit_metadata = self.decoder.fit(
            invariant, context, nuisance, targets
        )
        return self.fit_metadata

    def generate(
        self,
        invariant: np.ndarray,
        context: np.ndarray,
        nuisance: np.ndarray,
        metadata: Dict[str, Any] = None,
    ) -> GenerationResult:
        generated = self.decoder.decode(invariant, context, nuisance)
        if not np.isfinite(generated).all():
            raise ValueError("Decoder produced non-finite manifestation")
        return GenerationResult(
            generated_observations=generated,
            metadata={
                "method": type(self.decoder).__name__,
                "requested_type": self.requested_type,
                "runtime_wrapper": type(self).__name__,
                "fit": _json_ready(self.fit_metadata),
            },
            config_hash=self.get_config_hash(),
        )

    def get_config_hash(self) -> str:
        return self.decoder.get_config_hash()

    def get_output_dim(self) -> int:
        return self.decoder.output_dim


def create_extractor(config: dict, seed: int):
    extractor_type = config.get("type")
    if extractor_type == "PlaceholderInvariantExtractor":
        return PlaceholderInvariantExtractor(
            invariant_dim=config.get("invariant_dim", 64), seed=seed
        )
    if extractor_type == "OIRInvariantExtractor":
        return OIRInvariantExtractor(
            invariant_dim=config.get("invariant_dim", 64),
            encoder_hidden=config.get("encoder_hidden", [256, 128]),
            predictor_hidden=config.get("predictor_hidden", [64, 32]),
            invariant_weight=config.get("invariant_weight", 1.0),
            seed=seed,
        )
    if extractor_type in LearnerRegistry.list_encoders():
        params = {k: v for k, v in config.items() if k != "type"}
        encoder = create_learner_from_config(
            {"type": extractor_type, **params}, "encoder", seed
        )
        return EncoderWrapper(encoder, extractor_type)
    raise ValueError(
        f"Unknown extractor type: {extractor_type!r}. "
        f"Available: {LearnerRegistry.list_encoders()} plus explicit pipeline types"
    )


def create_generator(config: dict, seed: int):
    generator_type = config.get("type")
    if generator_type == "PlaceholderManifestationGenerator":
        return PlaceholderManifestationGenerator(
            output_dim=config.get("output_dim", 10), seed=seed
        )
    if generator_type == "OIRManifestationGenerator":
        return OIRManifestationGenerator(
            output_dim=config.get("output_dim", 10),
            invariant_dim=config.get("invariant_dim", 64),
            context_dim=config.get("context_dim", 5),
            nuisance_dim=config.get("nuisance_dim", 3),
            decoder_hidden=config.get("decoder_hidden", [256, 128, 256]),
            seed=seed,
        )
    if generator_type in LearnerRegistry.list_decoders():
        params = {k: v for k, v in config.items() if k != "type"}
        decoder = create_learner_from_config(
            {"type": generator_type, **params}, "decoder", seed
        )
        return DecoderWrapper(decoder, generator_type)
    raise ValueError(
        f"Unknown generator type: {generator_type!r}. "
        f"Available: {LearnerRegistry.list_decoders()} plus explicit pipeline types"
    )


def _apply_overrides(base_config: dict, overrides: dict) -> dict:
    import copy

    result = copy.deepcopy(base_config)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _apply_overrides(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _metadata_table(metadata: dict, flat: str, nested: str, length: int) -> np.ndarray:
    if flat in metadata:
        value = np.asarray(metadata[flat])
        return value.reshape(-1, 1) if value.ndim == 1 else value
    values = metadata.get(nested, {})
    if isinstance(values, dict) and values:
        columns = [np.asarray(values[name]).reshape(-1, 1) for name in sorted(values)]
        return np.hstack(columns)
    return np.zeros((length, 1))


def _split_table(values: np.ndarray, indices: np.ndarray) -> np.ndarray:
    return np.asarray(values)[np.asarray(indices, dtype=int)]


def _safe_correlation(x: np.ndarray, y: np.ndarray) -> Optional[float]:
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def _distribution(values: Iterable[Any]) -> Dict[str, float]:
    values = np.asarray(list(values)).astype(str)
    unique, counts = np.unique(values, return_counts=True)
    total = max(1, counts.sum())
    return {str(k): float(v / total) for k, v in zip(unique, counts)}


def _total_variation(left: Dict[str, float], right: Dict[str, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(left.get(k, 0.0) - right.get(k, 0.0)) for k in keys)


def _first_ood_split(splits: dict, preferred: str = None) -> tuple[str, np.ndarray]:
    if preferred and preferred in splits:
        return preferred, np.asarray(splits[preferred], dtype=int)
    for name in sorted(splits):
        if name.startswith("ood_") and len(splits[name]):
            return name, np.asarray(splits[name], dtype=int)
    return "ood", np.asarray(splits.get("ood", []), dtype=int)


def validate_shift_assertion(env_data: Any, assertion: dict) -> dict:
    kind = assertion.get("type")
    train = np.asarray(env_data.splits["train"], dtype=int)
    test = np.asarray(env_data.splits["test"], dtype=int)
    evidence: Dict[str, Any] = {"type": kind, "passed": False}

    if kind in {"nuisance_distribution", "shortcut_reversal"}:
        nuisance = env_data.metadata.get("nuisance_variables", {})
        feature = assertion.get("feature", env_data.metadata.get("shortcut_feature"))
        if feature not in nuisance:
            raise ValueError(f"Missing nuisance feature {feature!r}")
        values = np.asarray(nuisance[feature], dtype=float)
        train_corr = _safe_correlation(values[train], env_data.labels[train])
        test_corr = _safe_correlation(values[test], env_data.labels[test])
        evidence.update(
            {
                "feature": feature,
                "train_mean": float(np.mean(values[train])),
                "test_mean": float(np.mean(values[test])),
                "mean_shift": float(abs(np.mean(values[train]) - np.mean(values[test]))),
                "train_correlation": train_corr,
                "test_correlation": test_corr,
            }
        )
        if kind == "nuisance_distribution":
            evidence["passed"] = (
                evidence["mean_shift"] >= assertion.get("min_mean_shift", 0.5)
                and train_corr is not None
            )
        else:
            evidence["passed"] = (
                train_corr is not None
                and test_corr is not None
                and train_corr >= assertion.get("min_train_correlation", 0.3)
                and test_corr <= assertion.get("max_test_correlation", -0.3)
            )
    elif kind == "context_distribution":
        context = _metadata_table(
            env_data.metadata, "Z", "context_variables", len(env_data.labels)
        )[:, 0]
        split_name, shifted = _first_ood_split(
            env_data.splits, assertion.get("ood_split")
        )
        train_dist = _distribution(context[train])
        shifted_dist = _distribution(context[shifted])
        tv = _total_variation(train_dist, shifted_dist)
        evidence.update(
            {
                "shifted_split": split_name,
                "train_distribution": train_dist,
                "shifted_distribution": shifted_dist,
                "total_variation": tv,
                "passed": len(shifted) > 0
                and tv >= assertion.get("min_total_variation", 0.5),
            }
        )
    elif kind == "ood_holdout":
        split_name, ood = _first_ood_split(
            env_data.splits, assertion.get("ood_split")
        )
        overlap = np.intersect1d(train, ood)
        evidence.update(
            {
                "ood_split": split_name,
                "train_count": int(len(train)),
                "ood_count": int(len(ood)),
                "train_ood_overlap": int(len(overlap)),
                "passed": len(ood) > 0 and len(overlap) == 0,
            }
        )
    elif kind == "composition_holdout":
        factors = env_data.metadata.get("factor_values", {})
        if not isinstance(factors, dict) or not factors:
            raise ValueError("composition_holdout requires factor_values metadata")
        names = sorted(factors)
        train_combinations = {
            tuple(str(np.asarray(factors[name])[index]) for name in names)
            for index in train
        }
        test_combinations = {
            tuple(str(np.asarray(factors[name])[index]) for name in names)
            for index in test
        }
        overlap = train_combinations & test_combinations
        evidence.update(
            {
                "factor_names": names,
                "train_combination_count": len(train_combinations),
                "test_combination_count": len(test_combinations),
                "combination_overlap": len(overlap),
                "passed": bool(test_combinations) and not overlap,
            }
        )
    else:
        raise ValueError(f"Unknown stress assertion type: {kind!r}")

    if not evidence["passed"]:
        raise RuntimeError(f"Stress shift assertion failed: {evidence}")
    return _json_ready(evidence)


def _git_provenance() -> dict:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        )
        return completed.stdout.strip()

    try:
        return {
            "root": run("rev-parse", "--show-toplevel"),
            "branch": run("branch", "--show-current"),
            "head": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain")),
        }
    except (OSError, subprocess.CalledProcessError) as error:
        return {"available": False, "error": str(error)}


def _protocol_identity(config: dict) -> dict:
    declared = config.get("protocol")
    if not isinstance(declared, dict):
        raise ValueError("Missing required protocol identity")
    name = declared.get("name")
    version = declared.get("version")
    path = Path(declared.get("path", PROTOCOL_PATH))
    if name != PROTOCOL_NAME or version != PROTOCOL_VERSION:
        raise ValueError(
            f"Protocol identity mismatch: expected {PROTOCOL_NAME} {PROTOCOL_VERSION}, "
            f"got {name!r} {version!r}"
        )
    if path.as_posix() != PROTOCOL_PATH.as_posix():
        raise ValueError(
            f"Protocol path mismatch: expected {PROTOCOL_PATH}, got {path}"
        )
    protocol_path = RESEARCH_ROOT / path
    if not protocol_path.is_file():
        raise ValueError(f"Frozen protocol file missing: {protocol_path}")
    content = protocol_path.read_text(encoding="utf-8")
    if PROTOCOL_VERSION not in content:
        raise ValueError(
            f"Frozen protocol file does not declare {PROTOCOL_VERSION}"
        )
    return {
        "name": PROTOCOL_NAME,
        "version": PROTOCOL_VERSION,
        "path": path.as_posix(),
        "sha256": _hash_bytes(protocol_path.read_bytes()),
    }


def _source_snapshot_provenance() -> dict:
    digest = hashlib.sha256()
    files = []
    for relative_root in SOURCE_SNAPSHOT_PATHS:
        root = RESEARCH_ROOT / relative_root
        for path in sorted(root.rglob("*")):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or path.suffix in {".pyc", ".pyo"}
            ):
                continue
            relative = path.relative_to(RESEARCH_ROOT).as_posix()
            content = path.read_bytes()
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(content).digest())
            files.append(relative)

    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain", "--", *SOURCE_SNAPSHOT_PATHS],
            cwd=RESEARCH_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        status = [line for line in completed.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError) as error:
        status = [f"git_status_unavailable: {error}"]

    return {
        "paths": list(SOURCE_SNAPSHOT_PATHS),
        "file_count": len(files),
        "tree_sha256": digest.hexdigest(),
        "dirty": bool(status),
        "status": status,
    }


def _dependency_versions() -> dict:
    import scipy
    import sklearn
    import torch

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pyyaml": yaml.__version__,
        "scikit_learn": sklearn.__version__,
        "scipy": scipy.__version__,
        "torch": torch.__version__,
    }


def _classification_scores(
    train_i: np.ndarray,
    train_labels: np.ndarray,
    seen_i: np.ndarray,
    seen_labels: np.ndarray,
    ood_i: Optional[np.ndarray],
    ood_labels: Optional[np.ndarray],
    seed: int,
) -> dict:
    predictor = LogisticRegression(max_iter=1000, random_state=seed)
    predictor.fit(train_i, train_labels)
    train_score = float(predictor.score(train_i, train_labels))
    seen_score = float(predictor.score(seen_i, seen_labels))

    def auroc(features: np.ndarray, labels: np.ndarray) -> tuple[Optional[float], Optional[str]]:
        try:
            probabilities = predictor.predict_proba(features)
            if probabilities.shape[1] == 2:
                return float(roc_auc_score(labels, probabilities[:, 1])), None
            return float(
                roc_auc_score(
                    labels, probabilities, multi_class="ovr",
                    labels=predictor.classes_,
                )
            ), None
        except ValueError as error:
            return None, str(error)

    seen_auroc, seen_auroc_reason = auroc(seen_i, seen_labels)
    task_metrics = {
        "task_type": "classification",
        "accuracy": seen_score,
        "auroc": seen_auroc,
        "auroc_missing_reason": seen_auroc_reason,
        "r2": None,
        "r2_missing_reason": "classification task",
    }
    if ood_i is None or not len(ood_i):
        return {
            "train_environment_score": train_score,
            "seen_environment_score": seen_score,
            "unseen_environment_score": None,
            "generalization_delta": None,
            "generalization_delta_direction": "unseen_minus_train",
            "missing_reason": "no non-empty OOD split",
            "task_metrics": task_metrics,
        }
    unseen_score = float(predictor.score(ood_i, ood_labels))
    unseen_auroc, unseen_auroc_reason = auroc(ood_i, ood_labels)
    task_metrics["unseen_accuracy"] = unseen_score
    task_metrics["unseen_auroc"] = unseen_auroc
    task_metrics["unseen_auroc_missing_reason"] = unseen_auroc_reason
    return {
        "train_environment_score": train_score,
        "seen_environment_score": seen_score,
        "unseen_environment_score": unseen_score,
        "generalization_delta": unseen_score - train_score,
        "generalization_delta_direction": "unseen_minus_train",
        "task_metrics": task_metrics,
    }


def _array_manifest(path: Path) -> dict:
    with np.load(path) as archive:
        arrays = {
            name: {
                "shape": list(archive[name].shape),
                "dtype": str(archive[name].dtype),
            }
            for name in archive.files
        }
    return {
        "path": str(path),
        "sha256": _hash_bytes(path.read_bytes()),
        "arrays": arrays,
    }


def run_m3_experiment(
    config_path: Path,
    output_dir: Optional[Path] = None,
    command: Optional[str] = None,
) -> dict:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    protocol = _protocol_identity(config)
    exp_config = config["experiment"]
    env_config = config["environment"]
    pipe_config = config["pipeline"]
    eval_config = config["evaluation"]
    seed = int(env_config.get("seed", 42))

    base_dir = Path(output_dir or config["output"]["base_dir"])
    exp_output = base_dir / exp_config["id"]
    exp_output.mkdir(parents=True, exist_ok=True)

    base_env_config = yaml.safe_load(
        Path(env_config["config_path"]).read_text(encoding="utf-8")
    )
    overrides = env_config.get("overrides", {})
    effective_config = _apply_overrides(base_env_config, overrides)
    effective_path = exp_output / "effective_env_config.yaml"
    effective_path.write_text(
        yaml.safe_dump(effective_config, sort_keys=False), encoding="utf-8"
    )

    env = EnvironmentRegistry.create_from_config_path(effective_path, seed)
    env_data = env.generate()
    shift_evidence = validate_shift_assertion(
        env_data, config.get("stress_assertion", {})
    )
    (exp_output / "shift_assertions.json").write_text(
        json.dumps(shift_evidence, indent=2), encoding="utf-8"
    )

    train_idx = np.asarray(env_data.splits["train"], dtype=int)
    test_idx = np.asarray(env_data.splits["test"], dtype=int)
    ood_name, ood_idx = _first_ood_split(
        env_data.splits, config.get("stress_assertion", {}).get("ood_split")
    )

    context_raw = _metadata_table(
        env_data.metadata, "Z", "context_variables", len(env_data.labels)
    )
    nuisance_raw = _metadata_table(
        env_data.metadata, "N", "nuisance_variables", len(env_data.labels)
    )
    context_encoder = TableEncoder()
    nuisance_encoder = TableEncoder()
    train_context = context_encoder.fit_transform(_split_table(context_raw, train_idx))
    test_context = context_encoder.transform(_split_table(context_raw, test_idx))
    train_nuisance = nuisance_encoder.fit_transform(
        _split_table(nuisance_raw, train_idx)
    )
    test_nuisance = nuisance_encoder.transform(_split_table(nuisance_raw, test_idx))

    extractor = create_extractor(pipe_config["invariant_extractor"], seed)
    generator = create_generator(pipe_config["generator"], seed)
    expected_encoder = pipe_config["invariant_extractor"]["type"]
    expected_decoder = pipe_config["generator"]["type"]
    if isinstance(extractor, EncoderWrapper) and extractor.requested_type != expected_encoder:
        raise RuntimeError("Extractor runtime identity mismatch")
    if isinstance(generator, DecoderWrapper) and generator.requested_type != expected_decoder:
        raise RuntimeError("Generator runtime identity mismatch")

    train_obs = env_data.observations[train_idx]
    test_obs = env_data.observations[test_idx]
    train_labels = env_data.labels[train_idx]
    test_labels = env_data.labels[test_idx]
    train_result = extractor.extract(train_obs, train_context, train_labels)

    target_encoder = TableEncoder()
    train_targets = target_encoder.fit_transform(train_obs)
    test_targets = target_encoder.transform(test_obs)
    if not hasattr(generator, "fit"):
        raise RuntimeError("Configured generator does not expose fit()")
    generator_fit = generator.fit(
        train_result.invariant_representation,
        train_context,
        train_nuisance,
        train_targets,
    )

    runner = PipelineRunner(extractor, generator)
    test_result = runner.run(
        test_obs, test_context, test_nuisance, test_labels
    )
    evaluator = PipelineEvaluator(seed=seed)
    evaluation = evaluator.evaluate_pipeline(
        observations=test_targets,
        invariant_result=test_result["invariant_result"],
        generation_result=test_result["generation_result"],
        context=test_context,
        nuisance=test_nuisance,
        labels=test_labels,
        target_observations=test_targets,
        config_hash=extractor.get_config_hash(),
    )
    # The generic evaluator cannot recover the fitted extractor from the result
    # object. Re-encode generated numeric manifestations explicitly so invariant
    # preservation is measured instead of defaulting to zero.
    if isinstance(extractor, EncoderWrapper):
        generated_i = extractor.encoder.encode(
            test_result["generation_result"].generated_observations
        )
        evaluation.generation_metrics = evaluator.generation_evaluator.evaluate(
            test_result["generation_result"].generated_observations,
            test_targets,
            test_result["invariant_result"].invariant_representation,
            generated_i,
            test_context,
            extractor.get_config_hash(),
        )
        evaluation.overall_score = (
            0.3 * evaluation.invariant_metrics.invariance_score
            + 0.2 * evaluation.invariant_metrics.predictive_utility
            + 0.2 * evaluation.generation_metrics.invariant_preservation
            + 0.15 * evaluation.generation_metrics.context_response
            + 0.15 * evaluation.generation_metrics.distribution_similarity
        )

    ood_i = None
    ood_labels = None
    if len(ood_idx):
        ood_context = context_encoder.transform(_split_table(context_raw, ood_idx))
        ood_obs = env_data.observations[ood_idx]
        ood_i = extractor.extract(ood_obs, ood_context, None).invariant_representation
        ood_labels = env_data.labels[ood_idx]
    generalization = _classification_scores(
        train_result.invariant_representation,
        train_labels,
        test_result["invariant_result"].invariant_representation,
        test_labels,
        ood_i,
        ood_labels,
        seed,
    )
    generalization["ood_split"] = ood_name

    test_metadata: Dict[str, Any] = {}
    for key, value in env_data.metadata.items():
        if isinstance(value, dict):
            test_metadata[key] = {
                sub_key: (
                    np.asarray(sub_value)[test_idx]
                    if isinstance(sub_value, np.ndarray)
                    and len(sub_value) == len(env_data.observations)
                    else sub_value
                )
                for sub_key, sub_value in value.items()
            }
        elif isinstance(value, np.ndarray) and len(value) == len(env_data.observations):
            test_metadata[key] = value[test_idx]
        else:
            test_metadata[key] = value

    causal_result = run_causal_validation_experiment(
        extractor=extractor,
        environment=env,
        test_observations=test_obs,
        test_context=test_context,
        test_nuisance=test_nuisance,
        test_metadata=test_metadata,
        output_dir=exp_output,
        seed=seed,
    )
    dependency_result = run_dependency_analysis(
        invariant_representation=test_result[
            "invariant_result"
        ].invariant_representation,
        context=test_context,
        nuisance=test_nuisance,
        output_dir=exp_output,
        config_hash=extractor.get_config_hash(),
        seed=seed,
    )

    generated_path = exp_output / "generated.npz"
    np.savez_compressed(
        generated_path,
        generated=test_result["generation_result"].generated_observations,
        invariant=test_result["invariant_result"].invariant_representation,
    )
    array_manifest = _array_manifest(generated_path)

    evaluation_dict = _json_ready(evaluation.to_dict())
    evaluation_dict["generalization"] = _json_ready(generalization)
    (exp_output / "evaluation.json").write_text(
        json.dumps(evaluation_dict, indent=2), encoding="utf-8"
    )

    results = {
        "experiment_id": exp_config["id"],
        "protocol": protocol,
        "environment_family": env_config["family"],
        "shift_assertions": shift_evidence,
        "invariant_result": {
            "shape": list(
                test_result["invariant_result"].invariant_representation.shape
            ),
            "metadata": _json_ready(test_result["invariant_result"].metadata),
        },
        "generation_result": {
            "shape": list(
                test_result["generation_result"].generated_observations.shape
            ),
            "metadata": _json_ready(test_result["generation_result"].metadata),
        },
        "evaluation": evaluation_dict,
        "causal_validation": _json_ready(causal_result.to_dict()),
        "dependency_analysis": _json_ready(dependency_result.to_dict()),
        "arrays": array_manifest,
    }
    (exp_output / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    extractor_wrapped = getattr(extractor, "encoder", None)
    generator_wrapped = getattr(generator, "decoder", None)
    provenance = {
        "experiment_id": exp_config["id"],
        "protocol": protocol,
        "timestamp": datetime.now().isoformat(),
        "source_config": str(config_path),
        "command": command,
        "artifact_path": str(exp_output),
        "seed": seed,
        "environment": {
            "family": env_config["family"],
            "base_config": env_config["config_path"],
            "effective_config": str(effective_path),
            "effective_config_sha256": _hash_bytes(effective_path.read_bytes()),
            "overrides": _json_ready(overrides),
            "overrides_sha256": _hash_json(overrides),
        },
        "invariant_extractor": {
            "requested_type": expected_encoder,
            "runtime_wrapper_type": type(extractor).__name__,
            "wrapped_learner_type": (
                type(extractor_wrapped).__name__ if extractor_wrapped else None
            ),
            "config": _json_ready(pipe_config["invariant_extractor"]),
            "config_hash": extractor.get_config_hash(),
        },
        "generator": {
            "requested_type": expected_decoder,
            "runtime_wrapper_type": type(generator).__name__,
            "wrapped_learner_type": (
                type(generator_wrapped).__name__ if generator_wrapped else None
            ),
            "config": _json_ready(pipe_config["generator"]),
            "config_hash": generator.get_config_hash(),
            "fit": _json_ready(generator_fit),
        },
        "splits": {
            "train": int(len(train_idx)),
            "test": int(len(test_idx)),
            "ood_name": ood_name,
            "ood": int(len(ood_idx)),
        },
        "interventions": eval_config.get("intervention_targets", []),
        "git": _git_provenance(),
        "source_snapshot": _source_snapshot_provenance(),
        "dependencies": _dependency_versions(),
        "arrays": array_manifest,
    }
    (exp_output / "provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )

    print(f"Experiment {exp_config['id']} completed")
    print(f"Output: {exp_output}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    command = subprocess.list2cmdline([sys.executable, *sys.argv])
    run_m3_experiment(
        Path(args.config),
        Path(args.output) if args.output else None,
        command=command,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
