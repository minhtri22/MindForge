"""Typed M0 configuration and state models.

The JSON Schema remains the canonical syntax contract. These dataclasses are the
implementation-side typed view used after schema validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class RunClass(str, Enum):
    SMOKE = "smoke"
    DEVELOPMENT = "development"
    CALIBRATION = "calibration"
    CONFIRMATORY = "confirmatory"
    RELEASE = "release"


class RunState(str, Enum):
    DRAFT = "DRAFT"
    PREPARED = "PREPARED"
    PREFLIGHT_PASS = "PREFLIGHT_PASS"
    EXECUTION_LOCKED = "EXECUTION_LOCKED"
    RUNNING = "RUNNING"
    EVALUATED = "EVALUATED"
    ADJUDICATED_PASS = "ADJUDICATED_PASS"
    ADJUDICATED_FAIL = "ADJUDICATED_FAIL"
    INVALID = "INVALID"
    EXPORTED = "EXPORTED"
    RUNTIME_VERIFIED = "RUNTIME_VERIFIED"
    REPRO_VERIFIED = "REPRO_VERIFIED"
    QUALIFICATION_FAIL = "QUALIFICATION_FAIL"
    PROMOTED = "PROMOTED"


class PhaseState(str, Enum):
    PLANNED = "PLANNED"
    INPUT_READY = "INPUT_READY"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    CHECKPOINT_SELECTED = "CHECKPOINT_SELECTED"
    PHASE_EVALUATED = "PHASE_EVALUATED"
    PHASE_PASS = "PHASE_PASS"
    PHASE_FAIL = "PHASE_FAIL"
    PHASE_INVALID = "PHASE_INVALID"


@dataclass(frozen=True)
class ModelSpec:
    source: str
    id: str
    revision: str
    require_resolved_sha: bool
    profile: str
    allow_remote_code: bool = False


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    adapter: str
    snapshot: str
    freshness_class: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class TokenStreamSpec:
    sequence_length: int
    add_bos: bool
    add_eos: bool
    separator_policy: str
    truncation: str
    packing: Mapping[str, Any]
    sampling: Mapping[str, Any]
    workers: int


@dataclass(frozen=True)
class TrainingSpec:
    precision: str
    learning_rate: float
    warmup: Mapping[str, Any]
    checkpoint_every_steps: int
    save_optimizer_state: bool


@dataclass(frozen=True)
class CheckpointSelectionSpec:
    rule: str
    metric_id: str | None
    direction: str
    tie_breaker: str


@dataclass(frozen=True)
class PhaseSpec:
    id: str
    type: str
    parent_ref: str
    datasets: tuple[str, ...]
    token_stream: TokenStreamSpec
    stop: Mapping[str, Any]
    optimizer_transition: str
    scheduler_transition: str
    checkpoint_selection: CheckpointSelectionSpec
    training: TrainingSpec


@dataclass(frozen=True)
class BaselineSpec:
    id: str
    role: str
    source: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    metric_version: str
    target_artifact: str
    baseline_id: str
    comparison_type: str
    operator: str
    threshold: float
    aggregation: Mapping[str, Any]
    required: bool
    missing_data_policy: str


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    run_class: RunClass
    seed_sets: Mapping[str, tuple[int, ...]]
    model: ModelSpec
    datasets: Mapping[str, DatasetSpec]
    phases: tuple[PhaseSpec, ...]
    baselines: tuple[BaselineSpec, ...]
    fixture_set: str
    metrics: tuple[MetricSpec, ...]
    inference: Mapping[str, Any]
    reasoning: Mapping[str, Any]
    export: Mapping[str, Any]
    raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ExperimentConfig":
        exp = raw["experiment"]
        model = raw["model"]
        datasets = {
            name: DatasetSpec(
                name=name,
                adapter=value["adapter"],
                snapshot=str(value["snapshot"]),
                freshness_class=value["freshness_class"],
                raw=value,
            )
            for name, value in raw["datasets"].items()
        }
        phases: list[PhaseSpec] = []
        for value in raw["phases"]:
            stream = value["token_stream"]
            training = value["training"]
            selection = value["checkpoint_selection"]
            phases.append(
                PhaseSpec(
                    id=value["id"],
                    type=value["type"],
                    parent_ref=value["parent_ref"],
                    datasets=tuple(value["datasets"]),
                    token_stream=TokenStreamSpec(
                        sequence_length=int(stream["sequence_length"]),
                        add_bos=bool(stream["add_bos"]),
                        add_eos=bool(stream["add_eos"]),
                        separator_policy=stream["separator_policy"],
                        truncation=stream["truncation"],
                        packing=stream["packing"],
                        sampling=stream["sampling"],
                        workers=int(stream["workers"]),
                    ),
                    stop=value["stop"],
                    optimizer_transition=value["optimizer_transition"],
                    scheduler_transition=value["scheduler_transition"],
                    checkpoint_selection=CheckpointSelectionSpec(
                        rule=selection["rule"],
                        metric_id=selection.get("metric_id"),
                        direction=selection["direction"],
                        tie_breaker=selection["tie_breaker"],
                    ),
                    training=TrainingSpec(
                        precision=training["precision"],
                        learning_rate=float(training["learning_rate"]),
                        warmup=training["warmup"],
                        checkpoint_every_steps=int(training["checkpoint_every_steps"]),
                        save_optimizer_state=bool(training["save_optimizer_state"]),
                    ),
                )
            )
        baselines = tuple(
            BaselineSpec(id=value["id"], role=value["role"], source=value["source"], raw=value)
            for value in raw["baselines"]
        )
        metrics = tuple(
            MetricSpec(
                metric_id=value["metric_id"],
                metric_version=str(value["metric_version"]),
                target_artifact=value["target_artifact"],
                baseline_id=value["baseline_id"],
                comparison_type=value["comparison_type"],
                operator=value["operator"],
                threshold=float(value["threshold"]),
                aggregation=value["aggregation"],
                required=bool(value["required"]),
                missing_data_policy=value["missing_data_policy"],
            )
            for value in raw["evaluation"]["metrics"]
        )
        seed_sets = {
            name: tuple(int(seed) for seed in seeds)
            for name, seeds in exp.get("seed_sets", {}).items()
        }
        return cls(
            experiment_id=exp["id"],
            run_class=RunClass(exp["mode"]),
            seed_sets=seed_sets,
            model=ModelSpec(
                source=model["source"],
                id=model["id"],
                revision=str(model["revision"]),
                require_resolved_sha=bool(model["require_resolved_sha"]),
                profile=model["profile"],
                allow_remote_code=bool(model.get("allow_remote_code", False)),
            ),
            datasets=datasets,
            phases=tuple(phases),
            baselines=baselines,
            fixture_set=raw["evaluation"]["fixture_set"],
            metrics=metrics,
            inference=raw["evaluation"]["inference"],
            reasoning=raw["reasoning"],
            export=raw["export"],
            raw=raw,
        )
