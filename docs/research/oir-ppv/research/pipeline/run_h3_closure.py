"""Execute the frozen OIR-PPV H3 nuisance-robustness closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from environments.base import EnvironmentRegistry
from pipeline.causal_validation import CausalValidator
from pipeline.dependency_analysis import DependencyAnalyzer
from pipeline.run_m3_experiment import (
    TableEncoder,
    _apply_overrides,
    _metadata_table,
    _split_table,
    create_extractor,
)


REFERENCE_MANIFEST = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json"
REFERENCE_CONFIG_ROOT = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/configs/full"
M3_PROTOCOL = ROOT / "benchmark/M3_PROTOCOL.md"
EXP_ROOT = ROOT / "experiments/OIR_PPV/H3_Closure/EXP-H3-001"
ARTIFACT_ROOT = ROOT / "artifacts/h3_closure/EXP-H3-001"
FREEZE_PATH = EXP_ROOT / "h3_execution_manifest.json"
FREEZE_HASH_PATH = EXP_ROOT / "h3_execution_manifest.sha256"
SMOKE_PATH = EXP_ROOT / "h3_smoke_evidence.json"
SUMMARY_PATH = EXP_ROOT / "h3_summary.json"
REPORT_PATH = EXP_ROOT / "H3_CLOSURE_REPORT.md"

LEARNERS = ["L0", "L1", "L2", "L3", "L4"]
CANDIDATES = ["L1", "L2", "L3", "L4"]
ENVS = ["ENV-1", "ENV-2", "ENV-3", "ENV-4"]
TASK_PRESERVING_ENVS = ["ENV-1", "ENV-2", "ENV-4"]
SEEDS = [42, 123, 456, 789, 1011]
BASELINE = "L0"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _array_hash(value: np.ndarray) -> str:
    arr = np.ascontiguousarray(value)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _git_state() -> dict:
    return {
        "branch": _git("branch", "--show-current"),
        "head": _git("rev-parse", "HEAD"),
        "dirty": bool(_git("status", "--porcelain")),
    }


def _reference() -> dict:
    manifest = _read_json(REFERENCE_MANIFEST)
    if manifest.get("experiment_id") != "EXP-LRN-001" or manifest.get("status") != "frozen":
        raise RuntimeError("EXP-LRN-001 is not the frozen reference benchmark")
    if manifest.get("seeds") != SEEDS:
        raise RuntimeError("Frozen seed identity mismatch")
    return manifest


def freeze() -> dict:
    if FREEZE_PATH.exists() or FREEZE_HASH_PATH.exists():
        raise FileExistsError("Refusing to overwrite frozen H3 execution manifest")
    reference = _reference()
    learner_fidelity = {item["learner_id"]: item["fidelity"] for item in reference["learners"]}
    cells = [
        {"cell_id": f"{learner}-{env}-S{seed}", "learner": learner, "environment": env, "seed": seed}
        for learner in LEARNERS for env in ENVS for seed in SEEDS
    ]
    manifest = {
        "experiment_id": "EXP-H3-001",
        "hypothesis_id": "H3",
        "status": "frozen_before_decisive_execution",
        "frozen_at": datetime.now().isoformat(),
        "source": _git_state(),
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
        },
        "primary_baseline": BASELINE,
        "learners": [{"learner_id": x, "fidelity": learner_fidelity[x]} for x in LEARNERS],
        "environments": ENVS,
        "seeds": SEEDS,
        "cell_count": len(cells),
        "cells": cells,
        "paired_rule": "same environment + seed + factual rows + nuisance target/value for candidate and L0",
        "primary_metric": "Delta_N = Perf_factual - Perf_do(N); smaller absolute degradation is better",
        "leakage_metric": "max nuisance leakage_score emitted by the frozen DependencyAnalyzer probe",
        "retained_utility_metric": "factual downstream classification accuracy using M3 LogisticRegression semantics",
        "do_N_response": "mean absolute representation shift and invariance_score = 1/(1+mean_shift)",
        "closure_rule": {
            "SUPPORTED": "paired mean absolute Delta_N lower than L0, paired mean leakage lower/equal to L0, and paired mean factual predictive utility retained relative to L0",
            "NOT_SUPPORTED": "valid comparable evidence where leakage or task degradation is not improved, or apparent invariance loses useful predictive signal",
            "INCONCLUSIVE": "required comparable evidence missing/invalid or nuisance cannot be cleanly isolated",
            "DEGENERATE": "evidence flag only; final label remains NOT_SUPPORTED",
        },
        "environment_semantics": {
            "ENV-1": "task-preserving nuisance intervention supported",
            "ENV-2": "task-preserving nuisance intervention supported",
            "ENV-3": "existing do(N) recomputes Y and labels; retain as inapplicable/inconclusive for task-preserving H3 evidence",
            "ENV-4": "task-preserving shortcut/nuisance intervention supported",
        },
        "failed_cell_policy": "retain failed/null/inapplicable evidence; no replacement, silent retry, or seed substitution",
    }
    _write_json(FREEZE_PATH, manifest)
    FREEZE_HASH_PATH.write_text(_sha(FREEZE_PATH), encoding="utf-8")
    return manifest


def _load_freeze() -> dict:
    if not FREEZE_PATH.is_file() or not FREEZE_HASH_PATH.is_file():
        raise RuntimeError("H3 execution manifest is not frozen")
    expected = FREEZE_HASH_PATH.read_text(encoding="utf-8").strip()
    if expected != _sha(FREEZE_PATH):
        raise RuntimeError("H3 execution manifest hash mismatch")
    return _read_json(FREEZE_PATH)


def _test_metadata(metadata: dict, indices: np.ndarray, n_rows: int) -> dict:
    out: dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            out[key] = {
                sub_key: np.asarray(sub_value)[indices] if isinstance(sub_value, np.ndarray) and len(sub_value) == n_rows else sub_value
                for sub_key, sub_value in value.items()
            }
        elif isinstance(value, np.ndarray) and len(value) == n_rows:
            out[key] = value[indices]
        else:
            out[key] = value
    return out


def _cell_config(learner: str, env: str, seed: int) -> Path:
    path = REFERENCE_CONFIG_ROOT / f"{learner}-{env}-S{seed}.yaml"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _prepare_cell(learner: str, env_id: str, seed: int) -> dict:
    config_path = _cell_config(learner, env_id, seed)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    env_cfg = config["environment"]
    base_cfg = yaml.safe_load((ROOT / env_cfg["config_path"]).read_text(encoding="utf-8"))
    effective = _apply_overrides(base_cfg, env_cfg.get("overrides", {}))
    effective_path = ARTIFACT_ROOT / "effective_configs" / f"{learner}-{env_id}-S{seed}.yaml"
    effective_path.parent.mkdir(parents=True, exist_ok=True)
    effective_path.write_text(yaml.safe_dump(effective, sort_keys=False), encoding="utf-8")
    env = EnvironmentRegistry.create_from_config_path(effective_path, seed)
    data = env.generate()
    train_idx = np.asarray(data.splits["train"], dtype=int)
    test_idx = np.asarray(data.splits["test"], dtype=int)
    context_raw = _metadata_table(data.metadata, "Z", "context_variables", len(data.labels))
    nuisance_raw = _metadata_table(data.metadata, "N", "nuisance_variables", len(data.labels))
    context_encoder = TableEncoder()
    nuisance_encoder = TableEncoder()
    train_context = context_encoder.fit_transform(_split_table(context_raw, train_idx))
    test_context = context_encoder.transform(_split_table(context_raw, test_idx))
    nuisance_encoder.fit(_split_table(nuisance_raw, train_idx))
    test_nuisance = nuisance_encoder.transform(_split_table(nuisance_raw, test_idx))
    extractor = create_extractor(config["pipeline"]["invariant_extractor"], seed)
    train_obs = data.observations[train_idx]
    test_obs = data.observations[test_idx]
    train_labels = data.labels[train_idx]
    test_labels = data.labels[test_idx]
    train_i = extractor.extract(train_obs, train_context, train_labels).invariant_representation
    factual_i = extractor.extract(test_obs, test_context, None).invariant_representation
    predictor = LogisticRegression(max_iter=1000, random_state=seed)
    predictor.fit(train_i, train_labels)
    factual_accuracy = float(predictor.score(factual_i, test_labels))
    metadata = _test_metadata(data.metadata, test_idx, len(data.labels))
    return {
        "config_path": config_path,
        "effective_path": effective_path,
        "env": env,
        "metadata": metadata,
        "test_obs": test_obs,
        "test_context": test_context,
        "test_nuisance": test_nuisance,
        "test_labels": test_labels,
        "extractor": extractor,
        "predictor": predictor,
        "factual_i": factual_i,
        "factual_accuracy": factual_accuracy,
    }


def _mock_data(prepared: dict, seed: int) -> Any:
    return type("H3PairData", (), {
        "observations": prepared["test_obs"],
        "labels": prepared["test_labels"],
        "metadata": prepared["metadata"],
        "splits": {},
        "config_hash": "",
        "seed": seed,
        "timestamp": "",
    })()


def _paired_interventions(prepared: dict, seed: int) -> tuple[str | None, list[Any], list[dict]]:
    target, values = CausalValidator._target_and_values(prepared["env"], prepared["metadata"], "nuisance")
    rows = []
    if target is None:
        return None, [], rows
    for index, value in enumerate(values):
        intervened = prepared["env"].intervene(_mock_data(prepared, seed), target, value)
        labels_preserved = np.array_equal(intervened.labels, prepared["test_labels"])
        if not labels_preserved:
            rows.append({
                "index": index, "target": target, "value": value,
                "task_preserving": False,
                "reason": "environment intervention changed task labels",
            })
            continue
        intervened_i = prepared["extractor"].extract(intervened.observations, prepared["test_context"], None).invariant_representation
        accuracy = float(prepared["predictor"].score(intervened_i, prepared["test_labels"]))
        mean_shift = float(np.mean(np.abs(prepared["factual_i"] - intervened_i)))
        rows.append({
            "index": index,
            "target": target,
            "value": value,
            "task_preserving": True,
            "factual_accuracy": prepared["factual_accuracy"],
            "intervened_accuracy": accuracy,
            "delta_n": prepared["factual_accuracy"] - accuracy,
            "abs_delta_n": abs(prepared["factual_accuracy"] - accuracy),
            "mean_shift": mean_shift,
            "invariance_score": 1.0 / (1.0 + mean_shift),
            "failure_below_frozen_0_5": (1.0 / (1.0 + mean_shift)) < 0.5,
            "intervened_observation_sha256": _array_hash(intervened.observations),
            "intervened_representation_sha256": _array_hash(intervened_i),
        })
    return target, values, rows


def _run_cell(learner: str, env_id: str, seed: int, output_root: Path) -> dict:
    cell_id = f"{learner}-{env_id}-S{seed}"
    out = output_root / cell_id
    out.mkdir(parents=True, exist_ok=True)
    prepared = _prepare_cell(learner, env_id, seed)
    target, values, interventions = _paired_interventions(prepared, seed)
    clean = [row for row in interventions if row.get("task_preserving")]
    dependency = DependencyAnalyzer(seed).analyze(
        prepared["factual_i"], prepared["test_context"], prepared["test_nuisance"],
        config_hash=prepared["extractor"].get_config_hash(),
    )
    leak_n = max((x.leakage_score for x in dependency.nuisance_sensitivities), default=0.0)
    task_preserving = bool(clean) and len(clean) == len(interventions)
    status = "complete" if task_preserving else ("inapplicable" if env_id == "ENV-3" else "failed")
    result = {
        "cell_id": cell_id,
        "status": status,
        "learner": learner,
        "environment": env_id,
        "seed": seed,
        "factual_sample_sha256": _array_hash(prepared["test_obs"]),
        "task_label_sha256": _array_hash(prepared["test_labels"]),
        "nuisance_target": target,
        "nuisance_values": values,
        "factual_predictive_utility": prepared["factual_accuracy"],
        "leak_n": float(leak_n),
        "nuisance_leakage_detected": bool(dependency.nuisance_leakage_detected),
        "avg_nuisance_sensitivity": float(dependency.avg_nuisance_sensitivity),
        "shortcut_learning_score": float(dependency.shortcut_learning_score) if env_id == "ENV-4" else None,
        "interventions": interventions,
        "mean_abs_delta_n": float(np.mean([x["abs_delta_n"] for x in clean])) if clean else None,
        "mean_do_n_invariance": float(np.mean([x["invariance_score"] for x in clean])) if clean else None,
        "failure_count": sum(bool(x.get("failure_below_frozen_0_5")) for x in clean),
        "task_preserving": task_preserving,
        "provenance": {
            "config_path": str(prepared["config_path"].relative_to(ROOT)),
            "config_sha256": _sha(prepared["config_path"]),
            "effective_config_sha256": _sha(prepared["effective_path"]),
            "h3_execution_manifest_sha256": _sha(FREEZE_PATH),
            "reference_manifest_sha256": _sha(REFERENCE_MANIFEST),
            "m3_protocol_sha256": _sha(M3_PROTOCOL),
            "extractor_config_hash": prepared["extractor"].get_config_hash(),
        },
    }
    _write_json(out / "paired_evidence.json", result)
    return result


def smoke() -> dict:
    _load_freeze()
    results = [_run_cell(x, "ENV-4", 42, ARTIFACT_ROOT / "smoke") for x in ["L0", "L1"]]
    baseline, candidate = results
    passed = (
        baseline["status"] == "complete"
        and candidate["status"] == "complete"
        and baseline["factual_sample_sha256"] == candidate["factual_sample_sha256"]
        and baseline["task_label_sha256"] == candidate["task_label_sha256"]
        and baseline["nuisance_target"] == candidate["nuisance_target"]
        and baseline["nuisance_values"] == candidate["nuisance_values"]
    )
    evidence = {
        "status": "PASS" if passed else "FAIL",
        "pair": "L1-vs-L0-ENV-4-S42",
        "checks": {
            "same_factual_rows": baseline["factual_sample_sha256"] == candidate["factual_sample_sha256"],
            "same_labels": baseline["task_label_sha256"] == candidate["task_label_sha256"],
            "same_target": baseline["nuisance_target"] == candidate["nuisance_target"],
            "same_values": baseline["nuisance_values"] == candidate["nuisance_values"],
            "task_preserving_both": baseline["task_preserving"] and candidate["task_preserving"],
        },
    }
    _write_json(SMOKE_PATH, evidence)
    if not passed:
        raise RuntimeError("H3 paired smoke failed")
    return evidence


def run_matrix() -> dict:
    _load_freeze()
    if not SMOKE_PATH.is_file() or _read_json(SMOKE_PATH).get("status") != "PASS":
        raise RuntimeError("H3 smoke must PASS before decisive matrix")
    statuses = {"complete": 0, "failed": 0, "inapplicable": 0}
    failures = []
    for learner in LEARNERS:
        for env_id in ENVS:
            for seed in SEEDS:
                try:
                    result = _run_cell(learner, env_id, seed, ARTIFACT_ROOT / "full")
                    statuses[result["status"]] += 1
                except Exception as exc:
                    cell_id = f"{learner}-{env_id}-S{seed}"
                    statuses["failed"] += 1
                    failure = {"cell_id": cell_id, "status": "failed", "error": repr(exc)}
                    failures.append(failure)
                    _write_json(ARTIFACT_ROOT / "full" / cell_id / "failure.json", failure)
    result = {"experiment_id": "EXP-H3-001", "counts": statuses, "failures": failures}
    _write_json(ARTIFACT_ROOT / "matrix_execution.json", result)
    return result


def _load_cell(learner: str, env_id: str, seed: int) -> dict | None:
    path = ARTIFACT_ROOT / "full" / f"{learner}-{env_id}-S{seed}" / "paired_evidence.json"
    return _read_json(path) if path.is_file() else None


def aggregate() -> dict:
    freeze_manifest = _load_freeze()
    learner_environment = []
    for learner in LEARNERS:
        for env_id in ENVS:
            cells = [_load_cell(learner, env_id, seed) for seed in SEEDS]
            present = [cell for cell in cells if cell is not None]
            complete = [cell for cell in present if cell.get("status") == "complete"]
            learner_environment.append({
                "learner": learner,
                "environment": env_id,
                "complete_seeds": len(complete),
                "inapplicable_seeds": sum(cell.get("status") == "inapplicable" for cell in present),
                "failed_or_missing_seeds": len(SEEDS) - len(complete) - sum(cell.get("status") == "inapplicable" for cell in present),
                "mean_abs_delta_n": float(np.mean([cell["mean_abs_delta_n"] for cell in complete])) if complete else None,
                "mean_leak_n": float(np.mean([cell["leak_n"] for cell in complete])) if complete else None,
                "mean_predictive_utility": float(np.mean([cell["factual_predictive_utility"] for cell in complete])) if complete else None,
                "mean_do_n_invariance": float(np.mean([cell["mean_do_n_invariance"] for cell in complete])) if complete else None,
                "mean_shortcut_learning_score": float(np.mean([cell["shortcut_learning_score"] for cell in complete])) if env_id == "ENV-4" and complete else None,
                "failure_count": sum(cell["failure_count"] for cell in complete),
            })
    comparisons = []
    for learner in CANDIDATES:
        pairs = []
        missing = []
        for env_id in TASK_PRESERVING_ENVS:
            for seed in SEEDS:
                cand = _load_cell(learner, env_id, seed)
                base = _load_cell(BASELINE, env_id, seed)
                pair_id = f"{learner}-vs-{BASELINE}-{env_id}-S{seed}"
                if not cand or not base or cand.get("status") != "complete" or base.get("status") != "complete":
                    missing.append(pair_id)
                    continue
                if cand["factual_sample_sha256"] != base["factual_sample_sha256"] or cand["nuisance_values"] != base["nuisance_values"]:
                    missing.append(pair_id + ":pair_identity_mismatch")
                    continue
                pairs.append({
                    "pair_id": pair_id,
                    "environment": env_id,
                    "seed": seed,
                    "delta_task_degradation": cand["mean_abs_delta_n"] - base["mean_abs_delta_n"],
                    "delta_leak_n": cand["leak_n"] - base["leak_n"],
                    "delta_predictive_utility": cand["factual_predictive_utility"] - base["factual_predictive_utility"],
                    "delta_do_n_invariance": cand["mean_do_n_invariance"] - base["mean_do_n_invariance"],
                })
        if missing:
            label = "INCONCLUSIVE"
            degenerate = False
        else:
            mean_task = float(np.mean([x["delta_task_degradation"] for x in pairs]))
            mean_leak = float(np.mean([x["delta_leak_n"] for x in pairs]))
            mean_utility = float(np.mean([x["delta_predictive_utility"] for x in pairs]))
            mean_invariance = float(np.mean([x["delta_do_n_invariance"] for x in pairs]))
            degenerate = mean_invariance > 0 and mean_utility < 0
            label = "SUPPORTED" if mean_task < 0 and mean_leak <= 0 and mean_utility >= 0 else "NOT_SUPPORTED"
        comparisons.append({
            "learner": learner,
            "complete_pairs": len(pairs),
            "missing_pairs": missing,
            "mean_delta_task_degradation": float(np.mean([x["delta_task_degradation"] for x in pairs])) if pairs else None,
            "mean_delta_leak_n": float(np.mean([x["delta_leak_n"] for x in pairs])) if pairs else None,
            "mean_delta_predictive_utility": float(np.mean([x["delta_predictive_utility"] for x in pairs])) if pairs else None,
            "mean_delta_do_n_invariance": float(np.mean([x["delta_do_n_invariance"] for x in pairs])) if pairs else None,
            "task_degradation_wins": sum(x["delta_task_degradation"] < 0 for x in pairs),
            "leakage_wins_or_ties": sum(x["delta_leak_n"] <= 0 for x in pairs),
            "utility_retained_pairs": sum(x["delta_predictive_utility"] >= 0 for x in pairs),
            "degenerate": degenerate,
            "developer_candidate_h3": label,
            "candidate_authority": "DEVELOPER_CANDIDATE_ONLY",
        })
    labels = [x["developer_candidate_h3"] for x in comparisons]
    global_label = "INCONCLUSIVE" if "INCONCLUSIVE" in labels else ("SUPPORTED" if all(x == "SUPPORTED" for x in labels) else "NOT_SUPPORTED")
    counts = {"complete": 0, "failed": 0, "inapplicable": 0}
    for learner in LEARNERS:
        for env_id in ENVS:
            for seed in SEEDS:
                cell = _load_cell(learner, env_id, seed)
                if cell:
                    counts[cell["status"]] += 1
                else:
                    counts["failed"] += 1
    summary = {
        "experiment_id": "EXP-H3-001",
        "status": "READY_FOR_QA_REVIEW",
        "source": _git_state(),
        "execution_manifest_sha256": _sha(FREEZE_PATH),
        "reference_manifest_sha256": _sha(REFERENCE_MANIFEST),
        "m3_protocol_sha256": _sha(M3_PROTOCOL),
        "matrix_counts": counts,
        "task_preserving_environments": TASK_PRESERVING_ENVS,
        "inapplicable_environment": {"environment": "ENV-3", "reason": "existing do(N) recomputes Y and task labels"},
        "learner_environment_summaries": learner_environment,
        "comparisons": comparisons,
        "global_developer_candidate_h3": global_label,
        "candidate_authority": "DEVELOPER_CANDIDATE_ONLY",
        "claim_boundary": "tested L1-L4 configurations versus frozen L0/PCA under ENV-1, ENV-2, ENV-4 and seeds 42/123/456/789/1011 only",
        "freeze_source": freeze_manifest["source"],
    }
    _write_json(SUMMARY_PATH, summary)
    lines = [
        "# H3 Closure Report — EXP-H3-001",
        "",
        f"Status: `READY_FOR_QA_REVIEW`  ",
        f"Authority: `DEVELOPER_CANDIDATE_ONLY`  ",
        f"Global developer candidate: `{global_label}`",
        "",
        "ENV-1, ENV-2 and ENV-4 provide task-preserving paired nuisance interventions. ENV-3 is retained as inapplicable for decisive H3 evidence because its existing `do(N)` recomputes `Y` and task labels.",
        "",
        "| Learner | Pairs | mean Δ task degradation vs L0 | mean Δ leakage vs L0 | mean Δ predictive utility vs L0 | mean Δ do(N) invariance vs L0 | Degenerate | Candidate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in comparisons:
        fmt = lambda v: "null" if v is None else f"{v:.6f}"
        lines.append(f"| {row['learner']} | {row['complete_pairs']}/15 | {fmt(row['mean_delta_task_degradation'])} | {fmt(row['mean_delta_leak_n'])} | {fmt(row['mean_delta_predictive_utility'])} | {fmt(row['mean_delta_do_n_invariance'])} | {row['degenerate']} | {row['developer_candidate_h3']} |")
    lines += [
        "",
        "## Learner × environment summaries",
        "",
        "| Learner | Environment | Complete seeds | mean |Delta_N| | mean Leak_N | mean predictive utility | mean do(N) invariance | ENV-4 shortcut score | Failures |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in learner_environment:
        fmt = lambda v: "null" if v is None else f"{v:.6f}"
        lines.append(f"| {row['learner']} | {row['environment']} | {row['complete_seeds']}/5 | {fmt(row['mean_abs_delta_n'])} | {fmt(row['mean_leak_n'])} | {fmt(row['mean_predictive_utility'])} | {fmt(row['mean_do_n_invariance'])} | {fmt(row['mean_shortcut_learning_score'])} | {row['failure_count']} |")
    lines += [
        "",
        f"Matrix cells: complete={counts['complete']}, failed={counts['failed']}, inapplicable={counts['inapplicable']}.",
        "",
        "Claim boundary: tested L1-L4 configurations versus frozen L0/PCA under the supported task-preserving nuisance interventions and frozen seeds only. This report does not establish nuisance robustness in general and does not alter H1/H2 or start H4.",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["freeze", "smoke", "run", "aggregate"])
    args = parser.parse_args()
    actions = {"freeze": freeze, "smoke": smoke, "run": run_matrix, "aggregate": aggregate}
    print(json.dumps(actions[args.command](), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
