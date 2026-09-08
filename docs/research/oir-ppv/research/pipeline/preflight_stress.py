"""Generate and validate configured stress shifts without training learners."""

import argparse
import json
from pathlib import Path

import yaml

from environments import EnvironmentRegistry
from pipeline.run_m3_experiment import _apply_overrides, validate_shift_assertion


def run_preflight(config_path: Path, output_root: Path) -> dict:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    env_spec = config["environment"]
    base = yaml.safe_load(
        Path(env_spec["config_path"]).read_text(encoding="utf-8")
    )
    effective = _apply_overrides(base, env_spec.get("overrides", {}))
    output_dir = Path(output_root) / config["experiment"]["id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    effective_path = output_dir / "effective_env_config.yaml"
    effective_path.write_text(
        yaml.safe_dump(effective, sort_keys=False), encoding="utf-8"
    )
    environment = EnvironmentRegistry.create_from_config_path(
        effective_path, int(env_spec.get("seed", 42))
    )
    evidence = validate_shift_assertion(
        environment.generate(), config["stress_assertion"]
    )
    evidence["experiment_id"] = config["experiment"]["id"]
    evidence["source_config"] = str(config_path)
    (output_dir / "shift_assertions.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configs", nargs="+")
    parser.add_argument(
        "--output", default="artifacts/stress_test/m4_fix03/preflight"
    )
    args = parser.parse_args()
    results = [
        run_preflight(Path(config), Path(args.output)) for config in args.configs
    ]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
