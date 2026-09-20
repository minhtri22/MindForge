"""CPRM-0 zero-science specification verifier.

This verifier checks governance/specification consistency only.
It MUST NOT import or execute scientific experiment runners.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/continual-policy-response"
BASE = "0700601f9196d3c5989fa8eb5169f28b1bb01799"
REQUIRED = [
    "README.md",
    "ORIGIN.md",
    "EVIDENCE_INHERITANCE.md",
    "PRIMARY_TARGET_CONTRACT.md",
    "ELIGIBLE_POPULATION_CONTRACT.md",
    "BASELINE_CONTRACT.md",
    "FALSIFICATION_GATES.md",
    "ROADMAP.md",
    "LINEAGE.md",
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def verify() -> dict:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    checks["required_docs_exist"] = all((DOC / x).is_file() for x in REQUIRED)
    checks["base_is_ancestor"] = subprocess.call(
        ["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT
    ) == 0

    changed = [x for x in git("diff", "--name-only", f"{BASE}..HEAD").splitlines() if x]
    details["changed_paths"] = changed
    allowed_prefixes = (
        "docs/research/continual-policy-response/",
        "tools/cprm/",
        "tests/test_cprm0_spec.py",
        ".github/workflows/cprm0-zero-science-spec-qa.yml",
    )
    checks["scope_only_cprm0"] = all(
        any(x == p or x.startswith(p) for p in allowed_prefixes) for x in changed
    )

    text = {x: (DOC / x).read_text(encoding="utf-8") for x in REQUIRED}
    corpus = "\n".join(text.values())

    checks["not_aco2"] = "not ACO-2" in corpus or "không phải ACO-2" in corpus
    checks["continuous_target_frozen"] = all(
        token in text["PRIMARY_TARGET_CONTRACT.md"]
        for token in [
            "plasticity_auc",
            "final_current_accuracy",
            "prior_task_retention",
            "worst_prior_accuracy",
            "C_B(X)",
            "C_C(X)",
        ]
    )
    checks["all_boundary_population"] = (
        "ALL prospectively eligible matched boundaries"
        in text["ELIGIBLE_POPULATION_CONTRACT.md"]
    )
    checks["no_yprr_eligibility"] = (
        "Eligibility must not depend on" in text["ELIGIBLE_POPULATION_CONTRACT.md"]
        and "Y_PRR" in text["ELIGIBLE_POPULATION_CONTRACT.md"]
    )
    checks["seed_grouping"] = "Seed is the grouping unit" in text["ELIGIBLE_POPULATION_CONTRACT.md"]

    checks["mandatory_baselines"] = all(
        token in text["BASELINE_CONTRACT.md"]
        for token in ["B0 — action-global mean", "B1 — action-by-stage mean", "B2 — linear state-response baseline"]
    )
    checks["strongest_baseline_rule"] = "Strongest-baseline rule" in text["BASELINE_CONTRACT.md"]

    checks["aco_spent_manifest_recorded"] = (
        "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91"
        in text["EVIDENCE_INHERITANCE.md"]
    )
    checks["protected_cohort_recorded"] = all(
        str(s) in text["EVIDENCE_INHERITANCE.md"]
        for s in [13635,17473]
    )

    checks["finite_roadmap"] = all(
        f"CPRM-{i}" in text["ROADMAP.md"] for i in range(6)
    )
    checks["controller_gate"] = (
        "earliest point" in text["FALSIFICATION_GATES.md"]
        and "adaptive controller" in text["FALSIFICATION_GATES.md"]
    )
    checks["no_rescue_ladder"] = "No rescue ladder" in text["BASELINE_CONTRACT.md"]

    science_paths = []
    for root in [ROOT / "experiments", ROOT / "artifacts"]:
        if root.exists():
            for p in root.rglob("*"):
                if p.is_file() and "cprm" in str(p).lower():
                    science_paths.append(str(p.relative_to(ROOT)))
    checks["no_cprm_scientific_artifacts"] = not science_paths
    details["cprm_scientific_artifacts"] = science_paths

    workflow_hits = []
    wfdir = ROOT / ".github/workflows"
    if wfdir.exists():
        for p in wfdir.glob("*"):
            if not p.is_file():
                continue
            s = p.read_text(encoding="utf-8", errors="replace").lower()
            if "cprm" in s and any(k in s for k in ["--phase collect", "train", "fit model", "fresh seed"]):
                if p.name != "cprm0-zero-science-spec-qa.yml":
                    workflow_hits.append(str(p.relative_to(ROOT)))
    checks["no_cprm_execution_workflow"] = not workflow_hits
    details["cprm_execution_workflow_hits"] = workflow_hits

    checks["lineage_append_only_declared"] = "APPEND-ONLY" in text["LINEAGE.md"]
    checks["zero_science_declared"] = (
        "Scientific execution: **NONE**" in text["LINEAGE.md"]
        and "Fresh CPRM scientific seeds consumed: **NONE**" in text["LINEAGE.md"]
        and "Model fitting: **NONE**" in text["LINEAGE.md"]
    )

    ok = all(checks.values())
    return {
        "schema": "CPRM0-SPEC-QA-v1",
        "phase": "CPRM-0",
        "status": "PASS" if ok else "FAIL",
        "verdict": "CPRM0_ZERO_SCIENCE_SPEC_QA_PASS" if ok else "CPRM0_ZERO_SCIENCE_SPEC_QA_FAIL",
        "head_commit": git("rev-parse", "HEAD"),
        "base_commit": BASE,
        "checks": checks,
        "details": details,
        "scientific_execution_attempted": False,
        "fresh_scientific_seed_consumed": False,
        "model_fitting_performed": False,
    }


def main() -> int:
    out = ROOT / "artifacts/cprm0_spec_qa.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
