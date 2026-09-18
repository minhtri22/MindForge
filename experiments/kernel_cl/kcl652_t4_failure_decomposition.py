"""KCL-6.5.2: seed-9393 T4 acquisition failure decomposition."""

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
from experiments.kernel_cl.kcl6_long_horizon import task_sequence, replay_task_index
from experiments.kernel_cl import kcl6_long_horizon as k6
from experiments.kernel_cl import kcl62_reconstructive_memory_abc as k62
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl65_specificity_ab as k65

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl652-protocol.md")
KCL651_EVIDENCE = Path("experiments/kernel_cl/results/kcl651_summary.json")

SEED = 9393
STRICT_T4_MIN = 0.95
TOLERANCE = 1 / 24
CHECKPOINTS = tuple(range(0, 251, 25))
EXTRA_CURRENT_GEN_OFFSET = 4999


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


def _model_equal(a: torch.nn.Module, b: torch.nn.Module) -> bool:
    return all(
        torch.equal(a.state_dict()[name], b.state_dict()[name])
        for name in a.state_dict()
    )


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL651_EVIDENCE.read_text(encoding="utf-8"))
    row = next((x for x in raw.get("per_seed", []) if int(x["seed"]) == SEED), None)
    valid = (
        raw.get("status") == "FAIL"
        and raw.get("verdict") == "TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE"
        and row is not None
        and abs(float(row["E_T4"]) - 0.75) < 1e-12
        and abs(float(row["F_T4"]) - 0.875) < 1e-12
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "seed_9393": row,
        "sha256": _sha256(KCL651_EVIDENCE),
    }


def _curve_point(model: torch.nn.Module, task: tuple[torch.Tensor, torch.Tensor], step: int) -> dict[str, Any]:
    metrics = evaluate(model, task)
    return {"step": step, "accuracy": metrics["accuracy"], "loss": metrics["loss"]}


def _curve_summary(curve: list[dict[str, Any]]) -> dict[str, Any]:
    first = next((p["step"] for p in curve if p["accuracy"] >= STRICT_T4_MIN), None)
    final = curve[-1]["accuracy"]
    max_acc = max(p["accuracy"] for p in curve)
    fell_after = False
    if first is not None:
        seen = False
        for p in curve:
            if p["step"] == first:
                seen = True
            elif seen and p["accuracy"] < STRICT_T4_MIN:
                fell_after = True
                break
    return {
        "steps_to_95_checkpoint": first,
        "final_accuracy": final,
        "max_accuracy": max_acc,
        "fell_below_95_after_first_reach": fell_after,
        "pass_95_final": final >= STRICT_T4_MIN,
    }


def _train_current_only_curve(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    task: tuple[torch.Tensor, torch.Tensor],
    *,
    generator_seed: int,
) -> dict[str, Any]:
    x, y = task
    gen = torch.Generator(device="cpu")
    gen.manual_seed(generator_seed)
    curve = [_curve_point(model, task, 0)]
    model.train()
    for step in range(1, 251):
        idx = torch.randint(0, len(y), (16,), generator=gen)
        loss = F.cross_entropy(model(x[idx])[:, -1, :], y[idx])
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite current-only loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if step in CHECKPOINTS:
            curve.append(_curve_point(model, task, step))
    return {"curve": curve, **_curve_summary(curve)}


def _build_post_t1(config: KCL1Config) -> tuple[torch.nn.Module, torch.optim.Optimizer]:
    tasks = task_sequence(config)
    model = build_model(config, SEED)
    optimizer = optimizer_for(model, config)
    train_stage(
        model, optimizer, tasks[0][1],
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=SEED + 101,
    )
    return model, optimizer


