"""KCL-6.3: partial/fuzzy reconstructive decay A/B/C/D experiment."""

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
from typing import Any, Union

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config, build_model, evaluate, optimizer_for, parameter_count, train_stage
)
from experiments.kernel_cl.kcl6_long_horizon import TASK_ORDER, task_sequence, replay_task_index
from experiments.kernel_cl import kcl61_weighted_replay_ab as k61
from experiments.kernel_cl import kcl62_reconstructive_memory_abc as k62

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl63-protocol.md")
KCL61_EVIDENCE = Path("experiments/kernel_cl/results/kcl61_summary.json")
KCL62_EVIDENCE = Path("experiments/kernel_cl/results/kcl62_summary.json")

FINAL_SEEDS = (3333, 3535, 3737, 3939, 4141)
CURRENT_PER_BATCH = 15
REPLAY_PER_BATCH = 1
BATCH_SIZE = 16
REPLAY_FRACTION = 1 / 16
OFFSET_BUCKET_WIDTH = 4

EXACT_SCHEMA_BYTES = 41
FUZZY_SCHEMA_BYTES = 34
A_RAW_FINAL_BYTES = 2304
B_WEIGHTED_FINAL_BYTES = 2688
C_EXACT_FINAL_BYTES = 164
D_EXPECTED_FINAL_BYTES = 143

T4_ACCURACY_MIN = 0.95
D_PRIOR_MIN_PER_SEED = 0.25
D_PRIOR_MEAN_MIN = 0.35
D_TO_C_RETENTION_RATIO_MIN = 0.50
D_TO_C_STORAGE_RATIO_MAX = 0.90
A_OVER_D_STORAGE_MIN = 10.0
RELEARNING_ADVANTAGE_MEAN_MIN = 20.0
RELEARNING_THRESHOLD = 0.95
RELEARNING_MAX_STEPS = 250
RELEARNING_EVAL_INTERVAL = 10
RELEARNING_CENSORED_COST = 260

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


def _load_anchors() -> dict[str, Any]:
    k61e = json.loads(KCL61_EVIDENCE.read_text(encoding="utf-8"))
    k62e = json.loads(KCL62_EVIDENCE.read_text(encoding="utf-8"))
    k61_ok = (
        k61e.get("status") == "NEGATIVE"
        and k61e.get("verdict")
        == "EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE"
        and k61e.get("task_order") == list(TASK_ORDER)
    )
    k62_ok = (
        k62e.get("status") == "PASS"
        and k62e.get("verdict")
        == "RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS"
        and k62e.get("task_order") == list(TASK_ORDER)
    )
    return {
        "valid": k61_ok and k62_ok,
        "kcl61_valid": k61_ok,
        "kcl62_valid": k62_ok,
        "kcl61_sha256": _sha256(KCL61_EVIDENCE),
        "kcl62_sha256": _sha256(KCL62_EVIDENCE),
    }


@dataclass(frozen=True)
class ExactMemory:
    """Recent exact reconstructive memory. Raw observations are not replay storage."""

    schema: k62.AffineSchema
    keys: tuple[int, ...]

    @classmethod
    def from_task(cls, task: tuple[torch.Tensor, torch.Tensor]) -> "ExactMemory":
        store = k62.ReconstructiveStore.from_task(task)
        if store.residuals:
            raise ValueError("KCL-6.3 frozen workload requires zero residuals")
        return cls(store.schema, tuple(store.keys))

    def observation_at_rank(self, rank: int, _: torch.Generator | None = None) -> Observation:
        return self.schema.observation(self.keys[rank])

    @property
    def logical_bytes(self) -> int:
        return EXACT_SCHEMA_BYTES

    @property
    def state(self) -> str:
        return "exact"


