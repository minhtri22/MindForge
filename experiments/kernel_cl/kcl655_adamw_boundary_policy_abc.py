"""KCL-6.5.5: validate AdamW boundary policies on full sequential CL."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
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
from experiments.kernel_cl.kcl6_long_horizon import TASK_ORDER, replay_task_index, task_sequence
from experiments.kernel_cl import kcl61_weighted_replay_ab as k61
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl65_specificity_ab as k65

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl655-protocol.md")
KCL654_EVIDENCE = Path("experiments/kernel_cl/results/kcl654_summary.json")
KCL651_EVIDENCE = Path("experiments/kernel_cl/results/kcl651_summary.json")

POLICIES = ("A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS")
FRESH_SEEDS = (
    9595, 9797, 9999, 10201, 10403,
    10605, 10807, 11009, 11211, 11413,
    11615, 11817, 12019, 12221, 12423,
    12625, 12827, 13029, 13231, 13433,
)
SENTINEL_SEED = 9393

STRICT_CURRENT_MIN = 0.95
RETENTION_MARGIN = 1 / 24
PLASTICITY_EQ_MARGIN = 0.01
BOOTSTRAP_RESAMPLES = 20000
BOOTSTRAP_SEED = 655655
REPRO_TOLERANCE = 1e-9
CHECKPOINTS = tuple(range(0, 251, 25))
FINAL_MEMORY_BYTES = 143


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


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


def _load_anchors() -> dict[str, Any]:
    k654 = json.loads(KCL654_EVIDENCE.read_text(encoding="utf-8"))
    k651 = json.loads(KCL651_EVIDENCE.read_text(encoding="utf-8"))
    sentinel_rows = [r for r in k651.get("per_seed", []) if int(r.get("seed", -1)) == SENTINEL_SEED]
    sentinel = sentinel_rows[0] if len(sentinel_rows) == 1 else {}
    valid = (
        k654.get("status") == "PASS"
        and k654.get("verdict") == "MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT"
        and k654.get("architecture_gap_candidate")
        == "ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION"
        and len(sentinel_rows) == 1
        and abs(float(sentinel.get("E_T4", -1)) - 0.75) <= REPRO_TOLERANCE
        and abs(float(sentinel.get("E_mean_prior", -1)) - 0.5000000049670538)
        <= REPRO_TOLERANCE
    )
    return {
        "valid": valid,
        "kcl654": {
            "status": k654.get("status"),
            "verdict": k654.get("verdict"),
            "sha256": _sha256(KCL654_EVIDENCE),
        },
        "sentinel_expected": {
            "A_T4": sentinel.get("E_T4"),
            "A_mean_prior": sentinel.get("E_mean_prior"),
            "source_sha256": _sha256(KCL651_EVIDENCE),
        },
    }


def _percentile(sorted_values: list[float], q: float) -> float:
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def paired_bootstrap(values: list[float]) -> dict[str, Any]:
    if len(values) != len(FRESH_SEEDS):
        raise ValueError("paired bootstrap requires frozen N=20 cohort")
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    means = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        means.append(statistics.fmean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    return {
        "mean": statistics.fmean(values),
        "ci_lower": _percentile(means, 0.025),
        "ci_upper": _percentile(means, 0.975),
        "resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "pstdev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def normalized_auc(curve: list[dict[str, Any]]) -> float:
    if [int(x["step"]) for x in curve] != list(CHECKPOINTS):
        raise ValueError("unexpected curve checkpoints")
    area = 0.0
    for left, right in zip(curve, curve[1:]):
        dx = float(right["step"] - left["step"])
        area += 0.5 * (float(left["accuracy"]) + float(right["accuracy"])) * dx
    return area / 250.0


def _curve_summary(curve: list[dict[str, Any]]) -> dict[str, Any]:
    hits = [int(x["step"]) for x in curve if float(x["accuracy"]) >= STRICT_CURRENT_MIN]
    return {
        "final_accuracy": float(curve[-1]["accuracy"]),
        "max_accuracy": max(float(x["accuracy"]) for x in curve),
        "steps_to_95_checkpoint": hits[0] if hits else None,
        "normalized_auc": normalized_auc(curve),
    }


def _curve_point(
    model: torch.nn.Module,
    task: tuple[torch.Tensor, torch.Tensor],
    step: int,
) -> dict[str, Any]:
    metric = evaluate(model, task)
    return {"step": step, "accuracy": metric["accuracy"], "loss": metric["loss"]}


def _optimizer_state_count(opt: torch.optim.Optimizer) -> int:
    return len(opt.state_dict()["state"])


def _moment_zero_and_steps(opt: torch.optim.Optimizer) -> dict[str, Any]:
    sd = opt.state_dict()
    steps = []
    moment_zero = True
    for state in sd["state"].values():
        steps.append(float(state["step"].item()))
        moment_zero = (
            moment_zero
            and bool((state["exp_avg"] == 0).all())
            and bool((state["exp_avg_sq"] == 0).all())
        )
    return {
        "state_count": len(sd["state"]),
        "steps": steps,
        "moment_zero": moment_zero,
    }


def _policy_boundary(
    policy: str,
    model: torch.nn.Module,
    opt: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[torch.optim.Optimizer, dict[str, Any]]:
    model_before = copy.deepcopy(model.state_dict())
    before_sd = copy.deepcopy(opt.state_dict())

    if policy == "A_CARRY_ALL":
        out = opt
        info = {
            "action": "carry_all",
            "optimizer_state_unchanged": _deep_equal(before_sd, out.state_dict()),
        }
    elif policy == "B_RESET_ALL":
        out = optimizer_for(model, config)
        info = {
            "action": "reset_all",
            "state_count_after": _optimizer_state_count(out),
        }
    elif policy == "C_CARRY_STEP_RESET_MOMENTS":
        sd = copy.deepcopy(before_sd)
        before_steps = [float(s["step"].item()) for s in sd["state"].values()]
        for state in sd["state"].values():
            state["exp_avg"].zero_()
            state["exp_avg_sq"].zero_()
        out = optimizer_for(model, config)
        out.load_state_dict(sd)
        after = _moment_zero_and_steps(out)
        info = {
            "action": "carry_step_reset_moments",
            "state_count_after": after["state_count"],
            "moment_zero_after": after["moment_zero"],
            "step_values_preserved": after["steps"] == before_steps,
            "step_values_after": after["steps"],
        }
    else:
        raise ValueError(policy)

    model_after = model.state_dict()
    info["model_unchanged"] = all(
        torch.equal(model_before[k], model_after[k]) for k in model_before
    )
    return out, info


def _logical_size(memory: k63.Memory) -> int:
    return len(memory.keys) if isinstance(memory, k63.ExactMemory) else memory.modulus


def _train_stage_lockstep(
    models: dict[str, torch.nn.Module],
    opts: dict[str, torch.optim.Optimizer],
    memories: list[k63.Memory],
    current_task: tuple[torch.Tensor, torch.Tensor],
    previous_tasks: list[tuple[torch.Tensor, torch.Tensor]],
    *,
    seed: int,
    stage: int,
) -> dict[str, Any]:
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)

    rank_gens = []
    for i in range(len(memories)):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(rg)

    queried: set[int] = set()
    query_events = []
    replay_counts = [0 for _ in memories]
    exact_matches = 0
    replay_log: list[tuple[int, int, tuple[int, int, int]]] = []

    curves = {
        p: [_curve_point(models[p], current_task, 0)]
        for p in POLICIES
    }

    xcur, ycur = current_task

    for step0 in range(250):
        idx = torch.randint(0, len(ycur), (15,), generator=current_gen)
        cx, cy = xcur[idx], ycur[idx]

        source = replay_task_index(step0, len(memories))
        replay_counts[source] += 1
        memory = memories[source]
        size = _logical_size(memory)
        rank = int(torch.randint(0, size, (1,), generator=rank_gens[source]).item())
        exact_obs = k63.canonical_observations(previous_tasks[source])[rank]

        if isinstance(memory, k63.FuzzyMemory):
            if source in queried:
                raise RuntimeError("reactivated source unexpectedly returned to fuzzy")
            cue = k65._targeted_cue(memory, previous_tasks[source])
            before = k65._candidate_count(memory)
            memory = memory.reactivate_from_cue(cue)
            memories[source] = memory
            queried.add(source)
            query_events.append({
                "step": step0,
                "source_index": source,
                "candidate_count_before": before,
                "candidate_count_after": 1,
                "query_training_examples": 0,
                "query_gradient_updates": 0,
                "raw_cue_retained": False,
            })

        obs = memory.observation_at_rank(rank)
        exact_matches += int(obs == exact_obs)
        replay_log.append((source, rank, obs))
        rx, ry = k61.observation_to_tensors(obs)
        xb = torch.cat([cx, rx], dim=0)
        yb = torch.cat([cy, ry], dim=0)

        for p in POLICIES:
            model = models[p]
            opt = opts[p]
            loss = F.cross_entropy(model(xb)[:, -1, :], yb)
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite loss for {p}")
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()

        step = step0 + 1
        if step in CHECKPOINTS:
            for p in POLICIES:
                curves[p].append(_curve_point(models[p], current_task, step))

    digest = hashlib.sha256(repr(replay_log).encode("utf-8")).hexdigest()
    return {
        "curves": curves,
        "curve_summary": {p: _curve_summary(curves[p]) for p in POLICIES},
        "query_count": len(query_events),
        "query_events": query_events,
        "replay_counts": replay_counts,
        "exact_replay_match_rate": exact_matches / 250,
        "replay_stream_sha256": digest,
    }


def _decay(memories: list[k63.Memory]) -> list[k63.Memory]:
    return [
        k63.FuzzyMemory.from_exact(m) if isinstance(m, k63.ExactMemory) else m
        for m in memories
    ]


def _eval_all(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    count: int,
) -> dict[str, dict[str, float]]:
    return {name: evaluate(model, task) for name, task in tasks[:count]}


def run_seed(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    names = [name for name, _ in tasks]

    base = build_model(config, seed)
    base_opt = optimizer_for(base, config)
    train_stage(
        base,
        base_opt,
        tasks[0][1],
        steps=250,
        batch_size=16,
        seed=seed + 101,
    )

    models = {p: copy.deepcopy(base) for p in POLICIES}
    opts: dict[str, torch.optim.Optimizer] = {}
    boundary_events: dict[str, list[dict[str, Any]]] = {p: [] for p in POLICIES}

    for p in POLICIES:
        opt = optimizer_for(models[p], config)
        opt.load_state_dict(copy.deepcopy(base_opt.state_dict()))
        opt, info = _policy_boundary(p, models[p], opt, config)
        info["after_task"] = "T1"
        boundary_events[p].append(info)
        opts[p] = opt

    fork_models_equal = all(
        all(
            torch.equal(models[POLICIES[0]].state_dict()[k], models[p].state_dict()[k])
            for k in models[POLICIES[0]].state_dict()
        )
        for p in POLICIES[1:]
    )

    memories: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    matrices = {
        p: {"after_T1": _eval_all(models[p], tasks, 1)}
        for p in POLICIES
    }
    stages: dict[str, Any] = {}

    for idx in range(1, 4):
        stage = idx + 1
        stage_name = f"after_T{stage}"
        stage_result = _train_stage_lockstep(
            models,
            opts,
            memories,
            tasks[idx][1],
            [t for _, t in tasks[:idx]],
            seed=seed,
            stage=stage,
        )
        stages[stage_name] = stage_result

        for p in POLICIES:
            matrices[p][stage_name] = _eval_all(models[p], tasks, idx + 1)

        memories = _decay(memories)
        memories.append(k63.ExactMemory.from_task(tasks[idx][1]))

        if stage < 4:
            for p in POLICIES:
                opts[p], info = _policy_boundary(p, models[p], opts[p], config)
                info["after_task"] = f"T{stage}"
                boundary_events[p].append(info)

    query_schedule = {s: stages[s]["query_count"] for s in stages}
    final_memory_states = [m.state for m in memories]
    final_memory_bytes = sum(m.logical_bytes for m in memories)

    per_policy: dict[str, Any] = {}
    for p in POLICIES:
        final = {
            n: matrices[p]["after_T4"][n]["accuracy"]
            for n in names
        }
        prior = names[:3]
        stage_curves = {
            s: stages[s]["curves"][p]
            for s in stages
        }
        stage_summaries = {
            s: stages[s]["curve_summary"][p]
            for s in stages
        }
        plasticity_auc = statistics.fmean(
            stage_summaries[s]["normalized_auc"]
            for s in ("after_T2", "after_T3", "after_T4")
        )
        strict_pass = all(
            stage_summaries[s]["final_accuracy"] >= STRICT_CURRENT_MIN
            for s in ("after_T2", "after_T3", "after_T4")
        )
        per_policy[p] = {
            "final_accuracy": final,
            "mean_prior_accuracy": statistics.fmean(final[n] for n in prior),
            "worst_prior_accuracy": min(final[n] for n in prior),
            "all_task_mean_accuracy": statistics.fmean(final.values()),
            "T4_accuracy": final[names[3]],
            "plasticity_auc": plasticity_auc,
            "stage_curves": stage_curves,
            "stage_summaries": stage_summaries,
            "strict_current_gate_all_stages": strict_pass,
            "boundary_events": boundary_events[p],
        }

    boundary_integrity = (
        all(
            e["model_unchanged"]
            and e["optimizer_state_unchanged"]
            for e in boundary_events["A_CARRY_ALL"]
        )
        and all(
            e["model_unchanged"]
            and e["state_count_after"] == 0
            for e in boundary_events["B_RESET_ALL"]
        )
        and all(
            e["model_unchanged"]
            and e["state_count_after"] > 0
            and e["moment_zero_after"]
            and e["step_values_preserved"]
            for e in boundary_events["C_CARRY_STEP_RESET_MOMENTS"]
        )
    )

    memory_integrity = (
        query_schedule == {"after_T2": 0, "after_T3": 1, "after_T4": 2}
        and all(math.isclose(stages[s]["exact_replay_match_rate"], 1.0) for s in stages)
        and final_memory_states == ["fuzzy", "fuzzy", "fuzzy", "exact"]
        and final_memory_bytes == FINAL_MEMORY_BYTES
        and all(
            q["query_training_examples"] == 0
            and q["query_gradient_updates"] == 0
            and q["raw_cue_retained"] is False
            for s in stages
            for q in stages[s]["query_events"]
        )
    )

    return {
        "seed": seed,
        "policies": per_policy,
        "shared_training": {
            "fork_models_equal": fork_models_equal,
            "query_schedule": query_schedule,
            "total_queries": sum(query_schedule.values()),
            "replay_stream_sha256_by_stage": {
                s: stages[s]["replay_stream_sha256"] for s in stages
            },
            "exact_replay_match_rate_by_stage": {
                s: stages[s]["exact_replay_match_rate"] for s in stages
            },
            "final_memory_states": final_memory_states,
            "final_memory_bytes": final_memory_bytes,
        },
        "integrity": {
            "boundary_policy_valid": boundary_integrity,
            "memory_query_replay_valid": memory_integrity,
            "training_data_shared_by_construction": True,
        },
    }


def _paired_contrast(
    rows: list[dict[str, Any]],
    lhs: str,
    rhs: str,
    metric: str,
) -> dict[str, Any]:
    values = [
        float(r["policies"][lhs][metric]) - float(r["policies"][rhs][metric])
        for r in rows
    ]
    return {
        "stats": _stats(values),
        "bootstrap": paired_bootstrap(values),
        "values": values,
    }


def _all_strict(rows: list[dict[str, Any]], policy: str) -> bool:
    return all(r["policies"][policy]["strict_current_gate_all_stages"] for r in rows)


def _qualify_policy(
    rows: list[dict[str, Any]],
    sentinel: dict[str, Any],
    policy: str,
    plasticity_vs_a: dict[str, Any],
    retention_vs_a: dict[str, Any],
) -> dict[str, Any]:
    plasticity = plasticity_vs_a["bootstrap"]["ci_lower"] > 0
    retention = retention_vs_a["bootstrap"]["ci_lower"] > -RETENTION_MARGIN
    absolute = _all_strict(rows, policy)
    sentinel_repair = sentinel["policies"][policy]["T4_accuracy"] >= STRICT_CURRENT_MIN
    return {
        "plasticity_improvement_vs_A": plasticity,
        "retention_noninferior_vs_A": retention,
        "absolute_current_gate_all_fresh": absolute,
        "sentinel_9393_repaired": sentinel_repair,
        "qualified": plasticity and retention and absolute and sentinel_repair,
    }


def _bc_classification(
    plasticity_cb: dict[str, Any],
    retention_cb: dict[str, Any],
) -> str:
    p = plasticity_cb["bootstrap"]
    r = retention_cb["bootstrap"]
    if p["ci_lower"] > 0 and r["ci_lower"] > -RETENTION_MARGIN:
        return "C_STEP_CARRY_ADDS_VALUE"
    if p["ci_upper"] < 0 and r["ci_upper"] < RETENTION_MARGIN:
        return "B_RESET_ALL_ADDS_VALUE"
    if (
        p["ci_lower"] >= -PLASTICITY_EQ_MARGIN
        and p["ci_upper"] <= PLASTICITY_EQ_MARGIN
        and r["ci_lower"] >= -RETENTION_MARGIN
        and r["ci_upper"] <= RETENTION_MARGIN
    ):
        return "B_C_PRACTICALLY_EQUIVALENT"
    return "B_C_NO_CLEAR_WINNER"


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    anchors = _load_anchors()
    config = KCL1Config()

    if not anchors["valid"]:
        return {
            "experiment": "KCL-6.5.5",
            "status": "REVISE",
            "verdict": "BOUNDARY_POLICY_ABC_INVALID",
            "reason": "upstream anchors invalid",
        }

    sentinel = run_seed(SENTINEL_SEED, config)
    sentinel_reproduced = (
        abs(
            sentinel["policies"]["A_CARRY_ALL"]["T4_accuracy"]
            - float(anchors["sentinel_expected"]["A_T4"])
        )
        <= REPRO_TOLERANCE
        and abs(
            sentinel["policies"]["A_CARRY_ALL"]["mean_prior_accuracy"]
            - float(anchors["sentinel_expected"]["A_mean_prior"])
        )
        <= REPRO_TOLERANCE
    )

    rows = [run_seed(seed, config) for seed in FRESH_SEEDS]

    integrity = (
        sentinel_reproduced
        and sentinel["integrity"]["boundary_policy_valid"]
        and sentinel["integrity"]["memory_query_replay_valid"]
        and all(
            r["integrity"]["boundary_policy_valid"]
            and r["integrity"]["memory_query_replay_valid"]
            and r["integrity"]["training_data_shared_by_construction"]
            for r in rows
        )
    )

    contrasts = {
        "plasticity_B_minus_A": _paired_contrast(
            rows, "B_RESET_ALL", "A_CARRY_ALL", "plasticity_auc"
        ),
        "plasticity_C_minus_A": _paired_contrast(
            rows, "C_CARRY_STEP_RESET_MOMENTS", "A_CARRY_ALL", "plasticity_auc"
        ),
        "plasticity_C_minus_B": _paired_contrast(
            rows, "C_CARRY_STEP_RESET_MOMENTS", "B_RESET_ALL", "plasticity_auc"
        ),
        "retention_B_minus_A": _paired_contrast(
            rows, "B_RESET_ALL", "A_CARRY_ALL", "mean_prior_accuracy"
        ),
        "retention_C_minus_A": _paired_contrast(
            rows, "C_CARRY_STEP_RESET_MOMENTS", "A_CARRY_ALL", "mean_prior_accuracy"
        ),
        "retention_C_minus_B": _paired_contrast(
            rows, "C_CARRY_STEP_RESET_MOMENTS", "B_RESET_ALL", "mean_prior_accuracy"
        ),
    }

    q_b = _qualify_policy(
        rows,
        sentinel,
        "B_RESET_ALL",
        contrasts["plasticity_B_minus_A"],
        contrasts["retention_B_minus_A"],
    )
    q_c = _qualify_policy(
        rows,
        sentinel,
        "C_CARRY_STEP_RESET_MOMENTS",
        contrasts["plasticity_C_minus_A"],
        contrasts["retention_C_minus_A"],
    )

    bc = _bc_classification(
        contrasts["plasticity_C_minus_B"],
        contrasts["retention_C_minus_B"],
    ) if q_b["qualified"] and q_c["qualified"] else None

    if not integrity:
        status = "REVISE"
        verdict = "BOUNDARY_POLICY_ABC_INVALID"
    elif q_c["qualified"] and not q_b["qualified"]:
        status = "PASS"
        verdict = "C_STEP_CARRY_RESET_MOMENTS_POLICY_VALIDATED"
    elif q_b["qualified"] and not q_c["qualified"]:
        status = "PASS"
        verdict = "B_RESET_ALL_POLICY_VALIDATED"
    elif q_b["qualified"] and q_c["qualified"]:
        status = "PASS"
        verdict = "B_AND_C_BOUNDARY_POLICIES_VALIDATED"
    else:
        improving_policies = [
            q for q in (q_b, q_c)
            if q["plasticity_improvement_vs_A"]
        ]
        # Frozen protocol applies retention non-inferiority to the same
        # intervention that claims a plasticity improvement. A different
        # policy preserving retention cannot rescue an improving policy
        # that itself loses retention.
        if (
            improving_policies
            and all(
                not q["retention_noninferior_vs_A"]
                for q in improving_policies
            )
        ):
            status = "FAIL"
            verdict = "BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION"
        else:
            status = "NEGATIVE"
            verdict = "NO_BOUNDARY_POLICY_PLASTICITY_ADVANTAGE"

    aggregates = {}
    for p in POLICIES:
        aggregates[p] = {
            "plasticity_auc": _stats([r["policies"][p]["plasticity_auc"] for r in rows]),
            "mean_prior_accuracy": _stats([
                r["policies"][p]["mean_prior_accuracy"] for r in rows
            ]),
            "worst_prior_accuracy": _stats([
                r["policies"][p]["worst_prior_accuracy"] for r in rows
            ]),
            "T4_accuracy": _stats([
                r["policies"][p]["T4_accuracy"] for r in rows
            ]),
            "strict_gate_pass_seeds": sum(
                r["policies"][p]["strict_current_gate_all_stages"] for r in rows
            ),
        }

    return {
        "experiment": "KCL-6.5.5",
        "status": status,
        "verdict": verdict,
        "policies": {
            "A": "CARRY_ALL",
            "B": "RESET_ALL",
            "C": "CARRY_STEP_RESET_MOMENTS",
        },
        "historical_anchors": anchors,
        "sentinel_9393": {
            "canonical_A_reproduced": sentinel_reproduced,
            "result": sentinel,
        },
        "primary_cohort": {
            "N": len(FRESH_SEEDS),
            "seeds": list(FRESH_SEEDS),
            "independent_of_prior_KCL_cohorts": True,
        },
        "aggregates": aggregates,
        "paired_contrasts": contrasts,
        "policy_qualification": {
            "B_RESET_ALL": q_b,
            "C_CARRY_STEP_RESET_MOMENTS": q_c,
        },
        "B_vs_C_secondary_classification": bc,
        "per_seed": rows,
        "gates": {
            "strict_current_min": STRICT_CURRENT_MIN,
            "retention_noninferiority_margin": RETENTION_MARGIN,
            "plasticity_equivalence_margin": PLASTICITY_EQ_MARGIN,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "integrity": {
            "valid": integrity,
            "sentinel_A_reproduced": sentinel_reproduced,
            "memory_policy_changed": False,
            "model_architecture_changed": False,
            "optimizer_hyperparameters_changed": False,
            "training_data_matched": True,
            "kcl7_started": False,
        },
        "model_parameter_count": parameter_count(build_model(config, FRESH_SEEDS[0])),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl655_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] in {"PASS", "NEGATIVE"}:
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
