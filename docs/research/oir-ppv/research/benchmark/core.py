"""
Benchmark Core Framework
Core abstractions for OIR-PPV baseline benchmark suite.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import hashlib
from datetime import datetime


@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""
    experiment_id: str
    environment_family: str
    environment_config_path: str
    baseline_id: str
    baseline_config_path: str
    seed: int
    output_dir: str
    splits: List[str] = field(default_factory=lambda: ["train", "val", "test", "ood"])
    intervention_targets: List[str] = field(default_factory=list)
    counterfactual_enabled: bool = False


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    experiment_id: str
    environment_family: str
    baseline_id: str
    seed: int
    config_hashes: Dict[str, str]
    
    # Generalization metrics
    generalization: Dict[str, float] = field(default_factory=dict)
    
    # Intervention stability metrics
    intervention_stability: Dict[str, float] = field(default_factory=dict)
    
    # Generation quality metrics
    generation_quality: Dict[str, float] = field(default_factory=dict)
    
    # Counterfactual metrics
    counterfactual: Dict[str, float] = field(default_factory=dict)
    
    # Limitation metadata (for QA transparency)
    limitations: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    train_time_ms: float = 0.0
    eval_time_ms: float = 0.0
    intervention_time_ms: float = 0.0
    
    # Status
    status: str = "success"
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseBaseline(ABC):
    """Abstract base class for all baselines B0-B5."""
    
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.config = config
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.is_trained = False
        self._validate_config()
        self._feature_encoder = None
    
    def _preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """Preprocess data to numeric format."""
        if data.dtype.kind in 'SU':  # string/unicode
            # Convert string categorical to numeric
            return self._encode_categorical(data)
        return data.astype(float)
    
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
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate baseline-specific configuration."""
        pass
    
    @abstractmethod
    def train(self, train_data: np.ndarray, train_labels: np.ndarray, 
              val_data: np.ndarray = None, val_labels: np.ndarray = None,
              metadata: Dict = None) -> Dict[str, Any]:
        """Train the baseline on training data."""
        pass
    
    @abstractmethod
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict labels for data."""
        pass
    
    @abstractmethod
    def get_invariant_representation(self, data: np.ndarray) -> np.ndarray:
        """Extract invariant representation I from data."""
        pass
    
    def predict_proba(self, data: np.ndarray) -> np.ndarray:
        """Predict class probabilities (for AUROC). Override if supported."""
        preds = self.predict(data)
        if len(preds) == 0:
            return np.zeros((0, 2))
        
        # Handle case where preds might have max class >= n_classes
        n_classes = max(len(np.unique(preds)), int(preds.max()) + 1, 2)
        proba = np.zeros((len(preds), n_classes))
        valid_mask = preds < n_classes
        if np.any(valid_mask):
            proba[np.arange(len(preds))[valid_mask], preds[valid_mask]] = 1.0
        return proba
    
    def evaluate_generalization(self, test_data: np.ndarray, test_labels: np.ndarray,
                                metadata: Dict = None) -> Dict[str, float]:
        """Evaluate generalization on test data."""
        preds = self.predict(test_data)
        proba = self.predict_proba(test_data)
        return self._compute_classification_metrics(test_labels, preds, proba)
    
    def evaluate_intervention_stability(self, env, test_data: np.ndarray, 
                                        test_labels: np.ndarray,
                                        metadata: Dict = None) -> Dict[str, float]:
        """Evaluate intervention stability (to be implemented by baselines with intervention support)."""
        return {}
    
    def evaluate_generation_quality(self, env, test_data: np.ndarray = None) -> Dict[str, float]:
        """Evaluate generation quality (to be implemented by baselines with generator)."""
        return {}
    
    def evaluate_counterfactual(self, env, test_data: np.ndarray, 
                                test_labels: np.ndarray,
                                metadata: Dict = None) -> Dict[str, float]:
        """Evaluate counterfactual accuracy (to be implemented)."""
        return {}
    
    def get_limitations(self) -> Dict[str, Any]:
        """Return known limitations of this baseline implementation."""
        return {
            "implementation": "placeholder",
            "notes": "Override in subclass"
        }
    
    def _compute_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                                        y_proba: np.ndarray = None) -> Dict[str, float]:
        """Compute standard classification metrics."""
        from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
        
        metrics = {}
        metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
        metrics["f1_macro"] = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        metrics["f1_micro"] = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
        
        # AUC for binary/multiclass - use probabilities if available
        try:
            if y_proba is not None:
                if len(np.unique(y_true)) == 2:
                    metrics["auroc"] = float(roc_auc_score(y_true, y_proba[:, 1]))
                else:
                    metrics["auroc"] = float(roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro"))
            else:
                if len(np.unique(y_true)) == 2:
                    metrics["auroc"] = float(roc_auc_score(y_true, y_pred))
                else:
                    metrics["auroc"] = float(roc_auc_score(y_true, y_pred, multi_class="ovr", average="macro"))
        except:
            metrics["auroc"] = 0.0
        
        return metrics
    
    def get_config_hash(self) -> str:
        """Compute config hash for provenance."""
        import json
        content = json.dumps(self.config, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()[:16]


class BenchmarkRunner:
    """Orchestrates benchmark execution across environments and baselines."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []
    
    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run single benchmark configuration."""
        import time
        start_time = time.time()
        
        try:
            # Load environment
            from environments import EnvironmentRegistry
            env = EnvironmentRegistry.create_from_config_path(
                config.environment_config_path, config.seed
            )
            env_data = env.generate()
            
            # Load baseline
            baseline = self._create_baseline(config.baseline_id, config.baseline_config_path, config.seed)
            
            # Get splits
            train_idx = env_data.splits["train"]
            val_idx = env_data.splits["val"]
            test_idx = env_data.splits["test"]
            
            train_data = baseline._preprocess_data(env_data.observations[train_idx])
            train_labels = env_data.labels[train_idx]
            val_data = baseline._preprocess_data(env_data.observations[val_idx])
            val_labels = env_data.labels[val_idx]
            test_data = baseline._preprocess_data(env_data.observations[test_idx])
            test_labels = env_data.labels[test_idx]
            
            # Train
            train_start = time.time()
            train_info = baseline.train(train_data, train_labels, val_data, val_labels, env_data.metadata)
            train_time_ms = (time.time() - train_start) * 1000
            
            # Evaluate generalization
            eval_start = time.time()
            gen_metrics = baseline.evaluate_generalization(test_data, test_labels, env_data.metadata)
            eval_time_ms = (time.time() - eval_start) * 1000
            
            # Evaluate intervention stability
            int_metrics = {}
            if config.intervention_targets:
                int_start = time.time()
                int_metrics = baseline.evaluate_intervention_stability(env, test_data, test_labels, env_data.metadata)
                intervention_time_ms = (time.time() - int_start) * 1000
            else:
                intervention_time_ms = 0.0
            
            # Evaluate generation quality
            gen_quality = {}
            if hasattr(baseline, 'evaluate_generation_quality'):
                gen_quality = baseline.evaluate_generation_quality(env, test_data)
            
            # Evaluate counterfactual
            counter_metrics = {}
            if config.counterfactual_enabled:
                counter_start = time.time()
                counter_metrics = baseline.evaluate_counterfactual(env, test_data, test_labels, env_data.metadata)
                intervention_time_ms += (time.time() - counter_start) * 1000
            
            # Get limitations
            limitations = baseline.get_limitations()
            
            # Create result
            result = BenchmarkResult(
                experiment_id=config.experiment_id,
                environment_family=config.environment_family,
                baseline_id=config.baseline_id,
                seed=config.seed,
                config_hashes={
                    "environment": env.get_config_hash(),
                    "baseline": baseline.get_config_hash()
                },
                generalization=gen_metrics,
                intervention_stability=int_metrics,
                generation_quality=gen_quality,
                counterfactual=counter_metrics,
                limitations=limitations,
                train_time_ms=train_time_ms,
                eval_time_ms=eval_time_ms,
                intervention_time_ms=intervention_time_ms,
                status="success"
            )
            
        except Exception as e:
            result = BenchmarkResult(
                experiment_id=config.experiment_id,
                environment_family=config.environment_family,
                baseline_id=config.baseline_id,
                seed=config.seed,
                config_hashes={},
                status="failed",
                error=str(e)
            )
        
        self.results.append(result)
        self._save_result(result)
        return result
    
    def _create_baseline(self, baseline_id: str, config_path: str, seed: int) -> BaseBaseline:
        """Create baseline instance from ID and config path."""
        import yaml
        with open(config_path, 'r') as f:
            baseline_config = yaml.safe_load(f)
        
        # Map baseline IDs to classes
        baseline_map = {
            "B0": "B0_ERM",
            "B1": "B1_DomainGeneralization",
            "B2": "B2_EncoderRepresentation",
            "B3": "B3_InvariantOnly",
            "B4": "B4_OIR_PPV",
            "B5": "B5_OracleInvariant"
        }
        
        if baseline_id not in baseline_map:
            raise ValueError(f"Unknown baseline: {baseline_id}")
        
        class_name = baseline_map[baseline_id]
        # Import dynamically
        module = __import__(f"benchmark.baselines.{baseline_id.lower()}", fromlist=[class_name])
        baseline_class = getattr(module, class_name)
        
        return baseline_class(baseline_config.get("baseline", {}), seed)
    
    def _save_result(self, result: BenchmarkResult) -> None:
        """Save benchmark result to disk."""
        result_dir = self.output_dir / result.experiment_id
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON - use dataclass asdict for completeness
        import dataclasses
        result_dict = dataclasses.asdict(result)
        
        with open(result_dir / "result.json", 'w') as f:
            json.dump(result_dict, f, indent=2)
    
    def run_suite(self, configs: List[BenchmarkConfig]) -> List[BenchmarkResult]:
        """Run multiple benchmark configurations."""
        for config in configs:
            print(f"Running {config.experiment_id}: {config.environment_family} + {config.baseline_id}")
            self.run_benchmark(config)
        
        # Save summary
        self._save_summary()
        return self.results
    
    def _save_summary(self) -> None:
        """Save benchmark suite summary."""
        summary = {
            "total_runs": len(self.results),
            "successful": sum(1 for r in self.results if r.status == "success"),
            "failed": sum(1 for r in self.results if r.status == "failed"),
            "results": [
                {
                    "experiment_id": r.experiment_id,
                    "environment": r.environment_family,
                    "baseline": r.baseline_id,
                    "seed": r.seed,
                    "status": r.status,
                    "generalization": r.generalization,
                    "intervention_stability": r.intervention_stability,
                    "generation_quality": r.generation_quality
                }
                for r in self.results
            ]
        }
        
        with open(self.output_dir / "benchmark_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nBenchmark suite completed: {summary['successful']}/{summary['total_runs']} successful")


# Compatibility function for existing experiment runner
def run_baseline_experiment(experiment_id: str, environment_config: str, 
                           baseline_config: str, baseline_id: str,
                           seed: int = 42, output_dir: str = "artifacts/experiments") -> BenchmarkResult:
    """Run single baseline experiment (compatible with existing API)."""
    from environments import load_environment_config
    
    env_config = load_environment_config(Path(environment_config))
    
    config = BenchmarkConfig(
        experiment_id=experiment_id,
        environment_family=env_config.family,
        environment_config_path=environment_config,
        baseline_id=baseline_id,
        baseline_config_path=baseline_config,
        seed=seed,
        output_dir=output_dir
    )
    
    runner = BenchmarkRunner(Path(output_dir))
    return runner.run_benchmark(config)