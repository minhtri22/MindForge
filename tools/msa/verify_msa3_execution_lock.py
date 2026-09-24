"""Independent static verification of the MSA-3 execution lock.

No MSA scientific module is imported or executed.
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
LOCK = ROOT / "docs/research/measurement-substrate-adequacy/MSA3_EXECUTION_LOCK.json"
MSA1_LOCK = ROOT / "docs/research/measurement-substrate-adequacy/MSA1_EXECUTION_LOCK.json"
PROTOCOL = ROOT / "docs/research/measurement-substrate-adequacy/msa3-independent-replication-protocol.md"
WRAPPER = ROOT / "experiments/msa/msa3_independent_replication.py"
MSA1_RUNNER = ROOT / "experiments/msa/msa1_endpoint_adequacy.py"
TESTS = ROOT / "tests/test_msa3_independent_replication.py"
PREFLIGHT_WORKFLOW = ROOT / ".github/workflows/msa3-zero-science-preflight.yml"

EXPECTED_LOCK_SHA256 = "bd8deb49030d98d2c11254d792065ceaef2e4e53d8db35489efb2c15570d66a7"
EXPECTED_IMPLEMENTATION_COMMIT = "191639c572b5db72a7ea323aeb82bd683de09bdb"
EXPECTED_PROTOCOL_BLOB = "edd84edfe189af94578cc89dfcdc5e40f54e759a"
EXPECTED_WRAPPER_BLOB = "530521780d61f5dc2848476ed0c966c1a8fbcd1d"
EXPECTED_MSA1_RUNNER_BLOB = "55d6686c6c1182b7706f4831cb8f49eec2ec032d"
EXPECTED_TEST_BLOB = "a23c1752a32165c3be4de2d16d54119431c72498"
EXPECTED_PREFLIGHT_WORKFLOW_BLOB = "e4ea000cca7cefa9ef9d2c6cabbab4f8433905a3"
EXPECTED_SEED_HASH = "5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8"
EXPECTED_PHRASE = "MindForge|MSA-3|independent-fresh-replication|v1"
EXPECTED_DISCOVERY_VERDICT = "ACCURACY_COARSE_LOSS_INFORMATIVE"
EXPECTED_DISCOVERY_RESULT_SHA256 = "359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637"
EXPECTED_SUBSTRATE_BLOBS = {
    "experiments/kernel_cl/kcl1_substrate.py": "4303dd544e0bdb935c499abedc62aa095bc56674",
    "experiments/kernel_cl/kcl6_long_horizon.py": "33a743d62b5a83286c8945ffc0f473ae66fe50c0",
    "experiments/kernel_cl/kcl61_weighted_replay_ab.py": "9a2ea8435bc92d65af7044b5351d06adc6cc2d44",
    "experiments/kernel_cl/kcl63_fuzzy_decay_abcd.py": "cb6cf442d9d6a01c6cec173ecd73771fc6ba30c7",
    "experiments/kernel_cl/kcl65_specificity_ab.py": "88aa11fea6e8474c323c02491c0b85a91722c686",
    "experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py": "7119b9520f50de53a42313f7c7173c8d5daec2f1",
    "mindforge/config.py": "54ab270a25edd962e62360e14736b28f52a4fbcd",
    "mindforge/model.py": "3f6b8f1f411d7a3ba061d4bca10cd0002ae91594",
}
EXPECTED_PROTECTED = {
    13635,13837,14039,14241,14443,
    14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,
    16665,16867,17069,17271,17473,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(values) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_blob(path: Path) -> str:
    return git("hash-object", str(path.relative_to(ROOT)))


def literal_assignments(path: Path) -> dict[str, Any]:
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


def regenerate_seeds(phrase: str, count: int) -> tuple[int, ...]:
    accepted: list[int] = []
    seen: set[int] = set()
    i = 0
    while len(accepted) < count:
        digest = hashlib.sha256(f"{phrase}|{i}".encode()).digest()
        candidate = 2_000_000 + (int.from_bytes(digest[:8], "big") % 7_000_000)
        if candidate not in seen:
            accepted.append(candidate)
            seen.add(candidate)
        i += 1
    return tuple(accepted)


def historical_seed_candidates(fresh: set[int]) -> set[int]:
    out: set[int] = set()
    roots = [
        ROOT / "docs/research/kernel-continual-learning",
        ROOT / "experiments/kernel_cl",
        ROOT / "Lineage.md",
    ]
    paths: list[Path] = []
    for item in roots:
        if item.is_file():
            paths.append(item)
        elif item.exists():
            paths.extend(p for p in item.rglob("*") if p.is_file())
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out - fresh


def execution_workflows() -> list[str]:
    hits: list[str] = []
    wfdir = ROOT / ".github/workflows"
    if not wfdir.exists():
        return hits
    for path in wfdir.glob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if (
            "experiments/msa/msa3_independent_replication.py" in text
            and "--phase collect" in text
        ):
            hits.append(str(path.relative_to(ROOT)))
    return sorted(hits)


def static_safety() -> dict[str, bool]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    import_msa = False
    scientific_call = False
    scientific_subprocess = False
    forbidden = {
        "preflight","collect_fresh","adjudicate_replication",
        "build_endpoint_records","adjudicate_records",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_msa = import_msa or any(
                alias.name.startswith("experiments.msa") for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            import_msa = import_msa or (
                isinstance(node.module, str)
                and node.module.startswith("experiments.msa")
            )
        elif isinstance(node, ast.Call):
            fn = node.func
            name = (
                fn.id if isinstance(fn, ast.Name)
                else fn.attr if isinstance(fn, ast.Attribute)
                else None
            )
            if name in forbidden:
                scientific_call = True
            if name in {"run","call","check_call","check_output","Popen"}:
                literals = [
                    x.value for x in ast.walk(node)
                    if isinstance(x, ast.Constant) and isinstance(x.value, str)
                ]
                if (
                    any("msa3_independent_replication.py" in s for s in literals)
                    and any("python" in s.lower() for s in literals)
                ):
                    scientific_subprocess = True
    return {
        "does_not_import_msa": not import_msa,
        "does_not_call_scientific_api": not scientific_call,
        "does_not_launch_scientific_runner": not scientific_subprocess,
    }


def verify() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    msa1_lock = json.loads(MSA1_LOCK.read_text(encoding="utf-8"))
    wrapper_assigns = literal_assignments(WRAPPER)
    msa1_assigns = literal_assignments(MSA1_RUNNER)

    fresh = tuple(int(x) for x in lock["seed_manifest"]["seeds"])
    fresh_set = set(fresh)
    regenerated = regenerate_seeds(EXPECTED_PHRASE, 72)
    historical = historical_seed_candidates(fresh_set)
    protected = EXPECTED_PROTECTED
    aco = set(msa1_assigns["SPENT_ACO_SEEDS"])
    cprm = set(msa1_assigns["SPENT_CPRM_SEEDS"])
    msa1_spent = set(msa1_lock["seed_manifest"]["seeds"])

    checks: dict[str, bool] = {}

    checks["lock_hash_exact"] = sha256_file(LOCK) == EXPECTED_LOCK_SHA256
    checks["lock_schema_exact"] = lock.get("schema") == "MSA3-EXECUTION-LOCK-v1"
    checks["program_exact"] = lock.get("program") == "MSA-3"
    checks["implementation_commit_exact"] = (
        lock["implementation"]["commit"] == EXPECTED_IMPLEMENTATION_COMMIT
    )

    checks["protocol_blob_exact"] = (
        git_blob(PROTOCOL)
        == lock["protocol"]["git_blob_sha"]
        == EXPECTED_PROTOCOL_BLOB
    )
    checks["wrapper_blob_exact"] = (
        git_blob(WRAPPER)
        == lock["implementation"]["wrapper_git_blob_sha"]
        == EXPECTED_WRAPPER_BLOB
    )
    checks["msa1_classifier_blob_exact"] = (
        git_blob(MSA1_RUNNER)
        == lock["implementation"]["reused_msa1_runner_git_blob_sha"]
        == EXPECTED_MSA1_RUNNER_BLOB
    )
    checks["test_blob_exact"] = (
        git_blob(TESTS)
        == lock["implementation"]["test_git_blob_sha"]
        == EXPECTED_TEST_BLOB
    )
    checks["preflight_workflow_blob_exact"] = (
        git_blob(PREFLIGHT_WORKFLOW)
        == lock["implementation"]["preflight_workflow_git_blob_sha"]
        == EXPECTED_PREFLIGHT_WORKFLOW_BLOB
    )

    actual_substrate = {
        p: git_blob(ROOT / p) for p in EXPECTED_SUBSTRATE_BLOBS
    }
    checks["eight_substrate_blobs_exact"] = (
        lock["substrate"]["git_blobs"] == EXPECTED_SUBSTRATE_BLOBS
        and actual_substrate == EXPECTED_SUBSTRATE_BLOBS
    )
    checks["substrate_unchanged"] = (
        lock["substrate"]["difficulty_mutation_allowed"] is False
        and lock["substrate"]["endpoint_step"] == 250
        and lock["substrate"]["task_order"] == msa1_lock["substrate"]["task_order"]
        and lock["substrate"]["policies"] == msa1_lock["substrate"]["policies"]
    )

    checks["discovery_binding_exact"] = (
        lock["discovery"]["verdict"] == EXPECTED_DISCOVERY_VERDICT
        and lock["discovery"]["formal_result_sha256"] == EXPECTED_DISCOVERY_RESULT_SHA256
        and wrapper_assigns.get("DISCOVERY_VERDICT") == EXPECTED_DISCOVERY_VERDICT
    )

    checks["seed_count_unique_exact"] = len(fresh) == 72 and len(fresh_set) == 72
    checks["seed_hash_exact"] = (
        manifest_hash(fresh)
        == lock["seed_manifest"]["sha256"]
        == EXPECTED_SEED_HASH
    )
    checks["seed_phrase_exact"] = (
        lock["seed_manifest"]["generation_phrase"] == EXPECTED_PHRASE
        and wrapper_assigns.get("SEED_GENERATION_PHRASE") == EXPECTED_PHRASE
    )
    checks["seed_regeneration_exact"] = fresh == regenerated
    checks["wrapper_seed_tuple_exact"] = tuple(wrapper_assigns.get("FRESH_SEEDS", ())) == fresh
    checks["wrapper_seed_hash_exact"] = (
        wrapper_assigns.get("SEED_MANIFEST_SHA256") == EXPECTED_SEED_HASH
    )

    checks["historical_kcl_disjoint"] = fresh_set.isdisjoint(historical)
    checks["protected_kcl_disjoint"] = fresh_set.isdisjoint(protected)
    checks["aco_spent_disjoint"] = fresh_set.isdisjoint(aco)
    checks["cprm_spent_disjoint"] = fresh_set.isdisjoint(cprm)
    checks["msa1_spent_disjoint"] = fresh_set.isdisjoint(msa1_spent)
    checks["msa1_spent_hash_exact"] = (
        manifest_hash(tuple(msa1_lock["seed_manifest"]["seeds"]))
        == lock["excluded_evidence"]["spent_msa1_manifest_sha256"]
        == msa1_lock["seed_manifest"]["sha256"]
    )

    checks["scientific_contract_exact_copy"] = (
        lock["scientific_contract"]["accuracy"] == msa1_lock["gates"]["accuracy"]
        and lock["scientific_contract"]["loss"] == msa1_lock["gates"]["loss"]
        and lock["scientific_contract"]["classification_matrix"]
        == msa1_lock["gates"]["classifications"]
        and lock["scientific_contract"]["endpoints"]
        == ["terminal_accuracy","terminal_cross_entropy_loss"]
    )

    checks["replication_rule_exact"] = (
        lock["replication"] == {
            "success_criterion": "underlying verdict == ACCURACY_COARSE_LOSS_INFORMATIVE",
            "success_status": "REPLICATION_CONFIRMED",
            "failure_status": "REPLICATION_NOT_CONFIRMED",
            "partial_match_allowed": False,
            "post_outcome_gate_change_allowed": False,
        }
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

    retry = lock["technical_retry_policy"]
    checks["retry_policy_exact"] = (
        retry["collection_retry_only_before_complete_valid_collection"] is True
        and retry["same_seed_same_lock"] is True
        and retry["seed_substitution"] is False
        and retry["difficulty_change"] is False
        and retry["source_or_gate_change"] is False
        and retry["outcome_inspection_before_retry"] is False
        and retry["complete_valid_collection_must_not_be_rerun"] is True
        and retry["adjudication_exactly_one_valid_run"] is True
        and retry["adjudication_retry_only_if_no_valid_formal_result"] is True
        and retry["source_protocol_seed_runtime_or_gate_change_invalidates_lock"] is True
    )

    checks["adjudication_contract_exact"] = (
        lock["adjudication"]["one_shot"] is True
        and lock["adjudication"]["no_intermediate_endpoint_classification_inspection"] is True
        and lock["adjudication"]["underlying_classifier"] == "exact MSA-1 adjudicate_records"
        and lock["adjudication"]["allowed_replication_status"]
        == ["REPLICATION_CONFIRMED","REPLICATION_NOT_CONFIRMED"]
    )

    collection = ROOT / lock["outputs"]["collection"]
    formal = ROOT / lock["outputs"]["formal_result"]
    workflow_hits = execution_workflows()
    checks["fresh_collection_absent"] = not collection.exists()
    checks["formal_result_absent"] = not formal.exists()
    checks["fresh_execution_workflow_absent"] = not workflow_hits

    safety = static_safety()
    checks["verifier_independent"] = all(safety.values())

    checks["downstream_closed"] = (
        lock["downstream"]["msa2_closed"] is True
        and lock["downstream"]["predictor_closed"] is True
        and lock["downstream"]["controller_closed"] is True
        and lock["downstream"]["kcl7_closed"] is True
    )

    ok = all(checks.values())
    return {
        "schema": "MSA3-EXECUTION-LOCK-VERIFICATION-v1",
        "program": "MSA-3",
        "status": "PASS" if ok else "FAIL",
        "verdict": (
            "MSA3_EXECUTION_LOCK_VERIFICATION_PASS"
            if ok else
            "MSA3_EXECUTION_LOCK_VERIFICATION_FAIL"
        ),
        "head_commit": git("rev-parse", "HEAD"),
        "lock_sha256": sha256_file(LOCK),
        "checks": checks,
        "collisions": {
            "historical_kcl": sorted(fresh_set & historical),
            "protected_kcl": sorted(fresh_set & protected),
            "spent_aco": sorted(fresh_set & aco),
            "spent_cprm": sorted(fresh_set & cprm),
            "spent_msa1": sorted(fresh_set & msa1_spent),
        },
        "execution_workflow_hits": workflow_hits,
        "static_safety": safety,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "difficulty_mutation_performed": False,
        "predictor_fitting_performed": False,
    }


def main() -> int:
    out = ROOT / "artifacts/msa3_execution_lock_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
