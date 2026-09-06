from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from .baselines import BASELINES
from .evaluate import L4_VERSION, evaluate_all, sha256_file, sha256_json, write_json


REPO_ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "ppf_l3"
RESULT_ROOT = REPO_ROOT / "docs" / "research" / "data" / "ppf-l4"
DEV_RESULT = RESULT_ROOT / "dev-results.json"
VALIDATION_RESULT = RESULT_ROOT / "validation-results.json"
LOCK_FILE = RESULT_ROOT / "baseline-lock.json"
FINAL_RESULT = RESULT_ROOT / "final-one-shot-results.json"
SUMMARY_FILE = RESULT_ROOT / "summary.json"
BASELINES_FILE = Path(__file__).resolve().parent / "baselines.py"
EVALUATOR_FILE = Path(__file__).resolve().parent / "evaluate.py"
RUNNER_FILE = Path(__file__).resolve()


def _read(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def run_split(split: str, output: Path) -> dict:
    if split == "final":
        raise ValueError("FINAL must use run_final() so the lock guard cannot be bypassed")
    result = evaluate_all(BENCHMARK_ROOT, split)
    write_json(output, result)
    return result


def create_lock() -> dict:
    if not DEV_RESULT.exists() or not VALIDATION_RESULT.exists():
        raise RuntimeError("DEV and VALIDATION results must exist before baseline lock")
    if FINAL_RESULT.exists():
        raise RuntimeError("FINAL result already exists; lock cannot be rewritten")
    dev = _read(DEV_RESULT)
    validation = _read(VALIDATION_RESULT)
    lock = {
        "l4_version": L4_VERSION,
        "base_l3_head": _git_head(),
        "baseline_source_sha256": sha256_file(BASELINES_FILE),
        "evaluator_source_sha256": sha256_file(EVALUATOR_FILE),
        "runner_source_sha256": sha256_file(RUNNER_FILE),
        "dev_result_sha256": sha256_json(dev),
        "validation_result_sha256": sha256_json(validation),
        "locked_baselines": [
            {
                "baseline_id": spec.baseline_id,
                "name": spec.name,
                "parameters": spec.parameters,
            }
            for spec in BASELINES
        ],
        "final_policy": "ONE_SHOT_ALL_LOCKED_BASELINES_NO_POST_FINAL_TUNING",
        "final_private_read_before_lock": False,
    }
    write_json(LOCK_FILE, lock)
    return lock


def _verify_lock(lock: dict) -> None:
    if lock.get("baseline_source_sha256") != sha256_file(BASELINES_FILE):
        raise RuntimeError("baseline source changed after lock")
    if lock.get("evaluator_source_sha256") != sha256_file(EVALUATOR_FILE):
        raise RuntimeError("evaluator source changed after lock")
    if lock.get("runner_source_sha256") != sha256_file(RUNNER_FILE):
        raise RuntimeError("runner source changed after lock")
    if lock.get("dev_result_sha256") != sha256_json(_read(DEV_RESULT)):
        raise RuntimeError("DEV result changed after lock")
    if lock.get("validation_result_sha256") != sha256_json(_read(VALIDATION_RESULT)):
        raise RuntimeError("VALIDATION result changed after lock")
    current = [
        {"baseline_id": s.baseline_id, "name": s.name, "parameters": s.parameters}
        for s in BASELINES
    ]
    if lock.get("locked_baselines") != current:
        raise RuntimeError("baseline registry changed after lock")


def run_final() -> dict:
    if not LOCK_FILE.exists():
        raise RuntimeError("baseline lock must exist before FINAL evaluator access")
    if FINAL_RESULT.exists():
        raise RuntimeError("FINAL one-shot result already exists; refusing rerun/overwrite")
    lock = _read(LOCK_FILE)
    _verify_lock(lock)
    result = evaluate_all(BENCHMARK_ROOT, "final")
    result["baseline_lock_sha256"] = sha256_json(lock)
    result["one_shot"] = True
    write_json(FINAL_RESULT, result)
    return result


def create_summary() -> dict:
    if not all(path.exists() for path in (DEV_RESULT, VALIDATION_RESULT, LOCK_FILE, FINAL_RESULT)):
        raise RuntimeError("DEV, VALIDATION, lock, and FINAL results are required")
    dev = _read(DEV_RESULT)
    validation = _read(VALIDATION_RESULT)
    final = _read(FINAL_RESULT)
    lock = _read(LOCK_FILE)
    summary = {
        "l4_version": L4_VERSION,
        "status": "COMPLETE",
        "procedure": ["DEV", "VALIDATION", "BASELINE_LOCK", "FINAL_ONE_SHOT"],
        "baseline_lock_sha256": sha256_json(lock),
        "dev_result_sha256": sha256_json(dev),
        "validation_result_sha256": sha256_json(validation),
        "final_result_sha256": sha256_json(final),
        "baseline_results": [],
        "architecture_boundary": "research tooling only; no Model/Kernel/Host/production-plugin changes",
    }
    for baseline_id in [s.baseline_id for s in BASELINES]:
        item = {"baseline_id": baseline_id}
        for split, result in (("dev", dev), ("validation", validation), ("final", final)):
            row = next(x for x in result["baselines"] if x["baseline_id"] == baseline_id)
            metrics = row["metrics"]
            item[split] = {
                "exact_state_accuracy": metrics["exact_state_accuracy"],
                "pattern_precision_status_proxy": metrics["pattern_precision_status_proxy"],
                "pattern_recall_status_proxy": metrics["pattern_recall_status_proxy"],
                "false_discovery_rate": metrics["false_discovery_rate"],
                "false_promotion_rate": metrics["false_promotion_rate"],
                "negative_exact_accuracy": metrics["negative_exact_accuracy"],
                "lifecycle_exact_accuracy": metrics["lifecycle_exact_accuracy"],
                "hard_violations": metrics["hard_violations"],
            }
        summary["baseline_results"].append(item)
    write_json(SUMMARY_FILE, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["dev", "validation", "lock", "final", "summary"])
    args = parser.parse_args()
    if args.phase == "dev":
        result = run_split("dev", DEV_RESULT)
    elif args.phase == "validation":
        result = run_split("validation", VALIDATION_RESULT)
    elif args.phase == "lock":
        result = create_lock()
    elif args.phase == "final":
        result = run_final()
    else:
        result = create_summary()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
