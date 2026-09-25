"""Independent static verification of the CLRM-1 execution lock.

This verifier does not import or execute the CLRM-1 scientific runner.
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

LOCK = ROOT / "docs/research/continual-loss-response/CLRM1_EXECUTION_LOCK.json"
PROTOCOL = ROOT / "docs/research/continual-loss-response/clrm1-loss-response-support-protocol.md"
MANIFEST = ROOT / "docs/research/continual-loss-response/CLRM1_ROLE_S_SEED_MANIFEST.json"
RUNNER = ROOT / "experiments/clrm/clrm1_loss_response_support.py"
TESTS = ROOT / "tests/test_clrm1_loss_response_support.py"
PREFLIGHT_QA = ROOT / "docs/research/continual-loss-response/CLRM1_PREFLIGHT_QA.md"
MSA1_RUNNER = ROOT / "experiments/msa/msa1_endpoint_adequacy.py"
MSA3_RUNNER = ROOT / "experiments/msa/msa3_independent_replication.py"

EXPECTED_LOCK_SHA256 = "39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e"
EXPECTED_PROTOCOL_BLOB = "6560f7ff12b98bfcdead97661c934b58abe3a437"
EXPECTED_MANIFEST_BLOB = "3060fe5f6d348390f3dbcdc1ceb7471084635318"
EXPECTED_RUNNER_BLOB = "deb0c30af6a981705587637706e98ddc1cbc1ceb"
EXPECTED_TEST_BLOB = "00333df9b8293409f6a40cada3dfa763e61035e8"
EXPECTED_IMPLEMENTATION_COMMIT = "2b8f29547b29a63bf3f4131a0cdd48cfb48c3e63"
EXPECTED_SEED_HASH = "3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6"
EXPECTED_PHRASE = "MindForge|CLRM-1|role-s-loss-response-support|v1"
EXPECTED_PREFLIGHT_JSON_SHA256 = "d32e2efd209a8dcfd7ba6a1b2db9790536e65233817a3c476046c9758702976b"

EXPECTED_SPENT_HASHES = {
    "ACO-1": "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91",
    "CPRM-1": "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3",
    "MSA-1": "e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347",
    "MSA-3": "5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8",
}
EXPECTED_PROTECTED = {
    13635,13837,14039,14241,14443,
    14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,
    16665,16867,17069,17271,17473,
}
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


def historical_kcl_seeds() -> set[int]:
    paths = [ROOT / "Lineage.md"]
    for base in (
        ROOT / "docs/research/kernel-continual-learning",
        ROOT / "experiments/kernel_cl",
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out: set[int] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


def spent_sequences() -> dict[str, tuple[int, ...]]:
    m1 = literal_assignments(MSA1_RUNNER)
    m3 = literal_assignments(MSA3_RUNNER)
    return {
        "ACO-1": tuple(m1["SPENT_ACO_SEEDS"]),
        "CPRM-1": tuple(m1["SPENT_CPRM_SEEDS"]),
        "MSA-1": tuple(m1["FRESH_SEEDS"]),
        "MSA-3": tuple(m3["FRESH_SEEDS"]),
    }


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
            "experiments/clrm/clrm1_loss_response_support.py" in text
            and "--phase collect" in text
        ):
            hits.append(str(path.relative_to(ROOT)))
    return sorted(hits)


def static_safety() -> dict[str, bool]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports_clrm = False
    scientific_call = False
    launches_runner = False
    forbidden = {
        "preflight",
        "collect_fresh",
        "adjudicate_records",
        "build_response_records",
        "run_response_counterfactual",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports_clrm = imports_clrm or any(
                alias.name.startswith("experiments.clrm") for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            imports_clrm = imports_clrm or (
                isinstance(node.module, str)
                and node.module.startswith("experiments.clrm")
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
            if name in {"run", "call", "check_call", "check_output", "Popen"}:
                literals = [
                    x.value for x in ast.walk(node)
                    if isinstance(x, ast.Constant) and isinstance(x.value, str)
                ]
                if (
                    any("clrm1_loss_response_support.py" in s for s in literals)
                    and any("python" in s.lower() for s in literals)
                ):
                    launches_runner = True

    return {
        "does_not_import_clrm": not imports_clrm,
        "does_not_call_scientific_api": not scientific_call,
        "does_not_launch_scientific_runner": not launches_runner,
    }


def verify() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    runner = literal_assignments(RUNNER)

    fresh = tuple(int(x) for x in lock["seed_manifest"]["seeds"])
    fresh_set = set(fresh)
    regenerated = regenerate_seeds(EXPECTED_PHRASE, 72)
    spent = spent_sequences()
    historical = historical_kcl_seeds()

    checks: dict[str, bool] = {}

    checks["lock_hash_exact"] = sha256_file(LOCK) == EXPECTED_LOCK_SHA256
    checks["lock_schema_exact"] = lock["schema"] == "CLRM1-EXECUTION-LOCK-v1"
    checks["program_role_exact"] = (
        lock["program"] == "CLRM-1" and lock["role"] == "S_SUPPORT_ONLY"
    )
    checks["implementation_commit_exact"] = (
        lock["implementation"]["commit"] == EXPECTED_IMPLEMENTATION_COMMIT
    )

    checks["protocol_blob_exact"] = (
        git_blob(PROTOCOL)
        == lock["protocol"]["git_blob_sha"]
        == EXPECTED_PROTOCOL_BLOB
    )
    checks["manifest_blob_exact"] = (
        git_blob(MANIFEST)
        == lock["seed_manifest"]["git_blob_sha"]
        == EXPECTED_MANIFEST_BLOB
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

    actual_substrate = {
        p: git_blob(ROOT / p) for p in EXPECTED_SUBSTRATE_BLOBS
    }
    checks["eight_substrate_blobs_exact"] = (
        lock["substrate"]["git_blobs"] == EXPECTED_SUBSTRATE_BLOBS
        and actual_substrate == EXPECTED_SUBSTRATE_BLOBS
    )
    checks["substrate_identity_exact"] = (
        lock["substrate"]["endpoint_step"] == 250
        and lock["substrate"]["difficulty_mutation_allowed"] is False
        and lock["substrate"]["task_order"]
        == ["T1_U1_A", "T2_U1_B", "T3_U3_A", "T4_U3_B"]
        and lock["substrate"]["policies"]
        == ["A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS"]
    )

    checks["seed_count_unique_exact"] = len(fresh) == 72 and len(fresh_set) == 72
    checks["seed_phrase_exact"] = (
        lock["seed_manifest"]["generation_phrase"] == EXPECTED_PHRASE
        and runner["SEED_GENERATION_PHRASE"] == EXPECTED_PHRASE
    )
    checks["seed_regeneration_exact"] = fresh == regenerated
    checks["seed_hash_exact"] = (
        manifest_hash(fresh)
        == lock["seed_manifest"]["sha256"]
        == EXPECTED_SEED_HASH
        == manifest["sha256"]
    )
    checks["seed_sequence_exact_everywhere"] = (
        tuple(manifest["seeds"]) == fresh
        and tuple(runner["FRESH_SEEDS"]) == fresh
    )

    collisions = {
        "historical_kcl": sorted(fresh_set & historical),
        "protected_kcl": sorted(fresh_set & EXPECTED_PROTECTED),
    }
    checks["historical_kcl_disjoint"] = not collisions["historical_kcl"]
    checks["protected_kcl_disjoint"] = not collisions["protected_kcl"]

    for name, seq in spent.items():
        collisions[name] = sorted(fresh_set & set(seq))
        checks[f"{name}_hash_exact"] = (
            manifest_hash(seq)
            == lock["exclusions"]["spent_manifest_sha256"][name]
            == EXPECTED_SPENT_HASHES[name]
        )
        checks[f"{name}_disjoint"] = not collisions[name]

    expected_channels = [
        "A.current_loss","A.prior_mean_loss",
        "B.current_loss","B.prior_mean_loss",
        "C.current_loss","C.prior_mean_loss",
    ]
    checks["response_contract_exact"] = (
        lock["response_contract"]["direct_channels"] == expected_channels
        and lock["response_contract"]["exact_response_vector"]
        == ["L_current_end", "L_prior_mean_end"]
        and lock["response_contract"]["same_terminal_state_required"] is True
        and lock["response_contract"]["current_curve_point_exact_required"] is True
        and lock["response_contract"]["accuracy_sentinel"]["gating"] is False
        and lock["response_contract"]["contrasts"]["gating"] is False
    )

    checks["population_exact"] = (
        lock["population"]["seeds"] == 72
        and lock["population"]["expected_boundaries"] == 216
        and lock["population"]["expected_policy_response_vectors"] == 648
        and lock["population"]["expected_primary_loss_scalars"] == 1296
        and lock["population"]["expected_per_stage"]
        == {"1":72,"2":72,"3":72}
    )

    checks["geometry_gate_exact"] = (
        lock["geometry_gate"]["cell"]["unique_count_min"] == 10
        and lock["geometry_gate"]["cell"]["robust_span_definition"] == "p90-p10"
        and lock["geometry_gate"]["cell"]["robust_span_min"] == 0.02
        and lock["geometry_gate"]["channel"]["qualified_stage_count_min"] == 2
        and lock["geometry_gate"]["channel"]["total_stages"] == 3
        and lock["geometry_gate"]["pass_rule"] == "ALL_6_DIRECT_CHANNELS_QUALIFIED"
        and lock["geometry_gate"]["pooled_across_stage_qualification_allowed"] is False
    )

    checks["reliability_exact"] = (
        lock["reliability"]["repeat_seed_count"] == 6
        and tuple(lock["reliability"]["repeat_seeds"]) == fresh[:6]
        and lock["reliability"]["exact_required"] is True
        and float(lock["reliability"]["max_abs_diff_required"]) == 0.0
    )

    checks["adjudication_exact"] = (
        lock["adjudication"]["one_shot"] is True
        and lock["adjudication"]["pre_adjudication_geometry_inspection_allowed"] is False
        and lock["adjudication"]["allowed_verdicts"] == [
            "PASS_LOSS_RESPONSE_SUPPORT",
            "NEGATIVE_LOSS_RESPONSE_GEOMETRY",
            "STOP_INTEGRITY_OR_SUPPORT",
        ]
        and lock["adjudication"]["pass_verdict"] == "PASS_LOSS_RESPONSE_SUPPORT"
    )

    retry = lock["technical_retry_policy"]
    checks["retry_policy_exact"] = (
        retry["collection_retry_only_before_complete_valid_collection"] is True
        and retry["same_seed_same_lock"] is True
        and retry["seed_substitution"] is False
        and retry["extra_seeds"] is False
        and retry["difficulty_change"] is False
        and retry["source_or_gate_change"] is False
        and retry["outcome_inspection_before_retry"] is False
        and retry["complete_valid_collection_must_not_be_rerun"] is True
        and retry["adjudication_exactly_one_valid_run"] is True
        and retry["adjudication_retry_only_if_no_valid_formal_result"] is True
        and retry["source_protocol_seed_runtime_or_gate_change_invalidates_lock"] is True
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

    preflight_text = PREFLIGHT_QA.read_text(encoding="utf-8")
    checks["preflight_closure_exact"] = (
        "CLRM1_ZERO_SCIENCE_PREFLIGHT_PASS" in preflight_text
        and EXPECTED_LOCK_SHA256 in preflight_text
        and EXPECTED_PREFLIGHT_JSON_SHA256 in preflight_text
        and "72 fresh Role-S seeds          NOT RUN" in preflight_text
    )

    collection = ROOT / lock["outputs"]["collection"]
    formal = ROOT / lock["outputs"]["formal_result"]
    workflow_hits = execution_workflows()
    verification_doc = ROOT / "docs/research/continual-loss-response/CLRM1_EXECUTION_LOCK_VERIFICATION.md"

    checks["fresh_collection_absent"] = not collection.exists()
    checks["formal_result_absent"] = not formal.exists()
    checks["fresh_execution_workflow_absent"] = not workflow_hits
    checks["verification_doc_absent_during_verification"] = not verification_doc.exists()

    checks["downstream_closed"] = (
        lock["downstream"]["on_pass"] == "CLRM-2 DESIGN ONLY"
        and lock["downstream"]["predictor_training_authorized"] is False
        and lock["downstream"]["controller_closed"] is True
        and lock["downstream"]["kcl7_closed"] is True
    )

    safety = static_safety()
    checks["verifier_independent"] = all(safety.values())

    ok = all(checks.values())
    return {
        "schema": "CLRM1-EXECUTION-LOCK-VERIFICATION-v1",
        "program": "CLRM-1",
        "status": "PASS" if ok else "FAIL",
        "verdict": (
            "CLRM1_EXECUTION_LOCK_VERIFICATION_PASS"
            if ok else
            "CLRM1_EXECUTION_LOCK_VERIFICATION_FAIL"
        ),
        "head_commit": git("rev-parse", "HEAD"),
        "lock_sha256": sha256_file(LOCK),
        "checks": checks,
        "collisions": collisions,
        "execution_workflow_hits": workflow_hits,
        "static_safety": safety,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "response_geometry_inspected": False,
        "predictor_fitting_performed": False,
        "difficulty_mutation_performed": False,
        "controller_execution_performed": False,
    }


def main() -> int:
    out = ROOT / "artifacts/clrm1_execution_lock_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
