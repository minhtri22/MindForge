"""
Unit tests for real learner implementations (AutoencoderEncoder, MLPDecoder).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from pipeline.learners import (
    AutoencoderEncoder,
    MLPDecoder,
    LearnerRegistry,
    create_learner_from_config,
    EncoderLearner,
    DecoderLearner,
)


class TestAutoencoderEncoder:
    """Tests for AutoencoderEncoder."""
    
    def test_construction(self):
        """Test encoder construction."""
        encoder = AutoencoderEncoder(output_dim=32, hidden_dim=64, learning_rate=0.01, epochs=10, seed=42)
        assert encoder.output_dim == 32
        assert encoder.hidden_dim == 64
        assert encoder.learning_rate == 0.01
        assert encoder.epochs == 10
        assert encoder.seed == 42
        assert not encoder._fitted
    
    def test_fit_and_encode(self):
        """Test fitting and encoding."""
        encoder = AutoencoderEncoder(output_dim=16, hidden_dim=32, learning_rate=0.01, epochs=20, seed=42)
        
        # Create synthetic data
        X = np.random.randn(100, 20).astype(float)
        
        # Fit
        result = encoder.fit(X)
        assert result["status"] == "fitted"
        assert encoder._fitted
        assert "final_loss" in result
        assert "loss_history_length" in result
        assert result["loss_history_length"] == 20
        
        # Encode
        I = encoder.encode(X[:10])
        assert I.shape == (10, 16)
    
    def test_encode_before_fit_raises(self):
        """Test that encoding before fitting raises an error."""
        encoder = AutoencoderEncoder(output_dim=16, hidden_dim=32, seed=42)
        with pytest.raises(RuntimeError, match="Encoder not fitted"):
            encoder.encode(np.random.randn(10, 20))
    
    def test_config_hash(self):
        """Test config hash is deterministic."""
        encoder1 = AutoencoderEncoder(output_dim=32, hidden_dim=64, learning_rate=0.01, epochs=10, seed=42)
        encoder2 = AutoencoderEncoder(output_dim=32, hidden_dim=64, learning_rate=0.01, epochs=10, seed=42)
        assert encoder1.get_config_hash() == encoder2.get_config_hash()
        
        encoder3 = AutoencoderEncoder(output_dim=16, hidden_dim=64, learning_rate=0.01, epochs=10, seed=42)
        assert encoder1.get_config_hash() != encoder3.get_config_hash()
    
    def test_registry_registration(self):
        """Test that Autoencoder is registered."""
        assert "Autoencoder" in LearnerRegistry.list_encoders()
        assert LearnerRegistry.get_encoder("Autoencoder") is AutoencoderEncoder
    
    def test_create_from_registry(self):
        """Test creating from registry via create_learner_from_config."""
        encoder = create_learner_from_config({
            "type": "Autoencoder",
            "output_dim": 16,
            "hidden_dim": 32,
            "learning_rate": 0.01,
            "epochs": 10
        }, "encoder", seed=42)
        assert isinstance(encoder, AutoencoderEncoder)


class TestMLPDecoder:
    """Tests for MLPDecoder."""
    
    def test_construction(self):
        """Test decoder construction."""
        decoder = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        assert decoder.output_dim == 10
        assert decoder.hidden_dims == [64, 32]
        assert decoder.learning_rate == 0.01
        assert decoder.epochs == 10
        assert decoder.seed == 42
        assert not decoder._fitted
    
    def test_fit_and_decode(self):
        """Test fitting and decoding."""
        decoder = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        
        # Create synthetic data
        I = np.random.randn(100, 32).astype(float)
        Z = np.random.randn(100, 5).astype(float)
        N = np.random.randn(100, 3).astype(float)
        targets = np.random.randn(100, 10).astype(float)
        
        # Fit
        result = decoder.fit(I, Z, N, targets)
        assert result["status"] == "fitted"
        assert decoder._fitted
        assert "final_loss" in result
        assert "architecture" in result
        assert result["architecture"] == [40, 64, 32, 10]  # 32+5+3=40 input, then hidden, then 10 output
        
        # Decode
        generated = decoder.decode(I[:10], Z[:10], N[:10])
        assert generated.shape == (10, 10)
    
    def test_decode_before_fit_raises(self):
        """Test that decoding before fitting raises RuntimeError."""
        decoder = MLPDecoder(output_dim=10, hidden_dims=[64, 32], seed=42)
        I = np.random.randn(10, 32)
        Z = np.random.randn(10, 5)
        N = np.random.randn(10, 3)
        with pytest.raises(RuntimeError, match="not fitted"):
            decoder.decode(I, Z, N)
    
    def test_config_hash(self):
        """Test config hash is deterministic."""
        decoder1 = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        decoder2 = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        assert decoder1.get_config_hash() == decoder2.get_config_hash()
        
        decoder3 = MLPDecoder(output_dim=5, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        assert decoder1.get_config_hash() != decoder3.get_config_hash()
    
    def test_registry_registration(self):
        """Test that MLPDecoder is registered."""
        assert "MLPDecoder" in LearnerRegistry.list_decoders()
        assert LearnerRegistry.get_decoder("MLPDecoder") is MLPDecoder
    
    def test_create_from_registry(self):
        """Test creating from registry via create_learner_from_config."""
        decoder = create_learner_from_config({
            "type": "MLPDecoder",
            "output_dim": 10,
            "hidden_dims": [64, 32],
            "learning_rate": 0.01,
            "epochs": 10
        }, "decoder", seed=42)
        assert isinstance(decoder, MLPDecoder)


class TestLearnerInterfaces:
    """Tests for learner interface contracts."""
    
    def test_autoencoder_implements_encoder_interface(self):
        """Test that AutoencoderEncoder implements EncoderLearner."""
        encoder = AutoencoderEncoder(output_dim=16, hidden_dim=32, seed=42)
        assert isinstance(encoder, EncoderLearner)
    
    def test_mlp_decoder_implements_decoder_interface(self):
        """Test that MLPDecoder implements DecoderLearner."""
        decoder = MLPDecoder(output_dim=10, hidden_dims=[64, 32], seed=42)
        assert isinstance(decoder, DecoderLearner)
    
    def test_unknown_encoder_raises(self):
        """Test that unknown encoder type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown encoder"):
            LearnerRegistry.get_encoder("NonExistent")
    
    def test_unknown_decoder_raises(self):
        """Test that unknown decoder type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown decoder"):
            LearnerRegistry.get_decoder("NonExistent")


class TestDeterministicOutput:
    """Tests for deterministic output with fixed seeds."""
    
    def test_autoencoder_deterministic(self):
        """Test AutoencoderEncoder produces deterministic output with fixed seed."""
        encoder1 = AutoencoderEncoder(output_dim=16, hidden_dim=32, learning_rate=0.01, epochs=10, seed=42)
        encoder2 = AutoencoderEncoder(output_dim=16, hidden_dim=32, learning_rate=0.01, epochs=10, seed=42)
        
        X = np.random.randn(100, 20).astype(float)
        encoder1.fit(X)
        encoder2.fit(X)
        
        I1 = encoder1.encode(X[:10])
        I2 = encoder2.encode(X[:10])
        
        np.testing.assert_allclose(I1, I2, rtol=1e-6)
    
    def test_decoder_deterministic(self):
        """Test MLPDecoder produces deterministic output with fixed seed."""
        # Use same data for both decoders
        I = np.random.randn(100, 32)
        Z = np.random.randn(100, 5)
        N = np.random.randn(100, 3)
        targets = np.random.randn(100, 10)
        
        decoder1 = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        decoder2 = MLPDecoder(output_dim=10, hidden_dims=[64, 32], learning_rate=0.01, epochs=10, seed=42)
        
        decoder1.fit(I, Z, N, targets)
        decoder2.fit(I, Z, N, targets)
        
        gen1 = decoder1.decode(I[:10], Z[:10], N[:10])
        gen2 = decoder2.decode(I[:10], Z[:10], N[:10])
        
        np.testing.assert_allclose(gen1, gen2, rtol=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])