"""
B3: Invariant Representation Only Baseline
Learn invariant representation I, but no generator G(I,Z,N).
"""

import numpy as np
from benchmark.core import BaseBaseline
from typing import Dict, Any


class B3_InvariantOnly(BaseBaseline):
    """B3: Invariant Representation Only."""
    
    def _validate_config(self) -> None:
        self.invariant_dim = self.config.get("invariant_learner", {}).get("invariant_dim", 64)
        self.method = self.config.get("invariant_constraint", {}).get("method", "hsic")
    
    def train(self, train_data: np.ndarray, train_labels: np.ndarray, 
              val_data: np.ndarray = None, val_labels: np.ndarray = None,
              metadata: Dict = None) -> Dict[str, Any]:
        """Train invariant representation learner."""
        self.train_data = train_data.copy()
        self.train_labels = train_labels.copy()
        self.is_trained = True
        
        # Placeholder: use encoder with HSIC penalty
        from sklearn.decomposition import PCA
        self.encoder = PCA(n_components=min(self.invariant_dim, train_data.shape[1]))
        self.encoder.fit(train_data)
        
        return {"status": "trained", "invariant_dim": self.invariant_dim}
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict using invariant representation."""
        if not self.is_trained:
            return np.zeros(len(data), dtype=int)
        
        encoded = self.encoder.transform(data)
        train_encoded = self.encoder.transform(self.train_data)
        return self._knn_predict(encoded, train_encoded, self.train_labels)
    
    def get_invariant_representation(self, data: np.ndarray) -> np.ndarray:
        """Return invariant representation I."""
        if not self.is_trained:
            return data.copy()
        return self.encoder.transform(data)
    
    def evaluate_intervention_stability(self, env, test_data: np.ndarray, 
                                        test_labels: np.ndarray,
                                        metadata: Dict = None) -> Dict[str, float]:
        """Evaluate intervention stability using invariant representation."""
        # Get invariant representations
        I_test = self.get_invariant_representation(test_data)
        
        # Measure stability across intervention targets
        stability_scores = {}
        for target in env.get_intervention_targets():
            # Apply intervention
            intervened_data = env.intervene(
                type('Data', (), {
                    'observations': test_data,
                    'labels': test_labels,
                    'metadata': metadata,
                    'splits': {},
                    'config_hash': '',
                    'seed': 42,
                    'timestamp': ''
                })(), target, 0.0
            )
            
            I_intervened = self.get_invariant_representation(intervened_data.observations)
            
            # Invariance: I should not change under nuisance intervention
            if "nuis" in target or "N" in target:
                diff = np.mean(np.abs(I_test - I_intervened))
                stability_scores[f"invariance_{target}"] = float(1.0 / (1.0 + diff))
        
        return {
            "delta_causal": float(np.mean(list(stability_scores.values())) if stability_scores else 0),
            "invariance_scores": stability_scores
        }
    
    def _knn_predict(self, X_test, X_train, y_train, k=3):
        distances = np.sqrt(((X_test[:, np.newaxis] - X_train) ** 2).sum(axis=2))
        nearest_k = np.argsort(distances, axis=1)[:, :k]
        preds = []
        for idx in nearest_k:
            votes = np.bincount(y_train[idx])
            preds.append(np.argmax(votes))
        return np.array(preds)
    
    def get_limitations(self) -> Dict[str, Any]:
        return {
            "implementation": "placeholder",
            "method": "PCA + KNN (no true invariant constraint)",
            "notes": "Uses PCA as encoder; HSIC/other invariant constraints not implemented"
        }


try:
    from sklearn.decomposition import PCA
except ImportError:
    class PCA:
        def __init__(self, n_components):
            self.n_components = n_components
        
        def fit(self, X):
            U, s, Vt = np.linalg.svd(X, full_matrices=False)
            self.components_ = Vt[:self.n_components]
            return self
        
        def transform(self, X):
            return X @ self.components_.T