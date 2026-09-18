"""KCL-6.4: paired fuzzy-guess D vs ask/reactivate E."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import statistics
import subprocess
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config, build_model, evaluate, optimizer_for, parameter_count, train_stage
)
from experiments.kernel_cl.kcl6_long_horizon import TASK_ORDER, task_sequence, replay_task_index
from experiments.kernel_cl import kcl61_weighted_replay_ab as k61
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl64-protocol.md")
KCL63_EVIDENCE = Path("experiments/kernel_cl/results/kcl63_summary.json")

FINAL_SEEDS = (3333, 3535, 3737, 3939, 4141)
CURRENT_PER_BATCH = 15
REPLAY_PER_BATCH = 1
BATCH_SIZE = 16
REPLAY_FRACTION = 1 / 16

STRICT_T4_MIN = 0.95
PRIOR_MIN_PER_SEED = 0.25
PRIOR_MEAN_MIN = 0.35
C_HISTORICAL_MEAN_PRIOR = 0.6750000019868214
TO_C_RETENTION_RATIO_MIN = 0.50
MEAN_PRIOR_GAIN_OVER_D_MIN = 0.10
D_REPRO_TOLERANCE = 1 / 24
FINAL_PERSISTENT_BYTES = 143
EXPECTED_TOTAL_QUERIES = 3


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


def _load_kcl63_anchor() -> dict[str, Any]:
    raw = json.loads(KCL63_EVIDENCE.read_text(encoding="utf-8"))
    hypotheses = raw.get("hypotheses", {})
    valid = (
        raw.get("status") == "FAIL"
        and raw.get("verdict") == "FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY"
        and hypotheses.get("H1_fuzzy_trace_recoverable") is True
        and hypotheses.get("H2_useful_CL_trace_and_plasticity") is False
        and hypotheses.get("H3_relearning_advantage") is True
        and hypotheses.get("H4_storage_below_exact_schema") is True
        and raw.get("task_order") == list(TASK_ORDER)
    )
    by_seed = {
        int(row["seed"]): {
            "D_mean_prior": float(row["D_mean_prior"]),
            "D_T4": float(row["D_T4"]),
        }
        for row in raw.get("per_seed", [])
    }
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "hypotheses": hypotheses,
        "by_seed": by_seed,
        "D_mean_prior_aggregate": raw.get("aggregates", {}).get("D_mean_prior_accuracy", {}).get("mean"),
        "D_T4_aggregate": raw.get("aggregates", {}).get("D_T4_accuracy", {}).get("mean"),
        "sha256": _sha256(KCL63_EVIDENCE),
    }


def _sample_current(
    task: tuple[torch.Tensor, torch.Tensor],
    generator: torch.Generator,
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(0, len(y), (CURRENT_PER_BATCH,), generator=generator)
    return x[idx], y[idx]


def _exact_size(memory: k63.Memory) -> int:
    return len(memory.keys) if isinstance(memory, k63.ExactMemory) else memory.modulus


def _exact_reference_at_rank(
    task: tuple[torch.Tensor, torch.Tensor],
    rank: int,
) -> k63.Observation:
    return k63.canonical_observations(task)[rank]


def _clarification_cue(
    memory: k63.FuzzyMemory,
    task: tuple[torch.Tensor, torch.Tensor],
) -> k63.Observation:
    cue = k63.canonical_observations(task)[0]
    # Frozen cue must be key_min.
    key = cue[memory.varying_position]
    if key != memory.key_min:
        raise RuntimeError("clarification cue is not key_min")
    return cue


def _train_stage_pair(
    model_d: torch.nn.Module,
    optimizer_d: torch.optim.Optimizer,
    memories_d: list[k63.Memory],
    model_e: torch.nn.Module,
    optimizer_e: torch.optim.Optimizer,
    memories_e: list[k63.Memory],
    current_task: tuple[torch.Tensor, torch.Tensor],
    previous_reference_tasks: list[tuple[torch.Tensor, torch.Tensor]],
    *,
    steps: int,
    seed: int,
    stage: int,
) -> dict[str, Any]:
    if len(memories_d) != len(memories_e) or not memories_d:
        raise ValueError("paired D/E memories must have same positive length")

    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)

    rank_gens: list[torch.Generator] = []
    d_uncertainty_gens: list[torch.Generator] = []
    for i in range(len(memories_d)):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(rg)

        ug = torch.Generator(device="cpu")
        ug.manual_seed(seed + 1000 * stage + 1503 + 41 * i)
        d_uncertainty_gens.append(ug)

    clarified_sources: set[int] = set()
    query_events: list[dict[str, Any]] = []
    replay_counts = [0 for _ in memories_d]
    d_exact_matches = 0
    e_exact_matches = 0
    d_errors = 0
    e_errors = 0

    model_d.train()
    model_e.train()

    for step in range(steps):
        current_x, current_y = _sample_current(current_task, current_gen)

        source = replay_task_index(step, len(memories_d))
        replay_counts[source] += 1

        md = memories_d[source]
        me = memories_e[source]
        size = _exact_size(md)
        if size != _exact_size(me):
            raise RuntimeError("D/E logical replay domains differ")

        rank = int(torch.randint(0, size, (1,), generator=rank_gens[source]).item())
        exact_obs = _exact_reference_at_rank(previous_reference_tasks[source], rank)

        # D: unchanged KCL-6.3 guessing policy.
        obs_d = md.observation_at_rank(rank, d_uncertainty_gens[source])

        # E: if fuzzy, ask exactly once per source per stage before replay.
        if isinstance(me, k63.FuzzyMemory):
            if source in clarified_sources:
                raise RuntimeError("clarified source unexpectedly returned to fuzzy within stage")
            cue = _clarification_cue(me, previous_reference_tasks[source])
            reactivated = me.reactivate_from_cue(cue)
            memories_e[source] = reactivated
            me = reactivated
            clarified_sources.add(source)
            query_events.append({
                "step": step,
                "source_index": source,
                "cue": list(cue),
                "query_training_examples": 0,
                "query_gradient_updates": 0,
                "raw_cue_retained": False,
            })

        obs_e = me.observation_at_rank(rank)

        d_match = obs_d == exact_obs
        e_match = obs_e == exact_obs
        d_exact_matches += int(d_match)
        e_exact_matches += int(e_match)
        d_errors += int(not d_match)
        e_errors += int(not e_match)

        dx, dy = k61.observation_to_tensors(obs_d)
        ex, ey = k61.observation_to_tensors(obs_e)

        batch_dx = torch.cat([current_x, dx], dim=0)
        batch_dy = torch.cat([current_y, dy], dim=0)
        batch_ex = torch.cat([current_x, ex], dim=0)
        batch_ey = torch.cat([current_y, ey], dim=0)

        loss_d = F.cross_entropy(model_d(batch_dx)[:, -1, :], batch_dy)
        loss_e = F.cross_entropy(model_e(batch_ex)[:, -1, :], batch_ey)
        if not torch.isfinite(loss_d) or not torch.isfinite(loss_e):
            raise RuntimeError("non-finite KCL-6.4 loss")

        optimizer_d.zero_grad(set_to_none=True)
        loss_d.backward()
        optimizer_d.step()

        optimizer_e.zero_grad(set_to_none=True)
        loss_e.backward()
        optimizer_e.step()

    total = sum(replay_counts)
    peak_e_bytes = sum(m.logical_bytes for m in memories_e)
    return {
        "replay_counts": replay_counts,
        "queries": len(query_events),
        "query_events": query_events,
        "query_training_examples": sum(e["query_training_examples"] for e in query_events),
        "query_gradient_updates": sum(e["query_gradient_updates"] for e in query_events),
        "D_exact_match_rate": d_exact_matches / total,
        "E_exact_match_rate": e_exact_matches / total,
        "D_replay_errors": d_errors,
        "E_replay_errors": e_errors,
        "exact_replay_errors_avoided": d_errors - e_errors,
        "E_peak_reactivated_schema_bytes": peak_e_bytes,
    }


def _evaluate_learned(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    count: int,
) -> dict[str, dict[str, float]]:
    return {name: evaluate(model, task) for name, task in tasks[:count]}


def _decay_prior_memories(memories: list[k63.Memory]) -> list[k63.Memory]:
    return [
        k63.FuzzyMemory.from_exact(m) if isinstance(m, k63.ExactMemory) else m
        for m in memories
    ]


def run_pair(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    names = [name for name, _ in tasks]

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

    model_d = copy.deepcopy(base_model)
    optimizer_d = optimizer_for(model_d, config)
    optimizer_d.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    model_e = copy.deepcopy(base_model)
    optimizer_e = optimizer_for(model_e, config)
    optimizer_e.load_state_dict(copy.deepcopy(base_optimizer.state_dict()))

    fork_model_equal = all(
        torch.equal(model_d.state_dict()[name], model_e.state_dict()[name])
        for name in model_d.state_dict()
    )
    fork_optimizer_equal = _deep_equal(
        optimizer_d.state_dict(), optimizer_e.state_dict()
    )

    memories_d: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    memories_e: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]

    matrix_d = {"after_T1": _evaluate_learned(model_d, tasks, 1)}
    matrix_e = {"after_T1": _evaluate_learned(model_e, tasks, 1)}
    stage_accounting: dict[str, Any] = {}
    post_stage_memory_states: dict[str, Any] = {
        "after_T1": {
            "D": [m.state for m in memories_d],
            "E": [m.state for m in memories_e],
        }
    }

    max_e_transient_bytes = sum(m.logical_bytes for m in memories_e)

    for idx in range(1, len(tasks)):
        stage = idx + 1
        stage_name = f"after_T{stage}"

        stage_accounting[stage_name] = _train_stage_pair(
            model_d,
            optimizer_d,
            memories_d,
            model_e,
            optimizer_e,
            memories_e,
            tasks[idx][1],
            [task for _, task in tasks[:idx]],
            steps=config.stage_steps,
            seed=seed,
            stage=stage,
        )
        max_e_transient_bytes = max(
            max_e_transient_bytes,
            stage_accounting[stage_name]["E_peak_reactivated_schema_bytes"],
        )

        matrix_d[stage_name] = _evaluate_learned(model_d, tasks, idx + 1)
        matrix_e[stage_name] = _evaluate_learned(model_e, tasks, idx + 1)

        # Frozen one-subsequent-task decay remains active for BOTH arms.
        memories_d = _decay_prior_memories(memories_d)
        memories_e = _decay_prior_memories(memories_e)
        memories_d.append(k63.ExactMemory.from_task(tasks[idx][1]))
        memories_e.append(k63.ExactMemory.from_task(tasks[idx][1]))

        post_stage_memory_states[stage_name] = {
            "D": [m.state for m in memories_d],
            "E": [m.state for m in memories_e],
        }

    final_d = {name: matrix_d["after_T4"][name]["accuracy"] for name in names}
    final_e = {name: matrix_e["after_T4"][name]["accuracy"] for name in names}
    prior = names[:3]

    d_mean_prior = statistics.fmean(final_d[n] for n in prior)
    e_mean_prior = statistics.fmean(final_e[n] for n in prior)
    d_t4 = final_d[names[3]]
    e_t4 = final_e[names[3]]

    queries_by_stage = {
        stage: stage_accounting[stage]["queries"]
        for stage in ("after_T2", "after_T3", "after_T4")
    }
    total_queries = sum(queries_by_stage.values())
    errors_avoided = sum(
        stage_accounting[stage]["exact_replay_errors_avoided"]
        for stage in ("after_T2", "after_T3", "after_T4")
    )

    final_d_bytes = sum(m.logical_bytes for m in memories_d)
    final_e_bytes = sum(m.logical_bytes for m in memories_e)

    return {
        "seed": seed,
        "final_accuracy": {"D": final_d, "E": final_e},
        "D_mean_prior_accuracy": d_mean_prior,
        "E_mean_prior_accuracy": e_mean_prior,
        "prior_gain_E_minus_D": e_mean_prior - d_mean_prior,
        "D_T4_accuracy": d_t4,
        "E_T4_accuracy": e_t4,
        "T4_gain_E_minus_D": e_t4 - d_t4,
        "D_worst_prior_accuracy": min(final_d[n] for n in prior),
        "E_worst_prior_accuracy": min(final_e[n] for n in prior),
        "queries_by_stage": queries_by_stage,
        "total_queries": total_queries,
        "prior_gain_per_query": (
            (e_mean_prior - d_mean_prior) / total_queries
            if total_queries else None
        ),
        "T4_gain_per_query": (
            (e_t4 - d_t4) / total_queries
            if total_queries else None
        ),
        "exact_replay_errors_avoided": errors_avoided,
        "stage_accounting": stage_accounting,
        "persistent_storage": {
            "D_final_bytes": final_d_bytes,
            "E_final_bytes": final_e_bytes,
            "E_peak_transient_schema_bytes": max_e_transient_bytes,
        },
        "final_memory_states": {
            "D": [m.state for m in memories_d],
            "E": [m.state for m in memories_e],
        },
        "integrity": {
            "fork_model_equal": fork_model_equal,
            "fork_optimizer_equal": fork_optimizer_equal,
            "query_training_examples_zero": all(
                stage_accounting[s]["query_training_examples"] == 0
                for s in stage_accounting
            ),
            "query_gradient_updates_zero": all(
                stage_accounting[s]["query_gradient_updates"] == 0
                for s in stage_accounting
            ),
            "E_exact_replay_match_rate_all_stages": all(
                math.isclose(stage_accounting[s]["E_exact_match_rate"], 1.0)
                for s in stage_accounting
            ),
            "persistent_storage_equal": final_d_bytes == final_e_bytes == FINAL_PERSISTENT_BYTES,
            "final_age_schedule_equal": (
                [m.state for m in memories_d]
                == [m.state for m in memories_e]
                == ["fuzzy", "fuzzy", "fuzzy", "exact"]
            ),
        },
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    config = KCL1Config()
    anchor = _load_kcl63_anchor()

    rows: list[dict[str, Any]] = []
    if anchor["valid"]:
        rows = [run_pair(seed, config) for seed in FINAL_SEEDS]

    integrity = (
        anchor["valid"]
        and bool(rows)
        and all(
            all(value is True for value in row["integrity"].values())
            for row in rows
        )
        and all(
            row["queries_by_stage"] == {
                "after_T2": 0,
                "after_T3": 1,
                "after_T4": 2,
            }
            and row["total_queries"] == EXPECTED_TOTAL_QUERIES
            for row in rows
        )
    )

    # D must reproduce the already-closed failure condition and metrics.
    d_metric_consistency = True
    for row in rows:
        historical = anchor["by_seed"].get(row["seed"])
        if historical is None:
            d_metric_consistency = False
            break
        if (
            abs(row["D_mean_prior_accuracy"] - historical["D_mean_prior"])
            > D_REPRO_TOLERANCE
            or abs(row["D_T4_accuracy"] - historical["D_T4"])
            > D_REPRO_TOLERANCE
        ):
            d_metric_consistency = False
            break

    d_failure_condition = any(
        row["D_T4_accuracy"] < STRICT_T4_MIN for row in rows
    )
    d_reproduced = integrity and d_metric_consistency and d_failure_condition

    e_strict_cl = (
        integrity
        and all(row["E_T4_accuracy"] >= STRICT_T4_MIN for row in rows)
        and all(row["E_mean_prior_accuracy"] >= PRIOR_MIN_PER_SEED for row in rows)
        and statistics.fmean(row["E_mean_prior_accuracy"] for row in rows) >= PRIOR_MEAN_MIN
        and statistics.fmean(row["E_mean_prior_accuracy"] for row in rows)
        >= TO_C_RETENTION_RATIO_MIN * C_HISTORICAL_MEAN_PRIOR
    )

    paired_improvement = (
        integrity
        and all(
            row["E_T4_accuracy"] >= row["D_T4_accuracy"]
            and row["E_mean_prior_accuracy"] > row["D_mean_prior_accuracy"]
            for row in rows
        )
        and statistics.fmean(row["prior_gain_E_minus_D"] for row in rows)
        >= MEAN_PRIOR_GAIN_OVER_D_MIN
        and statistics.fmean(row["T4_gain_E_minus_D"] for row in rows) > 0
    )

    query_integrity = (
        integrity
        and all(
            row["total_queries"] == EXPECTED_TOTAL_QUERIES
            and row["stage_accounting"]["after_T2"]["E_exact_match_rate"] == 1.0
            and row["stage_accounting"]["after_T3"]["E_exact_match_rate"] == 1.0
            and row["stage_accounting"]["after_T4"]["E_exact_match_rate"] == 1.0
            for row in rows
        )
    )

    if not integrity or not query_integrity:
        status, verdict = "REVISE", "CLARIFICATION_CONTRAST_INVALID"
    elif not d_reproduced:
        status, verdict = "REVISE", "FUZZY_FAILURE_CONTROL_NOT_REPRODUCED"
    elif e_strict_cl and paired_improvement:
        status, verdict = "PASS", "CLARIFICATION_REACTIVATION_RESCUES_FUZZY_MEMORY_POLICY"
    else:
        status, verdict = "FAIL", "CLARIFICATION_DOES_NOT_RESCUE_FUZZY_MEMORY"

    aggregates: dict[str, Any] = {}
    if rows:
        aggregates = {
            "D_mean_prior_accuracy": _stats([r["D_mean_prior_accuracy"] for r in rows]),
            "E_mean_prior_accuracy": _stats([r["E_mean_prior_accuracy"] for r in rows]),
            "prior_gain_E_minus_D": _stats([r["prior_gain_E_minus_D"] for r in rows]),
            "D_T4_accuracy": _stats([r["D_T4_accuracy"] for r in rows]),
            "E_T4_accuracy": _stats([r["E_T4_accuracy"] for r in rows]),
            "T4_gain_E_minus_D": _stats([r["T4_gain_E_minus_D"] for r in rows]),
            "prior_gain_per_query": _stats([r["prior_gain_per_query"] for r in rows]),
            "exact_replay_errors_avoided": _stats([
                float(r["exact_replay_errors_avoided"]) for r in rows
            ]),
            "E_peak_transient_schema_bytes": _stats([
                float(r["persistent_storage"]["E_peak_transient_schema_bytes"]) for r in rows
            ]),
        }

    compact_rows = []
    for r in rows:
        compact_rows.append({
            "seed": r["seed"],
            "D_mean_prior": r["D_mean_prior_accuracy"],
            "E_mean_prior": r["E_mean_prior_accuracy"],
            "prior_gain": r["prior_gain_E_minus_D"],
            "D_T4": r["D_T4_accuracy"],
            "E_T4": r["E_T4_accuracy"],
            "T4_gain": r["T4_gain_E_minus_D"],
            "D_worst_prior": r["D_worst_prior_accuracy"],
            "E_worst_prior": r["E_worst_prior_accuracy"],
            "queries_by_stage": r["queries_by_stage"],
            "total_queries": r["total_queries"],
            "prior_gain_per_query": r["prior_gain_per_query"],
            "exact_replay_errors_avoided": r["exact_replay_errors_avoided"],
            "persistent_storage": r["persistent_storage"],
            "D_exact_match_rates": {
                s: r["stage_accounting"][s]["D_exact_match_rate"]
                for s in r["stage_accounting"]
            },
            "E_exact_match_rates": {
                s: r["stage_accounting"][s]["E_exact_match_rate"]
                for s in r["stage_accounting"]
            },
        })

    return {
        "experiment": "KCL-6.4",
        "status": status,
        "verdict": verdict,
        "arms": {
            "D": "FUZZY_GUESS_REPLAY",
            "E": "FUZZY_ASK_REACTIVATE",
        },
        "task_order": list(TASK_ORDER),
        "final_seeds": list(FINAL_SEEDS),
        "strict_gate_retained": {
            "T4_accuracy_min_every_seed": STRICT_T4_MIN,
            "gate_relaxed_from_KCL63": False,
        },
        "memory": {
            "bucket_width": k63.OFFSET_BUCKET_WIDTH,
            "decay_schedule_changed": False,
            "representation_changed_from_D": False,
            "D_final_bytes": FINAL_PERSISTENT_BYTES,
            "E_final_bytes": FINAL_PERSISTENT_BYTES,
        },
        "clarification": {
            "trigger": "first replay of fuzzy task in current stage",
            "cue": "one exact key_min observation",
            "cue_enters_gradient": False,
            "cue_enters_training_batch": False,
            "cue_stored_as_raw_episode": False,
            "expected_queries_by_stage": {
                "after_T2": 0,
                "after_T3": 1,
                "after_T4": 2,
            },
            "expected_total_queries": EXPECTED_TOTAL_QUERIES,
        },
        "historical_anchor": anchor,
        "hypotheses": {
            "D_failure_reproduced": d_reproduced,
            "E_strict_CL_pass": e_strict_cl,
            "paired_D_to_E_improvement_pass": paired_improvement,
            "query_integrity_pass": query_integrity,
        },
        "aggregates": aggregates,
        "per_seed": compact_rows,
        "integrity": {
            "paired_contrast_valid": integrity,
            "D_metric_consistency_with_KCL63": d_metric_consistency,
            "model_architecture_changed": False,
            "replay_budget_changed": False,
            "fuzzy_representation_changed": False,
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
            "adaptive_query_policy_started": False,
            "reasoning_work": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl64_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] == "PASS":
        return 0
    if result["status"] == "REVISE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
