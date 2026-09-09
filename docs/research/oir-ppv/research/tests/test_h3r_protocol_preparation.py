import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_required_h3r_source_of_truth_structure_exists():
    required = [
        "ontology/ontology_v1.0.md",
        "ontology/ontology_v1.0_amendment_001.md",
        "formal/formal_spec_v1.0.md",
        "formal/formal_spec_v1.0_closure.md",
        "formal/formal_spec_v1.0_manifest.json",
        "protocols/h3/historical/README.md",
        "protocols/h3r/H3_TO_H3R_LINEAGE.md",
        "protocols/h3r/H3R_PROTOCOL_v1.0_DRAFT.md",
        "protocols/h3r/h3r_protocol_schema.json",
        "protocols/h3r/h3r_freeze_checklist.md",
        "governance/research_status_v1.0.md",
        "governance/protocol_versioning.md",
        "governance/claim_registry.md",
        "governance/v1.0_source_of_truth_manifest.json",
        "archive/README.md",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing


def test_formal_spec_manifest_hashes_match_canonical_files():
    manifest = json.loads((ROOT / "formal/formal_spec_v1.0_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "FINAL"
    assert manifest["closure"] == "SPECIFICATION_CLOSED_AFTER_FIX_01"
    assert manifest["p0_blockers"] == 0
    assert manifest["p1_blockers"] == 0
    assert manifest["sha256"]["ontology_v1.0"] == _sha256(ROOT / "ontology/ontology_v1.0.md")
    assert manifest["sha256"]["formal_spec_v1.0"] == _sha256(ROOT / "formal/formal_spec_v1.0.md")
    assert manifest["sha256"]["formal_spec_v1.0_closure"] == _sha256(ROOT / "formal/formal_spec_v1.0_closure.md")


def test_formal_spec_contains_all_fix01_closure_items():
    spec = (ROOT / "formal/formal_spec_v1.0.md").read_text(encoding="utf-8")
    required_markers = [
        "Representation lifecycle/scope",
        "shared probe",
        "causal-identification contract",
        "split-unit contract",
        "component-wise cost schema",
        "uncertainty-aware Pareto dominance",
    ]
    for marker in required_markers:
        assert marker.lower() in spec.lower()


def test_h3_historical_evidence_identity_and_erratum_are_preserved():
    report = ROOT / "experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v3/H3_CLOSURE_REPORT_v3.md"
    summary = ROOT / "experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v3/h3_summary_v3.json"
    assert _sha256(report) == "4e717c6863f0f06cfb0496b804828492b8bbb4402ce7f45cac6c3ea323ecc497"
    assert _sha256(summary) == "ae91e3e5b1b443159ec7d94b6c9fcb1bb5012566b6226788bfdb749238d665a0"
    assert json.loads(summary.read_text(encoding="utf-8"))["version"] == 2
    historical = (ROOT / "protocols/h3/historical/README.md").read_text(encoding="utf-8")
    assert "CLOSED_WITH_LIMITS / NOT_SUPPORTED" in historical
    assert 'embedded field `"version": 2`' in historical
    assert "superseded_evidence: false" in historical


def test_h3r_lineage_separates_semantics_from_historical_evidence():
    lineage = (ROOT / "protocols/h3r/H3_TO_H3R_LINEAGE.md").read_text(encoding="utf-8")
    assert "relation_to_historical_h3: REVISED_SUCCESSOR" in lineage
    assert "supersedes_protocol_semantics: true" in lineage
    assert "supersedes_historical_evidence: false" in lineage
    assert "**NO.** H3 evidence" in lineage


def test_h3r_draft_is_preserved_and_frozen_protocol_has_no_tbd():
    draft = (ROOT / "protocols/h3r/H3R_PROTOCOL_v1.0_DRAFT.md").read_text(encoding="utf-8")
    protocol = (ROOT / "protocols/h3r/H3R_PROTOCOL_v1.0.md").read_text(encoding="utf-8")
    assert "status: DRAFT" in draft
    assert "freeze_status: NOT_FROZEN" in draft
    assert "TBD_BEFORE_FREEZE" in draft
    assert "status: FROZEN" in protocol
    assert "execution_status: NOT_EXECUTED" in protocol
    assert "freeze_status: FROZEN" in protocol
    assert "TBD_BEFORE_FREEZE" not in protocol
    assert "H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`" in protocol


def test_h3r_frozen_protocol_instance_and_test_lock_are_consistent():
    instance = json.loads((ROOT / "protocols/h3r/h3r_protocol_v1.0.json").read_text(encoding="utf-8"))
    manifest_path = ROOT / instance["test_lock"]["test_manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    protocol_path = ROOT / "protocols/h3r/H3R_PROTOCOL_v1.0.md"
    assert instance["identity"]["status"] == "FROZEN"
    assert instance["identity"]["execution_status"] == "NOT_EXECUTED"
    assert instance["identity"]["freeze_status"] == "FROZEN"
    assert instance["test_lock"]["test_access_count"] == 0
    assert instance["provenance"]["protocol_sha256"] == _sha256(protocol_path)
    assert instance["test_lock"]["test_hash"] == _sha256(manifest_path)
    assert manifest["cell_count"] == 20
    assert manifest["total_test_rows"] == 6131
    assert set(manifest["historical_test_seeds_excluded"]).isdisjoint(manifest["h3r_seeds"])


def test_h3r_protocol_schema_validates_frozen_instance():
    import jsonschema

    schema = json.loads((ROOT / "protocols/h3r/h3r_protocol_schema.json").read_text(encoding="utf-8"))
    instance = json.loads((ROOT / "protocols/h3r/h3r_protocol_v1.0.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(instance)


def test_h3r_schema_and_source_of_truth_manifest_parse_and_require_scientific_groups():
    schema = json.loads((ROOT / "protocols/h3r/h3r_protocol_schema.json").read_text(encoding="utf-8"))
    source = json.loads((ROOT / "governance/v1.0_source_of_truth_manifest.json").read_text(encoding="utf-8"))
    required_groups = {
        "identity",
        "historical_lineage",
        "representation_scope",
        "mechanism_contract",
        "shift_contract",
        "split_contract",
        "noise_contract",
        "metrics",
        "metric_registry",
        "utility_guard",
        "baseline",
        "candidate_set",
        "equivalence_contract",
        "evidence_contract",
        "statistical_plan",
        "pareto_rule",
        "cost_contract",
        "test_lock",
        "acceptance",
        "claim_boundary",
        "provenance",
    }
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert required_groups == set(schema["required"])
    assert source["frontier"]["H3R"] == "PROTOCOL_FROZEN / NOT_EXECUTED / TEST_LOCKED"
    assert source["frontier"]["H4"] == "NOT_OPENED"


def test_source_of_truth_manifest_hashes_match_all_non_self_canonical_entries():
    manifest = json.loads((ROOT / "governance/v1.0_source_of_truth_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["canonical"].values():
        if "sha256" not in entry:
            continue
        assert _sha256(ROOT / entry["path"]) == entry["sha256"]


def test_no_h3r_decisive_result_namespace_exists_and_h4_remains_unopened():
    assert not (ROOT / "experiments/OIR_PPV/H3R").exists()
    assert not (ROOT / "artifacts/h3r").exists()
    plan = (ROOT / "PLAN.md").read_text(encoding="utf-8")
    assert "H4  NOT_OPENED / DEFERRED_BY_OWNER" in plan
    assert "H3R PROTOCOL_v1.0_FROZEN / NOT_EXECUTED / TEST_LOCKED" in plan
