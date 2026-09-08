"""Validate PIT-15 artifacts and frozen-source provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "pit15"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = load_json(EXP / "protocol.json")
    samples = load_json(EXP / "samples.json")
    controls = load_jsonl(EXP / "control/control-results.jsonl")
    treatments = load_jsonl(EXP / "treatment/guardrail-results.jsonl")
    metrics = load_json(EXP / "metrics.json")
    effects = load_json(EXP / "candidate-effects.json")["candidate_effects"]
    summary = load_json(EXP / "summary.json")

    assert protocol["status"] == "FROZEN_BEFORE_EXECUTION"
    assert len(protocol["candidate_set"]) == 7
    assert len(protocol["scenario_set"]) == 7
    assert len(controls) == 49
    assert len(treatments) == 49
    assert len(effects) == 7
    assert all(row["guardrail_version"] == protocol["guardrail_version"] for row in treatments)
    assert all(row["guardrail_status"] in {"ACCEPT", "BLOCK", "FLAG"} for row in treatments)

    scenario_path = ROOT / samples["scenario_source"]
    assert sha256(scenario_path) == samples["scenario_source_sha256"]
    for row in samples["samples"]:
        assert row["control_evidence_status"] == "AVAILABLE"
        source = ROOT / row["control_source"]
        assert sha256(source) == row["control_source_sha256"]

    assert metrics["conflict_failure_detection_rate"] == 1.0
    assert metrics["unsupported_heuristic_detection_rate"] == 1.0
    assert metrics["positive_control_preservation_rate"] == 1.0
    assert metrics["lifecycle_preservation_rate"] == 1.0
    assert metrics["material_false_blocks_positive_control"] == 0
    assert metrics["material_false_blocks_lifecycle"] == 0
    assert metrics["false_negative_samples"] == 1
    assert metrics["expected_violation_class_instances"] == 13
    assert metrics["detected_expected_violation_class_instances"] == 12
    assert metrics["violation_class_recall"] == 0.923077
    assert summary["guardrail_verdict"] == "GUARDRAIL_EFFECTIVE"
    assert summary["api_calls"] == 0
    assert summary["new_teacher_inference"] == 0
    assert summary["teacher_selected"] is False

    guardrail_source = (ROOT / "scripts/pit15/guardrails.py").read_text(encoding="utf-8")
    for candidate_id in protocol["candidate_set"]:
        assert candidate_id not in guardrail_source, f"candidate-specific guardrail logic found: {candidate_id}"

    print("PIT15_VALIDATION_PASS")
    print(f"samples={len(treatments)} guardrail_verdict={summary['guardrail_verdict']}")


if __name__ == "__main__":
    main()
