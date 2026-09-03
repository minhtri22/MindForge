"""Research-only validator for the PPF-L2 representability proof."""
from __future__ import annotations
import copy
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from tools.research.ppf_l2_validation import (
    SCHEMA_PATH, load_json, semantic_errors,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "research" / "data" / "ppf-l2"
FIXTURE_DIR = DATA / "fixtures"

def negative_tests(schema_validator: Draft202012Validator, sample: dict) -> list[str]:
    failures: list[str] = []
    base = copy.deepcopy(sample)
    def expect_fail(name: str, fixture: dict, custom_only: bool = False):
        schema_errors = list(schema_validator.iter_errors(fixture))
        semantic = semantic_errors(fixture) if not schema_errors else []
        if custom_only:
            if not semantic: failures.append(f"negative test unexpectedly passed: {name}")
        elif not schema_errors and not semantic:
            failures.append(f"negative test unexpectedly passed: {name}")

    bad=copy.deepcopy(base); event=bad["records"][0]; event["observability"]={"state":"OBSERVABLE_NON_OCCURRENCE"}; event.pop("opportunity",None); expect_fail("observable_non_occurrence_without_opportunity",bad,True)
    bad=copy.deepcopy(base); bad["records"][0].setdefault("relations",[]).append({"type":"CORRECTS","target_event_id":"missing-event"}); expect_fail("invalid_lineage_target",bad,True)
    bad=copy.deepcopy(base); duplicate=copy.deepcopy(bad["records"][0]); duplicate["payload"]={"different":True}; bad["records"].append(duplicate); expect_fail("duplicate_event_identity",bad,True)
    bad=copy.deepcopy(base); event=bad["records"][0]; event["evidence_kind"]="DERIVED_OBSERVATION"; event["provenance"]={"procedure_status":"KNOWN"}; expect_fail("derived_missing_known_procedure",bad,True)
    bad=copy.deepcopy(base); event=bad["records"][0]; event["time"]["phenomenon_time"]["end"]="2026-09-03T07:00:00Z"; event["time"]["phenomenon_time"]["start"]="2026-09-03T08:00:00Z"; expect_fail("invalid_time_interval",bad,True)
    bad=copy.deepcopy(base); bad["records"][0]["observability"]["state"]="MAGIC_UNKNOWN_STATE"; expect_fail("unknown_enum",bad)
    bad=copy.deepcopy(base); bad["records"][0]["android_package_name"]="com.example.leak"; expect_fail("platform_specific_core_field",bad)
    bad=copy.deepcopy(base); bad["records"][0]["payload"]["pattern_confidence"]=0.9; expect_fail("pattern_logic_leak",bad,True)
    return failures

def main() -> int:
    schema=load_json(SCHEMA_PATH); validator=Draft202012Validator(schema, format_checker=FormatChecker()); paths=sorted(FIXTURE_DIR.glob("L2-F*.json"))
    if not paths:
        print("FAIL: no fixtures"); return 1
    all_errors=[]; fixture_ids=set(); global_event_ids=set(); fixtures=[]
    for path in paths:
        fixture=load_json(path); fixtures.append(fixture); se=sorted(validator.iter_errors(fixture), key=lambda e:list(e.path))
        all_errors.extend(f"{path.name}: schema: {e.message}" for e in se)
        if se: continue
        all_errors.extend(f"{path.name}: semantic: {e}" for e in semantic_errors(fixture))
        fid=fixture["fixture_id"]
        if fid in fixture_ids: all_errors.append(f"duplicate fixture_id: {fid}")
        fixture_ids.add(fid)
        for record in fixture["records"]:
            eid=record["event_id"]
            if eid in global_event_ids: all_errors.append(f"global duplicate event_id: {eid}")
            global_event_ids.add(eid)
    if fixtures: all_errors.extend(negative_tests(validator,fixtures[0]))
    expected_ids={f"L2-F{i:03d}" for i in range(1,len(paths)+1)}
    if fixture_ids != expected_ids: all_errors.append("fixture ID sequence is not contiguous from L2-F001")
    adversarial=sum(1 for f in fixtures if f.get("adversarial")); pairs={}
    for f in fixtures:
        p=f.get("cross_platform_pair")
        if p: pairs[p]=pairs.get(p,0)+1
    malformed={p:c for p,c in pairs.items() if c!=2}
    if malformed: all_errors.append(f"cross-platform pair cardinality invalid: {malformed}")
    if len(fixtures)!=60: all_errors.append(f"expected exactly 60 fixtures, found {len(fixtures)}")
    if adversarial<18: all_errors.append(f"expected at least 18 adversarial fixtures, found {adversarial}")
    if len(pairs)!=5: all_errors.append(f"expected exactly 5 cross-platform pairs, found {len(pairs)}")
    required={f"L2-G{i}" for i in range(1,19)}; covered={g for f in fixtures for g in f.get("gates",[])}; missing=sorted(required-covered)
    if missing: all_errors.append(f"fixtures do not cover gates: {missing}")
    if all_errors:
        print("FAIL"); [print(f"- {e}") for e in all_errors]; return 1
    print("PASS"); print(f"fixtures={len(fixtures)}"); print(f"adversarial={adversarial}"); print(f"cross_platform_pairs={len(pairs)}"); print(f"events={len(global_event_ids)}"); print("negative_tests=8/8"); return 0
if __name__=="__main__": raise SystemExit(main())
