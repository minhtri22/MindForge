from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from tools.research.ppf_l4.baselines import BASELINE_BY_ID


L5_VERSION = "ppf-l5-minimum-missing-mechanism/v1"
SUPPORTED = "SUPPORTED"
NOT_OBSERVABLE = "NOT_OBSERVABLE"
UNKNOWN_CONTEXT = "UNKNOWN_CONTEXT"
CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
STALE = "STALE"

# Evaluator-only keys must never be accepted by the method boundary.
FORBIDDEN_METHOD_KEYS = {
    "truth",
    "truth_kind",
    "expected_answer",
    "expected_answers",
    "identifiability",
    "identifiability_by_checkpoint",
    "families",
    "pair_template",
    "pair_arm",
    "risk_class",
    "lifecycle_variant",
    "holdout",
    "holdout_label",
    "structural_holdout",
}

E1_UNOBSERVABLE_STATES = {
    "NO_OBSERVATION",
    "SOURCE_UNAVAILABLE",
    "PERMISSION_UNAVAILABLE_OR_UNKNOWN",
    "DATA_DELAYED",
    "UNKNOWN_OUTCOME",
}
E4_CURRENTNESS_STATES = {"HISTORY_UNAVAILABLE", "OUTSIDE_CAPTURE_WINDOW"}


@dataclass(frozen=True)
class TreatmentSpec:
    treatment_id: str
    description: str
    components: tuple[str, ...]


TREATMENTS: tuple[TreatmentSpec, ...] = (
    TreatmentSpec("T0", "Frozen L4 B9 Lifecycle-Naive Rule", ()),
    TreatmentSpec("T1", "B9 + E1 observability eligibility", ("E1",)),
    TreatmentSpec("T2", "B9 + E2 context eligibility", ("E2",)),
    TreatmentSpec("T3", "B9 + E3 explicit conflict eligibility", ("E3",)),
    TreatmentSpec("T4", "B9 + E4 explicit currentness eligibility", ("E4",)),
    TreatmentSpec("T5", "B9 + E1 + E2", ("E1", "E2")),
    TreatmentSpec("T6", "B9 + E1 + E2 + E3", ("E1", "E2", "E3")),
    TreatmentSpec("T7", "B9 + E1 + E2 + E3 + E4", ("E1", "E2", "E3", "E4")),
)
TREATMENT_BY_ID = {item.treatment_id: item for item in TREATMENTS}


def validate_method_payload(value: object) -> None:
    """Reject evaluator-only metadata if it crosses the method boundary."""
    if isinstance(value, dict):
        forbidden = FORBIDDEN_METHOD_KEYS.intersection(value)
        if forbidden:
            raise ValueError(f"evaluator-only method input keys: {sorted(forbidden)}")
        for child in value.values():
            validate_method_payload(child)
    elif isinstance(value, list):
        for child in value:
            validate_method_payload(child)


def _sort_key(record: dict) -> tuple[str, str]:
    return (record.get("time", {}).get("ingested_time", ""), record.get("event_id", ""))


def _latest_control_state(records: Iterable[dict]) -> str | None:
    controls = [r for r in records if r.get("event_type") == "user.feedback"]
    if not controls:
        return None
    control = max(controls, key=_sort_key)
    relation_types = {x.get("type") for x in control.get("relations", [])}
    operation = control.get("payload", {}).get("operation")
    if "DELETES" in relation_types or operation in {"remove", "reset"}:
        return "DELETED"
    if "CORRECTS" in relation_types or operation == "reject":
        return "USER_REJECTED"
    if relation_types & {"SUPERSEDES", "INVALIDATES"} or operation in {"supersede", "invalidate"}:
        return "SUPERSEDED"
    return None


def _behavior_records(records: Iterable[dict]) -> list[dict]:
    return [
        r
        for r in records
        if r.get("event_type") != "user.feedback"
        and r.get("opportunity", {}).get("state")
        in {"OCCURRENCE", "OBSERVABLE_NON_OCCURRENCE"}
    ]


def _latest_non_control(records: Iterable[dict]) -> dict | None:
    values = [r for r in records if r.get("event_type") != "user.feedback"]
    return max(values, key=_sort_key) if values else None


def _e1_observability_gate(records: list[dict]) -> str | None:
    latest = _latest_non_control(records)
    if latest is None:
        return None
    if latest.get("observability", {}).get("state") in E1_UNOBSERVABLE_STATES:
        return NOT_OBSERVABLE
    return None


def _e2_context_gate(records: list[dict]) -> str | None:
    determinate = _behavior_records(records)
    if not determinate:
        return None
    common_dimensions = set(determinate[0].get("context", {}))
    for record in determinate[1:]:
        common_dimensions.intersection_update(record.get("context", {}))
    for dimension in sorted(common_dimensions):
        statuses = {
            record.get("context", {}).get(dimension, {}).get("status")
            for record in determinate
        }
        if statuses == {"UNKNOWN"}:
            return UNKNOWN_CONTEXT
    return None


def _e3_conflict_gate(records: list[dict]) -> str | None:
    # L5 deliberately refuses a count/frequency conflict detector. Only explicit
    # L2 conflict markers or incompatible determinate outcomes for the exact
    # same opportunity are admissible here.
    determinate = _behavior_records(records)
    for record in determinate:
        if any(v.get("status") == "CONFLICTING" for v in record.get("context", {}).values()):
            return CONFLICTING_EVIDENCE
    by_opportunity: dict[str, set[str]] = {}
    for record in determinate:
        opportunity = record.get("opportunity", {})
        opportunity_id = opportunity.get("id")
        if opportunity_id:
            by_opportunity.setdefault(opportunity_id, set()).add(str(opportunity.get("state")))
    if any({"OCCURRENCE", "OBSERVABLE_NON_OCCURRENCE"}.issubset(states) for states in by_opportunity.values()):
        return CONFLICTING_EVIDENCE
    return None


def _e4_currentness_gate(records: list[dict]) -> str | None:
    # No age threshold is used: DEV contains STALE and SUPPORTED checkpoints
    # with overlapping recency gaps. E4 therefore reacts only to explicit L2
    # history/window currentness loss.
    latest = _latest_non_control(records)
    if latest is None:
        return None
    if latest.get("observability", {}).get("state") in E4_CURRENTNESS_STATES:
        return STALE
    return None


COMPONENT_GATES = {
    "E1": _e1_observability_gate,
    "E2": _e2_context_gate,
    "E3": _e3_conflict_gate,
    "E4": _e4_currentness_gate,
}


def predict(records: list[dict], treatment: TreatmentSpec) -> str:
    validate_method_payload(records)

    # Explicit correction/deletion/supersession remains dominant in every L5
    # treatment. This is exactly the lifecycle part of frozen B9.
    lifecycle_state = _latest_control_state(records)
    if lifecycle_state is not None:
        return lifecycle_state

    b9 = BASELINE_BY_ID["B9"].predict(records)
    if treatment.treatment_id == "T0" or b9 != SUPPORTED:
        return b9

    for component in treatment.components:
        gated = COMPONENT_GATES[component](records)
        if gated is not None:
            return gated
    return b9

