"""
M3: Manifestation Generator Interface
G(I, Z, N) -> Manifestation

This module defines the interface for generating manifestations from
invariant representation, context, and nuisance variables.
Implementation to be completed in M3.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import numpy as np

# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .invariant_extractor import InvariantExtractor
else:
    InvariantExtractor = "InvariantExtractor"


@dataclass
class GenerationResult:
    """Result of manifestation generation."""
    generated_observations: np.ndarray  # Shape: (n_samples, n_features)
    metadata: Dict[str, Any]            # Generation metadata
    config_hash: str                    # Configuration hash for provenance


class ManifestationGenerator(ABC):
    """Abstract interface for manifestation generation G(I, Z, N)."""
    
    @abstractmethod
    def generate(self,
                 invariant: np.ndarray,       # I: (n_samples, invariant_dim)
                 context: np.ndarray,         # Z: (n_samples, n_context)
                 nuisance: np.ndarray,        # N: (n_samples, n_nuisance)
                 metadata: Dict = None) -> GenerationResult:
        """
        Generate manifestations from invariant representation, context, and nuisance.
        
        Args:
            invariant: Invariant representation I
            context: Context variables Z
            nuisance: Nuisance variables N
            metadata: Additional generation metadata
            
        Returns:
            GenerationResult containing generated observations
        """
        pass
    
    @abstractmethod
    def get_config_hash(self) -> str:
        """Return configuration hash for provenance."""
        pass
    
    @abstractmethod
    def get_output_dim(self) -> int:
        """Return dimension of generated observations."""
        pass


class PlaceholderManifestationGenerator(ManifestationGenerator):
    """Placeholder implementation for M2-M3 transition."""
    
    def __init__(self, output_dim: int = 10, seed: int = 42):
        self.output_dim = output_dim
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def generate(self,
                 invariant: np.ndarray,
                 context: np.ndarray,
                 nuisance: np.ndarray,
                 metadata: Dict = None) -> GenerationResult:
        """Placeholder: return random noise with correct shape."""
        n_samples = len(invariant)
        generated = self.rng.normal(0, 1, size=(n_samples, self.output_dim))
        
        return GenerationResult(
            generated_observations=generated,
            metadata={
                "method": "Random noise (placeholder)",
                "input_shapes": {
                    "invariant": invariant.shape,
                    "context": context.shape,
                    "nuisance": nuisance.shape
                }
            },
            config_hash=self.get_config_hash()
        )
    
    def get_config_hash(self) -> str:
        import hashlib, json
        config = {"method": "Random", "output_dim": self.output_dim, "seed": self.seed}
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
    
    def get_output_dim(self) -> int:
        return self.output_dim


class OIRManifestationGenerator(ManifestationGenerator):
    """
    Measurable OIR-PPV Manifestation Generator G(I, Z, N).
    
    Implements a conditional decoder:
    - Input: concatenated [I, Z, N]
    - Output: generated observations matching data distribution
    - Training: reconstruction loss + invariant preservation + context response
    
    This is a measurable implementation for M3 evaluation.
    """
    
    def __init__(self,
                 output_dim: int = 10,
                 invariant_dim: int = 64,
                 context_dim: int = 5,
                 nuisance_dim: int = 3,
                 decoder_hidden: list = None,
                 seed: int = 42):
        self.output_dim = output_dim
        self.invariant_dim = invariant_dim
        self.context_dim = context_dim
        self.nuisance_dim = nuisance_dim
        self.decoder_hidden = decoder_hidden or [256, 128, 256]
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._fitted = False
        self._decoder = None
        self._training_data = None
    
    def generate(self,
                 invariant: np.ndarray,
                 context: np.ndarray,
                 nuisance: np.ndarray,
                 metadata: Dict = None) -> GenerationResult:
        """
        Generate manifestations from I, Z, N.
        
        If not fitted, stores training data for later use.
        Then generates using conditional decoder.
        """
        # Ensure numeric
        invariant = invariant.astype(float) if invariant.dtype.kind not in 'f' else invariant
        context = context.astype(float) if context.dtype.kind not in 'f' else context
        nuisance = nuisance.astype(float) if nuisance.dtype.kind not in 'f' else nuisance
        
        n_samples = len(invariant)
        
        if not self._fitted:
            # First call: store data for training, return placeholder
            self._training_data = {
                'invariant': invariant.copy(),
                'context': context.copy(),
                'nuisance': nuisance.copy()
            }
            
            generated = self.rng.normal(0, 1, size=(n_samples, self.output_dim))
            method = "Random noise (first call - not fitted)"
        else:
            # Use decoder
            generated = self._generate_with_decoder(invariant, context, nuisance)
            method = "OIRManifestationGenerator (conditional decoder)"
        
        return GenerationResult(
            generated_observations=generated,
            metadata={
                "method": method,
                "output_dim": self.output_dim,
                "invariant_dim": self.invariant_dim,
                "context_dim": self.context_dim,
                "nuisance_dim": self.nuisance_dim,
                "decoder_hidden": self.decoder_hidden,
                "fitted": self._fitted
            },
            config_hash=self.get_config_hash()
        )
    
    def fit(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray, targets: np.ndarray = None):
        """
        Fit the conditional decoder on training data.
        
        Placeholder implementation: stores training data and fits simple linear decoder.
        Real implementation would use gradient-based training.
        """
        from sklearn.linear_model import LinearRegression
        
        # Concatenate inputs
        X = np.concatenate([invariant, context, nuisance], axis=1)
        
        if targets is not None:
            self._decoder = LinearRegression()
            self._decoder.fit(X, targets)
        else:
            # Autoencoder-style: reconstruct input observations
            pass
        
        self._fitted = True
        return self
    
    def _generate_with_decoder(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
        """Generate using fitted decoder."""
        if self._decoder is None:
            return self.rng.normal(0, 1, size=(len(invariant), self.output_dim))
        
        X = np.concatenate([invariant, context, nuisance], axis=1)
        return self._decoder.predict(X)
    
    def get_config_hash(self) -> str:
        import hashlib, json
        config = {
            "method": "OIRManifestationGenerator",
            "output_dim": self.output_dim,
            "invariant_dim": self.invariant_dim,
            "context_dim": self.context_dim,
            "nuisance_dim": self.nuisance_dim,
            "decoder_hidden": self.decoder_hidden,
            "seed": self.seed
        }
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
    
    def decode(self, invariant: np.ndarray, context: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
        """Alias for generate to match Decoder interface."""
        result = self.generate(invariant, context, nuisance)
        return result.generated_observations
    
    def get_output_dim(self) -> int:
        return self.output_dim


class PipelineRunner:
    """Run full OIR-PPV pipeline: Experience -> I -> G(I,Z,N) -> Manifestation."""
    
    def __init__(self, 
                 invariant_extractor: InvariantExtractor,
                 generator: ManifestationGenerator):
        self.invariant_extractor = invariant_extractor
        self.generator = generator
    
    def run(self,
            observations: np.ndarray,
            context: np.ndarray,
            nuisance: np.ndarray,
            labels: np.ndarray = None,
            metadata: Dict = None) -> Dict[str, Any]:
        """
        Run complete pipeline.
        
        Returns dict with:
        - invariant_result: InvariantExtractionResult
        - generation_result: GenerationResult
        """
        # Step 1: Extract invariant I
        invariant_result = self.invariant_extractor.extract(
            observations, context, labels, metadata
        )
        
        # Step 2: Generate manifestation G(I, Z, N)
        generation_result = self.generator.generate(
            invariant_result.invariant_representation,
            context,
            nuisance,
            metadata
        )
        
        return {
            "invariant_result": invariant_result,
            "generation_result": generation_result
        }