from tools.research.ppf_l4.baselines import BASELINE_BY_ID, BASELINES


def _record(
    event_id: str,
    occurrence: bool,
    *,
    context: str = "a",
    relation: str | None = None,
    evidence_kind: str = "RAW_OBSERVATION",
    opportunity_id: str | None = None,
) -> dict:
    record = {
        "event_id": event_id,
        "event_type": "activity.sample",
        "evidence_kind": evidence_kind,
        "source": {"provider": "sensor", "source_event_id": f"src-{event_id}"},
        "time": {"ingested_time": f"2026-01-01T00:00:{int(event_id[-1]):02d}Z"},
        "observability": {"state": "OBSERVED_OCCURRENCE" if occurrence else "OBSERVABLE_NON_OCCURRENCE"},
        "opportunity": {
            "id": opportunity_id or f"opp-{event_id}",
            "state": "OCCURRENCE" if occurrence else "OBSERVABLE_NON_OCCURRENCE",
        },
        "context": {"segment": {"status": "KNOWN", "value": context}},
    }
    if relation:
        record["relations"] = [{"type": relation, "target_event_id": "e0"}]
    return record


def _control(relation: str, operation: str) -> dict:
    return {
        "event_id": "control",
        "event_type": "user.feedback",
        "time": {"ingested_time": "2026-01-01T01:00:00Z"},
        "payload": {"operation": operation},
        "relations": [{"type": relation, "target_event_id": "e0"}],
    }


def test_registry_is_exact_b0_through_b11():
    assert [x.baseline_id for x in BASELINES] == [f"B{i}" for i in range(12)]
    assert [x.name for x in BASELINES] == [
        "Always Abstain",
        "Always Supported",
        "Last Observation",
        "Any Occurrence",
        "Raw Count Threshold",
        "Naive Frequency",
        "Recency Heuristic",
        "Naive Majority",
        "Context-Keyed Majority",
        "Lifecycle-Naive Rule",
        "Provenance-Naive Counter",
        "Provenance-Dedup Counter",
    ]


def test_trivial_and_count_baselines():
    records = [_record("e1", True), _record("e2", True), _record("e3", True)]
    assert BASELINE_BY_ID["B0"].predict(records) == "INSUFFICIENT_EVIDENCE"
    assert BASELINE_BY_ID["B1"].predict(records) == "SUPPORTED"
    assert BASELINE_BY_ID["B3"].predict(records) == "SUPPORTED"
    assert BASELINE_BY_ID["B4"].predict(records) == "SUPPORTED"


def test_last_observation_and_recency_can_disagree():
    records = [_record("e1", True), _record("e2", True), _record("e3", False)]
    assert BASELINE_BY_ID["B2"].predict(records) == "INSUFFICIENT_EVIDENCE"
    assert BASELINE_BY_ID["B6"].predict(records) == "SUPPORTED"


def test_context_keyed_majority_uses_latest_context_only():
    records = [
        _record("e1", True, context="a"),
        _record("e2", True, context="a"),
        _record("e3", True, context="a"),
        _record("e4", False, context="b"),
        _record("e5", False, context="b"),
        _record("e6", False, context="b"),
    ]
    assert BASELINE_BY_ID["B8"].predict(records) == "INSUFFICIENT_EVIDENCE"


def test_lifecycle_naive_rule_respects_explicit_controls():
    base = [_record("e1", True), _record("e2", True), _record("e3", True)]
    assert BASELINE_BY_ID["B9"].predict(base + [_control("CORRECTS", "reject")]) == "USER_REJECTED"
    assert BASELINE_BY_ID["B9"].predict(base + [_control("DELETES", "remove")]) == "DELETED"
    assert BASELINE_BY_ID["B9"].predict(base + [_control("SUPERSEDES", "supersede")]) == "SUPERSEDED"


def test_provenance_dedup_blocks_same_origin_inflation():
    base = _record("e1", True, opportunity_id="opp-1")
    replica = _record("e2", True, relation="SAME_ORIGIN_REPLICATED", opportunity_id="opp-1")
    derived = _record("e3", True, relation="DERIVED_FROM", evidence_kind="DERIVED_OBSERVATION", opportunity_id="opp-1")
    records = [base, replica, derived]
    assert BASELINE_BY_ID["B10"].predict(records) == "SUPPORTED"
    assert BASELINE_BY_ID["B11"].predict(records) == "INSUFFICIENT_EVIDENCE"

