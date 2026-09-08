"""
M3: Evaluation Hooks for OIR-PPV Pipeline
Metrics for invariant consistency, generation validity, novelty, reconstruction.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.decomposition import PCA
from scipy.stats import pearsonr
import hashlib
import json


@dataclass
class InvariantMetrics:
    """Metrics for invariant representation quality."""
    # Invariance to nuisance/context
    invariance_score: float          # 0-1, higher = more invariant
    context_sensitivity: float       # 0-1, higher = more sensitive to context
    nuisance_sensitivity: float      # 0-1, higher = more sensitive to nuisance
    
    # Utility for prediction
    predictive_utility: float        # Accuracy/F1 using I for prediction
    
    # Dimensionality
    effective_rank: int              # Effective rank of invariant representation
    explained_variance: float        # Variance explained by top components
    
    # Provenance
    config_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariance_score": self.invariance_score,
            "context_sensitivity": self.context_sensitivity,
            "nuisance_sensitivity": self.nuisance_sensitivity,
            "predictive_utility": self.predictive_utility,
            "effective_rank": self.effective_rank,
            "explained_variance": self.explained_variance,
            "config_hash": self.config_hash
        }


@dataclass
class GenerationMetrics:
    """Metrics for manifestation generation quality."""
    # Reconstruction quality
    reconstruction_mse: float        # MSE between generated and target
    reconstruction_mae: float        # MAE between generated and target
    
    # Invariant preservation
    invariant_preservation: float    # Correlation between I(orig) and I(gen)
    
    # Context response accuracy
    context_response: float          # Accuracy of context-dependent features
    
    # Novelty / Diversity
    diversity_score: float           # Average pairwise distance in generated set
    novelty_score: float             # Distance from training samples
    
    # Distribution matching
    distribution_similarity: float   # KS-test or MMD between generated and real
    
    # Provenance
    config_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reconstruction_mse": self.reconstruction_mse,
            "reconstruction_mae": self.reconstruction_mae,
            "invariant_preservation": self.invariant_preservation,
            "context_response": self.context_response,
            "diversity_score": self.diversity_score,
            "novelty_score": self.novelty_score,
            "distribution_similarity": self.distribution_similarity,
            "config_hash": self.config_hash
        }


@dataclass
class PipelineEvaluationResult:
    """Complete evaluation result for OIR-PPV pipeline."""
    invariant_metrics: InvariantMetrics
    generation_metrics: GenerationMetrics
    overall_score: float             # Weighted combination
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_metrics": self.invariant_metrics.to_dict(),
            "generation_metrics": self.generation_metrics.to_dict(),
            "overall_score": self.overall_score,
            "timestamp": self.timestamp
        }


class InvariantEvaluator:
    """Evaluate invariant representation quality."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def evaluate(self, 
                 invariant_representation: np.ndarray,
                 context: np.ndarray = None,
                 nuisance: np.ndarray = None,
                 labels: np.ndarray = None,
                 config_hash: str = "") -> InvariantMetrics:
        """Compute invariant metrics."""
        
        # 1. Invariance to nuisance (HSIC-like proxy)
        if nuisance is not None:
            nuisance_sensitivity = self._compute_sensitivity(invariant_representation, nuisance)
            invariance_score = 1.0 / (1.0 + nuisance_sensitivity)
        else:
            invariance_score = 1.0
            nuisance_sensitivity = 0.0
        
        # 2. Context sensitivity
        if context is not None:
            context_sensitivity = self._compute_sensitivity(invariant_representation, context)
        else:
            context_sensitivity = 0.0
        
        # 3. Predictive utility
        predictive_utility = 0.0
        if labels is not None and len(np.unique(labels)) > 1:
            predictive_utility = self._evaluate_predictive_utility(invariant_representation, labels)
        
        # 4. Dimensionality
        effective_rank = self._compute_effective_rank(invariant_representation)
        explained_variance = self._compute_explained_variance(invariant_representation)
        
        return InvariantMetrics(
            invariance_score=invariance_score,
            context_sensitivity=context_sensitivity,
            nuisance_sensitivity=nuisance_sensitivity,
            predictive_utility=predictive_utility,
            effective_rank=effective_rank,
            explained_variance=explained_variance,
            config_hash=config_hash
        )
    
    def _compute_sensitivity(self, I: np.ndarray, target: np.ndarray) -> float:
        """Compute sensitivity of I to target (proxy for HSIC/MMD)."""
        # Linear proxy: canonical correlation
        try:
            from sklearn.cross_decomposition import CCA
            cca = CCA(n_components=min(I.shape[1], target.shape[1]) if target.ndim > 1 else 1)
            I_centered = I - I.mean(axis=0)
            T_centered = target - target.mean(axis=0)
            
            # Simple correlation-based sensitivity
            corr = np.abs(np.corrcoef(I_centered.T, T_centered.T))
            # Off-diagonal blocks
            n_i = I.shape[1]
            if n_i < corr.shape[0]:
                cross_corr = corr[:n_i, n_i:]
                sensitivity = float(np.mean(np.abs(cross_corr)))
            else:
                sensitivity = 0.0
        except:
            # Fallback: simple variance ratio
            sensitivity = 0.1
        
        return sensitivity
    
    def _evaluate_predictive_utility(self, I: np.ndarray, labels: np.ndarray) -> float:
        """Evaluate how well I predicts labels."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        
        try:
            clf = LogisticRegression(max_iter=1000, random_state=self.seed)
            scores = cross_val_score(clf, I, labels, cv=min(5, len(labels)//2))
            return float(np.mean(scores))
        except:
            return 0.0
    
    def _compute_effective_rank(self, I: np.ndarray) -> int:
        """Compute effective rank via singular values."""
        U, s, Vt = np.linalg.svd(I, full_matrices=False)
        # Effective rank: number of singular values > 1% of max
        threshold = s[0] * 0.01
        return int(np.sum(s > threshold))
    
    def _compute_explained_variance(self, I: np.ndarray) -> float:
        """Compute variance explained by top components."""
        U, s, Vt = np.linalg.svd(I, full_matrices=False)
        total_var = np.sum(s**2)
        if total_var > 0:
            top_var = np.sum(s[:min(10, len(s))]**2)
            return float(top_var / total_var)
        return 0.0


class GenerationEvaluator:
    """Evaluate manifestation generation quality."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def evaluate(self,
                 generated: np.ndarray,
                 target: np.ndarray = None,
                 invariant_orig: np.ndarray = None,
                 invariant_gen: np.ndarray = None,
                 context: np.ndarray = None,
                 config_hash: str = "") -> GenerationMetrics:
        """Compute generation metrics."""
        
        # 1. Reconstruction quality
        if target is not None:
            reconstruction_mse = float(mean_squared_error(target, generated))
            reconstruction_mae = float(mean_absolute_error(target, generated))
        else:
            reconstruction_mse = 0.0
            reconstruction_mae = 0.0
        
        # 2. Invariant preservation
        if invariant_orig is not None and invariant_gen is not None:
            invariant_preservation = self._compute_invariant_preservation(invariant_orig, invariant_gen)
        else:
            invariant_preservation = 0.0
        
        # 3. Context response
        if context is not None:
            context_response = self._compute_context_response(generated, context)
        else:
            context_response = 0.0
        
        # 4. Diversity
        diversity_score = self._compute_diversity(generated)
        
        # 5. Novelty (if target available)
        if target is not None:
            novelty_score = self._compute_novelty(generated, target)
        else:
            novelty_score = 0.0
        
        # 6. Distribution similarity
        if target is not None:
            distribution_similarity = self._compute_distribution_similarity(generated, target)
        else:
            distribution_similarity = 0.0
        
        return GenerationMetrics(
            reconstruction_mse=reconstruction_mse,
            reconstruction_mae=reconstruction_mae,
            invariant_preservation=invariant_preservation,
            context_response=context_response,
            diversity_score=diversity_score,
            novelty_score=novelty_score,
            distribution_similarity=distribution_similarity,
            config_hash=config_hash
        )
    
    def _compute_invariant_preservation(self, I_orig: np.ndarray, I_gen: np.ndarray) -> float:
        """Compute correlation between original and generated invariants."""
        try:
            # Mean correlation across dimensions
            corrs = []
            for i in range(min(I_orig.shape[1], I_gen.shape[1])):
                r, _ = pearsonr(I_orig[:, i], I_gen[:, i])
                if not np.isnan(r):
                    corrs.append(abs(r))
            return float(np.mean(corrs)) if corrs else 0.0
        except:
            return 0.0
    
    def _compute_context_response(self, generated: np.ndarray, context: np.ndarray) -> float:
        """Compute how well generated observations respond to context."""
        # Train simple classifier to predict context from generated
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import cross_val_score
            
            if context.ndim == 1:
                context = context.reshape(-1, 1)
            
            # Use first few components
            X = generated[:, :min(50, generated.shape[1])]
            clf = LogisticRegression(max_iter=1000, random_state=self.seed)
            scores = cross_val_score(clf, X, context.ravel(), cv=3)
            return float(np.mean(scores))
        except:
            return 0.0
    
    def _compute_diversity(self, generated: np.ndarray) -> float:
        """Compute average pairwise distance (diversity)."""
        if len(generated) < 2:
            return 0.0
        
        # Sample for efficiency
        n_samples = min(100, len(generated))
        idx = self.rng.choice(len(generated), n_samples, replace=False)
        subset = generated[idx]
        
        # Pairwise distances
        from scipy.spatial.distance import pdist
        try:
            distances = pdist(subset, metric='euclidean')
            return float(np.mean(distances))
        except:
            return 0.0
    
    def _compute_novelty(self, generated: np.ndarray, target: np.ndarray) -> float:
        """Compute average distance to nearest training sample."""
        try:
            from scipy.spatial.distance import cdist
            
            n_samples = min(50, len(generated))
            idx_gen = self.rng.choice(len(generated), n_samples, replace=False)
            idx_tar = self.rng.choice(len(target), min(100, len(target)), replace=False)
            
            distances = cdist(generated[idx_gen], target[idx_tar], metric='euclidean')
            min_distances = np.min(distances, axis=1)
            return float(np.mean(min_distances))
        except:
            return 0.0
    
    def _compute_distribution_similarity(self, generated: np.ndarray, target: np.ndarray) -> float:
        """Compute distribution similarity (simplified MMD proxy)."""
        try:
            # Compare mean and covariance
            gen_mean = np.mean(generated, axis=0)
            tar_mean = np.mean(target, axis=0)
            gen_cov = np.cov(generated.T)
            tar_cov = np.cov(target.T)
            
            mean_diff = np.linalg.norm(gen_mean - tar_mean)
            cov_diff = np.linalg.norm(gen_cov - tar_cov)
            
            # Normalize and invert
            similarity = 1.0 / (1.0 + mean_diff + 0.1 * cov_diff)
            return float(similarity)
        except:
            return 0.0


