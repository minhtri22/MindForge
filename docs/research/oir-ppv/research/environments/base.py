"""
OIR-PPV Base Environment Classes
Core abstractions for SCM-based environment generators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import yaml
import hashlib
import json
from pathlib import Path
from datetime import datetime


@dataclass
class EnvironmentConfig:
    """Parsed environment configuration."""
    family: str
    name: str
    version: str
    generation: Dict[str, Any]
    raw_config: Dict[str, Any]


@dataclass
class GeneratedData:
    """Container for generated environment data."""
    observations: np.ndarray  # Shape: (n_samples, n_features)
    labels: np.ndarray        # Shape: (n_samples,) or (n_samples, n_classes)
    metadata: Dict[str, Any]  # Additional info: context, nuisance, etc.
    splits: Dict[str, np.ndarray]  # train/val/test/ood indices
    config_hash: str
    seed: int
    timestamp: str


class BaseEnvironment(ABC):
    """Abstract base class for all OIR-PPV environments."""
    
    def __init__(self, config: EnvironmentConfig, seed: int = 42):
        self.config = config
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate environment-specific configuration."""
        pass
    
    @abstractmethod
    def generate(self) -> GeneratedData:
        """Generate complete dataset with splits."""
        pass
    
    @abstractmethod
    def get_intervention_targets(self) -> List[str]:
        """Return list of valid intervention target names."""
        pass
    
    @abstractmethod
    def intervene(self, data: GeneratedData, target: str, value: Any) -> GeneratedData:
        """Apply intervention do(target=value) and return counterfactual data."""
        pass
    
    def get_config_hash(self) -> str:
        """Compute hash of configuration for provenance."""
        content = json.dumps(self.config.raw_config, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()[:16]
    
    def _split_indices(self, n: int, train_ratio: float, val_ratio: float, test_ratio: float) -> Dict[str, np.ndarray]:
        """Create deterministic train/val/test splits."""
        indices = np.arange(n)
        self.rng.shuffle(indices)
        
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        n_test = int(n * test_ratio)
        
        return {
            "train": indices[:n_train],
            "val": indices[n_train:n_train + n_val],
            "test": indices[n_train + n_val:n_train + n_val + n_test],
            "ood": indices[n_train + n_val + n_test:]  # Remaining for OOD
        }


def load_environment_config(config_path: Path) -> EnvironmentConfig:
    """Load and parse environment configuration from YAML."""
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    env_section = raw_config.get("environment", raw_config)
    
    # Generation can be at root level or inside environment section
    generation = env_section.get("generation", raw_config.get("generation", {}))
    
    return EnvironmentConfig(
        family=env_section.get("family", "unknown"),
        name=env_section.get("name", "unknown"),
        version=env_section.get("version", "1.0"),
        generation=generation,
        raw_config=raw_config
    )


class EnvironmentRegistry:
    """Registry for environment generators."""
    
    _generators: Dict[str, type] = {}
    
    @classmethod
    def register(cls, family: str):
        """Decorator to register environment generator."""
        def decorator(generator_class: type):
            cls._generators[family] = generator_class
            return generator_class
        return decorator
    
    @classmethod
    def get(cls, family: str) -> type:
        """Get generator class by family name."""
        if family not in cls._generators:
            raise ValueError(f"Unknown environment family: {family}. Available: {list(cls._generators.keys())}")
        return cls._generators[family]
    
    @classmethod
    def create(cls, family: str, config: EnvironmentConfig, seed: int = 42) -> BaseEnvironment:
        """Create environment instance."""
        generator_class = cls.get(family)
        return generator_class(config, seed)
    
    @classmethod
    def list_families(cls) -> List[str]:
        """List all registered environment families."""
        return list(cls._generators.keys())
    
    @classmethod
    def create_from_config_path(cls, config_path: Path, seed: int = 42) -> BaseEnvironment:
        """Load config and create environment in one step."""
        config = load_environment_config(config_path)
        return cls.create(config.family, config, seed)