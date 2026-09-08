"""Freeze PIT-18 Representation V2 inputs before one-shot final evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit18"
RUNTIME_FILES = (
    "scripts/pit18/surface_normalizer.py",
    "scripts/pit18/primitive_schema.py",
    "scripts/pit18/primitive_extractor.py",
    "scripts/pit18/canonicalizer.py",
    "scripts/pit18/scope_lattice.py",
    "scripts/pit18/support_relations_v2.py",
    "scripts/pit18/representation_v2.py",
)
METRIC_DEFINITION_FILES = (
    "scripts/pit18/evaluate_representation.py",
    "scripts/pit18/evaluate_pit15_regression.py",
    "scripts/pit18/evaluate_pit16_heldout.py",
    "scripts/pit18/summarize_pit16_views.py",
)
PRE_EXPOSED = ["conflict-04", "conflict-05", "conflict-06", "conflict-07", "conflict-08"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_files(paths: tuple[str, ...]) -> str:
    h = hashlib.sha256()
    for rel in paths:
        h.update((ROOT / rel).read_bytes())
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    from primitive_schema import PRIMITIVE_FAMILIES, PRIMITIVE_SCHEMA_VERSION, REPRESENTATION_VERSION
    from scope_lattice import SCOPE_LEVELS
    from evaluate_representation import score as score_representation
    from evaluate_pit15_regression import score as score_pit15
    from evaluate_pit16_heldout import score as score_pit16

    primitive_schema = {
        "version": PRIMITIVE_SCHEMA_VERSION,
        "representation_version": REPRESENTATION_VERSION,
        "families": {key: list(value) for key, value in PRIMITIVE_FAMILIES.items()},
    }
    scope_lattice = {
        "version": "pit18-scope-lattice-v1",
        "ordering": [key for key, _ in sorted(SCOPE_LEVELS.items(), key=lambda item: item[1])],
        "levels": SCOPE_LEVELS,
    }
    pre_exposure = {
        "status": "PARTIALLY_PRE_EXPOSED",
        "pre_exposed_ids": PRE_EXPOSED,
        "labels_exposed": False,
        "used_for_refinement": False,
        "disclosure": "Five PIT-16 held-out conflict surfaces were accidentally displayed before freeze; labels were not exposed and the displayed surfaces were not used for refinement.",
    }
    write_json(EXP / "primitive-schema.json", primitive_schema)
    write_json(EXP / "scope-lattice.json", scope_lattice)
    write_json(EXP / "pre-exposure-manifest.json", pre_exposure)
    dev_metrics = {
        "representation": score_representation(load_jsonl(EXP / "representation-results-dev.jsonl"), "DEV"),
        "pit15": score_pit15(load_jsonl(EXP / "dev-pit15-rerun.jsonl")),
        "pit16": score_pit16(load_jsonl(EXP / "dev-pit16-rerun.jsonl")),
    }
    write_json(EXP / "dev-metrics.json", dev_metrics)

    success = {
        "representation_heldout": {
            "primitive_precision_min": 0.95,
            "primitive_recall_min": 0.95,
            "canonical_fact_precision_min": 0.95,
            "canonical_fact_recall_min": 0.95,
            "scope_classification_accuracy_min": 0.95,
            "scope_relation_accuracy_min": 0.95,
            "support_relation_accuracy_min": 0.95,
            "representation_cluster_consistency_min": 0.95,
        },
        "pit15": {
            "known_failure_detection": 1.0,
            "conflict_detection": 1.0,
            "unsupported_heuristic_detection": 1.0,
            "muse_preservation": 1.0,
            "lifecycle_preservation": 1.0,
            "false_positive_rate_max": 0.05,
        },
        "pit16": {
            "unsafe_sample_recall_min": 0.95,
            "unsafe_sample_precision_min": 0.95,
            "violation_class_recall_min": 0.95,
            "violation_class_precision_min": 0.95,
            "hard_negative_fpr_max": 0.05,
            "conflict_recall": 1.0,
            "numeric_threshold_recall_min": 0.95,
            "temporal_rule_recall_min": 0.95,
            "fallback_recall_min": 0.95,
            "scope_generalization_recall_min": 0.95,
            "compound_full_class_recall": 1.0,
        },
    }
    freeze = {
        "implementation_files": list(RUNTIME_FILES),
        "representation_v2_sha256": sha256_files(RUNTIME_FILES),
        "primitive_schema_sha256": sha256_file(EXP / "primitive-schema.json"),
        "scope_lattice_sha256": sha256_file(EXP / "scope-lattice.json"),
        "support_relations_v2_sha256": sha256_file(ROOT / "scripts/pit18/support_relations_v2.py"),
        "guardrail_v3_sha256": sha256_file(ROOT / "scripts/pit17/guardrail_v3.py"),
        "representation_gold_dev_sha256": sha256_file(EXP / "representation-gold-dev.json"),
        "representation_gold_heldout_sha256": sha256_file(EXP / "representation-gold-heldout.json"),
        "representation_clusters_sha256": sha256_file(EXP / "representation-clusters.json"),
        "pit16_corpus_sha256": sha256_file(ROOT / "experiments/pit16/corpus.json"),
        "pit16_split_sha256": sha256_file(ROOT / "experiments/pit16/split.json"),
        "pre_exposure_manifest_sha256": sha256_file(EXP / "pre-exposure-manifest.json"),
        "metrics_definitions_sha256": sha256_files(METRIC_DEFINITION_FILES),
        "metrics_definition_files": list(METRIC_DEFINITION_FILES),
    }
    protocol = {
        "task": "PIT-18 Representation Layer Refinement",
        "status": "FROZEN_BEFORE_FINAL_EVALUATION",
        "representation_version": REPRESENTATION_VERSION,
        "guardrail_version": "pit17-unified-semantic-fact-guardrail-v3",
        "api_calls": 0,
        "new_teacher_inference": 0,
        "development_sources": ["PIT-15 historical corpus", "PIT-16 DEV", "PIT-18 representation DEV gold", "PIT-18 DEV invariance clusters"],
        "final_evaluation_sources": ["PIT-18 representation HELD_OUT", "PIT-15 historical corpus", "PIT-16 HELD_OUT"],
        "heldout_integrity": pre_exposure,
        "methodology_notes": {"heldout_surface_preexposure_detected": True, "post_freeze_tuning_allowed": False},
        "success_criteria": success,
        "dev_validation": dev_metrics,
        "freeze": freeze,
    }
    write_json(EXP / "protocol.json", protocol)
    print(json.dumps({"status": protocol["status"], "freeze": freeze, "heldout_integrity": pre_exposure}, indent=2))


if __name__ == "__main__":
    main()
