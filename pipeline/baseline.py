"""Baseline registry compiler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import sha256_object
from .errors import SemanticValidationError
from .models import BaselineSpec, ExperimentConfig


@dataclass(frozen=True)
class BaselineRegistry:
    entries: tuple[dict[str, Any], ...]
    sha256: str

    @classmethod
    def compile(cls, config: ExperimentConfig) -> "BaselineRegistry":
        seen: set[str] = set()
        entries: list[dict[str, Any]] = []
        for baseline in config.baselines:
            if baseline.id in seen:
                raise SemanticValidationError(f"duplicate baseline id: {baseline.id}")
            seen.add(baseline.id)
            entries.append(_compile_entry(baseline, config))
        return cls(entries=tuple(entries), sha256=sha256_object(entries))

    def ids(self) -> set[str]:
        return {entry["id"] for entry in self.entries}


def _compile_entry(baseline: BaselineSpec, config: ExperimentConfig) -> dict[str, Any]:
    raw = dict(baseline.raw)
    source = baseline.source
    if source == "model_revision":
        reference = f"model:{raw['model_id']}@{raw['revision']}"
    elif source == "phase_parent":
        reference = f"phase:{raw['phase_id']}:parent"
    elif source == "artifact":
        reference = f"artifact:{raw['artifact_id']}"
    elif source == "control_run":
        reference = f"control-run:{raw['control_run_id']}"
    else:  # defensive: schema should make this unreachable
        raise SemanticValidationError(f"unsupported baseline source: {source}")
    return {
        "id": baseline.id,
        "role": baseline.role,
        "source": source,
        "reference": reference,
        "contract": raw,
        "contract_hash": sha256_object(raw),
    }
