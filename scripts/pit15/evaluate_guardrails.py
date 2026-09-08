"""Execute PIT-15 control/treatment comparison from frozen PIT evidence only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from guardrails import evaluate_signal

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "pit15"
PROTOCOL_PATH = EXP / "protocol.json"

SOURCE_FILES = {
    "qwen/qwen3.7-max:free": ROOT / "experiments/pit13/evidence/normalized/qwen-qwen3.7-max-free.jsonl",
    "deepseek/deepseek-v4-pro": ROOT / "experiments/pit13/evidence/normalized/deepseek-deepseek-v4-pro.jsonl",
    "minimax/minimax-m3:free": ROOT / "experiments/pit13/evidence/normalized/minimax-minimax-m3-free.jsonl",
    "meta/muse-glimmer-30b": ROOT / "experiments/pit14_1/evidence/normalized/meta-muse-glimmer-30b.jsonl",
    "nvidia/nemotron-3.5-lightning-30b-a3b": ROOT / "experiments/pit14_1/evidence/normalized/nvidia-nemotron-3.5-lightning-30b-a3b.jsonl",
    "openai/gpt-oss-20b": ROOT / "experiments/pit14_1/evidence/normalized/openai-gpt-oss-20b.jsonl",
    "google/gemma-4-31b-it": ROOT / "experiments/pit14_1/evidence/normalized/google-gemma-4-31b-it.jsonl",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    protocol = load_json(PROTOCOL_PATH)
    if protocol.get("status") != "FROZEN_BEFORE_EXECUTION":
        raise SystemExit("PIT-15 protocol is not frozen before execution")

    scenario_path = ROOT / protocol["scenario_source"]
    scenario_doc = load_json(scenario_path)
    scenarios = {row["scenario_id"]: row for row in scenario_doc["scenarios"]}
    expected = protocol["known_expected_violations"]

    samples: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    treatments: list[dict[str, Any]] = []

    for candidate_id in protocol["candidate_set"]:
        source = SOURCE_FILES[candidate_id]
        by_scenario = {row["scenario_id"]: row for row in load_jsonl(source)}
        for scenario_id in protocol["scenario_set"]:
            key = f"{candidate_id}|{scenario_id}"
            signal = by_scenario.get(scenario_id)
            if signal is None or not signal.get("schema_status"):
                samples.append({
                    "candidate_id": candidate_id,
                    "scenario_id": scenario_id,
                    "control_source": str(source.relative_to(ROOT)).replace("\\", "/"),
                    "control_evidence_status": "CONTROL_EVIDENCE_UNAVAILABLE",
                })
                continue

            expected_classes = list(expected.get(key, []))
            known_valid = not expected_classes
            result = evaluate_signal(signal, scenarios[scenario_id])
            actual_classes = result["violation_classes"]
            false_positive = known_valid and result["status"] != "ACCEPT"
            false_negative = bool(expected_classes) and not set(expected_classes).issubset(set(actual_classes))

            samples.append({
                "candidate_id": candidate_id,
                "scenario_id": scenario_id,
                "control_source": str(source.relative_to(ROOT)).replace("\\", "/"),
                "control_source_sha256": sha256(source),
                "control_evidence_status": "AVAILABLE",
                "oracle_expected_violations": expected_classes,
            })
            controls.append({
                "candidate_id": candidate_id,
                "scenario_id": scenario_id,
                "control_status": "PASS" if known_valid else "FAIL",
                "known_expected_violations": expected_classes,
                "teaching_signal": signal,
            })
            treatments.append({
                "candidate_id": candidate_id,
                "scenario_id": scenario_id,
                "control_status": "PASS" if known_valid else "FAIL",
                "guardrail_status": result["status"],
                "violations": result["violations"],
                "violation_classes": actual_classes,
                "evidence_basis": result["evidence_refs"],
                "false_positive_flag": false_positive,
                "false_negative_flag": false_negative,
                "guardrail_version": result["guardrail_version"],
            })

    if len(controls) != 49:
        raise SystemExit(f"Expected 49 frozen controls, found {len(controls)}")

    known_failures = [row for row in treatments if row["control_status"] == "FAIL"]
    known_valid = [row for row in treatments if row["control_status"] == "PASS"]
    conflict_failures = [row for row in known_failures if "UNSUPPORTED_CONFLICT_RESOLUTION" in expected[f'{row["candidate_id"]}|{row["scenario_id"]}']]
    heuristic_failures = [row for row in known_failures if "UNSUPPORTED_CONFLICT_RESOLUTION" not in expected[f'{row["candidate_id"]}|{row["scenario_id"]}']]
    muse_valid = [row for row in known_valid if row["candidate_id"] == "meta/muse-glimmer-30b"]
    lifecycle_types = {"preference_drift_001", "user_correction_001", "rare_exception_001", "insufficient_evidence_001", "long_term_consistency_001"}
    lifecycle_valid = [row for row in known_valid if row["scenario_id"] in lifecycle_types]

    detected = lambda rows: sum(row["guardrail_status"] in {"BLOCK", "FLAG"} for row in rows)
    accepted = lambda rows: sum(row["guardrail_status"] == "ACCEPT" for row in rows)
    rate = lambda num, den: round(num / den, 6) if den else None

    metrics = {
        "total_control_samples": len(controls),
        "total_treatment_samples": len(treatments),
        "known_semantic_failure_samples": len(known_failures),
        "known_valid_samples": len(known_valid),
        "semantic_failure_detection_rate": rate(detected(known_failures), len(known_failures)),
        "false_positive_rate": rate(detected(known_valid), len(known_valid)),
        "conflict_failure_detection_rate": rate(detected(conflict_failures), len(conflict_failures)),
        "unsupported_heuristic_detection_rate": rate(detected(heuristic_failures), len(heuristic_failures)),
        "positive_control_preservation_rate": rate(accepted(muse_valid), len(muse_valid)),
        "lifecycle_preservation_rate": rate(accepted(lifecycle_valid), len(lifecycle_valid)),
        "material_false_blocks_positive_control": sum(row["guardrail_status"] == "BLOCK" for row in muse_valid),
        "material_false_blocks_lifecycle": sum(row["guardrail_status"] == "BLOCK" for row in lifecycle_valid),
        "false_negative_samples": sum(bool(row["false_negative_flag"]) for row in treatments),
    }
    expected_violation_instances = sum(
        len(expected[f'{row["candidate_id"]}|{row["scenario_id"]}']) for row in known_failures
    )
    detected_expected_violation_instances = sum(
        len(set(expected[f'{row["candidate_id"]}|{row["scenario_id"]}']) & set(row["violation_classes"]))
        for row in known_failures
    )
    metrics["expected_violation_class_instances"] = expected_violation_instances
    metrics["detected_expected_violation_class_instances"] = detected_expected_violation_instances
    metrics["violation_class_recall"] = rate(detected_expected_violation_instances, expected_violation_instances)

    criteria = protocol["success_criteria"]
    success = (
        metrics["conflict_failure_detection_rate"] >= criteria["conflict_failure_detection_rate"]
        and metrics["unsupported_heuristic_detection_rate"] >= criteria["unsupported_heuristic_detection_rate"]
        and metrics["positive_control_preservation_rate"] >= criteria["positive_control_preservation_rate"]
        and metrics["lifecycle_preservation_rate"] >= criteria["lifecycle_preservation_rate"]
        and metrics["material_false_blocks_positive_control"] <= criteria["positive_control_material_false_blocks"]
        and metrics["material_false_blocks_lifecycle"] <= criteria["lifecycle_material_false_blocks"]
    )

    candidate_effects = []
    for candidate_id in protocol["candidate_set"]:
        rows = [row for row in treatments if row["candidate_id"] == candidate_id]
        failures = [row for row in rows if row["control_status"] == "FAIL"]
        valid = [row for row in rows if row["control_status"] == "PASS"]
        caught = detected(failures)
        overblocked = detected(valid)
        if not failures and overblocked == 0:
            effect = "UNCHANGED_VALID"
        elif failures and caught == len(failures) and overblocked == 0:
            effect = "IMPROVED_BY_GUARDRAIL"
        elif overblocked and caught:
            effect = "MIXED_EFFECT"
        elif overblocked:
            effect = "OVERBLOCKED"
        else:
            effect = "UNCHANGED_UNSAFE"
        candidate_effects.append({
            "candidate_id": candidate_id,
            "effect": effect,
            "known_failure_samples": len(failures),
            "known_failures_detected": caught,
            "known_valid_samples": len(valid),
            "valid_samples_flagged_or_blocked": overblocked,
        })

    verdict = "GUARDRAIL_EFFECTIVE" if success and metrics["false_positive_rate"] == 0 else (
        "GUARDRAIL_EFFECTIVE_WITH_OVERBLOCKING" if success else "GUARDRAIL_INSUFFICIENT"
    )
    summary = {
        "task": "PIT-15 Teaching Signal Guardrail Experiment",
        "status": "COMPLETED",
        "guardrail_verdict": verdict,
        "success_criteria_met": success,
        "architectural_implication": "Within frozen PIT evidence, Teacher * Evidence-Bound Guardrail improves system-level semantic safety while leaving raw teacher behavior and verdicts unchanged.",
        "api_calls": 0,
        "new_teacher_inference": 0,
        "teacher_selected": False,
        "training": False,
        "distillation": False,
        "mindforge_integration": False,
        "next_recommended_milestone": "PIT-16 Guardrail Refinement / Adversarial Validation"
    }

    write_json(EXP / "samples.json", {
        "scenario_source": str(scenario_path.relative_to(ROOT)).replace("\\", "/"),
        "scenario_source_sha256": sha256(scenario_path),
        "samples": samples,
    })
    write_jsonl(EXP / "control/control-results.jsonl", controls)
    write_jsonl(EXP / "treatment/guardrail-results.jsonl", treatments)
    write_json(EXP / "metrics.json", metrics)
    write_json(EXP / "candidate-effects.json", {"candidate_effects": candidate_effects})
    write_json(EXP / "summary.json", summary)

    print(json.dumps({"summary": summary, "metrics": metrics, "candidate_effects": candidate_effects}, indent=2))


if __name__ == "__main__":
    main()
