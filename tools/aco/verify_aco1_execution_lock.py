"""Independent static/runtime verification for the frozen ACO-1 execution lock.

This script MUST NOT call the ACO-1 collection or adjudication phases.
It validates identity, provenance, runtime, commands, protected cohorts,
source immutability, and absence of scientific outputs/workflows.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

LOCK_PATH = Path("docs/research/adaptive-continual-outcomes/ACO1_EXECUTION_LOCK.json")
EXPECTED_SCHEMA = "ACO1-EXECUTION-LOCK-v1"
EXPECTED_PROGRAM = "ACO-1"
EXPECTED_RUNNER = Path("experiments/aco/aco1_target_stability.py")
EXPECTED_PROTOCOL = Path("docs/research/adaptive-continual-outcomes/aco1-target-stability-protocol.md")
EXPECTED_IMPLEMENTATION_COMMIT = "e4e8f27b164ca938e6efa910bfb1ec2fc056f1a2"
EXPECTED_RUNNER_BLOB = "117bd3f16d576bf6f683d83747b6c1723a7ae471"
EXPECTED_PROTOCOL_SHA256 = "a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb"
EXPECTED_SEED_SHA256 = "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91"
EXPECTED_COLLECTION = "experiments/aco/results/aco1_fresh_records.json"
EXPECTED_RESULT = "experiments/aco/results/FORMAL_RESULT.json"
EXPECTED_COLLECTION_CMD = (
    "PYTHONPATH=. python experiments/aco/aco1_target_stability.py --phase collect "
    "--output experiments/aco/results/aco1_fresh_records.json"
)
EXPECTED_ADJUDICATION_CMD = (
    "PYTHONPATH=. python experiments/aco/aco1_target_stability.py --phase adjudicate "
    "--input experiments/aco/results/aco1_fresh_records.json "
    "--output experiments/aco/results/FORMAL_RESULT.json"
)
ALLOWED_POST_IMPLEMENTATION_PREFIXES = (
    "docs/research/adaptive-continual-outcomes/",
    "tools/aco/",
    "tests/test_aco1_execution_lock.py",
    ".github/workflows/aco1-execution-lock-verify.yml",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def seed_hash(seeds: list[int]) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in seeds).encode()).hexdigest()


def package_version(name: str) -> str:
    from importlib.metadata import version
    return version(name)


def verify(lock_path: Path = LOCK_PATH) -> dict[str, Any]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    checks["schema"] = lock.get("schema") == EXPECTED_SCHEMA
    checks["program"] = lock.get("program") == EXPECTED_PROGRAM
    checks["conditional_authorization"] = (
        lock.get("authorized") is True
        and lock.get("status") == "LOCKED_PENDING_INDEPENDENT_VERIFICATION"
        and lock.get("independent_verification", {}).get("required") is True
    )

    impl = lock.get("implementation", {})
    checks["implementation_commit"] = impl.get("commit") == EXPECTED_IMPLEMENTATION_COMMIT
    checks["runner_path"] = impl.get("runner_path") == str(EXPECTED_RUNNER)
    current_runner_blob = git("hash-object", str(EXPECTED_RUNNER))
    implementation_runner_blob = git(
        "rev-parse", f"{EXPECTED_IMPLEMENTATION_COMMIT}:{EXPECTED_RUNNER.as_posix()}"
    )
    checks["runner_blob_current"] = current_runner_blob == EXPECTED_RUNNER_BLOB
    checks["runner_blob_at_implementation"] = implementation_runner_blob == EXPECTED_RUNNER_BLOB
    checks["runner_blob_lock"] = impl.get("runner_git_blob_sha") == EXPECTED_RUNNER_BLOB
    details["runner_blob_current"] = current_runner_blob
    details["runner_blob_at_implementation"] = implementation_runner_blob

    changed = [
        x for x in git("diff", "--name-only", f"{EXPECTED_IMPLEMENTATION_COMMIT}..HEAD").splitlines()
        if x
    ]
    disallowed = [
        x for x in changed
        if not any(x == p or x.startswith(p) for p in ALLOWED_POST_IMPLEMENTATION_PREFIXES)
    ]
    checks["no_post_preflight_scientific_source_change"] = not disallowed
    details["post_implementation_changed_paths"] = changed
    details["disallowed_changed_paths"] = disallowed

    protocol = lock.get("protocol", {})
    checks["protocol_path"] = protocol.get("path") == str(EXPECTED_PROTOCOL)
    checks["protocol_sha256_lock"] = protocol.get("sha256") == EXPECTED_PROTOCOL_SHA256
    checks["protocol_sha256_file"] = sha256_file(EXPECTED_PROTOCOL) == EXPECTED_PROTOCOL_SHA256
    checks["protocol_git_blob"] = git("hash-object", str(EXPECTED_PROTOCOL)) == protocol.get("git_blob_sha")

    manifest = lock.get("seed_manifest", {})
    seeds = [int(x) for x in manifest.get("seeds", [])]
    checks["seed_count"] = len(seeds) == 40 and len(set(seeds)) == 40
    checks["seed_hash_lock"] = manifest.get("sha256") == EXPECTED_SEED_SHA256
    checks["seed_hash_recomputed"] = seed_hash(seeds) == EXPECTED_SEED_SHA256

    protected = {int(x) for x in lock.get("protected_kcl_cohort", {}).get("seeds", [])}
    checks["protected_cohort_prohibited"] = lock.get("protected_kcl_cohort", {}).get("prohibited") is True
    checks["fresh_protected_disjoint"] = set(seeds).isdisjoint(protected)

    runtime = lock.get("runtime", {})
    versions = {
        "python": platform.python_version(),
        "numpy": package_version("numpy"),
        "pytest": package_version("pytest"),
        "torch": importlib.import_module("torch").__version__,
        "pip": package_version("pip"),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
    }
    details["runtime_observed"] = versions
    checks["python_version"] = versions["python"] == runtime.get("python")
    checks["numpy_version"] = versions["numpy"] == runtime.get("numpy")
    checks["pytest_version"] = versions["pytest"] == runtime.get("pytest")
    checks["torch_version"] = versions["torch"] == runtime.get("torch")
    checks["pip_version"] = versions["pip"] == runtime.get("pip")
    checks["architecture"] = versions["machine"] == runtime.get("architecture")
    checks["cpu_device"] = runtime.get("device") == "CPU"
    checks["deterministic_algorithms"] = runtime.get("deterministic_algorithms") is True
    checks["torch_num_threads"] = int(runtime.get("torch_num_threads", -1)) == 1

    execution = lock.get("execution", {})
    checks["collection_command"] = execution.get("collection_command") == EXPECTED_COLLECTION_CMD
    checks["adjudication_command"] = execution.get("adjudication_command") == EXPECTED_ADJUDICATION_CMD
    checks["collection_output"] = execution.get("collection_output") == EXPECTED_COLLECTION
    checks["formal_result_output"] = execution.get("formal_result_output") == EXPECTED_RESULT
    checks["expected_records"] = execution.get("expected_records") == 120
    checks["one_shot"] = execution.get("one_shot_adjudication") is True
    checks["no_intermediate_metric_inspection"] = (
        execution.get("no_scientific_metric_inspection_between_collection_and_adjudication") is True
    )

    retry = lock.get("technical_failure_retry_policy", {})
    checks["retry_same_lock"] = retry.get("collection", {}).get("retry_must_use_exact_same_lock") is True
    checks["no_outcome_inspection_before_collection_retry"] = retry.get("collection", {}).get("outcome_inspection_before_retry") is False
    checks["no_valid_collection_rerun"] = retry.get("collection", {}).get("complete_valid_collection_must_not_be_rerun") is True
    checks["one_valid_adjudication"] = retry.get("adjudication", {}).get("exactly_one_valid_adjudication") is True
    checks["no_valid_result_rerun"] = retry.get("adjudication", {}).get("valid_formal_result_must_not_be_rerun") is True
    checks["change_invalidates_lock"] = retry.get("any_source_protocol_seed_or_dependency_change_invalidates_lock") is True
    checks["return_to_preflight_on_change"] = retry.get("invalidated_lock_requires_return_to_zero_science_preflight") is True

    checks["collection_absent"] = not Path(EXPECTED_COLLECTION).exists()
    checks["formal_result_absent"] = not Path(EXPECTED_RESULT).exists()

    execution_workflow_hits = []
    for wf in Path(".github/workflows").glob("*.yml"):
        txt = wf.read_text(encoding="utf-8")
        if "experiments/aco/aco1_target_stability.py" in txt and "--phase collect" in txt:
            execution_workflow_hits.append(str(wf))
    checks["execution_workflow_absent"] = not execution_workflow_hits
    details["execution_workflow_hits"] = execution_workflow_hits

    # Static consistency with the scientific runner. Importing the module has no training side effect.
    aco1 = importlib.import_module("experiments.aco.aco1_target_stability")
    checks["runner_seed_manifest"] = tuple(seeds) == tuple(aco1.FRESH_SEEDS)
    checks["runner_seed_hash"] = aco1.SEED_MANIFEST_SHA256 == EXPECTED_SEED_SHA256
    checks["runner_protected_cohort"] = tuple(lock["protected_kcl_cohort"]["seeds"]) == tuple(aco1.PROTECTED_KCL_SEEDS)
    checks["runner_lock_path"] = str(aco1.EXECUTION_LOCK) == str(LOCK_PATH)
    checks["runner_output_path"] = str(aco1.DEFAULT_RECORDS) == EXPECTED_COLLECTION
    checks["runner_thresholds"] = (
        aco1.STRICT_CURRENT_MIN == 0.95
        and aco1.PLASTICITY_BENEFIT_MIN == 0.01
        and aco1.RETENTION_MARGIN == 1 / 24
    )

    ok = all(checks.values())
    return {
        "schema": "ACO1-EXECUTION-LOCK-VERIFICATION-v1",
        "program": "ACO-1",
        "phase": "EXECUTION_LOCK_VERIFICATION",
        "status": "PASS" if ok else "FAIL",
        "verdict": "ACO1_EXECUTION_LOCK_VERIFICATION_PASS" if ok else "ACO1_EXECUTION_LOCK_VERIFICATION_FAIL",
        "lock_sha256": sha256_file(lock_path),
        "lock_status": lock.get("status"),
        "implementation_commit": EXPECTED_IMPLEMENTATION_COMMIT,
        "head_commit": git("rev-parse", "HEAD"),
        "checks": checks,
        "details": details,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--lock", type=Path, default=LOCK_PATH)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = verify(args.lock)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