def _build_g1_post_t3(
    base: torch.nn.Module,
    base_opt: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[torch.nn.Module, torch.optim.Optimizer]:
    tasks = task_sequence(config)
    model = copy.deepcopy(base)
    optimizer = optimizer_for(model, config)
    optimizer.load_state_dict(copy.deepcopy(base_opt.state_dict()))
    for stage_idx in (1, 2):
        stage = stage_idx + 1
        train_stage(
            model,
            optimizer,
            tasks[stage_idx][1],
            steps=config.stage_steps,
            batch_size=16,
            seed=SEED + 1000 * stage + 307,
        )
    return model, optimizer


def _build_exact_post_t3(
    base: torch.nn.Module,
    base_opt: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[torch.nn.Module, torch.optim.Optimizer, list[k62.ReconstructiveStore]]:
    tasks = task_sequence(config)
    model = copy.deepcopy(base)
    optimizer = optimizer_for(model, config)
    optimizer.load_state_dict(copy.deepcopy(base_opt.state_dict()))
    stores = [k62.ReconstructiveStore.from_task(tasks[0][1])]
    for stage_idx in (1, 2):
        stage = stage_idx + 1
        k62._train_c_stage(
            model,
            optimizer,
            stores,
            tasks[stage_idx][1],
            steps=config.stage_steps,
            seed=SEED,
            stage=stage,
        )
        stores.append(k62.ReconstructiveStore.from_task(tasks[stage_idx][1]))
    return model, optimizer, stores


def _build_e_f_post_t3(
    base: torch.nn.Module,
    base_opt: torch.optim.Optimizer,
    config: KCL1Config,
) -> tuple[
    torch.nn.Module,
    torch.optim.Optimizer,
    list[k63.Memory],
    torch.nn.Module,
    torch.optim.Optimizer,
    list[k63.Memory],
]:
    tasks = task_sequence(config)

    model_e = copy.deepcopy(base)
    model_f = copy.deepcopy(base)
    opt_e = optimizer_for(model_e, config)
    opt_f = optimizer_for(model_f, config)
    opt_e.load_state_dict(copy.deepcopy(base_opt.state_dict()))
    opt_f.load_state_dict(copy.deepcopy(base_opt.state_dict()))

    memories_e: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
    memories_f: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]

    for stage_idx in (1, 2):
        stage = stage_idx + 1
        k65._train_stage_e_f(
            model_e,
            opt_e,
            memories_e,
            model_f,
            opt_f,
            memories_f,
            tasks[stage_idx][1],
            [task for _, task in tasks[:stage_idx]],
            steps=config.stage_steps,
            seed=SEED,
            stage=stage,
        )
        memories_e = k65._decay(memories_e)
        memories_f = k65._decay(memories_f)
        memories_e.append(k63.ExactMemory.from_task(tasks[stage_idx][1]))
        memories_f.append(k63.ExactMemory.from_task(tasks[stage_idx][1]))

    return model_e, opt_e, memories_e, model_f, opt_f, memories_f


def _train_t4_matched(
    g2_nr_model: torch.nn.Module,
    g2_nr_opt: torch.optim.Optimizer,
    g2_xr_model: torch.nn.Module,
    g2_xr_opt: torch.optim.Optimizer,
    exact_stores: list[k62.ReconstructiveStore],
    g3_model: torch.nn.Module,
    g3_opt: torch.optim.Optimizer,
    g3_memories: list[k63.Memory],
    g4_model: torch.nn.Module,
    g4_opt: torch.optim.Optimizer,
    g4_memories: list[k63.Memory],
    config: KCL1Config,
) -> dict[str, Any]:
    tasks = task_sequence(config)
    t4 = tasks[3][1]
    current_x, current_y = t4

    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(SEED + 4000 + 101)
    extra_gen = torch.Generator(device="cpu")
    extra_gen.manual_seed(SEED + EXTRA_CURRENT_GEN_OFFSET)

    rank_gens = []
    fuzzy_gens = []
    for i in range(3):
        rg = torch.Generator(device="cpu")
        rg.manual_seed(SEED + 4000 + 503 + 37 * i)
        rank_gens.append(rg)
        fg = torch.Generator(device="cpu")
        fg.manual_seed(SEED + 4000 + 1503 + 41 * i)
        fuzzy_gens.append(fg)

    curves = {
        "G2_NR": [_curve_point(g2_nr_model, t4, 0)],
        "G2_XR": [_curve_point(g2_xr_model, t4, 0)],
        "G3_E": [_curve_point(g3_model, t4, 0)],
        "G4_F": [_curve_point(g4_model, t4, 0)],
    }

    e_queried: set[int] = set()
    f_queried: set[int] = set()
    replay_stream_equal_xr_e = True
    current15_equal_by_construction = True
    g4_exact_matches = 0
    g2_xr_exact_matches = 0
    g3_exact_matches = 0
    replay_log: list[dict[str, Any]] = []

    for step0 in range(250):
        step = step0 + 1
        idx15 = torch.randint(0, len(current_y), (15,), generator=current_gen)
        cx15 = current_x[idx15]
        cy15 = current_y[idx15]

        idx_extra = torch.randint(0, len(current_y), (1,), generator=extra_gen)
        x_nr = torch.cat([cx15, current_x[idx_extra]], dim=0)
        y_nr = torch.cat([cy15, current_y[idx_extra]], dim=0)

        source = replay_task_index(step0, 3)
        rank = int(torch.randint(
            0, len(exact_stores[source].keys), (1,), generator=rank_gens[source]
        ).item())

        exact_obs = exact_stores[source].observation_at_rank(rank)
        xr_obs = exact_obs

        me = g3_memories[source]
        if isinstance(me, k63.FuzzyMemory):
            cue = k65._targeted_cue(me, tasks[source][1])
            me = me.reactivate_from_cue(cue)
            g3_memories[source] = me
            e_queried.add(source)
        e_obs = me.observation_at_rank(rank)

        mf = g4_memories[source]
        if isinstance(mf, k63.FuzzyMemory) and source not in f_queried:
            cue = k65._placebo_cue(t4)
            try:
                mf.reactivate_from_cue(cue)
            except ValueError:
                pass
            else:
                raise RuntimeError("G4 placebo unexpectedly reactivated fuzzy memory")
            f_queried.add(source)
        f_obs = mf.observation_at_rank(rank, fuzzy_gens[source])

        replay_stream_equal_xr_e = replay_stream_equal_xr_e and (xr_obs == e_obs)
        g2_xr_exact_matches += int(xr_obs == exact_obs)
        g3_exact_matches += int(e_obs == exact_obs)
        g4_exact_matches += int(f_obs == exact_obs)

        xr_x, xr_y = k65.k61.observation_to_tensors(xr_obs)
        e_x, e_y = k65.k61.observation_to_tensors(e_obs)
        f_x, f_y = k65.k61.observation_to_tensors(f_obs)

        batches = [
            (g2_nr_model, g2_nr_opt, x_nr, y_nr),
            (g2_xr_model, g2_xr_opt, torch.cat([cx15, xr_x], dim=0), torch.cat([cy15, xr_y], dim=0)),
            (g3_model, g3_opt, torch.cat([cx15, e_x], dim=0), torch.cat([cy15, e_y], dim=0)),
            (g4_model, g4_opt, torch.cat([cx15, f_x], dim=0), torch.cat([cy15, f_y], dim=0)),
        ]

        for model, optimizer, xb, yb in batches:
            loss = F.cross_entropy(model(xb)[:, -1, :], yb)
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite matched T4 loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

        replay_log.append({
            "step": step,
            "source": source,
            "rank": rank,
            "G2_XR_obs": list(xr_obs),
            "G3_E_obs": list(e_obs),
            "G4_F_obs": list(f_obs),
        })

        if step in CHECKPOINTS:
            curves["G2_NR"].append(_curve_point(g2_nr_model, t4, step))
            curves["G2_XR"].append(_curve_point(g2_xr_model, t4, step))
            curves["G3_E"].append(_curve_point(g3_model, t4, step))
            curves["G4_F"].append(_curve_point(g4_model, t4, step))

    return {
        "curves": curves,
        "summaries": {name: _curve_summary(curve) for name, curve in curves.items()},
        "queries": {
            "G3_E_sources": sorted(e_queried),
            "G4_F_sources": sorted(f_queried),
            "G3_E_count": len(e_queried),
            "G4_F_count": len(f_queried),
        },
        "replay": {
            "G2_XR_exact_match_rate": g2_xr_exact_matches / 250,
            "G3_E_exact_match_rate": g3_exact_matches / 250,
            "G4_F_exact_match_rate": g4_exact_matches / 250,
            "G2_XR_G3_stream_equal": replay_stream_equal_xr_e,
        },
        "current15_equal_by_construction": current15_equal_by_construction,
        "replay_log_sha256": hashlib.sha256(
            json.dumps(replay_log, sort_keys=True).encode("utf-8")
        ).hexdigest(),
    }


def classify(results: dict[str, float]) -> str:
    g0 = results["G0"]
    g1 = results["G1"]
    nr = results["G2_NR"]
    xr = results["G2_XR"]
    e = results["G3"]
    f = results["G4"]

    if g0 < STRICT_T4_MIN:
        return "INDEPENDENT_T4_LEARNABILITY_FAILURE"
    if g1 < STRICT_T4_MIN:
        return "SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE"
    if nr < STRICT_T4_MIN:
        return "EXACT_HISTORY_STATE_ACQUISITION_FAILURE"
    if (
        nr >= STRICT_T4_MIN
        and xr < STRICT_T4_MIN
        and e < STRICT_T4_MIN
    ):
        return "DIRECT_EXACT_REPLAY_INTERFERENCE"
    if xr >= STRICT_T4_MIN and e < STRICT_T4_MIN:
        return "E_POLICY_SPECIFIC_FAILURE"
    if xr >= STRICT_T4_MIN and e >= STRICT_T4_MIN and f < STRICT_T4_MIN:
        return "FUZZY_REPLAY_SPECIFIC_FAILURE"
    if xr >= STRICT_T4_MIN and e >= STRICT_T4_MIN and f >= STRICT_T4_MIN:
        return "FAILURE_NOT_REPRODUCED"
    return "MIXED_OR_UNRESOLVED"


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    config = KCL1Config()
    tasks = task_sequence(config)
    t4 = tasks[3][1]
    anchor = _load_anchor()

    if not anchor["valid"]:
        return {
            "experiment": "KCL-6.5.2",
            "status": "REVISE",
            "verdict": "T4_DECOMPOSITION_INVALID",
            "reason": "KCL-6.5.1 anchor invalid",
            "historical_anchor": anchor,
        }

    # G0 fresh T4 only.
    g0_model = build_model(config, SEED)
    g0_opt = optimizer_for(g0_model, config)
    g0 = _train_current_only_curve(
        g0_model, g0_opt, t4, generator_seed=SEED + 4000 + 307
    )

    # Shared post-T1 base for all sequential controls.
    base, base_opt = _build_post_t1(config)

    # G1 current-only sequential state through T3, then current-only T4.
    g1_model, g1_opt = _build_g1_post_t3(base, base_opt, config)
    g1 = _train_current_only_curve(
        g1_model, g1_opt, t4, generator_seed=SEED + 4000 + 307
    )

    # G2 exact reconstructive state through T3.
    exact_model, exact_opt, exact_stores = _build_exact_post_t3(base, base_opt, config)

    # G3/G4 frozen E/F state through T3.
    e_model, e_opt, e_memories, f_model, f_opt, f_memories = _build_e_f_post_t3(
        base, base_opt, config
    )

    exact_e_post_t3_model_equal = _model_equal(exact_model, e_model)
    exact_e_post_t3_optimizer_equal = _deep_equal(
        exact_opt.state_dict(), e_opt.state_dict()
    )

    # Matched fork from exact post-T3.
    g2_nr_model = copy.deepcopy(exact_model)
    g2_xr_model = copy.deepcopy(exact_model)
    g2_nr_opt = optimizer_for(g2_nr_model, config)
    g2_xr_opt = optimizer_for(g2_xr_model, config)
    g2_nr_opt.load_state_dict(copy.deepcopy(exact_opt.state_dict()))
    g2_xr_opt.load_state_dict(copy.deepcopy(exact_opt.state_dict()))

    pre_t4_fork_model_equal = _model_equal(g2_nr_model, g2_xr_model)
    pre_t4_fork_optimizer_equal = _deep_equal(
        g2_nr_opt.state_dict(), g2_xr_opt.state_dict()
    )

    matched = _train_t4_matched(
        g2_nr_model, g2_nr_opt,
        g2_xr_model, g2_xr_opt,
        exact_stores,
        e_model, e_opt, e_memories,
        f_model, f_opt, f_memories,
        config,
    )

    g2_xr_g3_final_model_equal = _model_equal(g2_xr_model, e_model)
    g2_xr_g3_final_optimizer_equal = _deep_equal(
        g2_xr_opt.state_dict(), e_opt.state_dict()
    )
    g2_xr_g3_curve_equal = matched["curves"]["G2_XR"] == matched["curves"]["G3_E"]

    finals = {
        "G0": g0["final_accuracy"],
        "G1": g1["final_accuracy"],
        "G2_NR": matched["summaries"]["G2_NR"]["final_accuracy"],
        "G2_XR": matched["summaries"]["G2_XR"]["final_accuracy"],
        "G3": matched["summaries"]["G3_E"]["final_accuracy"],
        "G4": matched["summaries"]["G4_F"]["final_accuracy"],
    }

    anomaly_reproduced = (
        abs(finals["G3"] - 0.75) <= TOLERANCE
        and abs(finals["G4"] - 0.875) <= TOLERANCE
    )

    finite = all(
        math.isfinite(float(p["accuracy"])) and math.isfinite(float(p["loss"]))
        for curve in [
            g0["curve"],
            g1["curve"],
            *matched["curves"].values(),
        ]
        for p in curve
    )

    equivalence = (
        exact_e_post_t3_model_equal
        and exact_e_post_t3_optimizer_equal
        and matched["replay"]["G2_XR_G3_stream_equal"]
        and g2_xr_g3_final_model_equal
        and g2_xr_g3_final_optimizer_equal
        and g2_xr_g3_curve_equal
    )

    integrity = (
        finite
        and pre_t4_fork_model_equal
        and pre_t4_fork_optimizer_equal
        and equivalence
        and anomaly_reproduced
        and matched["current15_equal_by_construction"]
        and math.isclose(matched["replay"]["G2_XR_exact_match_rate"], 1.0)
        and math.isclose(matched["replay"]["G3_E_exact_match_rate"], 1.0)
    )

    classification = classify(finals) if integrity else "UNCLASSIFIED"

    if not integrity:
        status, verdict = "REVISE", "T4_DECOMPOSITION_INVALID"
    else:
        status, verdict = "PASS", classification

    return {
        "experiment": "KCL-6.5.2",
        "status": status,
        "verdict": verdict,
        "seed": SEED,
        "historical_anchor": anchor,
        "arms": {
            "G0": "FRESH_T4_ONLY",
            "G1": "SEQUENTIAL_CURRENT_ONLY",
            "G2_NR": "EXACT_POST_T3_CURRENT_ONLY_T4",
            "G2_XR": "EXACT_POST_T3_EXACT_REPLAY_T4",
            "G3": "E_TARGETED_CLARIFICATION",
            "G4": "F_MATCHED_PLACEBO_FUZZY",
        },
        "final_T4_accuracy": finals,
        "curves": {
            "G0": g0["curve"],
            "G1": g1["curve"],
            **matched["curves"],
        },
        "curve_summaries": {
            "G0": {k: v for k, v in g0.items() if k != "curve"},
            "G1": {k: v for k, v in g1.items() if k != "curve"},
            **matched["summaries"],
        },
        "matched_T4": matched,
        "causal_classification": classification,
        "primary_contrasts": {
            "G2_NR_minus_G2_XR": finals["G2_NR"] - finals["G2_XR"],
            "G2_XR_minus_G3": finals["G2_XR"] - finals["G3"],
            "G3_minus_G4": finals["G3"] - finals["G4"],
        },
        "integrity": {
            "all_metrics_finite": finite,
            "G2_pre_T4_fork_model_equal": pre_t4_fork_model_equal,
            "G2_pre_T4_fork_optimizer_equal": pre_t4_fork_optimizer_equal,
            "exact_G3_post_T3_model_equal": exact_e_post_t3_model_equal,
            "exact_G3_post_T3_optimizer_equal": exact_e_post_t3_optimizer_equal,
            "G2_XR_G3_replay_stream_equal": matched["replay"]["G2_XR_G3_stream_equal"],
            "G2_XR_G3_final_model_equal": g2_xr_g3_final_model_equal,
            "G2_XR_G3_final_optimizer_equal": g2_xr_g3_final_optimizer_equal,
            "G2_XR_G3_curve_equal": g2_xr_g3_curve_equal,
            "G3_G4_anomaly_reproduced": anomaly_reproduced,
            "architecture_changed": False,
            "policy_changed": False,
            "kcl7_started": False,
        },
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "model_parameter_count": parameter_count(build_model(config, SEED)),
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
        default="experiments/kernel_cl/results/kcl652_summary.json",
    )
    args = parser.parse_args()

    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] == "PASS":
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
