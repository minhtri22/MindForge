"""Causal intervention checks for invariant representations."""

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def _json_value(value: Any) -> Any:
    return value.item() if isinstance(value, np.generic) else value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class InterventionResult:
    intervention_target: str
    intervention_value: Any
    I_before: np.ndarray
    I_after: np.ndarray
    mean_shift: float
    correlation: float
    invariance_score: float
    config_hash: str
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        """Return a compact summary; arrays are stored in causal_arrays.npz."""
        return {
            "intervention_target": self.intervention_target,
            "intervention_value": _json_value(self.intervention_value),
            "I_before_shape": list(self.I_before.shape),
            "I_after_shape": list(self.I_after.shape),
            "mean_shift": float(self.mean_shift),
            "correlation": float(self.correlation),
            "invariance_score": float(self.invariance_score),
            "config_hash": self.config_hash,
            "seed": self.seed,
        }


@dataclass
class CausalValidationResult:
    extractor_type: str
    extractor_config_hash: str
    environment: str
    seed: int
    nuisance_interventions: List[InterventionResult]
    context_interventions: List[InterventionResult]
    avg_nuisance_invariance: float
    avg_context_invariance: float
    overall_invariance: float
    failure_cases: List[Dict[str, Any]]
    timestamp: str
    arrays: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "extractor_type": self.extractor_type,
            "extractor_config_hash": self.extractor_config_hash,
            "environment": self.environment,
            "seed": self.seed,
            "nuisance_interventions": [r.to_dict() for r in self.nuisance_interventions],
            "context_interventions": [r.to_dict() for r in self.context_interventions],
            "avg_nuisance_invariance": float(self.avg_nuisance_invariance),
            "avg_context_invariance": float(self.avg_context_invariance),
            "overall_invariance": float(self.overall_invariance),
            "failure_cases": self.failure_cases,
            "timestamp": self.timestamp,
            "arrays": self.arrays,
        }


FAILURE_THRESHOLD = 0.5


def _collect_failure_cases(
    nuisance_results: List[InterventionResult],
    context_results: List[InterventionResult],
) -> List[Dict[str, Any]]:
    """Apply the frozen M3 failure threshold to every intervention type."""
    failures: List[Dict[str, Any]] = []
    for failure_type, results in (
        ("nuisance_leakage", nuisance_results),
        ("context_leakage", context_results),
    ):
        for result in results:
            if result.invariance_score < FAILURE_THRESHOLD:
                failures.append({
                    "type": failure_type,
                    "intervention": result.intervention_target,
                    "value": _json_value(result.intervention_value),
                    "invariance_score": result.invariance_score,
                })
    return failures


