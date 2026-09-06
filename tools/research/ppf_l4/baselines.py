from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
SUPPORTED = "SUPPORTED"


@dataclass(frozen=True)
class BaselineSpec:
    baseline_id: str
    name: str
    description: str
    parameters: dict[str, object]
    predict: Callable[[list[dict]], str]


def _is_behavior_record(record: dict) -> bool:
    return bool(record.get("opportunity")) and record.get("event_type") != "user.feedback"


def _determinate_records(records: Iterable[dict]) -> list[dict]:
    return [
        r
        for r in records
        if _is_behavior_record(r)
        and r.get("opportunity", {}).get("state")
        in {"OCCURRENCE", "OBSERVABLE_NON_OCCURRENCE"}
    ]


def _is_occurrence(record: dict) -> bool:
    return (
        record.get("opportunity", {}).get("state") == "OCCURRENCE"
        and record.get("observability", {}).get("state") == "OBSERVED_OCCURRENCE"
    )


def _counts(records: Iterable[dict]) -> tuple[int, int]:
    determinate = _determinate_records(records)
    occurrences = sum(1 for r in determinate if _is_occurrence(r))
    return occurrences, len(determinate) - occurrences


def _context_key(record: dict) -> tuple[tuple[str, str, str], ...]:
    parts: list[tuple[str, str, str]] = []
    for key, value in sorted(record.get("context", {}).items()):
        parts.append((key, str(value.get("status")), str(value.get("value"))))
    return tuple(parts)


def _latest_control(records: Iterable[dict]) -> dict | None:
    controls = [r for r in records if r.get("event_type") == "user.feedback"]
    if not controls:
        return None
    return max(
        controls,
        key=lambda r: (
            r.get("time", {}).get("ingested_time", ""),
            r.get("event_id", ""),
        ),
    )


def _control_state(record: dict) -> str | None:
    relation_types = {x.get("type") for x in record.get("relations", [])}
    operation = record.get("payload", {}).get("operation")
    if "DELETES" in relation_types or operation in {"remove", "reset"}:
        return "DELETED"
    if "CORRECTS" in relation_types or operation == "reject":
        return "USER_REJECTED"
    if relation_types & {"SUPERSEDES", "INVALIDATES"} or operation in {
        "supersede",
        "invalidate",
    }:
        return "SUPERSEDED"
    return None


def b0_always_abstain(records: list[dict]) -> str:
    del records
    return INSUFFICIENT


def b1_always_supported(records: list[dict]) -> str:
    del records
    return SUPPORTED


def b2_last_observation(records: list[dict]) -> str:
    determinate = _determinate_records(records)
    if not determinate:
        return INSUFFICIENT
    latest = max(
        determinate,
        key=lambda r: (
            r.get("time", {}).get("ingested_time", ""),
            r.get("event_id", ""),
        ),
    )
    return SUPPORTED if _is_occurrence(latest) else INSUFFICIENT


def b3_any_occurrence(records: list[dict]) -> str:
    return SUPPORTED if any(_is_occurrence(r) for r in _determinate_records(records)) else INSUFFICIENT


def b4_raw_count_threshold(records: list[dict]) -> str:
    occurrences, _ = _counts(records)
    return SUPPORTED if occurrences >= 3 else INSUFFICIENT


def b5_naive_frequency(records: list[dict]) -> str:
    occurrences, non_occurrences = _counts(records)
    total = occurrences + non_occurrences
    if total < 3:
        return INSUFFICIENT
    return SUPPORTED if occurrences / total >= 0.60 else INSUFFICIENT


def b6_recency_heuristic(records: list[dict]) -> str:
    determinate = sorted(
        _determinate_records(records),
        key=lambda r: (
            r.get("time", {}).get("ingested_time", ""),
            r.get("event_id", ""),
        ),
    )[-3:]
    if len(determinate) < 3:
        return INSUFFICIENT
    return SUPPORTED if sum(_is_occurrence(r) for r in determinate) >= 2 else INSUFFICIENT


def b7_naive_majority(records: list[dict]) -> str:
    occurrences, non_occurrences = _counts(records)
    if occurrences + non_occurrences < 3:
        return INSUFFICIENT
    return SUPPORTED if occurrences > non_occurrences else INSUFFICIENT


