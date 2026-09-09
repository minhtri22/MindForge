"""H2 paired OOD transfer closure over frozen EXP-LRN-001 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).parent.parent
EXP_ROOT = ROOT / "experiments/OIR_PPV/H2_Closure/EXP-H2-001"
ARTIFACT_ROOT = ROOT / "artifacts/h2_closure/EXP-H2-001"
REFERENCE_MANIFEST = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json"
REFERENCE_ROOT = ROOT / "artifacts/learner_benchmark/EXP-LRN-001/full"
H1_RAW_ROOT = ROOT / "artifacts/h1_closure/EXP-H1-001/full"
H1_FREEZE = ROOT / "experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_protocol_freeze.json"
M3_PROTOCOL = ROOT / "benchmark/M3_PROTOCOL.md"
FREEZE_PATH = EXP_ROOT / "h2_protocol_freeze.json"
FREEZE_HASH_PATH = EXP_ROOT / "h2_protocol_freeze.sha256"
MANIFEST_PATH = EXP_ROOT / "matrix_manifest.json"
MANIFEST_HASH_PATH = EXP_ROOT / "matrix_manifest.sha256"
COMPARISON_PATH = EXP_ROOT / "h2_comparison.json"
REPORT_PATH = EXP_ROOT / "H2_CLOSURE_REPORT.md"

LEARNERS = ["L1", "L2", "L3", "L4"]
BASELINE = "L0"
ELIGIBLE_ENVS = ["ENV-1", "ENV-3", "ENV-4"]
INAPPLICABLE_ENV = "ENV-2"
SEEDS = [42, 123, 456, 789, 1011]
TIE_TOLERANCE = 1e-12
CATASTROPHIC_THRESHOLD = -0.20
BOOTSTRAP_SEED = 20260909
BOOTSTRAP_REPS = 10000
CI_LEVEL = 0.95


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _git_state() -> dict:
    return {
        "branch": _git("branch", "--show-current"),
        "head": _git("rev-parse", "HEAD"),
        "dirty": bool(_git("status", "--porcelain")),
    }


def _reference_manifest() -> dict:
    manifest = _read_json(REFERENCE_MANIFEST)
    if manifest.get("experiment_id") != "EXP-LRN-001" or manifest.get("status") != "frozen":
        raise RuntimeError("Reference learner manifest is not frozen EXP-LRN-001")
    if manifest.get("seeds") != SEEDS:
        raise RuntimeError("Reference learner seed identity mismatch")
    return manifest


def freeze_protocol() -> dict:
    if FREEZE_PATH.exists() or FREEZE_HASH_PATH.exists():
        raise FileExistsError("Refusing to overwrite H2 protocol freeze")
    reference = _reference_manifest()
    h1 = _read_json(H1_FREEZE)
    learner_fidelity = {item["learner_id"]: item["fidelity"] for item in reference["learners"]}
    freeze = {
        "experiment_id": "EXP-H2-001",
        "hypothesis_id": "H2",
        "status": "frozen_before_decisive_analysis",
        "frozen_at": datetime.now().isoformat(),
        "base_protocol": {
            "name": "M3_PROTOCOL",
            "version": "M3-Protocol-v1.0",
            "path": str(M3_PROTOCOL.relative_to(ROOT)),
            "sha256": _sha(M3_PROTOCOL),
        },
        "reference_benchmark": {
            "experiment_id": "EXP-LRN-001",
            "manifest_path": str(REFERENCE_MANIFEST.relative_to(ROOT)),
            "manifest_sha256": _sha(REFERENCE_MANIFEST),
            "artifact_root": str(REFERENCE_ROOT),
        },
        "raw_control": {
            "experiment_id": "EXP-H1-001",
            "protocol_path": str(H1_FREEZE.relative_to(ROOT)),
            "protocol_sha256": _sha(H1_FREEZE),
            "reference_manifest_sha256": h1["reference_benchmark"]["manifest_sha256"],
            "artifact_root": str(H1_RAW_ROOT),
        },
        "source": _git_state(),
        "learners": [{"learner_id": learner, "fidelity": learner_fidelity[learner]} for learner in [BASELINE, *LEARNERS]],
        "primary_baseline": BASELINE,
        "secondary_control": "RAW",
        "eligible_environments": ELIGIBLE_ENVS,
        "inapplicable_environment": {
            "environment": INAPPLICABLE_ENV,
            "status": "INAPPLICABLE_FOR_H2_PRIMARY",
            "reason": "Frozen EXP-LRN-001 unseen_environment_score is null for ENV-2; no score may be imputed.",
        },
        "seeds": SEEDS,
        "paired_comparison_unit": "same environment + same seed + learner vs L0",
        "primary_metric": "delta_ood = unseen_environment_score(learner) - unseen_environment_score(L0)",
        "secondary_metrics": [
            "learner/baseline generalization_delta",
            "delta_generalization_delta",
            "unseen_accuracy",
            "unseen_auroc",
            "seen accuracy",
            "seen auroc",
            "delta_ood_vs_raw when split identity is proven compatible",
        ],
        "confidence_interval": {
            "method": "deterministic paired bootstrap percentile CI of mean delta over 15 eligible pairs",
            "level": CI_LEVEL,
            "bootstrap_repetitions": BOOTSTRAP_REPS,
            "rng_seed": BOOTSTRAP_SEED,
        },
        "tie_tolerance": TIE_TOLERANCE,
        "catastrophic_regression_rule": {
            "threshold": CATASTROPHIC_THRESHOLD,
            "rule": "delta_ood < -0.20 absolute score",
            "effect": "any catastrophic regression prevents global SUPPORTED for that learner",
        },
        "failed_inapplicable_policy": "retain every missing/failed/inapplicable cell; no imputation, seed replacement, or silent drop",
        "candidate_classification_rules": {
            "SUPPORTED": "15/15 valid pairs, mean delta > 0, paired CI lower bound > 0, and zero catastrophic regressions",
            "FALSIFIED_UNDER_TESTED_CONDITIONS": "15/15 valid pairs, mean delta < 0, paired CI upper bound < 0, and losses exceed wins",
            "NOT_SUPPORTED": "valid complete evidence that does not satisfy SUPPORTED or FALSIFIED_UNDER_TESTED_CONDITIONS",
            "INCONCLUSIVE": "required comparable evidence is missing/invalid; negative evidence alone is not inconclusive",
            "SUPPORTED_WITH_LIMITS": "not used by this closure unless a subset rule is separately pre-frozen before decisive analysis",
        },
        "artifact_sources": {
            "reference_results": str(REFERENCE_ROOT),
            "raw_results": str(H1_RAW_ROOT),
        },
        "config_hashes": {
            "learners": _json_hash(LEARNERS),
            "environments": _json_hash(ELIGIBLE_ENVS),
            "seeds": _json_hash(SEEDS),
            "statistical_rules": _json_hash({
                "tie": TIE_TOLERANCE,
                "catastrophic": CATASTROPHIC_THRESHOLD,
                "bootstrap_seed": BOOTSTRAP_SEED,
                "bootstrap_reps": BOOTSTRAP_REPS,
                "ci": CI_LEVEL,
            }),
        },
    }
    _write_json(FREEZE_PATH, freeze)
    FREEZE_HASH_PATH.write_text(_sha(FREEZE_PATH), encoding="utf-8")
    return freeze


def _load_freeze() -> dict:
    if not FREEZE_PATH.is_file() or not FREEZE_HASH_PATH.is_file():
        raise RuntimeError("H2 protocol freeze/hash missing")
    expected = FREEZE_HASH_PATH.read_text(encoding="utf-8").strip()
    if expected != _sha(FREEZE_PATH):
        raise RuntimeError("H2 protocol freeze identity mismatch")
    freeze = _read_json(FREEZE_PATH)
    if freeze.get("status") != "frozen_before_decisive_analysis":
        raise RuntimeError("H2 protocol is not frozen")
    return freeze


def freeze_matrix() -> dict:
    freeze = _load_freeze()
    if MANIFEST_PATH.exists() or MANIFEST_HASH_PATH.exists():
        raise FileExistsError("Refusing to overwrite H2 matrix manifest")
    pairs = []
    for learner in LEARNERS:
        for environment in ELIGIBLE_ENVS:
            for seed in SEEDS:
                pairs.append({
                    "pair_id": f"{learner}-vs-{BASELINE}-{environment}-S{seed}",
                    "learner": learner,
                    "baseline": BASELINE,
                    "environment": environment,
                    "seed": seed,
                })
    inapplicable = [
        {
            "pair_id": f"{learner}-vs-{BASELINE}-{INAPPLICABLE_ENV}-S{seed}",
            "learner": learner,
            "baseline": BASELINE,
            "environment": INAPPLICABLE_ENV,
            "seed": seed,
            "status": "INAPPLICABLE_FOR_H2_PRIMARY",
            "reason": freeze["inapplicable_environment"]["reason"],
        }
        for learner in LEARNERS for seed in SEEDS
    ]
    manifest = {
        "experiment_id": "EXP-H2-001",
        "status": "frozen",
        "frozen_at": datetime.now().isoformat(),
        "protocol_freeze_sha256": _sha(FREEZE_PATH),
        "reference_manifest_sha256": _sha(REFERENCE_MANIFEST),
        "primary_pair_count": len(pairs),
        "inapplicable_env2_pair_count": len(inapplicable),
        "pairs": pairs,
        "inapplicable_pairs": inapplicable,
    }
    _write_json(MANIFEST_PATH, manifest)
    MANIFEST_HASH_PATH.write_text(_sha(MANIFEST_PATH), encoding="utf-8")
    return manifest


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file() or not MANIFEST_HASH_PATH.is_file():
        raise RuntimeError("H2 matrix manifest/hash missing")
    if MANIFEST_HASH_PATH.read_text(encoding="utf-8").strip() != _sha(MANIFEST_PATH):
        raise RuntimeError("H2 matrix manifest identity mismatch")
    manifest = _read_json(MANIFEST_PATH)
    if manifest.get("protocol_freeze_sha256") != _sha(FREEZE_PATH):
        raise RuntimeError("H2 manifest/protocol hash mismatch")
    return manifest


def _reference_cell(learner: str, environment: str, seed: int) -> tuple[Path, dict, dict]:
    if learner not in [BASELINE, *LEARNERS]:
        raise ValueError(f"Unknown learner: {learner}")
    if environment not in [*ELIGIBLE_ENVS, INAPPLICABLE_ENV]:
        raise ValueError(f"Unknown environment: {environment}")
    if seed not in SEEDS:
        raise ValueError(f"Unknown seed: {seed}")
    path = REFERENCE_ROOT / f"{learner}-{environment}-S{seed}"
    result_path, provenance_path = path / "results.json", path / "provenance.json"
    if not result_path.is_file() or not provenance_path.is_file():
        raise RuntimeError(f"Missing source cell artifact: {path}")
    result, provenance = _read_json(result_path), _read_json(provenance_path)
    if result.get("environment_family") != environment or provenance.get("seed") != seed:
        raise RuntimeError(f"Source cell identity mismatch: {path}")
    if result.get("protocol", {}).get("sha256") != _load_freeze()["base_protocol"]["sha256"]:
        raise RuntimeError(f"Source protocol hash mismatch: {path}")
    return path, result, provenance


def _raw_cell(environment: str, seed: int, baseline_result: dict) -> tuple[dict | None, dict]:
    path = H1_RAW_ROOT / f"RAW-{environment}-S{seed}"
    rp, pp, cp = path / "results.json", path / "provenance.json", path / "condition_config.json"
    if not (rp.is_file() and pp.is_file() and cp.is_file()):
        return None, {"reason": "RAW source artifact missing", "path": str(path)}
    result, provenance, config = _read_json(rp), _read_json(pp), _read_json(cp)
    freeze = _load_freeze()
    compatible = (
        provenance.get("reference_benchmark", {}).get("manifest_sha256") == freeze["reference_benchmark"]["manifest_sha256"]
        and result.get("environment") == environment
        and result.get("seed") == seed
        and config.get("seed") == seed
        and config.get("environment", {}).get("environment_id") == environment
        and result.get("ood_split") == baseline_result.get("evaluation", {}).get("generalization", {}).get("ood_split")
        and result.get("shift_assertion") == baseline_result.get("shift_assertions")
    )
    if not compatible:
        return None, {"reason": "RAW split/provenance identity not provably equivalent", "path": str(path)}
    return result, {
        "path": str(path),
        "results_sha256": _sha(rp),
        "provenance_sha256": _sha(pp),
        "condition_config_sha256": _sha(cp),
    }


def derive_pairs() -> dict:
    freeze = _load_freeze()
    manifest = _load_manifest()
    if ARTIFACT_ROOT.exists():
        raise FileExistsError(f"Refusing to overwrite H2 derived evidence: {ARTIFACT_ROOT}")
    pairs_root = ARTIFACT_ROOT / "pairs"
    pairs_root.mkdir(parents=True, exist_ok=False)
    git = _git_state()
    complete = failed = 0
    for pair in manifest["pairs"]:
        pair_id = pair["pair_id"]
        out = pairs_root / pair_id
        out.mkdir(parents=True, exist_ok=False)
        try:
            learner_path, learner_result, learner_prov = _reference_cell(pair["learner"], pair["environment"], pair["seed"])
            baseline_path, baseline_result, baseline_prov = _reference_cell(BASELINE, pair["environment"], pair["seed"])
            lg = learner_result["evaluation"]["generalization"]
            bg = baseline_result["evaluation"]["generalization"]
            if lg.get("unseen_environment_score") is None or bg.get("unseen_environment_score") is None:
                raise RuntimeError(f"Missing primary OOD score for eligible pair {pair_id}")
            delta = float(lg["unseen_environment_score"] - bg["unseen_environment_score"])
            raw_result, raw_identity = _raw_cell(pair["environment"], pair["seed"], baseline_result)
            raw_score = None if raw_result is None else raw_result["utility"].get("unseen_environment_score")
            result = {
                "experiment_id": "EXP-H2-001",
                "pair_id": pair_id,
                "learner": pair["learner"],
                "baseline": BASELINE,
                "environment": pair["environment"],
                "seed": pair["seed"],
                "status": "complete",
                "learner_source_cell": learner_path.name,
                "baseline_source_cell": baseline_path.name,
                "learner_unseen_score": lg["unseen_environment_score"],
                "baseline_unseen_score": bg["unseen_environment_score"],
                "delta_ood": delta,
                "learner_generalization_delta": lg.get("generalization_delta"),
                "baseline_generalization_delta": bg.get("generalization_delta"),
                "delta_generalization_delta": None if lg.get("generalization_delta") is None or bg.get("generalization_delta") is None else float(lg["generalization_delta"] - bg["generalization_delta"]),
                "learner_unseen_accuracy": lg.get("task_metrics", {}).get("unseen_accuracy"),
                "baseline_unseen_accuracy": bg.get("task_metrics", {}).get("unseen_accuracy"),
                "learner_unseen_auroc": lg.get("task_metrics", {}).get("unseen_auroc"),
                "baseline_unseen_auroc": bg.get("task_metrics", {}).get("unseen_auroc"),
                "learner_seen_accuracy": lg.get("task_metrics", {}).get("accuracy"),
                "baseline_seen_accuracy": bg.get("task_metrics", {}).get("accuracy"),
                "learner_seen_auroc": lg.get("task_metrics", {}).get("auroc"),
                "baseline_seen_auroc": bg.get("task_metrics", {}).get("auroc"),
                "raw_unseen_score": raw_score,
                "delta_ood_vs_raw": None if raw_score is None else float(lg["unseen_environment_score"] - raw_score),
                "catastrophic_regression": delta < CATASTROPHIC_THRESHOLD,
                "source_hashes": {
                    "learner_results": _sha(learner_path / "results.json"),
                    "learner_provenance": _sha(learner_path / "provenance.json"),
                    "baseline_results": _sha(baseline_path / "results.json"),
                    "baseline_provenance": _sha(baseline_path / "provenance.json"),
                    "raw": raw_identity,
                },
                "limitations": [] if raw_result is not None else [raw_identity["reason"]],
            }
            _write_json(out / "pair_result.json", result)
            provenance = {
                "experiment_id": "EXP-H2-001",
                "pair_id": pair_id,
                "artifact_type": "derived",
                "protocol_freeze_sha256": _sha(FREEZE_PATH),
                "matrix_manifest_sha256": _sha(MANIFEST_PATH),
                "reference_manifest_sha256": freeze["reference_benchmark"]["manifest_sha256"],
                "source_paths": {"learner": str(learner_path), "baseline": str(baseline_path), "raw": raw_identity.get("path")},
                "source_hashes": result["source_hashes"],
                "git": git,
                "analysis_script": str(Path(__file__).relative_to(ROOT)),
                "analysis_script_sha256": _sha(Path(__file__)),
                "seed": pair["seed"],
                "command": "python -m pipeline.run_h2_closure derive",
                "runtime": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
            }
            _write_json(out / "provenance.json", provenance)
            complete += 1
        except Exception as exc:
            _write_json(out / "failure.json", {"pair_id": pair_id, "status": "failed", "error": repr(exc)})
            failed += 1
    summary = {
        "experiment_id": "EXP-H2-001",
        "evidence_mode": "derived",
        "expected_primary_pairs": len(manifest["pairs"]),
        "complete_primary_pairs": complete,
        "failed_primary_pairs": failed,
        "inapplicable_env2_pairs": len(manifest["inapplicable_pairs"]),
    }
    _write_json(ARTIFACT_ROOT / "derive_summary.json", summary)
    return summary


def _bootstrap_ci(values: list[float]) -> dict:
    if not values:
        return {"low": None, "high": None, "level": CI_LEVEL, "method": "paired_bootstrap_mean_percentile"}
    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    sampled = arr[rng.integers(0, len(arr), size=(BOOTSTRAP_REPS, len(arr)))].mean(axis=1)
    alpha = 1.0 - CI_LEVEL
    return {
        "low": float(np.quantile(sampled, alpha / 2)),
        "high": float(np.quantile(sampled, 1 - alpha / 2)),
        "level": CI_LEVEL,
        "method": "paired_bootstrap_mean_percentile",
        "repetitions": BOOTSTRAP_REPS,
        "rng_seed": BOOTSTRAP_SEED,
    }


def _summary(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(arr.mean()), "median": float(np.median(arr)), "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(arr.min()), "max": float(arr.max()),
    }


def _wlt(values: list[float]) -> dict:
    return {
        "wins": sum(v > TIE_TOLERANCE for v in values),
        "losses": sum(v < -TIE_TOLERANCE for v in values),
        "ties": sum(abs(v) <= TIE_TOLERANCE for v in values),
    }


def _classify(values: list[float], ci: dict, catastrophic_count: int, complete: bool) -> str:
    if not complete:
        return "INCONCLUSIVE"
    wlt = _wlt(values)
    mean = float(np.mean(values))
    if mean > 0 and ci["low"] is not None and ci["low"] > 0 and catastrophic_count == 0:
        return "SUPPORTED"
    if mean < 0 and ci["high"] is not None and ci["high"] < 0 and wlt["losses"] > wlt["wins"]:
        return "FALSIFIED_UNDER_TESTED_CONDITIONS"
    return "NOT_SUPPORTED"


def aggregate() -> dict:
    freeze = _load_freeze()
    manifest = _load_manifest()
    if not ARTIFACT_ROOT.is_dir():
        raise RuntimeError("Derived H2 evidence missing")
    comparisons = []
    failures = []
    for learner in LEARNERS:
        pairs = []
        for pair in [p for p in manifest["pairs"] if p["learner"] == learner]:
            pair_dir = ARTIFACT_ROOT / "pairs" / pair["pair_id"]
            rp, pp = pair_dir / "pair_result.json", pair_dir / "provenance.json"
            if not rp.is_file() or not pp.is_file():
                failures.append({"pair_id": pair["pair_id"], "reason": "missing derived pair/provenance"})
                continue
            result, provenance = _read_json(rp), _read_json(pp)
            if provenance.get("protocol_freeze_sha256") != _sha(FREEZE_PATH) or provenance.get("matrix_manifest_sha256") != _sha(MANIFEST_PATH):
                raise RuntimeError(f"Pair protocol/manifest hash mismatch: {pair['pair_id']}")
            if result.get("environment") != pair["environment"] or result.get("seed") != pair["seed"] or result.get("learner") != learner:
                raise RuntimeError(f"Pair identity mismatch: {pair['pair_id']}")
            pairs.append(result)
        values = [float(p["delta_ood"]) for p in pairs]
        ci = _bootstrap_ci(values)
        catastrophics = [p["pair_id"] for p in pairs if p["catastrophic_regression"]]
        per_env = {}
        for environment in ELIGIBLE_ENVS:
            subset = [p for p in pairs if p["environment"] == environment]
            vals = [float(p["delta_ood"]) for p in subset]
            per_env[environment] = {
                "pair_count": len(subset),
                "wins_losses_ties": _wlt(vals),
                "delta_ood": _summary(vals),
                "catastrophic_regressions": [p["pair_id"] for p in subset if p["catastrophic_regression"]],
            }
        raw_pairs = [p for p in pairs if p.get("delta_ood_vs_raw") is not None]
        raw_values = [float(p["delta_ood_vs_raw"]) for p in raw_pairs]
        gen_values = [float(p["delta_generalization_delta"]) for p in pairs if p.get("delta_generalization_delta") is not None]
        label = _classify(values, ci, len(catastrophics), len(pairs) == 15)
        comparisons.append({
            "learner": learner,
            "fidelity": next(x["fidelity"] for x in freeze["learners"] if x["learner_id"] == learner),
            "expected_pairs": 15,
            "complete_pairs": len(pairs),
            "missing_or_failed_pairs": 15 - len(pairs),
            "wins_losses_ties_vs_l0": _wlt(values),
            "delta_ood": _summary(values) if values else None,
            "paired_confidence_interval": ci,
            "catastrophic_regression_count": len(catastrophics),
            "catastrophic_regression_pairs": catastrophics,
            "per_environment": per_env,
            "per_seed_pairs": pairs,
            "secondary_generalization_delta_difference": _summary(gen_values) if gen_values else None,
            "raw_comparison": {
                "comparable_pair_count": len(raw_pairs),
                "noncomparable_pair_count": len(pairs) - len(raw_pairs),
                "delta_ood_vs_raw": _summary(raw_values) if raw_values else None,
                "wins_losses_ties": _wlt(raw_values) if raw_values else None,
            },
            "developer_candidate_h2": label,
            "candidate_authority": "DEVELOPER_CANDIDATE_ONLY",
        })
    labels = [c["developer_candidate_h2"] for c in comparisons]
    if any(label == "SUPPORTED" for label in labels):
        global_candidate = "SUPPORTED"
    elif labels and all(label == "FALSIFIED_UNDER_TESTED_CONDITIONS" for label in labels):
        global_candidate = "FALSIFIED_UNDER_TESTED_CONDITIONS"
    elif any(label == "INCONCLUSIVE" for label in labels):
        global_candidate = "INCONCLUSIVE"
    else:
        global_candidate = "NOT_SUPPORTED"
    output = {
        "experiment_id": "EXP-H2-001",
        "evidence_mode": "derived",
        "protocol_freeze_sha256": _sha(FREEZE_PATH),
        "matrix_manifest_sha256": _sha(MANIFEST_PATH),
        "reference_manifest_sha256": freeze["reference_benchmark"]["manifest_sha256"],
        "primary_baseline": BASELINE,
        "eligible_environments": ELIGIBLE_ENVS,
        "env2_status": freeze["inapplicable_environment"],
        "expected_primary_pairs": 60,
        "completed_primary_pairs": sum(c["complete_pairs"] for c in comparisons),
        "failed_or_missing_primary_pairs": len(failures),
        "inapplicable_env2_pairs": len(manifest["inapplicable_pairs"]),
        "tie_tolerance": TIE_TOLERANCE,
        "catastrophic_regression_threshold": CATASTROPHIC_THRESHOLD,
        "confidence_interval": freeze["confidence_interval"],
        "comparisons": comparisons,
        "failures": failures,
        "global_developer_candidate_h2": global_candidate,
        "candidate_authority": "DEVELOPER_CANDIDATE_ONLY",
        "limitations": [
            "H2 is limited to frozen synthetic ENV-1, ENV-3, ENV-4 and five seeds.",
            "ENV-2 is inapplicable because frozen unseen_environment_score is null; it is not imputed.",
            "L3 is an IRM-style surrogate; L1/L2/L4 are adapted implementations.",
            "RAW is a secondary control and never replaces L0 as the primary H2 baseline.",
            "Negative/null results are retained; no learner was tuned or retrained for H2.",
        ],
    }
    _write_json(COMPARISON_PATH, output)
    lines = [
        "# H2 Closure Report - EXP-H2-001",
        "",
        f"Evidence mode: `derived`. Global developer candidate: `{global_candidate}` (`DEVELOPER_CANDIDATE_ONLY`).",
        "",
        f"Primary baseline: `{BASELINE}`. Eligible OOD environments: {', '.join(ELIGIBLE_ENVS)}. ENV-2: `INAPPLICABLE_FOR_H2_PRIMARY`.",
        "",
        f"Paired CI: deterministic bootstrap mean, {BOOTSTRAP_REPS} repetitions, seed {BOOTSTRAP_SEED}, {int(CI_LEVEL*100)}% percentile CI. Tie tolerance: {TIE_TOLERANCE}. Catastrophic threshold: delta < {CATASTROPHIC_THRESHOLD}.",
        "",
        "| Learner | Fidelity | Pairs | W/L/T vs L0 | Mean delta | Median | Min | Max | 95% CI | Catastrophic | Candidate |",
        "|---|---|---:|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for c in comparisons:
        s, ci, w = c["delta_ood"], c["paired_confidence_interval"], c["wins_losses_ties_vs_l0"]
        lines.append(f"| {c['learner']} | {c['fidelity']} | {c['complete_pairs']} | {w['wins']}/{w['losses']}/{w['ties']} | {s['mean']:.6f} | {s['median']:.6f} | {s['min']:.6f} | {s['max']:.6f} | [{ci['low']:.6f}, {ci['high']:.6f}] | {c['catastrophic_regression_count']} | {c['developer_candidate_h2']} |")
    lines += ["", "## Per-environment summaries", ""]
    for c in comparisons:
        lines += [f"### {c['learner']}", "", "| Environment | Pairs | W/L/T | Mean delta | Min | Max | Catastrophic |", "|---|---:|---|---:|---:|---:|---:|"]
        for env, e in c["per_environment"].items():
            w, s = e["wins_losses_ties"], e["delta_ood"]
            lines.append(f"| {env} | {e['pair_count']} | {w['wins']}/{w['losses']}/{w['ties']} | {s['mean']:.6f} | {s['min']:.6f} | {s['max']:.6f} | {len(e['catastrophic_regressions'])} |")
        lines.append("")
    lines += ["## Per-seed evidence", "", "| Learner | Environment | Seed | Learner OOD | L0 OOD | Delta OOD | RAW OOD | Delta vs RAW | Catastrophic |", "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for c in comparisons:
        for p in c["per_seed_pairs"]:
            raw = "null" if p["raw_unseen_score"] is None else f"{p['raw_unseen_score']:.6f}"
            drv = "null" if p["delta_ood_vs_raw"] is None else f"{p['delta_ood_vs_raw']:.6f}"
            lines.append(f"| {c['learner']} | {p['environment']} | {p['seed']} | {p['learner_unseen_score']:.6f} | {p['baseline_unseen_score']:.6f} | {p['delta_ood']:.6f} | {raw} | {drv} | {p['catastrophic_regression']} |")
    lines += ["", "## Limitations", ""] + [f"- {x}" for x in output["limitations"]]
    lines += ["", "## Claim boundary", "", "Candidate labels apply only to paired OOD transfer versus frozen L0/PCA on ENV-1, ENV-3, ENV-4 and seeds 42, 123, 456, 789, 1011. Software PASS is not scientific support. QA/PM owns final H2 closure."]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="OIR-PPV H2 closure")
    parser.add_argument("command", choices=["freeze-protocol", "freeze-matrix", "derive", "aggregate"])
    args = parser.parse_args()
    result = {
        "freeze-protocol": freeze_protocol,
        "freeze-matrix": freeze_matrix,
        "derive": derive_pairs,
        "aggregate": aggregate,
    }[args.command]()
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
