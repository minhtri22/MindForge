"""
M3: Context/Nuisance Dependency Analysis
Sensitivity evaluation for context and nuisance variables.
Leakage detection and shortcut learning indicators.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import cross_val_score
import hashlib
import json
from pathlib import Path
from datetime import datetime


@dataclass
class SensitivityResult:
    """Sensitivity analysis result for one variable."""
    variable_name: str
    variable_type: str          # "context" or "nuisance"
    
    # Linear sensitivity (canonical correlation)
    linear_sensitivity: float
    
    # Nonlinear sensitivity (mutual information)
    mi_sensitivity: float
    
    # Predictability (can we predict I from this variable?)
    predictability_r2: float
    
    # Leakage indicator (0 = no leakage, 1 = full leakage)
    leakage_score: float
    
    # Per-dimension breakdown
    per_dim_sensitivity: Dict[int, float]


@dataclass
class DependencyAnalysisResult:
    """Complete dependency analysis result."""
    extractor_type: str
    extractor_config_hash: str
    environment: str
    seed: int
    
    # Results by variable type
    context_sensitivities: List[SensitivityResult]
    nuisance_sensitivities: List[SensitivityResult]
    
    # Summary
    max_context_sensitivity: float
    max_nuisance_sensitivity: float
    avg_context_sensitivity: float
    avg_nuisance_sensitivity: float
    
    # Leakage flags
    context_leakage_detected: bool
    nuisance_leakage_detected: bool
    
    # Shortcut learning indicator
    shortcut_learning_score: float
    shortcut_metric_status: str
    nan_policy: str
    
    # Provenance
    timestamp: str
    config_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        import dataclasses
        return dataclasses.asdict(self)


class DependencyAnalyzer:
    """Analyzes context/nuisance dependencies in invariant representations."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def analyze(self,
                invariant_representation: np.ndarray,
                context: np.ndarray,
                nuisance: np.ndarray,
                context_names: List[str] = None,
                nuisance_names: List[str] = None,
                config_hash: str = "") -> DependencyAnalysisResult:
        """
        Analyze dependencies between invariant representation and context/nuisance.
        
        Args:
            invariant_representation: I (n_samples, invariant_dim)
            context: Context variables Z (n_samples, n_context) or (n_samples,)
            nuisance: Nuisance variables N (n_samples, n_nuisance) or (n_samples,)
            context_names: Optional names for context variables
            nuisance_names: Optional names for nuisance variables
            config_hash: Configuration hash for provenance
            
        Returns:
            DependencyAnalysisResult with sensitivity metrics
        """
        # Ensure 2D
        if context.ndim == 1:
            context = context.reshape(-1, 1)
        if nuisance.ndim == 1:
            nuisance = nuisance.reshape(-1, 1)
        
        n_context_vars = context.shape[1]
        n_nuisance_vars = nuisance.shape[1]
        
        context_names = context_names or [f"context_{i}" for i in range(n_context_vars)]
        nuisance_names = nuisance_names or [f"nuisance_{i}" for i in range(n_nuisance_vars)]
        
        context_results = []
        nuisance_results = []
        
        # Analyze context variables
        for i in range(n_context_vars):
            var_context = context[:, i:i+1]
            result = self._analyze_variable(
                invariant_representation, var_context, context_names[i], "context"
            )
            context_results.append(result)
        
        # Analyze nuisance variables
        for i in range(n_nuisance_vars):
            var_nuisance = nuisance[:, i:i+1]
            result = self._analyze_variable(
                invariant_representation, var_nuisance, nuisance_names[i], "nuisance"
            )
            nuisance_results.append(result)
        
        # Summary metrics
        max_context_sens = max([r.linear_sensitivity for r in context_results]) if context_results else 0.0
        max_nuisance_sens = max([r.linear_sensitivity for r in nuisance_results]) if nuisance_results else 0.0
        avg_context_sens = np.mean([r.linear_sensitivity for r in context_results]) if context_results else 0.0
        avg_nuisance_sens = np.mean([r.linear_sensitivity for r in nuisance_results]) if nuisance_results else 0.0
        
        # Leakage detection
        context_leakage = max_context_sens > 0.3  # Threshold
        nuisance_leakage = max_nuisance_sens > 0.3
        
        # Shortcut learning indicator: high nuisance sensitivity + high context sensitivity
        shortcut_score = (max_nuisance_sens + max_context_sens) / 2
        
        return DependencyAnalysisResult(
            extractor_type="extractor",
            extractor_config_hash=config_hash,
            environment="env",
            seed=self.seed,
            context_sensitivities=context_results,
            nuisance_sensitivities=nuisance_results,
            max_context_sensitivity=max_context_sens,
            max_nuisance_sensitivity=max_nuisance_sens,
            avg_context_sensitivity=avg_context_sens,
            avg_nuisance_sensitivity=avg_nuisance_sens,
            context_leakage_detected=context_leakage,
            nuisance_leakage_detected=nuisance_leakage,
            shortcut_learning_score=shortcut_score,
            shortcut_metric_status="valid" if np.isfinite(shortcut_score) else "null",
            nan_policy="non-finite component metrics are replaced with 0.0 and reported as finite summaries",
            timestamp=datetime.now().isoformat(),
            config_hash=config_hash
        )
    
    def _analyze_variable(self,
                          I: np.ndarray,
                          variable: np.ndarray,
                          name: str,
                          var_type: str) -> SensitivityResult:
        """Analyze sensitivity to a single variable."""
        
        # 1. Linear sensitivity (CCA-like)
        linear_sens = self._linear_sensitivity(I, variable)
        
        # 2. Mutual information sensitivity
        mi_sens = self._mi_sensitivity(I, variable)
        
        # 3. Predictability (R^2)
        predict_r2 = self._predictability(I, variable)
        
        # 4. Per-dimension sensitivity
        per_dim = {}
        for dim in range(I.shape[1]):
            try:
                r, _ = pearsonr(I[:, dim], variable.ravel())
                per_dim[dim] = abs(r) if not np.isnan(r) else 0.0
            except:
                per_dim[dim] = 0.0
        
        # Leakage score: max of normalized sensitivities
        leakage = max(linear_sens, mi_sens, predict_r2)
        
        return SensitivityResult(
            variable_name=name,
            variable_type=var_type,
            linear_sensitivity=linear_sens,
            mi_sensitivity=mi_sens,
            predictability_r2=predict_r2,
            leakage_score=leakage,
            per_dim_sensitivity=per_dim
        )
    
    def _linear_sensitivity(self, I: np.ndarray, V: np.ndarray) -> float:
        """Linear sensitivity via canonical correlation approximation."""
        try:
            # Center
            I_centered = I - I.mean(axis=0)
            V_centered = V - V.mean()
            
            # Correlation
            corr = np.abs(np.corrcoef(I_centered.T, V_centered.ravel()))
            n_i = I.shape[1]
            if n_i < corr.shape[0]:
                cross_corr = corr[:n_i, n_i]
                finite = np.abs(cross_corr[np.isfinite(cross_corr)])
                return float(np.mean(finite)) if len(finite) else 0.0
        except:
            pass
        return 0.0
    
    def _mi_sensitivity(self, I: np.ndarray, V: np.ndarray) -> float:
        """Mutual information sensitivity (normalized)."""
        try:
            mi = mutual_info_regression(I, V.ravel(), random_state=self.seed)
            # Normalize by entropy of V
            from scipy.stats import entropy
            v_discrete = np.digitize(V.ravel(), bins=10)
            h_v = entropy(np.bincount(v_discrete))
            if h_v > 0:
                value = float(np.mean(mi) / h_v)
                return value if np.isfinite(value) else 0.0
        except:
            pass
        return 0.0
    
    def _predictability(self, I: np.ndarray, V: np.ndarray) -> float:
        """Predictability of I from V (R^2)."""
        try:
            reg = LinearRegression()
            reg.fit(V, I)
            r2 = reg.score(V, I)
            return float(max(0.0, r2)) if np.isfinite(r2) else 0.0
        except:
            return 0.0


def run_dependency_analysis(
    invariant_representation: np.ndarray,
    context: np.ndarray,
    nuisance: np.ndarray,
    output_dir: Path,
    config_hash: str = "",
    seed: int = 42
) -> DependencyAnalysisResult:
    """Run complete dependency analysis."""
    analyzer = DependencyAnalyzer(seed)
    result = analyzer.analyze(
        invariant_representation=invariant_representation,
        context=context,
        nuisance=nuisance,
        config_hash=config_hash
    )
    
    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "dependency_analysis.json", 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    print(f"Dependency Analysis Results:")
    print(f"  Max Context Sensitivity: {result.max_context_sensitivity:.4f}")
    print(f"  Max Nuisance Sensitivity: {result.max_nuisance_sensitivity:.4f}")
    print(f"  Context Leakage: {result.context_leakage_detected}")
    print(f"  Nuisance Leakage: {result.nuisance_leakage_detected}")
    print(f"  Shortcut Score: {result.shortcut_learning_score:.4f}")
    
    return result
