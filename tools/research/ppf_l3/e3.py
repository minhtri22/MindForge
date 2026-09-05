"""PPF-L3 E3 canonical VALIDATION generation.

Research tooling only. E3 reuses the frozen E2 generator primitives and
counterfactual contracts to materialize the protected validation split. It does
not implement a recognizer, baseline, model, kernel primitive, or runtime
feature.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tools.research import ppf_l2_validate
from tools.research.ppf_l2_validation import validate_fixture
from tools.research.ppf_l3 import e0, e1, e2

ROOT = e2.ROOT
BENCH_ROOT = e2.BENCH_ROOT
VERSION = e2.VERSION
GENERATOR_VERSION = "ppf-l3-e3-generator/1"
STARTING_COMMIT = "a6f2f630d42cc62c48d2b170cc76797656bf7ef7"
VALIDATION_MASTER_SEED = "mindforge-ppf-l3-e3-validation-v1"


def validation_truth_configs() -> list[e2.TruthConfig]:
    return [
        e2.TruthConfig("val-s01", "validation-stable-sequence", "STANDARD", ("routine/opportunity", "temporal sequence"), "MEDIUM", e2._repeat_plan((1, 0, 1, 1, 0, 1, 1, 1), 24)),
        e2.TruthConfig("val-s02", "validation-context-choice", "STANDARD", ("preference/availability", "conditional preference"), "MEDIUM", (1,) * 24, ("walk", "bike", "transit", "skip"), truth_kind="PREFERENCE", scope="choice:commute"),
        e2.TruthConfig("val-s03", "validation-relationship-scope", "STANDARD", ("relationship-conditioned", "unknown context"), "MEDIUM", e2._repeat_plan((1, 1, 0, 1, 0, 1), 24), truth_kind="RELATIONSHIP_CONDITIONED", scope="activity:collaboration"),
        e2.TruthConfig("val-s04", "validation-exception-parent", "STANDARD", ("exception", "scoped exception", "lifecycle parent relation"), "LONG", e2._repeat_plan((1, 1, 0, 1, 1, 1, 0, 1), 64)),
        e2.TruthConfig("val-s05", "validation-evidence-lineage", "STANDARD", ("multi-device replication", "independent corroboration", "raw/derived evidence"), "MEDIUM", (1,) + (0,) * 23, truth_kind="SINGLE_OCCURRENCE", base_answer="INSUFFICIENT_EVIDENCE"),
        e2.TruthConfig("val-h01", "validation-sparse-confound", "HIGH-RISK", ("confounding", "Simpson-like aggregation", "sparse coincidence", "NO_PATTERN controls", "multi-device replication", "independent corroboration"), "SHORT", (1, 0, 0, 1, 0, 1, 0, 0), truth_kind="NO_PATTERN", identifiability="PARTIAL", base_answer="INSUFFICIENT_EVIDENCE"),
        e2.TruthConfig("val-h02", "validation-context-choice", "HIGH-RISK", ("real drift", "coverage-induced fake drift", "reversal", "missingness", "observation quality", "unidentifiable latent truth", "pattern overlap", "conflicting structure", "correction/rejection", "deletion/reset", "staleness"), "LONG", e2._repeat_plan((1, 1, 1, 0, 1, 0, 0, 1), 64), truth_kind="DRIFT_OR_UNIDENTIFIABLE", identifiability="NO", base_answer="NOT_OBSERVABLE"),
    ]


def _validation_config_map() -> dict[str, e2.TruthConfig]:
    return {config.config_id: config for config in validation_truth_configs()}


def _validation_replicas_for(config: e2.TruthConfig) -> list[tuple[int, int]]:
    reps = (0, 1, 2) if config.risk_class == "HIGH-RISK" else (0, 1)
    return [(b, o) for b in reps for o in reps]


def _validation_pair_assignment_map() -> dict[tuple[str, int, int], tuple[str, str]]:
    assignments: dict[tuple[str, int, int], tuple[str, str]] = {}

    def add(config_id: str, seed_a: tuple[int, int], seed_b: tuple[int, int], template: str) -> None:
        assignments[(config_id, *seed_a)] = (template, "A")
        assignments[(config_id, *seed_b)] = (template, "B")

    add("val-s01", (0, 0), (0, 1), "full_observability_vs_permission_loss")
    add("val-s01", (1, 0), (1, 1), "normal_quality_vs_degraded_quality")
    add("val-s02", (0, 0), (0, 1), "meaningful_alternatives_vs_constrained_availability")
    add("val-s03", (0, 0), (0, 1), "known_relationship_vs_unknown_relationship")
    add("val-s04", (0, 0), (0, 1), "stable_exception_vs_random_deviation")
    add("val-s04", (1, 0), (1, 1), "correction_absent_vs_correction_applied")
    add("val-s05", (0, 0), (0, 1), "single_evidence_vs_same_origin_replicas")
    add("val-s05", (1, 0), (1, 1), "raw_only_vs_raw_plus_derived_lineage")
    add("val-h01", (0, 0), (0, 1), "true_routine_vs_chance_matching_no_pattern")
    add("val-h01", (1, 0), (1, 1), "conditional_truth_vs_misleading_aggregate")
    add("val-h01", (2, 0), (2, 1), "independent_corroboration_vs_same_origin_replication")
    add("val-h02", (0, 0), (0, 1), "stable_behavior_vs_fake_drift")
    add("val-h02", (1, 0), (1, 1), "true_drift_vs_observation_only_change")
    add("val-h02", (2, 0), (2, 1), "deletion_absent_vs_deletion_applied")
    return assignments


def _validation_lifecycle_assignment_map() -> dict[tuple[str, int, int], str]:
    return {
        ("val-s02", 1, 0): "staleness",
        ("val-s03", 1, 0): "reversal",
        ("val-h02", 0, 2): "correction_high_risk",
        ("val-h02", 1, 2): "reset",
        ("val-h02", 2, 2): "supersession_invalidation",
    }


def preregistered_validation_histories() -> list[e2.HistorySpec]:
    pair_map = _validation_pair_assignment_map()
    lifecycle_map = _validation_lifecycle_assignment_map()
    specs: list[e2.HistorySpec] = []
    for config in validation_truth_configs():
        for index, (b, o) in enumerate(_validation_replicas_for(config)):
            pair_template, pair_arm = pair_map.get((config.config_id, b, o), (None, None))
            lifecycle_variant = lifecycle_map.get((config.config_id, b, o))
            specs.append(e2.HistorySpec(config.config_id, index, b, o, pair_template, pair_arm, pair_template, lifecycle_variant))
    return specs


@contextmanager
def _validation_namespace():
    original_master_seed = e2.MASTER_SEED
    original_truth_configs = e2.truth_configs
    try:
        e2.MASTER_SEED = VALIDATION_MASTER_SEED
        e2.truth_configs = validation_truth_configs
        yield
    finally:
        e2.MASTER_SEED = original_master_seed
        e2.truth_configs = original_truth_configs


def _seed_record(config: e2.TruthConfig, spec: e2.HistorySpec) -> dict:
    return {
        "master_seed": VALIDATION_MASTER_SEED,
        "split": "validation",
        "scenario_seed": e2.derive_seed(VALIDATION_MASTER_SEED, "validation", spec.config_id, "scenario"),
        "person_seed": e2.derive_seed(VALIDATION_MASTER_SEED, "validation", config.person_key, "person"),
        "behavior_seed": e2.derive_seed(VALIDATION_MASTER_SEED, "validation", spec.config_id, "behavior", spec.behavior_replica),
        "observation_seed": e2.derive_seed(VALIDATION_MASTER_SEED, "validation", spec.config_id, "observation", spec.observation_replica),
    }


def _preregistration(specs: list[e2.HistorySpec]) -> dict:
    configs = _validation_config_map()
    histories = []
    units = []
    with _validation_namespace():
        for spec in specs:
            config = configs[spec.config_id]
            case_id = e2.case_id_for_spec(spec)
            times = e2._checkpoint_times(config)
            answers = e2._answer_plan(config, spec)
            ident = e2._identifiability_plan(config, spec)
            checkpoint_ids = [e2.opaque("cp", f"{spec.config_id}:{spec.history_index}:{i}") for i in range(len(times))]
            unit_ids = [e2.opaque("unit", f"{spec.config_id}:{spec.history_index}:{i}") for i in range(len(times))]
            histories.append({
                "case_id": case_id,
                "history_id": e2.opaque("history", f"validation:{spec.config_id}:{spec.history_index}"),
                "person_id": e2.opaque("person", config.person_key),
                "truth_config_id": spec.config_id,
                "split": "validation",
                "risk_class": config.risk_class,
                "history_regime": config.history_regime,
                "families": list(config.families),
                "behavior_replica": spec.behavior_replica,
                "observation_replica": spec.observation_replica,
                "seeds": _seed_record(config, spec),
                "pair_id": e2.PAIR_IDS.get(spec.pair_template) if spec.pair_template else None,
                "pair_template": spec.pair_template,
                "pair_arm": spec.pair_arm,
                "lifecycle_variant": spec.lifecycle_variant,
                "checkpoint_ids": checkpoint_ids,
                "evaluation_unit_ids": unit_ids,
            })
            for i, (when, answer, ident_value) in enumerate(zip(times, answers, ident)):
                units.append({
                    "evaluation_unit_id": unit_ids[i],
                    "case_id": case_id,
                    "checkpoint_id": checkpoint_ids[i],
                    "time": when,
                    "semantic_question": "active personal-pattern claim at checkpoint",
                    "expected_answer": answer,
                    "identifiability": ident_value,
                    "families": list(config.families),
                    "negative_denominator": answer != "SUPPORTED",
                })
    return {
        "benchmark_version": VERSION,
        "generator_version": GENERATOR_VERSION,
        "starting_commit": STARTING_COMMIT,
        "split": "validation",
        "master_seed": VALIDATION_MASTER_SEED,
        "registered_before_generation": True,
        "reroll_count": 0,
        "persons": sorted({e2.opaque("person", c.person_key) for c in validation_truth_configs()}),
        "truth_configurations": [
            {
                "truth_config_id": config.config_id,
                "person_id": e2.opaque("person", config.person_key),
                "risk_class": config.risk_class,
                "history_regime": config.history_regime,
                "families": list(config.families),
            }
            for config in validation_truth_configs()
        ],
        "risk_allocation": {
            "STANDARD": sum(1 for c in validation_truth_configs() if c.risk_class == "STANDARD"),
            "HIGH-RISK": sum(1 for c in validation_truth_configs() if c.risk_class == "HIGH-RISK"),
        },
        "histories": histories,
        "evaluation_units": units,
        "negative_denominator_unit_ids": [u["evaluation_unit_id"] for u in units if u["negative_denominator"]],
    }


def _generate_validation_case(spec: e2.HistorySpec) -> dict:
    with _validation_namespace():
        case = e2.generate_case(spec)
    case["seeds"] = _seed_record(case["config"], spec)
    return case


def _dev_canonical_paths(root: Path) -> list[Path]:
    return [
        root / "specs" / "dev_scenario_registry.json",
        root / "manifests" / "dev_manifest.json",
        root / "manifests" / "public_benchmark_manifest.json",
    ] + sorted((root / "generated" / "dev" / "cases").glob("*/history.json")) + sorted((root / "generated" / "dev" / "cases").glob("*/checkpoints.json")) + sorted((root / "evaluator" / "dev" / "truth").glob("*.json")) + sorted((root / "evaluator" / "dev" / "expected").glob("*.json"))


def _hash_files(paths: list[Path], root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.exists()
    }


def _dev_identity_snapshot(root: Path) -> dict:
    registry_path = root / "specs" / "dev_scenario_registry.json"
    if not registry_path.exists():
        return {"present": False}
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return {
        "present": True,
        "master_seed": registry.get("master_seed"),
        "persons": sorted(registry.get("persons", [])),
        "truth_config_ids": sorted(c["truth_config_id"] for c in registry.get("truth_configurations", [])),
        "history_ids": sorted(h.get("history_id") for h in registry.get("histories", []) if h.get("history_id")),
        "case_ids": sorted(h["case_id"] for h in registry.get("histories", [])),
        "registry_hash": e2.semantic_hash(registry),
        "reroll_count": registry.get("reroll_count"),
    }


def _dev_immutability(before_hashes: dict[str, str], before_identity: dict, root: Path) -> dict:
    after_hashes = _hash_files(_dev_canonical_paths(root), root)
    after_identity = _dev_identity_snapshot(root)
    changed = sorted(path for path, digest in after_hashes.items() if before_hashes.get(path) != digest)
    missing = sorted(path for path in before_hashes if path not in after_hashes)
    added = sorted(path for path in after_hashes if path not in before_hashes)
    return {
        "baseline_artifact_count": len(before_hashes),
        "current_artifact_count": len(after_hashes),
        "changed_artifacts": changed,
        "missing_dev_artifacts": missing,
        "added_dev_artifacts": added,
        "canonical_dev_unchanged": not changed and not missing and not added,
        "master_seed_unchanged": before_identity.get("master_seed") == after_identity.get("master_seed") == e2.MASTER_SEED,
        "registry_unchanged": before_identity.get("registry_hash") == after_identity.get("registry_hash"),
        "seed_registry_unchanged": before_identity.get("master_seed") == after_identity.get("master_seed"),
        "case_registry_unchanged": before_identity.get("case_ids") == after_identity.get("case_ids"),
        "before": before_identity,
        "after": after_identity,
    }


def _pair_manifest(cases: list[dict]) -> dict:
    pairs = []
    for template in e2.PAIR_TEMPLATES:
        arm_a, arm_b = e2._pair_cases(cases, template)
        pairs.append({
            "pair_id": e2.PAIR_IDS[template],
            "template": template,
            "case_a": arm_a["case_id"],
            "case_b": arm_b["case_id"],
            "split": "validation",
            "held_constant_paths": list(e2.PAIR_CONTRACTS[template].held_constant_paths),
            "allowed_changed_paths": list(e2.PAIR_CONTRACTS[template].allowed_changed_paths),
            "required_changed_paths": list(e2.PAIR_CONTRACTS[template].required_changed_paths),
            "arm_hashes": {arm_a["spec"].pair_arm: e2.semantic_hash(e2.evaluator_truth(arm_a)), arm_b["spec"].pair_arm: e2.semantic_hash(e2.evaluator_truth(arm_b))},
        })
    return {"benchmark_version": VERSION, "split": "validation", "pair_count": len(pairs), "pairs": pairs}


def _validation_manifest(preregistration: dict, cases: list[dict], prereg_evidence: dict) -> dict:
    manifest = copy.deepcopy(preregistration)
    manifest.update({
        "registration_hash": prereg_evidence["registration_hash"],
        "registered_history_count": len(preregistration["histories"]),
        "generated_history_count": len(cases),
        "retained_history_count": len(cases),
        "pair_instances": _pair_manifest(cases)["pairs"],
    })
    return manifest


def _validation_public_manifest(cases: list[dict], root: Path) -> dict:
    return {
        "benchmark_version": VERSION,
        "split": "validation",
        "cases": [
            {
                "case_id": c["case_id"],
                "history_path": str((root / "generated" / "validation" / "cases" / c["case_id"] / "history.json").relative_to(root)).replace("\\", "/"),
                "checkpoints_path": str((root / "generated" / "validation" / "cases" / c["case_id"] / "checkpoints.json").relative_to(root)).replace("\\", "/"),
                "history_hash": e2.semantic_hash(e2.method_visible_case(c)),
                "checkpoint_hash": e2.semantic_hash(e2.checkpoint_requests(c)),
            }
            for c in cases
        ],
    }


def _qa(cases: list[dict], preregistration: dict, prereg_evidence: dict, root: Path, dev_immutability: dict) -> dict:
    dev_identity = dev_immutability["after"]
    l2_errors = {c["case_id"]: validate_fixture(c["fixture"]) for c in cases}
    visible_blobs = [e2.method_visible_case(c) | {"checkpoints": e2.checkpoint_requests(c)["checkpoints"]} for c in cases]
    leak_violations = {
        c["case_id"]: sorted(term for term in e2.LEAK_TERMS if term in json.dumps(e2.method_visible_case(c) | e2.checkpoint_requests(c), sort_keys=True).lower())
        for c in cases
    }
    pair_reports = e2._strong_pair_reports(cases)
    pair_pass_count = sum(1 for r in pair_reports.values() if r["pass"])
    paired_cases = [c for c in cases if c["spec"].pair_template]
    templates = {c["spec"].pair_template for c in paired_cases}
    seed_tuples = {(c["spec"].config_id, c["spec"].behavior_replica, c["spec"].observation_replica) for c in cases}
    expected_seed_tuples = {(config.config_id, b, o) for config in validation_truth_configs() for b, o in _validation_replicas_for(config)}
    expected_seed_values = {c["seeds"]["master_seed"] for c in cases}

    checkpoint_future_leaks: list[dict] = []
    for c in cases:
        records = c["fixture"]["records"]
        for cp in c["checkpoints"]:
            cutoff = e2.datetime.fromisoformat(cp["time"].replace("Z", "+00:00"))
            expected_visible = [
                record["event_id"]
                for record in records
                if e2.datetime.fromisoformat(record["time"]["ingested_time"].replace("Z", "+00:00")) <= cutoff
            ]
            if cp["visible_event_ids"] != expected_visible:
                checkpoint_future_leaks.append({
                    "case_id": c["case_id"],
                    "checkpoint_id": cp["checkpoint_id"],
                    "expected_visible": expected_visible,
                    "actual_visible": cp["visible_event_ids"],
                })

    sample_config = validation_truth_configs()[0]
    with _validation_namespace():
        same_seed_a = e2.generate_case(e2.HistorySpec(sample_config.config_id, 100, 0, 0))
        same_seed_b = e2.generate_case(e2.HistorySpec(sample_config.config_id, 100, 0, 0))
        obs_a = e2.generate_case(e2.HistorySpec(sample_config.config_id, 101, 0, 0))
        obs_b = e2.generate_case(e2.HistorySpec(sample_config.config_id, 101, 0, 1))
        beh_a = e2.generate_case(e2.HistorySpec(sample_config.config_id, 102, 0, 0))
        beh_b = e2.generate_case(e2.HistorySpec(sample_config.config_id, 102, 1, 0))
    seed_isolation = {
        "same_tuple_stable": e2.semantic_hash(e2.evaluator_truth(same_seed_a)) == e2.semantic_hash(e2.evaluator_truth(same_seed_b)),
        "observation_seed_keeps_truth_opportunity_behavior": obs_a["truth"] == obs_b["truth"] and obs_a["opportunities"] == obs_b["opportunities"] and obs_a["behavior"] == obs_b["behavior"] and e2.semantic_hash(e2.method_visible_case(obs_a)) != e2.semantic_hash(e2.method_visible_case(obs_b)),
        "behavior_seed_keeps_truth_opportunity": beh_a["truth"] == beh_b["truth"] and beh_a["opportunities"] == beh_b["opportunities"] and e2.semantic_hash(beh_a["behavior"]) != e2.semantic_hash(beh_b["behavior"]),
        "validation_seed_namespace": expected_seed_values == {VALIDATION_MASTER_SEED} and VALIDATION_MASTER_SEED != e2.MASTER_SEED,
    }

    def pair_arms(template: str) -> tuple[dict, dict]:
        return e2._pair_cases(cases, template)

    correction_case = pair_arms("correction_absent_vs_correction_applied")[1]
    deletion_case = pair_arms("deletion_absent_vs_deletion_applied")[1]
    drift_case = pair_arms("true_drift_vs_observation_only_change")[0]
    fake_drift_a, fake_drift_b = pair_arms("stable_behavior_vs_fake_drift")
    reversal_case = next(c for c in cases if c["spec"].lifecycle_variant == "reversal")
    reset_case = next(c for c in cases if c["spec"].lifecycle_variant == "reset")
    supersession_case = next(c for c in cases if c["spec"].lifecycle_variant == "supersession_invalidation")
    stale_case = next(c for c in cases if c["spec"].lifecycle_variant == "staleness")

    def relation_types(case: dict) -> set[str]:
        return e2._relation_types(case)

    def operations(case: dict) -> set[str]:
        return {event.get("payload", {}).get("operation") for event in e2._control_events(case)}

    def no_supported_after_control(case: dict) -> bool:
        controls = e2._control_events(case)
        if not controls:
            return False
        first_control = min(e2.datetime.fromisoformat(event["time"]["ingested_time"].replace("Z", "+00:00")) for event in controls)
        later = [cp for cp in case["checkpoints"] if e2.datetime.fromisoformat(cp["time"].replace("Z", "+00:00")) >= first_control]
        return bool(later) and all(cp["expected_answer"] != "SUPPORTED" for cp in later)

    drift_mid = len(drift_case["behavior"]) // 2
    reversal_mid = len(reversal_case["behavior"]) // 2
    lifecycle_checks = {
        "correction_control_present": "CORRECTS" in relation_types(correction_case),
        "rejection_state_present": "reject" in operations(correction_case) and "USER_REJECTED" in {cp["expected_answer"] for cp in correction_case["checkpoints"]},
        "supersession_present": "SUPERSEDES" in relation_types(supersession_case) and "SUPERSEDED" in {cp["expected_answer"] for cp in supersession_case["checkpoints"]},
        "invalidation_present": "INVALIDATES" in relation_types(supersession_case) and "invalidate" in operations(supersession_case),
        "deletion_present": "DELETES" in relation_types(deletion_case) and "remove" in operations(deletion_case) and "DELETED" in {cp["expected_answer"] for cp in deletion_case["checkpoints"]},
        "reset_present": "DELETES" in relation_types(reset_case) and "reset" in operations(reset_case) and "DELETED" in {cp["expected_answer"] for cp in reset_case["checkpoints"]},
        "true_drift_has_latent_transition": drift_case["truth"]["truth_kind"] == "DRIFT" and all(b["occurred"] for b in drift_case["behavior"][:drift_mid]) and not any(b["occurred"] for b in drift_case["behavior"][drift_mid:]),
        "reversal_has_latent_transition": reversal_case["truth"]["truth_kind"] == "REVERSAL" and all(b["occurred"] for b in reversal_case["behavior"][:reversal_mid]) and not any(b["occurred"] for b in reversal_case["behavior"][reversal_mid:]),
        "staleness_present": stale_case["checkpoints"][-1]["expected_answer"] == "STALE",
        "fake_drift_has_no_latent_transition": fake_drift_a["truth"]["truth_kind"] == "STABLE_PATTERN" and fake_drift_b["truth"]["truth_kind"] == "STABLE_PATTERN" and e2._behavior_semantics(fake_drift_a) == e2._behavior_semantics(fake_drift_b) and fake_drift_b["observation_provenance"]["observation_policy"] == "COVERAGE_COLLAPSE",
        "no_passive_resurrection": all(no_supported_after_control(c) for c in (correction_case, deletion_case, reset_case, supersession_case)),
    }

    cf14_a, cf14_b = pair_arms("independent_corroboration_vs_same_origin_replication")
    cf03_a, cf03_b = pair_arms("single_evidence_vs_same_origin_replicas")
    cf13_a, cf13_b = pair_arms("raw_only_vs_raw_plus_derived_lineage")
    cf12_b = pair_arms("known_relationship_vs_unknown_relationship")[1]

    def has_relation(case: dict, relation_type: str) -> bool:
        return relation_type in relation_types(case)

    evidence_checks = {
        "same_origin_replica_not_new_behavior": has_relation(cf03_b, "SAME_ORIGIN_REPLICATED") and e2._behavior_semantics(cf03_a) == e2._behavior_semantics(cf03_b),
        "raw_derived_not_new_behavior": any(event["evidence_kind"] == "DERIVED_OBSERVATION" for event in cf13_b["fixture"]["records"]) and e2._behavior_semantics(cf13_a) == e2._behavior_semantics(cf13_b),
        "independent_and_same_origin_distinguished": len(cf14_a["fixture"]["records"]) == len(cf14_b["fixture"]["records"]) and e2._behavior_semantics(cf14_a) == e2._behavior_semantics(cf14_b) and has_relation(cf14_a, "INDEPENDENT_CORROBORATION") and not has_relation(cf14_a, "SAME_ORIGIN_REPLICATED") and has_relation(cf14_b, "SAME_ORIGIN_REPLICATED") and not has_relation(cf14_b, "INDEPENDENT_CORROBORATION"),
        "unknown_relationship_remains_unknown": any(event.get("context", {}).get("relationship", {}).get("status") == "UNKNOWN" for event in cf12_b["fixture"]["records"]),
    }

    family_evidence = {
        "routine": any(c["truth"]["truth_kind"] in {"STABLE_PATTERN", "STABLE_ROUTINE"} and "routine/opportunity" in c["config"].families for c in cases),
        "preference": any(c["truth"]["truth_kind"] == "PREFERENCE" and any(len(o["alternatives"]) > 1 for o in c["opportunities"]) for c in cases),
        "conditional_context_dependent_truth": any(c["spec"].pair_template == "conditional_truth_vs_misleading_aggregate" for c in cases),
        "relationship_conditioned": any(c["truth"]["truth_kind"] == "RELATIONSHIP_CONDITIONED" for c in cases),
        "temporal_sequence_association": any("temporal sequence" in c["config"].families and len(c["opportunities"]) >= 16 for c in cases),
        "exception": any(c["truth"]["truth_kind"] == "SCOPED_EXCEPTION" for c in cases),
        "drift": lifecycle_checks["true_drift_has_latent_transition"],
        "reversal": lifecycle_checks["reversal_has_latent_transition"],
        "no_pattern": any(c["truth"]["truth_kind"] == "NO_PATTERN" for c in cases),
        "insufficient_conflicting_support": any(cp["expected_answer"] in {"INSUFFICIENT_EVIDENCE", "CONFLICTING_EVIDENCE"} for c in cases for cp in c["checkpoints"]),
        "observability_loss": any(event["evidence_kind"] == "OBSERVABILITY_RECORD" for c in cases for event in c["fixture"]["records"]),
        "quality_degradation": any(event.get("quality", {}).get("quality_state") == "DEGRADED" for c in cases for event in c["fixture"]["records"]),
        "same_origin_replication": evidence_checks["same_origin_replica_not_new_behavior"],
        "independent_corroboration": has_relation(cf14_a, "INDEPENDENT_CORROBORATION"),
        "correction_rejection": lifecycle_checks["correction_control_present"] and lifecycle_checks["rejection_state_present"],
        "deletion_reset": lifecycle_checks["deletion_present"] and lifecycle_checks["reset_present"],
        "unknown_relationship": evidence_checks["unknown_relationship_remains_unknown"],
        "raw_derived_evidence": evidence_checks["raw_derived_not_new_behavior"],
        "confounding_misleading_aggregate": any(c["spec"].pair_template == "conditional_truth_vs_misleading_aggregate" and {o["context"]["segment"] for o in c["opportunities"]} == {"context-a", "context-b"} for c in cases),
        "fake_drift": lifecycle_checks["fake_drift_has_no_latent_transition"],
    }

    registered_case_ids = {h["case_id"] for h in preregistration["histories"]}
    generated_case_ids = {c["case_id"] for c in cases}
    registered_units = {u["evaluation_unit_id"]: u for u in preregistration["evaluation_units"]}
    actual_units = {cp["evaluation_unit_id"]: cp for c in cases for cp in c["checkpoints"]}
    registered_negative = set(preregistration["negative_denominator_unit_ids"])
    actual_negative = {unit_id for unit_id, cp in actual_units.items() if cp["expected_answer"] != "SUPPORTED"}
    registration_matches_generation = registered_case_ids == generated_case_ids and set(registered_units) == set(actual_units)
    registration_checkpoint_semantics_match = all(
        registered_units[unit_id]["expected_answer"] == cp["expected_answer"]
        and registered_units[unit_id]["identifiability"] == cp["identifiability"]
        and registered_units[unit_id]["checkpoint_id"] == cp["checkpoint_id"]
        for unit_id, cp in actual_units.items()
    )

    dev_persons = set(dev_identity.get("persons", []))
    dev_configs = set(dev_identity.get("truth_config_ids", []))
    dev_histories = set(dev_identity.get("history_ids", []))
    dev_cases = set(dev_identity.get("case_ids", []))
    val_persons = set(preregistration["persons"])
    val_configs = {c["truth_config_id"] for c in preregistration["truth_configurations"]}
    val_histories = {h["history_id"] for h in preregistration["histories"]}
    val_cases = {h["case_id"] for h in preregistration["histories"]}
    split_overlap = {
        "dev_person_overlap": sorted(dev_persons & val_persons),
        "dev_truth_config_overlap": sorted(dev_configs & val_configs),
        "dev_history_overlap": sorted(dev_histories & val_histories),
        "dev_case_id_overlap": sorted(dev_cases & val_cases),
    }

    oracle_source = inspect.getsource(e2._answer_plan) + inspect.getsource(e2.checkpoint_oracle)
    oracle_generic_threshold_found = bool(re.search(r"occurrences\s*>?=|confidence\s*[><=]|pattern_score|classifier|frequency\s*[><=]|ratio\s*[><=]|probability\s*[><=]", oracle_source, re.I))
    with tempfile.TemporaryDirectory() as tmp:
        e2_regression = e2.run_e2(Path(tmp) / "ppf_l3")
    e2_cf_pair_reports = e2._strong_pair_reports([e2.generate_case(spec) for spec in e2.preregistered_histories()])
    e2_cf_mutations = e2.counterfactual_contract_mutation_results()
    regression_checks = {
        "l2_60_and_8": ppf_l2_validate.main() == 0,
        "e0": e0.run_e0().get("status") == "PASS",
        "e1": (lambda result: result.get("status") == "PASS" and all(result.get("gates", {}).values()))(e1.run_e1()),
        "e2": e2_regression.get("status") == "PASS" and all(e2_regression.get("qa", {}).get("e2_gates", {}).values()),
        "e2_cf_a": len(e2_cf_pair_reports) == 14 and all(report["pass"] for report in e2_cf_pair_reports.values()) and e2_cf_mutations["status"] == "PASS",
    }

    tracked = subprocess.run(["git", "diff", "--name-only", STARTING_COMMIT, "--"], cwd=ROOT, check=True, capture_output=True, text=True)
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, check=True, capture_output=True, text=True)
    changed = {p.strip().replace("\\", "/") for p in tracked.stdout.splitlines() if p.strip()}
    changed.update(p.strip().replace("\\", "/") for p in untracked.stdout.splitlines() if p.strip())
    allowed_prefixes = ("docs/research/", "tools/research/ppf_l3/", "tests/research/ppf_l3/", "benchmarks/ppf_l3/")
    scope_violations = sorted(p for p in changed if not p.startswith(allowed_prefixes))
    final_paths = [root / "generated" / "final", root / "evaluator" / "final"]
    final_artifacts_present = any(path.exists() for path in final_paths)
    recognizer_or_l4_paths = sorted(p for p in changed if "recognizer" in p.lower() or "/l4" in p.lower() or "\\l4" in p.lower())

    qa_checks = {
        "allocation": len(preregistration["persons"]) == 6 and len(preregistration["truth_configurations"]) == 7 and len(cases) == 38,
        "replication": sum(1 for c in cases if c["config"].risk_class == "STANDARD") == 20 and sum(1 for c in cases if c["config"].risk_class == "HIGH-RISK") == 18 and seed_tuples == expected_seed_tuples,
        "split_disjointness": not any(split_overlap.values()),
        "l2_validity": not any(l2_errors.values()),
        "family_coverage": all(family_evidence.values()),
        "counterfactual_template_coverage": templates == set(e2.PAIR_TEMPLATES) and len(pair_reports) == 14,
        "hardened_pair_contracts": pair_pass_count == 14 and all(not r["held_constant_violations"] and not r["unexpected_changed_paths"] and not r["missing_required_changes"] for r in pair_reports.values()),
        "seed_isolation": all(seed_isolation.values()),
        "checkpoint_future_leakage": not checkpoint_future_leaks,
        "oracle_boundary": not oracle_generic_threshold_found,
        "identifiability": {cp["identifiability"] for c in cases for cp in c["checkpoints"]} == {"YES", "PARTIAL", "NO"} and all(cp["expected_answer"] != "SUPPORTED" for c in cases for cp in c["checkpoints"] if cp["identifiability"] == "NO"),
        "negative_denominator": registered_negative == actual_negative and bool(registered_negative),
        "lifecycle": all(lifecycle_checks.values()),
        "evidence_non_inflation": all(evidence_checks.values()),
        "no_cherry_picking": prereg_evidence.get("written_before_generation") and registration_matches_generation and registration_checkpoint_semantics_match and len(cases) == 38 and preregistration.get("reroll_count") == 0,
        "truth_leakage": not any(leak_violations.values()),
        "dev_immutability": dev_immutability["canonical_dev_unchanged"],
        "regression": all(regression_checks.values()),
        "validation_only_scope": not final_artifacts_present and not recognizer_or_l4_paths and not scope_violations,
    }
    e3_gates = {f"E3-G{i}": qa_checks[name] for i, name in enumerate((
        "allocation",
        "replication",
        "split_disjointness",
        "l2_validity",
        "family_coverage",
        "counterfactual_template_coverage",
        "hardened_pair_contracts",
        "seed_isolation",
        "checkpoint_future_leakage",
        "oracle_boundary",
        "identifiability",
        "negative_denominator",
        "lifecycle",
        "evidence_non_inflation",
        "no_cherry_picking",
        "truth_leakage",
        "dev_immutability",
        "regression",
        "validation_only_scope",
    ), start=1)}
    return {
        "benchmark_version": VERSION,
        "split": "validation",
        "status": "PASS" if all(qa_checks.values()) and all(e3_gates.values()) else "REVISE",
        "e3_gates": e3_gates,
        "qa_checks": qa_checks,
        "l2_errors": l2_errors,
        "pair_reports": pair_reports,
        "pair_pass_count": pair_pass_count,
        "split_overlap": split_overlap,
        "seed_isolation": seed_isolation,
        "checkpoint_future_leak_violations": checkpoint_future_leaks,
        "truth_leak_violations": leak_violations,
        "family_evidence": family_evidence,
        "lifecycle_checks": lifecycle_checks,
        "evidence_non_inflation": evidence_checks,
        "dev_immutability": dev_immutability,
        "regression_checks": regression_checks,
        "oracle_generic_threshold_found": oracle_generic_threshold_found,
        "scope_violations": scope_violations,
        "recognizer_or_l4_paths": recognizer_or_l4_paths,
        "registered_negative_denominator": len(registered_negative),
        "method_visible_hash": e2.semantic_hash(visible_blobs),
    }


def _summary(cases: list[dict], qa: dict, preregistration: dict) -> dict:
    checkpoints = sum(len(c["checkpoints"]) for c in cases)
    ident = {k: sum(1 for c in cases for cp in c["checkpoints"] if cp["identifiability"] == k) for k in ("YES", "PARTIAL", "NO")}
    regimes = {k: sum(1 for c in cases if c["config"].history_regime == k) for k in ("SHORT", "MEDIUM", "LONG")}
    valid_events = sum(len(c["fixture"]["records"]) for c in cases if not qa["l2_errors"][c["case_id"]])
    paired_histories = sum(1 for c in cases if c["spec"].pair_template)
    return {
        "benchmark_version": VERSION,
        "status": qa["status"],
        "split": "validation",
        "persons": len(preregistration["persons"]),
        "truth_configs": len(preregistration["truth_configurations"]),
        "standard_configs": sum(1 for c in validation_truth_configs() if c.risk_class == "STANDARD"),
        "high_risk_configs": sum(1 for c in validation_truth_configs() if c.risk_class == "HIGH-RISK"),
        "histories": len(cases),
        "standard_histories": sum(1 for c in cases if c["config"].risk_class == "STANDARD"),
        "high_risk_histories": sum(1 for c in cases if c["config"].risk_class == "HIGH-RISK"),
        "visible_events": sum(len(c["fixture"]["records"]) for c in cases),
        "l2_valid_events": valid_events,
        "checkpoints": checkpoints,
        "evaluation_units": checkpoints,
        "history_regime_counts": regimes,
        "counterfactual_template_count": len({c["spec"].pair_template for c in cases if c["spec"].pair_template}),
        "pair_instance_count": len(qa["pair_reports"]),
        "paired_history_count": paired_histories,
        "identifiability_distribution": ident,
        "negative_denominator_count": qa["registered_negative_denominator"],
        "seed_isolation": qa["seed_isolation"],
        "pair_qa_summary": {
            "pair_pass_count": qa["pair_pass_count"],
            "pair_count": len(qa["pair_reports"]),
            "held_constant_violations": sum(len(r["held_constant_violations"]) for r in qa["pair_reports"].values()),
            "unexpected_changed_paths": sum(len(r["unexpected_changed_paths"]) for r in qa["pair_reports"].values()),
            "missing_required_changes": sum(len(r["missing_required_changes"]) for r in qa["pair_reports"].values()),
        },
        "lifecycle_summary": qa["lifecycle_checks"],
        "evidence_non_inflation": qa["evidence_non_inflation"],
        "truth_leak_count": sum(1 for leaks in qa["truth_leak_violations"].values() if leaks),
        "future_leak_count": len(qa["checkpoint_future_leak_violations"]),
        "reroll_count": preregistration["reroll_count"],
        "dev_hash_comparison": qa["dev_immutability"],
        "split_overlap_counts": {key: len(value) for key, value in qa["split_overlap"].items()},
        "e3_gates": qa["e3_gates"],
    }


def generate_validation(root: Path = BENCH_ROOT) -> dict:
    before_hashes = _hash_files(_dev_canonical_paths(root), root)
    before_identity = _dev_identity_snapshot(root)
    specs = preregistered_validation_histories()
    preregistration = _preregistration(specs)
    for child in ("generated/validation", "evaluator/validation"):
        target = root / child
        if target.exists():
            shutil.rmtree(target)
    for stale in (
        "specs/validation_scenario_registry.json",
        "manifests/validation_manifest.json",
        "manifests/validation_public_manifest.json",
        "reports/validation_generator_qa.json",
        "reports/validation_dataset_summary.json",
    ):
        target = root / stale
        if target.exists():
            target.unlink()
    (root / "specs").mkdir(parents=True, exist_ok=True)
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    registration_path = root / "specs" / "validation_scenario_registry.json"
    e2.write_json(registration_path, preregistration)
    persisted_registration = json.loads(registration_path.read_text(encoding="utf-8"))
    prereg_evidence = {
        "written_before_generation": e2.semantic_hash(persisted_registration) == e2.semantic_hash(preregistration),
        "registration_hash": e2.semantic_hash(persisted_registration),
    }
    cases = [_generate_validation_case(spec) for spec in specs]
    prereg_evidence["generated_history_count"] = len(cases)
    for c in cases:
        case_dir = root / "generated" / "validation" / "cases" / c["case_id"]
        e2.write_json(case_dir / "history.json", e2.method_visible_case(c))
        e2.write_json(case_dir / "checkpoints.json", e2.checkpoint_requests(c))
        e2.write_json(root / "evaluator" / "validation" / "truth" / f"{c['case_id']}.json", e2.evaluator_truth(c))
        e2.write_json(root / "evaluator" / "validation" / "expected" / f"{c['case_id']}.json", e2.expected_answers(c))
    e2.write_json(root / "manifests" / "validation_manifest.json", _validation_manifest(preregistration, cases, prereg_evidence))
    e2.write_json(root / "manifests" / "validation_public_manifest.json", _validation_public_manifest(cases, root))
    dev_immutability = _dev_immutability(before_hashes, before_identity, root)
    qa = _qa(cases, preregistration, prereg_evidence, root, dev_immutability)
    summary = _summary(cases, qa, preregistration)
    e2.write_json(root / "reports" / "validation_generator_qa.json", qa)
    e2.write_json(root / "reports" / "validation_dataset_summary.json", summary)
    return summary | {"qa": qa}


def run_e3(root: Path = BENCH_ROOT) -> dict:
    return generate_validation(root)
