"""
Unit Tests for M3 Pipeline Interfaces
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest


class TestInvariantExtractor:
    """Tests for InvariantExtractor interface."""
    
    def test_placeholder_extractor_basic(self):
        """Test PlaceholderInvariantExtractor basic functionality."""
        from pipeline import PlaceholderInvariantExtractor, InvariantExtractionResult
        
        extractor = PlaceholderInvariantExtractor(invariant_dim=16, seed=42)
        
        # Create dummy observations
        n_samples = 100
        n_features = 50  # >= invariant_dim
        observations = np.random.randn(n_samples, n_features)
        
        result = extractor.extract(observations)
        
        assert isinstance(result, InvariantExtractionResult)
        assert result.invariant_representation.shape == (n_samples, 16)
        assert "method" in result.metadata
        assert result.metadata["invariant_dim"] == 16
        assert len(result.config_hash) == 16
    
    def test_placeholder_extractor_with_context(self):
        """Test extractor with context and labels."""
        from pipeline import PlaceholderInvariantExtractor
        
        extractor = PlaceholderInvariantExtractor(invariant_dim=10, seed=123)
        
        n_samples = 50
        n_features = 30  # >= invariant_dim
        observations = np.random.randn(n_samples, n_features)
        context = np.random.randn(n_samples, 5)
        labels = np.random.randint(0, 3, n_samples)
        
        result = extractor.extract(observations, context=context, labels=labels)
        
        assert result.invariant_representation.shape == (n_samples, 10)
    
    def test_config_hash_consistency(self):
        """Test config hash is deterministic."""
        from pipeline import PlaceholderInvariantExtractor
        
        ext1 = PlaceholderInvariantExtractor(invariant_dim=64, seed=42)
        ext2 = PlaceholderInvariantExtractor(invariant_dim=64, seed=42)
        
        assert ext1.get_config_hash() == ext2.get_config_hash()
    
    def test_different_configs_different_hash(self):
        """Test different configs produce different hashes."""
        from pipeline import PlaceholderInvariantExtractor
        
        ext1 = PlaceholderInvariantExtractor(invariant_dim=32, seed=42)
        ext2 = PlaceholderInvariantExtractor(invariant_dim=64, seed=42)
        
        assert ext1.get_config_hash() != ext2.get_config_hash()


class TestManifestationGenerator:
    """Tests for ManifestationGenerator interface."""
    
    def test_placeholder_generator_basic(self):
        """Test PlaceholderManifestationGenerator basic functionality."""
        from pipeline import PlaceholderManifestationGenerator, GenerationResult
        
        generator = PlaceholderManifestationGenerator(output_dim=10, seed=42)
        
        n_samples = 20
        invariant = np.random.randn(n_samples, 32)
        context = np.random.randn(n_samples, 5)
        nuisance = np.random.randn(n_samples, 3)
        
        result = generator.generate(invariant, context, nuisance)
        
        assert isinstance(result, GenerationResult)
        assert result.generated_observations.shape == (n_samples, 10)
        assert "method" in result.metadata
        assert result.metadata["input_shapes"]["invariant"] == (n_samples, 32)
        assert len(result.config_hash) == 16
    
    def test_config_hash_consistency(self):
        """Test config hash is deterministic."""
        from pipeline import PlaceholderManifestationGenerator
        
        gen1 = PlaceholderManifestationGenerator(output_dim=10, seed=42)
        gen2 = PlaceholderManifestationGenerator(output_dim=10, seed=42)
        
        assert gen1.get_config_hash() == gen2.get_config_hash()


class TestPipelineRunner:
    """Tests for complete PipelineRunner."""
    
    def test_pipeline_runner_basic(self):
        """Test PipelineRunner executes full pipeline."""
        from pipeline import (
            PlaceholderInvariantExtractor,
            PlaceholderManifestationGenerator,
            PipelineRunner
        )
        
        extractor = PlaceholderInvariantExtractor(invariant_dim=16, seed=42)
        generator = PlaceholderManifestationGenerator(output_dim=10, seed=123)
        runner = PipelineRunner(extractor, generator)
        
        n_samples = 30
        observations = np.random.randn(n_samples, 20)
        context = np.random.randn(n_samples, 5)
        nuisance = np.random.randn(n_samples, 3)
        labels = np.random.randint(0, 3, n_samples)
        
        result = runner.run(observations, context, nuisance, labels)
        
        assert "invariant_result" in result
        assert "generation_result" in result
        
        invariant_result = result["invariant_result"]
        generation_result = result["generation_result"]
        
        assert invariant_result.invariant_representation.shape == (n_samples, 16)
        assert generation_result.generated_observations.shape == (n_samples, 10)
    
    def test_pipeline_provenance(self):
        """Test pipeline preserves provenance through config hashes."""
        from pipeline import (
            PlaceholderInvariantExtractor,
            PlaceholderManifestationGenerator,
            PipelineRunner
        )
        
        extractor = PlaceholderInvariantExtractor(invariant_dim=8, seed=42)
        generator = PlaceholderManifestationGenerator(output_dim=10, seed=123)
        runner = PipelineRunner(extractor, generator)
        
        n_samples = 20
        observations = np.random.randn(n_samples, 20)
        context = np.random.randn(n_samples, 5)
        nuisance = np.random.randn(n_samples, 3)
        
        result = runner.run(observations, context, nuisance)
        
        invariant_hash = result["invariant_result"].config_hash
        generation_hash = result["generation_result"].config_hash
        
        # Hashes should be valid hex strings
        assert len(invariant_hash) == 16
        assert len(generation_hash) == 16
        assert all(c in '0123456789abcdef' for c in invariant_hash)
        assert all(c in '0123456789abcdef' for c in generation_hash)


class TestBenchmarkCompatibility:
    """Tests that M2 benchmarks still work after M3 additions."""
    
    def test_benchmark_runner_imports(self):
        """Test benchmark module imports correctly with M3 additions."""
        from benchmark import BenchmarkRunner, BaseBaseline, BenchmarkConfig
        from benchmark.baselines import B0_ERM, BASELINE_MAP
        
        assert BaseBaseline is not None
        assert len(BASELINE_MAP) == 6
    
    def test_m3_interfaces_importable(self):
        """Test M3 pipeline interfaces are importable."""
        from pipeline import (
            InvariantExtractor,
            ManifestationGenerator,
            PipelineRunner,
            PlaceholderInvariantExtractor,
            PlaceholderManifestationGenerator
        )
        
        assert InvariantExtractor is not None
        assert ManifestationGenerator is not None
        assert PipelineRunner is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])