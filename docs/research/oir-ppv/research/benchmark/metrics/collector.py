"""
Metrics Collection Module
Standardized metrics for OIR-PPV benchmark evaluation.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix


@dataclass
class GeneralizationMetrics:
    """Generalization evaluation metrics."""
    accuracy: float
    f1_macro: float
    f1_micro: float
    auroc: float
    per_class_accuracy: Dict[int, float]
    confusion_matrix: np.ndarray
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "f1_macro": self.f1_macro,
            "f1_micro": self.f1_micro,
            "auroc": self.auroc,
            "per_class_accuracy": self.per_class_accuracy,
            "confusion_matrix": self.confusion_matrix.tolist()
        }


@dataclass
class InterventionStabilityMetrics:
    """Intervention stability metrics."""
    delta_causal: float
    intervention_consistency: float
    invariance_scores: Dict[str, float]
    counterfactual_accuracy: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "delta_causal": self.delta_causal,
            "intervention_consistency": self.intervention_consistency,
            "invariance_scores": self.invariance_scores,
            "counterfactual_accuracy": self.counterfactual_accuracy
        }


@dataclass
class GenerationQualityMetrics:
    """Generation quality metrics."""
    fid: float
    invariant_preservation: float
    context_response_accuracy: float
    diversity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fid": self.fid,
            "invariant_preservation": self.invariant_preservation,
            "context_response_accuracy": self.context_response_accuracy,
            "diversity_score": self.diversity_score
        }


def compute_generalization_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> GeneralizationMetrics:
    """Compute comprehensive generalization metrics."""
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_micro = f1_score(y_true, y_pred, average="micro", zero_division=0)
    
    try:
        if len(np.unique(y_true)) == 2:
            auroc = roc_auc_score(y_true, y_pred)
        else:
            auroc = roc_auc_score(y_true, y_pred, multi_class="ovr", average="macro")
    except:
        auroc = 0.0
    
    # Per-class accuracy
    cm = confusion_matrix(y_true, y_pred)
    per_class = {}
    for i in range(len(cm)):
        if cm[i].sum() > 0:
            per_class[i] = cm[i, i] / cm[i].sum()
        else:
            per_class[i] = 0.0
    
    return GeneralizationMetrics(
        accuracy=acc,
        f1_macro=f1_macro,
        f1_micro=f1_micro,
        auroc=auroc,
        per_class_accuracy=per_class,
        confusion_matrix=cm
    )


def compute_intervention_stability(baseline, env, test_data: np.ndarray, 
                                   test_labels: np.ndarray,
                                   metadata: Dict = None) -> InterventionStabilityMetrics:
    """Compute intervention stability metrics."""
    if not hasattr(baseline, 'evaluate_intervention_stability'):
        return InterventionStabilityMetrics(
            delta_causal=0.0,
            intervention_consistency=0.0,
            invariance_scores={}
        )
    
    results = baseline.evaluate_intervention_stability(env, test_data, test_labels, metadata)
    
    return InterventionStabilityMetrics(
        delta_causal=results.get("delta_causal", 0.0),
        intervention_consistency=results.get("intervention_consistency", 0.0),
        invariance_scores=results.get("invariance_scores", {}),
        counterfactual_accuracy=results.get("counterfactual_accuracy")
    )


def compute_generation_quality(baseline, env, test_data: np.ndarray = None) -> GenerationQualityMetrics:
    """Compute generation quality metrics."""
    if not hasattr(baseline, 'evaluate_generation_quality'):
        return GenerationQualityMetrics(
            fid=0.0,
            invariant_preservation=0.0,
            context_response_accuracy=0.0,
            diversity_score=0.0
        )
    
    results = baseline.evaluate_generation_quality(env, test_data)
    
    return GenerationQualityMetrics(
        fid=results.get("fid", 0.0),
        invariant_preservation=results.get("invariant_preservation", 0.0),
        context_response_accuracy=results.get("context_response_accuracy", 0.0),
        diversity_score=results.get("diversity_score", 0.0)
    )


def aggregate_metrics(results: List[Dict]) -> Dict[str, Any]:
    """Aggregate metrics across multiple runs/seeds."""
    if not results:
        return {}
    
    keys = results[0].keys()
    aggregated = {}
    
    for key in keys:
        values = [r[key] for r in results if key in r]
        if values and isinstance(values[0], (int, float)):
            aggregated[key] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "values": values
            }
        elif values and isinstance(values[0], dict):
            # Recursively aggregate nested dicts
            aggregated[key] = aggregate_metrics(values)
    
    return aggregated