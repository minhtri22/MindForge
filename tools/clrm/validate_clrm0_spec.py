"""Static zero-science validator for CLRM-0 specification foundation."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/continual-loss-response"
PARENT = "64138ab9cb09dcb56a387d3b1f500063eff8302d"
BRANCH = "research/continual-loss-response"

REQUIRED = [
    "README.md",
    "ORIGIN.md",
    "EVIDENCE_INHERITANCE.md",
    "RESEARCH_QUESTION.md",
    "RESPONSE_VECTOR_CONTRACT.md",
    "ACCURACY_SENTINEL_CONTRACT.md",
    "ELIGIBLE_POPULATION_CONTRACT.md",
    "BASELINE_CONTRACT.md",
    "PARTITION_CONTRACT.md",
    "QUALIFICATION_GATES.md",
    "FRESHNESS_EXCLUSIONS.md",
    "ROADMAP.md",
    "LINEAGE.md",
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate() -> dict:
    checks = {}

    checks["required_docs"] = all((DOC / x).exists() for x in REQUIRED)
    checks["parent_is_ancestor"] = (
        subprocess.call(
            ["git", "merge-base", "--is-ancestor", PARENT, "HEAD"],
            cwd=ROOT,
        ) == 0
    )

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    checks["branch_exact"] = branch == BRANCH

    origin = (DOC / "ORIGIN.md").read_text(encoding="utf-8")
    target = (DOC / "RESPONSE_VECTOR_CONTRACT.md").read_text(encoding="utf-8")
    sentinel = (DOC / "ACCURACY_SENTINEL_CONTRACT.md").read_text(encoding="utf-8")
    population = (DOC / "ELIGIBLE_POPULATION_CONTRACT.md").read_text(encoding="utf-8")
    baseline = (DOC / "BASELINE_CONTRACT.md").read_text(encoding="utf-8")
    partitions = (DOC / "PARTITION_CONTRACT.md").read_text(encoding="utf-8")
    gates = (DOC / "QUALIFICATION_GATES.md").read_text(encoding="utf-8")
    exclusions = (DOC / "FRESHNESS_EXCLUSIONS.md").read_text(encoding="utf-8")
    roadmap = (DOC / "ROADMAP.md").read_text(encoding="utf-8")

    checks["not_cprm2"] = "not CPRM-2" in origin or "not CPRM-2" in origin.lower()
    checks["exact_two_axis_target"] = all(x in target for x in [
        "L_current_end(X,a)",
        "L_prior_mean_end(X,a)",
        "D_B(X) = R(X,B) - R(X,A)",
        "D_C(X) = R(X,C) - R(X,A)",
        "Direct prediction object has six channels".lower(),
    ]) if False else (
        "L_current_end(X,a)" in target
        and "L_prior_mean_end(X,a)" in target
        and "D_B(X) = R(X,B) - R(X,A)" in target
        and "D_C(X) = R(X,C) - R(X,A)" in target
        and "six channels" in target
    )

    checks["no_cprm_target_reuse"] = all(x not in target for x in [
        "plasticity_auc",
        "final_current_accuracy",
        "prior_task_retention",
        "worst_prior_accuracy",
    ])

    checks["accuracy_sentinel_only"] = all(x in sentinel for x in [
        "are not CLRM predictor targets",
        "do not enter baseline-superiority qualification",
        "do not enter point-calibration qualification",
    ])

    checks["all_boundary_population"] = all(x in population for x in [
        "after T1 → T2",
        "after T2 → T3",
        "after T3 → T4",
        "ALL prospectively eligible matched boundaries",
    ])

    checks["baseline_family_frozen"] = all(x in baseline for x in [
        "B0 — policy-global mean",
        "B1 — policy-by-stage mean",
        "B2 — ridge state-response baseline",
        "1e-6, 1e-4, 1e-2, 1, 100",
    ])

    checks["roles_separated"] = all(x in partitions for x in [
        "Role S",
        "Role D-train",
        "Role D-val",
        "Role R",
        "CLRM-0 generates no fresh manifest",
    ])

    checks["superiority_gate_frozen"] = all(x in gates for x in [
        "relative_gain >= 0.10",
        "upper CI of macro_ratio < 1.0",
        "ratio_j <= 1.05",
    ])

    checks["calibration_gate_frozen"] = all(x in gates for x in [
        "0.80 <= beta_j <= 1.20",
        "abs(alpha_j) / MAE_baseline_j <= 0.10",
    ])

    checks["exclusions_frozen"] = all(x in exclusions for x in [
        "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91",
        "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3",
        "e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347",
        "5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8",
        "CLRM-0 itself creates no fresh seed manifest",
    ])

    checks["finite_roadmap"] = all(x in roadmap for x in [
        "CLRM-0 — Specification Foundation",
        "CLRM-1 — Loss Response Support Qualification",
        "CLRM-2 — Predictive Discovery",
        "CLRM-3 — Independent Fresh Replication",
        "CLRM-4 — Downstream Decision Governance",
        "controller            = CLOSED",
    ])

    checks["no_scientific_runner"] = not (ROOT / "experiments/clrm").exists()
    checks["no_clrm_results"] = not (ROOT / "experiments/clrm/results").exists()

    files = [p for p in ROOT.rglob("*") if p.is_file()]
    new_manifest_hits = [
        str(p.relative_to(ROOT))
        for p in files
        if "clrm" in str(p).lower()
        and "seed" in p.name.lower()
        and "manifest" in p.name.lower()
    ]
    checks["no_fresh_seed_manifest"] = not new_manifest_hits

    clrm_text = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in DOC.rglob("*.md")
    )
    checks["predictor_not_authorized"] = "Predictor fitting: **NOT AUTHORIZED**" in clrm_text
    checks["controller_closed"] = "controller            = CLOSED" in roadmap
    checks["kcl7_closed"] = "KCL-7                 = CLOSED" in roadmap

    ok = all(checks.values())
    return {
        "schema": "CLRM0-SPEC-QA-v1",
        "program": "CLRM-0",
        "status": "PASS" if ok else "FAIL",
        "verdict": "CLRM0_ZERO_SCIENCE_SPEC_QA_PASS" if ok else "CLRM0_ZERO_SCIENCE_SPEC_QA_FAIL",
        "git_commit": git("rev-parse", "HEAD"),
        "branch": branch,
        "parent_closure": PARENT,
        "checks": checks,
        "new_manifest_hits": new_manifest_hits,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "predictor_fitting_performed": False,
        "controller_execution_performed": False,
    }


def main() -> int:
    result = validate()
    out = ROOT / "artifacts/clrm0_spec_qa.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
