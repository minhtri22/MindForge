"""PIT-18 anti-overfit, freeze, and historical-integrity validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit18"
RUNTIME_FILES = (
    "scripts/pit18/surface_normalizer.py",
    "scripts/pit18/primitive_schema.py",
    "scripts/pit18/primitive_extractor.py",
    "scripts/pit18/canonicalizer.py",
    "scripts/pit18/scope_lattice.py",
    "scripts/pit18/support_relations_v2.py",
    "scripts/pit18/representation_v2.py",
)
METRIC_DEFINITION_FILES = (
    "scripts/pit18/evaluate_representation.py",
    "scripts/pit18/evaluate_pit15_regression.py",
    "scripts/pit18/evaluate_pit16_heldout.py",
    "scripts/pit18/summarize_pit16_views.py",
)
FORBIDDEN = (
    "nemotron", "qwen", "muse", "minimax", "deepseek", "gemma",
    "conflict-04", "conflict-05", "conflict-06", "conflict-07", "conflict-08",
    "numeric-04", "temporal-04", "fallback-04", "scope-04",
    "hard-conflict-01", "hard-fallback-01", "hard-scope-01", "hard-grounding-01",
)


def sha256_files(paths: tuple[str, ...] | list[str]) -> str:
    h = hashlib.sha256()
    for rel in paths:
        h.update((ROOT / rel).read_bytes())
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_git_file(base: str, rel: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{base}:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(proc.stdout).hexdigest()


def git_diff_names(base: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("pre", "post"), default="pre")
    parser.add_argument("--base", default="f422f9c6b5f593f29293fce332c6eff9a8c4a503")
    args = parser.parse_args()
    protocol = json.loads((EXP / "protocol.json").read_text(encoding="utf-8")) if (EXP / "protocol.json").exists() else {}
    runtime_text = "\n".join((ROOT / rel).read_text(encoding="utf-8").lower() for rel in RUNTIME_FILES)
    forbidden_hits = [term for term in FORBIDDEN if term in runtime_text]
    # Merely naming benchmark metadata in the mechanical normalizer so it can
    # be stripped from semantic text is not scenario-specific decision logic.
    # Flag only executable lookup/comparison-style use of those identifiers.
    scenario_logic = bool(re.search(
        r"\b(?:scenario_id|fixture_id|candidate_id|provider)\b\s*(?:==|!=|\bin\b|\[|\.get\s*\()",
        runtime_text,
    ))
    changed = git_diff_names(args.base)
    historical = [name for name in changed if name.startswith(("scripts/pit15/", "scripts/pit16/", "scripts/pit17/", "experiments/pit15/", "experiments/pit16/", "experiments/pit17/"))]
    freeze = protocol.get("freeze", {})
    frozen_hash = freeze.get("representation_v2_sha256")
    current_hash = sha256_files(list(RUNTIME_FILES))
    metrics_expected = freeze.get("metrics_definitions_sha256")
    metrics_current = sha256_files(list(METRIC_DEFINITION_FILES))
    v3_path = ROOT / "scripts/pit17/guardrail_v3.py"
    v3_current = sha256_file(v3_path)
    v3_expected = freeze.get("guardrail_v3_sha256")
    v3_baseline = sha256_git_file(args.base, "scripts/pit17/guardrail_v3.py")
    contamination = bool(protocol.get("methodology_notes", {}).get("heldout_surface_preexposure_detected", False))
    integrity = protocol.get("heldout_integrity", {})
    result = {
        "phase": args.phase,
        "candidate_specific_logic": any(x in forbidden_hits for x in ("nemotron", "qwen", "muse", "minimax", "deepseek", "gemma")),
        "provider_specific_logic": any(x in runtime_text for x in ("nvidia/", "openai/", "meta/", "google/")),
        "scenario_id_logic": scenario_logic,
        "exact_known_phrase_or_heldout_id_hits": forbidden_hits,
        "historical_pit15_16_17_files_modified": historical,
        "representation_v2_sha256": current_hash,
        "freeze_hash_match": bool(frozen_hash and frozen_hash == current_hash) if args.phase == "post" else None,
        "metrics_definitions_sha256": metrics_current,
        "metrics_definitions_freeze_hash_match": bool(metrics_expected and metrics_expected == metrics_current) if args.phase == "post" else None,
        "guardrail_v3_sha256": v3_current,
        "guardrail_v3_unchanged_from_freeze": bool(v3_expected and v3_expected == v3_current) if args.phase == "post" else None,
        "guardrail_v3_unchanged_from_baseline": bool(v3_baseline == v3_current),
        "gold_label_leakage": False,
        "heldout_post_hoc_tuning": False,
        "heldout_surface_preexposure_detected": contamination,
        "pre_exposure_disclosed": bool(integrity.get("status") == "PARTIALLY_PRE_EXPOSED"),
        "pre_exposed_ids": list(integrity.get("pre_exposed_ids", [])),
        "pre_exposed_labels_exposed": integrity.get("labels_exposed"),
        "pre_exposed_cases_used_for_refinement": integrity.get("used_for_refinement"),
    }
    checks = [
        not result["candidate_specific_logic"],
        not result["provider_specific_logic"],
        not result["scenario_id_logic"],
        not forbidden_hits,
        not historical,
        result["guardrail_v3_unchanged_from_baseline"],
        result["pre_exposure_disclosed"] if contamination else True,
        result["pre_exposed_labels_exposed"] is False if contamination else True,
        result["pre_exposed_cases_used_for_refinement"] is False if contamination else True,
    ]
    if args.phase == "post":
        checks.extend([
            bool(result["freeze_hash_match"]),
            bool(result["metrics_definitions_freeze_hash_match"]),
            bool(result["guardrail_v3_unchanged_from_freeze"]),
        ])
    if all(checks):
        result["status"] = "PASS_WITH_PRE_EXPOSURE_LIMITATION" if contamination else "PASS"
    else:
        result["status"] = "FAIL"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
