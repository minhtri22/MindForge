"""
B0: ERM / Context Memorization Baseline Implementation
Empirical Risk Minimization - memorizes context-specific patterns.
"""

import numpy as np
from benchmark.core import BaseBaseline
from typing import Dict, Any
import json


class B0_ERM(BaseBaseline):
    """B0: ERM / Context Memorization Baseline."""
    
    def _validate_config(self) -> None:
        # B0 has minimal config requirements
        pass
    
    def train(self, train_data: np.ndarray, train_labels: np.ndarray, 
              val_data: np.ndarray = None, val_labels: np.ndarray = None,
              metadata: Dict = None) -> Dict[str, Any]:
        """Train ERM model (simple MLP)."""
        # Simple implementation: store training data for memorization
        # In practice: train MLP with cross-entropy
        self.train_data = train_data.copy()
        self.train_labels = train_labels.copy()
        self.is_trained = True
        
        # Store simple stats for "prediction"
        self.class_priors = np.bincount(train_labels) / len(train_labels)
        self.label_mapping = {i: i for i in range(len(self.class_priors))}
        
        return {"status": "trained", "n_samples": len(train_labels)}
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict using nearest neighbor memorization."""
        if not self.is_trained:
            # Return prior prediction
            return np.full(len(data), np.argmax(self.class_priors))
        
        # 1-NN memorization (simplified)
        from sklearn.neighbors import KNeighborsClassifier
        if len(self.train_data) > 1000:  # Subsample for efficiency
            idx = self.rng.choice(len(self.train_data), 1000, replace=False)
            train_sub = self.train_data[idx]
            label_sub = self.train_labels[idx]
        else:
            train_sub = self.train_data
            label_sub = self.train_labels
        
        knn = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
        knn.fit(train_sub, label_sub)
        return knn.predict(data)
    
    def get_invariant_representation(self, data: np.ndarray) -> np.ndarray:
        """B0 has no invariant representation - returns input."""
        return data.copy()
    
    def get_limitations(self) -> Dict[str, Any]:
        return {
            "implementation": "placeholder",
            "method": "1-NN memorization (not true ERM)",
            "notes": "Uses KNN as proxy for ERM; no gradient-based training"
        }


# Import for KNN (would normally be in requirements)
try:
    from sklearn.neighbors import KNeighborsClassifier
except ImportError:
    # Fallback for environments without sklearn
    class KNeighborsClassifier:
        def __init__(self, n_neighbors=1, metric='euclidean'):
            self.n_neighbors = n_neighbors
            self.metric = metric
            self.X_train = None
            self.y_train = None
        
        def fit(self, X, y):
            self.X_train = X
            self.y_train = y
        
        def predict(self, X):
            if self.X_train is None:
                return np.zeros(len(X))
            # Simple 1-NN
            from sklearn.metrics import pairwise_distances
            distances = pairwise_distances(X, self.X_train, metric=self.metric)
            nearest_idx = np.argmin(distances, axis=1)
            return self.y_train[nearest_idx]