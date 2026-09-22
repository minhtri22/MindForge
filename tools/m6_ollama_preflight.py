"""Zero-science/zero-runtime preflight helper for M6.

The helper deliberately does not import pipeline.m6 and never invokes Ollama.
Before an implementation lock exists it reports WAITING_FOR_IMPLEMENTATION_LOCK.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

LOCK_PATH = Path("artifacts/model-training-pipeline/m6/IMPLEMENTATION_LOCK.json")
OLLAMA_LOCK_PATH = Path("docs/model-training-pipeline/runtime/ollama.lock.json")


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
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
    lock_file = repo_root / LOCK_PATH
    if not lock_file.is_file():
        return {
            "schema": "mindforge-model-pipeline-m6-zero-runtime-preflight-v1",
            "status": "WAITING_FOR_IMPLEMENTATION_LOCK",
            "ollama_executable_invoked": False,
            "ollama_runtime_execution_executed": False,
            "m6_scientific_execution_executed": False,
            "m7_authorized": False,
        }

    lock = _read(lock_file)
    if lock.get("schema") != "mindforge-model-pipeline-m6-implementation-lock-v1":
        raise RuntimeError("M6 implementation lock schema mismatch")
    if lock.get("status") != "LOCKED":
        raise RuntimeError("M6 implementation is not LOCKED")

    blob_checks = []
    for path, expected in lock["git_blobs"].items():
        actual = _git_blob(repo_root, path)
        blob_checks.append({
            "path": path,
            "expected_git_blob_sha1": expected,
            "actual_git_blob_sha1": actual,
            "match": actual == expected,
        })

    source_path = repo_root / "pipeline/m6.py"
    tests_path = repo_root / "tests/test_model_pipeline_m6.py"
    workflow_path = repo_root / ".github/workflows/model-pipeline-m6-preflight.yml"
    source = source_path.read_text(encoding="utf-8")
    tests = tests_path.read_text(encoding="utf-8")
    workflow = workflow_path.read_text(encoding="utf-8")
    self_source = Path(__file__).read_text(encoding="utf-8")

    tree = ast.parse(self_source)
    imports_runtime = any(
        isinstance(node, ast.ImportFrom) and node.module == "pipeline.m6"
        or isinstance(node, ast.Import)
        and any(alias.name == "pipeline.m6" for alias in node.names)
        for node in ast.walk(tree)
    )

    combined_runtime_surfaces = "\n".join([source, tests, workflow, self_source])
    forbidden_exec_patterns = [
        r"subprocess\.(run|Popen|call|check_call|check_output)\([^\n]*ollama",
        r"os\.system\([^\n]*ollama",
    ]
    no_ollama_execution = not any(
        re.search(pattern, combined_runtime_surfaces, flags=re.IGNORECASE)
        for pattern in forbidden_exec_patterns
    )

    ollama_lock = _read(repo_root / OLLAMA_LOCK_PATH)
    implementation_stage = ollama_lock["implementation_stage"]

    static_checks = {
        "all_locked_blobs_match": all(item["match"] for item in blob_checks),
        "preflight_does_not_import_m6_runtime": not imports_runtime,
        "no_ollama_subprocess_execution": no_ollama_execution,
        "ollama_lock_exact_version": (
            ollama_lock["version"] == "0.34.2"
            and ollama_lock["tag"] == "v0.34.2"
        ),
        "ollama_lock_disallows_executable_invocation": (
            implementation_stage["executable_invocation_authorized"] is False
        ),
        "ollama_lock_disallows_version_probe": (
            implementation_stage["version_probe_authorized"] is False
        ),
        "ollama_lock_disallows_install_update": (
            implementation_stage["install_update_authorized"] is False
        ),
        "ollama_lock_disallows_download": (
            implementation_stage["download_authorized"] is False
        ),
        "m6_source_has_no_subprocess_import": "import subprocess" not in source,
        "m7_hard_false": '"m7_authorized": False' in source,
        "bulk_training_hard_false": '"bulk_training_authorized": False' in source,
        "modelfile_is_deterministic": "def render_modelfile" in source,
        "cleanup_requires_ownership": "cleanup_is_authorized" in source,
        "parity_is_not_exact_text": '"exact_text_required": False' in source,
    }

    passed = all(static_checks.values())
    return {
        "schema": "mindforge-model-pipeline-m6-zero-runtime-preflight-v1",
        "status": "PASS" if passed else "FAIL",
        "implementation_commit": lock["implementation_commit"],
        "blob_checks": blob_checks,
        "static_checks": static_checks,
        "ollama_executable_invoked": False,
        "ollama_runtime_execution_executed": False,
        "m6_scientific_execution_executed": False,
        "m7_authorized": False,
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
        print(f"M6 zero-runtime preflight: {result['status']}")
    return 0 if result["status"] in {"PASS", "WAITING_FOR_IMPLEMENTATION_LOCK"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
