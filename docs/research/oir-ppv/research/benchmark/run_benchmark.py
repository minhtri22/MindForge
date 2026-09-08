"""
Benchmark CLI Runner
Command-line interface for running benchmark suite.
"""

import argparse
import sys
from pathlib import Path
import time
import yaml
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from benchmark import BenchmarkRunner, BenchmarkConfig
from environments import load_environment_config


def run_single(args):
    """Run single benchmark configuration."""
    # Load environment config to get family
    env_config = load_environment_config(Path(args.env_config))
    
    config = BenchmarkConfig(
        experiment_id=args.experiment_id,
        environment_family=env_config.family,
        environment_config_path=args.env_config,
        baseline_id=args.baseline,
        baseline_config_path=args.baseline_config,
        seed=args.seed,
        output_dir=args.output,
        intervention_targets=args.intervention_targets.split(",") if args.intervention_targets else [],
        counterfactual_enabled=args.counterfactual
    )
    
    runner = BenchmarkRunner(Path(args.output))
    result = runner.run_benchmark(config)
    
    if result.status == "success":
        print(f"PASS {args.experiment_id}: {result.generalization}")
    else:
        print(f"FAIL {args.experiment_id}: {result.error}")
        return 1
    
    return 0


def run_suite(args):
    """Run benchmark suite from config file."""
    with open(args.suite_config, 'r') as f:
        suite_config = yaml.safe_load(f)
    
    configs = []
    for exp_config in suite_config["experiments"]:
        env_config = load_environment_config(Path(exp_config["env_config"]))
        
        config = BenchmarkConfig(
            experiment_id=exp_config["experiment_id"],
            environment_family=env_config.family,
            environment_config_path=exp_config["env_config"],
            baseline_id=exp_config["baseline"],
            baseline_config_path=exp_config["baseline_config"],
            seed=exp_config.get("seed", 42),
            output_dir=args.output,
            intervention_targets=exp_config.get("intervention_targets", []),
            counterfactual_enabled=exp_config.get("counterfactual", False)
        )
        configs.append(config)
    
    runner = BenchmarkRunner(Path(args.output))
    results = runner.run_suite(configs)
    
    successful = sum(1 for r in results if r.status == "success")
    print(f"\nSuite completed: {successful}/{len(results)} successful")
    
    return 0 if successful == len(results) else 1


def list_baselines(args):
    """List available baselines."""
    from benchmark.baselines import BASELINE_MAP
    print("Available baselines:")
    for bid, cls in BASELINE_MAP.items():
        print(f"  {bid}: {cls.__name__}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="OIR-PPV Benchmark Runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Single run
    single = subparsers.add_parser("run", help="Run single benchmark")
    single.add_argument("--experiment-id", required=True)
    single.add_argument("--env-config", required=True)
    single.add_argument("--baseline", required=True, choices=["B0", "B1", "B2", "B3", "B4", "B5"])
    single.add_argument("--baseline-config", required=True)
    single.add_argument("--seed", type=int, default=42)
    single.add_argument("--output", default="artifacts/benchmarks")
    single.add_argument("--intervention-targets", default="")
    single.add_argument("--counterfactual", action="store_true")
    
    # Suite run
    suite = subparsers.add_parser("suite", help="Run benchmark suite from config")
    suite.add_argument("--suite-config", required=True)
    suite.add_argument("--output", default="artifacts/benchmarks")
    
    # List
    list_parser = subparsers.add_parser("list-baselines", help="List available baselines")
    
    args = parser.parse_args()
    
    if args.command == "run":
        return run_single(args)
    elif args.command == "suite":
        return run_suite(args)
    elif args.command == "list-baselines":
        return list_baselines(args)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())