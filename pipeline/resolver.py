"""Zero-training canonical resolution.

M0 does not probe or initialize training frameworks. It resolves only values that
can be fixed without touching model weights or fresh evidence.
"""

from __future__ import annotations

import copy
import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .canonical import sha256_file, sha256_object
from .models import ExperimentConfig


@dataclass(frozen=True)
class ResolverContext:
    backend: str = "python-m0"
    device_class: str = "cpu"
    device_count: int = 1
    world_size: int = 1
    auto_precision: str = "fp32"

    @classmethod
    def from_environment(cls) -> "ResolverContext":
        return cls(
            backend=os.environ.get("PIPELINE_M0_BACKEND", "python-m0"),
            device_class=os.environ.get("PIPELINE_M0_DEVICE_CLASS", "cpu"),
            device_count=int(os.environ.get("PIPELINE_M0_DEVICE_COUNT", "1")),
            world_size=int(os.environ.get("PIPELINE_M0_WORLD_SIZE", "1")),
            auto_precision=os.environ.get("PIPELINE_M0_AUTO_PRECISION", "fp32"),
        )


def resolve_config(
    config: ExperimentConfig,
    profile: Mapping[str, Any],
    repo_root: Path,
    context: ResolverContext | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    context = context or ResolverContext.from_environment()
    resolved = copy.deepcopy(dict(config.raw))
    for phase in resolved["phases"]:
        requested = phase["training"]["precision"]
        phase["training"]["requested_precision"] = requested
        phase["training"]["precision"] = context.auto_precision if requested == "auto" else requested
        phase["resolved_resource"] = {
            "backend": context.backend,
            "device_class": context.device_class,
            "device_count": context.device_count,
            "world_size": context.world_size,
            "resolved_precision": phase["training"]["precision"],
            "resolution_scope": "m0_zero_training",
        }
    profile_path = repo_root / "docs/model-training-pipeline" / config.model.profile
    evidence = {
        "model_revision": config.model.revision,
        "model_profile_path": str(profile_path.relative_to(repo_root)).replace("\\", "/"),
        "model_profile_file_sha256": sha256_file(profile_path),
        "model_profile_contract_sha256": sha256_object(profile),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "source_identity": _git_identity(repo_root),
        "resolver_context": {
            "backend": context.backend,
            "device_class": context.device_class,
            "device_count": context.device_count,
            "world_size": context.world_size,
            "auto_precision": context.auto_precision,
        },
    }
    return resolved, evidence


def _git_identity(repo_root: Path) -> dict[str, Any]:
    explicit = os.environ.get("PIPELINE_SOURCE_SHA")
    if explicit:
        return {"git_commit": explicit, "dirty": None, "source": "environment"}
    try:
        commit = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout
        return {"git_commit": commit, "dirty": bool(status.strip()), "source": "git"}
    except (OSError, subprocess.SubprocessError):
        return {"git_commit": None, "dirty": None, "source": "unavailable"}
