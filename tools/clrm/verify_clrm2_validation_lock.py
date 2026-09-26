"""Independent static verification of CLRM2-B Validation Lock.

No CLRM-2 scientific runner is imported or executed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import platform
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "docs/research/continual-loss-response/CLRM2_VALIDATION_LOCK.json"
TRAINING_LOCK = ROOT / "docs/research/continual-loss-response/CLRM2_TRAINING_LOCK.json"
PROTOCOL = ROOT / "docs/research/continual-loss-response/clrm2-predictive-discovery-protocol.md"
MANIFEST = ROOT / "docs/research/continual-loss-response/CLRM2_DISCOVERY_SEED_MANIFEST.json"
RUNNER = ROOT / "experiments/clrm/clrm2_predictive_discovery.py"
DTRAIN = ROOT / "experiments/clrm/results/clrm2_dtrain.json"
CANDIDATE = ROOT / "experiments/clrm/results/CLRM2_DISCOVERY_CANDIDATE.json"
PHASE_A_CLOSURE = ROOT / "docs/research/continual-loss-response/CLRM2_PHASE_A_FORMAL_CLOSURE.md"
PHASE_A_WORKFLOW = ROOT / ".github/workflows/clrm2-dtrain-fit.yml"
DVAL = ROOT / "experiments/clrm/results/clrm2_dval.json"
FORMAL = ROOT / "experiments/clrm/results/CLRM2_FORMAL_RESULT.json"

EXPECTED_LOCK_SHA = "bd5845eb350bc5bbe889d0d1e2570d9a97b51c8bc683585c6d344f53ee15abde"
EXPECTED_TRAINING_LOCK_SHA = "e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5"
EXPECTED_PROTOCOL_BLOB = "9c35a9b8648ae2581a9f111680364dc75ffcf8a8"
EXPECTED_MANIFEST_BLOB = "c7600a8963a15b03a1d3c27a4134e0a724088519"
EXPECTED_RUNNER_BLOB = "2b802f0ff10508d573e0c8ae61b6337ef80a1807"
EXPECTED_DTRAIN_SHA = "8e7e38357f2117e76337b454f40debeb7741f1a8f3993a61add9f50c490d1b28"
EXPECTED_DTRAIN_BLOB = "46731fbbf621829d55234c0ad670482c7a09bd51"
EXPECTED_CANDIDATE_SHA = "310bd9805cb028691826722c8cf5ee365e85d549872f2f3e898d8e348cef2a83"
EXPECTED_CANDIDATE_BLOB = "7bf84b2c4c4ddbc84131aaab807d9620a317d40c"
EXPECTED_PHASE_A_CLOSURE_BLOB = "09e2905fc288988ab6baf44c3f43544607ab99c8"
EXPECTED_PHASE_A_WORKFLOW_BLOB = "c53de603d6c1a41f5f8f289864f8f89d52546d6f"
EXPECTED_DVAL_HASH = "a2287c490acf6c8a94cff56be1a5eb4aaa0115fce26675312ac590d5bfe6ee96"

OBS11 = (
    "STAGE_2","STAGE_3","H1_M1_RMS","H2_SQRT_M2_RMS",
    "H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS","H4_TASK_DRIFT_RELATIVE_L2",
    "H5_PRESSURE_TO_DRIFT_RATIO","H6_DRIFT_PRESSURE_COSINE",
    "H7_PRIOR_MEAN_ACCURACY","H8_PRIOR_WORST_ACCURACY","H9_CURRENT_TASK_LOSS",
)
TARGETS = (
    "A.current_loss","A.prior_mean_loss","B.current_loss","B.prior_mean_loss",
    "C.current_loss","C.prior_mean_loss",
)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def blob(path: Path) -> str:
    return git("hash-object", str(path.relative_to(ROOT)))

def assigns(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    return out

def verifier_safety() -> dict[str, bool]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports_runner = False
    scientific_call = False
    runner_launch = False
    forbidden_calls = {
        "preflight","build_discovery_records","candidate_cv","baseline_oof",
        "fit_candidate_package","adjudicate_validation",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports_runner |= any(a.name.startswith("experiments.clrm.clrm2") for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports_runner |= bool(node.module and node.module.startswith("experiments.clrm.clrm2"))
        elif isinstance(node, ast.Call):
            fn = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            scientific_call |= fn in forbidden_calls
            if fn in {"run","call","check_call","check_output","Popen"}:
                literals = [
                    x.value for x in ast.walk(node)
                    if isinstance(x, ast.Constant) and isinstance(x.value, str)
                ]
                runner_launch |= any("clrm2_predictive_discovery.py" in x for x in literals)
    return {
        "no_import_clrm2": not imports_runner,
        "no_scientific_call": not scientific_call,
        "no_runner_launch": not runner_launch,
    }

def verify() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    training_lock = json.loads(TRAINING_LOCK.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    dtrain = json.loads(DTRAIN.read_text(encoding="utf-8"))
    ra = assigns(RUNNER)

    checks: dict[str, bool] = {}
    checks["validation_lock_hash"] = sha(LOCK) == EXPECTED_LOCK_SHA
    checks["training_lock_hash"] = sha(TRAINING_LOCK) == EXPECTED_TRAINING_LOCK_SHA
    checks["protocol_blob"] = blob(PROTOCOL) == EXPECTED_PROTOCOL_BLOB == lock["protocol"]["git_blob_sha"]
    checks["manifest_blob"] = blob(MANIFEST) == EXPECTED_MANIFEST_BLOB == lock["dval_manifest"]["manifest_git_blob_sha"]
    checks["runner_blob"] = blob(RUNNER) == EXPECTED_RUNNER_BLOB == lock["scientific_source"]["git_blob_sha"]
    checks["dtrain_exact"] = (
        sha(DTRAIN) == EXPECTED_DTRAIN_SHA == lock["dtrain_evidence"]["sha256"]
        and blob(DTRAIN) == EXPECTED_DTRAIN_BLOB == lock["dtrain_evidence"]["git_blob_sha"]
    )
    checks["candidate_exact"] = (
        sha(CANDIDATE) == EXPECTED_CANDIDATE_SHA == lock["candidate_package"]["sha256"]
        and blob(CANDIDATE) == EXPECTED_CANDIDATE_BLOB == lock["candidate_package"]["git_blob_sha"]
    )
    checks["phase_a_closure_exact"] = (
        blob(PHASE_A_CLOSURE) == EXPECTED_PHASE_A_CLOSURE_BLOB
        == lock["parent"]["phase_a_closure_git_blob"]
    )
    checks["phase_a_workflow_retired_exact"] = (
        blob(PHASE_A_WORKFLOW) == EXPECTED_PHASE_A_WORKFLOW_BLOB
        == lock["parent"]["phase_a_workflow_retired_git_blob"]
    )

    phase_a_wf = PHASE_A_WORKFLOW.read_text(encoding="utf-8")
    checks["phase_a_hard_disabled"] = (
        "(RETIRED)" in phase_a_wf
        and "if: ${{ false }}" in phase_a_wf
        and "push:" not in phase_a_wf
    )

    checks["lock_identity"] = (
        lock["schema"] == "CLRM2-VALIDATION-LOCK-v1"
        and lock["program"] == "CLRM-2"
        and lock["phase"] == "B_SEALED_DVAL_ONLY"
    )
    checks["candidate_contract"] = (
        candidate["schema"] == "CLRM2-DISCOVERY-CANDIDATE-v1"
        and candidate["candidate_family"] == "RBF-KRR-v1"
        and candidate["representation"] == "OBS11-v1"
        and tuple(candidate["feature_names"]) == OBS11
        and tuple(candidate["target_names"]) == TARGETS
        and float(candidate["candidate"]["gamma"]) == 0.02
        and float(candidate["candidate"]["lambda"]) == 1.0
        and candidate["baseline_selection"]["strongest_baseline"] == "B2"
        and [float(x) for x in candidate["baseline_selection"]["b2_lambdas"]]
            == [100.0,0.01,100.0,1.0,100.0,1.0]
        and candidate["dval_used"] is False
    )
    checks["lock_candidate_matches"] = (
        lock["candidate_package"]["family"] == "RBF-KRR-v1"
        and lock["candidate_package"]["representation"] == "OBS11-v1"
        and float(lock["candidate_package"]["selected_gamma"]) == 0.02
        and float(lock["candidate_package"]["selected_lambda"]) == 1.0
        and lock["candidate_package"]["strongest_baseline"] == "B2"
        and [float(x) for x in lock["candidate_package"]["b2_lambdas"]]
            == [100.0,0.01,100.0,1.0,100.0,1.0]
        and lock["candidate_package"]["dval_used"] is False
        and lock["candidate_package"]["refit_on_dval_allowed"] is False
        and lock["candidate_package"]["recalibration_allowed"] is False
    )

    checks["dtrain_spent"] = (
        dtrain["schema"] == "CLRM2-DTRAIN-v1"
        and dtrain["seed_sha256"] == "bc7f7dd941a5ec280156e9cbfc3f1501565213db7efa3b940dd4d189891b93e8"
        and len(dtrain["records"]) == 480
        and lock["dtrain_evidence"]["spent"] is True
        and lock["dtrain_evidence"]["rerun_allowed"] is False
    )
    checks["dval_manifest_exact"] = (
        len(manifest["dval"]["seeds"]) == 80
        and manifest["dval"]["sha256"] == EXPECTED_DVAL_HASH
        and lock["dval_manifest"]["seed_sha256"] == EXPECTED_DVAL_HASH
        and lock["dval_manifest"]["seed_count"] == 80
        and lock["dval_manifest"]["expected_boundaries"] == 240
        and lock["dval_manifest"]["sealed"] is True
    )
    checks["obs11_exact"] = tuple(ra["OBS11"]) == OBS11 and lock["representation"]["exact_order"] == list(OBS11)
    checks["targets_exact"] = tuple(ra["TARGETS"]) == TARGETS and lock["target_contract"]["exact_six_channels"] == list(TARGETS)
    checks["bootstrap_exact"] = int(ra["BOOTSTRAP_RESAMPLES"]) == 20000 and int(ra["BOOTSTRAP_SEED"]) == 72002
    checks["gate2_exact"] = (
        lock["gate2"]["strongest_baseline"] == "B2"
        and float(lock["gate2"]["relative_gain_min"]) == 0.10
        and int(lock["gate2"]["whole_seed_bootstrap_resamples"]) == 20000
        and int(lock["gate2"]["bootstrap_seed"]) == 72002
        and float(lock["gate2"]["macro_ratio_ci_upper_must_be_below"]) == 1.0
        and float(lock["gate2"]["every_channel_ratio_max"]) == 1.05
        and float(lock["gate2"]["calibration_beta_min"]) == 0.80
        and float(lock["gate2"]["calibration_beta_max"]) == 1.20
        and float(lock["gate2"]["calibration_abs_alpha_over_baseline_mae_max"]) == 0.10
        and lock["gate2"]["no_recalibration"] is True
        and lock["gate2"]["one_shot_adjudication"] is True
    )
    checks["training_lock_transition_preserved"] = (
        training_lock["validation_transition"]["requires_separate_validation_lock"] is True
        and training_lock["validation_transition"]["requires_independent_validation_lock_verification"] is True
        and training_lock["validation_transition"]["dval_execution_before_both"] is False
    )

    rt = lock["runtime"]
    checks["runtime"] = (
        platform.machine() == rt["architecture"] == "x86_64"
        and platform.python_version() == rt["python"] == "3.12.14"
        and version("pip") == rt["pip"] == "26.2.1"
        and version("numpy") == rt["numpy"] == "2.3.3"
        and version("pytest") == rt["pytest"] == "8.4.2"
        and torch.__version__ == rt["torch"] == "2.10.0+cpu"
    )

    checks["dval_absent"] = not DVAL.exists()
    checks["formal_absent"] = not FORMAL.exists()
    safety = verifier_safety()
    checks["verifier_independent"] = all(safety.values())

    ok = all(checks.values())
    return {
        "schema":"CLRM2-VALIDATION-LOCK-VERIFICATION-v1",
        "program":"CLRM-2",
        "phase":"B_SEALED_DVAL_ONLY",
        "status":"PASS" if ok else "FAIL",
        "verdict":"CLRM2_VALIDATION_LOCK_VERIFICATION_PASS" if ok else "CLRM2_VALIDATION_LOCK_VERIFICATION_FAIL",
        "head_commit":git("rev-parse","HEAD"),
        "validation_lock_sha256":sha(LOCK),
        "candidate_package_sha256":sha(CANDIDATE),
        "dtrain_sha256":sha(DTRAIN),
        "checks":checks,
        "static_safety":safety,
        "dval_outcomes_generated":False,
        "gate2_called":False,
        "scientific_outcome_generated":False,
    }

def main() -> int:
    out = ROOT / "artifacts/clrm2_validation_lock_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
