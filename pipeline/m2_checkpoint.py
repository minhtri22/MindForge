"""Atomic M2 recoverable checkpoint implementation."""

from __future__ import annotations

import json
import os
import pickle
import random
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch
from jsonschema import Draft202012Validator

from .canonical import sha256_file, sha256_object
from .errors import DataIntegrityError
from .loader import validate_mapping


def trainable_state(model: torch.nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: parameter.detach().cpu().clone()
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    }


def trainable_state_hash(model: torch.nn.Module) -> str:
    entries = []
    for name, tensor in sorted(trainable_state(model).items()):
        entries.append(
            {
                "name": name,
                "dtype": str(tensor.dtype),
                "shape": list(tensor.shape),
                "sha256": _tensor_sha256(tensor),
            }
        )
    return sha256_object(entries)


def apply_trainable_state(model: torch.nn.Module, state: Mapping[str, torch.Tensor]) -> None:
    parameters = dict(model.named_parameters())
    expected = {name for name, parameter in parameters.items() if parameter.requires_grad}
    if set(state) != expected:
        raise DataIntegrityError(
            f"trainable state keys mismatch expected={sorted(expected)} actual={sorted(state)}"
        )
    with torch.no_grad():
        for name, tensor in state.items():
            target = parameters[name]
            if tuple(target.shape) != tuple(tensor.shape):
                raise DataIntegrityError(f"trainable tensor shape mismatch for {name}")
            target.copy_(tensor.to(dtype=target.dtype, device=target.device))