def b8_context_keyed_majority(records: list[dict]) -> str:
    determinate = sorted(
        _determinate_records(records),
        key=lambda r: (
            r.get("time", {}).get("ingested_time", ""),
            r.get("event_id", ""),
        ),
    )
    if not determinate:
        return INSUFFICIENT
    key = _context_key(determinate[-1])
    same_context = [r for r in determinate if _context_key(r) == key]
    occurrences = sum(_is_occurrence(r) for r in same_context)
    non_occurrences = len(same_context) - occurrences
    if len(same_context) < 3:
        return INSUFFICIENT
    return SUPPORTED if occurrences > non_occurrences else INSUFFICIENT


def b9_lifecycle_naive_rule(records: list[dict]) -> str:
    control = _latest_control(records)
    if control is not None:
        state = _control_state(control)
        if state is not None:
            return state
    return b7_naive_majority(records)


def b10_provenance_naive_counter(records: list[dict]) -> str:
    # Intentionally treats each source record as independent evidence even when
    # lineage marks it as a replica or derivation.
    occurrences = 0
    for record in _determinate_records(records):
        source = record.get("source", {})
        if source.get("provider") and source.get("source_event_id") and _is_occurrence(record):
            occurrences += 1
    return SUPPORTED if occurrences >= 3 else INSUFFICIENT


def b11_provenance_dedup_counter(records: list[dict]) -> str:
    # Minimal lineage-aware counter: one behavioral opportunity can contribute
    # at most once, and explicit replica/derived records never add recurrence.
    seen_opportunities: set[str] = set()
    occurrences = 0
    for record in _determinate_records(records):
        relation_types = {x.get("type") for x in record.get("relations", [])}
        if relation_types & {"SAME_ORIGIN_REPLICATED", "DERIVED_FROM"}:
            continue
        opportunity_id = record.get("opportunity", {}).get("id")
        if not opportunity_id or opportunity_id in seen_opportunities:
            continue
        seen_opportunities.add(opportunity_id)
        if _is_occurrence(record):
            occurrences += 1
    return SUPPORTED if occurrences >= 3 else INSUFFICIENT


BASELINES: tuple[BaselineSpec, ...] = (
    BaselineSpec("B0", "Always Abstain", "Always emit INSUFFICIENT_EVIDENCE.", {}, b0_always_abstain),
    BaselineSpec("B1", "Always Supported", "Always emit SUPPORTED.", {}, b1_always_supported),
    BaselineSpec("B2", "Last Observation", "Use only the last determinate observation.", {}, b2_last_observation),
    BaselineSpec("B3", "Any Occurrence", "Any visible occurrence promotes SUPPORTED.", {}, b3_any_occurrence),
    BaselineSpec("B4", "Raw Count Threshold", "Count all determinate occurrence records.", {"occurrence_threshold": 3}, b4_raw_count_threshold),
    BaselineSpec("B5", "Naive Frequency", "Global raw occurrence frequency heuristic.", {"minimum_records": 3, "support_frequency": 0.60}, b5_naive_frequency),
    BaselineSpec("B6", "Recency Heuristic", "Majority of the latest three determinate records.", {"window": 3, "support_occurrences": 2}, b6_recency_heuristic),
    BaselineSpec("B7", "Naive Majority", "Strict global majority over determinate records.", {"minimum_records": 3}, b7_naive_majority),
    BaselineSpec("B8", "Context-Keyed Majority", "Strict majority within the latest visible context key.", {"minimum_context_records": 3}, b8_context_keyed_majority),
    BaselineSpec("B9", "Lifecycle-Naive Rule", "Latest explicit control wins, else naive majority.", {"fallback": "B7"}, b9_lifecycle_naive_rule),
    BaselineSpec("B10", "Provenance-Naive Counter", "Count source records independently and ignore lineage.", {"occurrence_threshold": 3}, b10_provenance_naive_counter),
    BaselineSpec("B11", "Provenance-Dedup Counter", "Deduplicate replicas/derived evidence and opportunity IDs before counting.", {"occurrence_threshold": 3}, b11_provenance_dedup_counter),
)


BASELINE_BY_ID = {spec.baseline_id: spec for spec in BASELINES}

