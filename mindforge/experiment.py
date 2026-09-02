"""Reproducible experiment orchestration for MindForge."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import psutil
import torch

from .config import DataConfig, KernelConfig, ModelConfig, TrainingConfig
from .data import prepare_data
from .device import resolve_device
from .evaluate import evaluate_checkpoint
from .generate import generate_checkpoint
from .model import TransformerLM, parameter_count
from .tokenizer import load_tokenizer, metadata, sha256_file, train_tokenizer
from .train import train

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ArmConfig:
    """Configuration for one experiment arm (baseline or treatment)."""
    config: str
    seeds: list[int] = field(default_factory=lambda: [101, 202, 303])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ArmConfig":
        if not isinstance(value, dict):
            raise ValueError("ArmConfig must be an object")
        return cls(
            config=value["config"],
            seeds=value.get("seeds", [101, 202, 303]),
        )


@dataclass(frozen=True)
class MetricsConfig:
    """Metric selection for experiment comparison."""
    primary: str = "bits_per_byte"
    secondary: list[str] = field(default_factory=lambda: [
        "cross_entropy",
        "tokens_per_second",
        "peak_device_memory_bytes",
    ])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "MetricsConfig":
        if not isinstance(value, dict):
            raise ValueError("MetricsConfig must be an object")
        return cls(
            primary=value.get("primary", "bits_per_byte"),
            secondary=value.get("secondary", [
                "cross_entropy",
                "tokens_per_second",
                "peak_device_memory_bytes",
            ]),
        )


@dataclass(frozen=True)
class ExperimentManifest:
    """Complete experiment manifest."""
    experiment_id: str
    description: str
    baseline: ArmConfig
    treatment: ArmConfig
    metrics: MetricsConfig = field(default_factory=MetricsConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ExperimentManifest":
        source = Path(path)
        if not source.is_file():
            raise FileNotFoundError(f"missing manifest: {source}")
        try:
            value = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON in manifest {source}: {error}") from error
        if not isinstance(value, dict):
            raise ValueError("manifest must be an object")
        return cls.from_dict(value)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ExperimentManifest":
        if not isinstance(value, dict):
            raise ValueError("manifest must be an object")
        allowed = {"experiment_id", "description", "baseline", "treatment", "metrics"}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown manifest fields: {sorted(unknown)}")
        return cls(
            experiment_id=value["experiment_id"],
            description=value.get("description", ""),
            baseline=ArmConfig.from_dict(value["baseline"]),
            treatment=ArmConfig.from_dict(value["treatment"]),
            metrics=MetricsConfig.from_dict(value.get("metrics", {})),
        )

    def manifest_hash(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class RunPlan:
    """Plan for a single experiment run."""
    experiment_id: str
    arm: str  # "baseline" or "treatment"
    seed: int
    config_path: Path
    run_dir: Path


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _git_diff_hash() -> str | None:
    """Return SHA-256 of `git diff --binary HEAD` for tracked source files if dirty, else None.
    
    Only considers tracked source files (*.py, *.json, *.md, *.txt) for canonical cleanliness.
    Untracked runtime directories (runs/, .agentloop/) do not affect canonical cleanliness.
    """
    try:
        # Check only tracked source files for modifications
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "*.py", "*.json", "*.md", "*.txt"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        if not status:
            return None
        diff = subprocess.check_output(
            ["git", "diff", "--binary", "HEAD", "--", "*.py", "*.json", "*.md", "*.txt"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
        return hashlib.sha256(diff.encode()).hexdigest()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _git_untracked() -> list[str]:
    """Return list of untracked files relevant to source (py files)."""
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "*.py"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
        return [line.strip() for line in output.strip().splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def _source_tree_hash() -> str:
    """Deterministic hash of all tracked source files."""
    try:
        files = subprocess.check_output(
            ["git", "ls-files", "*.py", "*.md", "*.txt", "*.json"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip().splitlines()
        if not files:
            return "empty"
        digest = hashlib.sha256()
        for rel in sorted(files):
            full = ROOT / rel
            if full.is_file():
                content = full.read_bytes()
                digest.update(rel.encode())
                digest.update(b"\0")
                digest.update(content)
                digest.update(b"\n")
        return digest.hexdigest()
    except (FileNotFoundError, subprocess.CalledProcessError):
        # In test environments without git, compute hash directly from filesystem
        source_files = []
        for pattern in ["*.py", "*.json", "*.md", "*.txt"]:
            source_files.extend(ROOT.glob(pattern))
        source_files = [f for f in source_files if f.is_file()]
        if not source_files:
            return "empty"
        digest = hashlib.sha256()
        for full in sorted(source_files):
            rel = full.relative_to(ROOT)
            content = full.read_bytes()
            digest.update(str(rel).encode())
            digest.update(b"\0")
            digest.update(content)
            digest.update(b"\n")
        return digest.hexdigest()


def _software() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "tokenizers": __import__("tokenizers").__version__,
    }


def _hardware() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "ram_bytes": psutil.virtual_memory().total,
        "xpu_available": bool(hasattr(torch, "xpu") and torch.xpu.is_available()),
        "xpu_name": torch.xpu.get_device_name(0) if hasattr(torch, "xpu") and torch.xpu.is_available() else None,
    }


def _config_hash(config_path: str | Path) -> str:
    content = Path(config_path).read_bytes()
    return hashlib.sha256(content).hexdigest()


def _artifact_hash(path: Path) -> str:
    """SHA-256 of a file."""
    return sha256_file(path)


def _run_status(path: Path) -> str:
    run_json = path / "run.json"
    if not run_json.is_file():
        return "MISSING"
    try:
        data = json.loads(run_json.read_text(encoding="utf-8"))
        return data.get("status", "UNKNOWN")
    except (OSError, json.JSONDecodeError):
        return "CORRUPT"


def validate_manifest(manifest_path: str | Path, *, strict: bool = False) -> dict[str, Any]:
    """Validate manifest structure and referenced configs."""
    manifest = ExperimentManifest.load(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    for arm_name, arm in [("baseline", manifest.baseline), ("treatment", manifest.treatment)]:
        cfg_path = Path(arm.config)
        if not cfg_path.is_file():
            errors.append(f"{arm_name}: config file not found: {cfg_path}")
            continue
        try:
            KernelConfig.load(cfg_path)
        except Exception as error:
            errors.append(f"{arm_name}: invalid config {cfg_path}: {error}")

    if manifest.baseline.seeds != manifest.treatment.seeds:
        errors.append("baseline and treatment seeds must be identical for paired comparison")

    if strict:
        dirty_hash = _git_diff_hash()
        if dirty_hash:
            errors.append(f"working tree is dirty (diff hash: {dirty_hash}); commit or use --allow-dirty")

    return {
        "manifest_hash": manifest.manifest_hash(),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def _load_kernel_config(config_path: str | Path, seed: int, run_dir: Path) -> KernelConfig:
    cfg = KernelConfig.load(config_path)
    # Create a new KernelConfig with updated seed and run_dir
    return KernelConfig(
        data=DataConfig(
            train_tokens=cfg.data.train_tokens,
            validation_tokens=cfg.data.validation_tokens,
            tokenizer=cfg.data.tokenizer,
            run_dir=str(run_dir),
        ),
        model=cfg.model,
        training=TrainingConfig(
            steps=cfg.training.steps,
            micro_batch=cfg.training.micro_batch,
            accumulation=cfg.training.accumulation,
            learning_rate=cfg.training.learning_rate,
            weight_decay=cfg.training.weight_decay,
            gradient_clip=cfg.training.gradient_clip,
            warmup_fraction=cfg.training.warmup_fraction,
            min_lr_fraction=cfg.training.min_lr_fraction,
            eval_interval=cfg.training.eval_interval,
            checkpoint_interval=cfg.training.checkpoint_interval,
            eval_windows=cfg.training.eval_windows,
            seed=seed,
            device=cfg.training.device,
            dtype=cfg.training.dtype,
        ),
    )


def execute_runs(
    manifest_path: str | Path,
    *,
    allow_dirty: bool = False,
    resume: bool = False,
    force_new: bool = False,
) -> dict[str, Any]:
    """Execute all runs defined by the manifest."""
    manifest = ExperimentManifest.load(manifest_path)
    validation = validate_manifest(manifest_path, strict=not allow_dirty)
    if not validation["valid"]:
        raise ValueError("Manifest validation failed: " + "; ".join(validation["errors"]))

    exp_dir = ROOT / "runs" / manifest.experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)

    # Write manifest copy into experiment directory
    manifest.save(exp_dir / "manifest.json")

    git_commit = _git_commit()
    diff_hash = _git_diff_hash()
    untracked = _git_untracked()
    source_hash = _source_tree_hash()

    provenance = {
        "git_commit": git_commit,
        "working_tree_clean": diff_hash is None,
        "working_tree_diff_hash": diff_hash,
        "untracked_source_files": untracked,
        "source_tree_hash": source_hash,
        "manifest_hash": validation["manifest_hash"],
        "software": _software(),
        "hardware": _hardware(),
        "kernel_checkpoint_format_version": 1,
    }

    runs_plan: list[RunPlan] = []
    for arm_name, arm in [("baseline", manifest.baseline), ("treatment", manifest.treatment)]:
        for seed in arm.seeds:
            run_dir = exp_dir / arm_name / f"seed-{seed}"
            runs_plan.append(RunPlan(
                experiment_id=manifest.experiment_id,
                arm=arm_name,
                seed=seed,
                config_path=Path(arm.config),
                run_dir=run_dir,
            ))

    executed = 0
    skipped = 0
    failed = 0

    for plan in runs_plan:
        run_dir = plan.run_dir
        if run_dir.exists():
            status = _run_status(run_dir)
            if status == "PASS" and not force_new:
                skipped += 1
                continue
            if status in {"PASS", "RUNNING"} and resume:
                # Check if we can resume from latest checkpoint
                checkpoints = sorted(run_dir.glob("checkpoint-step-*.pt"))
                if checkpoints:
                    # Would resume - but for Phase 2 we re-run for clean evidence
                    pass
            if not force_new and not resume:
                raise RuntimeError(
                    f"Run directory exists for {manifest.experiment_id}/{plan.arm}/seed-{plan.seed}. "
                    "Use --resume or --force-new-id to override."
                )

        # Clean up any partial run
        if run_dir.exists():
            shutil.rmtree(run_dir)

        run_dir.mkdir(parents=True, exist_ok=True)

        try:
            kernel_cfg = _load_kernel_config(plan.config_path, plan.seed, run_dir)
            result = train(kernel_cfg)
            executed += 1
        except Exception as error:
            failed += 1
            error_record = {
                "experiment_id": manifest.experiment_id,
                "arm": plan.arm,
                "seed": plan.seed,
                "status": "FAIL",
                "error": str(error),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            (run_dir / "run.json").write_text(json.dumps(error_record, indent=2) + "\n", encoding="utf-8")

    # Write experiment-level provenance
    (exp_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    return {
        "experiment_id": manifest.experiment_id,
        "status": "PASS" if failed == 0 else "FAIL",
        "total_runs": len(runs_plan),
        "executed": executed,
        "skipped": skipped,
        "failed": failed,
    }


def _discover_runs(manifest: ExperimentManifest) -> dict[str, dict[int, Path]]:
    """Discover all run directories for an experiment."""
    exp_dir = ROOT / "runs" / manifest.experiment_id
    runs: dict[str, dict[int, Path]] = {"baseline": {}, "treatment": {}}
    for arm_name in ("baseline", "treatment"):
        arm_dir = exp_dir / arm_name
        if not arm_dir.is_dir():
            continue
        for seed_dir in arm_dir.iterdir():
            if seed_dir.is_dir() and seed_dir.name.startswith("seed-"):
                try:
                    seed = int(seed_dir.name.split("-")[1])
                    runs[arm_name][seed] = seed_dir
                except (IndexError, ValueError):
                    continue
    return runs


def _extract_final_metrics(run_dir: Path) -> dict[str, Any] | None:
    """Extract final evaluation metrics from a completed run."""
    run_json = run_dir / "run.json"
    if not run_json.is_file():
        return None
    try:
        data = json.loads(run_json.read_text(encoding="utf-8"))
        if data.get("status") != "PASS":
            return None
        final_eval = data.get("final_evaluation", {})
        if not final_eval or final_eval.get("status") != "PASS":
            return None
        return {
            "seed": data.get("seed"),
            "bits_per_byte": final_eval.get("bits_per_byte"),
            "cross_entropy": final_eval.get("cross_entropy"),
            "bits_per_token": final_eval.get("bits_per_token"),
            "wall_clock_seconds": data.get("wall_clock_seconds"),
            "peak_device_memory_bytes": data.get("peak_device_memory_bytes"),
            "checkpoint_path": str(sorted(run_dir.glob("checkpoint-step-*.pt"))[-1]) if list(run_dir.glob("checkpoint-step-*.pt")) else None,
            "run_json_hash": _artifact_hash(run_json),
            "metrics_jsonl_hash": _artifact_hash(run_dir / "metrics.jsonl") if (run_dir / "metrics.jsonl").exists() else None,
            "checkpoint_hash": _artifact_hash(Path(data["checkpoint"]["path"])) if data.get("checkpoint") else None,
        }
    except (OSError, json.JSONDecodeError, KeyError, IndexError):
        return None


def _aggregate_arm(metrics: list[dict[str, Any]], metric_name: str) -> dict[str, Any] | None:
    """Compute mean/median/std for a list of metric values."""
    values = [m.get(metric_name) for m in metrics if m.get(metric_name) is not None and np.isfinite(m.get(metric_name))]
    if not values:
        return None
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "values": values,
        "count": len(values),
    }


def _paired_effects(baseline: list[dict[str, Any]], treatment: list[dict[str, Any]], metric: str) -> list[dict[str, Any]]:
    """Compute paired effects for aligned seeds."""
    baseline_by_seed = {m["seed"]: m for m in baseline if m.get("seed") is not None}
    treatment_by_seed = {m["seed"]: m for m in treatment if m.get("seed") is not None}
    aligned = []
    for seed in sorted(set(baseline_by_seed) & set(treatment_by_seed)):
        b = baseline_by_seed[seed]
        t = treatment_by_seed[seed]
        if b.get(metric) is None or t.get(metric) is None:
            continue
        b_val = b[metric]
        t_val = t[metric]
        if not (np.isfinite(b_val) and np.isfinite(t_val)):
            continue
        abs_effect = t_val - b_val
        rel_effect = abs_effect / b_val if b_val != 0 else float("inf")
        aligned.append({
            "seed": seed,
            "baseline": b_val,
            "treatment": t_val,
            "absolute_effect": abs_effect,
            "relative_effect": rel_effect,
        })
    return aligned


def summarize(manifest_path: str | Path) -> dict[str, Any]:
    """Aggregate results from completed experiment runs."""
    manifest = ExperimentManifest.load(manifest_path)
    runs = _discover_runs(manifest)

    primary = manifest.metrics.primary

    baseline_metrics = []
    treatment_metrics = []

    missing = []
    for seed in manifest.baseline.seeds:
        run_dir = runs["baseline"].get(seed)
        if not run_dir:
            missing.append(f"baseline/seed-{seed}")
            continue
        metrics = _extract_final_metrics(run_dir)
        if metrics is None:
            missing.append(f"baseline/seed-{seed} (incomplete or failed)")
            continue
        baseline_metrics.append(metrics)

    for seed in manifest.treatment.seeds:
        run_dir = runs["treatment"].get(seed)
        if not run_dir:
            missing.append(f"treatment/seed-{seed}")
            continue
        metrics = _extract_final_metrics(run_dir)
        if metrics is None:
            missing.append(f"treatment/seed-{seed} (incomplete or failed)")
            continue
        treatment_metrics.append(metrics)

    if missing:
        return {
            "experiment_id": manifest.experiment_id,
            "status": "INCOMPLETE",
            "missing": missing,
            "manifest_hash": manifest.manifest_hash(),
        }

    # Aggregate primary metric
    baseline_primary = _aggregate_arm(baseline_metrics, primary)
    treatment_primary = _aggregate_arm(treatment_metrics, primary)

    # Paired effects on primary metric
    paired = _paired_effects(baseline_metrics, treatment_metrics, primary)
    paired_effects_agg = _aggregate_arm(
        [{"seed": p["seed"], "value": p["absolute_effect"]} for p in paired],
        "value",
    )
    paired_rel_agg = _aggregate_arm(
        [{"seed": p["seed"], "value": p["relative_effect"]} for p in paired],
        "value",
    )

    # Secondary metrics
    secondary: dict[str, dict[str, Any]] = {}
    for metric in manifest.metrics.secondary:
        b_agg = _aggregate_arm(baseline_metrics, metric)
        t_agg = _aggregate_arm(treatment_metrics, metric)
        if b_agg or t_agg:
            secondary[metric] = {
                "baseline": b_agg,
                "treatment": t_agg,
            }

    # Resource comparison
    resources = {}
    for metric in ["wall_clock_seconds", "peak_device_memory_bytes", "tokens_per_second"]:
        b_agg = _aggregate_arm(baseline_metrics, metric)
        t_agg = _aggregate_arm(treatment_metrics, metric)
        if b_agg and t_agg:
            resources[metric] = {
                "baseline": b_agg,
                "treatment": t_agg,
                "delta_mean": t_agg["mean"] - b_agg["mean"],
                "delta_median": t_agg["median"] - b_agg["median"],
            }

    # Build summary
    summary = {
        "experiment_id": manifest.experiment_id,
        "status": "PASS",
        "manifest_hash": manifest.manifest_hash(),
        "baseline": {
            "seeds": [m["seed"] for m in baseline_metrics],
            "primary_metric": primary,
            "primary": baseline_primary,
        },
        "treatment": {
            "seeds": [m["seed"] for m in treatment_metrics],
            "primary_metric": primary,
            "primary": treatment_primary,
        },
        "paired_effects": {
            "primary_metric": primary,
            "seeds": paired,
            "absolute": paired_effects_agg,
            "relative": paired_rel_agg,
        },
        "secondary_metrics": secondary,
        "resources": resources,
    }

    # Write summary
    exp_dir = ROOT / "runs" / manifest.experiment_id
    (exp_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Write human-readable comparison
    _write_comparison_md(summary, manifest)

    return summary


def check_regression(manifest_path: str | Path, *, thresholds: dict[str, float] | None = None) -> dict[str, Any]:
    """Check regression thresholds against experiment summary."""
    manifest = ExperimentManifest.load(manifest_path)
    summary = summarize(manifest_path)

    if summary.get("status") != "PASS":
        return {"status": "FAIL", "reason": f"Experiment not complete: {summary.get('status')}"}

    if thresholds is None:
        thresholds = {
            "baseline_bpb_cv_max": 0.10,  # coefficient of variation <= 10%
            "all_finite": True,
            "no_missing": True,
        }

    results = {"status": "PASS", "checks": {}}

    # Baseline repeatability
    baseline_primary = summary["baseline"].get("primary")
    if baseline_primary and baseline_primary.get("mean", 0) != 0:
        cv = baseline_primary.get("std", 0) / baseline_primary.get("mean", 1)
        passed = cv <= thresholds.get("baseline_bpb_cv_max", 0.10)
        results["checks"]["baseline_bpb_cv"] = {
            "value": cv,
            "threshold": thresholds.get("baseline_bpb_cv_max", 0.10),
            "passed": passed,
        }
        if not passed:
            results["status"] = "REVISE"

    # All finite
    if thresholds.get("all_finite", True):
        all_finite = True
        for arm in ["baseline", "treatment"]:
            primary = summary[arm].get("primary")
            if primary:
                for val in primary.get("values", []):
                    if not np.isfinite(val):
                        all_finite = False
        results["checks"]["all_finite"] = {"passed": all_finite}
        if not all_finite:
            results["status"] = "REVISE"

    # No missing (already checked in summarize)
    results["checks"]["no_missing"] = {"passed": summary.get("status") == "PASS"}

    return results


def _write_comparison_md(summary: dict[str, Any], manifest: ExperimentManifest) -> str:
    """Generate a human-readable comparison report."""
    lines = [
        f"# Experiment Comparison: {manifest.experiment_id}",
        "",
        f"Primary metric: {manifest.metrics.primary}",
        f"Seeds: {manifest.baseline.seeds}",
        "",
        "## Baseline",
        f"- Mean {manifest.metrics.primary}: {summary['baseline']['primary']['mean']:.6f}" if summary['baseline'].get('primary') else "- No data",
        f"- Median: {summary['baseline']['primary']['median']:.6f}" if summary['baseline'].get('primary') else "",
        f"- Std: {summary['baseline']['primary']['std']:.6f}" if summary['baseline'].get('primary') else "",
        "",
        "## Treatment",
        f"- Mean {manifest.metrics.primary}: {summary['treatment']['primary']['mean']:.6f}" if summary['treatment'].get('primary') else "- No data",
        f"- Median: {summary['treatment']['primary']['median']:.6f}" if summary['treatment'].get('primary') else "",
        f"- Std: {summary['treatment']['primary']['std']:.6f}" if summary['treatment'].get('primary') else "",
        "",
        "## Paired Effects",
    ]
    for p in summary.get("paired_effects", {}).get("seeds", []):
        lines.append(f"- Seed {p['seed']}: baseline={p['baseline']:.6f}, treatment={p['treatment']:.6f}, "
                     f"abs={p['absolute_effect']:.6f}, rel={p['relative_effect']:.4%}")

    if summary.get("resources"):
        lines.extend(["", "## Resources"])
        for metric, data in summary["resources"].items():
            lines.append(f"- {metric}: baseline_mean={data['baseline']['mean']:.2f}, "
                         f"treatment_mean={data['treatment']['mean']:.2f}, "
                         f"delta={data['delta_mean']:.2f}")

    text = "\n".join(lines) + "\n"
    exp_dir = ROOT / "runs" / manifest.experiment_id
    md_path = exp_dir / "comparison.md"
    md_path.write_text(text, encoding="utf-8")
    return str(md_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="MindForge experiment orchestration")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate manifest and configs")
    validate.add_argument("manifest", help="Path to experiment manifest")
    validate.add_argument("--strict", action="store_true", help="Require clean working tree")

    run = sub.add_parser("run", help="Execute experiment runs")
    run.add_argument("manifest", help="Path to experiment manifest")
    run.add_argument("--allow-dirty", action="store_true", help="Allow dirty working tree")
    run.add_argument("--resume", action="store_true", help="Resume incomplete runs")
    run.add_argument("--force-new-id", action="store_true", help="Force new run IDs (overwrites)")

    summarize_cmd = sub.add_parser("summarize", help="Aggregate and compare experiment results")
    summarize_cmd.add_argument("manifest", help="Path to experiment manifest")
    summarize_cmd.add_argument("--output", help="Output JSON path")

    check = sub.add_parser("check", help="Check regression thresholds")
    check.add_argument("manifest", help="Path to experiment manifest")
    check.add_argument("--baseline-bpb-cv-max", type=float, default=0.10)

    args = parser.parse_args()

    if args.command == "validate":
        result = validate_manifest(args.manifest, strict=args.strict)
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1

    if args.command == "run":
        result = execute_runs(args.manifest, allow_dirty=args.allow_dirty, resume=args.resume, force_new=args.force_new_id)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1

    if args.command == "summarize":
        result = summarize(args.manifest)
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if result.get("status") == "PASS" else 1

    if args.command == "check":
        thresholds = {"baseline_bpb_cv_max": args.baseline_bpb_cv_max}
        result = check_regression(args.manifest, thresholds=thresholds)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
