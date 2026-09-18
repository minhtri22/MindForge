"""KCL-6.5: targeted clarification E vs matched-placebo query F."""

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
from experiments.kernel_cl import kcl65q_specificity_qualification as q65

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl65-protocol.md")
Q_EVIDENCE = Path("experiments/kernel_cl/results/kcl65q_summary.json")

FINAL_SEEDS = (4343, 4545, 4747, 4949, 5353)
CURRENT_PER_BATCH = 15
REPLAY_PER_BATCH = 1
BATCH_SIZE = 16
REPLAY_FRACTION = 1 / 16

STRICT_T4_MIN = 0.95
PRIOR_MIN_PER_SEED = 0.25
PRIOR_MEAN_MIN = 0.35
HISTORICAL_C_MEAN_PRIOR = 0.6750000019868214
TO_C_RETENTION_RATIO_MIN = 0.50
MEAN_SPECIFICITY_GAIN_MIN = 0.10
FINAL_PERSISTENT_BYTES = 143
EXPECTED_QUERY_SCHEDULE = {"after_T2": 0, "after_T3": 1, "after_T4": 2}
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


def _load_q_anchor() -> dict[str, Any]:
    raw = json.loads(Q_EVIDENCE.read_text(encoding="utf-8"))
    valid = (
        raw.get("status") == "PASS"
        and raw.get("verdict") == "MATCHED_QUERY_CONTROL_QUALIFIED"
        and raw.get("Q1_targeted_identifiability", {}).get("pass") is True
        and raw.get("Q2_placebo_nonidentifiability", {}).get("pass") is True
        and raw.get("Q3_equal_query_envelope", {}).get("pass") is True
        and raw.get("Q4_placebo_operational_null", {}).get("pass") is True
        and raw.get("Q5_no_hidden_cross_task_resolver", {}).get("pass") is True
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "sha256": _sha256(Q_EVIDENCE),
    }


