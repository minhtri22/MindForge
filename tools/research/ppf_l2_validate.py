"""Research-only validator for the PPF-L2 representability proof.

This validates fixture structure and frozen semantic invariants only. It does not
infer, score, admit, retrieve, or otherwise implement personal patterns.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "research" / "data" / "ppf-l2"
SCHEMA_PATH = DATA / "schema.json"
FIXTURE_DIR = DATA / "fixtures"

MISSING_STATES = {
    "NO_OBSERVATION",
    "SOURCE_UNAVAILABLE",
    "PERMISSION_UNAVAILABLE_OR_UNKNOWN",
    "OUTSIDE_CAPTURE_WINDOW",
    "HISTORY_UNAVAILABLE",
    "DATA_DELAYED",
    "UNKNOWN_OUTCOME",
}

FORBIDDEN_PATTERN_KEYS = {
    "pattern",
    "pattern_status",
    "pattern_confidence",
    "routine_score",
    "preference_score",
    "admission_score",
    "confidence",
}


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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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

    allowed_duplicate_relations = {
        "SAME_ORIGIN_REPLICATED",
        "CORRECTS",
        "SUPERSEDES",
        "INVALIDATES",
        "DELETES",
    }
    for key, duplicate_records in source_ids.items():
        if len(duplicate_records) < 2:
            continue
        ids = [record["event_id"] for record in duplicate_records]
        for i, source_id in enumerate(ids):
            for target_id in ids[i + 1 :]:
                if not (
                    relation_exists(records, source_id, target_id, allowed_duplicate_relations)
                    or relation_exists(records, target_id, source_id, allowed_duplicate_relations)
                ):
                    errors.append(
                        f"source identity {key} reused by {source_id}/{target_id} without replica/correction lineage"
                    )
    return errors


def negative_tests(schema_validator: Draft202012Validator, sample: dict) -> list[str]:
    failures: list[str] = []
    base = copy.deepcopy(sample)

    def expect_fail(name: str, fixture: dict, custom_only: bool = False):
        schema_errors = list(schema_validator.iter_errors(fixture))
        semantic = semantic_errors(fixture) if not schema_errors else []
        if custom_only:
            if not semantic:
                failures.append(f"negative test unexpectedly passed: {name}")
        elif not schema_errors and not semantic:
            failures.append(f"negative test unexpectedly passed: {name}")

    bad = copy.deepcopy(base)
    event = bad["records"][0]
    event["observability"] = {"state": "OBSERVABLE_NON_OCCURRENCE"}
    event.pop("opportunity", None)
    expect_fail("observable_non_occurrence_without_opportunity", bad, custom_only=True)

    bad = copy.deepcopy(base)
    bad["records"][0].setdefault("relations", []).append(
        {"type": "CORRECTS", "target_event_id": "missing-event"}
    )
    expect_fail("invalid_lineage_target", bad, custom_only=True)

    bad = copy.deepcopy(base)
    duplicate = copy.deepcopy(bad["records"][0])
    duplicate["payload"] = {"different": True}
    bad["records"].append(duplicate)
    expect_fail("duplicate_event_identity", bad, custom_only=True)

    bad = copy.deepcopy(base)
    event = bad["records"][0]
    event["evidence_kind"] = "DERIVED_OBSERVATION"
    event["provenance"] = {"procedure_status": "KNOWN"}
    expect_fail("derived_missing_known_procedure", bad, custom_only=True)

    bad = copy.deepcopy(base)
    event = bad["records"][0]
    event["time"]["phenomenon_time"]["end"] = "2026-09-03T07:00:00Z"
    event["time"]["phenomenon_time"]["start"] = "2026-09-03T08:00:00Z"
    expect_fail("invalid_time_interval", bad, custom_only=True)

    bad = copy.deepcopy(base)
    bad["records"][0]["observability"]["state"] = "MAGIC_UNKNOWN_STATE"
    expect_fail("unknown_enum", bad)

    bad = copy.deepcopy(base)
    bad["records"][0]["android_package_name"] = "com.example.leak"
    expect_fail("platform_specific_core_field", bad)

    bad = copy.deepcopy(base)
    bad["records"][0]["payload"]["pattern_confidence"] = 0.9
    expect_fail("pattern_logic_leak", bad, custom_only=True)

    return failures


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(FIXTURE_DIR.glob("L2-F*.json"))
    if not paths:
        print("FAIL: no fixtures")
        return 1

    all_errors: list[str] = []
    fixture_ids: set[str] = set()
    global_event_ids: set[str] = set()
    fixtures: list[dict] = []

    for path in paths:
        fixture = load_json(path)
        fixtures.append(fixture)
        schema_errors = sorted(validator.iter_errors(fixture), key=lambda e: list(e.path))
        for error in schema_errors:
            all_errors.append(f"{path.name}: schema: {error.message}")
        if schema_errors:
            continue
        for error in semantic_errors(fixture):
            all_errors.append(f"{path.name}: semantic: {error}")

        fid = fixture["fixture_id"]
        if fid in fixture_ids:
            all_errors.append(f"duplicate fixture_id: {fid}")
        fixture_ids.add(fid)
        for record in fixture["records"]:
            eid = record["event_id"]
            if eid in global_event_ids:
                all_errors.append(f"global duplicate event_id: {eid}")
            global_event_ids.add(eid)

    if fixtures:
        all_errors.extend(negative_tests(validator, fixtures[0]))

    expected_ids = {f"L2-F{i:03d}" for i in range(1, len(paths) + 1)}
    if fixture_ids != expected_ids:
        all_errors.append("fixture ID sequence is not contiguous from L2-F001")

    adversarial = sum(1 for fixture in fixtures if fixture.get("adversarial"))
    pairs: dict[str, int] = {}
    for fixture in fixtures:
        pair = fixture.get("cross_platform_pair")
        if pair:
            pairs[pair] = pairs.get(pair, 0) + 1
    malformed_pairs = {pair: count for pair, count in pairs.items() if count != 2}
    if malformed_pairs:
        all_errors.append(f"cross-platform pair cardinality invalid: {malformed_pairs}")

    if len(fixtures) != 60:
        all_errors.append(f"expected exactly 60 fixtures, found {len(fixtures)}")
    if adversarial < 18:
        all_errors.append(f"expected at least 18 adversarial fixtures, found {adversarial}")
    if len(pairs) != 5:
        all_errors.append(f"expected exactly 5 cross-platform pairs, found {len(pairs)}")

    required_gates = {f"L2-G{i}" for i in range(1, 19)}
    covered_gates = {
        gate
        for fixture in fixtures
        for gate in fixture.get("gates", [])
    }
    missing_gates = sorted(required_gates - covered_gates)
    if missing_gates:
        all_errors.append(f"fixtures do not cover gates: {missing_gates}")

    if all_errors:
        print("FAIL")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print("PASS")
    print(f"fixtures={len(fixtures)}")
    print(f"adversarial={adversarial}")
    print(f"cross_platform_pairs={len(pairs)}")
    print(f"events={len(global_event_ids)}")
    print("negative_tests=8/8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
