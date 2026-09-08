"""
Environment package init - registers all generators.
"""

from .base import BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry, load_environment_config
from .env1_generator import Env1IdentityStyleShift
from .env2_generator import Env2CompositionalGeneration
from .env3_generator import Env3CausalDynamics
from .env4_generator import Env4AdversarialShortcut
from .seed_manifest import SeedManifest, ExecutionLogger, create_seed_manifest

__all__ = [
    "BaseEnvironment",
    "EnvironmentConfig", 
    "GeneratedData",
    "EnvironmentRegistry",
    "load_environment_config",
    "Env1IdentityStyleShift",
    "Env2CompositionalGeneration",
    "Env3CausalDynamics",
    "Env4AdversarialShortcut",
    "SeedManifest",
    "ExecutionLogger",
    "create_seed_manifest",
]

# Verify all families registered
_registered = EnvironmentRegistry.list_families()
_expected = ["ENV-1", "ENV-2", "ENV-3", "ENV-4"]
for exp in _expected:
    if exp not in _registered:
        raise RuntimeError(f"Environment {exp} not registered! Registered: {_registered}")