"""Execute the gated EXP-LRN-001 reference learner benchmark."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

import numpy as np
import torch
import yaml

from pipeline.run_m3_experiment import run_m3_experiment


ROOT = Path(__file__).parent.parent
EXPERIMENT_ROOT = ROOT / "experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001"
DEFAULT_ARTIFACT_ROOT = ROOT / "artifacts/learner_benchmark/EXP-LRN-001"
PROTOCOL = {
    "name": "M3_PROTOCOL",
    "version": "M3-Protocol-v1.0",
    "path": "benchmark/M3_PROTOCOL.md",
}
SEEDS = [42, 123, 456, 789, 1011]

LEARNERS = [
    {
        "learner_id": "L0", "display_name": "PCA", "type": "PCA",
        "fidelity": "faithful", "paper": "Pearson, 1901, On Lines and Planes of Closest Fit",
        "implementation_source": "project-owned sklearn adapter",
        "params": {"output_dim": 8},
        "deviations": "Uses scikit-learn PCA with deterministic full SVD behavior.",
    },
    {
        "learner_id": "L1", "display_name": "Supervised MLP encoder",
        "type": "MLPTrainable", "fidelity": "adapted",
        "paper": "Rumelhart, Hinton, Williams, 1986, Learning representations by back-propagating errors",
        "implementation_source": "project-owned PyTorch implementation",
        "params": {"output_dim": 8, "hidden_dims": [24], "learning_rate": 0.01, "epochs": 4},
        "deviations": "Compact full-batch classifier used as the nonlinear representation baseline.",
    },
    {
        "learner_id": "L2", "display_name": "Variational Autoencoder",
        "type": "VAE", "fidelity": "adapted",
        "paper": "Kingma and Welling, 2013, Auto-Encoding Variational Bayes, arXiv:1312.6114",
        "implementation_source": "project-owned PyTorch implementation",
        "params": {"output_dim": 8, "hidden_dim": 24, "learning_rate": 0.005, "epochs": 4, "beta": 0.1},
        "deviations": "Compact full-batch VAE; posterior mean is used for deterministic evaluation.",
    },
    {
        "learner_id": "L3", "display_name": "IRM-style encoder",
        "type": "IRMStyle", "fidelity": "surrogate",
        "paper": "Arjovsky et al., 2019, Invariant Risk Minimization, arXiv:1907.02893",
        "implementation_source": "project-owned PyTorch implementation",
        "params": {"output_dim": 8, "hidden_dim": 24, "learning_rate": 0.01, "epochs": 4, "irm_penalty_weight": 1.0},
        "deviations": "Risk-variance surrogate across explicit context domains; not canonical IRMv1.",
    },
    {
        "learner_id": "L4", "display_name": "Domain-Adversarial encoder",
        "type": "DANN", "fidelity": "adapted",
        "paper": "Ganin et al., 2016, Domain-Adversarial Training of Neural Networks, JMLR 17(59)",
        "implementation_source": "project-owned PyTorch implementation",
        "params": {"output_dim": 8, "hidden_dim": 24, "learning_rate": 0.01, "epochs": 4, "domain_penalty_weight": 0.5},
        "deviations": "Compact full-batch DANN with task head, domain head, and gradient reversal.",
    },
]

EXPECTED_RUNTIME_TYPES = {
    "L0": "PCAEncoder",
    "L1": "MLPEncoderTrainable",
    "L2": "VAEEncoder",
    "L3": "IRMStyleEncoderSurrogate",
    "L4": "DANNSurrogateEncoder",
}

ENVIRONMENTS = [
    {
        "environment_id": "ENV-1", "config_path": "environments/env1_config.yaml",
        "generator_output_dim": 12,
        "overrides": {"generation": {"num_samples": 1200}},
        "assertion": {"type": "ood_holdout", "ood_split": "ood_unseen_style"},
    },
    {
        "environment_id": "ENV-2", "config_path": "environments/env2_config.yaml",
        "generator_output_dim": 15,
        "overrides": {"generation": {"num_samples": 1600}},
        "assertion": {"type": "composition_holdout"},
    },
    {
        "environment_id": "ENV-3", "config_path": "environments/env3_config.yaml",
        "generator_output_dim": 6,
        "overrides": {"generation": {"num_episodes": 150}},
        "assertion": {"type": "context_distribution", "ood_split": "ood_unseen_context", "min_total_variation": 0.5},
    },
    {
        "environment_id": "ENV-4", "config_path": "environments/env4_config.yaml",
        "generator_output_dim": 11,
        "overrides": {
            "generation": {"num_samples": 1200},
            "shortcut": {"correlation_strength": 0.95, "test_conditional_means": {0: 1.5, 1: 0.0, 2: -1.5}},
        },
        "assertion": {"type": "shortcut_reversal", "feature": "spurious_feature", "min_train_correlation": 0.3, "max_test_correlation": -0.3},
    },
]


def _json_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_identity() -> dict:
    paths = [ROOT / "benchmark", ROOT / "environments", ROOT / "pipeline"]
    digest = hashlib.sha256()
    count = 0
    for base in paths:
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            relative = path.relative_to(ROOT).as_posix()
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
            count += 1
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    try:
        return {
            "git_head": git("rev-parse", "HEAD"),
            "git_branch": git("branch", "--show-current"),
            "source_tree_sha256": digest.hexdigest(), "source_file_count": count,
            "source_status": git("status", "--porcelain", "--", "benchmark", "environments", "pipeline").splitlines(),
        }
    except (OSError, subprocess.CalledProcessError) as error:
        return {"git_available": False, "error": str(error), "source_tree_sha256": digest.hexdigest(), "source_file_count": count}


def _config(learner: dict, environment: dict, seed: int, run_id: str) -> dict:
    return {
        "protocol": PROTOCOL,
        "experiment": {"id": run_id, "name": "EXP-LRN-001 reference learner cell", "milestone": "M4.1"},
        "environment": {
            "family": environment["environment_id"], "config_path": environment["config_path"],
            "seed": seed, "splits": ["train", "val", "test", "ood"],
            "overrides": environment["overrides"],
        },
        "stress_assertion": environment["assertion"],
        "pipeline": {
            "invariant_extractor": {"type": learner["type"], **learner["params"], "seed": seed},
            "generator": {
                "type": "MLPDecoder", "output_dim": environment["generator_output_dim"],
                "hidden_dims": [24], "learning_rate": 0.01, "epochs": 4, "seed": seed,
            },
        },
        "evaluation": {
            "enabled": True,
            "metrics": ["invariant_consistency", "generation_validity", "reconstruction_quality", "invariant_preservation", "context_response", "diversity", "distribution_similarity"],
            "intervention_targets": ["do(N)", "do(Z)"], "counterfactual": True,
            "causal_validation": True, "dependency_analysis": True,
        },
        "output": {"base_dir": "artifacts/learner_benchmark/EXP-LRN-001"},
        "provenance": {"track_config_hashes": True, "track_seeds": True, "track_timing": True},
    }


def _write_cell_config(config: dict, config_dir: Path, run_id: str) -> Path:
    config_dir.mkdir(parents=True, exist_ok=True)
    path = config_dir / f"{run_id}.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def _execute_cell(learner: dict, environment: dict, seed: int, run_id: str,
                  output_root: Path, config_dir: Path) -> dict:
    destination = output_root / run_id
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing evidence: {destination}")
    config = _config(learner, environment, seed, run_id)
    config_path = _write_cell_config(config, config_dir, run_id)
    command = f"python -m pipeline.run_m3_experiment --config {config_path} --output {output_root}"
    started = time.perf_counter()
    try:
        result = run_m3_experiment(config_path, output_root, command=command)
        status, error = "complete", None
    except Exception as exc:
        destination.mkdir(parents=True, exist_ok=True)
        error = {"type": type(exc).__name__, "message": str(exc)}
        (destination / "failure.json").write_text(json.dumps(error, indent=2), encoding="utf-8")
        result, status = None, "failed"
    learner_config = {
        **learner, "seed": seed, "environment_id": environment["environment_id"],
        "config_path": str(config_path), "config_sha256": _json_hash(config),
        "status": status, "error": error,
    }
    (destination / "learner_config.json").write_text(
        json.dumps(learner_config, indent=2), encoding="utf-8"
    )
    return {"run_id": run_id, "status": status, "duration_seconds": time.perf_counter() - started, "error": error, "result": result}


def _strip_dynamic(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_dynamic(item) for key, item in value.items()
            if key not in {"timestamp", "path", "sha256", "command", "artifact_path", "source_config", "effective_config"}
        }
    if isinstance(value, list):
        return [_strip_dynamic(item) for item in value]
    return value


def _compare_smoke(left: Path, right: Path) -> dict:
    left_result = json.loads((left / "results.json").read_text(encoding="utf-8"))
    right_result = json.loads((right / "results.json").read_text(encoding="utf-8"))
    json_equal = _strip_dynamic(left_result) == _strip_dynamic(right_result)
    array_equal = True
    with np.load(left / "generated.npz") as a, np.load(right / "generated.npz") as b:
        if set(a.files) != set(b.files):
            array_equal = False
        else:
            array_equal = all(np.allclose(a[name], b[name], rtol=1e-6, atol=1e-7) for name in a.files)
    return {"json_equal": json_equal, "arrays_allclose": array_equal, "rtol": 1e-6, "atol": 1e-7, "passed": json_equal and array_equal}


def run_smoke(artifact_root: Path) -> dict:
    smoke_root = artifact_root / "smoke"
    records = []
    for repeat in ("run_a", "run_b"):
        for learner in LEARNERS:
            run_id = f"SMOKE-{learner['learner_id']}-ENV-1-S42"
            records.append(_execute_cell(
                learner, ENVIRONMENTS[0], 42, run_id,
                smoke_root / repeat, EXPERIMENT_ROOT / "configs/smoke" / repeat,
            ))
    comparisons = []
    for learner in LEARNERS:
        run_id = f"SMOKE-{learner['learner_id']}-ENV-1-S42"
        left, right = smoke_root / "run_a" / run_id, smoke_root / "run_b" / run_id
        if (left / "results.json").is_file() and (right / "results.json").is_file():
            comparison = _compare_smoke(left, right)
        else:
            comparison = {"passed": False, "reason": "one or both smoke runs failed"}
        comparisons.append({"learner_id": learner["learner_id"], **comparison})
    report = {
        "phase": "smoke", "seed": 42, "cell_count": len(records),
        "all_cells_complete": all(r["status"] == "complete" for r in records),
        "all_reproducible": all(c["passed"] for c in comparisons),
        "records": [{k: v for k, v in r.items() if k != "result"} for r in records],
        "comparisons": comparisons,
    }
    (smoke_root / "smoke_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _nonfinite_paths(value: Any, prefix: str = "$") -> list[str]:
    """Return JSON paths containing non-finite numeric values."""
    if isinstance(value, dict):
        paths = []
        for key, item in value.items():
            paths.extend(_nonfinite_paths(item, f"{prefix}.{key}"))
        return paths
    if isinstance(value, list):
        paths = []
        for index, item in enumerate(value):
            paths.extend(_nonfinite_paths(item, f"{prefix}[{index}]"))
        return paths
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return [prefix]
    return []


def _audit_run(directory: Path, learner: dict, seed: int) -> dict:
    required = ["results.json", "learner_config.json", "provenance.json"]
    missing = [name for name in required if not (directory / name).is_file()]
    findings: list[str] = []
    if missing:
        findings.append(f"missing artifacts: {missing}")
        return {"passed": False, "findings": findings}

    documents = {
        name: json.loads((directory / name).read_text(encoding="utf-8"))
        for name in required
    }
    result = documents["results.json"]
    learner_config = documents["learner_config.json"]
    provenance = documents["provenance.json"]
    expected_runtime = EXPECTED_RUNTIME_TYPES[learner["learner_id"]]

    if learner_config.get("learner_id") != learner["learner_id"]:
        findings.append("learner_config learner_id mismatch")
    if learner_config.get("fidelity") != learner["fidelity"]:
        findings.append("learner fidelity mismatch")
    if provenance.get("seed") != seed:
        findings.append("provenance seed mismatch")
    extractor = provenance.get("invariant_extractor", {})
    if extractor.get("requested_type") != learner["type"]:
        findings.append("requested learner type mismatch")
    if extractor.get("runtime_wrapper_type") != "EncoderWrapper":
        findings.append("unexpected extractor wrapper")
    if extractor.get("wrapped_learner_type") != expected_runtime:
        findings.append("unexpected wrapped learner runtime")
    if provenance.get("protocol", {}).get("version") != PROTOCOL["version"]:
        findings.append("protocol version mismatch")
    if result.get("shift_assertions", {}).get("passed") is not True:
        findings.append("shift assertion did not pass")
    if not result.get("evaluation", {}).get("generalization", {}).get("task_metrics"):
        findings.append("task metrics missing")
    arrays = provenance.get("arrays", {})
    array_path = Path(arrays.get("path", ""))
    if not array_path.is_file() or not arrays.get("sha256"):
        findings.append("array manifest is incomplete")
    for name, document in documents.items():
        nonfinite = _nonfinite_paths(document)
        if nonfinite:
            findings.append(f"{name} has non-finite values at {nonfinite[:5]}")
    return {"passed": not findings, "findings": findings}


def audit_smoke(artifact_root: Path) -> dict:
    smoke_root = artifact_root / "smoke"
    source = _source_identity()
    records = []
    for repeat in ("run_a", "run_b"):
        for learner in LEARNERS:
            run_id = f"SMOKE-{learner['learner_id']}-ENV-1-S42"
            directory = smoke_root / repeat / run_id
            records.append({
                "repeat": repeat,
                "run_id": run_id,
                "learner_id": learner["learner_id"],
                **_audit_run(directory, learner, 42),
            })
    source_clean = source.get("source_status") == []
    report = {
        "phase": "smoke_artifact_schema_provenance_audit",
        "required_artifacts": ["results.json", "learner_config.json", "provenance.json"],
        "source": source,
        "source_scope_clean": source_clean,
        "records": records,
        "passed": source_clean and all(record["passed"] for record in records),
    }
    (smoke_root / "smoke_artifact_audit.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def freeze_manifest(artifact_root: Path) -> dict:
    smoke_path = artifact_root / "smoke/smoke_report.json"
    if not smoke_path.is_file():
        raise RuntimeError("Smoke report missing; full matrix cannot be frozen")
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    if not smoke["all_cells_complete"] or not smoke["all_reproducible"]:
        raise RuntimeError("Smoke/reproducibility gate failed; matrix remains unfrozen")
    audit = audit_smoke(artifact_root)
    if not audit["passed"]:
        raise RuntimeError("Smoke artifact/schema/provenance audit failed")
    protocol_path = ROOT / PROTOCOL["path"]
    identity = _source_identity()
    manifest = {
        "experiment_id": "EXP-LRN-001", "status": "frozen",
        "frozen_at": datetime.now().isoformat(), "protocol": {
            **PROTOCOL, "sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        },
        "source": identity, "learners": LEARNERS, "environments": ENVIRONMENTS,
        "seeds": SEEDS, "splits": ["train", "val", "test", "ood"],
        "interventions": ["do(N)", "do(Z)"],
        "matrix_cell_count": len(LEARNERS) * len(ENVIRONMENTS) * len(SEEDS),
        "failed_run_policy": "retain failure artifact; no silent retry or seed replacement",
        "smoke_evidence": "artifacts/learner_benchmark/EXP-LRN-001/smoke/smoke_report.json",
        "smoke_audit_evidence": "artifacts/learner_benchmark/EXP-LRN-001/smoke/smoke_artifact_audit.json",
    }
    EXPERIMENT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = EXPERIMENT_ROOT / "matrix_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (EXPERIMENT_ROOT / "matrix_manifest.sha256").write_text(digest + "\n", encoding="utf-8")
    return manifest


def _load_frozen_manifest() -> dict:
    path = EXPERIMENT_ROOT / "matrix_manifest.json"
    digest_path = EXPERIMENT_ROOT / "matrix_manifest.sha256"
    if not path.is_file() or not digest_path.is_file():
        raise RuntimeError("Frozen manifest/hash missing")
    expected = digest_path.read_text(encoding="utf-8").strip()
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if expected != actual or manifest.get("status") != "frozen":
        raise RuntimeError("Frozen manifest identity mismatch")
    return manifest


def run_full(artifact_root: Path) -> dict:
    manifest = _load_frozen_manifest()
    full_root = artifact_root / "full"
    records = []
    for learner in manifest["learners"]:
        for environment in manifest["environments"]:
            for seed in manifest["seeds"]:
                run_id = f"{learner['learner_id']}-{environment['environment_id']}-S{seed}"
                records.append(_execute_cell(
                    learner, environment, int(seed), run_id,
                    full_root, EXPERIMENT_ROOT / "configs/full",
                ))
    summary = {
        "phase": "full", "expected_cells": manifest["matrix_cell_count"],
        "complete_cells": sum(r["status"] == "complete" for r in records),
        "failed_cells": sum(r["status"] == "failed" for r in records),
        "records": [{k: v for k, v in r.items() if k != "result"} for r in records],
    }
    (artifact_root / "full_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def audit_full(artifact_root: Path) -> dict:
    manifest = _load_frozen_manifest()
    full_root = artifact_root / "full"
    learner_by_id = {item["learner_id"]: item for item in manifest["learners"]}
    records = []
    for learner_id, learner in learner_by_id.items():
        for environment in manifest["environments"]:
            for seed in manifest["seeds"]:
                run_id = f"{learner_id}-{environment['environment_id']}-S{seed}"
                records.append({
                    "run_id": run_id,
                    "learner_id": learner_id,
                    "environment_id": environment["environment_id"],
                    "seed": seed,
                    **_audit_run(full_root / run_id, learner, int(seed)),
                })
    report = {
        "phase": "full_artifact_schema_provenance_audit",
        "expected_cells": manifest["matrix_cell_count"],
        "audited_cells": len(records),
        "passed_cells": sum(record["passed"] for record in records),
        "failed_cells": sum(not record["passed"] for record in records),
        "records": records,
    }
    report["passed"] = (
        report["audited_cells"] == report["expected_cells"]
        and report["failed_cells"] == 0
    )
    (artifact_root / "full_artifact_audit.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def write_report(artifact_root: Path) -> dict:
    manifest = _load_frozen_manifest()
    full_audit = audit_full(artifact_root)
    full_root = artifact_root / "full"
    rows, failures = [], []
    aggregates: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for learner in manifest["learners"]:
        for environment in manifest["environments"]:
            for seed in manifest["seeds"]:
                run_id = f"{learner['learner_id']}-{environment['environment_id']}-S{seed}"
                directory = full_root / run_id
                if not (directory / "results.json").is_file():
                    failure = json.loads((directory / "failure.json").read_text(encoding="utf-8")) if (directory / "failure.json").is_file() else {"message": "missing result"}
                    failures.append({"run_id": run_id, **failure})
                    continue
                result = json.loads((directory / "results.json").read_text(encoding="utf-8"))
                evaluation = result["evaluation"]
                generalization = evaluation["generalization"]
                dependency = result["dependency_analysis"]
                causal = result["causal_validation"]
                metric = {
                    "accuracy": generalization["task_metrics"]["accuracy"],
                    "auroc": generalization["task_metrics"]["auroc"],
                    "unseen_score": generalization.get("unseen_environment_score"),
                    "generalization_delta": generalization.get("generalization_delta"),
                    "invariance_score": evaluation["invariant_metrics"]["invariance_score"],
                    "effective_rank": evaluation["invariant_metrics"]["effective_rank"],
                    "context_leakage": dependency["context_leakage_detected"],
                    "nuisance_leakage": dependency["nuisance_leakage_detected"],
                    "shortcut_learning_score": dependency["shortcut_learning_score"],
                    "do_N_response": causal["avg_nuisance_invariance"] if causal["nuisance_interventions"] else None,
                    "do_N_missing_reason": None if causal["nuisance_interventions"] else "environment exposes no nuisance intervention",
                    "do_Z_response": causal["avg_context_invariance"] if causal["context_interventions"] else None,
                    "do_Z_missing_reason": None if causal["context_interventions"] else "environment exposes no context intervention",
                    "failure_case_count": len(causal["failure_cases"]),
                }
                rows.append({"run_id": run_id, "learner_id": learner["learner_id"], "environment_id": environment["environment_id"], "seed": seed, **metric})
                aggregates[(learner["learner_id"], environment["environment_id"])].append(metric)

    def mean(values: list[Any]) -> float | None:
        finite = [float(value) for value in values if value is not None and np.isfinite(value)]
        return float(np.mean(finite)) if finite else None

    aggregate_rows = []
    for (learner_id, environment_id), metrics in sorted(aggregates.items()):
        aggregate_rows.append({
            "learner_id": learner_id, "environment_id": environment_id, "seed_count": len(metrics),
            "mean_accuracy": mean([m["accuracy"] for m in metrics]),
            "mean_auroc": mean([m["auroc"] for m in metrics]),
            "mean_unseen_score": mean([m["unseen_score"] for m in metrics]),
            "mean_generalization_delta": mean([m["generalization_delta"] for m in metrics]),
            "mean_invariance_score": mean([m["invariance_score"] for m in metrics]),
            "context_leakage_runs": sum(bool(m["context_leakage"]) for m in metrics),
            "nuisance_leakage_runs": sum(bool(m["nuisance_leakage"]) for m in metrics),
            "failure_cases": sum(int(m["failure_case_count"]) for m in metrics),
        })
    machine = {
        "experiment_id": "EXP-LRN-001", "manifest_sha256": hashlib.sha256((EXPERIMENT_ROOT / "matrix_manifest.json").read_bytes()).hexdigest(),
        "complete_cells": len(rows), "failed_cells": len(failures),
        "rows": rows, "aggregates": aggregate_rows, "failures": failures,
        "artifact_audit_passed": full_audit["passed"],
    }
    (artifact_root / "comparison_results.json").write_text(json.dumps(machine, indent=2), encoding="utf-8")

    lines = [
        "# EXP-LRN-001 Reference Learner Comparison", "", "## Status", "",
        f"Full matrix execution complete: {len(rows)}/{manifest['matrix_cell_count']} cells; failures: {len(failures)}.", "",
        "This report compares reference learner families. It does not establish OIR-PPV or MindForge superiority.", "",
        "## Fidelity", "", "| ID | Learner | Fidelity | Deviation |", "| --- | --- | --- | --- |",
    ]
    for learner in manifest["learners"]:
        lines.append(f"| {learner['learner_id']} | {learner['display_name']} | {learner['fidelity']} | {learner['deviations']} |")
    lines += ["", "## Aggregate results", "", "| Learner | ENV | Seeds | Accuracy | AUROC | Unseen | Gen. delta | Invariance | Context leaks | Nuisance leaks |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    def fmt(value: Any) -> str:
        return "null" if value is None else f"{float(value):.4f}"
    for row in aggregate_rows:
        lines.append(f"| {row['learner_id']} | {row['environment_id']} | {row['seed_count']} | {fmt(row['mean_accuracy'])} | {fmt(row['mean_auroc'])} | {fmt(row['mean_unseen_score'])} | {fmt(row['mean_generalization_delta'])} | {fmt(row['mean_invariance_score'])} | {row['context_leakage_runs']} | {row['nuisance_leakage_runs']} |")
    lines += ["", "## Failed cells", ""]
    lines += [f"- {failure['run_id']}: {failure.get('type')}: {failure.get('message')}" for failure in failures] or ["None."]
    (EXPERIMENT_ROOT / "comparison_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return machine


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["smoke", "freeze", "full", "report", "all"])
    parser.add_argument("--output", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if args.phase in {"smoke", "all"}:
        smoke = run_smoke(output)
        if not smoke["all_cells_complete"] or not smoke["all_reproducible"]:
            raise SystemExit("Smoke gate failed")
    if args.phase in {"freeze", "all"}:
        freeze_manifest(output)
    if args.phase in {"full", "all"}:
        summary = run_full(output)
        if summary["failed_cells"]:
            print(f"Full matrix retained {summary['failed_cells']} failed cells")
    if args.phase in {"report", "all"}:
        report = write_report(output)
        if not report["artifact_audit_passed"]:
            raise SystemExit("Full artifact/schema/provenance audit failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
