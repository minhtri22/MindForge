"""Zero-science preflight for locked M5Q Q4_K_M implementation.

This helper performs repository/provenance/static-contract checks only. It does
not import the Q4 scientific runtime and never invokes model loading, conversion,
llama-cli, llama-quantize, or training.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any

LOCK_PATH = Path(
    "artifacts/model-training-pipeline/m5_quantization/Q4_K_M_IMPLEMENTATION_LOCK.json"
)
EXPOSURE_PATH = Path(
    "artifacts/model-training-pipeline/m5_quantization/Q4_OUTCOME_EXPOSURE.json"
)


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def _git_blob(repo_root: Path, path: str) -> str:
    completed = subprocess.run(
        ["git", "hash-object", "--", path],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git hash-object failed for {path}: {completed.stderr}")
    return completed.stdout.strip()


def _exposed_outcome_strings(exposure: dict[str, Any]) -> list[str]:
    q4 = exposure["q4_outcome_exposure"]
    observed = q4["observed_artifact"]
    replay = q4["accidental_replay"]
    return [
        str(observed["sha256"]),
        str(observed["aggregate_manifest_hash"]),
        str(observed["size"]),
        str(replay["combined_result_hash"]),
    ]


def run_preflight(repo_root: Path) -> dict[str, Any]:
    lock_path = repo_root / LOCK_PATH
    if not lock_path.is_file():
        return {
            "schema": "mindforge-model-pipeline-m5q-q4-zero-science-preflight-v1",
            "status": "WAITING_FOR_IMPLEMENTATION_LOCK",
            "quantization_executed": False,
            "q4_scientific_execution_executed": False,
            "m6_authorized": False,
        }

    lock = _read(lock_path)
    if lock.get("schema") != "mindforge-model-pipeline-m5q-q4-implementation-lock-v1":
        raise RuntimeError("Q4 implementation lock schema mismatch")
    if lock.get("status") != "LOCKED":
        raise RuntimeError("Q4 implementation is not LOCKED")

    checks: list[dict[str, Any]] = []
    for path, expected in lock["git_blobs"].items():
        actual = _git_blob(repo_root, path)
        checks.append(
            {
                "path": path,
                "expected_git_blob_sha1": expected,
                "actual_git_blob_sha1": actual,
                "match": actual == expected,
            }
        )

    q4_source_path = repo_root / "pipeline/m5q_q4.py"
    runner_path = repo_root / "tools/m5q_q4_qualification.py"
    tests_path = repo_root / "tests/test_model_pipeline_m5q_q4.py"
    workflow_path = repo_root / ".github/workflows/model-pipeline-m5q-q4-preflight.yml"

    q4_source = q4_source_path.read_text(encoding="utf-8")
    runner_source = runner_path.read_text(encoding="utf-8")
    tests_source = tests_path.read_text(encoding="utf-8")
    workflow_source = workflow_path.read_text(encoding="utf-8")
    lock_source = lock_path.read_text(encoding="utf-8")

    preflight_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports_q4_runtime = any(
        (
            isinstance(node, ast.Import)
            and any(alias.name == "pipeline.m5q_q4" for alias in node.names)
        )
        or (
            isinstance(node, ast.ImportFrom)
            and node.module == "pipeline.m5q_q4"
        )
        for node in ast.walk(preflight_tree)
    )

    exposure = _read(repo_root / EXPOSURE_PATH)
    forbidden = _exposed_outcome_strings(exposure)
    implementation_text = "\n".join(
        [q4_source, runner_source, tests_source, workflow_source, lock_source]
    )
    exposed_value_absent = all(value not in implementation_text for value in forbidden)

    static_checks = {
        "all_locked_blobs_match": all(row["match"] for row in checks),
        "q4_target_literal_present": 'Q4_QUANTIZER_TYPE = "Q4_K_M"' in q4_source,
        "q4_target_key_present": 'Q4_TARGET_KEY = "q4_k_m"' in q4_source,
        "no_general_m5_target_loop": "run_m5_qualification" not in q4_source,
        "no_q8_execution_entrypoint": "run_q8_qualification" not in q4_source,
        "q8_hard_false_in_sequence_provenance": '"q8_executed": False' in q4_source,
        "m6_hard_false_in_result": '"m6_authorized": False' in q4_source,
        "m6_auto_open_hard_false": '"m6_auto_open": False' in q4_source,
        "post_exposure_thresholds_hard_false": (
            '"post_exposure_thresholds_added": False' in q4_source
        ),
        "runner_calls_q4_only_entrypoint": "run_q4_qualification" in runner_source,
        "preflight_does_not_import_q4_runtime": not imports_q4_runtime,
        "exposed_outcome_values_absent_from_q4_implementation": exposed_value_absent,
        "no_strict_q4_q8_ordering_gate": "strict_compression_ordering" not in q4_source,
    }

    passed = all(static_checks.values())
    return {
        "schema": "mindforge-model-pipeline-m5q-q4-zero-science-preflight-v1",
        "status": "PASS" if passed else "FAIL",
        "implementation_commit": lock["implementation_commit"],
        "parent_f16_closure_commit": lock["parent_f16_closure_commit"],
        "prior_out_of_protocol_outcome_exposure": True,
        "blob_checks": checks,
        "static_checks": static_checks,
        "quantization_executed": False,
        "q4_scientific_execution_executed": False,
        "m6_authorized": False,
        "bulk_training_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = run_preflight(Path(args.workspace).resolve())
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"M5Q Q4_K_M zero-science preflight: {result['status']}")
    return 0 if result["status"] in {"PASS", "WAITING_FOR_IMPLEMENTATION_LOCK"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
