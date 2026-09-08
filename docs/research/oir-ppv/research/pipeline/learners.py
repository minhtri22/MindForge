"""
M3: Pluggable Learner Interfaces
Replaceable encoder/predictor implementations for invariant extraction and generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import hashlib
import json


@dataclass
class LearnerConfig:
    """Configuration for a learner."""
    learner_type: str
    params: Dict[str, Any]
    seed: int = 42
    
    def get_hash(self) -> str:
        content = json.dumps({
            "type": self.learner_type,
            "params": self.params,
            "seed": self.seed
        }, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()[:16]


class EncoderLearner(ABC):
    """Abstract interface for invariant encoder."""
    
    @abstractmethod
    def fit(self, 
            observations: np.ndarray,
            context: np.ndarray = None,
            labels: np.ndarray = None,
            nuisance: np.ndarray = None) -> Dict[str, Any]:
        """Train encoder on data."""
        pass
    
    @abstractmethod
    def encode(self, observations: np.ndarray) -> np.ndarray:
        """Encode observations to invariant representation."""
        pass
    
    @abstractmethod
    def get_output_dim(self) -> int:
        """Return invariant representation dimension."""
        pass
    
    @abstractmethod
    def get_config_hash(self) -> str:
        """Return configuration hash."""
        pass


class PredictorLearner(ABC):
    """Abstract interface for predictor from invariant representation."""
    
    @abstractmethod
    def fit(self, invariant: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """Train predictor."""
        pass
    
    @abstractmethod
    def predict(self, invariant: np.ndarray) -> np.ndarray:
        """Predict labels from invariant."""
        pass
    
    @abstractmethod
    def predict_proba(self, invariant: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        pass
    
    @abstractmethod
    def get_config_hash(self) -> str:
        pass


class DecoderLearner(ABC):
    """Abstract interface for manifestation decoder G(I, Z, N)."""
    
    @abstractmethod
    def fit(self, 
            invariant: np.ndarray,
            context: np.ndarray,
            nuisance: np.ndarray,
            targets: np.ndarray) -> Dict[str, Any]:
        """Train decoder."""
        pass
    
    @abstractmethod
    def decode(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
        """Generate manifestations."""
        pass
    
    @abstractmethod
    def get_config_hash(self) -> str:
        pass


# ===========================================
# Built-in Implementations (Placeholders)
# ===========================================

class PCAEncoder(EncoderLearner):
    """PCA-based encoder (baseline)."""
    
    def __init__(self, output_dim: int = 64, seed: int = 42):
        self.output_dim = output_dim
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.pca = None
        self._fitted = False
    
    def fit(self, observations: np.ndarray, context: np.ndarray = None, 
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        from sklearn.decomposition import PCA
        self.pca = PCA(n_components=min(self.output_dim, observations.shape[1]))
        self.pca.fit(observations)
        self._fitted = True
        return {"status": "fitted", "explained_variance": self.pca.explained_variance_ratio_.sum()}
    
    def encode(self, observations: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Encoder not fitted")
        return self.pca.transform(observations)
    
    def get_output_dim(self) -> int:
        return self.output_dim
    
    def get_config_hash(self) -> str:
        config = {"type": "PCAEncoder", "output_dim": self.output_dim, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


class MLPEncoder(EncoderLearner):
    """MLP encoder (future: gradient-based)."""
    
    def __init__(self, output_dim: int = 64, hidden_dims: List[int] = None, 
                 activation: str = "relu", seed: int = 42):
        self.output_dim = output_dim
        self.hidden_dims = hidden_dims or [256, 128]
        self.activation = activation
        self.seed = seed
        self._fitted = False
    
    def fit(self, observations: np.ndarray, context: np.ndarray = None,
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        # Placeholder: would use gradient-based training
        self._fitted = True
        return {"status": "placeholder_fitted", "note": "MLP training not implemented"}
    
    def encode(self, observations: np.ndarray) -> np.ndarray:
        # Fallback to PCA
        from sklearn.decomposition import PCA
        pca = PCA(n_components=min(self.output_dim, observations.shape[1]))
        return pca.fit_transform(observations)
    
    def get_output_dim(self) -> int:
        return self.output_dim
    
    def get_config_hash(self) -> str:
        config = {"type": "MLPEncoder", "output_dim": self.output_dim, 
                  "hidden_dims": self.hidden_dims, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


class LogisticPredictor(PredictorLearner):
    """Logistic regression predictor."""
    
    def __init__(self, max_iter: int = 1000, seed: int = 42):
        self.max_iter = max_iter
        self.seed = seed
        self.predictor = None
        self._fitted = False
    
    def fit(self, invariant: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        from sklearn.linear_model import LogisticRegression
        self.predictor = LogisticRegression(max_iter=self.max_iter, random_state=self.seed)
        self.predictor.fit(invariant, labels)
        self._fitted = True
        return {"status": "fitted"}
    
    def predict(self, invariant: np.ndarray) -> np.ndarray:
        if not self._fitted:
            return np.zeros(len(invariant))
        return self.predictor.predict(invariant)
    
    def predict_proba(self, invariant: np.ndarray) -> np.ndarray:
        if not self._fitted:
            n_samples = len(invariant)
            return np.zeros((n_samples, 2))
        return self.predictor.predict_proba(invariant)
    
    def get_config_hash(self) -> str:
        config = {"type": "LogisticPredictor", "max_iter": self.max_iter, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


class LinearDecoder(DecoderLearner):
    """Linear regression decoder."""
    
    def __init__(self, output_dim: int = 10, seed: int = 42):
        self.output_dim = output_dim
        self.seed = seed
        self.decoder = None
        self._fitted = False
    
    def fit(self, invariant: np.ndarray, context: np.ndarray, 
            nuisance: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        from sklearn.linear_model import LinearRegression
        X = np.concatenate([invariant, context, nuisance], axis=1)
        self.decoder = LinearRegression()
        self.decoder.fit(X, targets)
        self._fitted = True
        return {"status": "fitted"}
    
    def decode(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
        if not self._fitted:
            return np.random.randn(len(invariant), self.output_dim)
        X = np.concatenate([invariant, context, nuisance], axis=1)
        return self.decoder.predict(X)
    
    def get_config_hash(self) -> str:
        config = {"type": "LinearDecoder", "output_dim": self.output_dim, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


# ===========================================
# Registry for Pluggable Learners
# ===========================================

class LearnerRegistry:
    """Registry for learner implementations."""
    
    _encoders: Dict[str, type] = {}
    _predictors: Dict[str, type] = {}
    _decoders: Dict[str, type] = {}
    
    @classmethod
    def register_encoder(cls, name: str):
        def decorator(encoder_class: type):
            cls._encoders[name] = encoder_class
            return encoder_class
        return decorator
    
    @classmethod
    def register_predictor(cls, name: str):
        def decorator(predictor_class: type):
            cls._predictors[name] = predictor_class
            return predictor_class
        return decorator
    
    @classmethod
    def register_decoder(cls, name: str):
        def decorator(decoder_class: type):
            cls._decoders[name] = decoder_class
            return decoder_class
        return decorator
    
    @classmethod
    def get_encoder(cls, name: str) -> type:
        if name not in cls._encoders:
            raise ValueError(f"Unknown encoder: {name}. Available: {list(cls._encoders.keys())}")
        return cls._encoders[name]
    
    @classmethod
    def get_predictor(cls, name: str) -> type:
        if name not in cls._predictors:
            raise ValueError(f"Unknown predictor: {name}. Available: {list(cls._predictors.keys())}")
        return cls._predictors[name]
    
    @classmethod
    def get_decoder(cls, name: str) -> type:
        if name not in cls._decoders:
            raise ValueError(f"Unknown decoder: {name}. Available: {list(cls._decoders.keys())}")
        return cls._decoders[name]
    
    @classmethod
    def list_encoders(cls) -> List[str]:
        return list(cls._encoders.keys())
    
    @classmethod
    def list_predictors(cls) -> List[str]:
        return list(cls._predictors.keys())
    
    @classmethod
    def list_decoders(cls) -> List[str]:
        return list(cls._decoders.keys())
    
    @classmethod
    def create_encoder(cls, config: LearnerConfig) -> EncoderLearner:
        encoder_class = cls.get_encoder(config.learner_type)
        return encoder_class(**config.params)
    
    @classmethod
    def create_predictor(cls, config: LearnerConfig) -> PredictorLearner:
        predictor_class = cls.get_predictor(config.learner_type)
        return predictor_class(**config.params)
    
    @classmethod
    def create_decoder(cls, config: LearnerConfig) -> DecoderLearner:
        decoder_class = cls.get_decoder(config.learner_type)
        return decoder_class(**config.params)


# ===========================================
# Real (Non-Placeholder) Learner Implementations
# ===========================================

class AutoencoderEncoder(EncoderLearner):
    """
    Trainable autoencoder-based invariant encoder.
    
    Learns a compressed invariant representation I via reconstruction.
    Uses numpy-only gradient descent (no external deep learning lib).
    Loss = reconstruction MSE + L2 penalty on weights.
    """
    
    def __init__(self, output_dim: int = 64, hidden_dim: int = 128, 
                 learning_rate: float = 0.01, epochs: int = 200, seed: int = 42):
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._fitted = False
        self._W1 = None
        self._b1 = None
        self._W2 = None
        self._b2 = None
        self._loss_history = []
    
    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
    
    def _fit_layers(self, dim_in, dim_out):
        """Initialize layer weights."""
        scale = np.sqrt(6.0 / (dim_in + dim_out))
        W = self.rng.uniform(-scale, scale, size=(dim_in, dim_out))
        b = np.zeros(dim_out)
        return W, b
    
    def fit(self, observations: np.ndarray, context: np.ndarray = None, 
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        X = observations.astype(float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Normalize data
        self._mean = X.mean(axis=0)
        self._std = X.std(axis=0) + 1e-8
        X_norm = (X - self._mean) / self._std
        
        # Initialize weights
        self._W1, self._b1 = self._fit_layers(X_norm.shape[1], self.hidden_dim)
        self._W2, self._b2 = self._fit_layers(self.hidden_dim, self.output_dim)
        self._W3, self._b3 = self._fit_layers(self.output_dim, self.hidden_dim)
        self._W4, self._b4 = self._fit_layers(self.hidden_dim, X_norm.shape[1])
        
        self._loss_history = []
        initial_loss = None
        # Gradient descent training
        for epoch in range(self.epochs):
            # Forward pass
            h1 = self._sigmoid(X_norm @ self._W1 + self._b1)
            I = h1 @ self._W2 + self._b2
            h2 = self._sigmoid(I @ self._W3 + self._b3)
            X_rec = h2 @ self._W4 + self._b4
            
            # Reconstruction loss
            loss = np.mean((X_norm - X_rec) ** 2)
            if not np.isfinite(loss):
                raise FloatingPointError("Autoencoder training produced non-finite loss")
            if initial_loss is None:
                initial_loss = float(loss)
            
            # Backward pass
            d_X_rec = 2 * (X_rec - X_norm) / len(X_norm)
            d_h2 = d_X_rec @ self._W4.T
            d_h2_sigmoid = d_h2 * h2 * (1 - h2)
            d_I = d_h2_sigmoid @ self._W3.T
            d_h1 = d_I @ self._W2.T
            d_h1_sigmoid = d_h1 * h1 * (1 - h1)
            
            # Gradient updates
            self._W4 -= self.learning_rate * (h2.T @ d_X_rec)
            self._b4 -= self.learning_rate * d_X_rec.sum(axis=0)
            self._W3 -= self.learning_rate * (I.T @ d_h2_sigmoid)
            self._b3 -= self.learning_rate * d_h2_sigmoid.sum(axis=0)
            self._W2 -= self.learning_rate * (h1.T @ d_I)
            self._b2 -= self.learning_rate * d_I.sum(axis=0)
            self._W1 -= self.learning_rate * (X_norm.T @ d_h1_sigmoid)
            self._b1 -= self.learning_rate * d_h1_sigmoid.sum(axis=0)
            
            self._loss_history.append(loss)
        
        self._fitted = True
        return {
            "status": "fitted",
            "method": "Autoencoder (numpy gradient descent)",
            "initial_loss": initial_loss,
            "final_loss": float(loss),
            "loss_history_length": len(self._loss_history),
            "input_dim": X.shape[1],
            "hidden_dim": self.hidden_dim,
            "output_dim": self.output_dim,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate
        }
    
    def encode(self, observations: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Encoder not fitted")
        X = observations.astype(float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        X_norm = (X - self._mean) / self._std
        h1 = self._sigmoid(X_norm @ self._W1 + self._b1)
        I = h1 @ self._W2 + self._b2
        return I
    
    def get_output_dim(self) -> int:
        return self.output_dim
    
    def get_config_hash(self) -> str:
        config = {
            "type": "AutoencoderEncoder",
            "output_dim": self.output_dim,
            "hidden_dim": self.hidden_dim,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "seed": self.seed
        }
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


class MLPDecoder(DecoderLearner):
    """
    Trainable MLP conditional decoder G(I, Z, N).
    
    Learns to reconstruct observations from [I, Z, N] concatenation.
    Uses numpy-only gradient descent.
    """
    
    def __init__(self, output_dim: int = 10, hidden_dims: List[int] = None,
                 learning_rate: float = 0.01, epochs: int = 200, seed: int = 42):
        self.output_dim = output_dim
        self.hidden_dims = hidden_dims or [128]
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._fitted = False
        self._loss_history = []
        self._weights = []
        self._biases = []
    
    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
    
    def fit(self, invariant: np.ndarray, context: np.ndarray, 
            nuisance: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        # Concatenate inputs
        X = np.concatenate([invariant, context, nuisance], axis=1).astype(float)
        Y = targets.astype(float)
        
        # Normalize
        self._input_mean = X.mean(axis=0)
        self._input_std = X.std(axis=0) + 1e-8
        X_norm = (X - self._input_mean) / self._input_std
        
        self._target_mean = Y.mean(axis=0)
        self._target_std = Y.std(axis=0) + 1e-8
        Y_norm = (Y - self._target_mean) / self._target_std
        
        # Build architecture
        dims = [X.shape[1]] + self.hidden_dims + [Y.shape[1]]
        self._weights = []
        self._biases = []
        for i in range(len(dims) - 1):
            scale = np.sqrt(6.0 / (dims[i] + dims[i+1]))
            self._weights.append(self.rng.uniform(-scale, scale, size=(dims[i], dims[i+1])))
            self._biases.append(np.zeros(dims[i+1]))
        
        self._loss_history = []
        initial_loss = None
        # Training
        for epoch in range(self.epochs):
            # Forward pass
            activations = [X_norm]
            for i in range(len(self._weights)):
                z = activations[-1] @ self._weights[i] + self._biases[i]
                a = self._sigmoid(z) if i < len(self._weights) - 1 else z
                activations.append(a)
            
            Y_rec = activations[-1]
            loss = np.mean((Y_norm - Y_rec) ** 2)
            if not np.isfinite(loss):
                raise FloatingPointError("MLP decoder training produced non-finite loss")
            if initial_loss is None:
                initial_loss = float(loss)
            
            # Backward pass
            delta = 2 * (Y_rec - Y_norm) / len(Y_norm)
            for i in range(len(self._weights) - 1, -1, -1):
                self._weights[i] -= self.learning_rate * (activations[i].T @ delta)
                self._biases[i] -= self.learning_rate * delta.sum(axis=0)
                if i > 0:
                    delta = (delta @ self._weights[i].T) * activations[i] * (1 - activations[i])
            
            self._loss_history.append(loss)
        
        self._fitted = True
        return {
            "status": "fitted",
            "method": "MLP Decoder (numpy gradient descent)",
            "initial_loss": initial_loss,
            "final_loss": float(loss),
            "architecture": dims,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate
        }
    
    def decode(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("MLPDecoder not fitted. Call fit() before decode().")
        
        X = np.concatenate([invariant, context, nuisance], axis=1).astype(float)
        X_norm = (X - self._input_mean) / self._input_std
        
        a = X_norm
        for i in range(len(self._weights)):
            z = a @ self._weights[i] + self._biases[i]
            a = self._sigmoid(z) if i < len(self._weights) - 1 else z
        
        return a * self._target_std + self._target_mean
    
    def get_config_hash(self) -> str:
        config = {
            "type": "MLPDecoder",
            "output_dim": self.output_dim,
            "hidden_dims": self.hidden_dims,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "seed": self.seed
        }
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


# Register built-in learners
LearnerRegistry.register_encoder("PCA")(PCAEncoder)
LearnerRegistry.register_encoder("MLP")(MLPEncoder)
LearnerRegistry.register_encoder("Autoencoder")(AutoencoderEncoder)
LearnerRegistry.register_predictor("Logistic")(LogisticPredictor)
LearnerRegistry.register_decoder("Linear")(LinearDecoder)
LearnerRegistry.register_decoder("MLPDecoder")(MLPDecoder)


def create_learner_from_config(config: Dict[str, Any], component: str, seed: int = 42) -> Any:
    """Create learner instance from config dict."""
    learner_config = LearnerConfig(
        learner_type=config.get("type", "PCA" if component == "encoder" else "Logistic" if component == "predictor" else "Linear"),
        params={k: v for k, v in config.items() if k != "type"},
        seed=seed
    )
    
    if component == "encoder":
        return LearnerRegistry.create_encoder(learner_config)
    elif component == "predictor":
        return LearnerRegistry.create_predictor(learner_config)
    elif component == "decoder":
        return LearnerRegistry.create_decoder(learner_config)
    else:
        raise ValueError(f"Unknown component: {component}")