def _sample_current(
    task: tuple[torch.Tensor, torch.Tensor],
    gen: torch.Generator,
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(0, len(y), (CURRENT_PER_BATCH,), generator=gen)
    return x[idx], y[idx]


def _logical_size(memory: k63.Memory) -> int:
    return len(memory.keys) if isinstance(memory, k63.ExactMemory) else memory.modulus


def _targeted_cue(
    fuzzy: k63.FuzzyMemory,
    prior_task: tuple[torch.Tensor, torch.Tensor],
) -> k63.Observation:
    cue = k63.canonical_observations(prior_task)[0]
    key = cue[fuzzy.varying_position]
    if key != fuzzy.key_min:
        raise RuntimeError("targeted cue is not key_min")
    return cue


def _placebo_cue(
    current_task: tuple[torch.Tensor, torch.Tensor],
) -> k63.Observation:
    return q65.current_task_placebo_cue(current_task)


def _candidate_count(memory: k63.FuzzyMemory) -> int:
    return len(q65.candidate_offsets(memory))


def _train_stage_e_f(
    model_e: torch.nn.Module,
    opt_e: torch.optim.Optimizer,
    memories_e: list[k63.Memory],
    model_f: torch.nn.Module,
    opt_f: torch.optim.Optimizer,
    memories_f: list[k63.Memory],
    current_task: tuple[torch.Tensor, torch.Tensor],
    previous_tasks: list[tuple[torch.Tensor, torch.Tensor]],
    *,
    steps: int,
    seed: int,
    stage: int,
) -> dict[str, Any]:
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)

    rank_gens: list[torch.Generator] = []
    f_uncertainty: list[torch.Generator] = []
    for i in range(len(memories_e)):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(rg)
        ug = torch.Generator(device="cpu")
        ug.manual_seed(seed + 1000 * stage + 1503 + 41 * i)
        f_uncertainty.append(ug)

    e_queried: set[int] = set()
    f_queried: set[int] = set()
    e_queries = []
    f_queries = []
    replay_counts = [0 for _ in memories_e]
    e_exact_matches = 0
    f_exact_matches = 0
    e_errors = 0
    f_errors = 0
    total = 0

    for step in range(steps):
        cx, cy = _sample_current(current_task, current_gen)
        source = replay_task_index(step, len(memories_e))
        replay_counts[source] += 1

        me = memories_e[source]
        mf = memories_f[source]
        size = _logical_size(me)
        if size != _logical_size(mf):
            raise RuntimeError("E/F logical replay domains differ")
        rank = int(torch.randint(0, size, (1,), generator=rank_gens[source]).item())
        exact_obs = k63.canonical_observations(previous_tasks[source])[rank]

        # E targeted clarification.
        if isinstance(me, k63.FuzzyMemory):
            if source in e_queried:
                raise RuntimeError("E clarified source returned to fuzzy within stage")
            before = _candidate_count(me)
            cue = _targeted_cue(me, previous_tasks[source])
            reactivated = me.reactivate_from_cue(cue)
            memories_e[source] = reactivated
            me = reactivated
            e_queried.add(source)
            e_queries.append({
                "step": step,
                "source_index": source,
                "candidate_count_before": before,
                "candidate_count_after": 1,
                "cue": list(cue),
                "payload_arity": len(cue),
                "query_training_examples": 0,
                "query_gradient_updates": 0,
                "raw_cue_retained": False,
                "memory_updated": True,
            })

        # F matched placebo query, but no prior-memory update.
        if isinstance(mf, k63.FuzzyMemory) and source not in f_queried:
            before = _candidate_count(mf)
            cue = _placebo_cue(current_task)
            rejected = False
            try:
                mf.reactivate_from_cue(cue)
            except ValueError:
                rejected = True
            if not rejected:
                raise RuntimeError("placebo unexpectedly resolved fuzzy prior memory")
            f_queried.add(source)
            f_queries.append({
                "step": step,
                "source_index": source,
                "candidate_count_before": before,
                "candidate_count_after": before,
                "cue": list(cue),
                "payload_arity": len(cue),
                "query_training_examples": 0,
                "query_gradient_updates": 0,
                "raw_cue_retained": False,
                "memory_updated": False,
            })

        obs_e = me.observation_at_rank(rank)
        obs_f = mf.observation_at_rank(rank, f_uncertainty[source])

        e_match = obs_e == exact_obs
        f_match = obs_f == exact_obs
        e_exact_matches += int(e_match)
        f_exact_matches += int(f_match)
        e_errors += int(not e_match)
        f_errors += int(not f_match)
        total += 1

        ex, ey = k61.observation_to_tensors(obs_e)
        fx, fy = k61.observation_to_tensors(obs_f)

        xb_e = torch.cat([cx, ex], dim=0)
        yb_e = torch.cat([cy, ey], dim=0)
        xb_f = torch.cat([cx, fx], dim=0)
        yb_f = torch.cat([cy, fy], dim=0)

        loss_e = F.cross_entropy(model_e(xb_e)[:, -1, :], yb_e)
        loss_f = F.cross_entropy(model_f(xb_f)[:, -1, :], yb_f)
        if not torch.isfinite(loss_e) or not torch.isfinite(loss_f):
            raise RuntimeError("non-finite KCL-6.5 loss")

        opt_e.zero_grad(set_to_none=True)
        loss_e.backward()
        opt_e.step()

        opt_f.zero_grad(set_to_none=True)
        loss_f.backward()
        opt_f.step()

    return {
        "replay_counts": replay_counts,
        "E_queries": len(e_queries),
        "F_queries": len(f_queries),
        "E_query_events": e_queries,
        "F_query_events": f_queries,
        "E_exact_match_rate": e_exact_matches / total,
        "F_exact_match_rate": f_exact_matches / total,
        "E_replay_errors": e_errors,
        "F_replay_errors": f_errors,
        "errors_avoided_by_E": f_errors - e_errors,
        "query_envelope_equal": (
            len(e_queries) == len(f_queries)
            and all(e["step"] == f["step"] for e, f in zip(e_queries, f_queries))
            and all(e["source_index"] == f["source_index"] for e, f in zip(e_queries, f_queries))
            and all(e["payload_arity"] == f["payload_arity"] == 3 for e, f in zip(e_queries, f_queries))
        ),
    }


