"""
B1: Domain Generalization Baseline (IRM, VREx class)
"""

import numpy as np
from benchmark.core import BaseBaseline
from typing import Dict, Any


class B1_DomainGeneralization(BaseBaseline):
    """B1: Domain Generalization Baseline (IRM/VREx)."""
    
    def _validate_config(self) -> None:
        self.method = self.config.get("dg_method", "irm")
        self.penalty_weight = self.config.get("irm", {}).get("penalty_weight", 1.0)
        self.warmup_epochs = self.config.get("irm", {}).get("warmup_epochs", 10)
    
    def train(self, train_data: np.ndarray, train_labels: np.ndarray, 
              val_data: np.ndarray = None, val_labels: np.ndarray = None,
              metadata: Dict = None) -> Dict[str, Any]:
        """Train domain generalization model."""
        # Placeholder: store data and config
        self.train_data = train_data.copy()
        self.train_labels = train_labels.copy()
        self.domain_labels = metadata.get("context_variables", {}).get("domain", 
                                        np.zeros(len(train_labels))) if metadata else None
        self.is_trained = True
        
        return {"status": "trained", "method": self.method}
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict using trained model."""
        if not self.is_trained:
            return np.zeros(len(data), dtype=int)
        
        # Placeholder: random prediction based on class prior
        classes = np.unique(self.train_labels)
        return self.rng.choice(classes, size=len(data))
    
    def get_invariant_representation(self, data: np.ndarray) -> np.ndarray:
        """Return invariant representation (placeholder)."""
        # IRM would return phi(x) where phi is invariant predictor
        return data.copy()
    
    def evaluate_intervention_stability(self, env, test_data: np.ndarray, 
                                        test_labels: np.ndarray,
                                        metadata: Dict = None) -> Dict[str, float]:
        """Evaluate intervention stability."""
        # Placeholder: return dummy metrics
        return {
            "delta_causal": 0.0,
            "intervention_consistency": 0.0
        }


# Fallback for pairwise_distances
try:
    from sklearn.metrics import pairwise_distances
except ImportError:
    def pairwise_distances(X, Y, metric='euclidean'):
        if metric == 'euclidean':
            return np.sqrt(((X[:, np.newaxis] - Y) ** 2).sum(axis=2))
        return np.zeros((len(X), len(Y)))