def write_checkpoint(
    *,
    checkpoints_root: Path,
    repo_root: Path,
    run_id: str,
    phase_id: str,
    checkpoint_id: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    step: int,
    consumed_tokens: int,
    sampler_state: Mapping[str, Any],
    config_hash: str,
    data_manifest_hash: str,
    parent_artifact_hash: str,
) -> Path:
    checkpoints_root.mkdir(parents=True, exist_ok=True)
    target = checkpoints_root / checkpoint_id
    if target.exists():
        raise DataIntegrityError(f"checkpoint already exists: {target}")

    temp = Path(tempfile.mkdtemp(prefix=f".{checkpoint_id}.partial-", dir=str(checkpoints_root)))
    try:
        weights_path = temp / "trainable_weights.pt"
        optimizer_path = temp / "optimizer.pt"
        scheduler_path = temp / "scheduler.pt"
        python_rng_path = temp / "rng_python.pkl"
        numpy_rng_path = temp / "rng_numpy.pkl"
        torch_rng_path = temp / "rng_torch_cpu.pt"

        torch.save(trainable_state(model), weights_path)
        torch.save(optimizer.state_dict(), optimizer_path)
        torch.save(scheduler.state_dict(), scheduler_path)
        python_rng_path.write_bytes(pickle.dumps(random.getstate(), protocol=pickle.HIGHEST_PROTOCOL))
        numpy_rng_path.write_bytes(pickle.dumps(np.random.get_state(), protocol=pickle.HIGHEST_PROTOCOL))
        torch.save(torch.get_rng_state(), torch_rng_path)

        artifacts = {
            "weights": {"path": weights_path.name, "sha256": sha256_file(weights_path)},
            "optimizer": {"path": optimizer_path.name, "sha256": sha256_file(optimizer_path)},
            "scheduler": {"path": scheduler_path.name, "sha256": sha256_file(scheduler_path)},
            "python_rng": {"path": python_rng_path.name, "sha256": sha256_file(python_rng_path)},
            "numpy_rng": {"path": numpy_rng_path.name, "sha256": sha256_file(numpy_rng_path)},
            "torch_rng": {"path": torch_rng_path.name, "sha256": sha256_file(torch_rng_path)},
        }
        manifest = {
            "run_id": run_id,
            "phase_id": phase_id,
            "checkpoint_id": checkpoint_id,
            "step": step,
            "consumed_tokens": consumed_tokens,
            "weights": [artifacts["weights"]],
            "optimizer_state": artifacts["optimizer"],
            "scheduler_state": artifacts["scheduler"],
            "rng_state": {
                "python": artifacts["python_rng"],
                "numpy": artifacts["numpy_rng"],
                "framework_cpu": artifacts["torch_rng"],
                "framework_device": [],
            },
            "sampler_state": dict(sampler_state),
            "gradient_accumulation_state": {"micro_step": 0},
            "config_hash": config_hash,
            "data_manifest_hash": data_manifest_hash,
            "parent_artifact_hash": parent_artifact_hash,
            "status": "COMMITTED",
        }
        _validate_checkpoint_manifest(manifest, repo_root)
        manifest_path = temp / "checkpoint_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        state_history = {
            "states": ["WRITING", "VERIFIED", "COMMITTED"],
            "manifest_sha256": sha256_file(manifest_path),
        }
        (temp / "checkpoint_state_history.json").write_text(
            json.dumps(state_history, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        _verify_artifacts(temp, manifest)
        marker = {
            "status": "COMMITTED",
            "manifest_sha256": sha256_file(manifest_path),
            "payload_hash": _checkpoint_payload_hash(temp),
        }
        (temp / "CHECKPOINT_COMPLETE.json").write_text(
            json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        _fsync_tree(temp)
        os.replace(temp, target)
        return target
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        raise


def restore_checkpoint(
    checkpoint_dir: Path,
    repo_root: Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
) -> dict[str, Any]:
    manifest = verify_checkpoint(checkpoint_dir, repo_root)
    weights = torch.load(checkpoint_dir / manifest["weights"][0]["path"], map_location="cpu", weights_only=True)
    apply_trainable_state(model, weights)
    optimizer.load_state_dict(
        torch.load(checkpoint_dir / manifest["optimizer_state"]["path"], map_location="cpu", weights_only=False)
    )
    scheduler.load_state_dict(
        torch.load(checkpoint_dir / manifest["scheduler_state"]["path"], map_location="cpu", weights_only=False)
    )
    random.setstate(pickle.loads((checkpoint_dir / manifest["rng_state"]["python"]["path"]).read_bytes()))
    np.random.set_state(pickle.loads((checkpoint_dir / manifest["rng_state"]["numpy"]["path"]).read_bytes()))
    torch.set_rng_state(
        torch.load(
            checkpoint_dir / manifest["rng_state"]["framework_cpu"]["path"],
            map_location="cpu",
            weights_only=True,
        )
    )
    return manifest


def verify_checkpoint(checkpoint_dir: Path, repo_root: Path) -> dict[str, Any]:
    marker_path = checkpoint_dir / "CHECKPOINT_COMPLETE.json"
    manifest_path = checkpoint_dir / "checkpoint_manifest.json"
    if not marker_path.is_file() or not manifest_path.is_file():
        raise DataIntegrityError(f"checkpoint is not COMMITTED: {checkpoint_dir}")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if marker.get("status") != "COMMITTED" or manifest.get("status") != "COMMITTED":
        raise DataIntegrityError(f"checkpoint status is not COMMITTED: {checkpoint_dir}")
    if marker.get("manifest_sha256") != sha256_file(manifest_path):
        raise DataIntegrityError(f"checkpoint manifest hash mismatch: {checkpoint_dir}")
    _validate_checkpoint_manifest(manifest, repo_root)
    _verify_artifacts(checkpoint_dir, manifest)
    expected_payload = marker.get("payload_hash")
    actual_payload = _checkpoint_payload_hash(checkpoint_dir)
    if expected_payload != actual_payload:
        raise DataIntegrityError(f"checkpoint payload hash mismatch: {checkpoint_dir}")
    return manifest


def create_incomplete_checkpoint_sentinel(checkpoints_root: Path, checkpoint_id: str) -> Path:
    path = checkpoints_root / f".{checkpoint_id}.partial-injected"
    path.mkdir(parents=True, exist_ok=False)
    (path / "INTERRUPTED").write_text("intentional M2 interruption\n", encoding="utf-8")
    return path


def committed_checkpoint_hash(checkpoint_dir: Path, repo_root: Path) -> str:
    manifest = verify_checkpoint(checkpoint_dir, repo_root)
    return sha256_object(
        {
            "manifest_sha256": sha256_file(checkpoint_dir / "checkpoint_manifest.json"),
            "weights_sha256": manifest["weights"][0]["sha256"],
            "checkpoint_id": manifest["checkpoint_id"],
        }
    )


def _validate_checkpoint_manifest(manifest: Mapping[str, Any], repo_root: Path) -> None:
    schema_path = repo_root / "docs/model-training-pipeline/schemas/checkpoint_manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validate_mapping(manifest, schema, "CheckpointManifest")


def _verify_artifacts(checkpoint_dir: Path, manifest: Mapping[str, Any]) -> None:
    artifacts = [
        *manifest["weights"],
        manifest["optimizer_state"],
        manifest["scheduler_state"],
        manifest["rng_state"]["python"],
        manifest["rng_state"]["numpy"],
        manifest["rng_state"]["framework_cpu"],
        *manifest["rng_state"].get("framework_device", []),
    ]
    for artifact in artifacts:
        path = checkpoint_dir / artifact["path"]
        if not path.is_file():
            raise DataIntegrityError(f"checkpoint artifact missing: {path}")
        actual = sha256_file(path)
        if actual != artifact["sha256"]:
            raise DataIntegrityError(f"checkpoint artifact hash mismatch: {path}")


def _checkpoint_payload_hash(checkpoint_dir: Path) -> str:
    entries = []
    for path in sorted(checkpoint_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name == "CHECKPOINT_COMPLETE.json":
            continue
        entries.append({"path": path.name, "sha256": sha256_file(path)})
    return sha256_object(entries)


def _tensor_sha256(tensor: torch.Tensor) -> str:
    raw = tensor.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
    import hashlib

    return hashlib.sha256(raw).hexdigest()


def _fsync_tree(path: Path) -> None:
    for file_path in path.iterdir():
        if file_path.is_file():
            with file_path.open("rb") as handle:
                try:
                    os.fsync(handle.fileno())
                except OSError:
                    pass
    try:
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass
