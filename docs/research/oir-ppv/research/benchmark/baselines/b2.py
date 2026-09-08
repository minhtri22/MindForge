"""
B2: Encoder Representation Baseline
Learn encoder representation without explicit invariant constraint.
"""

import numpy as np
from benchmark.core import BaseBaseline
from typing import Dict, Any


class B2_EncoderRepresentation(BaseBaseline):
    """B2: Encoder Representation Baseline."""
    
    def _validate_config(self) -> None:
        self.latent_dim = self.config.get("encoder", {}).get("latent_dim", 64)
    
    def train(self, train_data: np.ndarray, train_labels: np.ndarray, 
              val_data: np.ndarray = None, val_labels: np.ndarray = None,
              metadata: Dict = None) -> Dict[str, Any]:
        """Train encoder + predictor."""
        self.train_data = train_data.copy()
        self.train_labels = train_labels.copy()
        self.is_trained = True
        
        # Placeholder: simple PCA as encoder
        from sklearn.decomposition import PCA
        self.encoder = PCA(n_components=min(self.latent_dim, train_data.shape[1]))
        self.encoder.fit(train_data)
        
        return {"status": "trained", "latent_dim": self.latent_dim}
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict using encoded representation."""
        if not self.is_trained:
            return np.zeros(len(data), dtype=int)
        
        # Encode then simple classifier
        encoded = self.encoder.transform(data)
        # Nearest neighbor in latent space
        train_encoded = self.encoder.transform(self.train_data)
        return self._knn_predict(encoded, train_encoded, self.train_labels)
    
    def get_invariant_representation(self, data: np.ndarray) -> np.ndarray:
        """Return encoder representation."""
        if not self.is_trained:
            return data.copy()
        return self.encoder.transform(data)
    
    def _knn_predict(self, X_test, X_train, y_train, k=3):
        """Simple k-NN prediction."""
        distances = np.sqrt(((X_test[:, np.newaxis] - X_train) ** 2).sum(axis=2))
        nearest_k = np.argsort(distances, axis=1)[:, :k]
        preds = []
        for idx in nearest_k:
            votes = np.bincount(y_train[idx])
            preds.append(np.argmax(votes))
        return np.array(preds)


try:
    from sklearn.decomposition import PCA
except ImportError:
    class PCA:
        def __init__(self, n_components):
            self.n_components = n_components
        
        def fit(self, X):
            # Simple SVD
            U, s, Vt = np.linalg.svd(X, full_matrices=False)
            self.components_ = Vt[:self.n_components]
            return self
        
        def transform(self, X):
            return X @ self.components_.T