"""
Unit Tests for M2 Benchmark Framework (Post-QA Corrections)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest


class TestBenchmarkCore:
    """Tests for Benchmark Core Framework."""
    
    def test_base_baseline_has_limitations(self):
        """Test BaseBaseline has get_limitations method."""
        from benchmark.core import BaseBaseline
        from benchmark.baselines import B0_ERM
        
        baseline = B0_ERM({}, seed=42)
        limitations = baseline.get_limitations()
        
        assert isinstance(limitations, dict)
        assert "implementation" in limitations
    
    def test_base_baseline_predict_proba(self):
        """Test BaseBaseline has predict_proba method."""
        from benchmark.baselines import B0_ERM
        
        baseline = B0_ERM({}, seed=42)
        baseline.is_trained = True
        baseline.train_labels = np.array([0, 1, 2, 0, 1])
        baseline.class_priors = np.array([0.4, 0.4, 0.2])
        
        # Mock train_data for KNN
        baseline.train_data = np.random.randn(5, 10)
        
        proba = baseline.predict_proba(np.random.randn(3, 10))
        
        # Base class implementation: n_classes derived from preds
        assert proba.shape[0] == 3  # n_samples
        assert proba.shape[1] >= 2  # at least 2 classes
        assert np.allclose(proba.sum(axis=1), 1.0)
    
    def test_benchmark_result_has_limitations_field(self):
        """Test BenchmarkResult dataclass has limitations field."""
        from benchmark.core import BenchmarkResult
        
        result = BenchmarkResult(
            experiment_id="TEST",
            environment_family="ENV-1",
            baseline_id="B0",
            seed=42,
            config_hashes={}
        )
        
        assert hasattr(result, 'limitations')
        assert result.limitations == {}
    
    def test_benchmark_result_has_counterfactual_field(self):
        """Test BenchmarkResult dataclass has counterfactual field."""
        from benchmark.core import BenchmarkResult
        
        result = BenchmarkResult(
            experiment_id="TEST",
            environment_family="ENV-1",
            baseline_id="B0",
            seed=42,
            config_hashes={}
        )
        
        assert hasattr(result, 'counterfactual')
        assert result.counterfactual == {}


class TestBaselineLimitations:
    """Tests for baseline-specific limitations."""
    
    def test_b0_limitations(self):
        from benchmark.baselines import B0_ERM
        baseline = B0_ERM({}, seed=42)
        lim = baseline.get_limitations()
        assert lim["implementation"] == "placeholder"
        assert "KNN" in lim["notes"] or "memorization" in lim["notes"]
    
    def test_b3_limitations(self):
        from benchmark.baselines import B3_InvariantOnly
        baseline = B3_InvariantOnly({}, seed=42)
        lim = baseline.get_limitations()
        assert lim["implementation"] == "placeholder"
        assert "PCA" in lim["notes"]
    
    def test_b4_limitations(self):
        from benchmark.baselines import B4_OIR_PPV
        baseline = B4_OIR_PPV({}, seed=42)
        lim = baseline.get_limitations()
        assert lim["implementation"] == "placeholder"
        assert "generator" in lim["notes"]
    
    def test_b5_limitations(self):
        from benchmark.baselines import B5_OracleInvariant
        baseline = B5_OracleInvariant({}, seed=42)
        lim = baseline.get_limitations()
        assert lim["implementation"] == "oracle"
        assert "upper bound" in lim["notes"].lower()


class TestMetricCollection:
    """Tests for metric collection improvements."""
    
    def test_compute_classification_metrics_with_proba(self):
        """Test _compute_classification_metrics accepts probabilities."""
        from benchmark.baselines import B0_ERM
        
        baseline = B0_ERM({}, seed=42)
        
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 1, 2])
        y_proba = np.eye(3)[y_true]
        
        metrics = baseline._compute_classification_metrics(y_true, y_pred, y_proba)
        
        assert "accuracy" in metrics
        assert "f1_macro" in metrics
        assert "auroc" in metrics
        assert metrics["accuracy"] == 1.0
    
    def test_auroc_with_probabilities(self):
        """Test AUROC computation uses probabilities when provided."""
        from benchmark.baselines import B0_ERM
        
        baseline = B0_ERM({}, seed=42)
        
        # Binary case
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 0, 1, 1])
        y_proba = np.array([[0.9, 0.1], [0.8, 0.2], [0.3, 0.7], [0.2, 0.8]])
        
        metrics = baseline._compute_classification_metrics(y_true, y_pred, y_proba)
        
        assert metrics["auroc"] > 0.5  # Should be high for perfect separation


class TestProvenanceIntegrity:
    """Tests for provenance tracking integrity."""
    
    def test_environment_config_hash(self):
        """Test environment config hash is computed."""
        from environments import EnvironmentRegistry
        
        env = EnvironmentRegistry.create_from_config_path(
            'environments/env1_config.yaml', 42
        )
        hash_val = env.get_config_hash()
        
        assert isinstance(hash_val, str)
        assert len(hash_val) == 16
    
    def test_baseline_config_hash(self):
        """Test baseline config hash is computed."""
        from benchmark.baselines import B0_ERM
        
        baseline = B0_ERM({"test_param": "value"}, seed=42)
        hash_val = baseline.get_config_hash()
        
        assert isinstance(hash_val, str)
        assert len(hash_val) == 16


if __name__ == "__main__":
    pytest.main([__file__, "-v"])