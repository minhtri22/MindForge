"""Run every M4 stress scenario twice and verify deterministic evidence."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from pipeline.run_m3_experiment import run_m3_experiment


DEFAULT_CONFIGS = [
    Path("pipeline/stress_nuisance.yaml"),
    Path("pipeline/stress_context.yaml"),
    Path("pipeline/stress_shortcut.yaml"),
    Path("pipeline/stress_ood.yaml"),
]


def _array_content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with np.load(path) as archive:
        for name in sorted(archive.files):
            value = np.ascontiguousarray(archive[name])
            digest.update(name.encode("utf-8"))
            digest.update(str(value.dtype).encode("ascii"))
            digest.update(json.dumps(list(value.shape)).encode("ascii"))
            digest.update(value.tobytes())
    return digest.hexdigest()


def _stable(value: Any) -> Any:
    ignored = {
        "timestamp", "path", "artifact_path", "command", "source_config",
        "effective_config", "sha256",
    }
    if isinstance(value, dict):
        return {
            key: _stable(item) for key, item in value.items()
            if key not in ignored
        }
    if isinstance(value, list):
        return [_stable(item) for item in value]
    return value


def _json_hash(path: Path) -> str:
    stable = _stable(json.loads(path.read_text(encoding="utf-8")))
    return hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def run_suite(configs: List[Path], output_root: Path) -> Dict[str, Any]:
    completed: Dict[str, Dict[str, Path]] = {}
    for repeat in ("run_a", "run_b"):
        for config in configs:
            command = (
                f"python -m pipeline.run_m3_experiment --config {config} "
                f"--output {output_root / repeat}"
            )
            result = run_m3_experiment(
                config, output_root / repeat, command=command
            )
            experiment_id = result["experiment_id"]
            completed.setdefault(experiment_id, {})[repeat] = (
                output_root / repeat / experiment_id
            )

    scenarios = []
    for experiment_id, repeats in sorted(completed.items()):
        left, right = repeats["run_a"], repeats["run_b"]
        json_files = [
            "evaluation.json", "dependency_analysis.json",
            "causal_validation.json", "shift_assertions.json", "results.json",
        ]
        json_comparison = {
            name: {
                "run_a_hash": _json_hash(left / name),
                "run_b_hash": _json_hash(right / name),
            }
            for name in json_files
        }
        for comparison in json_comparison.values():
            comparison["equal"] = (
                comparison["run_a_hash"] == comparison["run_b_hash"]
            )
        array_comparison = {}
        for name in ("generated.npz", "causal_arrays.npz"):
            left_hash = _array_content_hash(left / name)
            right_hash = _array_content_hash(right / name)
            array_comparison[name] = {
                "run_a_content_hash": left_hash,
                "run_b_content_hash": right_hash,
                "equal": left_hash == right_hash,
            }
        passed = all(item["equal"] for item in json_comparison.values()) and all(
            item["equal"] for item in array_comparison.values()
        )
        scenarios.append({
            "experiment_id": experiment_id,
            "seed": 42,
            "comparison_policy": (
                "exact canonical JSON and exact decoded array content; timestamps, "
                "commands, paths, and container-file hashes excluded"
            ),
            "json": json_comparison,
            "arrays": array_comparison,
            "passed": passed,
        })

    report = {
        "protocol": "m4_stress_reproducibility_v1",
        "scenario_count": len(scenarios),
        "all_passed": all(item["passed"] for item in scenarios),
        "scenarios": scenarios,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "reproducibility_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    if not report["all_passed"]:
        raise RuntimeError("Reproducibility comparison failed; inspect report")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/stress_test/m4_fix03")
    parser.add_argument("configs", nargs="*", default=DEFAULT_CONFIGS)
    args = parser.parse_args()
    report = run_suite([Path(path) for path in args.configs], Path(args.output))
    print(json.dumps({
        "all_passed": report["all_passed"],
        "scenario_count": report["scenario_count"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
