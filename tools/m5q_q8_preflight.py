"""Zero-science preflight for the locked M5Q Q8_0 implementation.

This program performs only repository/provenance/static-contract checks. It does
not invoke llama-quantize, llama-cli, model loading, conversion, or training.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any

LOCK_PATH = Path("artifacts/model-training-pipeline/m5_quantization/Q8_0_IMPLEMENTATION_LOCK.json")


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


def run_preflight(repo_root: Path) -> dict[str, Any]:
    lock_path = repo_root / LOCK_PATH
    if not lock_path.is_file():
        return {
            "schema": "mindforge-model-pipeline-m5q-q8-zero-science-preflight-v1",
            "status": "WAITING_FOR_IMPLEMENTATION_LOCK",
            "quantization_executed": False,
            "q4_executed": False,
            "m6_authorized": False,
        }

    lock = _read(lock_path)
    if lock.get("schema") != "mindforge-model-pipeline-m5q-q8-implementation-lock-v1":
        raise RuntimeError("Q8 implementation lock schema mismatch")
    if lock.get("status") != "LOCKED":
        raise RuntimeError("Q8 implementation is not LOCKED")

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

    q8_source = (repo_root / "pipeline/m5q.py").read_text(encoding="utf-8")
    runner_source = (repo_root / "tools/m5q_q8_qualification.py").read_text(
        encoding="utf-8"
    )

    preflight_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports_q8_runtime = any(
        (
            isinstance(node, ast.Import)
            and any(alias.name == "pipeline.m5q" for alias in node.names)
        )
        or (
            isinstance(node, ast.ImportFrom)
            and node.module == "pipeline.m5q"
        )
        for node in ast.walk(preflight_tree)
    )

    static_checks = {
        "all_locked_blobs_match": all(row["match"] for row in checks),
        "q8_target_literal_present": 'Q8_QUANTIZER_TYPE = "Q8_0"' in q8_source,
        "q8_target_key_present": 'Q8_TARGET_KEY = "q8_0"' in q8_source,
        "no_q4_quantizer_literal_in_q8_module": "Q4_K_M" not in q8_source,
        "no_general_m5_target_loop": "run_m5_qualification" not in q8_source,
        "q4_hard_false_in_result": '"q4_executed": False' in q8_source,
        "m6_hard_false_in_result": '"m6_authorized": False' in q8_source,
        "m6_auto_open_hard_false": '"m6_auto_open": False' in q8_source,
        "runner_calls_q8_only_entrypoint": "run_q8_qualification" in runner_source,
        "preflight_does_not_import_q8_runtime": not imports_q8_runtime,
    }

    passed = all(static_checks.values())
    return {
        "schema": "mindforge-model-pipeline-m5q-q8-zero-science-preflight-v1",
        "status": "PASS" if passed else "FAIL",
        "implementation_commit": lock["implementation_commit"],
        "parent_f16_closure_commit": lock["parent_f16_closure_commit"],
        "blob_checks": checks,
        "static_checks": static_checks,
        "quantization_executed": False,
        "q4_executed": False,
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
        print(f"M5Q Q8_0 zero-science preflight: {result['status']}")
    return 0 if result["status"] in {"PASS", "WAITING_FOR_IMPLEMENTATION_LOCK"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
