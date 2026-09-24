"""Independent static verifier for the frozen MSA-1 execution lock.

This verifier intentionally does not import or call the MSA-1 scientific
runner. It verifies files, hashes, frozen constants, runtime identity,
collision exclusions, and absence of any fresh execution path/result.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import platform
import re
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "docs/research/measurement-substrate-adequacy/MSA1_EXECUTION_LOCK.json"
PROTOCOL = ROOT / "docs/research/measurement-substrate-adequacy/msa1-endpoint-adequacy-protocol.md"
RUNNER = ROOT / "experiments/msa/msa1_endpoint_adequacy.py"
TESTS = ROOT / "tests/test_msa1_endpoint_adequacy.py"
PREFLIGHT_WORKFLOW = ROOT / ".github/workflows/msa1-zero-science-preflight.yml"

EXPECTED_LOCK_SHA256 = "c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657"
EXPECTED_IMPLEMENTATION_COMMIT = "3dfb18c3704f4f8e91160b30514687fe7a1fbb00"
EXPECTED_PROTOCOL_BLOB = "b4a68aee9db6a0698f70dbb1e1e4b33fbf7ffc4a"
EXPECTED_RUNNER_BLOB = "55d6686c6c1182b7706f4831cb8f49eec2ec032d"
EXPECTED_TEST_BLOB = "0cd1702ae2ecc64af270aa0e8843df3ea1f75fae"
EXPECTED_PREFLIGHT_WORKFLOW_BLOB = "a72ea5105e6dc306d7f214084b4160463f49f00d"
EXPECTED_SEED_MANIFEST_SHA256 = "e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347"
EXPECTED_SEED_PHRASE = "MindForge|MSA-1|current-substrate-endpoint-adequacy|v1"
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
EXPECTED_PROTECTED = (
    13635,13837,14039,14241,14443,
    14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,
    16665,16867,17069,17271,17473,
)
EXPECTED_ACO = (
    714845,799297,471852,671302,797856,525370,494800,333039,618491,662800,
    265044,434671,501990,723350,393434,774787,806053,890854,613906,707487,
    415555,641958,505262,776960,428051,767077,464825,448672,416287,770416,
    596609,359597,454064,431281,705347,294795,641624,345481,326782,242385,
)
EXPECTED_CPRM = (
    814887,863137,944290,493874,333929,674723,629896,563470,452971,659444,
    563718,222175,332624,957861,506630,735777,693319,612663,330455,271971,
    396729,463395,650240,394015,596743,717212,700981,787278,430901,538687,
    927431,885588,748598,724163,573227,689490,439438,774009,639141,850216,
    427422,235913,355296,574310,665271,791304,909129,757353,834226,280648,
    906973,523942,480884,388898,404202,430651,508646,398464,915507,458769,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(values: list[int] | tuple[int, ...]) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_blob(path: Path) -> str:
    return git("hash-object", str(path.relative_to(ROOT)))


def _safe_numeric_expr(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp):
        value = _safe_numeric_expr(node.operand)
        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.UAdd):
            return +value
    if isinstance(node, ast.BinOp):
        lhs = _safe_numeric_expr(node.left)
        rhs = _safe_numeric_expr(node.right)
        if isinstance(node.op, ast.Add):
            return lhs + rhs
        if isinstance(node.op, ast.Sub):
            return lhs - rhs
        if isinstance(node.op, ast.Mult):
            return lhs * rhs
        if isinstance(node.op, ast.Div):
            return lhs / rhs
        if isinstance(node.op, ast.Mod):
            return lhs % rhs
        if isinstance(node.op, ast.Pow):
            return lhs ** rhs
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "math"
        and node.func.attr == "log"
        and len(node.args) == 1
        and not node.keywords
    ):
        return math.log(float(_safe_numeric_expr(node.args[0])))
    raise ValueError("not a permitted static numeric expression")


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
            continue
        except Exception:
            pass
        try:
            out[target.id] = _safe_numeric_expr(node.value)
        except Exception:
            pass
    return out


def regenerate_seeds(phrase: str, count: int) -> tuple[int, ...]:
    accepted: list[int] = []
    seen: set[int] = set()
    i = 0
    while len(accepted) < count:
        digest = hashlib.sha256(f"{phrase}|{i}".encode("utf-8")).digest()
        candidate = 2_000_000 + (int.from_bytes(digest[:8], "big") % 7_000_000)
        if candidate not in seen:
            accepted.append(candidate)
            seen.add(candidate)
        i += 1
    return tuple(accepted)


def historical_kcl_seed_candidates() -> set[int]:
    out: set[int] = set()
    roots = [
        ROOT / "docs/research/kernel-continual-learning",
        ROOT / "experiments/kernel_cl",
    ]
    root_lineage = ROOT / "Lineage.md"
    paths: list[Path] = [root_lineage] if root_lineage.exists() else []
    for base in roots:
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())

    for path in paths:
        if path.suffix == ".py":
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    names = [
                        t.id for t in node.targets if isinstance(t, ast.Name)
                    ]
                    if not any("SEED" in n.upper() for n in names):
                        continue
                    for sub in ast.walk(node.value):
                        if isinstance(sub, ast.Constant) and isinstance(sub.value, int):
                            out.add(int(sub.value))
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if "seed" not in line.lower():
                    continue
                out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


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
            "experiments/msa/msa1_endpoint_adequacy.py" in text
            and "--phase collect" in text
        ):
            hits.append(str(path.relative_to(ROOT)))
    return sorted(hits)


def verifier_static_safety() -> dict[str, bool]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports_runner = False
    calls_scientific_api = False
    launches_scientific_runner = False
    forbidden_calls = {
        "preflight",
        "collect_fresh",
        "adjudicate_records",
        "build_endpoint_records",
        "run_endpoint_counterfactual",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports_runner = imports_runner or any(
                alias.name.startswith("experiments.msa") for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            imports_runner = imports_runner or (
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
            if name in forbidden_calls:
                calls_scientific_api = True
            if name in {"run", "call", "check_call", "check_output", "Popen"}:
                literals = [
                    x.value for x in ast.walk(node)
                    if isinstance(x, ast.Constant) and isinstance(x.value, str)
                ]
                if (
                    any("msa1_endpoint_adequacy.py" in s for s in literals)
                    and any("python" in s.lower() for s in literals)
                ):
                    launches_scientific_runner = True
    return {
        "does_not_import_runner": not imports_runner,
        "does_not_call_scientific_api": not calls_scientific_api,
        "does_not_launch_scientific_runner": not launches_scientific_runner,
    }


def verify() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    assigns = literal_assignments(RUNNER)
    fresh = tuple(int(x) for x in lock["seed_manifest"]["seeds"])
    regenerated = regenerate_seeds(EXPECTED_SEED_PHRASE, 72)
    historical = historical_kcl_seed_candidates()
    protected = set(EXPECTED_PROTECTED)
    aco = set(EXPECTED_ACO)
    cprm = set(EXPECTED_CPRM)

    checks: dict[str, bool] = {}

    checks["lock_hash_exact"] = sha256_file(LOCK) == EXPECTED_LOCK_SHA256
    checks["lock_schema_exact"] = lock.get("schema") == "MSA1-EXECUTION-LOCK-v1"
    checks["program_exact"] = lock.get("program") == "MSA-1"
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
    checks["substrate_identity_unchanged"] = (
        lock["substrate"]["identity"] == "UNCHANGED_CANONICAL_KCL_COMPATIBLE_SUBSTRATE"
        and lock["substrate"]["difficulty_mutation_allowed"] is False
        and lock["substrate"]["endpoint_step"] == 250
        and lock["substrate"]["task_order"] == [
            "T1_U1_A","T2_U1_B","T3_U3_A","T4_U3_B"
        ]
        and lock["substrate"]["policies"] == [
            "A_CARRY_ALL","B_RESET_ALL","C_CARRY_STEP_RESET_MOMENTS"
        ]
    )

    checks["seed_count_unique_exact"] = len(fresh) == 72 and len(set(fresh)) == 72
    checks["seed_manifest_hash_exact"] = (
        manifest_hash(fresh)
        == lock["seed_manifest"]["sha256"]
        == EXPECTED_SEED_MANIFEST_SHA256
    )
    checks["seed_generation_phrase_exact"] = (
        lock["seed_manifest"]["generation_phrase"] == EXPECTED_SEED_PHRASE
    )
    checks["seed_generation_reproducible"] = fresh == regenerated
    checks["runner_seed_tuple_exact"] = tuple(assigns.get("FRESH_SEEDS", ())) == fresh
    checks["runner_seed_hash_exact"] = (
        assigns.get("SEED_MANIFEST_SHA256") == EXPECTED_SEED_MANIFEST_SHA256
    )

    checks["historical_kcl_disjoint"] = set(fresh).isdisjoint(historical)
    checks["protected_kcl_disjoint"] = set(fresh).isdisjoint(protected)
    checks["aco_spent_disjoint"] = set(fresh).isdisjoint(aco)
    checks["cprm_spent_disjoint"] = set(fresh).isdisjoint(cprm)
    checks["protected_lock_exact"] = tuple(lock["excluded_evidence"]["protected_kcl"]) == EXPECTED_PROTECTED
    checks["aco_manifest_hash_exact"] = (
        manifest_hash(EXPECTED_ACO)
        == lock["excluded_evidence"]["spent_aco_manifest_sha256"]
        == "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91"
    )
    checks["cprm_manifest_hash_exact"] = (
        manifest_hash(EXPECTED_CPRM)
        == lock["excluded_evidence"]["spent_cprm_manifest_sha256"]
        == "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3"
    )

    runtime = lock["runtime"]
    checks["runtime_exact"] = (
        runtime["platform"] == "GitHub-hosted ubuntu-24.04"
        and platform.machine() == runtime["architecture"] == "x86_64"
        and platform.python_version() == runtime["python"] == "3.12.14"
        and version("pip") == runtime["pip"] == "26.2.1"
        and version("numpy") == runtime["numpy"] == "2.3.3"
        and version("pytest") == runtime["pytest"] == "8.4.2"
        and torch.__version__ == runtime["torch"] == "2.10.0+cpu"
        and runtime["device"] == "CPU"
        and runtime["deterministic_algorithms"] is True
        and runtime["torch_num_threads"] == 1
    )

    gates = lock["gates"]
    checks["accuracy_gates_exact"] = (
        gates["accuracy"] == {
            "natural_resolution": "1/24",
            "saturated_cell": {
                "ceiling_fraction_min": 0.5,
                "p10_min": "23/24",
            },
            "informative_cell": {
                "unique_count_min": 4,
                "robust_span_min": "2/24",
            },
            "global_rule": "same state for >=2 of 3 policies at each of all 3 stages",
        }
        and assigns.get("ACCURACY_CEILING_MIN") == 0.50
        and math.isclose(assigns.get("ACCURACY_P10_SAT_MIN"), 23.0/24.0, rel_tol=0, abs_tol=1e-15)
        and assigns.get("ACCURACY_MIN_UNIQUE") == 4
        and math.isclose(assigns.get("ACCURACY_MIN_SPAN"), 2.0/24.0, rel_tol=0, abs_tol=1e-15)
    )
    checks["loss_gates_exact"] = (
        gates["loss"]["mastery_reference"] == "-ln(0.95)"
        and math.isclose(gates["loss"]["mastery_reference_value"], -math.log(0.95), rel_tol=0, abs_tol=1e-15)
        and gates["loss"]["saturated_cell"] == {"p90_max": "-ln(0.95)"}
        and gates["loss"]["informative_cell"] == {
            "unique_count_min": 10,
            "robust_span_min": 0.02,
            "p90_must_exceed_mastery_reference": True,
        }
        and gates["loss"]["global_rule"] == "same state for >=2 of 3 policies at each of all 3 stages"
        and math.isclose(assigns.get("LOSS_MASTERY_95"), -math.log(0.95), rel_tol=0, abs_tol=1e-15)
        and assigns.get("LOSS_MIN_UNIQUE") == 10
        and assigns.get("LOSS_MIN_SPAN") == 0.02
    )

    expected_matrix = {
        "ACCURACY_INFORMATIVE+LOSS_INFORMATIVE": "ENDPOINT_MEASUREMENT_ADEQUATE",
        "ACCURACY_SATURATED+LOSS_INFORMATIVE": "ACCURACY_COARSE_LOSS_INFORMATIVE",
        "ACCURACY_SATURATED+LOSS_SATURATED": "CURRENT_SUBSTRATE_ENDPOINT_SATURATED",
        "ANY_OTHER_COMPLETE_PATTERN": "STOP_INTEGRITY_OR_SUPPORT",
    }
    checks["classification_matrix_exact"] = (
        gates["classifications"] == expected_matrix
        and lock["adjudication"]["allowed_verdicts"] == [
            "ENDPOINT_MEASUREMENT_ADEQUATE",
            "ACCURACY_COARSE_LOSS_INFORMATIVE",
            "CURRENT_SUBSTRATE_ENDPOINT_SATURATED",
            "STOP_INTEGRITY_OR_SUPPORT",
        ]
        and lock["adjudication"]["one_shot"] is True
        and lock["adjudication"]["no_intermediate_endpoint_classification_inspection"] is True
    )

    retry = lock["technical_retry_policy"]
    checks["retry_policy_exact"] = (
        retry == {
            "collection_retry_only_before_complete_valid_collection": True,
            "same_seed_same_lock": True,
            "seed_substitution": False,
            "difficulty_change": False,
            "outcome_inspection_before_retry": False,
            "complete_valid_collection_must_not_be_rerun": True,
            "adjudication_exactly_one_valid_run": True,
            "adjudication_retry_only_if_no_valid_formal_result": True,
            "source_protocol_seed_runtime_or_gate_change_invalidates_lock": True,
        }
    )

    collection = ROOT / lock["outputs"]["collection"]
    formal = ROOT / lock["outputs"]["formal_result"]
    workflow_hits = execution_workflows()
    checks["fresh_collection_absent"] = not collection.exists()
    checks["formal_result_absent"] = not formal.exists()
    checks["fresh_execution_workflow_absent"] = not workflow_hits

    safety = verifier_static_safety()
    checks["verifier_independent"] = all(safety.values())

    msa_sources = list((ROOT / "experiments/msa").rglob("*.py"))
    source_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in msa_sources)
    checks["predictor_api_absent"] = all(
        token not in source_text
        for token in ["def fit_model(", "def train_predictor(", "def select_action("]
    )

    checks["downstream_remains_closed"] = (
        lock["downstream"]["msa2_not_automatic"] is True
        and lock["downstream"]["formal_post_msa1_transition_review_required"] is True
        and lock["downstream"]["predictor_training_remains_outside_msa"] is True
        and lock["downstream"]["controller_closed"] is True
        and lock["downstream"]["kcl7_closed"] is True
    )

    ok = all(checks.values())
    return {
        "schema": "MSA1-EXECUTION-LOCK-VERIFICATION-v1",
        "program": "MSA-1",
        "status": "PASS" if ok else "FAIL",
        "verdict": (
            "MSA1_EXECUTION_LOCK_VERIFICATION_PASS"
            if ok else
            "MSA1_EXECUTION_LOCK_VERIFICATION_FAIL"
        ),
        "head_commit": git("rev-parse", "HEAD"),
        "lock_sha256": sha256_file(LOCK),
        "checks": checks,
        "collisions": {
            "historical_kcl": sorted(set(fresh) & historical),
            "protected_kcl": sorted(set(fresh) & protected),
            "spent_aco": sorted(set(fresh) & aco),
            "spent_cprm": sorted(set(fresh) & cprm),
        },
        "execution_workflow_hits": workflow_hits,
        "verifier_static_safety": safety,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "difficulty_mutation_performed": False,
        "predictor_fitting_performed": False,
    }


def main() -> int:
    out = ROOT / "artifacts/msa1_execution_lock_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
