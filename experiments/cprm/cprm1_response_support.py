"""CPRM-1 fresh response support & geometry qualification.

Preflight is zero-science and uses historical KCL seeds only.
Fresh CPRM-1 collection is blocked until an independently verified execution
lock exists. No predictor is trained anywhere in this module.
"""
from __future__ import annotations

import argparse
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
from experiments.kernel_cl import kcl656_boundary_health_signal as k656

PROGRAM = "CPRM-1"
PROTOCOL = Path("docs/research/continual-policy-response/cprm1-response-support-protocol.md")
EXECUTION_LOCK = Path("docs/research/continual-policy-response/CPRM1_EXECUTION_LOCK.json")
LOCK_VERIFICATION = Path("docs/research/continual-policy-response/CPRM1_EXECUTION_LOCK_VERIFICATION.md")
DEFAULT_RECORDS = Path("experiments/cprm/results/cprm1_fresh_responses.json")
DEFAULT_FORMAL = Path("experiments/cprm/results/FORMAL_RESULT.json")

POLICIES = ("A_CARRY_ALL", "B_RESET_ALL", "C_CARRY_STEP_RESET_MOMENTS")
A_POLICY, B_POLICY, C_POLICY = POLICIES
COMPONENTS = (
    "plasticity_auc",
    "final_current_accuracy",
    "prior_task_retention",
    "worst_prior_accuracy",
)

FRESH_SEEDS = (
    814887,863137,944290,493874,333929,674723,
    629896,563470,452971,659444,563718,222175,
    332624,957861,506630,735777,693319,612663,
    330455,271971,396729,463395,650240,394015,
    596743,717212,700981,787278,430901,538687,
    927431,885588,748598,724163,573227,689490,
    439438,774009,639141,850216,427422,235913,
    355296,574310,665271,791304,909129,757353,
    834226,280648,906973,523942,480884,388898,
    404202,430651,508646,398464,915507,458769,
)
SEED_MANIFEST_SHA256 = "d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3"
RELIABILITY_SEEDS = FRESH_SEEDS[:6]

SPENT_ACO_SEEDS = (
    714845,799297,471852,671302,797856,525370,494800,333039,618491,662800,
    265044,434671,501990,723350,393434,774787,806053,890854,613906,707487,
    415555,641958,505262,776960,428051,767077,464825,448672,416287,770416,
    596609,359597,454064,431281,705347,294795,641624,345481,326782,242385,
)
PROTECTED_KCL_SEEDS = tuple(k656.CONFIRM_SEEDS)

EXPECTED_SEEDS = 60
EXPECTED_BOUNDARIES = 180
EXPECTED_PER_STAGE = 60

CELL_MIN_UNIQUE = 4
CELL_SPAN_RESOLUTION_MULT = 2.0
RESPONSE_COMPONENT_MIN_CELLS = 6
RESPONSE_COMPONENT_MIN_STAGES = 2
RESPONSE_COMPONENT_MIN_POLICIES = 2
CONTRAST_NONZERO_MIN = 0.20
CONTRAST_DIRECTION_MIN = 0.10
CONTRAST_STAGE_SIGN_MIN = 3
CONTRAST_COMPONENT_MIN_STAGES = 2
CONTRAST_FAMILY_MIN_MAG_COMPONENTS = 2
CONTRAST_FAMILY_MIN_DIR_COMPONENTS = 1

