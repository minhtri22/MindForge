"""CLRM-1 loss-response support qualification.

No predictor is fitted. Fresh Role-S execution is blocked until independent
verification of the exact CLRM-1 execution lock.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any, Iterable

import torch

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    evaluate,
    optimizer_for,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655

PROGRAM = "CLRM-1"
PROTOCOL = Path("docs/research/continual-loss-response/clrm1-loss-response-support-protocol.md")
SEED_MANIFEST = Path("docs/research/continual-loss-response/CLRM1_ROLE_S_SEED_MANIFEST.json")
EXECUTION_LOCK = Path("docs/research/continual-loss-response/CLRM1_EXECUTION_LOCK.json")
LOCK_VERIFICATION = Path("docs/research/continual-loss-response/CLRM1_EXECUTION_LOCK_VERIFICATION.md")
DEFAULT_RECORDS = Path("experiments/clrm/results/clrm1_role_s_responses.json")
DEFAULT_FORMAL = Path("experiments/clrm/results/CLRM1_FORMAL_RESULT.json")

MSA1_RUNNER = Path("experiments/msa/msa1_endpoint_adequacy.py")
MSA3_RUNNER = Path("experiments/msa/msa3_independent_replication.py")

POLICIES = ("A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS")
A_POLICY = POLICIES[0]

SEED_GENERATION_PHRASE = "MindForge|CLRM-1|role-s-loss-response-support|v1"
FRESH_SEEDS = (3010487,6390804,7554778,6421546,8255747,3221303,4920374,6284346,4716387,5672294,6811595,5893018,8611908,3537915,3904505,6328288,3828589,5858064,7762622,7393682,7860013,6639705,2326389,2733788,6182716,7681758,4502424,4542422,4883553,7560158,6740910,6765774,5812757,6374908,6785962,5738725,5242548,3626182,8429721,5169376,7906970,7389765,2621346,5051772,3290569,4656879,4458089,6890844,7215063,6226921,7653913,7095910,8732714,7547285,7882034,4917790,4193824,3048847,5211537,5003679,5923954,3107127,8263759,5352954,4767982,5964534,7997783,5425848,2302199,4020310,5879011,7559240,)
SEED_MANIFEST_SHA256 = "3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6"
RELIABILITY_SEEDS = FRESH_SEEDS[:6]

EXPECTED_SEEDS = 72
EXPECTED_BOUNDARIES = 216
EXPECTED_PER_STAGE = 72
EXPECTED_POLICY_RESPONSES = 648

CELL_MIN_UNIQUE = 10
CELL_MIN_ROBUST_SPAN = 0.02
CHANNEL_MIN_QUALIFIED_STAGES = 2

HISTORICAL_PROBE_SEED = 9595

PROTECTED_KCL_SEEDS = (
    13635,13837,14039,14241,14443,
    14645,14847,15049,15251,15453,
    15655,15857,16059,16261,16463,
    16665,16867,17069,17271,17473,
)

EXPECTED_SPENT_HASHES = {
    "ACO-1": "9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91",
    "CPRM-1": "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3",
    "MSA-1": "e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347",
    "MSA-3": "5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8",
}

SUBSTRATE_BLOBS = {
    "experiments/kernel_cl/kcl1_substrate.py": "4303dd544e0bdb935c499abedc62aa095bc56674",
    "experiments/kernel_cl/kcl6_long_horizon.py": "33a743d62b5a83286c8945ffc0f473ae66fe50c0",
    "experiments/kernel_cl/kcl61_weighted_replay_ab.py": "9a2ea8435bc92d65af7044b5351d06adc6cc2d44",
    "experiments/kernel_cl/kcl63_fuzzy_decay_abcd.py": "cb6cf442d9d6a01c6cec173ecd73771fc6ba30c7",
    "experiments/kernel_cl/kcl65_specificity_ab.py": "88aa11fea6e8474c323c02491c0b85a91722c686",
    "experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py": "7119b9520f50de53a42313f7c7173c8d5daec2f1",
    "mindforge/config.py": "54ab270a25edd962e62360e14736b28f52a4fbcd",
    "mindforge/model.py": "3f6b8f1f411d7a3ba061d4bca10cd0002ae91594",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(values: Iterable[int]) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def git_blob(path: str | Path) -> str:
    return git("hash-object", str(path))


def _literal_assignments(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            out[target.id] = ast.literal_eval(node.value)
        except Exception:
            pass
    return out


def regenerate_fresh_seeds() -> tuple[int, ...]:
    accepted: list[int] = []
    seen: set[int] = set()
    i = 0
    while len(accepted) < EXPECTED_SEEDS:
        digest = hashlib.sha256(f"{SEED_GENERATION_PHRASE}|{i}".encode()).digest()
        candidate = 2_000_000 + (int.from_bytes(digest[:8], "big") % 7_000_000)
        if candidate not in seen:
            accepted.append(candidate)
            seen.add(candidate)
        i += 1
    return tuple(accepted)


def _historical_kcl_seed_candidates() -> set[int]:
    paths = [Path("Lineage.md")]
    for base in (
        Path("docs/research/kernel-continual-learning"),
        Path("experiments/kernel_cl"),
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out: set[int] = set()
    for path in paths:
        try:
            txt = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in txt.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


def _spent_sets() -> dict[str, set[int]]:
    m1 = _literal_assignments(MSA1_RUNNER)
    m3 = _literal_assignments(MSA3_RUNNER)
    return {
        "ACO-1": set(int(x) for x in m1["SPENT_ACO_SEEDS"]),
        "CPRM-1": set(int(x) for x in m1["SPENT_CPRM_SEEDS"]),
        "MSA-1": set(int(x) for x in m1["FRESH_SEEDS"]),
        "MSA-3": set(int(x) for x in m3["FRESH_SEEDS"]),
    }


def validate_seed_manifest() -> dict[str, Any]:
    fresh = set(FRESH_SEEDS)
    spent = _spent_sets()
    historical = _historical_kcl_seed_candidates()
    protected = set(PROTECTED_KCL_SEEDS)
    source_manifest = json.loads(SEED_MANIFEST.read_text(encoding="utf-8"))
    checks = {
        "count_72": len(FRESH_SEEDS) == EXPECTED_SEEDS,
        "unique_72": len(fresh) == EXPECTED_SEEDS,
        "regeneration_exact": regenerate_fresh_seeds() == FRESH_SEEDS,
        "manifest_hash_exact": manifest_hash(FRESH_SEEDS) == SEED_MANIFEST_SHA256,
        "manifest_file_hash_exact": source_manifest["sha256"] == SEED_MANIFEST_SHA256,
        "manifest_file_sequence_exact": tuple(source_manifest["seeds"]) == FRESH_SEEDS,
        "historical_kcl_disjoint": fresh.isdisjoint(historical),
        "protected_kcl_disjoint": fresh.isdisjoint(protected),
    }
    collisions = {
        "historical_kcl": sorted(fresh & historical),
        "protected_kcl": sorted(fresh & protected),
    }
    spent_hashes: dict[str, str] = {}
    for name, values in spent.items():
        spent_hashes[name] = manifest_hash(tuple(
            _literal_assignments(MSA1_RUNNER)["SPENT_ACO_SEEDS"]
            if name == "ACO-1" else
            _literal_assignments(MSA1_RUNNER)["SPENT_CPRM_SEEDS"]
            if name == "CPRM-1" else
            _literal_assignments(MSA1_RUNNER)["FRESH_SEEDS"]
            if name == "MSA-1" else
            _literal_assignments(MSA3_RUNNER)["FRESH_SEEDS"]
        ))
        checks[f"{name}_hash_exact"] = spent_hashes[name] == EXPECTED_SPENT_HASHES[name]
        checks[f"{name}_disjoint"] = fresh.isdisjoint(values)
        collisions[name] = sorted(fresh & values)
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "collisions": collisions,
        "spent_hashes": spent_hashes,
        "manifest_sha256": manifest_hash(FRESH_SEEDS),
    }


def frozen_substrate_snapshot() -> dict[str, Any]:
    cfg = KCL1Config()
    checks = {
        "config_exact": (
            cfg.vocab_size == 96 and cfg.d_model == 16 and cfg.n_heads == 2
            and cfg.n_layers == 1 and cfg.max_context == 2 and cfg.ff_mult == 4
            and cfg.dropout == 0.0 and cfg.relations == 24 and cfg.batch_size == 16
            and cfg.stage_steps == 250 and cfg.learning_rate == 3e-3
            and cfg.weight_decay == 0.0
        ),
        "task_order_exact": [x[0] for x in task_sequence(cfg)] == [
            "T1_U1_A", "T2_U1_B", "T3_U3_A", "T4_U3_B"
        ],
        "policies_exact": tuple(k655.POLICIES) == POLICIES,
        "checkpoints_exact": tuple(k655.CHECKPOINTS) == tuple(range(0, 251, 25)),
        "source_blobs_exact": all(git_blob(p) == sha for p, sha in SUBSTRATE_BLOBS.items()),
    }
    return {"valid": all(checks.values()), "checks": checks}


def _clone_model_opt(model, opt, cfg):
    m = copy.deepcopy(model)
    o = optimizer_for(m, cfg)
    o.load_state_dict(copy.deepcopy(opt.state_dict()))
    return m, o


def _state_copy(model: torch.nn.Module) -> dict[str, torch.Tensor]:
    return {k: v.detach().clone() for k, v in model.state_dict().items()}


def _state_equal(before: dict[str, torch.Tensor], model: torch.nn.Module) -> bool:
    now = model.state_dict()
    return all(torch.equal(before[k], now[k]) for k in before)


def run_response_counterfactual(
    *,
    model,
    optimizer,
    memories,
    observed_tasks,
    next_task,
    seed,
    next_stage,
    cfg,
):
    models = {}
    opts = {}
    infos = {}
    for policy in POLICIES:
        m, o = _clone_model_opt(model, optimizer, cfg)
        o, info = k655._policy_boundary(policy, m, o, cfg)
        models[policy] = m
        opts[policy] = o
        infos[policy] = info

    fork_equal = all(
        all(
            torch.equal(
                models[A_POLICY].state_dict()[name],
                models[p].state_dict()[name],
            )
            for name in models[A_POLICY].state_dict()
        )
        for p in POLICIES[1:]
    )

    memory_copy = copy.deepcopy(memories)
    stage = k655._train_stage_lockstep(
        models,
        opts,
        memory_copy,
        next_task[1],
        [task for _, task in observed_tasks],
        seed=seed,
        stage=next_stage,
    )

    responses: dict[str, Any] = {}
    same_state_ok = True
    current_curve_ok = True

    for policy in POLICIES:
        m = models[policy]
        before = _state_copy(m)

        current_metric = evaluate(m, next_task[1])
        prior_metrics = [
            (name, evaluate(m, task))
            for name, task in observed_tasks
        ]

        same_state = _state_equal(before, m)
        same_state_ok = same_state_ok and same_state

        point = stage["curves"][policy][-1]
        curve_match = (
            int(point["step"]) == 250
            and float(point["accuracy"]) == float(current_metric["accuracy"])
            and float(point["loss"]) == float(current_metric["loss"])
        )
        current_curve_ok = current_curve_ok and curve_match

        prior_losses = {
            name: float(metric["loss"]) for name, metric in prior_metrics
        }
        prior_accuracies = {
            name: float(metric["accuracy"]) for name, metric in prior_metrics
        }

        responses[policy] = {
            "current_loss": float(current_metric["loss"]),
            "prior_mean_loss": statistics.fmean(prior_losses.values()),
            "step": 250,
            "prior_task_losses": prior_losses,
            "accuracy_sentinel": {
                "current_terminal_accuracy": float(current_metric["accuracy"]),
                "min_prior_terminal_accuracy": min(prior_accuracies.values()),
                "prior_task_accuracies": prior_accuracies,
            },
            "same_terminal_state_verified": same_state,
            "current_curve_point_exact": curve_match,
        }

    integrity = {
        "fork_models_equal": fork_equal,
        "boundary_model_unchanged": all(bool(x["model_unchanged"]) for x in infos.values()),
        "exact_replay_match": math.isclose(
            float(stage["exact_replay_match_rate"]), 1.0, abs_tol=0.0, rel_tol=0.0
        ),
        "same_terminal_state_for_both_loss_axes": same_state_ok,
        "current_curve_point_exact": current_curve_ok,
    }
    integrity["valid"] = all(integrity.values())

    next_memories = k655._decay(memory_copy)
    next_memories.append(k63.ExactMemory.from_task(next_task[1]))

    return {
        "responses": responses,
        "integrity": integrity,
        "_reference_model": models[A_POLICY],
        "_reference_optimizer": opts[A_POLICY],
        "_next_memories": next_memories,
    }


def build_response_records(seed: int, cfg: KCL1Config | None = None) -> list[dict[str, Any]]:
    cfg = cfg or KCL1Config()
    tasks = task_sequence(cfg)

    model = build_model(cfg, seed)
    opt = optimizer_for(model, cfg)
    train_stage(
        model,
        opt,
        tasks[0][1],
        steps=250,
        batch_size=16,
        seed=seed + 101,
    )

    memories = [k63.ExactMemory.from_task(tasks[0][1])]
    observed = [tasks[0]]
    rows: list[dict[str, Any]] = []

    for boundary in (1, 2, 3):
        next_task = tasks[boundary]
        out = run_response_counterfactual(
            model=model,
            optimizer=opt,
            memories=memories,
            observed_tasks=observed,
            next_task=next_task,
            seed=seed,
            next_stage=boundary + 1,
            cfg=cfg,
        )
        rows.append({
            "seed": int(seed),
            "boundary_index": boundary,
            "after_task": observed[-1][0],
            "next_task": next_task[0],
            "prior_task_count": len(observed),
            "responses": out["responses"],
            "integrity": out["integrity"],
        })
        model = out["_reference_model"]
        opt = out["_reference_optimizer"]
        memories = out["_next_memories"]
        observed = tasks[:boundary + 1]

    return rows


def compare_repeat(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> dict[str, Any]:
    av: list[float] = []
    bv: list[float] = []
    for ra, rb in zip(a, b):
        for p in POLICIES:
            ea, eb = ra["responses"][p], rb["responses"][p]
            av += [
                ea["current_loss"],
                ea["prior_mean_loss"],
                ea["accuracy_sentinel"]["current_terminal_accuracy"],
                ea["accuracy_sentinel"]["min_prior_terminal_accuracy"],
            ]
            bv += [
                eb["current_loss"],
                eb["prior_mean_loss"],
                eb["accuracy_sentinel"]["current_terminal_accuracy"],
                eb["accuracy_sentinel"]["min_prior_terminal_accuracy"],
            ]
            for name in sorted(ea["prior_task_losses"]):
                av += [
                    ea["prior_task_losses"][name],
                    ea["accuracy_sentinel"]["prior_task_accuracies"][name],
                ]
                bv += [
                    eb["prior_task_losses"][name],
                    eb["accuracy_sentinel"]["prior_task_accuracies"][name],
                ]
    md = max(abs(float(x) - float(y)) for x, y in zip(av, bv))
    structure = [
        (r["seed"], r["boundary_index"], r["prior_task_count"], sorted(r["responses"]), r["integrity"])
        for r in a
    ] == [
        (r["seed"], r["boundary_index"], r["prior_task_count"], sorted(r["responses"]), r["integrity"])
        for r in b
    ]
    return {
        "max_abs_diff": md,
        "same_structure": structure,
        "exact": md == 0.0 and structure,
    }


def _row_valid(r: dict[str, Any]) -> bool:
    if not bool(r["integrity"]["valid"]):
        return False
    boundary = int(r["boundary_index"])
    if boundary not in {1, 2, 3}:
        return False
    if int(r["prior_task_count"]) != boundary:
        return False
    if set(r["responses"]) != set(POLICIES):
        return False
    for p in POLICIES:
        e = r["responses"][p]
        if int(e["step"]) != 250:
            return False
        if not bool(e["same_terminal_state_verified"]):
            return False
        if not bool(e["current_curve_point_exact"]):
            return False
        if len(e["prior_task_losses"]) != boundary:
            return False
        cur = float(e["current_loss"])
        prior = float(e["prior_mean_loss"])
        ca = float(e["accuracy_sentinel"]["current_terminal_accuracy"])
        pa = float(e["accuracy_sentinel"]["min_prior_terminal_accuracy"])
        if not (
            math.isfinite(cur) and cur >= 0.0
            and math.isfinite(prior) and prior >= 0.0
            and math.isfinite(ca) and 0.0 <= ca <= 1.0
            and math.isfinite(pa) and 0.0 <= pa <= 1.0
        ):
            return False
    return True


def support_integrity(
    records: list[dict[str, Any]],
    expected_seeds: Iterable[int] = FRESH_SEEDS,
) -> dict[str, Any]:
    expected = set(int(x) for x in expected_seeds)
    observed = set(int(r["seed"]) for r in records)
    per_seed = {s: 0 for s in expected}
    per_stage = {1: 0, 2: 0, 3: 0}
    policy_responses = 0

    for r in records:
        seed = int(r["seed"])
        stage = int(r["boundary_index"])
        if seed in per_seed:
            per_seed[seed] += 1
        if stage in per_stage:
            per_stage[stage] += 1
        policy_responses += len(r.get("responses", {}))

    n = len(expected)
    checks = {
        "seed_set_exact": observed == expected,
        "seed_count_exact": len(observed) == n,
        "records_exact": len(records) == n * 3,
        "three_boundaries_per_seed": all(v == 3 for v in per_seed.values()),
        "stage_counts_exact": per_stage == {1: n, 2: n, 3: n},
        "policy_response_count_exact": policy_responses == n * 3 * 3,
        "all_rows_valid": all(_row_valid(r) for r in records),
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "per_stage": per_stage,
        "policy_response_count": policy_responses,
    }


def _percentile(values: list[float], q: float) -> float:
    xs = sorted(float(x) for x in values)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[int(lo)]
    frac = pos - lo
    return xs[int(lo)] * (1 - frac) + xs[int(hi)] * frac


def _cell(values: list[float]) -> dict[str, Any]:
    p10 = _percentile(values, 0.10)
    p90 = _percentile(values, 0.90)
    span = p90 - p10
    unique = len(set(values))
    qualified = unique >= CELL_MIN_UNIQUE and span >= CELL_MIN_ROBUST_SPAN
    return {
        "n": len(values),
        "unique_count": unique,
        "p10": p10,
        "p90": p90,
        "robust_span": span,
        "qualified": qualified,
    }


def response_geometry(records: list[dict[str, Any]]) -> dict[str, Any]:
    channels: dict[str, Any] = {}
    for policy in POLICIES:
        for metric in ("current_loss", "prior_mean_loss"):
            key = f"{policy}|{metric}"
            cells: dict[str, Any] = {}
            for stage in (1, 2, 3):
                rows = [r for r in records if int(r["boundary_index"]) == stage]
                values = [float(r["responses"][policy][metric]) for r in rows]
                cells[str(stage)] = _cell(values)
            q = sum(bool(c["qualified"]) for c in cells.values())
            channels[key] = {
                "cells": cells,
                "qualified_stage_count": q,
                "qualified": q >= CHANNEL_MIN_QUALIFIED_STAGES,
            }
    return {
        "channels": channels,
        "all_six_qualified": len(channels) == 6 and all(
            bool(x["qualified"]) for x in channels.values()
        ),
    }


def contrast_geometry(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, policy in (
        ("B_minus_A", "B_RESET_ALL"),
        ("C_minus_A", "C_CARRY_STEP_RESET_MOMENTS"),
    ):
        for metric in ("current_loss", "prior_mean_loss"):
            cells: dict[str, Any] = {}
            for stage in (1, 2, 3):
                rows = [r for r in records if int(r["boundary_index"]) == stage]
                values = [
                    float(r["responses"][policy][metric])
                    - float(r["responses"][A_POLICY][metric])
                    for r in rows
                ]
                cells[str(stage)] = _cell(values)
            out[f"{label}|{metric}"] = {"cells": cells}
    return out


def accuracy_sentinel_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for policy in POLICIES:
        for name in ("current_terminal_accuracy", "min_prior_terminal_accuracy"):
            values = [
                float(r["responses"][policy]["accuracy_sentinel"][name])
                for r in records
            ]
            out[f"{policy}|{name}"] = {
                "min": min(values),
                "max": max(values),
                "unique_count": len(set(values)),
            }
    return out


def adjudicate_records(
    records: list[dict[str, Any]],
    reliability_checks: list[dict[str, Any]],
    expected_seeds: Iterable[int] = FRESH_SEEDS,
) -> dict[str, Any]:
    support = support_integrity(records, expected_seeds)
    reliability_ok = (
        len(reliability_checks) == len(RELIABILITY_SEEDS)
        and [int(x["seed"]) for x in reliability_checks] == list(RELIABILITY_SEEDS)
        and all(bool(x.get("exact")) for x in reliability_checks)
        and all(float(x.get("max_abs_diff", -1.0)) == 0.0 for x in reliability_checks)
    )

    if not support["valid"] or not reliability_ok:
        return {
            "status": "STOP",
            "verdict": "STOP_INTEGRITY_OR_SUPPORT",
            "reason": "INTEGRITY_OR_RELIABILITY_FAILURE",
            "support_integrity": support,
            "reliability_ok": reliability_ok,
        }

    geometry = response_geometry(records)
    contrast = contrast_geometry(records)
    sentinel = accuracy_sentinel_summary(records)

    if geometry["all_six_qualified"]:
        status = "PASS"
        verdict = "PASS_LOSS_RESPONSE_SUPPORT"
        reason = "ALL_SIX_DIRECT_LOSS_CHANNELS_NONDEGENERATE"
    else:
        status = "NEGATIVE"
        verdict = "NEGATIVE_LOSS_RESPONSE_GEOMETRY"
        reason = "ONE_OR_MORE_DIRECT_LOSS_CHANNELS_NOT_QUALIFIED"

    return {
        "status": status,
        "verdict": verdict,
        "reason": reason,
        "support_integrity": support,
        "reliability_ok": reliability_ok,
        "response_geometry": geometry,
        "contrast_geometry_diagnostic_only": contrast,
        "accuracy_sentinel_diagnostic_only": sentinel,
        "predictor_fitted": False,
    }


def _validate_lock(lock: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "program": lock.get("program") == PROGRAM,
        "seed_manifest": lock.get("seed_manifest", {}).get("sha256") == SEED_MANIFEST_SHA256,
        "protocol_blob": lock.get("protocol", {}).get("git_blob_sha") == git_blob(PROTOCOL),
        "seed_manifest_blob": lock.get("seed_manifest", {}).get("git_blob_sha") == git_blob(SEED_MANIFEST),
        "runner_blob": lock.get("implementation", {}).get("runner_git_blob_sha") == git_blob(Path(__file__)),
        "substrate_blobs": lock.get("substrate", {}).get("git_blobs") == SUBSTRATE_BLOBS,
    }
    return {"valid": all(checks.values()), "checks": checks}


def execution_authorized() -> bool:
    if not EXECUTION_LOCK.exists() or not LOCK_VERIFICATION.exists():
        return False
    txt = LOCK_VERIFICATION.read_text(encoding="utf-8")
    return (
        "CLRM1_EXECUTION_LOCK_VERIFICATION_PASS" in txt
        and sha256_file(EXECUTION_LOCK) in txt
    )


def _historical_probe() -> dict[str, Any]:
    first = build_response_records(HISTORICAL_PROBE_SEED)
    second = build_response_records(HISTORICAL_PROBE_SEED)
    repeat = compare_repeat(first, second)
    return {
        "seed": HISTORICAL_PROBE_SEED,
        "record_count": len(first),
        "all_integrity_valid": len(first) == 3 and all(_row_valid(r) for r in first),
        "repeat": repeat,
        "fresh_seed_used": HISTORICAL_PROBE_SEED in set(FRESH_SEEDS),
        "geometry_inspected": False,
        "adjudicator_called": False,
    }


def preflight() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    seeds = validate_seed_manifest()
    substrate = frozen_substrate_snapshot()
    lock = (
        _validate_lock(json.loads(EXECUTION_LOCK.read_text(encoding="utf-8")))
        if EXECUTION_LOCK.exists()
        else {"valid": False, "checks": {"lock_exists": False}}
    )
    probe = _historical_probe()

    checks = {
        "seed_manifest_valid": seeds["valid"],
        "substrate_exact": substrate["valid"],
        "lock_valid": lock["valid"],
        "historical_probe_integrity": probe["all_integrity_valid"],
        "historical_probe_repeat_exact": probe["repeat"]["exact"],
        "historical_probe_not_fresh": not probe["fresh_seed_used"],
        "fresh_records_absent": not DEFAULT_RECORDS.exists(),
        "formal_result_absent": not DEFAULT_FORMAL.exists(),
        "independent_verification_absent": not LOCK_VERIFICATION.exists(),
        "fresh_execution_blocked": not execution_authorized(),
    }
    ok = all(checks.values())

    return {
        "schema": "CLRM1-ZERO-SCIENCE-PREFLIGHT-v1",
        "program": PROGRAM,
        "status": "PASS" if ok else "FAIL",
        "verdict": (
            "CLRM1_ZERO_SCIENCE_PREFLIGHT_PASS"
            if ok else
            "CLRM1_ZERO_SCIENCE_PREFLIGHT_FAIL"
        ),
        "git_commit": git("rev-parse", "HEAD"),
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest": seeds,
        "substrate": substrate,
        "execution_lock": lock,
        "historical_probe": probe,
        "checks": checks,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "response_geometry_inspected": False,
        "predictor_fitting_performed": False,
        "difficulty_mutation_performed": False,
        "controller_execution_performed": False,
    }


def collect_fresh() -> dict[str, Any]:
    if not execution_authorized():
        raise RuntimeError("CLRM-1 fresh execution is not independently authorized")
    if not validate_seed_manifest()["valid"]:
        raise RuntimeError("CLRM-1 frozen Role-S manifest invalid")
    if not frozen_substrate_snapshot()["valid"]:
        raise RuntimeError("CLRM-1 frozen substrate invalid")

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    records: list[dict[str, Any]] = []
    reliability: list[dict[str, Any]] = []

    for seed in FRESH_SEEDS:
        first = build_response_records(seed)
        records.extend(first)
        if seed in RELIABILITY_SEEDS:
            second = build_response_records(seed)
            reliability.append({"seed": seed, **compare_repeat(first, second)})

    return {
        "schema": "CLRM1-ROLE-S-COLLECTION-v1",
        "program": PROGRAM,
        "role": "S_SUPPORT_ONLY",
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest_sha256": manifest_hash(FRESH_SEEDS),
        "records": records,
        "reliability_checks": reliability,
    }


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("preflight", "collect", "adjudicate"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.phase == "preflight":
        out = preflight()
        _write(args.output, out)
        return 0 if out["status"] == "PASS" else 2

    if args.phase == "collect":
        _write(args.output, collect_fresh())
        return 0

    if args.input is None:
        parser.error("--input required")

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    result = adjudicate_records(raw["records"], raw["reliability_checks"])
    _write(args.output, {
        "schema": "CLRM1-FORMAL-RESULT-v1",
        "program": PROGRAM,
        "role": "S_SUPPORT_ONLY",
        "protocol_sha256": sha256_file(PROTOCOL),
        "source_records_sha256": sha256_file(args.input),
        "adjudication": result,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
