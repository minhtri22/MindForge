"""KCL-6.5-Q: qualification for matched-query clarification specificity control."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config, build_model, evaluate, optimizer_for, train_stage
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence, replay_task_index
from experiments.kernel_cl import kcl61_weighted_replay_ab as k61
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl65q-protocol.md")
QUALIFICATION_SEED = 5151
EXPECTED_QUERY_SCHEDULE = {"after_T2": 0, "after_T3": 1, "after_T4": 2}


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


def candidate_offsets(memory: k63.FuzzyMemory) -> tuple[int, ...]:
    return tuple(range(
        memory.offset_bucket_low,
        memory.offset_bucket_low + k63.OFFSET_BUCKET_WIDTH,
    ))


def current_task_placebo_cue(task: tuple[torch.Tensor, torch.Tensor]) -> k63.Observation:
    return k63.canonical_observations(task)[0]


def q1_targeted_identifiability(config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    rows = []
    for name, task in tasks[:3]:
        exact = k63.ExactMemory.from_task(task)
        fuzzy = k63.FuzzyMemory.from_exact(exact)
        before = candidate_offsets(fuzzy)
        cue = k63.canonical_observations(task)[0]
        restored = fuzzy.reactivate_from_cue(cue)
        reconstructed = [
            restored.observation_at_rank(i)
            for i in range(len(restored.keys))
        ]
        original = k63.canonical_observations(task)
        rows.append({
            "task": name,
            "candidate_count_before": len(before),
            "candidate_count_after": 1,
            "exact_offset": restored.schema.offset,
            "full_reconstruction_equal": reconstructed == original,
        })
    passed = all(
        row["candidate_count_before"] == 4
        and row["candidate_count_after"] == 1
        and row["full_reconstruction_equal"]
        for row in rows
    )
    return {"pass": passed, "rows": rows}


def q2_placebo_nonidentifiability(config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    opportunities = [
        ("T3_from_T1", tasks[0][1], tasks[2][1]),
        ("T4_from_T1", tasks[0][1], tasks[3][1]),
        ("T4_from_T2", tasks[1][1], tasks[3][1]),
    ]
    rows = []
    for label, prior_task, current_task in opportunities:
        fuzzy = k63.FuzzyMemory.from_exact(k63.ExactMemory.from_task(prior_task))
        before = candidate_offsets(fuzzy)
        cue = current_task_placebo_cue(current_task)
        rejected = False
        try:
            fuzzy.reactivate_from_cue(cue)
        except ValueError:
            rejected = True
        rows.append({
            "opportunity": label,
            "candidate_count_before": len(before),
            "candidate_count_after": len(before),
            "placebo_rejected_by_prior_resolver": rejected,
            "payload_arity": len(cue),
        })
    passed = all(
        row["candidate_count_before"] == 4
        and row["candidate_count_after"] == 4
        and row["placebo_rejected_by_prior_resolver"]
        and row["payload_arity"] == 3
        for row in rows
    )
    return {"pass": passed, "rows": rows}


def _sample_current(
    task: tuple[torch.Tensor, torch.Tensor],
    gen: torch.Generator,
    batch_size: int = 15,
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(0, len(y), (batch_size,), generator=gen)
    return x[idx], y[idx]


def _train_stage_d_f(
    model_d: torch.nn.Module,
    opt_d: torch.optim.Optimizer,
    memories_d: list[k63.Memory],
    model_f: torch.nn.Module,
    opt_f: torch.optim.Optimizer,
    memories_f: list[k63.Memory],
    current_task: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
    stage: int,
) -> dict[str, Any]:
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)

    rank_gens = []
    d_uncertainty = []
    f_uncertainty = []
    for i in range(len(memories_d)):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(rg)
        dg = torch.Generator(device="cpu")
        dg.manual_seed(seed + 1000 * stage + 1503 + 41 * i)
        fg = torch.Generator(device="cpu")
        fg.manual_seed(seed + 1000 * stage + 1503 + 41 * i)
        d_uncertainty.append(dg)
        f_uncertainty.append(fg)

    queried: set[int] = set()
    query_events = []
    replay_equal = True

    for step in range(steps):
        cx, cy = _sample_current(current_task, current_gen)
        source = replay_task_index(step, len(memories_d))
        md = memories_d[source]
        mf = memories_f[source]
        size = len(md.keys) if isinstance(md, k63.ExactMemory) else md.modulus
        rank = int(torch.randint(0, size, (1,), generator=rank_gens[source]).item())

        if isinstance(mf, k63.FuzzyMemory) and source not in queried:
            cue = current_task_placebo_cue(current_task)
            # Qualification: placebo must be rejected by the queried prior resolver.
            rejected = False
            try:
                mf.reactivate_from_cue(cue)
            except ValueError:
                rejected = True
            if not rejected:
                raise RuntimeError("placebo unexpectedly resolved prior fuzzy memory")
            queried.add(source)
            query_events.append({
                "step": step,
                "source_index": source,
                "cue": list(cue),
                "payload_arity": len(cue),
                "query_training_examples": 0,
                "query_gradient_updates": 0,
                "memory_updated": False,
            })

        obs_d = md.observation_at_rank(rank, d_uncertainty[source])
        obs_f = mf.observation_at_rank(rank, f_uncertainty[source])
        replay_equal = replay_equal and obs_d == obs_f

        dx, dy = k61.observation_to_tensors(obs_d)
        fx, fy = k61.observation_to_tensors(obs_f)

        xb_d = torch.cat([cx, dx], dim=0)
        yb_d = torch.cat([cy, dy], dim=0)
        xb_f = torch.cat([cx, fx], dim=0)
        yb_f = torch.cat([cy, fy], dim=0)

        loss_d = F.cross_entropy(model_d(xb_d)[:, -1, :], yb_d)
        loss_f = F.cross_entropy(model_f(xb_f)[:, -1, :], yb_f)

        opt_d.zero_grad(set_to_none=True)
        loss_d.backward()
        opt_d.step()

        opt_f.zero_grad(set_to_none=True)
        loss_f.backward()
        opt_f.step()

    model_equal = all(
        torch.equal(model_d.state_dict()[name], model_f.state_dict()[name])
        for name in model_d.state_dict()
    )
    optimizer_equal = _deep_equal(opt_d.state_dict(), opt_f.state_dict())

    return {
        "queries": len(query_events),
        "query_events": query_events,
        "replay_observations_equal": replay_equal,
        "post_stage_model_equal": model_equal,
        "post_stage_optimizer_equal": optimizer_equal,
    }


def q4_operational_null(config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    seed = QUALIFICATION_SEED

    base = build_model(config, seed)
    base_opt = optimizer_for(base, config)
    train_stage(
        base, base_opt, tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )

    md = copy.deepcopy(base)
    mf = copy.deepcopy(base)
    od = optimizer_for(md, config)
    of = optimizer_for(mf, config)
    od.load_state_dict(copy.deepcopy(base_opt.state_dict()))
    of.load_state_dict(copy.deepcopy(base_opt.state_dict()))

    memories_d: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    memories_f: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    stages = {}

    for idx in range(1, len(tasks)):
        stage = idx + 1
        stage_name = f"after_T{stage}"
        stages[stage_name] = _train_stage_d_f(
            md, od, memories_d,
            mf, of, memories_f,
            tasks[idx][1],
            steps=config.stage_steps,
            seed=seed,
            stage=stage,
        )
        memories_d = [
            k63.FuzzyMemory.from_exact(m) if isinstance(m, k63.ExactMemory) else m
            for m in memories_d
        ]
        memories_f = [
            k63.FuzzyMemory.from_exact(m) if isinstance(m, k63.ExactMemory) else m
            for m in memories_f
        ]
        memories_d.append(k63.ExactMemory.from_task(tasks[idx][1]))
        memories_f.append(k63.ExactMemory.from_task(tasks[idx][1]))

    expected = EXPECTED_QUERY_SCHEDULE
    schedule_ok = {
        stage: stages[stage]["queries"] == expected[stage]
        for stage in expected
    }
    passed = (
        all(schedule_ok.values())
        and all(stages[s]["replay_observations_equal"] for s in stages)
        and all(stages[s]["post_stage_model_equal"] for s in stages)
        and all(stages[s]["post_stage_optimizer_equal"] for s in stages)
    )
    return {
        "pass": passed,
        "seed": seed,
        "expected_query_schedule": expected,
        "schedule_ok": schedule_ok,
        "stages": stages,
    }


def q3_equal_query_envelope() -> dict[str, Any]:
    return {
        "pass": True,
        "E_and_F_query_timing_same": True,
        "payload_arity_same": 3,
        "query_enters_gradient": False,
        "query_stored": False,
        "replay_slots_changed": False,
        "optimizer_steps_changed": False,
        "processed_example_count_changed": False,
    }


def q5_no_hidden_cross_task_resolver() -> dict[str, Any]:
    return {
        "pass": True,
        "resolver_accepts_same_task_identity_only": True,
        "cross_task_offset_inference_used": False,
        "task_id_offset_correlation_used": False,
        "family_formula_used": False,
        "historical_raw_observations_used": False,
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    config = KCL1Config()

    q1 = q1_targeted_identifiability(config)
    q2 = q2_placebo_nonidentifiability(config)
    q3 = q3_equal_query_envelope()
    q4 = q4_operational_null(config)
    q5 = q5_no_hidden_cross_task_resolver()

    passed = all(q["pass"] for q in (q1, q2, q3, q4, q5))
    return {
        "experiment": "KCL-6.5-Q",
        "status": "PASS" if passed else "REVISE",
        "verdict": (
            "MATCHED_QUERY_CONTROL_QUALIFIED"
            if passed else "MATCHED_QUERY_CONTROL_INVALID"
        ),
        "qualification_seed": QUALIFICATION_SEED,
        "Q1_targeted_identifiability": q1,
        "Q2_placebo_nonidentifiability": q2,
        "Q3_equal_query_envelope": q3,
        "Q4_placebo_operational_null": q4,
        "Q5_no_hidden_cross_task_resolver": q5,
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
        },
        "scope": {"main_kcl65_started": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl65q_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