HISTORICAL_PROBE_SEED = 9595


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_manifest_sha256(seeds: Iterable[int] = FRESH_SEEDS) -> str:
    return hashlib.sha256(",".join(str(int(s)) for s in seeds).encode("utf-8")).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def git_blob(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "hash-object", str(path)], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _percentile(values: list[float], q: float) -> float:
    xs = sorted(float(x) for x in values)
    if not xs:
        raise ValueError("empty percentile input")
    pos = (len(xs) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def natural_resolution(component: str, boundary_index: int) -> float:
    if component == "plasticity_auc":
        return 1.0 / 480.0
    if component == "final_current_accuracy":
        return 1.0 / 24.0
    if component == "prior_task_retention":
        return 1.0 / (24.0 * float(boundary_index))
    if component == "worst_prior_accuracy":
        return 1.0 / 24.0
    raise KeyError(component)


def _historical_kcl_seed_candidates() -> set[int]:
    paths: list[Path] = [Path("Lineage.md")]
    for base in (
        Path("docs/research/kernel-continual-learning"),
        Path("experiments/kernel_cl"),
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out: set[int] = set()
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if "seed" not in line.lower():
                continue
            out.update(int(x) for x in re.findall(r"\b\d{4,7}\b", line))
    return out


def validate_seed_manifest() -> dict[str, Any]:
    fresh = set(FRESH_SEEDS)
    hist = _historical_kcl_seed_candidates()
    protected = set(PROTECTED_KCL_SEEDS)
    spent = set(SPENT_ACO_SEEDS)
    manifest = seed_manifest_sha256()
    checks = {
        "count_60": len(FRESH_SEEDS) == EXPECTED_SEEDS,
        "unique_60": len(fresh) == EXPECTED_SEEDS,
        "manifest_hash_matches": manifest == SEED_MANIFEST_SHA256,
        "historical_kcl_disjoint": fresh.isdisjoint(hist),
        "protected_kcl_disjoint": fresh.isdisjoint(protected),
        "spent_aco_disjoint": fresh.isdisjoint(spent),
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "count": len(FRESH_SEEDS),
        "unique_count": len(fresh),
        "manifest_sha256": manifest,
        "historical_kcl_collisions": sorted(fresh & hist),
        "protected_kcl_collisions": sorted(fresh & protected),
        "spent_aco_collisions": sorted(fresh & spent),
    }


def frozen_contract_snapshot() -> dict[str, Any]:
    checks = {
        "policy_identity": tuple(k655.POLICIES) == POLICIES,
        "checkpoints_identity": tuple(k655.CHECKPOINTS) == tuple(range(0, 251, 25)),
        "protected_identity": tuple(k656.CONFIRM_SEEDS) == PROTECTED_KCL_SEEDS,
    }
    return {"valid": all(checks.values()), "checks": checks}


def _clone_model_opt(model, opt, config):
    m = copy.deepcopy(model)
    o = optimizer_for(m, config)
    o.load_state_dict(copy.deepcopy(opt.state_dict()))
    return m, o


def _prior_accuracy_vector(model, observed_tasks):
    return [float(evaluate(model, task)["accuracy"]) for _, task in observed_tasks]


def run_response_counterfactual(
    *,
    model,
    optimizer,
    memories,
    observed_tasks,
    next_task,
    seed: int,
    next_stage: int,
    config: KCL1Config,
) -> dict[str, Any]:
    models = {}
    opts = {}
    policy_integrity = {}
    for policy in POLICIES:
        m, o = _clone_model_opt(model, optimizer, config)
        o, info = k655._policy_boundary(policy, m, o, config)
        models[policy] = m
        opts[policy] = o
        policy_integrity[policy] = info

    fork_equal = all(
        all(
            torch.equal(models[A_POLICY].state_dict()[name], models[p].state_dict()[name])
            for name in models[A_POLICY].state_dict()
        )
        for p in (B_POLICY, C_POLICY)
    )

    memory_copy = copy.deepcopy(memories)
    stage = k655._train_stage_lockstep(
        models, opts, memory_copy, next_task[1],
        [task for _, task in observed_tasks],
        seed=seed, stage=next_stage,
    )

    responses = {}
    for policy in POLICIES:
        summary = stage["curve_summary"][policy]
        prior = _prior_accuracy_vector(models[policy], observed_tasks)
        responses[policy] = {
            "response": {
                "plasticity_auc": float(summary["normalized_auc"]),
                "final_current_accuracy": float(summary["final_accuracy"]),
                "prior_task_retention": float(statistics.fmean(prior)),
                "worst_prior_accuracy": float(min(prior)),
            },
            "prior_task_accuracies": prior,
        }

    integrity = {
        "fork_models_equal": fork_equal,
        "boundary_model_unchanged": all(
            bool(info["model_unchanged"]) for info in policy_integrity.values()
        ),
        "exact_replay_match": math.isclose(
            float(stage["exact_replay_match_rate"]), 1.0, rel_tol=0.0, abs_tol=0.0
        ),
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


def build_response_records(seed: int, config: KCL1Config | None = None) -> list[dict[str, Any]]:
    config = config or KCL1Config()
    tasks = task_sequence(config)
    model = build_model(config, seed)
    opt = optimizer_for(model, config)
    train_stage(model, opt, tasks[0][1], steps=250, batch_size=16, seed=seed + 101)
    memories = [k63.ExactMemory.from_task(tasks[0][1])]
    observed = [tasks[0]]
    records = []

    for boundary_index in (1, 2, 3):
        current_task = observed[-1]
        next_task = tasks[boundary_index]
        counter = run_response_counterfactual(
            model=model, optimizer=opt, memories=memories,
            observed_tasks=observed, next_task=next_task,
            seed=seed, next_stage=boundary_index + 1, config=config,
        )
        records.append({
            "seed": int(seed),
            "boundary_index": boundary_index,
            "after_task": current_task[0],
            "next_task": next_task[0],
            "responses": counter["responses"],
            "integrity": counter["integrity"],
        })
        model = counter["_reference_model"]
        opt = counter["_reference_optimizer"]
        memories = counter["_next_memories"]
        observed = tasks[: boundary_index + 1]
    return records


def _numeric_response_values(records):
    out = []
    for row in records:
        for policy in POLICIES:
            for component in COMPONENTS:
                out.append(float(row["responses"][policy]["response"][component]))
    return out


def compare_repeat(a, b):
    av = _numeric_response_values(a)
    bv = _numeric_response_values(b)
    max_abs_diff = max(abs(x - y) for x, y in zip(av, bv)) if av else 0.0
    same_structure = (
        [(r["seed"], r["boundary_index"], sorted(r["responses"]), r["integrity"]) for r in a]
        ==
        [(r["seed"], r["boundary_index"], sorted(r["responses"]), r["integrity"]) for r in b]
    )
    return {
        "max_abs_diff": max_abs_diff,
        "same_structure": same_structure,
        "exact": max_abs_diff == 0.0 and same_structure,
    }


def _row_integrity(row):
    if not bool(row.get("integrity", {}).get("valid")):
        return False
    if set(row.get("responses", {})) != set(POLICIES):
        return False
    boundary = int(row["boundary_index"])
    for policy in POLICIES:
        payload = row["responses"][policy]
        response = payload["response"]
        prior = [float(x) for x in payload["prior_task_accuracies"]]
        if len(prior) != boundary:
            return False
        vals = [float(response[c]) for c in COMPONENTS]
        if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in vals):
            return False
        mean_prior = float(response["prior_task_retention"])
        worst_prior = float(response["worst_prior_accuracy"])
        if worst_prior > mean_prior + 1e-12:
            return False
        if not math.isclose(mean_prior, statistics.fmean(prior), abs_tol=1e-12):
            return False
        if not math.isclose(worst_prior, min(prior), abs_tol=1e-12):
            return False
        if boundary == 1 and not math.isclose(mean_prior, worst_prior, abs_tol=1e-12):
            return False
    return True


def support_integrity(records, expected_seeds=FRESH_SEEDS):
    seedset = {int(s) for s in expected_seeds}
    observed = {int(r["seed"]) for r in records}
    per_seed = {s: 0 for s in seedset}
    per_stage = {1: 0, 2: 0, 3: 0}
    for row in records:
        s = int(row["seed"])
        b = int(row["boundary_index"])
        if s in per_seed:
            per_seed[s] += 1
        if b in per_stage:
            per_stage[b] += 1
    expected_n = len(expected_seeds)
    checks = {
        "seed_set_exact": observed == seedset,
        "seed_count_exact": len(observed) == expected_n,
        "records_exact": len(records) == expected_n * 3,
        "three_boundaries_per_seed": all(v == 3 for v in per_seed.values()),
        "stage_counts_exact": per_stage == {1: expected_n, 2: expected_n, 3: expected_n},
        "all_row_integrity": all(_row_integrity(r) for r in records),
    }
    return {"valid": all(checks.values()), "checks": checks, "per_stage": per_stage}


def _cell_geometry(values, resolution):
    unique_count = len(set(values))
    p10 = _percentile(values, 0.10)
    p90 = _percentile(values, 0.90)
    span = p90 - p10
    qualified = unique_count >= CELL_MIN_UNIQUE and span >= CELL_SPAN_RESOLUTION_MULT * resolution
    return {
        "unique_count": unique_count,
        "p10": p10,
        "p90": p90,
        "robust_span": span,
        "resolution": resolution,
        "qualified": qualified,
    }


def response_geometry(records):
    components = {}
    for component in COMPONENTS:
        cells = {}
        qualified_cells = 0
        stage_hits = set()
        policy_hits = set()
        for policy in POLICIES:
            for stage in (1, 2, 3):
                values = [
                    float(r["responses"][policy]["response"][component])
                    for r in records if int(r["boundary_index"]) == stage
                ]
                cell = _cell_geometry(values, natural_resolution(component, stage))
                cells[f"{policy}|stage{stage}"] = cell
                if cell["qualified"]:
                    qualified_cells += 1
                    stage_hits.add(stage)
                    policy_hits.add(policy)
        qualified = (
            qualified_cells >= RESPONSE_COMPONENT_MIN_CELLS
            and len(stage_hits) >= RESPONSE_COMPONENT_MIN_STAGES
            and len(policy_hits) >= RESPONSE_COMPONENT_MIN_POLICIES
        )
        components[component] = {
            "qualified": qualified,
            "qualified_cells": qualified_cells,
            "qualified_stages": sorted(stage_hits),
            "qualified_policies": sorted(policy_hits),
            "cells": cells,
        }
    return {
        "components": components,
        "all_components_qualified": all(x["qualified"] for x in components.values()),
    }


def contrast_geometry(records):
    families = {}
    for policy in (B_POLICY, C_POLICY):
        fam_components = {}
        mag_count = 0
        dir_count = 0
        for component in COMPONENTS:
            stage_cells = {}
            mag_stages = 0
            pooled = []
            for stage in (1, 2, 3):
                resolution = natural_resolution(component, stage)
                values = []
                for r in records:
                    if int(r["boundary_index"]) != stage:
                        continue
                    delta = (
                        float(r["responses"][policy]["response"][component])
                        - float(r["responses"][A_POLICY]["response"][component])
                    )
                    values.append(delta)
                    pooled.append((stage, delta, resolution))
                base = _cell_geometry(values, resolution)
                nonzero_rate = sum(abs(v) >= resolution for v in values) / len(values)
                qualified = base["qualified"] and nonzero_rate >= CONTRAST_NONZERO_MIN
                stage_cells[f"stage{stage}"] = {
                    **base,
                    "nonzero_rate": nonzero_rate,
                    "qualified": qualified,
                }
                mag_stages += int(qualified)

            magnitude_supported = mag_stages >= CONTRAST_COMPONENT_MIN_STAGES
            mag_count += int(magnitude_supported)

            pos = [(s,d,res) for s,d,res in pooled if d >= res]
            neg = [(s,d,res) for s,d,res in pooled if d <= -res]
            n = len(pooled)
            pos_rate = len(pos) / n
            neg_rate = len(neg) / n
            pos_stages = {
                s for s in (1,2,3)
                if sum(1 for ss,_,_ in pos if ss == s) >= CONTRAST_STAGE_SIGN_MIN
            }
            neg_stages = {
                s for s in (1,2,3)
                if sum(1 for ss,_,_ in neg if ss == s) >= CONTRAST_STAGE_SIGN_MIN
            }
            direction_supported = (
                pos_rate >= CONTRAST_DIRECTION_MIN
                and neg_rate >= CONTRAST_DIRECTION_MIN
                and len(pos_stages) >= 2 and len(neg_stages) >= 2
            )
            dir_count += int(direction_supported)
            fam_components[component] = {
                "magnitude_supported": magnitude_supported,
                "magnitude_supported_stages": mag_stages,
                "direction_supported": direction_supported,
                "positive_rate": pos_rate,
                "negative_rate": neg_rate,
                "positive_stages": sorted(pos_stages),
                "negative_stages": sorted(neg_stages),
                "stage_cells": stage_cells,
            }

        families[policy] = {
            "qualified": (
                mag_count >= CONTRAST_FAMILY_MIN_MAG_COMPONENTS
                and dir_count >= CONTRAST_FAMILY_MIN_DIR_COMPONENTS
            ),
            "magnitude_supported_components": mag_count,
            "direction_supported_components": dir_count,
            "components": fam_components,
        }
    return {
        "families": families,
        "all_families_qualified": all(x["qualified"] for x in families.values()),
    }


def adjudicate_records(records, reliability_checks, expected_seeds=FRESH_SEEDS):
    support = support_integrity(records, expected_seeds)
    reliability_ok = (
        len(reliability_checks) == len(RELIABILITY_SEEDS)
        and all(bool(x.get("exact")) for x in reliability_checks)
    )
    if not support["valid"] or not reliability_ok:
        return {
            "status": "STOP",
            "verdict": "STOP_INTEGRITY_OR_SUPPORT",
            "support_integrity": support,
            "reliability_ok": reliability_ok,
        }

    response = response_geometry(records)
    contrast = contrast_geometry(records)
    geometry_ok = response["all_components_qualified"] and contrast["all_families_qualified"]
    return {
        "status": "PASS" if geometry_ok else "NEGATIVE",
        "verdict": "PASS_RESPONSE_SUPPORT" if geometry_ok else "NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED",
        "support_integrity": support,
        "reliability_ok": reliability_ok,
        "response_geometry": response,
        "contrast_geometry": contrast,
    }


def _historical_probe():
    assert HISTORICAL_PROBE_SEED not in set(FRESH_SEEDS)
    first = build_response_records(HISTORICAL_PROBE_SEED)
    second = build_response_records(HISTORICAL_PROBE_SEED)
    repeat = compare_repeat(first, second)
    return {
        "seed": HISTORICAL_PROBE_SEED,
        "record_count": len(first),
        "all_integrity_valid": len(first) == 3 and all(_row_integrity(r) for r in first),
        "repeat": repeat,
        "fresh_seed_used": False,
    }


def _validate_lock(lock):
    observed = {
        "program": lock.get("program"),
        "seed_manifest_sha256": lock.get("seed_manifest", {}).get("sha256"),
        "protocol_git_blob": lock.get("protocol", {}).get("git_blob_sha"),
        "runner_git_blob": lock.get("implementation", {}).get("runner_git_blob_sha"),
    }
    expected = {
        "program": PROGRAM,
        "seed_manifest_sha256": SEED_MANIFEST_SHA256,
        "protocol_git_blob": git_blob(PROTOCOL),
        "runner_git_blob": git_blob(Path(__file__)),
    }
    checks = {k: observed.get(k) == v for k, v in expected.items()}
    return {"valid": all(checks.values()), "checks": checks}


def execution_authorized():
    if not EXECUTION_LOCK.exists() or not LOCK_VERIFICATION.exists():
        return False
    try:
        lock_sha = sha256_file(EXECUTION_LOCK)
        text = LOCK_VERIFICATION.read_text(encoding="utf-8")
    except OSError:
        return False
    return "CPRM1_EXECUTION_LOCK_VERIFICATION_PASS" in text and lock_sha in text


def preflight():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    seeds = validate_seed_manifest()
    contract = frozen_contract_snapshot()
    lock = (
        _validate_lock(json.loads(EXECUTION_LOCK.read_text(encoding="utf-8")))
        if EXECUTION_LOCK.exists() else {"valid": False, "checks": {"lock_exists": False}}
    )
    historical = _historical_probe()
    checks = {
        "protocol_exists": PROTOCOL.exists(),
        "seed_manifest_valid": seeds["valid"],
        "frozen_contract_valid": contract["valid"],
        "execution_lock_valid": lock["valid"],
        "historical_probe_integrity": historical["all_integrity_valid"],
        "historical_probe_repeat_exact": historical["repeat"]["exact"],
        "historical_probe_not_fresh": not historical["fresh_seed_used"],
        "fresh_records_absent": not DEFAULT_RECORDS.exists(),
        "formal_result_absent": not DEFAULT_FORMAL.exists(),
        "independent_lock_verification_absent": not LOCK_VERIFICATION.exists(),
        "fresh_execution_not_authorized_yet": not execution_authorized(),
    }
    ok = all(checks.values())
    return {
        "schema": "CPRM1-ZERO-SCIENCE-PREFLIGHT-v1",
        "program": PROGRAM,
        "phase": "ZERO_SCIENCE_PREFLIGHT",
        "status": "PASS" if ok else "FAIL",
        "verdict": "CPRM1_ZERO_SCIENCE_PREFLIGHT_PASS" if ok else "CPRM1_ZERO_SCIENCE_PREFLIGHT_FAIL",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL) if PROTOCOL.exists() else None,
        "seed_manifest": seeds,
        "contract": contract,
        "execution_lock": lock,
        "historical_probe": historical,
        "checks": checks,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "model_fitting_performed": False,
    }


def collect_fresh():
    if not execution_authorized():
        raise RuntimeError("CPRM-1 fresh execution is not independently authorized")
    if not validate_seed_manifest()["valid"]:
        raise RuntimeError("CPRM-1 seed manifest invalid")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    records = []
    reliability = []
    for seed in FRESH_SEEDS:
        first = build_response_records(seed)
        records.extend(first)
        if seed in RELIABILITY_SEEDS:
            second = build_response_records(seed)
            reliability.append({"seed": seed, **compare_repeat(first, second)})
    return {
        "schema": "CPRM1-FRESH-COLLECTION-v1",
        "program": PROGRAM,
        "phase": "FRESH_COLLECTION",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest_sha256": seed_manifest_sha256(),
        "records": records,
        "reliability_checks": reliability,
    }


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", required=True, choices=("preflight", "collect", "adjudicate"))
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.phase == "preflight":
        out = preflight()
        _write(args.output, out)
        return 0 if out["status"] == "PASS" else 2
    if args.phase == "collect":
        _write(args.output, collect_fresh())
        return 0
    if args.input is None:
        p.error("--input is required for adjudicate")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    records = raw.get("records")
    reliability = raw.get("reliability_checks")
    if not isinstance(records, list) or not isinstance(reliability, list):
        raise RuntimeError("invalid CPRM-1 adjudication input")
    _write(args.output, {
        "schema": "CPRM1-FORMAL-RESULT-v1",
        "program": PROGRAM,
        "phase": "ONE_SHOT_ADJUDICATION",
        "git_commit": git_commit(),
        "protocol_sha256": sha256_file(PROTOCOL),
        "source_records_sha256": sha256_file(args.input),
        "adjudication": adjudicate_records(records, reliability),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
