"""Shared frozen PPF-L2 validation helpers for research tooling.

This module centralizes schema + semantic validation. It does not infer patterns.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "research" / "data" / "ppf-l2" / "schema.json"

MISSING_STATES = {
    "NO_OBSERVATION", "SOURCE_UNAVAILABLE", "PERMISSION_UNAVAILABLE_OR_UNKNOWN",
    "OUTSIDE_CAPTURE_WINDOW", "HISTORY_UNAVAILABLE", "DATA_DELAYED", "UNKNOWN_OUTCOME",
}
FORBIDDEN_PATTERN_KEYS = {
    "pattern", "pattern_status", "pattern_confidence", "routine_score",
    "preference_score", "admission_score", "confidence",
}

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def forbidden_payload_paths(value, prefix: str = "payload") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key in FORBIDDEN_PATTERN_KEYS:
                paths.append(path)
            paths.extend(forbidden_payload_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(forbidden_payload_paths(child, f"{prefix}[{index}]"))
    return paths

def relation_exists(records, source_id: str, target_id: str, allowed: set[str]) -> bool:
    for record in records:
        if record["event_id"] != source_id:
            continue
        for rel in record.get("relations", []):
            if rel["target_event_id"] == target_id and rel["type"] in allowed:
                return True
    return False

def semantic_errors(fixture: dict) -> list[str]:
    errors: list[str] = []
    records = fixture["records"]
    event_ids = {record["event_id"] for record in records}
    if len(event_ids) != len(records):
        errors.append("duplicate event_id inside fixture")

    source_ids: dict[tuple[str, str, str], list[dict]] = {}
    for record in records:
        source = record["source"]
        source_event_id = source.get("source_event_id")
        if source_event_id:
            key = (source["platform"], source["provider"], source_event_id)
            source_ids.setdefault(key, []).append(record)

        ptime = record["time"]["phenomenon_time"]
        if "end" in ptime and parse_time(ptime["end"]) < parse_time(ptime["start"]):
            errors.append(f"{record['event_id']}: phenomenon interval ends before start")

        state = record["observability"]["state"]
        if state in MISSING_STATES and "missingness_reason" not in record["observability"]:
            errors.append(f"{record['event_id']}: missing-like state lacks missingness_reason")
        if state == "OBSERVABLE_NON_OCCURRENCE":
            opportunity = record.get("opportunity")
            if not opportunity or opportunity["state"] != "OBSERVABLE_NON_OCCURRENCE":
                errors.append(f"{record['event_id']}: observable non-occurrence lacks explicit opportunity")

        if record["evidence_kind"] == "DERIVED_OBSERVATION":
            provenance = record["provenance"]
            if provenance["procedure_status"] == "NOT_APPLICABLE":
                errors.append(f"{record['event_id']}: derived observation cannot have NOT_APPLICABLE procedure")
            if provenance["procedure_status"] == "KNOWN" and not provenance.get("procedure"):
                errors.append(f"{record['event_id']}: known derivation procedure missing procedure reference")

        for ref in record["provenance"].get("input_event_refs", []):
            if ref not in event_ids:
                errors.append(f"{record['event_id']}: unresolved input_event_ref {ref}")
        for rel in record.get("relations", []):
            if rel["target_event_id"] not in event_ids:
                errors.append(f"{record['event_id']}: unresolved relation target {rel['target_event_id']}")

        if record["event_type"].startswith("pattern."):
            errors.append(f"{record['event_id']}: pattern-level event_type leaks into L2")
        leaked = forbidden_payload_paths(record["payload"])
        if leaked:
            errors.append(f"{record['event_id']}: pattern-level payload keys {sorted(leaked)}")

        if record["evidence_kind"] in {"RAW_OBSERVATION", "DERIVED_OBSERVATION", "OBSERVABILITY_RECORD"}:
            if record["source"]["platform"] != "USER" and "capture_policy" not in record:
                errors.append(f"{record['event_id']}: passive/source evidence lacks capture_policy provenance")

    allowed_duplicate_relations = {"SAME_ORIGIN_REPLICATED", "CORRECTS", "SUPERSEDES", "INVALIDATES", "DELETES"}
    for key, duplicate_records in source_ids.items():
        if len(duplicate_records) < 2:
            continue
        ids = [record["event_id"] for record in duplicate_records]
        for i, source_id in enumerate(ids):
            for target_id in ids[i + 1:]:
                if not (relation_exists(records, source_id, target_id, allowed_duplicate_relations)
                        or relation_exists(records, target_id, source_id, allowed_duplicate_relations)):
                    errors.append(f"source identity {key} reused by {source_id}/{target_id} without replica/correction lineage")
    return errors

def schema_errors(fixture: dict, schema_path: Path = SCHEMA_PATH) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(fixture), key=lambda e: list(e.path))]

def validate_fixture(fixture: dict, schema_path: Path = SCHEMA_PATH) -> list[str]:
    errors = schema_errors(fixture, schema_path)
    if not errors:
        errors.extend(semantic_errors(fixture))
    return errors
