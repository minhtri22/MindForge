"""PPF-L3 E2 canonical DEV generation.

Research tooling only. This module generates the authorized DEV split from the
frozen L3 execution plan. It does not implement a recognizer, baseline, model,
kernel primitive, or runtime feature.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import random
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.research.ppf_l2_validation import validate_fixture

ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "benchmarks" / "ppf_l3"
VERSION = "ppf-l3-benchmark/v1"
GENERATOR_VERSION = "ppf-l3-e2-generator/1"
STARTING_COMMIT = "5a86b74ca7ec339f472a8e65c273dda6b0cc92a2"
MASTER_SEED = "mindforge-ppf-l3-e2-dev-v1"

PAIR_TEMPLATES = (
    "full_observability_vs_permission_loss",
    "normal_quality_vs_degraded_quality",
    "single_evidence_vs_same_origin_replicas",
    "true_routine_vs_chance_matching_no_pattern",
    "stable_behavior_vs_fake_drift",
    "true_drift_vs_observation_only_change",
    "meaningful_alternatives_vs_constrained_availability",
    "conditional_truth_vs_misleading_aggregate",
    "stable_exception_vs_random_deviation",
    "correction_absent_vs_correction_applied",
    "deletion_absent_vs_deletion_applied",
    "known_relationship_vs_unknown_relationship",
    "raw_only_vs_raw_plus_derived_lineage",
    "independent_corroboration_vs_same_origin_replication",
)

PAIR_IDS = {template: f"CF-{i:02d}" for i, template in enumerate(PAIR_TEMPLATES, start=1)}
PAIR_LABELS = {
    "full_observability_vs_permission_loss": "full observability -> permission loss",
    "normal_quality_vs_degraded_quality": "normal -> degraded quality",
    "single_evidence_vs_same_origin_replicas": "single evidence -> same-origin replicas",
    "true_routine_vs_chance_matching_no_pattern": "true routine -> chance-matching NO_PATTERN",
    "stable_behavior_vs_fake_drift": "stable coverage -> fake drift coverage collapse",
    "true_drift_vs_observation_only_change": "true drift -> observation-only change",
    "meaningful_alternatives_vs_constrained_availability": "meaningful alternatives -> constrained availability",
    "conditional_truth_vs_misleading_aggregate": "contextual slices -> misleading aggregate",
    "stable_exception_vs_random_deviation": "scoped exception -> random deviation",
    "correction_absent_vs_correction_applied": "no correction -> correction applied",
    "deletion_absent_vs_deletion_applied": "no deletion -> deletion applied",
    "known_relationship_vs_unknown_relationship": "known relationship -> hidden relationship identity",
    "raw_only_vs_raw_plus_derived_lineage": "raw only -> raw+derived lineage",
    "independent_corroboration_vs_same_origin_replication": "independent corroboration -> same-origin replication",
}

PAIR_HELD_CONSTANT = {
    "full_observability_vs_permission_loss": ("truth", "opportunities", "behavior"),
    "normal_quality_vs_degraded_quality": ("truth", "opportunities", "behavior"),
    "single_evidence_vs_same_origin_replicas": ("behavioral episode",),
    "true_routine_vs_chance_matching_no_pattern": ("observation policy", "record-count shape"),
    "stable_behavior_vs_fake_drift": ("behavior", "truth"),
    "true_drift_vs_observation_only_change": ("pre-change history shape",),
    "meaningful_alternatives_vs_constrained_availability": ("visible option frequency where possible",),
    "conditional_truth_vs_misleading_aggregate": ("aggregate count shape",),
    "stable_exception_vs_random_deviation": ("parent pattern",),
    "correction_absent_vs_correction_applied": ("underlying prior history",),
    "deletion_absent_vs_deletion_applied": ("pre-delete history",),
    "known_relationship_vs_unknown_relationship": ("behavior",),
    "raw_only_vs_raw_plus_derived_lineage": ("behavioral episode",),
    "independent_corroboration_vs_same_origin_replication": ("visible source count",),
}

PAIR_EXPECTED_EFFECT = {
    "full_observability_vs_permission_loss": "identifiability/status may change; latent behavior unchanged",
    "normal_quality_vs_degraded_quality": "support may weaken or abstain; truth unchanged",
    "single_evidence_vs_same_origin_replicas": "behavioral occurrence unchanged",
    "true_routine_vs_chance_matching_no_pattern": "positive truth changes",
    "stable_behavior_vs_fake_drift": "no behavioral drift",
    "true_drift_vs_observation_only_change": "only true-drift side changes latent behavior",
    "meaningful_alternatives_vs_constrained_availability": "preference identifiability/truth relation differs",
    "conditional_truth_vs_misleading_aggregate": "conditional truth must not collapse globally",
    "stable_exception_vs_random_deviation": "exception relation differs",
    "correction_absent_vs_correction_applied": "active semantic state changes",
    "deletion_absent_vs_deletion_applied": "active state becomes DELETED",
    "known_relationship_vs_unknown_relationship": "relationship-specific claim becomes UNKNOWN_CONTEXT",
    "raw_only_vs_raw_plus_derived_lineage": "recurrence truth unchanged",
    "independent_corroboration_vs_same_origin_replication": "evidentiary relation changes; episode does not multiply",
}

LEAK_TERMS = {
    "latent_truth",
    "expected_answer",
    "identifiability",
    "scenario_family",
    "truth_configuration",
    "behavior_seed",
    "observation_seed",
    "pair_id",
    "no_pattern",
    "fake_drift",
    "deleted",
    "user_rejected",
}


@dataclass(frozen=True)
class TruthConfig:
    config_id: str
    person_key: str
    risk_class: str
    families: tuple[str, ...]
    history_regime: str
    occurrence_plan: tuple[int, ...]
    alternatives: tuple[str, ...] = ("act", "not-act")
    truth_kind: str = "STABLE_PATTERN"
    identifiability: str = "YES"
    base_answer: str = "SUPPORTED"
    scope: str = "activity:generic"


@dataclass(frozen=True)
class HistorySpec:
    config_id: str
    history_index: int
    behavior_replica: int
    observation_replica: int
    pair_template: str | None = None
    pair_arm: str | None = None
    controlled_variable: str | None = None
    lifecycle_variant: str | None = None


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def derive_seed(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256(canonical_bytes([str(p) for p in parts])).digest()[:8], "big")


def opaque(kind: str, value: str) -> str:
    return f"{kind}-{hashlib.sha256(f'{VERSION}|{kind}|{value}'.encode('utf-8')).hexdigest()[:12]}"


def iso(base: datetime, minutes: int) -> str:
    return (base + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def _repeat_plan(pattern: tuple[int, ...], length: int) -> tuple[int, ...]:
    return tuple(pattern[i % len(pattern)] for i in range(length))


def truth_configs() -> list[TruthConfig]:
    return [
        TruthConfig("tc-s01", "p1", "STANDARD", ("routine/opportunity", "temporal sequence"), "MEDIUM", _repeat_plan((1, 1, 0, 1, 1, 0, 1, 1), 20)),
        TruthConfig("tc-s02", "p2", "STANDARD", ("preference/availability", "conditional preference"), "MEDIUM", (1,) * 20, ("tea", "coffee", "water"), truth_kind="PREFERENCE", scope="choice:drink"),
        TruthConfig("tc-s03", "p3", "STANDARD", ("relationship-conditioned", "unknown context"), "MEDIUM", _repeat_plan((1, 1, 1, 0, 1, 1, 0, 1), 20), truth_kind="RELATIONSHIP_CONDITIONED", scope="activity:relationship"),
        TruthConfig("tc-s04", "p4", "STANDARD", ("exception", "scoped exception", "lifecycle parent relation"), "LONG", _repeat_plan((1, 1, 1, 1, 0, 1, 1, 1), 56)),
        TruthConfig("tc-s05", "p5", "STANDARD", ("multi-device replication", "independent corroboration", "raw/derived evidence"), "MEDIUM", (1,) + (0,) * 19, truth_kind="SINGLE_OCCURRENCE", base_answer="INSUFFICIENT_EVIDENCE"),
        TruthConfig("tc-h01", "p6", "HIGH-RISK", ("confounding", "Simpson-like aggregation", "sparse coincidence", "NO_PATTERN controls", "multi-device replication", "independent corroboration"), "SHORT", (1, 0, 1, 0, 0, 1, 0, 0), truth_kind="NO_PATTERN", identifiability="PARTIAL", base_answer="INSUFFICIENT_EVIDENCE"),
        TruthConfig("tc-h02", "p2", "HIGH-RISK", ("real drift", "coverage-induced fake drift", "reversal", "missingness", "observation quality", "unidentifiable latent truth", "pattern overlap", "conflicting structure", "correction/rejection", "deletion/reset", "staleness"), "LONG", _repeat_plan((1, 1, 1, 1, 0, 0, 0, 1), 56), truth_kind="DRIFT_OR_UNIDENTIFIABLE", identifiability="NO", base_answer="NOT_OBSERVABLE"),
    ]


def _replicas_for(config: TruthConfig) -> list[tuple[int, int]]:
    reps = (0, 1, 2) if config.risk_class == "HIGH-RISK" else (0, 1)
    return [(b, o) for b in reps for o in reps]


def _pair_assignment_map() -> dict[tuple[str, int, int], tuple[str, str]]:
    assignments: dict[tuple[str, int, int], tuple[str, str]] = {}
    def add(config_id: str, seed_a: tuple[int,int], seed_b: tuple[int,int], template: str) -> None:
        assignments[(config_id, *seed_a)] = (template, "A")
        assignments[(config_id, *seed_b)] = (template, "B")
    add("tc-s01", (0,0), (0,1), "full_observability_vs_permission_loss")
    add("tc-s01", (1,0), (1,1), "normal_quality_vs_degraded_quality")
    add("tc-s02", (0,0), (0,1), "meaningful_alternatives_vs_constrained_availability")
    add("tc-s03", (0,0), (0,1), "known_relationship_vs_unknown_relationship")
    add("tc-s04", (0,0), (0,1), "stable_exception_vs_random_deviation")
    add("tc-s04", (1,0), (1,1), "correction_absent_vs_correction_applied")
    add("tc-s05", (0,0), (0,1), "single_evidence_vs_same_origin_replicas")
    add("tc-s05", (1,0), (1,1), "raw_only_vs_raw_plus_derived_lineage")
    add("tc-h01", (0,0), (0,1), "true_routine_vs_chance_matching_no_pattern")
    add("tc-h01", (1,0), (1,1), "conditional_truth_vs_misleading_aggregate")
    add("tc-h01", (2,0), (2,1), "independent_corroboration_vs_same_origin_replication")
    add("tc-h02", (0,0), (0,1), "stable_behavior_vs_fake_drift")
    add("tc-h02", (1,0), (1,1), "true_drift_vs_observation_only_change")
    add("tc-h02", (2,0), (2,1), "deletion_absent_vs_deletion_applied")
    return assignments


def _lifecycle_assignment_map() -> dict[tuple[str,int,int], str]:
    return {
        ("tc-s02", 1, 0): "staleness",
        ("tc-s03", 1, 0): "reversal",
        ("tc-h02", 0, 2): "correction_high_risk",
        ("tc-h02", 1, 2): "reset",
        ("tc-h02", 2, 2): "supersession_invalidation",
    }


def preregistered_histories() -> list[HistorySpec]:
    pair_map = _pair_assignment_map()
    lifecycle_map = _lifecycle_assignment_map()
    specs: list[HistorySpec] = []
    for config in truth_configs():
        for index, (b, o) in enumerate(_replicas_for(config)):
            pair_template, pair_arm = pair_map.get((config.config_id, b, o), (None, None))
            lifecycle_variant = lifecycle_map.get((config.config_id, b, o))
            specs.append(HistorySpec(config.config_id, index, b, o, pair_template, pair_arm, pair_template, lifecycle_variant))
    return specs


def _config_map() -> dict[str, TruthConfig]:
    return {c.config_id: c for c in truth_configs()}


def truth_spec(config: TruthConfig, spec: HistorySpec) -> dict:
    truth_kind = config.truth_kind
    if spec.pair_template == "true_routine_vs_chance_matching_no_pattern":
        truth_kind = "STABLE_ROUTINE" if spec.pair_arm == "A" else "NO_PATTERN"
    elif spec.pair_template == "stable_behavior_vs_fake_drift":
        truth_kind = "STABLE_PATTERN"
    elif spec.pair_template == "true_drift_vs_observation_only_change":
        truth_kind = "DRIFT" if spec.pair_arm == "A" else "STABLE_PATTERN"
    elif spec.pair_template == "meaningful_alternatives_vs_constrained_availability":
        truth_kind = "PREFERENCE" if spec.pair_arm == "A" else "INSUFFICIENT_TRUE_SUPPORT"
    elif spec.pair_template == "conditional_truth_vs_misleading_aggregate":
        truth_kind = "CONDITIONAL_PATTERN" if spec.pair_arm == "A" else "NO_GLOBAL_PATTERN"
    elif spec.pair_template == "stable_exception_vs_random_deviation":
        truth_kind = "SCOPED_EXCEPTION" if spec.pair_arm == "A" else "RANDOM_DEVIATION"
    elif spec.lifecycle_variant == "reversal":
        truth_kind = "REVERSAL"
    return {
        "person_id": opaque("person", config.person_key),
        "truth_config_id": config.config_id,
        "truth_kind": truth_kind,
        "scope": config.scope,
        "families": list(config.families),
        "risk_class": config.risk_class,
        "history_regime": config.history_regime,
        "lifecycle_variant": spec.lifecycle_variant,
    }


def opportunity_sequence(config: TruthConfig, spec: HistorySpec, truth: dict) -> list[dict]:
    rng = random.Random(derive_seed(MASTER_SEED, config.config_id, config.person_key, "opportunity"))
    base = datetime(2026, 3, 1, 8, tzinfo=timezone.utc)
    result = []
    for i in range(len(config.occurrence_plan)):
        alternatives = list(config.alternatives)
        if spec.pair_template == "meaningful_alternatives_vs_constrained_availability" and spec.pair_arm == "B":
            alternatives = alternatives[:1]
        result.append({
            "opportunity_id": opaque("opp", f"{spec.config_id}:{spec.history_index}:{i}"),
            "phenomenon_time": iso(base, i * 35 + rng.randint(0, 3)),
            "alternatives": alternatives,
            "context": {
                "period": "morning" if i < 3 else "later",
                "relationship": "known" if not (spec.pair_template == "known_relationship_vs_unknown_relationship" and spec.pair_arm == "B") else "unknown",
                "segment": "context-a" if i % 2 == 0 else "context-b",
            },
        })
    return result


def behavior_realization(config: TruthConfig, spec: HistorySpec, opportunities: list[dict]) -> list[dict]:
    rng = random.Random(derive_seed(MASTER_SEED, config.config_id, "behavior", spec.behavior_replica))
    plan = list(config.occurrence_plan)
    if spec.pair_template == "true_routine_vs_chance_matching_no_pattern":
        plan = ([1, 1, 0, 1, 1, 0, 1, 1] if spec.pair_arm == "A" else [1, 0, 0, 1, 0, 0, 0, 1])[: len(plan)]
    if spec.pair_template == "stable_behavior_vs_fake_drift":
        plan = list(_repeat_plan((1, 1, 0, 1, 1, 0, 1, 1), len(plan)))
    if spec.pair_template == "conditional_truth_vs_misleading_aggregate":
        if spec.pair_arm == "A":
            plan = [1 if i % 2 == 0 else 0 for i in range(len(plan))]
        else:
            block = (1, 1, 0, 0, 1, 0, 0, 1)
            plan = list(_repeat_plan(block, len(plan)))
    if spec.pair_template == "stable_exception_vs_random_deviation" and spec.pair_arm == "A":
        plan = list(_repeat_plan((1, 1, 1, 0, 1, 1, 1, 1), len(plan)))
    if spec.pair_template == "stable_exception_vs_random_deviation" and spec.pair_arm == "B":
        plan = [1 if rng.random() > 0.45 else 0 for _ in plan]
    if spec.pair_template == "true_drift_vs_observation_only_change":
        midpoint = len(plan) // 2
        plan = [1] * midpoint + ([0] * (len(plan) - midpoint) if spec.pair_arm == "A" else [1] * (len(plan) - midpoint))
    if spec.lifecycle_variant == "reversal":
        midpoint = len(plan) // 2
        plan = [1] * midpoint + [0] * (len(plan) - midpoint)
    behavior = []
    for i, op in enumerate(opportunities):
        occurred = bool(plan[i])
        choice = op["alternatives"][0] if occurred and op["alternatives"] else None
        behavior.append({
            "opportunity_id": op["opportunity_id"],
            "occurred": occurred,
            "choice": choice,
            "phenomenon_time": op["phenomenon_time"],
            "behavior_nonce": rng.randint(0, 10**9),
        })
    return behavior


def _event(case_id: str, i: int, op: dict, bh: dict, ingested: str, provider: str) -> dict:
    occurred = bh["occurred"]
    obs = "OBSERVED_OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE"
    ost = "OCCURRENCE" if occurred else "OBSERVABLE_NON_OCCURRENCE"
    return {
        "schema_version": "ppf-l2/1",
        "event_id": opaque("event", f"{case_id}:{i}:raw"),
        "event_type": "activity.sample",
        "source": {"platform": "GENERIC", "device_class": "SERVICE", "provider": provider, "source_event_id": opaque("src", f"{case_id}:{i}:raw")},
        "time": {"phenomenon_time": {"start": bh["phenomenon_time"], "timezone": "UTC", "timing_quality": "KNOWN"}, "result_or_observed_time": bh["phenomenon_time"], "ingested_time": ingested},
        "evidence_kind": "RAW_OBSERVATION",
        "capture_policy": {"mode": "EVENT_DRIVEN", "expected_observability": "EXPECTED"},
        "observability": {"state": obs},
        "opportunity": {"id": op["opportunity_id"], "state": ost, "alternatives": op["alternatives"], "observability": "FULL"},
        "context": {
            "relationship": {"status": "KNOWN" if op["context"]["relationship"] == "known" else "UNKNOWN", "value": op["context"]["relationship"] if op["context"]["relationship"] == "known" else None, "sources": [provider]},
            "period": {"status": "KNOWN", "value": op["context"]["period"], "sources": [provider]},
            "segment": {"status": "KNOWN", "value": op["context"]["segment"], "sources": [provider]},
        },
        "quality": {"quality_state": "GOOD", "coverage_state": "COMPLETE"},
        "provenance": {"procedure_status": "NOT_APPLICABLE"},
        "payload": {"action": bh["choice"] or "not-act"},
    }


def _control_event(case_id: str, suffix: str, target: str, when: str, relation: str, operation: str, scope: str) -> dict:
    return {
        "schema_version": "ppf-l2/1",
        "event_id": opaque("event", f"{case_id}:{suffix}"),
        "event_type": "user.feedback",
        "source": {"platform": "USER", "device_class": "USER", "provider": "user"},
        "time": {"phenomenon_time": {"start": when, "timezone": "UTC", "timing_quality": "KNOWN"}, "result_or_observed_time": when, "ingested_time": when},
        "evidence_kind": "USER_FEEDBACK",
        "observability": {"state": "OBSERVED_OCCURRENCE"},
        "context": {},
        "quality": {"quality_state": "GOOD", "coverage_state": "NOT_APPLICABLE"},
        "provenance": {"procedure_status": "NOT_APPLICABLE"},
        "relations": [{"type": relation, "target_event_id": target}],
        "payload": {"operation": operation, "scope": scope},
    }


def render_history(config: TruthConfig, spec: HistorySpec, opportunities: list[dict], behavior: list[dict], case_id: str) -> tuple[dict, dict]:
    rng = random.Random(derive_seed(MASTER_SEED, config.config_id, "observation", spec.observation_replica))
    provider = "e2-sensor"
    records = []
    provenance = {"observation_policy": "NORMAL", "records": []}
    for i, (op, bh) in enumerate(zip(opportunities, behavior)):
        pt = datetime.fromisoformat(bh["phenomenon_time"].replace("Z", "+00:00"))
        delay = 1 + rng.randint(0, 4)
        if spec.pair_template == "stable_behavior_vs_fake_drift" and spec.pair_arm == "B" and i >= len(behavior) // 2:
            delay = 90 + rng.randint(0, 8)
        if spec.pair_template == "true_drift_vs_observation_only_change" and spec.pair_arm == "B" and i >= len(behavior) // 2:
            delay = 90 + rng.randint(0, 8)
        ingested = (pt + timedelta(minutes=delay)).isoformat().replace("+00:00", "Z")
        ev = _event(case_id, i, op, bh, ingested, provider)
        if spec.pair_template == "full_observability_vs_permission_loss" and spec.pair_arm == "B" and i >= len(behavior) // 2:
            ev["event_type"] = "source.observability"
            ev["evidence_kind"] = "OBSERVABILITY_RECORD"
            ev["observability"] = {"state": "PERMISSION_UNAVAILABLE_OR_UNKNOWN", "missingness_reason": "PERMISSION_LIMITATION"}
            ev["opportunity"]["state"] = "UNKNOWN_OUTCOME"
            ev["opportunity"]["observability"] = "UNKNOWN"
            ev["quality"] = {"quality_state": "UNKNOWN", "coverage_state": "UNKNOWN"}
            ev["payload"] = {"availability": "unavailable"}
            provenance["observation_policy"] = "PERMISSION_LOSS"
        if spec.pair_template == "normal_quality_vs_degraded_quality" and spec.pair_arm == "B":
            ev["quality"] = {"quality_state": "DEGRADED", "coverage_state": "PARTIAL"}
            provenance["observation_policy"] = "DEGRADED_QUALITY"
        if spec.pair_template == "stable_behavior_vs_fake_drift" and spec.pair_arm == "B" and i >= len(behavior) // 2:
            ev["event_type"] = "source.observability"
            ev["evidence_kind"] = "OBSERVABILITY_RECORD"
            ev["observability"] = {"state": "NO_OBSERVATION", "missingness_reason": "SAMPLING_GAP"}
            ev["opportunity"]["state"] = "UNKNOWN_OUTCOME"
            ev["opportunity"]["observability"] = "UNKNOWN"
            ev["quality"] = {"quality_state": "UNKNOWN", "coverage_state": "PARTIAL"}
            ev["payload"] = {"availability": "coverage-gap"}
            provenance["observation_policy"] = "COVERAGE_COLLAPSE"
        if spec.pair_template == "true_drift_vs_observation_only_change" and spec.pair_arm == "B" and i >= len(behavior) // 2:
            ev["event_type"] = "source.observability"
            ev["evidence_kind"] = "OBSERVABILITY_RECORD"
            ev["observability"] = {"state": "DATA_DELAYED", "missingness_reason": "SYNC_DELAY"}
            ev["opportunity"]["state"] = "UNKNOWN_OUTCOME"
            ev["opportunity"]["observability"] = "PARTIAL"
            ev["quality"] = {"quality_state": "DEGRADED", "coverage_state": "PARTIAL"}
            ev["payload"] = {"availability": "delayed"}
            provenance["observation_policy"] = "OBSERVATION_ONLY_CHANGE"
        records.append(ev)
        provenance["records"].append({"event_id": ev["event_id"], "opportunity_id": op["opportunity_id"], "behavior_occurred": bh["occurred"]})
        if spec.pair_template == "independent_corroboration_vs_same_origin_replication" and spec.pair_arm == "A" and i == 0:
            corroboration = copy.deepcopy(ev)
            corroboration["event_id"] = opaque("event", f"{case_id}:{i}:corroboration")
            corroboration["source"]["platform"] = "ANDROID"
            corroboration["source"]["device_class"] = "PHONE"
            corroboration["source"]["provider"] = "e2-independent"
            corroboration["source"]["source_event_id"] = opaque("src", f"{case_id}:{i}:corroboration")
            corroboration["relations"] = [{"type": "INDEPENDENT_CORROBORATION", "target_event_id": ev["event_id"]}]
            records.append(corroboration)
            provenance["records"].append({"event_id": corroboration["event_id"], "independent_corroboration_of": ev["event_id"], "behavior_occurred": bh["occurred"]})
        if spec.pair_template in {"single_evidence_vs_same_origin_replicas", "independent_corroboration_vs_same_origin_replication"} and spec.pair_arm == "B" and i == 0:
            replica = copy.deepcopy(ev)
            replica["event_id"] = opaque("event", f"{case_id}:{i}:replica")
            replica["source"]["platform"] = "ANDROID"
            replica["source"]["device_class"] = "PHONE"
            replica["source"]["provider"] = "e2-mirror"
            replica["source"]["source_event_id"] = opaque("src", f"{case_id}:{i}:replica")
            replica["relations"] = [{"type": "SAME_ORIGIN_REPLICATED", "target_event_id": ev["event_id"]}]
            records.append(replica)
            provenance["records"].append({"event_id": replica["event_id"], "same_origin_of": ev["event_id"], "behavior_occurred": bh["occurred"]})
        if spec.pair_template == "raw_only_vs_raw_plus_derived_lineage" and spec.pair_arm == "B" and i == 0:
            derived = copy.deepcopy(ev)
            derived["event_id"] = opaque("event", f"{case_id}:{i}:derived")
            derived["evidence_kind"] = "DERIVED_OBSERVATION"
            derived["source"]["source_event_id"] = opaque("src", f"{case_id}:{i}:derived")
            derived["provenance"] = {"procedure_status": "KNOWN", "procedure": "e2-derivation-v1", "input_event_refs": [ev["event_id"]]}
            derived["relations"] = [{"type": "DERIVED_FROM", "target_event_id": ev["event_id"]}]
            records.append(derived)
            provenance["records"].append({"event_id": derived["event_id"], "derived_from": ev["event_id"]})
    target = records[1]["event_id"]
    controls: list[dict] = []
    if spec.pair_template == "correction_absent_vs_correction_applied" and spec.pair_arm == "B":
        controls.append(_control_event(case_id, "correction", target, "2026-03-01T10:30:00Z", "CORRECTS", "reject", config.scope))
    if spec.pair_template == "deletion_absent_vs_deletion_applied" and spec.pair_arm == "B":
        controls.append(_control_event(case_id, "deletion", target, "2026-03-01T10:30:00Z", "DELETES", "remove", config.scope))
    if spec.lifecycle_variant == "correction_high_risk":
        controls.append(_control_event(case_id, "correction", target, "2026-03-01T10:30:00Z", "CORRECTS", "reject", config.scope))
    if spec.lifecycle_variant == "reset":
        controls.append(_control_event(case_id, "reset", target, "2026-03-01T10:30:00Z", "DELETES", "reset", config.scope))
    if spec.lifecycle_variant == "supersession_invalidation":
        controls.append(_control_event(case_id, "supersede", target, "2026-03-01T10:30:00Z", "SUPERSEDES", "supersede", config.scope))
        controls.append(_control_event(case_id, "invalidate", target, "2026-03-01T13:00:00Z", "INVALIDATES", "invalidate", config.scope))
    records.extend(controls)
    if controls:
        provenance["controls"] = [{"operation": c["payload"]["operation"], "effective_time": c["time"]["ingested_time"], "target_event_id": target, "event_id": c["event_id"]} for c in controls]
    fixture = {
        "fixture_id": "L2-F001",
        "title": "E2 DEV visible history",
        "family": "E2_DEV",
        "purpose": "Validate L2 semantics for one PPF-L3 DEV case",
        "source_platform_class": "GENERIC",
        "records": records,
        "expected": {
            "semantic_interpretation": "Visible evidence only; evaluator truth is stored separately",
            "observability": "Explicit",
            "opportunity": "Explicit",
            "time": "Three-time explicit",
            "provenance": "Retained",
            "multi_device": "Lineage retained",
            "raw_derived": "Explicit where present",
            "lineage": "Explicit",
            "must_not_infer": "Truth is evaluator-only",
        },
        "adversarial": config.risk_class == "HIGH-RISK" or spec.pair_template is not None,
        "gates": ["L2-G1"],
    }
    return fixture, provenance


CHECKPOINT_OFFSETS = {
    "SHORT": (20, 90, 180, 300),
    "MEDIUM": (20, 120, 240, 480, 720),
    "LONG": (20, 120, 160, 360, 900, 1500, 2100),
}


def case_id_for_spec(spec: HistorySpec) -> str:
    return opaque("case", f"{spec.config_id}:{spec.history_index}:{spec.behavior_replica}:{spec.observation_replica}")


def _checkpoint_times(config: TruthConfig) -> list[str]:
    base = datetime(2026, 3, 1, 8, tzinfo=timezone.utc)
    return [iso(base, minutes) for minutes in CHECKPOINT_OFFSETS[config.history_regime]]


def _supported_after_early(count: int, value: str="SUPPORTED") -> list[str]:
    return ["INSUFFICIENT_EVIDENCE" if i < 2 else value for i in range(count)]


def _answer_plan(config: TruthConfig, spec: HistorySpec) -> list[str]:
    n = len(CHECKPOINT_OFFSETS[config.history_regime])
    answers = _supported_after_early(n, config.base_answer)
    t = spec.pair_template
    arm = spec.pair_arm
    if t == "full_observability_vs_permission_loss":
        answers = _supported_after_early(n)
        if arm == "B": answers[-2:] = ["NOT_OBSERVABLE", "NOT_OBSERVABLE"]
    elif t == "normal_quality_vs_degraded_quality":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE"] * n
    elif t == "single_evidence_vs_same_origin_replicas":
        answers = ["INSUFFICIENT_EVIDENCE"] * n
    elif t == "true_routine_vs_chance_matching_no_pattern":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE"] * n
    elif t == "stable_behavior_vs_fake_drift":
        answers = _supported_after_early(n)
        if arm == "B": answers[-2:] = ["NOT_OBSERVABLE", "STALE"]
    elif t == "true_drift_vs_observation_only_change":
        answers = _supported_after_early(n)
        if arm == "B": answers[-2:] = ["NOT_OBSERVABLE", "STALE"]
    elif t == "meaningful_alternatives_vs_constrained_availability":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE"] * n
    elif t == "conditional_truth_vs_misleading_aggregate":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE" if i < 2 else "CONFLICTING_EVIDENCE" for i in range(n)]
    elif t == "stable_exception_vs_random_deviation":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE"] * n
    elif t == "correction_absent_vs_correction_applied":
        answers = _supported_after_early(n)
        if arm == "B": answers[2:] = ["USER_REJECTED"] * (n - 2)
    elif t == "deletion_absent_vs_deletion_applied":
        answers = _supported_after_early(n)
        if arm == "B": answers[2:] = ["DELETED"] * (n - 2)
    elif t == "known_relationship_vs_unknown_relationship":
        answers = _supported_after_early(n) if arm == "A" else ["INSUFFICIENT_EVIDENCE"] + ["UNKNOWN_CONTEXT"] * (n - 1)
    elif t in {"raw_only_vs_raw_plus_derived_lineage", "independent_corroboration_vs_same_origin_replication"}:
        answers = ["INSUFFICIENT_EVIDENCE"] * n

    if spec.lifecycle_variant == "staleness":
        answers = _supported_after_early(n); answers[-1] = "STALE"
    elif spec.lifecycle_variant == "reversal":
        answers = _supported_after_early(n)
    elif spec.lifecycle_variant == "correction_high_risk":
        answers = _supported_after_early(n); answers[2:] = ["USER_REJECTED"] * (n - 2)
    elif spec.lifecycle_variant == "reset":
        answers = _supported_after_early(n); answers[2:] = ["DELETED"] * (n - 2)
    elif spec.lifecycle_variant == "supersession_invalidation":
        answers = _supported_after_early(n); answers[2:] = ["SUPERSEDED"] * (n - 2)
    return answers


def _identifiability_plan(config: TruthConfig, spec: HistorySpec) -> list[str]:
    n = len(CHECKPOINT_OFFSETS[config.history_regime])
    values = [config.identifiability] * n
    t = spec.pair_template
    arm = spec.pair_arm
    if t in {"full_observability_vs_permission_loss", "normal_quality_vs_degraded_quality", "stable_behavior_vs_fake_drift", "true_drift_vs_observation_only_change"}:
        values = ["YES"] * n
        if arm == "B": values[-2:] = ["PARTIAL", "NO"]
    elif t == "meaningful_alternatives_vs_constrained_availability":
        values = ["YES"] * n if arm == "A" else ["PARTIAL"] * n
    elif t == "conditional_truth_vs_misleading_aggregate":
        values = ["YES"] * n if arm == "A" else ["PARTIAL"] * n
    elif t == "known_relationship_vs_unknown_relationship":
        values = ["YES"] * n if arm == "A" else ["NO"] * n
    elif t in {"single_evidence_vs_same_origin_replicas", "raw_only_vs_raw_plus_derived_lineage", "independent_corroboration_vs_same_origin_replication"}:
        values = ["PARTIAL"] * n
    elif t in {"true_routine_vs_chance_matching_no_pattern", "stable_exception_vs_random_deviation", "correction_absent_vs_correction_applied", "deletion_absent_vs_deletion_applied"}:
        values = ["YES"] * n
    if spec.lifecycle_variant in {"reversal", "correction_high_risk", "reset", "supersession_invalidation"}:
        values = ["YES"] * n
    if spec.lifecycle_variant == "staleness":
        values = ["YES"] * n; values[-1] = "PARTIAL"
    return values


def checkpoint_oracle(config: TruthConfig, spec: HistorySpec, records: list[dict]) -> list[dict]:
    times = _checkpoint_times(config)
    answers = _answer_plan(config, spec)
    identifiability = _identifiability_plan(config, spec)
    cps = []
    for i, (when, answer, ident) in enumerate(zip(times, answers, identifiability)):
        cutoff = datetime.fromisoformat(when.replace("Z", "+00:00"))
        visible = [e["event_id"] for e in records if datetime.fromisoformat(e["time"]["ingested_time"].replace("Z", "+00:00")) <= cutoff]
        cps.append({
            "checkpoint_id": opaque("cp", f"{spec.config_id}:{spec.history_index}:{i}"),
            "evaluation_unit_id": opaque("unit", f"{spec.config_id}:{spec.history_index}:{i}"),
            "time": when,
            "visible_event_ids": visible,
            "expected_answer": answer,
            "identifiability": ident,
        })
    return cps


def generate_case(spec: HistorySpec) -> dict:
    config = _config_map()[spec.config_id]
    case_id = case_id_for_spec(spec)
    truth = truth_spec(config, spec)
    opportunities = opportunity_sequence(config, spec, truth)
    behavior = behavior_realization(config, spec, opportunities)
    fixture, observation_provenance = render_history(config, spec, opportunities, behavior, case_id)
    checkpoints = checkpoint_oracle(config, spec, fixture["records"])
    return {
        "case_id": case_id,
        "person_id": truth["person_id"],
        "config": config,
        "spec": spec,
        "truth": truth,
        "opportunities": opportunities,
        "behavior": behavior,
        "fixture": fixture,
        "checkpoints": checkpoints,
        "seeds": {
            "master_seed": MASTER_SEED,
            "scenario_seed": derive_seed(MASTER_SEED, spec.config_id, "scenario"),
            "person_seed": derive_seed(MASTER_SEED, config.person_key, "person"),
            "behavior_seed": derive_seed(MASTER_SEED, spec.config_id, "behavior", spec.behavior_replica),
            "observation_seed": derive_seed(MASTER_SEED, spec.config_id, "observation", spec.observation_replica),
        },
        "observation_provenance": observation_provenance,
    }


def method_visible_case(case: dict) -> dict:
    return {
        "benchmark_version": VERSION,
        "case_id": case["case_id"],
        "history": case["fixture"]["records"],
    }


def checkpoint_requests(case: dict) -> dict:
    return {
        "benchmark_version": VERSION,
        "case_id": case["case_id"],
        "checkpoints": [{"checkpoint_id": c["checkpoint_id"], "time": c["time"]} for c in case["checkpoints"]],
    }


def expected_answers(case: dict) -> dict:
    return {
        "benchmark_version": VERSION,
        "case_id": case["case_id"],
        "answers": [{"checkpoint_id": c["checkpoint_id"], "evaluation_unit_id": c["evaluation_unit_id"], "expected_answer": c["expected_answer"], "visible_event_ids": c["visible_event_ids"], "identifiability": c["identifiability"]} for c in case["checkpoints"]],
    }


def evaluator_truth(case: dict) -> dict:
    return {
        "benchmark_version": VERSION,
        "case_id": case["case_id"],
        "person_id": case["person_id"],
        "truth": case["truth"],
        "opportunities": case["opportunities"],
        "behavior": case["behavior"],
        "observation_provenance": case["observation_provenance"],
        "seeds": case["seeds"],
        "pair_template": case["spec"].pair_template,
        "pair_arm": case["spec"].pair_arm,
        "families": list(case["config"].families),
        "identifiability_by_checkpoint": {c["checkpoint_id"]: c["identifiability"] for c in case["checkpoints"]},
    }


def _seed_record(config: TruthConfig, spec: HistorySpec) -> dict:
    return {
        "master_seed": MASTER_SEED,
        "scenario_seed": derive_seed(MASTER_SEED, spec.config_id, "scenario"),
        "person_seed": derive_seed(MASTER_SEED, config.person_key, "person"),
        "behavior_seed": derive_seed(MASTER_SEED, spec.config_id, "behavior", spec.behavior_replica),
        "observation_seed": derive_seed(MASTER_SEED, spec.config_id, "observation", spec.observation_replica),
    }


def _preregistration(specs: list[HistorySpec]) -> dict:
    configs = _config_map()
    histories=[]; units=[]
    for spec in specs:
        config=configs[spec.config_id]
        case_id=case_id_for_spec(spec)
        times=_checkpoint_times(config); answers=_answer_plan(config,spec); ident=_identifiability_plan(config,spec)
        checkpoint_ids=[opaque("cp",f"{spec.config_id}:{spec.history_index}:{i}") for i in range(len(times))]
        unit_ids=[opaque("unit",f"{spec.config_id}:{spec.history_index}:{i}") for i in range(len(times))]
        histories.append({
            "case_id":case_id,
            "person_id":opaque("person",config.person_key),
            "truth_config_id":spec.config_id,
            "risk_class":config.risk_class,
            "history_regime":config.history_regime,
            "families":list(config.families),
            "behavior_replica":spec.behavior_replica,
            "observation_replica":spec.observation_replica,
            "seeds":_seed_record(config,spec),
            "pair_id":PAIR_IDS.get(spec.pair_template) if spec.pair_template else None,
            "pair_template":spec.pair_template,
            "pair_arm":spec.pair_arm,
            "lifecycle_variant":spec.lifecycle_variant,
            "checkpoint_ids":checkpoint_ids,
            "evaluation_unit_ids":unit_ids,
        })
        for i,(when,answer,ident_value) in enumerate(zip(times,answers,ident)):
            units.append({
                "evaluation_unit_id":unit_ids[i],
                "case_id":case_id,
                "checkpoint_id":checkpoint_ids[i],
                "time":when,
                "semantic_question":"active personal-pattern claim at checkpoint",
                "expected_answer":answer,
                "identifiability":ident_value,
                "families":list(config.families),
                "negative_denominator":answer != "SUPPORTED",
            })
    return {
        "benchmark_version": VERSION,
        "generator_version": GENERATOR_VERSION,
        "starting_commit": STARTING_COMMIT,
        "split": "dev",
        "master_seed": MASTER_SEED,
        "registered_before_generation": True,
        "reroll_count": 0,
        "persons": sorted({opaque("person",c.person_key) for c in truth_configs()}),
        "truth_configurations": [{"truth_config_id":c.config_id,"person_id":opaque("person",c.person_key),"risk_class":c.risk_class,"history_regime":c.history_regime,"families":list(c.families)} for c in truth_configs()],
        "risk_allocation": {"STANDARD":sum(1 for c in truth_configs() if c.risk_class=="STANDARD"),"HIGH-RISK":sum(1 for c in truth_configs() if c.risk_class=="HIGH-RISK")},
        "histories": histories,
        "evaluation_units": units,
        "negative_denominator_unit_ids": [u["evaluation_unit_id"] for u in units if u["negative_denominator"]],
    }


def _public_case_schema() -> dict:
    return {
        "benchmark_version": VERSION,
        "required_files": ["history.json", "checkpoints.json"],
        "history_contract": {
            "allowed_top_level": ["benchmark_version", "case_id", "history"],
            "history_records": "ppf-l2/1",
        },
        "checkpoint_contract": {
            "allowed_top_level": ["benchmark_version", "case_id", "checkpoints"],
            "checkpoint_fields": ["checkpoint_id", "time"],
        },
    }


def _validation_policy() -> dict:
    return {
        "benchmark_version": VERSION,
        "status": "NOT_GENERATED_NOT_AUTHORIZED",
        "person_disjoint": True,
        "truth_configuration_disjoint": True,
        "dev_history_count": 38,
        "validation_history_count_planned": 38,
        "final_history_count_planned": 112,
        "final_truth_public": False,
    }


def _pair_public_contract() -> dict:
    return {
        "benchmark_version": VERSION,
        "templates": [
            {
                "pair_id": PAIR_IDS[template],
                "template": template,
                "controlled_variable": PAIR_LABELS[template],
                "held_constant": list(PAIR_HELD_CONSTANT[template]),
                "expected_effect": PAIR_EXPECTED_EFFECT[template],
            }
            for template in PAIR_TEMPLATES
        ],
        "instance_membership_visibility": "EVALUATOR_ONLY",
    }


def _pair_manifest(cases: list[dict]) -> dict:
    by_template: dict[str, list[dict]] = {}
    for c in cases:
        if c["spec"].pair_template:
            by_template.setdefault(c["spec"].pair_template, []).append(c)
    pairs = []
    for i, template in enumerate(PAIR_TEMPLATES, start=1):
        arms = sorted(by_template.get(template, []), key=lambda c: c["spec"].pair_arm or "")
        pairs.append({
            "pair_id": PAIR_IDS[template],
            "template": template,
            "controlled_variable": template,
            "case_a": arms[0]["case_id"],
            "case_b": arms[1]["case_id"],
            "held_constant_summary": ["benchmark_version", "split", "registered_configuration_family", "case_schema"],
            "arm_hashes": {a["spec"].pair_arm: semantic_hash(evaluator_truth(a)) for a in arms},
        })
    return {"benchmark_version": VERSION, "pair_count": len(pairs), "pairs": pairs}


def _normalize_record_for_diff(record: dict) -> dict:
    item = copy.deepcopy(record)
    pt = datetime.fromisoformat(record["time"]["phenomenon_time"]["start"].replace("Z", "+00:00"))
    it = datetime.fromisoformat(record["time"]["ingested_time"].replace("Z", "+00:00"))
    item["ingestion_delay_class"] = "late" if (it - pt).total_seconds() > 3600 else "normal"
    item.pop("event_id", None)
    item.pop("time", None)
    item["source"].pop("source_event_id", None)
    item.get("opportunity", {}).pop("id", None)
    for rel in item.get("relations", []):
        rel.pop("target_event_id", None)
    if item.get("provenance", {}).get("input_event_refs"):
        item["provenance"]["input_event_refs"] = ["<ref>"] * len(item["provenance"]["input_event_refs"])
    return item


def _normalize_case_for_diff(case: dict) -> dict:
    return {
        "truth_kind": case["truth"]["truth_kind"],
        "scope": case["truth"]["scope"],
        "opportunities": [{"alternatives": o["alternatives"], "context": o["context"]} for o in case["opportunities"]],
        "behavior": [{"occurred": b["occurred"], "choice": b["choice"]} for b in case["behavior"]],
        "records": [_normalize_record_for_diff(r) for r in case["fixture"]["records"]],
        "expected_answers": [c["expected_answer"] for c in case["checkpoints"]],
    }


def _diff_paths(a: Any, b: Any, path: str = "") -> list[str]:
    if type(a) is not type(b):
        return [path or "$"]
    if isinstance(a, dict):
        paths: list[str] = []
        for key in sorted(set(a) | set(b)):
            child = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                paths.append(child)
            else:
                paths.extend(_diff_paths(a[key], b[key], child))
        return paths
    if isinstance(a, list):
        paths = []
        for i in range(max(len(a), len(b))):
            child = f"{path}[{i}]"
            if i >= len(a) or i >= len(b):
                paths.append(child)
            else:
                paths.extend(_diff_paths(a[i], b[i], child))
        return paths
    return [] if a == b else [path or "$"]


def _allowed_pair_path(template: str, path: str) -> bool:
    allowed = {
        "full_observability_vs_permission_loss": ("records", "expected_answers"),
        "normal_quality_vs_degraded_quality": ("records", "expected_answers"),
        "single_evidence_vs_same_origin_replicas": ("records",),
        "true_routine_vs_chance_matching_no_pattern": ("truth_kind", "behavior", "records", "expected_answers"),
        "stable_behavior_vs_fake_drift": ("records", "expected_answers"),
        "true_drift_vs_observation_only_change": ("truth_kind", "behavior", "records", "expected_answers"),
        "meaningful_alternatives_vs_constrained_availability": ("truth_kind", "opportunities", "behavior", "records", "expected_answers"),
        "conditional_truth_vs_misleading_aggregate": ("truth_kind", "behavior", "records", "expected_answers"),
        "stable_exception_vs_random_deviation": ("truth_kind", "behavior", "records", "expected_answers"),
        "correction_absent_vs_correction_applied": ("records", "expected_answers"),
        "deletion_absent_vs_deletion_applied": ("records", "expected_answers"),
        "known_relationship_vs_unknown_relationship": ("opportunities", "records", "expected_answers"),
        "raw_only_vs_raw_plus_derived_lineage": ("records",),
        "independent_corroboration_vs_same_origin_replication": ("records",),
    }[template]
    return any(path == root or path.startswith(root + ".") or path.startswith(root + "[") for root in allowed)


def _strong_pair_reports(cases: list[dict]) -> dict[str, dict]:
    by_template: dict[str, list[dict]] = {}
    for c in cases:
        if c["spec"].pair_template:
            by_template.setdefault(c["spec"].pair_template, []).append(c)
    reports = {}
    for template, arms in by_template.items():
        arms = sorted(arms, key=lambda c: c["spec"].pair_arm or "")
        diffs = _diff_paths(_normalize_case_for_diff(arms[0]), _normalize_case_for_diff(arms[1]))
        unexpected = [p for p in diffs if not _allowed_pair_path(template, p)]
        reports[template] = {
            "changed_paths": diffs,
            "unexpected_paths": unexpected,
            "pass": bool(diffs) and not unexpected,
        }
    return reports


def _public_manifest(cases: list[dict], root: Path) -> dict:
    return {
        "benchmark_version": VERSION,
        "split": "dev",
        "cases": [
            {
                "case_id": c["case_id"],
                "history_path": str((root / "generated" / "dev" / "cases" / c["case_id"] / "history.json").relative_to(root)).replace("\\", "/"),
                "checkpoints_path": str((root / "generated" / "dev" / "cases" / c["case_id"] / "checkpoints.json").relative_to(root)).replace("\\", "/"),
                "history_hash": semantic_hash(method_visible_case(c)),
                "checkpoint_hash": semantic_hash(checkpoint_requests(c)),
            }
            for c in cases
        ],
    }


def _qa(cases: list[dict], preregistration: dict, prereg_evidence: dict, root: Path) -> dict:
    l2_errors = {c["case_id"]: validate_fixture(c["fixture"]) for c in cases}
    visible_blobs = [method_visible_case(c) | {"checkpoints": checkpoint_requests(c)["checkpoints"]} for c in cases]
    leak_violations = {
        c["case_id"]: sorted(term for term in LEAK_TERMS if term in json.dumps(method_visible_case(c) | checkpoint_requests(c), sort_keys=True).lower())
        for c in cases
    }
    pair_manifest = _pair_manifest(cases)
    pair_reports = _strong_pair_reports(cases)
    paired_cases = [c for c in cases if c["spec"].pair_template]
    one_pair_per_history = len({c["case_id"] for c in paired_cases}) == len(paired_cases)
    templates = {p["template"] for p in pair_manifest["pairs"]}
    seed_tuples = {(c["spec"].config_id, c["spec"].behavior_replica, c["spec"].observation_replica) for c in cases}
    expected_seed_tuples = {(s.config_id, b, o) for s in truth_configs() for b, o in _replicas_for(s)}
    checkpoint_future_leaks: list[dict] = []
    for c in cases:
        records = c["fixture"]["records"]
        for cp in c["checkpoints"]:
            cutoff = datetime.fromisoformat(cp["time"].replace("Z", "+00:00"))
            expected_visible = [
                e["event_id"]
                for e in records
                if datetime.fromisoformat(e["time"]["ingested_time"].replace("Z", "+00:00")) <= cutoff
            ]
            if cp["visible_event_ids"] != expected_visible:
                checkpoint_future_leaks.append({
                    "case_id": c["case_id"],
                    "checkpoint_id": cp["checkpoint_id"],
                    "expected_visible": expected_visible,
                    "actual_visible": cp["visible_event_ids"],
                })
    sample_config = truth_configs()[0]
    same_seed_a = generate_case(HistorySpec(sample_config.config_id, 100, 0, 0))
    same_seed_b = generate_case(HistorySpec(sample_config.config_id, 100, 0, 0))
    obs_a = generate_case(HistorySpec(sample_config.config_id, 101, 0, 0))
    obs_b = generate_case(HistorySpec(sample_config.config_id, 101, 0, 1))
    beh_a = generate_case(HistorySpec(sample_config.config_id, 102, 0, 0))
    beh_b = generate_case(HistorySpec(sample_config.config_id, 102, 1, 0))
    seed_isolation = {
        "same_tuple_stable": semantic_hash(evaluator_truth(same_seed_a)) == semantic_hash(evaluator_truth(same_seed_b)),
        "observation_seed_keeps_truth_opportunity_behavior": obs_a["truth"] == obs_b["truth"] and obs_a["opportunities"] == obs_b["opportunities"] and obs_a["behavior"] == obs_b["behavior"] and semantic_hash(method_visible_case(obs_a)) != semantic_hash(method_visible_case(obs_b)),
        "behavior_seed_keeps_truth_opportunity": beh_a["truth"] == beh_b["truth"] and beh_a["opportunities"] == beh_b["opportunities"] and semantic_hash(beh_a["behavior"]) != semantic_hash(beh_b["behavior"]),
    }
    families = {family for c in truth_configs() for family in c.families}

    def pair_arms(template: str) -> tuple[dict, dict]:
        arms = sorted(
            (c for c in cases if c["spec"].pair_template == template),
            key=lambda c: c["spec"].pair_arm or "",
        )
        return arms[0], arms[1]

    def control_events(case: dict) -> list[dict]:
        return [e for e in case["fixture"]["records"] if e["evidence_kind"] == "USER_FEEDBACK"]

    def relation_types(case: dict) -> set[str]:
        return {rel["type"] for e in control_events(case) for rel in e.get("relations", [])}

    def operations(case: dict) -> set[str]:
        return {e.get("payload", {}).get("operation") for e in control_events(case)}

    def behavior_semantics(case: dict) -> list[dict]:
        return [{"occurred": b["occurred"], "choice": b["choice"]} for b in case["behavior"]]

    def no_supported_after_control(case: dict) -> bool:
        controls = control_events(case)
        if not controls:
            return False
        first_control = min(datetime.fromisoformat(e["time"]["ingested_time"].replace("Z", "+00:00")) for e in controls)
        later = [cp for cp in case["checkpoints"] if datetime.fromisoformat(cp["time"].replace("Z", "+00:00")) >= first_control]
        return bool(later) and all(cp["expected_answer"] != "SUPPORTED" for cp in later)

    correction_case = pair_arms("correction_absent_vs_correction_applied")[1]
    deletion_case = pair_arms("deletion_absent_vs_deletion_applied")[1]
    drift_case = pair_arms("true_drift_vs_observation_only_change")[0]
    fake_drift_a, fake_drift_b = pair_arms("stable_behavior_vs_fake_drift")
    reversal_case = next(c for c in cases if c["spec"].lifecycle_variant == "reversal")
    reset_case = next(c for c in cases if c["spec"].lifecycle_variant == "reset")
    supersession_case = next(c for c in cases if c["spec"].lifecycle_variant == "supersession_invalidation")
    stale_case = next(c for c in cases if c["spec"].lifecycle_variant == "staleness")

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
        "fake_drift_has_no_latent_transition": fake_drift_a["truth"]["truth_kind"] == "STABLE_PATTERN" and fake_drift_b["truth"]["truth_kind"] == "STABLE_PATTERN" and behavior_semantics(fake_drift_a) == behavior_semantics(fake_drift_b) and fake_drift_b["observation_provenance"]["observation_policy"] == "COVERAGE_COLLAPSE",
        "no_passive_resurrection": all(no_supported_after_control(c) for c in (correction_case, deletion_case, reset_case, supersession_case)),
    }

    cf14_a, cf14_b = pair_arms("independent_corroboration_vs_same_origin_replication")
    cf03_a, cf03_b = pair_arms("single_evidence_vs_same_origin_replicas")
    cf13_a, cf13_b = pair_arms("raw_only_vs_raw_plus_derived_lineage")
    cf12_b = pair_arms("known_relationship_vs_unknown_relationship")[1]

    def has_relation(case: dict, relation_type: str) -> bool:
        return any(
            rel["type"] == relation_type
            for e in case["fixture"]["records"]
            for rel in e.get("relations", [])
        )

    evidence_checks = {
        "same_origin_replica_not_new_behavior": has_relation(cf03_b, "SAME_ORIGIN_REPLICATED") and behavior_semantics(cf03_a) == behavior_semantics(cf03_b),
        "raw_derived_not_new_behavior": any(e["evidence_kind"] == "DERIVED_OBSERVATION" for e in cf13_b["fixture"]["records"]) and behavior_semantics(cf13_a) == behavior_semantics(cf13_b),
        "independent_and_same_origin_distinguished": len(cf14_a["fixture"]["records"]) == len(cf14_b["fixture"]["records"]) and behavior_semantics(cf14_a) == behavior_semantics(cf14_b) and has_relation(cf14_a, "INDEPENDENT_CORROBORATION") and not has_relation(cf14_a, "SAME_ORIGIN_REPLICATED") and has_relation(cf14_b, "SAME_ORIGIN_REPLICATED") and not has_relation(cf14_b, "INDEPENDENT_CORROBORATION"),
        "unknown_relationship_remains_unknown": any(e.get("context", {}).get("relationship", {}).get("status") == "UNKNOWN" for e in cf12_b["fixture"]["records"]),
    }

    family_evidence = {
        "routine": any(c["truth"]["truth_kind"] in {"STABLE_PATTERN", "STABLE_ROUTINE"} and "routine/opportunity" in c["config"].families for c in cases),
        "preference": any(c["truth"]["truth_kind"] == "PREFERENCE" and any(len(o["alternatives"]) > 1 for o in c["opportunities"]) for c in cases),
        "relationship_conditioned": any(c["truth"]["truth_kind"] == "RELATIONSHIP_CONDITIONED" for c in cases),
        "temporal_sequence": any("temporal sequence" in c["config"].families and len(c["opportunities"]) >= 16 for c in cases),
        "exception": any(c["truth"]["truth_kind"] == "SCOPED_EXCEPTION" for c in cases),
        "drift_reversal": lifecycle_checks["true_drift_has_latent_transition"] and lifecycle_checks["reversal_has_latent_transition"],
        "no_pattern": any(c["truth"]["truth_kind"] == "NO_PATTERN" for c in cases),
        "insufficient_or_conflicting": any(cp["expected_answer"] in {"INSUFFICIENT_EVIDENCE", "CONFLICTING_EVIDENCE"} for c in cases for cp in c["checkpoints"]),
        "observability_loss": any(e["evidence_kind"] == "OBSERVABILITY_RECORD" for c in cases for e in c["fixture"]["records"]),
        "same_origin_replication": evidence_checks["same_origin_replica_not_new_behavior"],
        "correction": lifecycle_checks["correction_control_present"],
        "deletion_reset": lifecycle_checks["deletion_present"] and lifecycle_checks["reset_present"],
        "relationship_visibility": evidence_checks["unknown_relationship_remains_unknown"],
        "confounding_simpson": any(c["spec"].pair_template == "conditional_truth_vs_misleading_aggregate" and {o["context"]["segment"] for o in c["opportunities"]} == {"context-a", "context-b"} for c in cases),
        "fake_drift": lifecycle_checks["fake_drift_has_no_latent_transition"],
    }

    registered_case_ids = {h["case_id"] for h in preregistration["histories"]}
    generated_case_ids = {c["case_id"] for c in cases}
    registered_units = {u["evaluation_unit_id"]: u for u in preregistration["evaluation_units"]}
    actual_units = {
        cp["evaluation_unit_id"]: cp
        for c in cases
        for cp in c["checkpoints"]
    }
    registered_negative = set(preregistration["negative_denominator_unit_ids"])
    actual_negative = {unit_id for unit_id, cp in actual_units.items() if cp["expected_answer"] != "SUPPORTED"}
    registration_matches_generation = registered_case_ids == generated_case_ids and set(registered_units) == set(actual_units)
    registration_checkpoint_semantics_match = all(
        registered_units[unit_id]["expected_answer"] == cp["expected_answer"]
        and registered_units[unit_id]["identifiability"] == cp["identifiability"]
        and registered_units[unit_id]["checkpoint_id"] == cp["checkpoint_id"]
        for unit_id, cp in actual_units.items()
    )

    oracle_source = inspect.getsource(_answer_plan) + inspect.getsource(checkpoint_oracle)
    oracle_generic_threshold_found = bool(re.search(r"occurrences\s*>?=|confidence\s*[><=]|pattern_score|classifier|frequency\s*[><=]|ratio\s*[><=]|probability\s*[><=]", oracle_source, re.I))

    from tools.research import ppf_l2_validate
    from tools.research.ppf_l3 import e0, e1

    l2_regression = ppf_l2_validate.main() == 0
    e0_regression = e0.run_e0()
    e1_regression = e1.run_e1()
    regression_checks = {
        "l2_60_and_8": l2_regression,
        "e0": e0_regression.get("status") == "PASS",
        "e1": e1_regression.get("status") == "PASS" and all(e1_regression.get("gates", {}).values()),
    }

    changed = set()
    tracked = subprocess.run(["git", "diff", "--name-only", STARTING_COMMIT, "--"], cwd=ROOT, check=True, capture_output=True, text=True)
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, check=True, capture_output=True, text=True)
    changed.update(p.strip().replace("\\", "/") for p in tracked.stdout.splitlines() if p.strip())
    changed.update(p.strip().replace("\\", "/") for p in untracked.stdout.splitlines() if p.strip())
    allowed_prefixes = ("docs/research/", "tools/research/ppf_l3/", "tests/research/ppf_l3/", "benchmarks/ppf_l3/")
    scope_violations = sorted(p for p in changed if not p.startswith(allowed_prefixes))
    forbidden_split_paths = [
        root / "generated" / "validation",
        root / "generated" / "final",
        root / "evaluator" / "validation",
        root / "evaluator" / "final",
    ]
    secret_final_candidates = [p for p in root.rglob("*") if p.is_file() and "final" in p.name.lower() and "validation_policy" not in p.name.lower()]

    qa_checks = {
        "preregistered_before_generation": bool(prereg_evidence.get("written_before_generation")) and prereg_evidence.get("registration_hash") == semantic_hash(preregistration),
        "registration_matches_generation": registration_matches_generation and registration_checkpoint_semantics_match,
        "reroll_count_zero": preregistration.get("reroll_count") == 0 and prereg_evidence.get("generated_history_count") == 38,
        "person_count": len({c["person_id"] for c in cases}) == 6,
        "truth_config_count": len({c["spec"].config_id for c in cases}) == 7,
        "standard_history_count": sum(1 for c in cases if c["config"].risk_class == "STANDARD") == 20,
        "high_risk_history_count": sum(1 for c in cases if c["config"].risk_class == "HIGH-RISK") == 18,
        "history_count": len(cases) == 38,
        "seed_matrix_exact": seed_tuples == expected_seed_tuples,
        "counterfactual_pair_templates": templates == set(PAIR_TEMPLATES),
        "counterfactual_pair_count": pair_manifest["pair_count"] == 14,
        "counterfactual_strong_isolation": all(r["pass"] for r in pair_reports.values()),
        "one_pair_per_history": one_pair_per_history,
        "l2_validity": not any(l2_errors.values()),
        "truth_leakage": not any(leak_violations.values()),
        "checkpoint_future_leakage": not checkpoint_future_leaks,
        "seed_isolation": all(seed_isolation.values()),
        "semantic_family_coverage": all(family_evidence.values()),
        "oracle_boundary": not oracle_generic_threshold_found,
        "identifiability_labels": {cp["identifiability"] for c in cases for cp in c["checkpoints"]} == {"YES", "PARTIAL", "NO"} and all(cp["expected_answer"] != "SUPPORTED" for c in cases for cp in c["checkpoints"] if cp["identifiability"] == "NO"),
        "negative_denominator_preregistered": registered_negative == actual_negative and bool(registered_negative) and prereg_evidence.get("written_before_generation") is True,
        "lifecycle_correctness": all(lifecycle_checks.values()),
        "evidence_non_inflation": all(evidence_checks.values()),
        "dev_only_generation": preregistration.get("split") == "dev" and not any(path.exists() for path in forbidden_split_paths) and not secret_final_candidates,
        "regression": all(regression_checks.values()),
        "scope_integrity": not scope_violations,
    }
    e2_gates = {
        "E2-G1": qa_checks["person_count"] and qa_checks["truth_config_count"] and qa_checks["history_count"],
        "E2-G2": qa_checks["standard_history_count"] and qa_checks["high_risk_history_count"] and qa_checks["seed_matrix_exact"],
        "E2-G3": qa_checks["l2_validity"],
        "E2-G4": qa_checks["semantic_family_coverage"],
        "E2-G5": qa_checks["counterfactual_pair_templates"] and qa_checks["counterfactual_pair_count"],
        "E2-G6": qa_checks["counterfactual_strong_isolation"],
        "E2-G7": qa_checks["seed_isolation"],
        "E2-G8": qa_checks["checkpoint_future_leakage"],
        "E2-G9": qa_checks["oracle_boundary"],
        "E2-G10": qa_checks["identifiability_labels"],
        "E2-G11": qa_checks["negative_denominator_preregistered"],
        "E2-G12": qa_checks["lifecycle_correctness"],
        "E2-G13": qa_checks["evidence_non_inflation"],
        "E2-G14": qa_checks["preregistered_before_generation"] and qa_checks["registration_matches_generation"] and qa_checks["reroll_count_zero"] and qa_checks["history_count"],
        "E2-G15": qa_checks["truth_leakage"],
        "E2-G16": qa_checks["dev_only_generation"],
        "E2-G17": qa_checks["regression"],
        "E2-G18": qa_checks["scope_integrity"],
    }
    return {
        "benchmark_version": VERSION,
        "status": "PASS" if all(qa_checks.values()) and all(e2_gates.values()) else "REVISE",
        "e2_gates": e2_gates,
        "qa_checks": qa_checks,
        "semantic_families": sorted(families),
        "family_evidence": family_evidence,
        "lifecycle_checks": lifecycle_checks,
        "seed_isolation": seed_isolation,
        "regression_checks": regression_checks,
        "oracle_generic_threshold_found": oracle_generic_threshold_found,
        "scope_violations": scope_violations,
        "pair_reports": pair_reports,
        "evidence_non_inflation": evidence_checks,
        "l2_errors": l2_errors,
        "truth_leak_violations": leak_violations,
        "checkpoint_future_leak_violations": checkpoint_future_leaks,
        "registered_negative_denominator": len(registered_negative),
        "method_visible_hash": semantic_hash(visible_blobs),
    }


def _summary(cases: list[dict], qa: dict) -> dict:
    checkpoints = sum(len(c["checkpoints"]) for c in cases)
    units = checkpoints
    positive = sum(1 for c in cases for cp in c["checkpoints"] if cp["expected_answer"] == "SUPPORTED")
    negative = sum(1 for c in cases for cp in c["checkpoints"] if cp["expected_answer"] in {"INSUFFICIENT_EVIDENCE", "UNKNOWN_CONTEXT", "NOT_OBSERVABLE"})
    abstention = sum(1 for c in cases for cp in c["checkpoints"] if cp["expected_answer"] in {"INSUFFICIENT_EVIDENCE", "UNKNOWN_CONTEXT", "NOT_OBSERVABLE", "USER_REJECTED", "DELETED"})
    ident = {k: sum(1 for c in cases for cp in c["checkpoints"] if cp["identifiability"] == k) for k in ("YES", "PARTIAL", "NO")}
    valid_events = sum(len(c["fixture"]["records"]) for c in cases if not qa["l2_errors"][c["case_id"]])
    return {
        "benchmark_version": VERSION,
        "status": qa["status"],
        "split": "dev",
        "synthetic_persons": len({c["person_id"] for c in cases}),
        "truth_configurations": len({c["spec"].config_id for c in cases}),
        "standard_truth_configurations": sum(1 for c in truth_configs() if c.risk_class == "STANDARD"),
        "high_risk_truth_configurations": sum(1 for c in truth_configs() if c.risk_class == "HIGH-RISK"),
        "histories": len(cases),
        "standard_histories": sum(1 for c in cases if c["config"].risk_class == "STANDARD"),
        "high_risk_histories": sum(1 for c in cases if c["config"].risk_class == "HIGH-RISK"),
        "checkpoints": checkpoints,
        "evaluation_units": units,
        "visible_l2_events": sum(len(c["fixture"]["records"]) for c in cases),
        "l2_valid_visible_events": valid_events,
        "counterfactual_pair_instances": 14,
        "counterfactual_templates_covered": len(PAIR_TEMPLATES),
        "positive_units": positive,
        "negative_or_no_positive_units": negative,
        "required_abstention_or_lifecycle_units": abstention,
        "false_promotion_denominator": qa["registered_negative_denominator"],
        "identifiability_units": ident,
        "behavior_seeds": sorted({c["spec"].behavior_replica for c in cases}),
        "observation_seeds": sorted({c["spec"].observation_replica for c in cases}),
        "reroll_count": 0,
        "architecture_boundary": "research tooling only; no Model/Kernel/Host changes",
    }


def generate_dev(root: Path = BENCH_ROOT) -> dict:
    specs = preregistered_histories()
    preregistration = _preregistration(specs)
    if root.exists():
        for child in ("generated/dev", "evaluator/dev", "manifests/dev"):
            target = root / child
            if target.exists():
                shutil.rmtree(target)
        for stale in (
            "reports/generator_qa.json",
            "reports/oracle_qa.json",
            "reports/dev_dataset_summary.json",
            "reports/e2-dev-summary.json",
            "manifests/dev_manifest.json",
            "manifests/public_benchmark_manifest.json",
            "manifests/pair_public_contract.json",
        ):
            target = root / stale
            if target.exists():
                target.unlink()
    (root / "specs").mkdir(parents=True, exist_ok=True)
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "VERSION").write_text(VERSION + "\n", encoding="utf-8", newline="\n")
    (root / "README.md").write_text(
        "# PPF-L3 Benchmark Artifacts\n\nThis directory contains the canonical PPF-L3 DEV benchmark artifacts only. DEV evaluator truth is development-only. Validation and final-test artifacts are not generated by E2.\n",
        encoding="utf-8",
        newline="\n",
    )
    write_json(root / "specs" / "public_execution_contract.json", {"benchmark_version": VERSION, "visible_inputs": ["history.json", "checkpoints.json"], "recognizer": "not implemented"})
    write_json(root / "specs" / "public_case_schema.json", _public_case_schema())
    write_json(root / "specs" / "validation_policy.json", _validation_policy())
    write_json(root / "manifests" / "pair_public_contract.json", _pair_public_contract())

    registration_path = root / "specs" / "dev_scenario_registry.json"
    write_json(registration_path, preregistration)
    persisted_registration = json.loads(registration_path.read_text(encoding="utf-8"))
    prereg_evidence = {
        "written_before_generation": semantic_hash(persisted_registration) == semantic_hash(preregistration),
        "registration_hash": semantic_hash(persisted_registration),
    }

    # Scientific order is fixed: preregister -> generate once -> retain all.
    cases = [generate_case(spec) for spec in specs]
    prereg_evidence["generated_history_count"] = len(cases)
    for c in cases:
        case_dir = root / "generated" / "dev" / "cases" / c["case_id"]
        write_json(case_dir / "history.json", method_visible_case(c))
        write_json(case_dir / "checkpoints.json", checkpoint_requests(c))
        write_json(root / "evaluator" / "dev" / "truth" / f"{c['case_id']}.json", evaluator_truth(c))
        write_json(root / "evaluator" / "dev" / "expected" / f"{c['case_id']}.json", expected_answers(c))
    write_json(root / "manifests" / "public_benchmark_manifest.json", _public_manifest(cases, root))
    dev_manifest = copy.deepcopy(preregistration)
    dev_manifest.update({
        "registration_hash": prereg_evidence["registration_hash"],
        "registered_history_count": len(preregistration["histories"]),
        "generated_history_count": len(cases),
        "retained_history_count": len(cases),
        "pair_instances": _pair_manifest(cases)["pairs"],
    })
    write_json(root / "manifests" / "dev_manifest.json", dev_manifest)

    qa = _qa(cases, preregistration, prereg_evidence, root)
    summary = _summary(cases, qa)
    write_json(root / "reports" / "generator_qa.json", qa)
    write_json(root / "reports" / "oracle_qa.json", {
        "benchmark_version": VERSION,
        "status": "PASS" if qa["e2_gates"]["E2-G8"] and qa["e2_gates"]["E2-G9"] and qa["e2_gates"]["E2-G10"] and qa["e2_gates"]["E2-G12"] else "REVISE",
        "checkpoint_future_leak_violations": qa["checkpoint_future_leak_violations"],
        "oracle_generic_threshold_found": qa["oracle_generic_threshold_found"],
        "lifecycle_checks": qa["lifecycle_checks"],
    })
    write_json(root / "reports" / "dev_dataset_summary.json", summary)
    return summary | {"qa": qa}


def run_e2(root: Path = BENCH_ROOT) -> dict:
    return generate_dev(root)
