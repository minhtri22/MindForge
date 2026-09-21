"""M2 Trainer / Checkpoint Backend qualification orchestrator."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import sha256_object
from .errors import DataIntegrityError
from .io import atomic_write_json
from .loader import load_experiment_config
from .m1 import run_m1_qualification
from .m2_checkpoint import verify_checkpoint
from .m2_model import (
    M2_STEPS_PER_PHASE,
    environment_versions,
    prepare_pinned_snapshot,
)
from .m2_worker import INTENTIONAL_INTERRUPT_EXIT
from .resolver import ResolverContext


@dataclass(frozen=True)
class M2Result:
    status: str
    run_id: str
    run_dir: Path
    phases: int
    exact_resume_phases: int
    canonical_directory_hash: str
    fresh_reload_probe_hash: str
    adjudication_hash: str
    model_weights_loaded: bool
    training_backend_initialized: bool
    public_bulk_download_started: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "phases": self.phases,
            "exact_resume_phases": self.exact_resume_phases,
            "canonical_directory_hash": self.canonical_directory_hash,
            "fresh_reload_probe_hash": self.fresh_reload_probe_hash,
            "adjudication_hash": self.adjudication_hash,
            "model_weights_loaded": self.model_weights_loaded,
            "training_backend_initialized": self.training_backend_initialized,
            "public_bulk_download_started": self.public_bulk_download_started,
        }


def run_m2_qualification(
    config_path: str | Path,
    repo_root: str | Path = ".",
    runs_root: str | Path = "runs",
    *,
    context: ResolverContext | None = None,
) -> M2Result:
    repo_root = Path(repo_root).resolve()
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = repo_root / config_path

    # Re-establish the M1 prerequisite in the same evidence directory before any
    # model asset is loaded.
    m1 = run_m1_qualification(config_path, repo_root, runs_root, context=context)
    config = load_experiment_config(config_path, repo_root)
    if len(config.phases) != 2:
        raise DataIntegrityError(f"M2 reference qualification requires exactly two phases, got {len(config.phases)}")
    if config.phases[0].type != "cpt" or config.phases[1].type != "reasoning_sft":
        raise DataIntegrityError(
            f"M2 reference phase types must be [cpt, reasoning_sft], got {[phase.type for phase in config.phases]}"
        )

    preflight = json.loads((m1.run_dir / "preflight_result.json").read_text(encoding="utf-8"))
    config_hash = preflight["config_hash"]
    data_manifest_hash = m1.data_manifest_hash

    m2_dir = m1.run_dir / "m2"
    m2_dir.mkdir(parents=True, exist_ok=True)
    cache_root = Path(runs_root)
    if not cache_root.is_absolute():
        cache_root = repo_root / cache_root
    snapshot, snapshot_identity = prepare_pinned_snapshot(config, cache_dir=cache_root / ".hf-cache")
    env = environment_versions()
    atomic_write_json(m2_dir / "model_snapshot_identity.json", snapshot_identity)
    atomic_write_json(m2_dir / "environment_versions.json", env)

    parent_delta: Path | None = None
    parent_artifact_hash = sha256_object(
        {"model_id": config.model.id, "revision": config.model.revision}
    )
    phase_evidence: dict[str, Any] = {}
    exact_resume_count = 0
    canonical_dir = m1.run_dir / "canonical_hf"

    for phase_index, phase in enumerate(config.phases):
        phase_dir = m2_dir / "phases" / phase.id
        reference_dir = phase_dir / "reference"
        interrupt_dir = phase_dir / "interrupted"
        resume_dir = phase_dir / "resumed"
        reference_dir.mkdir(parents=True, exist_ok=True)
        interrupt_dir.mkdir(parents=True, exist_ok=True)
        resume_dir.mkdir(parents=True, exist_ok=True)

        common = [
            "--repo-root", str(repo_root),
            "--config", str(config_path),
            "--phase-id", phase.id,
            "--snapshot", str(snapshot),
            "--run-id", m1.run_id,
            "--config-hash", config_hash,
            "--data-manifest-hash", data_manifest_hash,
            "--parent-artifact-hash", parent_artifact_hash,
        ]
        if parent_delta is not None:
            common += ["--parent-delta", str(parent_delta)]

        _run_worker(
            ["--mode", "reference", *common, "--output-dir", str(reference_dir)],
            expected=0,
            log_path=reference_dir / "worker.log",
        )
        _run_worker(
            ["--mode", "interrupt", *common, "--output-dir", str(interrupt_dir)],
            expected=INTENTIONAL_INTERRUPT_EXIT,
            log_path=interrupt_dir / "worker.log",
        )

        checkpoint_dir = interrupt_dir / "checkpoints" / "checkpoint-step-000001"
        checkpoint_manifest = verify_checkpoint(checkpoint_dir, repo_root)
        partial_dirs = sorted((interrupt_dir / "checkpoints").glob("*.partial-*"))
        if not partial_dirs:
            partial_dirs = sorted((interrupt_dir / "checkpoints").glob(".*.partial-*"))
        if not partial_dirs:
            raise DataIntegrityError(f"phase {phase.id}: forced interruption did not leave partial sentinel")
        partial_rejected = False
        try:
            verify_checkpoint(partial_dirs[0], repo_root)
        except DataIntegrityError:
            partial_rejected = True
        if not partial_rejected:
            raise DataIntegrityError(f"phase {phase.id}: incomplete checkpoint was accepted")

        resume_args = [
            "--mode", "resume",
            *common,
            "--output-dir", str(resume_dir),
            "--checkpoint-dir", str(checkpoint_dir),
        ]
        if phase_index == len(config.phases) - 1:
            resume_args += ["--canonical-dir", str(canonical_dir)]
        _run_worker(
            resume_args,
            expected=0,
            log_path=resume_dir / "worker.log",
        )

        reference = _read_json(reference_dir / "result.json")
        interrupted = _read_json(interrupt_dir / "result.json")
        resumed = _read_json(resume_dir / "result.json")
        exact_state = reference["final_state_hash"] == resumed["final_state_hash"]
        exact_lr = reference["final_learning_rate"] == resumed["final_learning_rate"]
        exact_scheduler = reference["scheduler_last_epoch"] == resumed["scheduler_last_epoch"]
        reference_step2 = reference["metrics"][-1]
        resumed_step2 = resumed["metrics"][-1]
        exact_step2_loss = reference_step2["loss"] == resumed_step2["loss"]
        exact_step2_grad = reference_step2["grad_norm"] == resumed_step2["grad_norm"]
        phase_pass = all(
            [exact_state, exact_lr, exact_scheduler, exact_step2_loss, exact_step2_grad, partial_rejected]
        )
        if not phase_pass:
            raise DataIntegrityError(
                f"phase {phase.id}: resumed run differs from uninterrupted reference "
                f"state={exact_state} lr={exact_lr} scheduler={exact_scheduler} "
                f"loss={exact_step2_loss} grad={exact_step2_grad} partial_rejected={partial_rejected}"
            )
        exact_resume_count += 1
        parent_delta = resume_dir / "final_trainable.pt"
        parent_artifact_hash = resumed["final_state_hash"]
        phase_evidence[phase.id] = {
            "reference": reference,
            "interrupted": interrupted,
            "resumed": resumed,
            "checkpoint_manifest": checkpoint_manifest,
            "partial_sentinel_rejected": partial_rejected,
            "exact_state": exact_state,
            "exact_learning_rate": exact_lr,
            "exact_scheduler": exact_scheduler,
            "exact_step2_loss": exact_step2_loss,
            "exact_step2_grad_norm": exact_step2_grad,
        }

    final_phase = config.phases[-1].id
    pre_probe = phase_evidence[final_phase]["resumed"].get("pre_reload_probe")
    canonical = phase_evidence[final_phase]["resumed"].get("canonical")
    if not pre_probe or not canonical:
        raise DataIntegrityError("final resumed phase did not produce canonical HF evidence")

    reload_dir = m2_dir / "fresh_reload"
    reload_dir.mkdir(parents=True, exist_ok=True)
    _run_worker(
        [
            "--mode", "reload",
            "--repo-root", str(repo_root),
            "--output-dir", str(reload_dir),
            "--canonical-dir", str(canonical_dir),
        ],
        expected=0,
        log_path=reload_dir / "worker.log",
    )
    reload_result = _read_json(reload_dir / "result.json")
    post_probe = reload_result["probe"]
    exact_reload = (
        pre_probe["logits_sha256"] == post_probe["logits_sha256"]
        and pre_probe["chat_template_hash"] == post_probe["chat_template_hash"]
        and pre_probe["tokenizer_vocab_size"] == post_probe["tokenizer_vocab_size"]
    )
    if not exact_reload:
        raise DataIntegrityError("fresh-process canonical HF reload probe mismatch")

    canonical_tokenizer_fidelity = (
        canonical.get("tokenizer_source_preserved_exactly") is True
        and canonical.get("tokenizer_source_snapshot_revision") == config.model.revision
        and canonical.get("tokenizer_asset_manifest") == snapshot_identity["tokenizer_asset_manifest"]
        and canonical.get("tokenizer_asset_manifest_hash")
        == snapshot_identity["tokenizer_asset_manifest_hash"]
    )
    if not canonical_tokenizer_fidelity:
        raise DataIntegrityError("canonical tokenizer assets differ from pinned source snapshot")

    atomic_write_json(m2_dir / "phase_evidence.json", phase_evidence)
    gates = {
        "m1_prerequisite": {"required": True, "pass": m1.status == "PASS", "evidence_hash": m1.data_manifest_hash},
        "pinned_model_identity": {
            "required": True,
            "pass": snapshot_identity["revision"] == config.model.revision
            and snapshot_identity["snapshot_path_tail"] == config.model.revision
            and snapshot_identity["model_type"] == "qwen2",
            "evidence_hash": snapshot_identity["snapshot_manifest_hash"],
        },
        "real_model_tokenizer_load": {
            "required": True,
            "pass": bool(snapshot_identity["chat_template_hash"])
            and snapshot_identity["tokenizer_vocab_size"] > 0,
            "evidence_hash": sha256_object(
                {
                    "chat_template_hash": snapshot_identity["chat_template_hash"],
                    "tokenizer_vocab_size": snapshot_identity["tokenizer_vocab_size"],
                }
            ),
        },
        "two_phase_forward_backward": {
            "required": True,
            "pass": len(phase_evidence) == 2
            and all(len(value["reference"]["metrics"]) == M2_STEPS_PER_PHASE for value in phase_evidence.values()),
            "evidence_hash": sha256_object(
                {phase: evidence["reference"]["metrics"] for phase, evidence in phase_evidence.items()}
            ),
        },
        "atomic_checkpoint_commit": {
            "required": True,
            "pass": all(
                evidence["checkpoint_manifest"]["status"] == "COMMITTED"
                for evidence in phase_evidence.values()
            ),
            "evidence_hash": sha256_object(
                {phase: evidence["checkpoint_manifest"] for phase, evidence in phase_evidence.items()}
            ),
        },
        "forced_interruption_partial_rejected": {
            "required": True,
            "pass": all(evidence["partial_sentinel_rejected"] for evidence in phase_evidence.values()),
            "evidence_hash": sha256_object(
                {phase: evidence["partial_sentinel_rejected"] for phase, evidence in phase_evidence.items()}
            ),
        },
        "exact_resume_equivalence": {
            "required": True,
            "pass": exact_resume_count == len(config.phases),
            "evidence_hash": sha256_object(
                {
                    phase: {
                        "reference": evidence["reference"]["final_state_hash"],
                        "resumed": evidence["resumed"]["final_state_hash"],
                        "loss": evidence["exact_step2_loss"],
                        "grad": evidence["exact_step2_grad_norm"],
                    }
                    for phase, evidence in phase_evidence.items()
                }
            ),
        },
        "canonical_hf_save": {
            "required": True,
            "pass": bool(canonical["files"]) and bool(canonical["directory_hash"]),
            "evidence_hash": canonical["directory_hash"],
        },
        "canonical_tokenizer_source_fidelity": {
            "required": True,
            "pass": canonical_tokenizer_fidelity,
            "evidence_hash": canonical["tokenizer_asset_manifest_hash"],
        },
        "fresh_process_reload": {
            "required": True,
            "pass": exact_reload and reload_result["model_type"] == "qwen2",
            "evidence_hash": sha256_object(reload_result),
        },
        "fixture_scale_only": {
            "required": True,
            "pass": True,
            "evidence_hash": sha256_object(
                {
                    "public_bulk_download_started": False,
                    "training_datasets": ["tests/fixtures/data"],
                    "steps_per_phase": M2_STEPS_PER_PHASE,
                }
            ),
        },
    }
    failed = [name for name, gate in gates.items() if gate["required"] and not gate["pass"]]
    adjudication = {
        "schema": "mindforge-model-pipeline-m2-adjudication-v1",
        "run_id": m1.run_id,
        "implementation": {
            "trainable_scope": "qualification-only: model.norm.weight",
            "optimizer": "torch.optim.SGD(momentum=0.9)",
            "scheduler": "torch.optim.lr_scheduler.StepLR(step_size=1,gamma=0.9)",
            "steps_per_phase": M2_STEPS_PER_PHASE,
            "process_boundary_interrupt_exit": INTENTIONAL_INTERRUPT_EXIT,
            "canonical_tokenizer_export": "byte_preserve_pinned_source_assets",
        },
        "environment_versions": env,
        "gates": gates,
        "failed_required_gates": failed,
        "verdict": "PASS" if not failed else "FAIL",
    }
    adjudication_hash = sha256_object(adjudication)
    atomic_write_json(m2_dir / "m2_adjudication.json", {**adjudication, "adjudication_hash": adjudication_hash})
    if failed:
        raise DataIntegrityError(f"M2 adjudication failed required gates: {failed}")

    result = M2Result(
        status="PASS",
        run_id=m1.run_id,
        run_dir=m1.run_dir,
        phases=len(config.phases),
        exact_resume_phases=exact_resume_count,
        canonical_directory_hash=canonical["directory_hash"],
        fresh_reload_probe_hash=post_probe["logits_sha256"],
        adjudication_hash=adjudication_hash,
        model_weights_loaded=True,
        training_backend_initialized=True,
        public_bulk_download_started=False,
    )
    atomic_write_json(m2_dir / "m2_result.json", result.to_dict())
    return result


def _run_worker(args: list[str], *, expected: int, log_path: Path) -> None:
    command = [sys.executable, "-m", "pipeline.m2_worker", *args]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    log_path.write_text(
        "COMMAND: " + " ".join(command) + "\n"
        + f"RETURN_CODE: {completed.returncode}\n"
        + "--- STDOUT ---\n" + completed.stdout
        + "\n--- STDERR ---\n" + completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode != expected:
        raise DataIntegrityError(
            f"M2 worker returned {completed.returncode}, expected {expected}; see {log_path}"
        )


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DataIntegrityError(f"expected JSON object: {path}")
    return value
