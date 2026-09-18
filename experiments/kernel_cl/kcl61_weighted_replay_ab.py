"""KCL-6.1: A/B test raw replay storage vs exact weighted consolidation.

Protocol: docs/research/kernel-continual-learning/kcl61-protocol.md
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import statistics
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    evaluate,
    optimizer_for,
    parameter_count,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import (
    TASK_ORDER,
    task_sequence,
    replay_task_index,
)


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl61-protocol.md")
KCL6_EVIDENCE = Path("experiments/kernel_cl/results/kcl6_summary.json")

FINAL_SEEDS = (3333, 3535, 3737, 3939, 4141)

CONTROL_CURRENT_PER_BATCH = 15
REPLAY_PER_BATCH = 1
BATCH_SIZE = 16
REPLAY_FRACTION = 1 / 16

TASK_SIZE = 24
RAW_BYTES_PER_OBSERVATION = 24
WEIGHTED_BYTES_PER_UNIQUE = 28

BEHAVIOR_TOLERANCE = 1 / 24
T4_ACCURACY_MIN = 0.95
BYTE_COMPRESSION_RATIO_MIN = 1.20


Observation = tuple[int, int, int]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "pstdev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def _deep_equal(a: Any, b: Any) -> bool:
    if torch.is_tensor(a) and torch.is_tensor(b):
        return torch.equal(a, b)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_deep_equal(x, y) for x, y in zip(a, b))
    return a == b


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL6_EVIDENCE.read_text(encoding="utf-8"))
    valid = (
        raw.get("status") == "PASS"
        and raw.get("verdict") == "FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON"
        and raw.get("task_order") == list(TASK_ORDER)
        and abs(float(raw["replay"]["fraction"]) - REPLAY_FRACTION) < 1e-12
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "task_order": raw.get("task_order"),
        "replay_fraction": raw.get("replay", {}).get("fraction"),
        "sha256": _sha256(KCL6_EVIDENCE),
    }


def task_observations(
    task: tuple[torch.Tensor, torch.Tensor],
) -> list[Observation]:
    x, y = task
    return [
        (int(x[i, 0]), int(x[i, 1]), int(y[i]))
        for i in range(len(y))
    ]


def observation_to_tensors(obs: Observation) -> tuple[torch.Tensor, torch.Tensor]:
    x0, x1, y = obs
    return (
        torch.tensor([[x0, x1]], dtype=torch.long),
        torch.tensor([y], dtype=torch.long),
    )


@dataclass
class RawTaskStore:
    observations: list[Observation]

    @classmethod
    def from_task(cls, task: tuple[torch.Tensor, torch.Tensor]) -> "RawTaskStore":
        return cls(task_observations(task))

    @property
    def total_multiplicity(self) -> int:
        return len(self.observations)

    @property
    def unique_entries(self) -> int:
        return len(set(self.observations))

    def observation_at_rank(self, rank: int) -> Observation:
        if not 0 <= rank < len(self.observations):
            raise IndexError(rank)
        return self.observations[rank]

    def logical_accounting(self) -> dict[str, int | float]:
        entries = len(self.observations)
        return {
            "raw_entries": entries,
            "unique_entries": self.unique_entries,
            "total_multiplicity": entries,
            "duplicate_consolidations": entries - self.unique_entries,
            "payload_scalars": entries * 3,
            "payload_bytes": entries * RAW_BYTES_PER_OBSERVATION,
            "count_metadata_bytes": 0,
            "total_logical_bytes": entries * RAW_BYTES_PER_OBSERVATION,
        }


@dataclass
class WeightedExactTaskStore:
    counts: dict[Observation, int]

    @classmethod
    def from_task(
        cls,
        task: tuple[torch.Tensor, torch.Tensor],
    ) -> "WeightedExactTaskStore":
        store = cls({})
        for obs in task_observations(task):
            store.ingest(obs)
        return store

    def ingest(self, obs: Observation, multiplicity: int = 1) -> None:
        if multiplicity <= 0:
            raise ValueError("multiplicity must be positive")
        self.counts[obs] = self.counts.get(obs, 0) + multiplicity

    @property
    def total_multiplicity(self) -> int:
        return sum(self.counts.values())

    @property
    def unique_entries(self) -> int:
        return len(self.counts)

    def canonical_items(self) -> list[tuple[Observation, int]]:
        return sorted(self.counts.items())

    def observation_at_rank(self, rank: int) -> Observation:
        if not 0 <= rank < self.total_multiplicity:
            raise IndexError(rank)
        cursor = 0
        for obs, count in self.canonical_items():
            if rank < cursor + count:
                return obs
            cursor += count
        raise AssertionError("weighted rank lookup fell through")

    def expand_canonical(self) -> list[Observation]:
        out: list[Observation] = []
        for obs, count in self.canonical_items():
            out.extend([obs] * count)
        return out

    def logical_accounting(self) -> dict[str, int | float]:
        unique = self.unique_entries
        total = self.total_multiplicity
        return {
            "raw_entries_equivalent": total,
            "unique_entries": unique,
            "total_multiplicity": total,
            "duplicate_consolidations": total - unique,
            "payload_scalars": unique * 3,
            "payload_bytes": unique * RAW_BYTES_PER_OBSERVATION,
            "count_metadata_bytes": unique * 4,
            "total_logical_bytes": unique * WEIGHTED_BYTES_PER_UNIQUE,
        }


def exact_repeat_mechanism_validation(
    task: tuple[torch.Tensor, torch.Tensor],
) -> dict[str, Any]:
    base = task_observations(task)
    raw_expanded: list[Observation] = []
    weighted = WeightedExactTaskStore({})

    repeat_counts: list[int] = []
    for i, obs in enumerate(base):
        count = 1 + (i % 4)
        repeat_counts.append(count)
        raw_expanded.extend([obs] * count)
        weighted.ingest(obs, count)

    raw_canonical = sorted(raw_expanded)
    weighted_expanded = weighted.expand_canonical()

    rank_equivalent = all(
        raw_canonical[rank] == weighted.observation_at_rank(rank)
        for rank in range(len(raw_canonical))
    )

    expected_total = sum(repeat_counts)
    return {
        "expected_total_multiplicity": expected_total,
        "raw_expanded_count": len(raw_expanded),
        "weighted_unique_entries": weighted.unique_entries,
        "weighted_total_multiplicity": weighted.total_multiplicity,
        "canonical_expansion_equal": raw_canonical == weighted_expanded,
        "rank_lookup_equivalent": rank_equivalent,
        "no_conflict_merge_key_includes_target": True,
        "pass": (
            len(raw_expanded) == expected_total
            and weighted.unique_entries == TASK_SIZE
            and weighted.total_multiplicity == expected_total
            and raw_canonical == weighted_expanded
            and rank_equivalent
        ),
    }


def _sample_current_batch(
    task: tuple[torch.Tensor, torch.Tensor],
    generator: torch.Generator,
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(
        0, len(y), (CONTROL_CURRENT_PER_BATCH,), generator=generator
    )
    return x[idx], y[idx]


def _train_replay_stage_ab(
    model_a: torch.nn.Module,
    optimizer_a: torch.optim.Optimizer,
    model_b: torch.nn.Module,
    optimizer_b: torch.optim.Optimizer,
    raw_previous: list[RawTaskStore],
    weighted_previous: list[WeightedExactTaskStore],
    current_task: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
    stage_index: int,
) -> dict[str, Any]:
    if len(raw_previous) != len(weighted_previous) or not raw_previous:
        raise ValueError("paired replay stores must have same positive task count")

    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage_index + 101)

    rank_gens: list[torch.Generator] = []
    for task_index in range(len(raw_previous)):
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed + 1000 * stage_index + 503 + 37 * task_index)
        rank_gens.append(gen)

    replay_counts = [0 for _ in raw_previous]
    matched_replay_observations = True

    model_a.train()
    model_b.train()

    for step in range(steps):
        current_x, current_y = _sample_current_batch(current_task, current_gen)

        source = replay_task_index(step, len(raw_previous))
        replay_counts[source] += 1

        raw_store = raw_previous[source]
        weighted_store = weighted_previous[source]

        if raw_store.total_multiplicity != weighted_store.total_multiplicity:
            raise RuntimeError("A/B replay multiplicity mismatch")

        rank = int(torch.randint(
            0,
            raw_store.total_multiplicity,
            (1,),
            generator=rank_gens[source],
        ).item())

        raw_obs = raw_store.observation_at_rank(rank)
        weighted_obs = weighted_store.observation_at_rank(rank)
        matched_replay_observations = (
            matched_replay_observations and raw_obs == weighted_obs
        )

        raw_rx, raw_ry = observation_to_tensors(raw_obs)
        weighted_rx, weighted_ry = observation_to_tensors(weighted_obs)

        xa = torch.cat([current_x, raw_rx], dim=0)
        ya = torch.cat([current_y, raw_ry], dim=0)
        xb = torch.cat([current_x, weighted_rx], dim=0)
        yb = torch.cat([current_y, weighted_ry], dim=0)

        logits_a = model_a(xa)[:, -1, :]
        logits_b = model_b(xb)[:, -1, :]
        loss_a = F.cross_entropy(logits_a, ya)
        loss_b = F.cross_entropy(logits_b, yb)
        if not torch.isfinite(loss_a) or not torch.isfinite(loss_b):
            raise RuntimeError("non-finite KCL-6.1 loss")

        optimizer_a.zero_grad(set_to_none=True)
        loss_a.backward()
        optimizer_a.step()

        optimizer_b.zero_grad(set_to_none=True)
        loss_b.backward()
        optimizer_b.step()

    state_equal = all(
        torch.equal(model_a.state_dict()[name], model_b.state_dict()[name])
        for name in model_a.state_dict()
    )

    return {
        "previous_task_count": len(raw_previous),
        "replay_counts_by_previous_task": replay_counts,
        "matched_replay_observations": matched_replay_observations,
        "post_stage_model_state_equal": state_equal,
        "total_replay_examples": sum(replay_counts),
        "total_current_examples": steps * CONTROL_CURRENT_PER_BATCH,
        "total_processed_examples": steps * BATCH_SIZE,
    }


def _evaluate_learned(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    learned_count: int,
) -> dict[str, dict[str, float]]:
    return {
        name: evaluate(model, task)
        for name, task in tasks[:learned_count]
    }


def _storage_snapshot(
    raw_stores: list[RawTaskStore],
    weighted_stores: list[WeightedExactTaskStore],
) -> dict[str, Any]:
    raw_entries = sum(store.total_multiplicity for store in raw_stores)
    raw_unique = sum(store.unique_entries for store in raw_stores)
    raw_bytes = sum(
        int(store.logical_accounting()["total_logical_bytes"])
        for store in raw_stores
    )

    weighted_unique = sum(store.unique_entries for store in weighted_stores)
    weighted_total = sum(store.total_multiplicity for store in weighted_stores)
    weighted_duplicates = sum(
        int(store.logical_accounting()["duplicate_consolidations"])
        for store in weighted_stores
    )
    weighted_payload_bytes = sum(
        int(store.logical_accounting()["payload_bytes"])
        for store in weighted_stores
    )
    weighted_count_bytes = sum(
        int(store.logical_accounting()["count_metadata_bytes"])
        for store in weighted_stores
    )
    weighted_total_bytes = sum(
        int(store.logical_accounting()["total_logical_bytes"])
        for store in weighted_stores
    )

    return {
        "A_raw": {
            "entries": raw_entries,
            "unique_entries": raw_unique,
            "logical_bytes": raw_bytes,
        },
        "B_weighted_exact": {
            "unique_entries": weighted_unique,
            "total_multiplicity": weighted_total,
            "duplicate_consolidations": weighted_duplicates,
            "payload_bytes": weighted_payload_bytes,
            "count_metadata_bytes": weighted_count_bytes,
            "logical_bytes": weighted_total_bytes,
        },
        "entry_compression_ratio_A_over_B": (
            raw_entries / weighted_unique if weighted_unique else None
        ),
        "byte_compression_ratio_A_over_B": (
            raw_bytes / weighted_total_bytes if weighted_total_bytes else None
        ),
    }


def run_seed(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    task_names = [name for name, _ in tasks]

    base_model = build_model(config, seed)
    base_optimizer = optimizer_for(base_model, config)

    train_stage(
        base_model,
        base_optimizer,
        tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )

    model_a = copy.deepcopy(base_model)
    optimizer_a = optimizer_for(model_a, config)
    optimizer_a.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    model_b = copy.deepcopy(base_model)
    optimizer_b = optimizer_for(model_b, config)
    optimizer_b.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    post_t1_model_state_equal = all(
        torch.equal(model_a.state_dict()[name], model_b.state_dict()[name])
        for name in model_a.state_dict()
    )
    post_t1_optimizer_state_equal = _deep_equal(
        optimizer_a.state_dict(), optimizer_b.state_dict()
    )

    matrix_a: dict[str, dict[str, dict[str, float]]] = {
        "after_T1": _evaluate_learned(model_a, tasks, 1)
    }
    matrix_b: dict[str, dict[str, dict[str, float]]] = {
        "after_T1": _evaluate_learned(model_b, tasks, 1)
    }

    raw_stores = [RawTaskStore.from_task(tasks[0][1])]
    weighted_stores = [WeightedExactTaskStore.from_task(tasks[0][1])]

    storage_by_stage = {
        "after_T1": _storage_snapshot(raw_stores, weighted_stores)
    }
    stage_accounting: dict[str, Any] = {}

    for stage_idx in range(1, len(tasks)):
        stage_number = stage_idx + 1
        stage_name = f"after_T{stage_number}"
        current_task = tasks[stage_idx][1]

        accounting = _train_replay_stage_ab(
            model_a,
            optimizer_a,
            model_b,
            optimizer_b,
            raw_stores,
            weighted_stores,
            current_task,
            steps=config.stage_steps,
            seed=seed,
            stage_index=stage_number,
        )
        stage_accounting[stage_name] = accounting

        matrix_a[stage_name] = _evaluate_learned(model_a, tasks, stage_idx + 1)
        matrix_b[stage_name] = _evaluate_learned(model_b, tasks, stage_idx + 1)

        raw_stores.append(RawTaskStore.from_task(current_task))
        weighted_stores.append(WeightedExactTaskStore.from_task(current_task))
        storage_by_stage[stage_name] = _storage_snapshot(
            raw_stores, weighted_stores
        )

    final_stage = "after_T4"
    final_a = {
        name: matrix_a[final_stage][name]["accuracy"] for name in task_names
    }
    final_b = {
        name: matrix_b[final_stage][name]["accuracy"] for name in task_names
    }

    deltas = {name: final_b[name] - final_a[name] for name in task_names}
    prior_names = task_names[:3]
    mean_prior_a = statistics.fmean(final_a[name] for name in prior_names)
    mean_prior_b = statistics.fmean(final_b[name] for name in prior_names)
    worst_prior_a = min(final_a[name] for name in prior_names)
    worst_prior_b = min(final_b[name] for name in prior_names)

    behavioral_equivalence = (
        all(abs(delta) <= BEHAVIOR_TOLERANCE for delta in deltas.values())
        and abs(mean_prior_b - mean_prior_a) <= BEHAVIOR_TOLERANCE
        and final_a[task_names[3]] >= T4_ACCURACY_MIN
        and final_b[task_names[3]] >= T4_ACCURACY_MIN
    )

    all_stage_replay_matched = all(
        row["matched_replay_observations"] for row in stage_accounting.values()
    )
    all_stage_models_equal = all(
        row["post_stage_model_state_equal"] for row in stage_accounting.values()
    )

    final_storage = storage_by_stage[final_stage]
    storage_effect = (
        final_storage["entry_compression_ratio_A_over_B"] > 1.0
        and final_storage["byte_compression_ratio_A_over_B"]
        >= BYTE_COMPRESSION_RATIO_MIN
    )

    return {
        "seed": seed,
        "task_order": task_names,
        "final_accuracy": {
            "A_raw": final_a,
            "B_weighted_exact": final_b,
            "delta_B_minus_A": deltas,
        },
        "final_summary": {
            "A_mean_prior_accuracy": mean_prior_a,
            "B_mean_prior_accuracy": mean_prior_b,
            "delta_mean_prior": mean_prior_b - mean_prior_a,
            "A_worst_prior_accuracy": worst_prior_a,
            "B_worst_prior_accuracy": worst_prior_b,
            "A_average_accuracy_all_tasks": statistics.fmean(final_a.values()),
            "B_average_accuracy_all_tasks": statistics.fmean(final_b.values()),
            "A_T4_accuracy": final_a[task_names[3]],
            "B_T4_accuracy": final_b[task_names[3]],
        },
        "storage_by_stage": storage_by_stage,
        "stage_accounting": stage_accounting,
        "gates": {
            "behavioral_equivalence_pass": behavioral_equivalence,
            "storage_effect_pass": storage_effect,
        },
        "integrity": {
            "post_t1_model_state_equal": post_t1_model_state_equal,
            "post_t1_optimizer_state_equal": post_t1_optimizer_state_equal,
            "all_replay_observations_matched": all_stage_replay_matched,
            "all_post_stage_model_states_equal": all_stage_models_equal,
            "equal_update_and_batch_budget": True,
        },
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    anchor = _load_anchor()
    tasks = task_sequence(config)
    repeat_validation = exact_repeat_mechanism_validation(tasks[0][1])

    per_seed: list[dict[str, Any]] = []
    if anchor["valid"] and repeat_validation["pass"]:
        per_seed = [run_seed(seed, config) for seed in FINAL_SEEDS]

    integrity_valid = (
        anchor["valid"]
        and repeat_validation["pass"]
        and bool(per_seed)
        and all(
            all(value is True for value in row["integrity"].values())
            for row in per_seed
        )
    )

    behavioral_equivalence = (
        integrity_valid
        and all(row["gates"]["behavioral_equivalence_pass"] for row in per_seed)
        and abs(
            statistics.fmean(
                row["final_summary"]["B_mean_prior_accuracy"] for row in per_seed
            )
            - statistics.fmean(
                row["final_summary"]["A_mean_prior_accuracy"] for row in per_seed
            )
        )
        <= BEHAVIOR_TOLERANCE
    )

    storage_effect = (
        integrity_valid
        and all(row["gates"]["storage_effect_pass"] for row in per_seed)
    )

    if not integrity_valid:
        status = "REVISE"
        verdict = "WEIGHTED_REPLAY_AB_CONTRAST_INVALID"
    elif not behavioral_equivalence:
        status = "FAIL"
        verdict = "WEIGHTED_EXACT_REPRESENTATION_CHANGES_CL_BEHAVIOR"
    elif storage_effect:
        status = "PASS"
        verdict = "WEIGHTED_EXACT_COMPRESSION_REDUCES_STORAGE_WITHOUT_CL_LOSS"
    else:
        status = "NEGATIVE"
        verdict = "EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE"

    aggregates: dict[str, Any] = {}
    if per_seed:
        aggregates = {
            "A_final_mean_prior_accuracy": _stats([
                row["final_summary"]["A_mean_prior_accuracy"] for row in per_seed
            ]),
            "B_final_mean_prior_accuracy": _stats([
                row["final_summary"]["B_mean_prior_accuracy"] for row in per_seed
            ]),
            "delta_mean_prior_B_minus_A": _stats([
                row["final_summary"]["delta_mean_prior"] for row in per_seed
            ]),
            "A_final_average_accuracy_all_tasks": _stats([
                row["final_summary"]["A_average_accuracy_all_tasks"] for row in per_seed
            ]),
            "B_final_average_accuracy_all_tasks": _stats([
                row["final_summary"]["B_average_accuracy_all_tasks"] for row in per_seed
            ]),
            "A_final_T4_accuracy": _stats([
                row["final_summary"]["A_T4_accuracy"] for row in per_seed
            ]),
            "B_final_T4_accuracy": _stats([
                row["final_summary"]["B_T4_accuracy"] for row in per_seed
            ]),
            "final_entry_compression_ratio": _stats([
                row["storage_by_stage"]["after_T4"]["entry_compression_ratio_A_over_B"]
                for row in per_seed
            ]),
            "final_byte_compression_ratio": _stats([
                row["storage_by_stage"]["after_T4"]["byte_compression_ratio_A_over_B"]
                for row in per_seed
            ]),
        }

    final_storage_template = (
        per_seed[0]["storage_by_stage"]["after_T4"] if per_seed else None
    )

    model = build_model(config, FINAL_SEEDS[0])
    return {
        "experiment": "KCL-6.1",
        "status": status,
        "verdict": verdict,
        "arms": {
            "A": "RAW_TASK_OBSERVATION_STORE",
            "B": "WEIGHTED_EXACT_OBSERVATION_STORE",
        },
        "final_seeds": list(FINAL_SEEDS),
        "task_order": list(TASK_ORDER),
        "replay": {
            "fraction": REPLAY_FRACTION,
            "current_examples_per_batch": CONTROL_CURRENT_PER_BATCH,
            "replay_examples_per_batch": REPLAY_PER_BATCH,
            "loss_multiplication_used": False,
            "sampling_by_multiplicity": True,
        },
        "repeat_mechanism_validation": repeat_validation,
        "historical_anchor": anchor,
        "per_seed": per_seed,
        "aggregates": aggregates,
        "final_storage_template": final_storage_template,
        "gates": {
            "behavior_tolerance": BEHAVIOR_TOLERANCE,
            "T4_accuracy_min": T4_ACCURACY_MIN,
            "byte_compression_ratio_min": BYTE_COMPRESSION_RATIO_MIN,
            "entry_compression_ratio_must_exceed_one": True,
        },
        "integrity": {
            "historical_anchor_valid": anchor["valid"],
            "repeat_mechanism_validation_pass": repeat_validation["pass"],
            "paired_contrast_valid": integrity_valid,
            "model_architecture_changed": False,
            "semantic_merging_used": False,
            "prototype_merging_used": False,
            "rule_inference_used": False,
        },
        "model_parameter_count": parameter_count(model),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "scope": {
            "kcl7_started": False,
            "semantic_compression_started": False,
            "challenger_started": False,
            "reasoning_work": False,
            "external_api_calls": 0,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen KCL-6.1 weighted replay A/B")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl61_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] in {"PASS", "NEGATIVE"}:
        return 0
    if result["status"] == "REVISE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
