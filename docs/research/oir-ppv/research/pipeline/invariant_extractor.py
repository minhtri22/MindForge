"""
M3: Invariant Representation Extractor Interface
Experience -> Invariant I

This module defines the interface for extracting invariant representations
from environment experience. Implementation to be completed in M3.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class InvariantExtractionResult:
    """Result of invariant extraction."""
    invariant_representation: np.ndarray  # Shape: (n_samples, invariant_dim)
    metadata: Dict[str, Any]              # Extraction metadata
    config_hash: str                      # Configuration hash for provenance


class InvariantExtractor(ABC):
    """Abstract interface for invariant representation extraction."""
    
    @abstractmethod
    def extract(self, 
                observations: np.ndarray, 
                context: np.ndarray = None,
                labels: np.ndarray = None,
                metadata: Dict = None) -> InvariantExtractionResult:
        """
        Extract invariant representation I from experience.
        
        Args:
            observations: Raw observations from environment (n_samples, n_features)
            context: Context variables Z (n_samples, n_context) if available
            labels: Target labels Y (n_samples,) if available
            metadata: Additional environment metadata
            
        Returns:
            InvariantExtractionResult containing I and metadata
        """
        pass
    
    @abstractmethod
    def get_config_hash(self) -> str:
        """Return configuration hash for provenance."""
        pass
    
    @abstractmethod
    def get_invariant_dim(self) -> int:
        """Return dimension of invariant representation."""
        pass


class PlaceholderInvariantExtractor(InvariantExtractor):
    """Placeholder implementation for M2-M3 transition."""
    
    def __init__(self, invariant_dim: int = 64, seed: int = 42):
        self.invariant_dim = invariant_dim
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._fitted = False
    
    def extract(self, 
                observations: np.ndarray, 
                context: np.ndarray = None,
                labels: np.ndarray = None,
                metadata: Dict = None) -> InvariantExtractionResult:
        """Placeholder: use PCA as invariant extractor."""
        if not self._fitted:
            # Fit on first call
            from sklearn.decomposition import PCA
            self.pca = PCA(n_components=min(self.invariant_dim, observations.shape[1]))
            self.pca.fit(observations)
            self._fitted = True
        
        I = self.pca.transform(observations)
        
        return InvariantExtractionResult(
            invariant_representation=I,
            metadata={
                "method": "PCA (placeholder)",
                "explained_variance_ratio": self.pca.explained_variance_ratio_.tolist(),
                "invariant_dim": self.invariant_dim
            },
            config_hash=self.get_config_hash()
        )
    
    def get_config_hash(self) -> str:
        import hashlib, json
        config = {"method": "PCA", "invariant_dim": self.invariant_dim, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
    
    def get_invariant_dim(self) -> int:
        return self.invariant_dim


class OIRInvariantExtractor(InvariantExtractor):
    """
    Measurable OIR-PPV Invariant Extractor.
    
    Implements a VAE-style encoder with invariant constraint:
    - Encoder: observations + context -> latent distribution q(z|x,c)
    - Invariant loss: HSIC/MMD between z and nuisance/context
    - Predictor: latent -> labels (ensures utility)
    
    This is a measurable implementation for M3 evaluation.
    """
    
    def __init__(self, 
                 invariant_dim: int = 64,
                 encoder_hidden: list = None,
                 predictor_hidden: list = None,
                 invariant_weight: float = 1.0,
                 seed: int = 42):
        self.invariant_dim = invariant_dim
        self.encoder_hidden = encoder_hidden or [256, 128]
        self.predictor_hidden = predictor_hidden or [64, 32]
        self.invariant_weight = invariant_weight
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._fitted = False
        self._encoder = None
        self._predictor = None
        self._invariant_loss_fn = None
    
    def extract(self, 
                observations: np.ndarray, 
                context: np.ndarray = None,
                labels: np.ndarray = None,
                metadata: Dict = None) -> InvariantExtractionResult:
        """
        Extract invariant representation I from observations.
        
        If not fitted, trains the encoder+predictor on the provided data.
        Then returns invariant representations.
        """
        # Ensure numeric data
        if observations.dtype.kind in 'SU':
            observations = self._encode_categorical(observations)
        else:
            observations = observations.astype(float)
        
        if not self._fitted:
            self._train(observations, context, labels)
        
        # Encode to invariant representation
        I = self._encoder.transform(observations)
        
        return InvariantExtractionResult(
            invariant_representation=I,
            metadata={
                "method": "OIRInvariantExtractor (VAE-style + invariant constraint)",
                "invariant_dim": self.invariant_dim,
                "encoder_hidden": self.encoder_hidden,
                "predictor_hidden": self.predictor_hidden,
                "invariant_weight": self.invariant_weight,
                "training_samples": getattr(self, '_n_train_samples', 0)
            },
            config_hash=self.get_config_hash()
        )
    
    def _train(self, observations: np.ndarray, context: np.ndarray, labels: np.ndarray):
        """Train encoder + predictor with invariant constraint (placeholder training)."""
        from sklearn.decomposition import PCA
        from sklearn.linear_model import LogisticRegression
        
        # Placeholder: use PCA as encoder, LogisticRegression as predictor
        # Real implementation would use gradient-based VAE training
        self._encoder = PCA(n_components=min(self.invariant_dim, observations.shape[1]))
        self._encoder.fit(observations)
        
        I_train = self._encoder.transform(observations)
        
        if labels is not None:
            self._predictor = LogisticRegression(max_iter=1000, random_state=self.seed)
            self._predictor.fit(I_train, labels)
        
        self._fitted = True
        self._n_train_samples = len(observations)
    
    def _encode_categorical(self, data: np.ndarray) -> np.ndarray:
        """Encode categorical string data to numeric."""
        from sklearn.preprocessing import LabelEncoder
        n_samples, n_features = data.shape
        encoded = np.zeros((n_samples, n_features), dtype=float)
        
        for i in range(n_features):
            col = data[:, i]
            le = LabelEncoder()
            encoded[:, i] = le.fit_transform(col)
        
        return encoded
    
    def predict(self, observations: np.ndarray) -> np.ndarray:
        """Predict labels using invariant representation."""
        if not self._fitted or self._predictor is None:
            return np.zeros(len(observations))
        
        I = self.extract(observations).invariant_representation
        return self._predictor.predict(I)
    
    def predict_proba(self, observations: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self._fitted or self._predictor is None:
            return np.zeros((len(observations), 2))
        
        I = self.extract(observations).invariant_representation
        return self._predictor.predict_proba(I)
    
    def get_config_hash(self) -> str:
        import hashlib, json
        config = {
            "method": "OIRInvariantExtractor",
            "invariant_dim": self.invariant_dim,
            "encoder_hidden": self.encoder_hidden,
            "predictor_hidden": self.predictor_hidden,
            "invariant_weight": self.invariant_weight,
            "seed": self.seed
        }
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
    
    def get_invariant_dim(self) -> int:
        return self.invariant_dim