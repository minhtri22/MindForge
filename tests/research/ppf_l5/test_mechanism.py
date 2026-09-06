from __future__ import annotations

import pytest

from tools.research.ppf_l4.baselines import BASELINE_BY_ID
from tools.research.ppf_l5.mechanism import TREATMENT_BY_ID, TREATMENTS, predict, validate_method_payload
from tools.research.ppf_l5.evaluate import predict_split
from tools.research.ppf_l5.run_l5 import _selection


def _record(event_id: str, occurrence: bool = True, *, obs: str | None = None, context_status: str = "KNOWN", opportunity_id: str | None = None) -> dict:
    state = "OCCURRENCE" if occurrence else "OBSERVABLE_NON_OCCURRENCE"
    return {
        "event_id": event_id,
        "event_type": "activity.sample",
        "evidence_kind": "RAW_OBSERVATION",
        "time": {"ingested_time": f"2026-01-01T00:00:{int(event_id[-1]):02d}Z"},
        "observability": {"state": obs or ("OBSERVED_OCCURRENCE" if occurrence else "OBSERVABLE_NON_OCCURRENCE")},
        "opportunity": {"id": opportunity_id or f"opp-{event_id}", "state": state, "observability": "FULL"},
        "context": {"relationship": {"status": context_status, "value": "known" if context_status == "KNOWN" else None}},
        "quality": {"quality_state": "GOOD", "coverage_state": "COMPLETE"},
        "payload": {},
    }


def _unobservable(event_id: str, state: str) -> dict:
    row = _record(event_id)
    row["event_type"] = "source.observability"
    row["evidence_kind"] = "OBSERVABILITY_RECORD"
    row["observability"] = {"state": state}
    row["opportunity"] = {"id": f"opp-{event_id}", "state": "UNKNOWN_OUTCOME", "observability": "UNKNOWN"}
    return row


def _control(relation: str, operation: str) -> dict:
    return {
        "event_id": "control",
        "event_type": "user.feedback",
        "time": {"ingested_time": "2026-01-01T01:00:00Z"},
        "payload": {"operation": operation},
        "relations": [{"type": relation, "target_event_id": "e1"}],
    }


def _supported_base() -> list[dict]:
    return [_record("e1"), _record("e2"), _record("e3")]


def test_registry_is_exact_t0_through_t7():
    assert [t.treatment_id for t in TREATMENTS] == [f"T{i}" for i in range(8)]


def test_t0_exactly_delegates_to_b9():
    samples = [
        _supported_base(),
        [_record("e1"), _record("e2", False), _record("e3", False)],
        _supported_base() + [_control("CORRECTS", "reject")],
        _supported_base() + [_control("DELETES", "remove")],
    ]
    for records in samples:
        assert predict(records, TREATMENT_BY_ID["T0"]) == BASELINE_BY_ID["B9"].predict(records)


def test_e1_no_observation_is_not_behavioral_negative_and_blocks_active_promotion():
    records = _supported_base() + [_unobservable("e4", "NO_OBSERVATION")]
    assert predict(records, TREATMENT_BY_ID["T1"]) == "NOT_OBSERVABLE"
    records[-1]["observability"]["state"] = "PERMISSION_UNAVAILABLE_OR_UNKNOWN"
    assert predict(records, TREATMENT_BY_ID["T1"]) == "NOT_OBSERVABLE"


def test_e2_all_unknown_required_context_abstains():
    records = [_record("e1", context_status="UNKNOWN"), _record("e2", context_status="UNKNOWN"), _record("e3", context_status="UNKNOWN")]
    assert predict(records, TREATMENT_BY_ID["T2"]) == "UNKNOWN_CONTEXT"


def test_e3_requires_explicit_conflict_semantics():
    records = _supported_base()
    records[-1]["context"]["relationship"]["status"] = "CONFLICTING"
    assert predict(records, TREATMENT_BY_ID["T3"]) == "CONFLICTING_EVIDENCE"
    same = [_record("e1", True, opportunity_id="opp-x"), _record("e2", False, opportunity_id="opp-x"), _record("e3", True)]
    assert predict(same, TREATMENT_BY_ID["T3"]) == "CONFLICTING_EVIDENCE"


def test_e4_explicit_history_unavailable_marks_prior_support_stale():
    records = _supported_base() + [_unobservable("e4", "HISTORY_UNAVAILABLE")]
    assert predict(records, TREATMENT_BY_ID["T4"]) == "STALE"


def test_lifecycle_controls_dominate_all_components():
    rejected = _supported_base() + [_unobservable("e4", "NO_OBSERVATION"), _control("CORRECTS", "reject")]
    deleted = _supported_base() + [_unobservable("e4", "NO_OBSERVATION"), _control("DELETES", "remove")]
    assert predict(rejected, TREATMENT_BY_ID["T7"]) == "USER_REJECTED"
    assert predict(deleted, TREATMENT_BY_ID["T7"]) == "DELETED"


def test_private_evaluator_fields_are_rejected():
    with pytest.raises(ValueError):
        validate_method_payload({"history": [], "truth_kind": "STABLE_PATTERN"})
    with pytest.raises(ValueError):
        validate_method_payload({"history": [{"payload": {"expected_answer": "SUPPORTED"}}]})


def test_l5_runner_refuses_l3_final(tmp_path):
    with pytest.raises(ValueError, match="FINAL"):
        predict_split(tmp_path, "final", TREATMENT_BY_ID["T0"])


def _fake_result(rows: dict[str, tuple[float, float, float, dict]]) -> dict:
    return {
        "treatments": [
            {
                "treatment_id": tid,
                "metrics": {
                    "exact_state_accuracy": exact,
                    "false_promotion_rate": fp,
                    "pattern_recall_status_proxy": recall,
                    "hard_violations": hard,
                },
            }
            for tid, (exact, fp, recall, hard) in rows.items()
        ]
    }


def test_selection_is_deterministic_and_prefers_fewer_components():
    base_hard = {
        "deleted_active_return_violations": 0,
        "correction_resurrection_violations": 0,
        "stale_as_current_violations": 3,
        "not_observable_as_current_violations": 4,
        "unknown_context_positive_violations": 4,
        "conflict_positive_violations": 1,
    }
    rows = {"T0": (0.70, 0.30, 0.90, base_hard)}
    for treatment in TREATMENTS[1:]:
        hard = dict(base_hard)
        for component in treatment.components:
            key = {"E1": "not_observable_as_current_violations", "E2": "unknown_context_positive_violations", "E3": "conflict_positive_violations", "E4": "stale_as_current_violations"}[component]
            hard[key] = max(0, hard[key] - 1)
        rows[treatment.treatment_id] = (0.71, 0.29, 0.90, hard)
    dev = _fake_result(rows)
    val = _fake_result(rows)
    assert _selection(dev, val)["selected_treatment"] == "T1"
