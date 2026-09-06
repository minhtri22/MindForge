from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from tools.research.ppf_l4.baselines import BASELINE_BY_ID
from tools.research.ppf_l4.evaluate import score_predictions as l4_score_predictions

from .evaluate import evaluate_all, load_json, sha256_file, sha256_json, write_json
from .mechanism import L5_VERSION, TREATMENTS


REPO_ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "ppf_l3"
DATA_ROOT = REPO_ROOT / "docs" / "research" / "data" / "ppf-l5"
PREREG = DATA_ROOT / "mechanism-preregistration.json"
DEV_RESULT = DATA_ROOT / "dev-results.json"
VALIDATION_RESULT = DATA_ROOT / "validation-results.json"
VALIDATION_STATE = DATA_ROOT / "validation-run-state.json"
LOCK = DATA_ROOT / "mechanism-lock.json"
SUMMARY = DATA_ROOT / "summary.json"
MECHANISM_SOURCE = Path(__file__).resolve().parent / "mechanism.py"
EVALUATOR_SOURCE = Path(__file__).resolve().parent / "evaluate.py"
RUNNER_SOURCE = Path(__file__).resolve()

TARGETED_HARD = {
    "E1": "not_observable_as_current_violations",
    "E2": "unknown_context_positive_violations",
    "E3": "conflict_positive_violations",
    "E4": "stale_as_current_violations",
}


def _git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _row(result: dict, treatment_id: str) -> dict:
    return next(x for x in result["treatments"] if x["treatment_id"] == treatment_id)


def _metric_projection(metrics: dict) -> dict:
    return {
        key: metrics[key]
        for key in (
            "exact_state_accuracy",
            "pattern_precision_status_proxy",
            "pattern_recall_status_proxy",
            "false_discovery_rate",
            "false_promotion_rate",
            "negative_exact_accuracy",
            "lifecycle_exact_accuracy",
            "hard_violations",
        )
    }


def _verify_t0_against_l4(split: str, result: dict) -> None:
    l4_path = REPO_ROOT / "docs" / "research" / "data" / "ppf-l4" / f"{split}-results.json"
    l4 = load_json(l4_path)
    b9 = next(x for x in l4["baselines"] if x["baseline_id"] == "B9")
    t0 = _row(result, "T0")
    if _metric_projection(t0["metrics"]) != _metric_projection(b9["metrics"]):
        raise RuntimeError(f"T0 does not reproduce frozen L4 B9 on {split}")


def _selection(dev: dict, validation: dict) -> dict:
    t0_dev = _row(dev, "T0")["metrics"]
    t0_val = _row(validation, "T0")["metrics"]
    candidates = []
    decisions = []
    for treatment in TREATMENTS[1:]:
        d = _row(dev, treatment.treatment_id)["metrics"]
        v = _row(validation, treatment.treatment_id)["metrics"]
        targeted = {TARGETED_HARD[c] for c in treatment.components}
        all_hard = set(t0_dev["hard_violations"])
        checks = {
            "dev_exact_improves": d["exact_state_accuracy"] > t0_dev["exact_state_accuracy"],
            "validation_exact_improves": v["exact_state_accuracy"] > t0_val["exact_state_accuracy"],
            "dev_false_promotion_improves": d["false_promotion_rate"] < t0_dev["false_promotion_rate"],
            "validation_false_promotion_improves": v["false_promotion_rate"] < t0_val["false_promotion_rate"],
            "dev_recall_preserved": d["pattern_recall_status_proxy"] >= t0_dev["pattern_recall_status_proxy"],
            "validation_recall_preserved": v["pattern_recall_status_proxy"] >= t0_val["pattern_recall_status_proxy"],
            "correction_resurrection_zero": d["hard_violations"]["correction_resurrection_violations"] == 0 and v["hard_violations"]["correction_resurrection_violations"] == 0,
            "deleted_active_return_zero": d["hard_violations"]["deleted_active_return_violations"] == 0 and v["hard_violations"]["deleted_active_return_violations"] == 0,
            "targeted_hard_improves_dev": any(d["hard_violations"][k] < t0_dev["hard_violations"][k] for k in targeted),
            "targeted_hard_improves_validation": any(v["hard_violations"][k] < t0_val["hard_violations"][k] for k in targeted),
            "untargeted_not_worse_dev": all(d["hard_violations"][k] <= t0_dev["hard_violations"][k] for k in all_hard - targeted),
            "untargeted_not_worse_validation": all(v["hard_violations"][k] <= t0_val["hard_violations"][k] for k in all_hard - targeted),
        }
        qualifies = all(checks.values())
        decision = {
            "treatment_id": treatment.treatment_id,
            "components": list(treatment.components),
            "checks": checks,
            "qualifies": qualifies,
        }
        decisions.append(decision)
        if qualifies:
            candidates.append((treatment, d, v))
    if not candidates:
        return {"selected_treatment": None, "status": "NO_MINIMUM_FOUND", "decisions": decisions}
    candidates.sort(
        key=lambda item: (
            len(item[0].components),
            item[2]["false_promotion_rate"],
            -item[2]["exact_state_accuracy"],
            sum(item[2]["hard_violations"].values()),
            item[0].treatment_id,
        )
    )
    selected = candidates[0][0]
    return {
        "selected_treatment": selected.treatment_id,
        "selected_components": list(selected.components),
        "status": "MINIMUM_MECHANISM_FOUND",
        "decisions": decisions,
    }