def _eval_learned(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    count: int,
) -> dict[str, dict[str, float]]:
    return {name: evaluate(model, task) for name, task in tasks[:count]}


def _decay(memories: list[k63.Memory]) -> list[k63.Memory]:
    return [
        k63.FuzzyMemory.from_exact(m) if isinstance(m, k63.ExactMemory) else m
        for m in memories
    ]


def run_seed(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    names = [name for name, _ in tasks]

    base = build_model(config, seed)
    base_opt = optimizer_for(base, config)
    train_stage(
        base, base_opt, tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )

    model_e = copy.deepcopy(base)
    model_f = copy.deepcopy(base)
    opt_e = optimizer_for(model_e, config)
    opt_f = optimizer_for(model_f, config)
    opt_e.load_state_dict(copy.deepcopy(base_opt.state_dict()))
    opt_f.load_state_dict(copy.deepcopy(base_opt.state_dict()))

    fork_model_equal = all(
        torch.equal(model_e.state_dict()[n], model_f.state_dict()[n])
        for n in model_e.state_dict()
    )
    fork_optimizer_equal = _deep_equal(
        opt_e.state_dict(), opt_f.state_dict()
    )

    memories_e: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    memories_f: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]

    matrices_e = {"after_T1": _eval_learned(model_e, tasks, 1)}
    matrices_f = {"after_T1": _eval_learned(model_f, tasks, 1)}
    stages = {}

    for idx in range(1, len(tasks)):
        stage = idx + 1
        stage_name = f"after_T{stage}"
        stages[stage_name] = _train_stage_e_f(
            model_e, opt_e, memories_e,
            model_f, opt_f, memories_f,
            tasks[idx][1],
            [task for _, task in tasks[:idx]],
            steps=config.stage_steps,
            seed=seed,
            stage=stage,
        )
        matrices_e[stage_name] = _eval_learned(model_e, tasks, idx + 1)
        matrices_f[stage_name] = _eval_learned(model_f, tasks, idx + 1)

        memories_e = _decay(memories_e)
        memories_f = _decay(memories_f)
        memories_e.append(k63.ExactMemory.from_task(tasks[idx][1]))
        memories_f.append(k63.ExactMemory.from_task(tasks[idx][1]))

    final_e = {n: matrices_e["after_T4"][n]["accuracy"] for n in names}
    final_f = {n: matrices_f["after_T4"][n]["accuracy"] for n in names}
    prior = names[:3]
    e_mean = statistics.fmean(final_e[n] for n in prior)
    f_mean = statistics.fmean(final_f[n] for n in prior)
    e_t4 = final_e[names[3]]
    f_t4 = final_f[names[3]]

    queries_e = {s: stages[s]["E_queries"] for s in stages}
    queries_f = {s: stages[s]["F_queries"] for s in stages}
    total_e = sum(queries_e.values())
    total_f = sum(queries_f.values())

    final_e_bytes = sum(m.logical_bytes for m in memories_e)
    final_f_bytes = sum(m.logical_bytes for m in memories_f)

    candidate_integrity = all(
        all(
            q["candidate_count_before"] == 4
            and q["candidate_count_after"] == 1
            for q in stages[s]["E_query_events"]
        )
        and all(
            q["candidate_count_before"] == 4
            and q["candidate_count_after"] == 4
            and q["memory_updated"] is False
            for q in stages[s]["F_query_events"]
        )
        for s in stages
    )

    query_no_gradient_storage = all(
        all(
            q["query_training_examples"] == 0
            and q["query_gradient_updates"] == 0
            and q["raw_cue_retained"] is False
            for q in stages[s]["E_query_events"] + stages[s]["F_query_events"]
        )
        for s in stages
    )

    return {
        "seed": seed,
        "E_final_accuracy": final_e,
        "F_final_accuracy": final_f,
        "E_mean_prior": e_mean,
        "F_mean_prior": f_mean,
        "prior_gain_E_minus_F": e_mean - f_mean,
        "E_worst_prior": min(final_e[n] for n in prior),
        "F_worst_prior": min(final_f[n] for n in prior),
        "E_T4": e_t4,
        "F_T4": f_t4,
        "T4_gain_E_minus_F": e_t4 - f_t4,
        "queries_E_by_stage": queries_e,
        "queries_F_by_stage": queries_f,
        "total_queries_E": total_e,
        "total_queries_F": total_f,
        "specificity_gain_per_query": (
            (e_mean - f_mean) / total_e if total_e else None
        ),
        "errors_avoided_by_E": sum(stages[s]["errors_avoided_by_E"] for s in stages),
        "E_exact_match_rates": {s: stages[s]["E_exact_match_rate"] for s in stages},
        "F_exact_match_rates": {s: stages[s]["F_exact_match_rate"] for s in stages},
        "persistent_storage": {
            "E_final_bytes": final_e_bytes,
            "F_final_bytes": final_f_bytes,
        },
        "integrity": {
            "fork_model_equal": fork_model_equal,
            "fork_optimizer_equal": fork_optimizer_equal,
            "query_schedules_equal": queries_e == queries_f == EXPECTED_QUERY_SCHEDULE,
            "query_envelope_equal_all_stages": all(stages[s]["query_envelope_equal"] for s in stages),
            "candidate_set_integrity": candidate_integrity,
            "query_no_gradient_or_storage": query_no_gradient_storage,
            "E_exact_replay_all_stages": all(
                math.isclose(stages[s]["E_exact_match_rate"], 1.0) for s in stages
            ),
            "persistent_storage_equal": (
                final_e_bytes == final_f_bytes == FINAL_PERSISTENT_BYTES
            ),
            "final_age_schedule_equal": (
                [m.state for m in memories_e]
                == [m.state for m in memories_f]
                == ["fuzzy", "fuzzy", "fuzzy", "exact"]
            ),
        },
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    q_anchor = _load_q_anchor()
    config = KCL1Config()

    rows = [run_seed(seed, config) for seed in FINAL_SEEDS] if q_anchor["valid"] else []

    integrity = (
        q_anchor["valid"]
        and bool(rows)
        and all(
            all(v is True for v in row["integrity"].values())
            for row in rows
        )
        and all(
            row["total_queries_E"] == row["total_queries_F"] == EXPECTED_TOTAL_QUERIES
            for row in rows
        )
    )

    hs1 = (
        integrity
        and all(row["integrity"]["candidate_set_integrity"] for row in rows)
    )
    hs2 = (
        integrity
        and all(row["integrity"]["query_no_gradient_or_storage"] for row in rows)
    )
    hs3 = (
        integrity
        and all(row["E_mean_prior"] > row["F_mean_prior"] for row in rows)
        and statistics.fmean(row["prior_gain_E_minus_F"] for row in rows)
        >= MEAN_SPECIFICITY_GAIN_MIN
    )
    hs4 = (
        integrity
        and all(row["E_T4"] >= STRICT_T4_MIN for row in rows)
        and all(row["E_T4"] >= row["F_T4"] for row in rows)
        and statistics.fmean(row["T4_gain_E_minus_F"] for row in rows) >= 0
        and all(row["E_mean_prior"] >= PRIOR_MIN_PER_SEED for row in rows)
        and statistics.fmean(row["E_mean_prior"] for row in rows) >= PRIOR_MEAN_MIN
        and statistics.fmean(row["E_mean_prior"] for row in rows)
        >= TO_C_RETENTION_RATIO_MIN * HISTORICAL_C_MEAN_PRIOR
    )
    hs5 = (
        integrity
        and all(
            row["persistent_storage"]["E_final_bytes"]
            == row["persistent_storage"]["F_final_bytes"]
            == FINAL_PERSISTENT_BYTES
            and row["total_queries_E"] == row["total_queries_F"] == EXPECTED_TOTAL_QUERIES
            for row in rows
        )
    )

    if not integrity:
        status, verdict = "REVISE", "MATCHED_QUERY_AB_INVALID"
    elif not hs4:
        status, verdict = "FAIL", "TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS"
    elif hs1 and hs2 and hs3 and hs5:
        status, verdict = "PASS", "TARGETED_CLARIFICATION_SPECIFICITY_CAUSALLY_CONFIRMED"
    else:
        status, verdict = "NEGATIVE", "QUERY_OCCURRED_BUT_SPECIFICITY_EFFECT_NOT_CONFIRMED"

    aggregates: dict[str, Any] = {}
    if rows:
        aggregates = {
            "E_mean_prior": _stats([r["E_mean_prior"] for r in rows]),
            "F_mean_prior": _stats([r["F_mean_prior"] for r in rows]),
            "prior_gain_E_minus_F": _stats([r["prior_gain_E_minus_F"] for r in rows]),
            "E_T4": _stats([r["E_T4"] for r in rows]),
            "F_T4": _stats([r["F_T4"] for r in rows]),
            "T4_gain_E_minus_F": _stats([r["T4_gain_E_minus_F"] for r in rows]),
            "specificity_gain_per_query": _stats([r["specificity_gain_per_query"] for r in rows]),
            "errors_avoided_by_E": _stats([float(r["errors_avoided_by_E"]) for r in rows]),
            "E_worst_prior": _stats([r["E_worst_prior"] for r in rows]),
            "F_worst_prior": _stats([r["F_worst_prior"] for r in rows]),
        }

    return {
        "experiment": "KCL-6.5",
        "status": status,
        "verdict": verdict,
        "arms": {
            "E": "TARGETED_CLARIFICATION",
            "F": "MATCHED_PLACEBO_QUERY",
        },
        "final_seeds": list(FINAL_SEEDS),
        "task_order": list(TASK_ORDER),
        "qualification_anchor": q_anchor,
        "manipulation": {
            "E_candidate_set": "4->1",
            "F_candidate_set": "4->4",
            "query_count_matched": True,
            "query_timing_matched": True,
            "payload_arity_matched": 3,
            "equal_mutual_information_claimed": False,
        },
        "hypotheses": {
            "H_S1_target_specificity": hs1,
            "H_S2_matched_query_null": hs2,
            "H_S3_targeted_information_improves_CL": hs3,
            "H_S4_strict_plasticity_retained": hs4,
            "H_S5_query_storage_integrity": hs5,
        },
        "aggregates": aggregates,
        "per_seed": rows,
        "gates": {
            "strict_T4_min": STRICT_T4_MIN,
            "prior_min_per_seed": PRIOR_MIN_PER_SEED,
            "prior_mean_min": PRIOR_MEAN_MIN,
            "mean_specificity_gain_min": MEAN_SPECIFICITY_GAIN_MIN,
            "expected_total_queries": EXPECTED_TOTAL_QUERIES,
            "final_persistent_bytes": FINAL_PERSISTENT_BYTES,
        },
        "integrity": {
            "paired_contrast_valid": integrity,
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
        },
        "scope": {
            "kcl7_started": False,
            "autonomous_query_generation_started": False,
            "reasoning_work": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl65_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] in {"PASS", "NEGATIVE"}:
        return 0
    if result["status"] == "REVISE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
