"""M0 zero-training preflight compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .baseline import BaselineRegistry
from .canonical import dump_canonical_yaml, sha256_object
from .freshness import FreshnessRegistry
from .io import atomic_write_json, atomic_write_text
from .loader import load_experiment_config, load_model_profile
from .models import PhaseState, RunState
from .resolver import ResolverContext, resolve_config
from .semantic import validate_semantics
from .state import RunMachine


@dataclass(frozen=True)
class PreflightResult:
    status: str
    run_id: str
    run_dir: Path
    config_hash: str
    model_profile_hash: str
    baseline_registry_hash: str
    preflight_contract_hash: str
    run_state: RunState

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "config_hash": self.config_hash,
            "model_profile_hash": self.model_profile_hash,
            "baseline_registry_hash": self.baseline_registry_hash,
            "preflight_contract_hash": self.preflight_contract_hash,
            "run_state": self.run_state.value,
        }


def run_preflight(
    config_path: str | Path,
    repo_root: str | Path = ".",
    runs_root: str | Path = "runs",
    context: ResolverContext | None = None,
) -> PreflightResult:
    repo_root = Path(repo_root).resolve()
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()
    config = load_experiment_config(config_path, repo_root)
    profile = load_model_profile(config, repo_root)
    validate_semantics(config, profile, repo_root)

    resolved, resolution_evidence = resolve_config(config, profile, repo_root, context=context)
    config_hash = sha256_object(resolved)
    profile_hash = sha256_object(profile)
    baselines = BaselineRegistry.compile(config)
    freshness = FreshnessRegistry.from_config(config, _fixture_freshness(config.fixture_set, repo_root))

    run_id = f"{_slug(config.experiment_id)}-{config_hash[:12]}"
    runs_root_path = Path(runs_root)
    if not runs_root_path.is_absolute():
        runs_root_path = repo_root / runs_root_path
    run_dir = runs_root_path / run_id
    frozen = run_dir / "frozen"

    machine = RunMachine()
    machine.advance(RunState.PREPARED)

    phase_contracts = []
    for phase_raw in resolved["phases"]:
        phase_contracts.append(
            {
                "phase_id": phase_raw["id"],
                "parent_ref": phase_raw["parent_ref"],
                "phase_config_hash": sha256_object(phase_raw),
                "token_stream_hash": sha256_object(phase_raw["token_stream"]),
                "checkpoint_selection_hash": sha256_object(phase_raw["checkpoint_selection"]),
                "phase_resource_hash": sha256_object(phase_raw["resolved_resource"]),
                "state": PhaseState.PLANNED.value,
            }
        )

    preflight_contract = {
        "schema": "mindforge-model-pipeline-m0-preflight-v1",
        "run_id": run_id,
        "run_class": config.run_class.value,
        "config_hash": config_hash,
        "model_profile_hash": profile_hash,
        "baseline_registry_hash": baselines.sha256,
        "resolution_evidence": resolution_evidence,
        "freshness_registry": {
            "seed_ids": sorted(freshness.seed_ids),
            "dataset_ids": sorted(freshness.dataset_ids),
            "fixture_set_ids": sorted(freshness.fixture_set_ids),
        },
        "phase_contracts": phase_contracts,
        "zero_training_assertions": {
            "model_weights_loaded": False,
            "training_backend_initialized": False,
            "dataset_download_started": False,
            "fresh_evidence_accessed": False,
        },
    }
    contract_hash = sha256_object(preflight_contract)

    atomic_write_text(frozen / "run_config.yaml", dump_canonical_yaml(resolved))
    atomic_write_text(frozen / "model_profile.yaml", dump_canonical_yaml(profile))
    atomic_write_json(
        frozen / "baseline_registry.json",
        {"sha256": baselines.sha256, "entries": list(baselines.entries)},
    )
    atomic_write_json(frozen / "preflight_contract.json", preflight_contract)
    atomic_write_text(frozen / "preflight_contract.sha256", contract_hash + "\n")

    machine.advance(RunState.PREFLIGHT_PASS)
    result = PreflightResult(
        status="PASS",
        run_id=run_id,
        run_dir=run_dir,
        config_hash=config_hash,
        model_profile_hash=profile_hash,
        baseline_registry_hash=baselines.sha256,
        preflight_contract_hash=contract_hash,
        run_state=machine.state,
    )
    atomic_write_json(run_dir / "preflight_result.json", result.to_dict())
    return result


def _fixture_freshness(fixture_set: str, repo_root: Path) -> str | None:
    if not fixture_set.startswith("tests/"):
        return None
    import json

    path = repo_root / fixture_set
    manifest = path / "manifest.json" if path.is_dir() else path
    if not manifest.is_file():
        return None
    value = json.loads(manifest.read_text(encoding="utf-8"))
    return value.get("freshness_class")


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe or "run"