def run_dev() -> dict:
    if not PREREG.exists():
        raise RuntimeError("mechanism preregistration must exist before treatments")
    result = evaluate_all(BENCHMARK_ROOT, "dev")
    _verify_t0_against_l4("dev", result)
    write_json(DEV_RESULT, result)
    return result


def freeze() -> dict:
    if not DEV_RESULT.exists() or not PREREG.exists():
        raise RuntimeError("DEV and preregistration required before freeze")
    prereg = load_json(PREREG)
    if prereg.get("validation_run_count", 0) != 0:
        raise RuntimeError("validation already started")
    prereg["freeze"] = {
        "mechanism_source_sha256": sha256_file(MECHANISM_SOURCE),
        "evaluator_source_sha256": sha256_file(EVALUATOR_SOURCE),
        "runner_source_sha256": sha256_file(RUNNER_SOURCE),
        "dev_result_sha256": sha256_json(load_json(DEV_RESULT)),
    }
    write_json(PREREG, prereg)
    prereg["preregistration_sha256"] = sha256_json(prereg)
    write_json(PREREG, prereg)
    return prereg


def _verify_freeze(prereg: dict) -> None:
    freeze_data = prereg.get("freeze") or {}
    expected = {
        "mechanism_source_sha256": sha256_file(MECHANISM_SOURCE),
        "evaluator_source_sha256": sha256_file(EVALUATOR_SOURCE),
        "runner_source_sha256": sha256_file(RUNNER_SOURCE),
        "dev_result_sha256": sha256_json(load_json(DEV_RESULT)),
    }
    if freeze_data != expected:
        raise RuntimeError("L5 source/evaluator/runner/DEV changed after validation freeze")


def run_validation_once() -> dict:
    if VALIDATION_RESULT.exists() or VALIDATION_STATE.exists():
        raise RuntimeError("VALIDATION one-shot has already started or completed; refusing rerun")
    prereg = load_json(PREREG)
    _verify_freeze(prereg)
    if prereg.get("validation_run_count", 0) != 0:
        raise RuntimeError("VALIDATION run count is not zero")
    write_json(
        VALIDATION_STATE,
        {
            "l5_version": L5_VERSION,
            "status": "STARTED",
            "semantic_run_count": 1,
            "source_freeze_verified": True,
        },
    )
    result = evaluate_all(BENCHMARK_ROOT, "validation")
    _verify_t0_against_l4("validation", result)
    write_json(VALIDATION_RESULT, result)
    write_json(
        VALIDATION_STATE,
        {
            "l5_version": L5_VERSION,
            "status": "COMPLETED",
            "semantic_run_count": 1,
            "source_freeze_verified": True,
            "validation_result_sha256": sha256_json(result),
        },
    )
    return result


