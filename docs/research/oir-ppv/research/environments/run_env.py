"""
Environment CLI Runner
Command-line interface for generating environment data.
"""

import argparse
import sys
from pathlib import Path
import time
import numpy as np

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import environments package to register generators
import environments

from environments.base import EnvironmentRegistry, load_environment_config
from environments.seed_manifest import create_seed_manifest, ExecutionLogger, SeedManifest


def generate_environment(args):
    """Generate environment data from config."""
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return 1
    
    # Load config
    config = load_environment_config(config_path)
    family = config.family
    
    # Create output directory
    output_dir = Path(args.output) / args.experiment_id / family
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create seed manifest
    env_configs = {family: config.raw_config}
    manifest = create_seed_manifest(args.experiment_id, args.seed, env_configs)
    env_seed = manifest.environment_seeds[family]
    
    # Create logger
    logger = ExecutionLogger(args.experiment_id, Path(args.output) / args.experiment_id / "logs")
    
    # Create environment
    print(f"Creating {family} environment with seed {env_seed}...")
    start_time = time.time()
    
    try:
        env = EnvironmentRegistry.create_from_config_path(config_path, env_seed)
        data = env.generate()
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log generation
        logger.log_generation(
            environment_family=family,
            seed=env_seed,
            config_hash=data.config_hash,
            data_shape=data.observations.shape,
            duration_ms=duration_ms,
            status="success",
            metadata={
                "n_samples": len(data.labels),
                "n_features": data.observations.shape[1],
                "splits": {k: len(v) for k, v in data.splits.items()}
            }
        )
        
        # Save data
        np.savez_compressed(
            output_dir / "data.npz",
            observations=data.observations,
            labels=data.labels,
            **{f"metadata_{k}": v for k, v in data.metadata.items() if isinstance(v, np.ndarray)}
        )
        
        # Save splits
        np.savez_compressed(
            output_dir / "splits.npz",
            **data.splits
        )
        
        # Save metadata (non-array)
        import json
        meta_json = {k: v.tolist() if isinstance(v, np.ndarray) else str(v) 
                     for k, v in data.metadata.items()}
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(meta_json, f, indent=2)
        
        # Save provenance
        provenance = {
            "experiment_id": args.experiment_id,
            "environment_family": family,
            "seed": env_seed,
            "config_hash": data.config_hash,
            "timestamp": data.timestamp,
            "n_samples": len(data.labels),
            "n_features": data.observations.shape[1],
            "splits": {k: len(v) for k, v in data.splits.items()},
            "intervention_targets": env.get_intervention_targets()
        }
        with open(output_dir / "provenance.json", 'w') as f:
            json.dump(provenance, f, indent=2)
        
        # Save seed manifest
        manifest.save(output_dir.parent / "seed_manifest.json")
        
        # Save execution log summary
        logger.save_summary(output_dir.parent / "logs" / "execution_summary.txt")
        
        print(f"✓ Generated {family}: {len(data.labels)} samples, {data.observations.shape[1]} features")
        print(f"  Splits: {', '.join(f'{k}={len(v)}' for k, v in data.splits.items())}")
        print(f"  Output: {output_dir}")
        print(f"  Duration: {duration_ms:.1f} ms")
        
        return 0
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_generation(
            environment_family=family,
            seed=env_seed,
            config_hash="",
            data_shape=(0, 0),
            duration_ms=duration_ms,
            status="failed",
            error=str(e)
        )
        print(f"✗ Failed to generate {family}: {e}")
        return 1


def intervene_environment(args):
    """Apply intervention to generated environment data."""
    config_path = Path(args.config)
    data_path = Path(args.data)
    
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return 1
    if not data_path.exists():
        print(f"Data not found: {data_path}")
        return 1
    
    config = load_environment_config(config_path)
    family = config.family
    
    # Load data
    data_npz = np.load(data_path / "data.npz")
    observations = data_npz["observations"]
    labels = data_npz["labels"]
    
    # Load metadata
    meta_npz = {k: data_npz[k] for k in data_npz.files if k.startswith("metadata_")}
    metadata = {k.replace("metadata_", ""): v for k, v in meta_npz.items()}
    
    # Load splits
    splits_npz = np.load(data_path / "splits.npz")
    splits = {k: splits_npz[k] for k in splits_npz.files}
    
    # Load provenance
    import json
    with open(data_path / "provenance.json", 'r') as f:
        provenance = json.load(f)
    
    # Reconstruct GeneratedData
    from base import GeneratedData
    data = GeneratedData(
        observations=observations,
        labels=labels,
        metadata=metadata,
        splits=splits,
        config_hash=provenance["config_hash"],
        seed=provenance["seed"],
        timestamp=provenance["timestamp"]
    )
    
    # Create environment
    env = EnvironmentRegistry.create_from_config_path(config_path, provenance["seed"])
    
    # Apply intervention
    print(f"Applying intervention do({args.target}={args.value})...")
    start_time = time.time()
    
    try:
        intervened_data = env.intervene(data, args.target, args.value)
        duration_ms = (time.time() - start_time) * 1000
        
        # Save intervened data
        output_dir = Path(args.output) / args.experiment_id / family / f"intervention_{args.target}_{args.value}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        np.savez_compressed(
            output_dir / "data.npz",
            observations=intervened_data.observations,
            labels=intervened_data.labels,
            **{f"metadata_{k}": v for k, v in intervened_data.metadata.items() if isinstance(v, np.ndarray)}
        )
        
        np.savez_compressed(
            output_dir / "splits.npz",
            **intervened_data.splits
        )
        
        print(f"✓ Intervention completed: {intervened_data.observations.shape}")
        print(f"  Output: {output_dir}")
        print(f"  Duration: {duration_ms:.1f} ms")
        
        return 0
        
    except Exception as e:
        print(f"✗ Intervention failed: {e}")
        return 1


def list_families(args):
    """List available environment families."""
    families = EnvironmentRegistry.list_families()
    print("Available environment families:")
    for f in families:
        print(f"  {f}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="OIR-PPV Environment Generator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate environment data")
    gen_parser.add_argument("--config", required=True, help="Path to environment config YAML")
    gen_parser.add_argument("--experiment-id", required=True, help="Experiment ID")
    gen_parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    gen_parser.add_argument("--output", default="artifacts/environments", help="Output directory")
    
    # Intervene command
    int_parser = subparsers.add_parser("intervene", help="Apply intervention to generated data")
    int_parser.add_argument("--config", required=True, help="Path to environment config YAML")
    int_parser.add_argument("--data", required=True, help="Path to generated data directory")
    int_parser.add_argument("--target", required=True, help="Intervention target (e.g., do(A))")
    int_parser.add_argument("--value", required=True, help="Intervention value")
    int_parser.add_argument("--experiment-id", required=True, help="Experiment ID")
    int_parser.add_argument("--output", default="artifacts/environments", help="Output directory")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available environment families")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        return generate_environment(args)
    elif args.command == "intervene":
        return intervene_environment(args)
    elif args.command == "list":
        return list_families(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())