class CausalValidator:
    """Measure representation changes under environment interventions."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    @staticmethod
    def _target_and_values(
        environment: Any, metadata: Dict[str, Any], kind: str
    ) -> Tuple[Optional[str], List[Any]]:
        del environment
        if kind == "nuisance":
            if "N" in metadata:
                return "do(N)", [-0.5, 0.0, 0.5]
            variables = metadata.get("nuisance_variables", {})
            preferred = metadata.get("shortcut_feature")
        else:
            if "Z" in metadata:
                values = list(np.unique(metadata["Z"]))[:3]
                return "do(Z)", [_json_value(value) for value in values]
            variables = metadata.get("context_variables", {})
            preferred = None

        if not isinstance(variables, dict) or not variables:
            return None, []
        target = preferred if preferred in variables else sorted(variables)[0]
        raw = np.asarray(variables[target])
        if raw.dtype.kind in "SUO":
            values = list(np.unique(raw))[:3]
        else:
            values = list(np.quantile(raw.astype(float), [0.1, 0.5, 0.9]))
        return target, [_json_value(value) for value in values]

    def validate(
        self,
        extractor: Any,
        environment: Any,
        test_observations: np.ndarray,
        test_context: np.ndarray,
        test_nuisance: np.ndarray,
        test_metadata: Optional[Dict[str, Any]] = None,
        intervention_targets: Optional[Dict[str, List[Any]]] = None,
    ) -> CausalValidationResult:
        metadata = test_metadata or {"Z": test_context, "N": test_nuisance}
        invariant_before = extractor.extract(
            test_observations, test_context, None
        ).invariant_representation

        if intervention_targets is None:
            nuisance_target, nuisance_values = self._target_and_values(
                environment, metadata, "nuisance"
            )
            context_target, context_values = self._target_and_values(
                environment, metadata, "context"
            )
        else:
            nuisance_target = "do(N)"
            nuisance_values = intervention_targets.get("do(N)", [])
            context_target = "do(Z)"
            context_values = intervention_targets.get("do(Z)", [])

        nuisance_results = [
            self._test_intervention(
                extractor, environment, test_observations, test_context,
                test_nuisance, nuisance_target, value, invariant_before, metadata
            )
            for value in nuisance_values
            if nuisance_target is not None
        ]
        context_results = [
            self._test_intervention(
                extractor, environment, test_observations, test_context,
                test_nuisance, context_target, value, invariant_before, metadata
            )
            for value in context_values
            if context_target is not None
        ]

        failures = _collect_failure_cases(nuisance_results, context_results)

        nuisance_avg = float(np.mean([r.invariance_score for r in nuisance_results])) if nuisance_results else 1.0
        context_avg = float(np.mean([r.invariance_score for r in context_results])) if context_results else 1.0
        return CausalValidationResult(
            extractor_type=type(extractor).__name__,
            extractor_config_hash=extractor.get_config_hash(),
            environment=type(environment).__name__,
            seed=self.seed,
            nuisance_interventions=nuisance_results,
            context_interventions=context_results,
            avg_nuisance_invariance=nuisance_avg,
            avg_context_invariance=context_avg,
            overall_invariance=(nuisance_avg + context_avg) / 2.0,
            failure_cases=failures,
            timestamp=datetime.now().isoformat(),
        )

    def _test_intervention(
        self, extractor: Any, environment: Any, observations: np.ndarray,
        context: np.ndarray, nuisance: np.ndarray, target: str, value: Any,
        invariant_before: np.ndarray, metadata: Dict[str, Any]
    ) -> InterventionResult:
        mock_data = type("InterventionData", (), {
            "observations": observations,
            "labels": np.zeros(len(observations)),
            "metadata": metadata,
            "splits": {},
            "config_hash": "",
            "seed": self.seed,
            "timestamp": "",
        })()
        intervened = environment.intervene(mock_data, target, value)
        intervened_context = intervened.metadata.get("Z", context)
        invariant_after = extractor.extract(
            intervened.observations, intervened_context, None
        ).invariant_representation
        mean_shift = float(np.mean(np.abs(invariant_before - invariant_after)))
        correlations: List[float] = []
        for column in range(min(invariant_before.shape[1], invariant_after.shape[1])):
            left, right = invariant_before[:, column], invariant_after[:, column]
            if np.std(left) == 0 or np.std(right) == 0:
                continue
            correlation = float(np.corrcoef(left, right)[0, 1])
            if np.isfinite(correlation):
                correlations.append(abs(correlation))
        return InterventionResult(
            intervention_target=str(target),
            intervention_value=value,
            I_before=invariant_before,
            I_after=invariant_after,
            mean_shift=mean_shift,
            correlation=float(np.mean(correlations)) if correlations else 0.0,
            invariance_score=1.0 / (1.0 + mean_shift),
            config_hash=extractor.get_config_hash(),
            seed=self.seed,
        )


def run_causal_validation_experiment(
    extractor: Any, environment: Any, test_observations: np.ndarray,
    test_context: np.ndarray, test_nuisance: np.ndarray, output_dir: Path,
    seed: int = 42, test_metadata: Optional[Dict[str, Any]] = None
) -> CausalValidationResult:
    result = CausalValidator(seed).validate(
        extractor, environment, test_observations, test_context, test_nuisance,
        test_metadata
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    arrays: Dict[str, np.ndarray] = {}
    for group_name, interventions in (
        ("nuisance", result.nuisance_interventions),
        ("context", result.context_interventions),
    ):
        for index, intervention in enumerate(interventions):
            arrays[f"{group_name}_{index}_before"] = intervention.I_before
            arrays[f"{group_name}_{index}_after"] = intervention.I_after
    arrays_path = output_dir / "causal_arrays.npz"
    np.savez_compressed(arrays_path, **arrays)
    result.arrays = {
        "path": str(arrays_path),
        "sha256": _sha256(arrays_path),
        "entries": {
            name: {"shape": list(value.shape), "dtype": str(value.dtype)}
            for name, value in arrays.items()
        },
    }
    (output_dir / "causal_validation.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8"
    )
    return result
