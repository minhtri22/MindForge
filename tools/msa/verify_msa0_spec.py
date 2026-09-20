"""MSA-0 zero-science specification verifier."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/measurement-substrate-adequacy"
BASE = "c1837438d944c0e11dcb961fa669cfef92bc3c2d"
REQUIRED = [
    "README.md","ORIGIN.md","EVIDENCE_INHERITANCE.md","RESEARCH_QUESTION.md",
    "ENDPOINT_MEASUREMENT_CONTRACT.md","SUBSTRATE_DIFFICULTY_CONTRACT.md",
    "FRESHNESS_EXCLUSIONS.md","FALSIFICATION_GATES.md","ROADMAP.md","LINEAGE.md",
]

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def verify() -> dict:
    checks = {}
    details = {}
    checks["required_docs_exist"] = all((DOC/p).is_file() for p in REQUIRED)
    checks["base_is_ancestor"] = subprocess.call(
        ["git","merge-base","--is-ancestor",BASE,"HEAD"], cwd=ROOT
    ) == 0

    changed=[x for x in git("diff","--name-only",f"{BASE}..HEAD").splitlines() if x]
    details["changed_paths"]=changed
    allowed=(
        "docs/research/measurement-substrate-adequacy/",
        "tools/msa/",
        "tests/test_msa0_spec.py",
        ".github/workflows/msa0-zero-science-spec-qa.yml",
    )
    checks["msa0_scope_only"] = all(any(x==p or x.startswith(p) for p in allowed) for x in changed)

    text={p:(DOC/p).read_text(encoding="utf-8") for p in REQUIRED}
    corpus="\n".join(text.values())
    checks["not_cprm_rescue"] = "not CPRM-2" in corpus and "not predictor rescue" in corpus
    checks["terminal_accuracy_mandatory"] = (
        "terminal accuracy" in text["ENDPOINT_MEASUREMENT_CONTRACT.md"]
        and "MANDATORY SENTINEL" in text["ENDPOINT_MEASUREMENT_CONTRACT.md"]
    )
    checks["terminal_loss_mandatory"] = (
        "terminal cross-entropy loss" in text["ENDPOINT_MEASUREMENT_CONTRACT.md"]
        and "MANDATORY CO-MEASUREMENT" in text["ENDPOINT_MEASUREMENT_CONTRACT.md"]
    )
    checks["pre_cprm_loss_provenance"] = (
        "KCL-1" in text["EVIDENCE_INHERITANCE.md"]
        and "cross-entropy loss" in text["EVIDENCE_INHERITANCE.md"]
        and "before ACO/CPRM" in text["EVIDENCE_INHERITANCE.md"]
    )
    checks["msa1_unchanged"] = (
        "MSA-1 must use the current canonical KCL-compatible substrate **unchanged**"
        in text["SUBSTRATE_DIFFICULTY_CONTRACT.md"]
    )
    checks["difficulty_mutation_forbidden"] = all(
        x in text["SUBSTRATE_DIFFICULTY_CONTRACT.md"]
        for x in ["reducing or increasing training steps","changing batch size",
                  "changing model capacity","inventing new task mappings"]
    )
    checks["saturation_valid"] = (
        "CURRENT_SUBSTRATE_ENDPOINT_SATURATED" in corpus
        and "valid conclusion" in text["SUBSTRATE_DIFFICULTY_CONTRACT.md"]
    )
    checks["adaptive_difficulty_forbidden"] = (
        "Prohibited adaptive difficulty search" in text["SUBSTRATE_DIFFICULTY_CONTRACT.md"]
    )
    checks["protected_kcl_recorded"] = all(str(s) in text["FRESHNESS_EXCLUSIONS.md"] for s in [13635,17473])
    checks["aco_spent_recorded"] = "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91" in text["FRESHNESS_EXCLUSIONS.md"]
    checks["cprm_spent_recorded"] = "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3" in text["FRESHNESS_EXCLUSIONS.md"]
    checks["finite_roadmap"] = all(f"MSA-{i}" in text["ROADMAP.md"] for i in range(5))
    checks["predictor_outside_msa"] = "Predictor fitting remains outside MSA" in text["ROADMAP.md"]
    checks["append_only_lineage"] = "APPEND-ONLY" in text["LINEAGE.md"]

    scientific=[]
    for root in [ROOT/"experiments",ROOT/"artifacts"]:
        if root.exists():
            scientific.extend(str(p.relative_to(ROOT)) for p in root.rglob("*")
                              if p.is_file() and "msa" in str(p).lower())
    details["msa_scientific_paths"]=scientific
    checks["no_msa_scientific_artifacts_or_runners"] = not scientific

    seed_manifests=[str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                    if p.is_file() and "measurement-substrate-adequacy" in str(p)
                    and "seed_manifest" in p.name.lower()]
    details["fresh_seed_manifest_paths"]=seed_manifests
    checks["no_fresh_msa_seed_manifest"] = not seed_manifests

    wf_hits=[]
    wfdir=ROOT/".github/workflows"
    if wfdir.exists():
        for p in wfdir.glob("*"):
            if not p.is_file():
                continue
            s=p.read_text(encoding="utf-8",errors="replace").lower()
            if p.name!="msa0-zero-science-spec-qa.yml" and "experiments/msa" in s:
                wf_hits.append(str(p.relative_to(ROOT)))
    details["msa_execution_workflow_hits"]=wf_hits
    checks["no_msa_execution_workflow"] = not wf_hits

    ok=all(checks.values())
    return {
        "schema":"MSA0-SPEC-QA-v1","program":"MSA","phase":"MSA-0",
        "status":"PASS" if ok else "FAIL",
        "verdict":"MSA0_ZERO_SCIENCE_SPEC_QA_PASS" if ok else "MSA0_ZERO_SCIENCE_SPEC_QA_FAIL",
        "base_commit":BASE,"head_commit":git("rev-parse","HEAD"),
        "checks":checks,"details":details,
        "scientific_execution_attempted":False,
        "fresh_scientific_seed_generated":False,
        "difficulty_mutation_performed":False,
        "predictor_fitting_performed":False,
    }

def main() -> int:
    out=ROOT/"artifacts/msa0_spec_qa.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    result=verify()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["status"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
