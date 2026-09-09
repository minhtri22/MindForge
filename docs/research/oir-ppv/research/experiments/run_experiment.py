#!/usr/bin/env python3
"""
OIR-PPV Experiment Runner Skeleton
Minimal runnable configuration for benchmark execution.
"""

import argparse
import yaml
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def load_config(path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def compute_config_hash(config: Dict[str, Any]) -> str:
    """Compute SHA256 hash of configuration for provenance."""
    content = json.dumps(config, sort_keys=True).encode()
    return hashlib.sha256(content).hexdigest()[:16]


def create_provenance_record(
    experiment_id: str,
    experiment_name: str,
    milestone: str,
    git_commit: str,
    environment_config: Dict,
    learner_config: Dict,
    output_dir: Path
) -> Dict[str, Any]:
    """Create a provenance record for the experiment."""
    return {
        "experiment": {
            "id": experiment_id,
            "name": experiment_name,
            "milestone": milestone,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "git_commit": git_commit
        },
        "environment": {
            "family": environment_config.get("environment", {}).get("family", "unknown"),
            "variant": environment_config.get("environment", {}).get("name", "default"),
            "seed": 42,
            "config_hash": compute_config_hash(environment_config)
        },
        "invariant_learner": {
            "method": learner_config.get("method", "unknown"),
            "config_hash": compute_config_hash(learner_config),
            "checkpoint": ""
        },
        "generation": {
            "generator_type": "none",
            "config_hash": "",
            "num_samples": 0
        },
        "intervention": {
            "type": "none",
            "targets": [],
            "num_trials": 0
        },
        "counterfactual": {
            "enabled": False,
            "query": "",
            "num_samples": 0
        },
        "metrics": {
            "generalization": [],
            "causal_stability": [],
            "generation_validity": []
        },
        "artifacts": [
            {"path": str(output_dir), "description": "Experiment outputs"},
            {"path": f"reports/{experiment_id}.md", "description": "Experiment report"}
        ],
        "notes": ""
    }


def save_provenance(record: Dict[str, Any], output_path: Path):
    """Save provenance record as YAML."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(record, f, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="OIR-PPV Experiment Runner")
    parser.add_argument("--experiment-id", required=True, help="Experiment ID (e.g., EXP-001)")
    parser.add_argument("--experiment-name", required=True, help="Experiment name")
    parser.add_argument("--milestone", required=True, choices=["M0", "M1", "M2", "M3", "M4", "M5"], help="Milestone")
    parser.add_argument("--env-config", required=True, help="Path to environment config YAML")
    parser.add_argument("--learner-config", required=True, help="Path to learner config YAML")
    parser.add_argument("--git-commit", default="unknown", help="Git commit SHA")
    parser.add_argument("--output-dir", default="artifacts/experiments", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    # Load configurations
    env_config = load_config(Path(args.env_config))
    learner_config = load_config(Path(args.learner_config))
    
    # Create output directory
    output_dir = Path(args.output_dir) / args.experiment_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create provenance record
    provenance = create_provenance_record(
        experiment_id=args.experiment_id,
        experiment_name=args.experiment_name,
        milestone=args.milestone,
        git_commit=args.git_commit,
        environment_config=env_config,
        learner_config=learner_config,
        output_dir=output_dir
    )
    
    # Save provenance
    provenance_path = output_dir / "provenance.yaml"
    save_provenance(provenance, provenance_path)
    
    # Save experiment configs (for reproducibility)
    with open(output_dir / "env_config.yaml", 'w') as f:
        yaml.dump(env_config, f, default_flow_style=False)
    with open(output_dir / "learner_config.yaml", 'w') as f:
        yaml.dump(learner_config, f, default_flow_style=False)
    
    print(f"Experiment {args.experiment_id} initialized")
    print(f"Output directory: {output_dir}")
    print(f"Provenance saved to: {provenance_path}")
    print("\nNext steps:")
    print("1. Implement environment data generation from env_config")
    print("2. Implement invariant learner from learner_config")
    print("3. Run evaluation and populate metrics in provenance")
    print("4. Generate report at reports/{args.experiment_id}.md")


if __name__ == "__main__":
    main()