def finalize() -> dict:
    if not DEV_RESULT.exists() or not VALIDATION_RESULT.exists():
        raise RuntimeError("DEV and VALIDATION required")
    dev = load_json(DEV_RESULT)
    validation = load_json(VALIDATION_RESULT)
    selection = _selection(dev, validation)
    selected_id = selection.get("selected_treatment")
    lock = None
    if selected_id:
        treatment = next(t for t in TREATMENTS if t.treatment_id == selected_id)
        lock = {
            "l5_version": L5_VERSION,
            "starting_commit": "18dc5332e73d673e245baa365a173f169c2ee412",
            "selected_treatment": selected_id,
            "selected_components": list(treatment.components),
            "learned_parameters": 0,
            "mechanism_source_sha256": sha256_file(MECHANISM_SOURCE),
            "evaluator_source_sha256": sha256_file(EVALUATOR_SOURCE),
            "runner_source_sha256": sha256_file(RUNNER_SOURCE),
            "dev_result_sha256": sha256_json(dev),
            "validation_result_sha256": sha256_json(validation),
            "preregistration_sha256": sha256_json(load_json(PREREG)),
            "final_policy": "L3_FINAL_FORBIDDEN_FOR_L5; NEW_BLIND_CONFIRMATORY_SPLIT_REQUIRED",
        }
        write_json(LOCK, lock)
    summary = {
        "l5_version": L5_VERSION,
        "starting_commit": "18dc5332e73d673e245baa365a173f169c2ee412",
        "status": selection["status"],
        "selection": selection,
        "validation_run_count": 1,
        "l3_final_used": False,
        "confirmatory_status": "NOT YET CONFIRMED ON A NEW BLIND HOLDOUT",
        "mechanism_lock_sha256": sha256_json(lock) if lock else None,
        "treatments": [],
    }
    t0d = _row(dev, "T0")["metrics"]
    t0v = _row(validation, "T0")["metrics"]
    for treatment in TREATMENTS:
        d = _row(dev, treatment.treatment_id)
        v = _row(validation, treatment.treatment_id)
        summary["treatments"].append(
            {
                "treatment_id": treatment.treatment_id,
                "components": list(treatment.components),
                "dev": _metric_projection(d["metrics"]),
                "validation": _metric_projection(v["metrics"]),
                "delta_vs_t0": {
                    "dev_exact": d["metrics"]["exact_state_accuracy"] - t0d["exact_state_accuracy"],
                    "dev_false_promotion": d["metrics"]["false_promotion_rate"] - t0d["false_promotion_rate"],
                    "dev_recall": d["metrics"]["pattern_recall_status_proxy"] - t0d["pattern_recall_status_proxy"],
                    "validation_exact": v["metrics"]["exact_state_accuracy"] - t0v["exact_state_accuracy"],
                    "validation_false_promotion": v["metrics"]["false_promotion_rate"] - t0v["false_promotion_rate"],
                    "validation_recall": v["metrics"]["pattern_recall_status_proxy"] - t0v["pattern_recall_status_proxy"],
                },
                "counterfactual_pairs_dev": d["counterfactual_pairs"],
                "counterfactual_pairs_validation": v["counterfactual_pairs"],
            }
        )
    write_json(SUMMARY, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["dev", "freeze", "validation", "finalize"])
    args = parser.parse_args()
    if args.phase == "dev":
        result = run_dev()
    elif args.phase == "freeze":
        result = freeze()
    elif args.phase == "validation":
        result = run_validation_once()
    else:
        result = finalize()
    if args.phase in {"dev", "validation"}:
        print(
            json.dumps(
                {
                    "phase": args.phase,
                    "treatments": [
                        {
                            "id": row["treatment_id"],
                            "exact": row["metrics"]["exact_state_accuracy"],
                            "false_promotion": row["metrics"]["false_promotion_rate"],
                            "recall": row["metrics"]["pattern_recall_status_proxy"],
                            "hard": row["metrics"]["hard_violations"],
                        }
                        for row in result["treatments"]
                    ],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
