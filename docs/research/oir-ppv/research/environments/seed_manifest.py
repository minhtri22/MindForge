"""
Seed Manifest & Execution Log System
Provenance tracking for environment generation.
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import numpy as np


@dataclass
class SeedManifest:
    """Manifest tracking all seeds used in an experiment."""
    experiment_id: str
    base_seed: int
    environment_seeds: Dict[str, int]  # family -> seed
    split_seeds: Dict[str, int]      # split_name -> seed
    generator_versions: Dict[str, str]  # family -> version
    timestamp: str
    config_hashes: Dict[str, str]    # family -> config hash
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SeedManifest':
        return cls(**data)
    
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'SeedManifest':
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


@dataclass
class ExecutionLogEntry:
    """Single execution log entry."""
    timestamp: str
    experiment_id: str
    environment_family: str
    action: str  # "generate", "intervene", "validate"
    seed: int
    config_hash: str
    input_shape: tuple
    output_shape: tuple
    duration_ms: float
    status: str  # "success", "failed"
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class ExecutionLogger:
    """Logger for environment generation executions."""
    
    def __init__(self, experiment_id: str, log_dir: Path):
        self.experiment_id = experiment_id
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / f"{experiment_id}_execution_log.jsonl"
        self.entries: List[ExecutionLogEntry] = []
    
    def log(self, entry: ExecutionLogEntry) -> None:
        self.entries.append(entry)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry.__dict__) + '\n')
    
    def log_generation(self, environment_family: str, seed: int, config_hash: str,
                       data_shape: tuple, duration_ms: float, status: str = "success",
                       error: str = None, metadata: Dict = None) -> None:
        entry = ExecutionLogEntry(
            timestamp=datetime.now().isoformat(),
            experiment_id=self.experiment_id,
            environment_family=environment_family,
            action="generate",
            seed=seed,
            config_hash=config_hash,
            input_shape=(0,),  # No input for generation
            output_shape=data_shape,
            duration_ms=duration_ms,
            status=status,
            error=error,
            metadata=metadata or {}
        )
        self.log(entry)
    
    def log_intervention(self, environment_family: str, seed: int, config_hash: str,
                         input_shape: tuple, output_shape: tuple, duration_ms: float,
                         target: str, value: Any, status: str = "success",
                         error: str = None) -> None:
        entry = ExecutionLogEntry(
            timestamp=datetime.now().isoformat(),
            experiment_id=self.experiment_id,
            environment_family=environment_family,
            action="intervene",
            seed=seed,
            config_hash=config_hash,
            input_shape=input_shape,
            output_shape=output_shape,
            duration_ms=duration_ms,
            status=status,
            error=error,
            metadata={"target": target, "value": str(value)}
        )
        self.log(entry)
    
    def get_logs(self) -> List[ExecutionLogEntry]:
        return self.entries
    
    def save_summary(self, path: Path) -> None:
        """Save human-readable summary."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(f"Execution Log Summary: {self.experiment_id}\n")
            f.write("=" * 60 + "\n\n")
            for entry in self.entries:
                f.write(f"[{entry.timestamp}] {entry.environment_family} - {entry.action}\n")
                f.write(f"  Seed: {entry.seed}\n")
                f.write(f"  Config Hash: {entry.config_hash}\n")
                f.write(f"  Output Shape: {entry.output_shape}\n")
                f.write(f"  Duration: {entry.duration_ms:.2f} ms\n")
                f.write(f"  Status: {entry.status}\n")
                if entry.error:
                    f.write(f"  Error: {entry.error}\n")
                if entry.metadata:
                    f.write(f"  Metadata: {entry.metadata}\n")
                f.write("\n")


def create_seed_manifest(experiment_id: str, base_seed: int,
                         environment_configs: Dict[str, Any]) -> SeedManifest:
    """Create seed manifest from experiment configuration."""
    # Derive environment seeds from base seed
    rng = np.random.default_rng(base_seed)
    
    environment_seeds = {}
    config_hashes = {}
    generator_versions = {}
    
    for family, config in environment_configs.items():
        env_seed = rng.integers(0, 2**32 - 1)
        environment_seeds[family] = int(env_seed)
        
        # Compute config hash
        import json
        content = json.dumps(config, sort_keys=True).encode()
        config_hashes[family] = hashlib.sha256(content).hexdigest()[:16]
        
        generator_versions[family] = "1.0"
    
    # Split seeds
    split_seeds = {
        "train": int(rng.integers(0, 2**32 - 1)),
        "val": int(rng.integers(0, 2**32 - 1)),
        "test": int(rng.integers(0, 2**32 - 1)),
        "ood": int(rng.integers(0, 2**32 - 1))
    }
    
    return SeedManifest(
        experiment_id=experiment_id,
        base_seed=base_seed,
        environment_seeds=environment_seeds,
        split_seeds=split_seeds,
        generator_versions=generator_versions,
        timestamp=datetime.now().isoformat(),
        config_hashes=config_hashes
    )