class PipelineEvaluator:
    """Complete OIR-PPV pipeline evaluation."""
    
    def __init__(self, seed: int = 42):
        self.invariant_evaluator = InvariantEvaluator(seed)
        self.generation_evaluator = GenerationEvaluator(seed)
    
    def evaluate_pipeline(self,
                          observations: np.ndarray,
                          invariant_result: Any,
                          generation_result: Any,
                          context: np.ndarray = None,
                          nuisance: np.ndarray = None,
                          labels: np.ndarray = None,
                          target_observations: np.ndarray = None,
                          config_hash: str = "") -> PipelineEvaluationResult:
        """Evaluate complete pipeline."""
        from datetime import datetime
        
        # Extract invariants
        I_orig = invariant_result.invariant_representation
        I_gen = None
        
        # If we can extract invariant from generated
        if hasattr(invariant_result, 'extractor') and invariant_result.extractor:
            I_gen = invariant_result.extractor.extract(generation_result.generated_observations).invariant_representation
        
        # Evaluate invariant
        invariant_metrics = self.invariant_evaluator.evaluate(
            I_orig, context, nuisance, labels, config_hash
        )
        
        # Evaluate generation
        generation_metrics = self.generation_evaluator.evaluate(
            generation_result.generated_observations,
            target_observations,
            I_orig, I_gen, context, config_hash
        )
        
        # Overall score (weighted)
        overall_score = (
            0.3 * invariant_metrics.invariance_score +
            0.2 * invariant_metrics.predictive_utility +
            0.2 * generation_metrics.invariant_preservation +
            0.15 * generation_metrics.context_response +
            0.15 * generation_metrics.distribution_similarity
        )
        
        return PipelineEvaluationResult(
            invariant_metrics=invariant_metrics,
            generation_metrics=generation_metrics,
            overall_score=overall_score,
            timestamp=datetime.now().isoformat()
        )