@dataclass(frozen=True)
class FuzzyMemory:
    """Aged schema with exact offset/support deliberately removed."""

    varying_position: int
    constant_token: int
    key_min: int
    output_min: int
    modulus: int
    multiplier: int
    offset_bucket_low: int

    @classmethod
    def from_exact(cls, exact: ExactMemory) -> "FuzzyMemory":
        s = exact.schema
        low = (s.offset // OFFSET_BUCKET_WIDTH) * OFFSET_BUCKET_WIDTH
        if low + OFFSET_BUCKET_WIDTH > s.modulus:
            raise ValueError("offset bucket exceeds modulus")
        return cls(
            varying_position=s.varying_position,
            constant_token=s.constant_token,
            key_min=s.key_min,
            output_min=s.output_min,
            modulus=s.modulus,
            multiplier=s.multiplier,
            offset_bucket_low=low,
        )

    def _observation_with_offset(self, rank: int, offset: int) -> Observation:
        key = self.key_min + rank
        target = self.output_min + (
            (self.multiplier * (key - self.key_min) + offset) % self.modulus
        )
        if self.varying_position == 0:
            return (key, self.constant_token, target)
        return (self.constant_token, key, target)

    def observation_at_rank(self, rank: int, uncertainty_gen: torch.Generator) -> Observation:
        delta = int(torch.randint(
            0, OFFSET_BUCKET_WIDTH, (1,), generator=uncertainty_gen
        ).item())
        return self._observation_with_offset(rank, self.offset_bucket_low + delta)

    def representative_observation_at_rank(self, rank: int) -> Observation:
        representative = self.offset_bucket_low + (OFFSET_BUCKET_WIDTH // 2)
        return self._observation_with_offset(rank, representative)

    def reactivate_from_cue(self, cue: Observation) -> ExactMemory:
        key = self.key_min
        expected_input = (
            (key, self.constant_token)
            if self.varying_position == 0
            else (self.constant_token, key)
        )
        if cue[:2] != expected_input:
            raise ValueError("cue must be the key_min observation")
        exact_b = cue[2] - self.output_min
        if not (self.offset_bucket_low <= exact_b < self.offset_bucket_low + OFFSET_BUCKET_WIDTH):
            raise ValueError("cue offset is outside remembered bucket")
        schema = k62.AffineSchema(
            varying_position=self.varying_position,
            constant_token=self.constant_token,
            key_min=self.key_min,
            output_min=self.output_min,
            modulus=self.modulus,
            multiplier=self.multiplier,
            offset=exact_b,
            support_count=self.modulus,
        )
        return ExactMemory(schema=schema, keys=tuple(range(self.key_min, self.key_min + self.modulus)))

    @property
    def logical_bytes(self) -> int:
        return FUZZY_SCHEMA_BYTES

    @property
    def state(self) -> str:
        return "fuzzy"


Memory = Union[ExactMemory, FuzzyMemory]


def canonical_observations(task: tuple[torch.Tensor, torch.Tensor]) -> list[Observation]:
    obs = k62.task_observations(task)
    c0 = len({o[0] for o in obs})
    varying = 1 if c0 == 1 else 0
    return sorted(obs, key=lambda o: o[varying])


def reconstruction_accuracy(memory: Memory, task: tuple[torch.Tensor, torch.Tensor], *, representative: bool) -> float:
    original = canonical_observations(task)
    reconstructed: list[Observation] = []
    if isinstance(memory, ExactMemory):
        reconstructed = [memory.observation_at_rank(i) for i in range(len(memory.keys))]
    else:
        if not representative:
            raise ValueError("fuzzy deterministic reconstruction requires representative=True")
        reconstructed = [memory.representative_observation_at_rank(i) for i in range(memory.modulus)]
    return sum(a == b for a, b in zip(original, reconstructed)) / len(original)


def one_cue_reactivate(memory: FuzzyMemory, task: tuple[torch.Tensor, torch.Tensor]) -> dict[str, Any]:
    original = canonical_observations(task)
    cue = original[0]
    reactivated = memory.reactivate_from_cue(cue)
    recovered = [reactivated.observation_at_rank(i) for i in range(len(reactivated.keys))]
    accuracy = sum(a == b for a, b in zip(original, recovered)) / len(original)
    return {
        "cue": cue,
        "external_cue_count": 1,
        "reconstruction_accuracy": accuracy,
        "exact_offset_restored": reactivated.schema.offset,
        "pass": accuracy == 1.0,
    }


def _sample_current(
    task: tuple[torch.Tensor, torch.Tensor], gen: torch.Generator
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(0, len(y), (CURRENT_PER_BATCH,), generator=gen)
    return x[idx], y[idx]


def _train_d_stage(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    previous: list[Memory],
    current: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
    stage: int,
    exact_reference_tasks: list[tuple[torch.Tensor, torch.Tensor]],
) -> dict[str, Any]:
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)

    rank_gens: list[torch.Generator] = []
    uncertainty_gens: list[torch.Generator] = []
    for i in range(len(previous)):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(rg)
        ug = torch.Generator(device="cpu")
        ug.manual_seed(seed + 1000 * stage + 1503 + 41 * i)
        uncertainty_gens.append(ug)

    replay_counts = [0 for _ in previous]
    exact_match_count = 0
    fuzzy_draw_count = 0
    total_draw_count = 0

    model.train()
    for step in range(steps):
        cx, cy = _sample_current(current, current_gen)
        source = replay_task_index(step, len(previous))
        replay_counts[source] += 1

        memory = previous[source]
        size = len(memory.keys) if isinstance(memory, ExactMemory) else memory.modulus
        rank = int(torch.randint(0, size, (1,), generator=rank_gens[source]).item())
        obs = memory.observation_at_rank(rank, uncertainty_gens[source])

        exact_obs = canonical_observations(exact_reference_tasks[source])[rank]
        exact_match_count += int(obs == exact_obs)
        total_draw_count += 1
        if isinstance(memory, FuzzyMemory):
            fuzzy_draw_count += 1

        rx, ry = k61.observation_to_tensors(obs)
        x = torch.cat([cx, rx], dim=0)
        y = torch.cat([cy, ry], dim=0)
        loss = F.cross_entropy(model(x)[:, -1, :], y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-6.3 D loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    return {
        "replay_counts": replay_counts,
        "total_replay": sum(replay_counts),
        "fuzzy_draw_count": fuzzy_draw_count,
        "exact_replay_match_count": exact_match_count,
        "exact_replay_match_rate": exact_match_count / total_draw_count,
    }


def _evaluate_all(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    count: int,
) -> dict[str, dict[str, float]]:
    return {name: evaluate(model, task) for name, task in tasks[:count]}


def run_d(seed: int, config: KCL1Config) -> tuple[dict[str, Any], torch.nn.Module]:
    tasks = task_sequence(config)
    names = [name for name, _ in tasks]

    model = build_model(config, seed)
    optimizer = optimizer_for(model, config)
    train_stage(
        model,
        optimizer,
        tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )

    memories: list[Memory] = [ExactMemory.from_task(tasks[0][1])]
    matrices = {"after_T1": _evaluate_all(model, tasks, 1)}
    memory_states = {"after_T1": [m.state for m in memories]}
    accounting: dict[str, Any] = {}

    for idx in range(1, len(tasks)):
        stage = idx + 1
        stage_name = f"after_T{stage}"
        accounting[stage_name] = _train_d_stage(
            model,
            optimizer,
            memories,
            tasks[idx][1],
            steps=config.stage_steps,
            seed=seed,
            stage=stage,
            exact_reference_tasks=[t for _, t in tasks[:idx]],
        )
        matrices[stage_name] = _evaluate_all(model, tasks, idx + 1)

        # One-subsequent-task age rule: exact prior memories decay now.
        memories = [
            FuzzyMemory.from_exact(m) if isinstance(m, ExactMemory) else m
            for m in memories
        ]
        memories.append(ExactMemory.from_task(tasks[idx][1]))
        memory_states[stage_name] = [m.state for m in memories]

    final = {name: matrices["after_T4"][name]["accuracy"] for name in names}
    prior = names[:3]
    return {
        "final_accuracy": final,
        "mean_prior_accuracy": statistics.fmean(final[n] for n in prior),
        "worst_prior_accuracy": min(final[n] for n in prior),
        "average_accuracy_all_tasks": statistics.fmean(final.values()),
        "T4_accuracy": final[names[3]],
        "logical_bytes": sum(m.logical_bytes for m in memories),
        "final_memory_states": [m.state for m in memories],
        "memory_states_by_stage": memory_states,
        "stage_accounting": accounting,
        "final_memories": memories,
        "matrices": matrices,
    }, model


def _train_curve_from_model(
    model: torch.nn.Module,
    task: tuple[torch.Tensor, torch.Tensor],
    config: KCL1Config,
    seed: int,
) -> dict[str, Any]:
    model = copy.deepcopy(model)
    optimizer = optimizer_for(model, config)
    x, y = task
    gen = torch.Generator(device="cpu")
    gen.manual_seed(seed)

    curve = [{"step": 0, **evaluate(model, task)}]
    first = 0 if curve[0]["accuracy"] >= RELEARNING_THRESHOLD else None

    for step in range(1, RELEARNING_MAX_STEPS + 1):
        idx = torch.randint(0, len(y), (config.batch_size,), generator=gen)
        logits = model(x[idx])[:, -1, :]
        loss = F.cross_entropy(logits, y[idx])
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if step % RELEARNING_EVAL_INTERVAL == 0:
            metrics = evaluate(model, task)
            curve.append({"step": step, **metrics})
            if first is None and metrics["accuracy"] >= RELEARNING_THRESHOLD:
                first = step

    return {
        "steps_to_95": first if first is not None else RELEARNING_CENSORED_COST,
        "curve": curve,
    }


def relearning_probe(
    final_d_model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    config: KCL1Config,
    seed: int,
) -> dict[str, Any]:
    per_task = []
    for i, (name, task) in enumerate(tasks[:3]):
        stream_seed = seed + 12000 + 101 * i
        d_curve = _train_curve_from_model(final_d_model, task, config, stream_seed)
        novel_model = build_model(config, seed)
        novel_curve = _train_curve_from_model(novel_model, task, config, stream_seed)
        advantage = novel_curve["steps_to_95"] - d_curve["steps_to_95"]
        per_task.append({
            "task": name,
            "D_reencounter_steps_to_95": d_curve["steps_to_95"],
            "NOVEL_steps_to_95": novel_curve["steps_to_95"],
            "advantage_steps": advantage,
            "D_curve": d_curve["curve"],
            "NOVEL_curve": novel_curve["curve"],
        })

    advantages = [r["advantage_steps"] for r in per_task]
    faster_count = sum(r["advantage_steps"] > 0 for r in per_task)
    return {
        "per_task": per_task,
        "mean_advantage_steps": statistics.fmean(advantages),
        "tasks_faster_than_novel": faster_count,
        "pass": (
            statistics.fmean(advantages) > 0
            and faster_count >= 2
        ),
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    anchors = _load_anchors()
    tasks = task_sequence(config)

    rows: list[dict[str, Any]] = []
    if anchors["valid"]:
        for seed in FINAL_SEEDS:
            ab = k61.run_seed(seed, config)
            c = k62.run_c(seed, config)
            d, final_d_model = run_d(seed, config)

            fuzzy_checks = []
            for i in range(3):
                memory = d["final_memories"][i]
                if not isinstance(memory, FuzzyMemory):
                    raise RuntimeError("T1-T3 must be fuzzy at final T4")
                pre = reconstruction_accuracy(memory, tasks[i][1], representative=True)
                post = one_cue_reactivate(memory, tasks[i][1])
                fuzzy_checks.append({
                    "task": tasks[i][0],
                    "pre_cue_reconstruction_accuracy": pre,
                    "post_cue": post,
                })

            relearn = relearning_probe(final_d_model, tasks, config, seed)
            a_mean = ab["final_summary"]["A_mean_prior_accuracy"]
            b_mean = ab["final_summary"]["B_mean_prior_accuracy"]
            c_mean = c["mean_prior_accuracy"]

            # JSON-safe view of D excludes live model/memory objects.
            d_public = {
                k: v for k, v in d.items()
                if k not in {"final_memories"}
            }
            d_public["final_memory_descriptors"] = [
                {
                    "state": m.state,
                    "logical_bytes": m.logical_bytes,
                    **(
                        {
                            "offset_bucket_low": m.offset_bucket_low,
                            "multiplier": m.multiplier,
                            "modulus": m.modulus,
                        }
                        if isinstance(m, FuzzyMemory)
                        else {
                            "exact_offset": m.schema.offset,
                            "multiplier": m.schema.multiplier,
                            "modulus": m.schema.modulus,
                        }
                    ),
                }
                for m in d["final_memories"]
            ]

            rows.append({
                "seed": seed,
                "A": {
                    "mean_prior_accuracy": a_mean,
                    "T4_accuracy": ab["final_summary"]["A_T4_accuracy"],
                    "logical_bytes": A_RAW_FINAL_BYTES,
                },
                "B": {
                    "mean_prior_accuracy": b_mean,
                    "T4_accuracy": ab["final_summary"]["B_T4_accuracy"],
                    "logical_bytes": B_WEIGHTED_FINAL_BYTES,
                },
                "C": {
                    "mean_prior_accuracy": c_mean,
                    "T4_accuracy": c["T4_accuracy"],
                    "logical_bytes": C_EXACT_FINAL_BYTES,
                },
                "D": d_public,
                "fuzzy_reconstruction": fuzzy_checks,
                "relearning": relearn,
            })

    integrity = (
        anchors["valid"]
        and bool(rows)
        and all(
            row["D"]["logical_bytes"] == D_EXPECTED_FINAL_BYTES
            and row["D"]["final_memory_states"] == ["fuzzy", "fuzzy", "fuzzy", "exact"]
            for row in rows
        )
    )

    h1_fuzzy_recoverable = (
        integrity
        and all(
            all(
                item["pre_cue_reconstruction_accuracy"] < 1.0
                and item["post_cue"]["external_cue_count"] == 1
                and item["post_cue"]["pass"]
                for item in row["fuzzy_reconstruction"]
            )
            for row in rows
        )
    )

    h2_trace_plasticity = (
        integrity
        and all(row["D"]["T4_accuracy"] >= T4_ACCURACY_MIN for row in rows)
        and all(row["D"]["mean_prior_accuracy"] >= D_PRIOR_MIN_PER_SEED for row in rows)
        and statistics.fmean(row["D"]["mean_prior_accuracy"] for row in rows) >= D_PRIOR_MEAN_MIN
        and statistics.fmean(row["D"]["mean_prior_accuracy"] for row in rows)
        >= D_TO_C_RETENTION_RATIO_MIN
        * statistics.fmean(row["C"]["mean_prior_accuracy"] for row in rows)
    )

    h3_relearning = (
        integrity
        and all(row["relearning"]["mean_advantage_steps"] > 0 for row in rows)
        and all(row["relearning"]["tasks_faster_than_novel"] >= 2 for row in rows)
        and statistics.fmean(row["relearning"]["mean_advantage_steps"] for row in rows)
        >= RELEARNING_ADVANTAGE_MEAN_MIN
    )

    h4_storage = (
        integrity
        and all(
            row["D"]["logical_bytes"] <= D_TO_C_STORAGE_RATIO_MAX * row["C"]["logical_bytes"]
            and row["A"]["logical_bytes"] / row["D"]["logical_bytes"] >= A_OVER_D_STORAGE_MIN
            for row in rows
        )
    )

    if not integrity:
        status, verdict = "REVISE", "FUZZY_DECAY_CONTRAST_INVALID"
    elif not h1_fuzzy_recoverable:
        status, verdict = "REVISE", "DECAY_DID_NOT_CREATE_VALID_FUZZY_MEMORY"
    elif not h2_trace_plasticity:
        status, verdict = "FAIL", "FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY"
    elif not h3_relearning:
        status, verdict = "NEGATIVE", "FUZZY_TRACE_RECOVERABLE_BUT_NO_RELEARNING_ADVANTAGE"
    elif h4_storage:
        status, verdict = "PASS", "FUZZY_RECONSTRUCTIVE_MEMORY_RETAINS_RECOVERABLE_TRACE"
    else:
        status, verdict = "NEGATIVE", "FUZZY_TRACE_VALID_BUT_STORAGE_TARGET_NOT_MET"

    aggregates: dict[str, Any] = {}
    if rows:
        for arm in ("A", "B", "C"):
            aggregates[f"{arm}_mean_prior_accuracy"] = _stats(
                [row[arm]["mean_prior_accuracy"] for row in rows]
            )
        aggregates["D_mean_prior_accuracy"] = _stats(
            [row["D"]["mean_prior_accuracy"] for row in rows]
        )
        aggregates["D_T4_accuracy"] = _stats([row["D"]["T4_accuracy"] for row in rows])
        aggregates["D_relearning_advantage_steps"] = _stats(
            [row["relearning"]["mean_advantage_steps"] for row in rows]
        )
        aggregates["D_exact_replay_match_rate_T3"] = _stats(
            [row["D"]["stage_accounting"]["after_T3"]["exact_replay_match_rate"] for row in rows]
        )
        aggregates["D_exact_replay_match_rate_T4"] = _stats(
            [row["D"]["stage_accounting"]["after_T4"]["exact_replay_match_rate"] for row in rows]
        )

    # Compact per-seed summary for the committed JSON.
    compact_rows = []
    for row in rows:
        compact_rows.append({
            "seed": row["seed"],
            "A_mean_prior": row["A"]["mean_prior_accuracy"],
            "B_mean_prior": row["B"]["mean_prior_accuracy"],
            "C_mean_prior": row["C"]["mean_prior_accuracy"],
            "D_mean_prior": row["D"]["mean_prior_accuracy"],
            "D_worst_prior": row["D"]["worst_prior_accuracy"],
            "D_T4": row["D"]["T4_accuracy"],
            "D_all_task_average": row["D"]["average_accuracy_all_tasks"],
            "D_storage_bytes": row["D"]["logical_bytes"],
            "D_final_memory_states": row["D"]["final_memory_states"],
            "fuzzy_reconstruction": row["fuzzy_reconstruction"],
            "relearning": {
                "mean_advantage_steps": row["relearning"]["mean_advantage_steps"],
                "tasks_faster_than_novel": row["relearning"]["tasks_faster_than_novel"],
                "per_task": [
                    {
                        "task": p["task"],
                        "D_reencounter_steps_to_95": p["D_reencounter_steps_to_95"],
                        "NOVEL_steps_to_95": p["NOVEL_steps_to_95"],
                        "advantage_steps": p["advantage_steps"],
                    }
                    for p in row["relearning"]["per_task"]
                ],
            },
            "replay_match_rates": {
                "after_T2": row["D"]["stage_accounting"]["after_T2"]["exact_replay_match_rate"],
                "after_T3": row["D"]["stage_accounting"]["after_T3"]["exact_replay_match_rate"],
                "after_T4": row["D"]["stage_accounting"]["after_T4"]["exact_replay_match_rate"],
            },
        })

    return {
        "experiment": "KCL-6.3",
        "status": status,
        "verdict": verdict,
        "arms": {
            "A": "RAW_EPISODIC",
            "B": "WEIGHTED_EXACT",
            "C": "EXACT_RECONSTRUCTIVE_SCHEMA",
            "D": "FUZZY_RECONSTRUCTIVE_DECAY",
        },
        "final_seeds": list(FINAL_SEEDS),
        "task_order": list(TASK_ORDER),
        "decay": {
            "offset_bucket_width": OFFSET_BUCKET_WIDTH,
            "age_after_subsequent_completed_tasks": 1,
            "fuzzy_fields_retained": [
                "varying_position",
                "constant_token",
                "key_min",
                "output_min",
                "modulus",
                "multiplier",
                "offset_bucket_low",
            ],
            "exact_offset_retained_after_decay": False,
            "support_count_retained_after_decay": False,
            "fuzzy_replay_offset_sampling": "uniform_within_bucket",
        },
        "storage": {
            "A_final_bytes": A_RAW_FINAL_BYTES,
            "B_final_bytes": B_WEIGHTED_FINAL_BYTES,
            "C_final_bytes": C_EXACT_FINAL_BYTES,
            "D_final_bytes": D_EXPECTED_FINAL_BYTES,
            "C_over_D_ratio": C_EXACT_FINAL_BYTES / D_EXPECTED_FINAL_BYTES,
            "A_over_D_ratio": A_RAW_FINAL_BYTES / D_EXPECTED_FINAL_BYTES,
        },
        "hypotheses": {
            "H1_fuzzy_trace_recoverable": h1_fuzzy_recoverable,
            "H2_useful_CL_trace_and_plasticity": h2_trace_plasticity,
            "H3_relearning_advantage": h3_relearning,
            "H4_storage_below_exact_schema": h4_storage,
        },
        "aggregates": aggregates,
        "per_seed": compact_rows,
        "historical_anchors": anchors,
        "gates": {
            "T4_accuracy_min": T4_ACCURACY_MIN,
            "D_prior_min_per_seed": D_PRIOR_MIN_PER_SEED,
            "D_prior_mean_min": D_PRIOR_MEAN_MIN,
            "D_to_C_retention_ratio_min": D_TO_C_RETENTION_RATIO_MIN,
            "D_to_C_storage_ratio_max": D_TO_C_STORAGE_RATIO_MAX,
            "A_over_D_storage_min": A_OVER_D_STORAGE_MIN,
            "relearning_advantage_mean_min": RELEARNING_ADVANTAGE_MEAN_MIN,
            "relearning_threshold": RELEARNING_THRESHOLD,
        },
        "integrity": {
            "historical_anchors_valid": anchors["valid"],
            "expected_final_seeds_exact": [row["seed"] for row in rows] == list(FINAL_SEEDS) if rows else False,
            "final_memory_age_schedule_exact": all(
                row["D"]["final_memory_states"] == ["fuzzy", "fuzzy", "fuzzy", "exact"]
                for row in rows
            ) if rows else False,
            "model_architecture_changed": False,
            "replay_budget_changed": False,
            "raw_episodes_retained_inside_fuzzy_memory": False,
        },
        "model_parameter_count": parameter_count(build_model(config, FINAL_SEEDS[0])),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "scope": {
            "kcl7_started": False,
            "semantic_memory_started": False,
            "reasoning_work": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl63_summary.json",
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
