"""Independent CPRM-1 execution-lock verifier.

This module is intentionally static:
- it does not import experiments.cprm.cprm1_response_support;
- it does not call preflight, collect, adjudicate, or any scientific harness;
- it does not execute any CPRM-1 fresh seed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import platform
import re
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "docs/research/continual-policy-response/CPRM1_EXECUTION_LOCK.json"
PROTOCOL = ROOT / "docs/research/continual-policy-response/cprm1-response-support-protocol.md"
RUNNER = ROOT / "experiments/cprm/cprm1_response_support.py"
TESTS = ROOT / "tests/test_cprm1_response_support.py"
PREFLIGHT_WORKFLOW = ROOT / ".github/workflows/cprm1-zero-science-preflight.yml"

EXPECTED_LOCK_SHA256 = "26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274"
EXPECTED_IMPLEMENTATION_COMMIT = "e955c4962846cda8cac633c4c9fd49b40a901750"
EXPECTED_PROTOCOL_BLOB = "f61aabc5605400faea30e5d2af4349a2b32c792f"
EXPECTED_RUNNER_BLOB = "18774a9349adeb4a0e5d66ce46416564640f41aa"
EXPECTED_TEST_BLOB = "dd54c5aaba63cf0fa649b5db445aec476e2a3847"
EXPECTED_PREFLIGHT_WORKFLOW_BLOB = "20968ba824194c6530b6a393d8aa5848b4fed79a"
EXPECTED_SEED_MANIFEST_SHA256 = "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3"
EXPECTED_SPENT_ACO_MANIFEST_SHA256 = "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91"
EXPECTED_PROTECTED = (
    13635,13837,14039,14241,14443,
    14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,
    16665,16867,17069,17271,17473,
)
SPENT_ACO = (
    714845,799297,471852,671302,797856,525370,494800,333039,618491,662800,
    265044,434671,501990,723350,393434,774787,806053,890854,613906,707487,
    415555,641958,505262,776960,428051,767077,464825,448672,416287,770416,
    596609,359597,454064,431281,705347,294795,641624,345481,326782,242385,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(values: tuple[int, ...] | list[int]) -> str:
    raw = ",".join(str(int(x)) for x in values).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_blob(path: Path) -> str:
    return git("hash-object", str(path.relative_to(ROOT)))


def _literal_assignments(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            out[target.id] = ast.literal_eval(node.value)
        except Exception:
            pass
    return out


def _historical_kcl_seed_candidates() -> set[int]:
    paths: list[Path] = [ROOT / "Lineage.md"]
    for base in (
        ROOT / "docs/research/kernel-continual-learning",
        ROOT / "experiments/kernel_cl",
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out: set[int] = set()
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


def _execution_workflows() -> list[str]:
    hits: list[str] = []
    wf = ROOT / ".github/workflows"
    if not wf.exists():
        return hits
    for path in wf.glob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if (
            "experiments/cprm/cprm1_response_support.py" in text
            and "--phase collect" in text
        ):
            hits.append(str(path.relative_to(ROOT)))
    return sorted(hits)


def verify() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    source_text = RUNNER.read_text(encoding="utf-8")
    assigns = _literal_assignments(RUNNER)
    fresh = tuple(int(x) for x in lock["seed_manifest"]["seeds"])
    historical = _historical_kcl_seed_candidates()
    protected = set(int(x) for x in lock["excluded_assets"]["protected_kcl_seeds"])
    spent = set(SPENT_ACO)

    checks: dict[str, bool] = {}

    checks["lock_hash_exact"] = sha256_file(LOCK) == EXPECTED_LOCK_SHA256
    checks["lock_schema"] = lock.get("schema") == "CPRM1-EXECUTION-LOCK-v1"
    checks["program_identity"] = lock.get("program") == "CPRM-1"
    checks["implementation_commit_exact"] = (
        lock["implementation"]["commit"] == EXPECTED_IMPLEMENTATION_COMMIT
    )

    checks["protocol_blob_exact"] = (
        git_blob(PROTOCOL)
        == lock["protocol"]["git_blob_sha"]
        == EXPECTED_PROTOCOL_BLOB
    )
    checks["runner_blob_exact"] = (
        git_blob(RUNNER)
        == lock["implementation"]["runner_git_blob_sha"]
        == EXPECTED_RUNNER_BLOB
    )
    checks["test_blob_exact"] = (
        git_blob(TESTS)
        == lock["implementation"]["test_git_blob_sha"]
        == EXPECTED_TEST_BLOB
    )
    checks["preflight_workflow_blob_exact"] = (
        git_blob(PREFLIGHT_WORKFLOW)
        == lock["implementation"]["workflow_git_blob_sha"]
        == EXPECTED_PREFLIGHT_WORKFLOW_BLOB
    )

    checks["seed_count_exact"] = len(fresh) == 60 and len(set(fresh)) == 60
    checks["seed_manifest_exact"] = (
        manifest_hash(fresh)
        == lock["seed_manifest"]["sha256"]
        == EXPECTED_SEED_MANIFEST_SHA256
    )
    checks["source_seed_tuple_exact"] = tuple(assigns.get("FRESH_SEEDS", ())) == fresh
    checks["source_seed_hash_constant_exact"] = (
        assigns.get("SEED_MANIFEST_SHA256") == EXPECTED_SEED_MANIFEST_SHA256
    )

    checks["protected_list_exact"] = tuple(lock["excluded_assets"]["protected_kcl_seeds"]) == EXPECTED_PROTECTED
    checks["spent_manifest_exact"] = (
        manifest_hash(SPENT_ACO)
        == lock["excluded_assets"]["spent_aco_seed_manifest_sha256"]
        == EXPECTED_SPENT_ACO_MANIFEST_SHA256
    )
    checks["historical_kcl_disjoint"] = set(fresh).isdisjoint(historical)
    checks["protected_kcl_disjoint"] = set(fresh).isdisjoint(protected)
    checks["spent_aco_disjoint"] = set(fresh).isdisjoint(spent)

    pop = lock["population"]
    checks["support_contract_exact"] = (
        pop["seed_count"] == 60
        and pop["boundaries_per_seed"] == 3
        and pop["expected_boundaries"] == 180
        and pop["expected_per_stage"] == {"1":60,"2":60,"3":60}
        and pop["expected_response_vectors"] == 540
        and pop["policies"] == [
            "A_CARRY_ALL",
            "B_RESET_ALL",
            "C_CARRY_STEP_RESET_MOMENTS",
        ]
    )
    checks["source_support_constants_exact"] = (
        assigns.get("EXPECTED_SEEDS") == 60
        and assigns.get("EXPECTED_BOUNDARIES") == 180
        and assigns.get("EXPECTED_PER_STAGE") == 60
    )

    gates = lock["geometry_gates"]
    checks["geometry_gates_exact"] = (
        gates["response_cell"] == {
            "min_unique":4,
            "min_robust_span_resolution_units":2,
        }
        and gates["response_component"] == {
            "min_qualified_policy_stage_cells":6,
            "min_qualified_stages":2,
            "min_qualified_policies":2,
            "all_four_components_required":True,
        }
        and gates["contrast_cell"] == {
            "min_unique":4,
            "min_robust_span_resolution_units":2,
            "min_nonzero_fraction":0.2,
        }
        and gates["contrast_component"] == {
            "min_magnitude_supported_stages":2,
            "direction_positive_fraction":0.1,
            "direction_negative_fraction":0.1,
            "min_sign_stages":2,
            "min_seeds_per_sign_stage":3,
        }
        and gates["contrast_family"] == {
            "min_magnitude_supported_components":2,
            "min_direction_supported_components":1,
            "both_BA_and_CA_required":True,
        }
    )
    checks["source_geometry_constants_exact"] = all([
        assigns.get("CELL_MIN_UNIQUE") == 4,
        assigns.get("CELL_SPAN_RESOLUTION_MULT") == 2.0,
        assigns.get("RESPONSE_COMPONENT_MIN_CELLS") == 6,
        assigns.get("RESPONSE_COMPONENT_MIN_STAGES") == 2,
        assigns.get("RESPONSE_COMPONENT_MIN_POLICIES") == 2,
        assigns.get("CONTRAST_NONZERO_MIN") == 0.20,
        assigns.get("CONTRAST_DIRECTION_MIN") == 0.10,
        assigns.get("CONTRAST_STAGE_SIGN_MIN") == 3,
        assigns.get("CONTRAST_COMPONENT_MIN_STAGES") == 2,
        assigns.get("CONTRAST_FAMILY_MIN_MAG_COMPONENTS") == 2,
        assigns.get("CONTRAST_FAMILY_MIN_DIR_COMPONENTS") == 1,
    ])

    retry = lock["technical_retry_policy"]
    checks["retry_policy_frozen"] = (
        retry["collection_retry_only_before_complete_valid_collection"] is True
        and retry["retry_same_seed_same_lock"] is True
        and retry["seed_substitution"] is False
        and retry["outcome_inspection_before_retry"] is False
        and retry["complete_valid_collection_must_not_be_rerun"] is True
        and retry["adjudication_exactly_one_valid_run"] is True
        and retry["adjudication_retry_only_if_no_valid_formal_result"] is True
        and retry["any_source_protocol_seed_dependency_or_gate_change_invalidates_lock"] is True
    )
    checks["protocol_retry_language_present"] = all(
        phrase in protocol_text
        for phrase in [
            "do not replace a seed",
            "once a complete valid collection exists, collection must not be rerun",
            "exactly one valid one-shot adjudication",
            "Any scientific-source, protocol, seed, dependency or gate change invalidates",
        ]
    )

    runtime = lock["runtime"]
    checks["runtime_exact"] = (
        platform.machine() == runtime["architecture"] == "x86_64"
        and platform.python_version() == runtime["python"] == "3.12.14"
        and version("pip") == runtime["pip"] == "26.2.1"
        and version("numpy") == runtime["numpy"] == "2.3.3"
        and version("pytest") == runtime["pytest"] == "8.4.2"
        and torch.__version__ == runtime["torch"] == "2.10.0+cpu"
        and runtime["device"] == "CPU"
        and runtime["deterministic_algorithms"] is True
        and runtime["torch_num_threads"] == 1
    )

    checks["one_shot_contract_exact"] = (
        lock["adjudication"]["one_shot"] is True
        and lock["adjudication"]["pass"] == "PASS_RESPONSE_SUPPORT"
        and lock["adjudication"]["negative"] == "NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED"
        and lock["adjudication"]["stop"] == "STOP_INTEGRITY_OR_SUPPORT"
        and lock["adjudication"]["no_intermediate_scientific_metric_inspection_before_adjudication"] is True
    )
    checks["cprm2_transition_exact"] = (
        lock["next_transition"]["cprm2_design_authorized_only_if"]
        == "CPRM-1 canonical verdict == PASS_RESPONSE_SUPPORT"
        and lock["next_transition"]["controller_remains_closed"] is True
        and lock["next_transition"]["kcl7_remains_closed"] is True
    )

    checks["fresh_collection_absent"] = not (ROOT / lock["outputs"]["collection"]).exists()
    checks["formal_result_absent"] = not (ROOT / lock["outputs"]["formal_result"]).exists()
    execution_hits = _execution_workflows()
    checks["fresh_execution_workflow_absent"] = not execution_hits

    # Static anti-execution guarantees for this verifier itself.
    verifier_source = Path(__file__).read_text(encoding="utf-8")
    checks["verifier_does_not_import_runner"] = (
        "import experiments.cprm.cprm1_response_support" not in verifier_source
        and "from experiments.cprm" not in verifier_source
    )
    checks["verifier_does_not_call_scientific_phases"] = all(
        token not in verifier_source
        for token in [
            "--phase collect",
            "--phase adjudicate",
            "build_response_records(",
            "collect_fresh(",
            "adjudicate_records(",
        ]
    )

    ok = all(checks.values())
    return {
        "schema": "CPRM1-EXECUTION-LOCK-VERIFICATION-v1",
        "program": "CPRM-1",
        "status": "PASS" if ok else "FAIL",
        "verdict": (
            "CPRM1_EXECUTION_LOCK_VERIFICATION_PASS"
            if ok else
            "CPRM1_EXECUTION_LOCK_VERIFICATION_FAIL"
        ),
        "head_commit": git("rev-parse", "HEAD"),
        "lock_sha256": sha256_file(LOCK),
        "checks": checks,
        "collisions": {
            "historical_kcl": sorted(set(fresh) & historical),
            "protected_kcl": sorted(set(fresh) & protected),
            "spent_aco": sorted(set(fresh) & spent),
        },
        "execution_workflow_hits": execution_hits,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "model_fitting_performed": False,
    }


def main() -> int:
    out = ROOT / "artifacts/cprm1_execution_lock_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
