"""KCL-6.5.9.6 — Mechanistic Representation Qualification.

Tests MRIG-v1, a pre-boundary reset-interference representation, against the
frozen KCL-6.5.9.5 S2 representation. No future-task probe and no controller.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config,
    build_model,
    optimizer_for,
    train_stage,
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl63_fuzzy_decay_abcd as k63
from experiments.kernel_cl import kcl655_adamw_boundary_policy_abc as k655
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl658_localized_boundary_state as k658
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592
from experiments.kernel_cl import kcl6593_action_identifiability as k6593
from experiments.kernel_cl import kcl6594_action_target_failure_modes as k6594
from experiments.kernel_cl import kcl6595_mechanism_target_identifiability as k6595

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6596-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6596_mechanistic_representation.py")

TARGET_A = k6595.TARGET_A
TARGET_PR = k6595.TARGET_PR
TARGET_PRR = k6595.TARGET_PRR
TARGETS = (TARGET_A, TARGET_PR, TARGET_PRR)
CLASS_ORDER = k6595.CLASS_ORDER

MECH_PR = k6595.MECH_PR
MECH_PRR = k6595.MECH_PRR

S2_FEATURES = k6595.S2_FEATURES
MRIG_FEATURES = (
    "M1_CURRENT_RETENTION_GRAD_COSINE",
    "M2_MIN_PLASTICITY_CONTRAST",
    "M3_MAX_PLASTICITY_CONTRAST",
    "M4_MIN_RETENTION_COST_CONTRAST",
    "M5_MAX_RETENTION_COST_CONTRAST",
    "M6_PLASTICITY_CONTRAST_GAP",
    "M7_RETENTION_CONTRAST_GAP",
    "M8_BOTH_RETENTION_BADNESS",
    "M9_MAX_JOINT_BADNESS",
    "M10_STEP_SCALE_LOG_GAP",
)
S3_FEATURES = S2_FEATURES + MRIG_FEATURES
FEATURE_SETS = {"S2": S2_FEATURES, "S3": S3_FEATURES}

_generated = random.Random(6596).sample(range(5_000_001, 7_000_000), 720)
TRAIN_SEEDS = tuple(_generated[:480])
VALIDATION_SEEDS = tuple(_generated[480:])
ALL_SEED_SHA256 = "f96a7f4c5c8f45234c9108a6eb184b941bcd464398f34e2d5798fe722a24aade"
TRAIN_SEED_SHA256 = "3c2b02dccac5f7344daf2ffdb22b2dd7f581af5bbdd92c5c8481c001e0ed19d6"
VALIDATION_SEED_SHA256 = "f036e088b316f8988df27bbb088f87d50ac52efa062ad5058ccf8a35b0151051"

TRAIN_MIN_COUNT = 50
TRAIN_MIN_SEEDS = 40
VAL_MIN_COUNT = 25
VAL_MIN_SEEDS = 20

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6596

GAIN_POINT_MIN = 0.10
GAIN_CI_LOWER_MIN = 0.03
EPS = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_seed_list(seeds: tuple[int, ...] | list[int]) -> str:
    return hashlib.sha256(",".join(map(str, seeds)).encode("utf-8")).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def prior_seed_set() -> set[int]:
    return (
        set(k656.DISCOVERY_SEEDS)
        | set(k656.CONFIRM_SEEDS)
        | set(k6591.REPLICATION_SEEDS)
        | set(k6592.TRAIN_SEEDS)
        | set(k6592.VALIDATION_SEEDS)
        | set(k6593.TRAIN_SEEDS)
        | set(k6593.VALIDATION_SEEDS)
        | set(k6594.DISCOVERY_SEEDS)
        | set(k6594.REPLICATION_SEEDS)
        | set(k6595.TRAIN_SEEDS)
        | set(k6595.VALIDATION_SEEDS)
    )


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    return set(seeds).isdisjoint(prior_seed_set())


def _flatten_named(
    tensors: dict[str, torch.Tensor],
    model: torch.nn.Module,
) -> torch.Tensor:
    return torch.cat([
        tensors[name].detach().float().reshape(-1)
        for name, _ in model.named_parameters()
    ])


def _theta(model: torch.nn.Module) -> torch.Tensor:
    return torch.cat([
        p.detach().float().reshape(-1)
        for _, p in model.named_parameters()
    ])


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = float(torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b))
    if denom <= 1e-20:
        return 0.0
    return float(torch.dot(a, b) / denom)


def _capture_gradients(
    model: torch.nn.Module,
    loss: torch.Tensor,
) -> dict[str, torch.Tensor]:
    model.zero_grad(set_to_none=True)
    loss.backward()
    out: dict[str, torch.Tensor] = {}
    for name, p in model.named_parameters():
        out[name] = (
            torch.zeros_like(p.detach())
            if p.grad is None
            else p.grad.detach().clone()
        )
    model.zero_grad(set_to_none=True)
    return out


def observed_gradients(
    *,
    model: torch.nn.Module,
    current_task: tuple[torch.Tensor, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
) -> dict[str, Any]:
    model_before = copy.deepcopy(model.state_dict())

    xcur, ycur = current_task
    current_loss = F.cross_entropy(model(xcur)[:, -1, :], ycur)
    g_cur = _capture_gradients(model, current_loss)

    retention_losses = []
    for _, task in observed_tasks:
        x, y = task
        retention_losses.append(F.cross_entropy(model(x)[:, -1, :], y))
    retention_loss = torch.stack(retention_losses).mean()
    g_ret = _capture_gradients(model, retention_loss)

    model_unchanged = all(
        torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    gradients_cleared = all(p.grad is None for p in model.parameters())

    return {
        "current": g_cur,
        "retention": g_ret,
        "current_loss": float(current_loss.detach()),
        "retention_loss": float(retention_loss.detach()),
        "model_unchanged": model_unchanged,
        "gradients_cleared": gradients_cleared,
    }


def virtual_policy_update(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    config: KCL1Config,
    policy: str,
    gradient: dict[str, torch.Tensor],
) -> dict[str, Any]:
    m = copy.deepcopy(model)
    o = optimizer_for(m, config)
    o.load_state_dict(copy.deepcopy(optimizer.state_dict()))
    o, boundary_info = k655._policy_boundary(policy, m, o, config)

    before = _theta(m)
    for name, p in m.named_parameters():
        p.grad = gradient[name].detach().clone().to(
            device=p.device,
            dtype=p.dtype,
        )
    o.step()
    after = _theta(m)
    update = after - before
    o.zero_grad(set_to_none=True)

    return {
        "update": update,
        "boundary_info": boundary_info,
        "finite": bool(torch.isfinite(update).all().item()),
    }


def mrigr_features_from_responses(
    grad_cosine: float,
    responses: dict[str, dict[str, float]],
) -> dict[str, float]:
    a = responses[k655.POLICIES[0]]
    b = responses[k655.POLICIES[1]]
    c = responses[k655.POLICIES[2]]

    d_i_b = float(b["adaptation_response"] - a["adaptation_response"])
    d_i_c = float(c["adaptation_response"] - a["adaptation_response"])
    d_r_b = float(b["retention_cost"] - a["retention_cost"])
    d_r_c = float(c["retention_cost"] - a["retention_cost"])

    ls_b = math.log((float(b["step_scale"]) + EPS) / (float(a["step_scale"]) + EPS))
    ls_c = math.log((float(c["step_scale"]) + EPS) / (float(a["step_scale"]) + EPS))

    features = {
        "M1_CURRENT_RETENTION_GRAD_COSINE": float(grad_cosine),
        "M2_MIN_PLASTICITY_CONTRAST": min(d_i_b, d_i_c),
        "M3_MAX_PLASTICITY_CONTRAST": max(d_i_b, d_i_c),
        "M4_MIN_RETENTION_COST_CONTRAST": min(d_r_b, d_r_c),
        "M5_MAX_RETENTION_COST_CONTRAST": max(d_r_b, d_r_c),
        "M6_PLASTICITY_CONTRAST_GAP": abs(d_i_b - d_i_c),
        "M7_RETENTION_CONTRAST_GAP": abs(d_r_b - d_r_c),
        "M8_BOTH_RETENTION_BADNESS": min(max(d_r_b, 0.0), max(d_r_c, 0.0)),
        "M9_MAX_JOINT_BADNESS": max(
            max(-d_i_b, 0.0) * max(d_r_b, 0.0),
            max(-d_i_c, 0.0) * max(d_r_c, 0.0),
        ),
        "M10_STEP_SCALE_LOG_GAP": abs(ls_b - ls_c),
    }
    if not all(math.isfinite(float(v)) for v in features.values()):
        raise RuntimeError("non-finite MRIG-v1 feature")
    return features


def extract_mrig(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    config: KCL1Config,
    current_task: tuple[torch.Tensor, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
) -> dict[str, Any]:
    model_before = copy.deepcopy(model.state_dict())
    opt_before = copy.deepcopy(optimizer.state_dict())

    grads = observed_gradients(
        model=model,
        current_task=current_task,
        observed_tasks=observed_tasks,
    )
    g_cur_vec = _flatten_named(grads["current"], model)
    g_ret_vec = _flatten_named(grads["retention"], model)

    gcur_sq = float(torch.dot(g_cur_vec, g_cur_vec))
    gret_sq = float(torch.dot(g_ret_vec, g_ret_vec))
    gcur_norm = float(torch.linalg.vector_norm(g_cur_vec))
    grad_cosine = _cosine(g_cur_vec, g_ret_vec)

    responses: dict[str, dict[str, float]] = {}
    policy_integrity: dict[str, Any] = {}
    for policy in k655.POLICIES:
        vr = virtual_policy_update(
            model=model,
            optimizer=optimizer,
            config=config,
            policy=policy,
            gradient=grads["current"],
        )
        u = vr["update"]
        responses[policy] = {
            "adaptation_response": float(-torch.dot(g_cur_vec, u) / (gcur_sq + EPS)),
            "retention_cost": float(torch.dot(g_ret_vec, u) / (gret_sq + EPS)),
            "step_scale": float(torch.linalg.vector_norm(u) / (gcur_norm + EPS)),
        }
        policy_integrity[policy] = {
            "virtual_update_finite": vr["finite"],
            "boundary_model_unchanged": bool(vr["boundary_info"]["model_unchanged"]),
        }

    features = mrigr_features_from_responses(grad_cosine, responses)

    swapped = {
        k655.POLICIES[0]: responses[k655.POLICIES[0]],
        k655.POLICIES[1]: responses[k655.POLICIES[2]],
        k655.POLICIES[2]: responses[k655.POLICIES[1]],
    }
    swapped_features = mrigr_features_from_responses(grad_cosine, swapped)
    exchange_symmetric = all(
        abs(float(features[k]) - float(swapped_features[k])) <= 1e-15
        for k in MRIG_FEATURES
    )

    model_unchanged = all(
        torch.equal(model_before[k], model.state_dict()[k])
        for k in model_before
    )
    optimizer_unchanged = k655._deep_equal(opt_before, optimizer.state_dict())
    gradients_cleared = all(p.grad is None for p in model.parameters())

    return {
        "features": features,
        "details": {
            "current_loss": grads["current_loss"],
            "retention_loss": grads["retention_loss"],
            "grad_cosine": grad_cosine,
            "responses": responses,
        },
        "integrity": {
            "gradient_model_unchanged": bool(grads["model_unchanged"]),
            "gradient_cleanup_valid": bool(grads["gradients_cleared"]),
            "original_model_unchanged": bool(model_unchanged),
            "original_optimizer_unchanged": bool(optimizer_unchanged),
            "gradients_cleared": bool(gradients_cleared),
            "policy_virtual_updates_finite": all(
                x["virtual_update_finite"] for x in policy_integrity.values()
            ),
            "virtual_boundary_models_unchanged": all(
                x["boundary_model_unchanged"] for x in policy_integrity.values()
            ),
            "exchange_symmetric": bool(exchange_symmetric),
        },
    }


def build_records(seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    cfg = KCL1Config()
    out: list[dict[str, Any]] = []

    for seed in seeds:
        tasks = task_sequence(cfg)
        model = build_model(cfg, seed)
        opt = optimizer_for(model, cfg)
        pre_task_model_state = copy.deepcopy(model.state_dict())

        train_stage(
            model,
            opt,
            tasks[0][1],
            steps=250,
            batch_size=16,
            seed=seed + 101,
        )
        memories: list[k63.Memory] = [k63.ExactMemory.from_task(tasks[0][1])]
        observed = [tasks[0]]

        for boundary_index in (1, 2, 3):
            current_task = observed[-1]

            global_features = k656.extract_boundary_features(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                current_task=current_task,
                boundary_index=boundary_index,
            )
            localized = k658.extract_localized_features(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                boundary_index=boundary_index,
            )

            # Anti-leakage: MRIG is extracted before next_task is bound.
            mrig = extract_mrig(
                model=model,
                optimizer=opt,
                config=cfg,
                current_task=current_task[1],
                observed_tasks=observed,
            )

            features = {k: float(v) for k, v in global_features.items()}
            for name in tuple(f"F{i}" for i in range(1, 14)):
                features[name] = float(localized["features"][name])
            features.update({k: float(v) for k, v in mrig["features"].items()})

            next_task = tasks[boundary_index]
            counter = k656.run_next_task_counterfactual(
                model=model,
                optimizer=opt,
                memories=memories,
                observed_tasks=observed,
                next_task=next_task,
                seed=seed,
                next_stage=boundary_index + 1,
                config=cfg,
            )
            labels = k6595.labels_from_outcomes(counter["outcomes"])
            action_target, mechanism = k6595.mechanism_from_outcomes(
                counter["outcomes"]
            )

            share_sums = localized["details"]["share_sums"]
            lrbs_shares_valid = all(
                abs(float(share_sums[name]) - 1.0) <= 1e-9
                for name in ("drift", "pressure", "retention")
            )

            out.append({
                "seed": int(seed),
                "boundary_index": int(boundary_index),
                "after_task": current_task[0],
                "features": features,
                "labels": labels,
                "action_target": action_target,
                "mechanism_signature": mechanism,
                "mrig_details": mrig["details"],
                "counterfactual_outcomes": counter["outcomes"],
                "integrity": {
                    "counterfactual_valid": bool(counter["integrity"]["valid"]),
                    "lrbs_shares_valid": bool(lrbs_shares_valid),
                    **mrig["integrity"],
                },
            })

            pre_task_model_state = copy.deepcopy(model.state_dict())
            model = counter["_reference_model"]
            opt = counter["_reference_optimizer"]
            memories = counter["_next_memories"]
            observed = tasks[: boundary_index + 1]

    return out


def binary_class(record: dict[str, Any], target: str) -> str:
    return "POS" if bool(record["labels"][target]) else "NEG"


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for target in TARGETS:
        out[target] = {}
        for cls in CLASS_ORDER:
            rr = [r for r in records if binary_class(r, target) == cls]
            out[target][cls] = {
                "count": len(rr),
                "unique_seed_count": len({int(r["seed"]) for r in rr}),
                "boundary_counts": dict(sorted(Counter(
                    int(r["boundary_index"]) for r in rr
                ).items())),
            }
    return out


def primary_support_pass(
    table: dict[str, dict[str, Any]],
    *,
    min_count: int,
    min_seeds: int,
) -> bool:
    return all(
        int(table[TARGET_PRR][cls]["count"]) >= min_count
        and int(table[TARGET_PRR][cls]["unique_seed_count"]) >= min_seeds
        for cls in CLASS_ORDER
    )


def cohort_integrity(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
    expected_records: int,
    expected_seed_sha: str,
) -> dict[str, bool]:
    counts = Counter(int(r["seed"]) for r in records)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))

    return {
        "seed_sha_matches": sha_seed_list(seeds) == expected_seed_sha,
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(boundaries[s] == {1, 2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "train_validation_disjoint": set(TRAIN_SEEDS).isdisjoint(VALIDATION_SEEDS),
        "features_finite": all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        ),
        "mrig_features_exact": all(
            all(k in r["features"] for k in MRIG_FEATURES)
            for r in records
        ),
        "counterfactual_integrity_valid": all(
            r["integrity"]["counterfactual_valid"] for r in records
        ),
        "lrbs_shares_valid": all(
            r["integrity"]["lrbs_shares_valid"] for r in records
        ),
        "gradient_model_unchanged": all(
            r["integrity"]["gradient_model_unchanged"] for r in records
        ),
        "gradient_cleanup_valid": all(
            r["integrity"]["gradient_cleanup_valid"] for r in records
        ),
        "original_model_unchanged": all(
            r["integrity"]["original_model_unchanged"] for r in records
        ),
        "original_optimizer_unchanged": all(
            r["integrity"]["original_optimizer_unchanged"] for r in records
        ),
        "gradients_cleared": all(
            r["integrity"]["gradients_cleared"] for r in records
        ),
        "policy_virtual_updates_finite": all(
            r["integrity"]["policy_virtual_updates_finite"] for r in records
        ),
        "virtual_boundary_models_unchanged": all(
            r["integrity"]["virtual_boundary_models_unchanged"] for r in records
        ),
        "exchange_symmetric": all(
            r["integrity"]["exchange_symmetric"] for r in records
        ),
        "mechanism_targets_subset_A_ONLY": all(
            (not r["labels"][TARGET_PR] or r["labels"][TARGET_A])
            and (not r["labels"][TARGET_PRR] or r["labels"][TARGET_A])
            for r in records
        ),
        "future_probe_absent": all(
            not any("_NEXT_" in k for k in r["features"])
            for r in records
        ),
    }


def fit_all(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        target: {
            arm: k6595.fit_binary(records, target, features)
            for arm, features in FEATURE_SETS.items()
        }
        for target in TARGETS
    }


def metrics_all(
    records: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, list[str]]],
    dict[str, dict[str, np.ndarray]],
]:
    metrics: dict[str, dict[str, Any]] = {}
    preds: dict[str, dict[str, list[str]]] = {}
    probs: dict[str, dict[str, np.ndarray]] = {}
    for target in TARGETS:
        metrics[target], preds[target], probs[target] = {}, {}, {}
        for arm in FEATURE_SETS:
            p, pr = k6595.predict_binary(records, models[target][arm])
            preds[target][arm] = p
            probs[target][arm] = pr
            metrics[target][arm] = k6595.metrics_binary(
                records, target, p, pr
            )
    return metrics, preds, probs


def _percentile(values: list[float], q: float) -> float:
    return float(np.percentile(
        np.asarray(values, dtype=np.float64),
        q,
        method="linear",
    ))


def paired_bootstrap(
    records: list[dict[str, Any]],
    preds: dict[str, dict[str, list[str]]],
    probs: dict[str, dict[str, np.ndarray]],
) -> dict[str, Any]:
    seeds = sorted({int(r["seed"]) for r in records})
    by_seed: dict[int, list[int]] = {s: [] for s in seeds}
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    recall = {
        target: {arm: [] for arm in FEATURE_SETS}
        for target in TARGETS
    }
    deltas = {
        "D_MRIG": [],
        "D_PR": [],
        "D_A": [],
    }

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = rng.integers(0, len(seeds), size=len(seeds))
        idxs = [i for j in drawn for i in by_seed[seeds[int(j)]]]
        rr = [records[i] for i in idxs]
        mr: dict[str, dict[str, float]] = {}

        for target in TARGETS:
            mr[target] = {}
            for arm in FEATURE_SETS:
                pp = [preds[target][arm][i] for i in idxs]
                pr = probs[target][arm][idxs, :]
                m = k6595.metrics_binary(rr, target, pp, pr)
                value = float(m["macro_recall"])
                recall[target][arm].append(value)
                mr[target][arm] = value

        deltas["D_MRIG"].append(
            mr[TARGET_PRR]["S3"] - mr[TARGET_PRR]["S2"]
        )
        deltas["D_PR"].append(
            mr[TARGET_PR]["S3"] - mr[TARGET_PR]["S2"]
        )
        deltas["D_A"].append(
            mr[TARGET_A]["S3"] - mr[TARGET_A]["S2"]
        )

    arms = {
        target: {
            arm: {
                "macro_recall": {
                    "ci_lower": _percentile(recall[target][arm], 2.5),
                    "ci_upper": _percentile(recall[target][arm], 97.5),
                }
            }
            for arm in FEATURE_SETS
        }
        for target in TARGETS
    }
    delta_out = {
        name: {
            "ci_lower": _percentile(values, 2.5),
            "ci_upper": _percentile(values, 97.5),
        }
        for name, values in deltas.items()
    }
    return {
        "arms": arms,
        "deltas": delta_out,
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
    }


def adjudicate(
    metrics: dict[str, dict[str, Any]],
    bootstrap: dict[str, Any],
) -> dict[str, Any]:
    q_s2 = k6595.qualified(
        metrics[TARGET_PRR]["S2"],
        bootstrap["arms"][TARGET_PRR]["S2"],
    )
    q_s3 = k6595.qualified(
        metrics[TARGET_PRR]["S3"],
        bootstrap["arms"][TARGET_PRR]["S3"],
    )
    delta = (
        float(metrics[TARGET_PRR]["S3"]["macro_recall"])
        - float(metrics[TARGET_PRR]["S2"]["macro_recall"])
    )
    gain = bool(
        q_s3
        and delta >= GAIN_POINT_MIN
        and bootstrap["deltas"]["D_MRIG"]["ci_lower"] > GAIN_CI_LOWER_MIN
    )

    if gain:
        status = "PASS"
        verdict = "MRIG_V1_QUALIFIES_MECH_PRR_REPRESENTATION"
    elif q_s3:
        status = "NEGATIVE"
        verdict = "MRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S2"
    else:
        status = "NEGATIVE"
        verdict = "MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION"

    return {
        "status": status,
        "verdict": verdict,
        "primary": {
            "S2_qualified": bool(q_s2),
            "S3_qualified": bool(q_s3),
            "D_MRIG": delta,
            "route_pass": gain,
            "point_gain_min": GAIN_POINT_MIN,
            "bootstrap_ci_lower_min": GAIN_CI_LOWER_MIN,
        },
    }


def feature_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in MRIG_FEATURES:
        arr = np.asarray(
            [float(r["features"][name]) for r in records],
            dtype=np.float64,
        )
        out[name] = {
            "mean": float(arr.mean()),
            "std": float(arr.std(ddof=0)),
            "min": float(arr.min()),
            "max": float(arr.max()),
        }
    return out


def rule_payload(
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "rule": "MRIG-Q-v1",
        "experiment": "KCL-6.5.9.6",
        "primary_target": TARGET_PRR,
        "diagnostic_targets": [TARGET_PR, TARGET_A],
        "feature_sets": {k: list(v) for k, v in FEATURE_SETS.items()},
        "mrig_features": list(MRIG_FEATURES),
        "models": models,
        "protocol_sha256": sha256_file(PROTOCOL),
        "script_sha256": sha256_file(SCRIPT),
        "training_seed_sha256": sha_seed_list(TRAIN_SEEDS),
        "source_git_commit": git_commit(),
        "validation_executed_before_freeze": False,
        "controller_implemented": False,
        "protected_confirmatory_touched": False,
        "kcl7_started": False,
    }


def run_train(output: Path, rule_path: Path) -> dict[str, Any]:
    records = build_records(TRAIN_SEEDS)
    integrity = cohort_integrity(
        records,
        TRAIN_SEEDS,
        expected_records=1440,
        expected_seed_sha=TRAIN_SEED_SHA256,
    )
    integrity.update({
        "all_seed_sha_matches": sha_seed_list(
            tuple(list(TRAIN_SEEDS) + list(VALIDATION_SEEDS))
        ) == ALL_SEED_SHA256,
        "validation_seeds_executed": False,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })

    support = support_table(records)
    support_ok = primary_support_pass(
        support,
        min_count=TRAIN_MIN_COUNT,
        min_seeds=TRAIN_MIN_SEEDS,
    )

    hard = {
        k: v for k, v in integrity.items()
        if k not in {
            "validation_seeds_executed",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_seeds_executed"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.6-TRAIN",
            "status": "REVISE",
            "verdict": "MRIG_V1_TRAIN_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.6-TRAIN",
            "status": "NEGATIVE",
            "verdict": "MRIG_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "mrig_feature_summary": feature_summary(records),
            "records": records,
        }
    else:
        models = fit_all(records)
        solver_ok = all(
            models[target][arm]["solver"]["converged"]
            for target in TARGETS
            for arm in FEATURE_SETS
        )
        integrity["all_solvers_converged"] = bool(solver_ok)

        if not solver_ok:
            result = {
                "experiment": "KCL-6.5.9.6-TRAIN",
                "status": "REVISE",
                "verdict": "MRIG_V1_TRAIN_INVALID",
                "reason": "frozen solver did not converge",
                "integrity": integrity,
                "support": support,
                "records": records,
            }
        else:
            metrics, _, _ = metrics_all(records, models)
            rule = rule_payload(models)
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            rule_path.write_text(
                json.dumps(rule, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            result = {
                "experiment": "KCL-6.5.9.6-TRAIN",
                "status": "PASS",
                "verdict": "MRIG_V1_MODELS_TRAINED_AND_READY_TO_FREEZE",
                "integrity": integrity,
                "support": support,
                "train_metrics_descriptive": metrics,
                "mrig_feature_summary": feature_summary(records),
                "rule": {
                    "path": str(rule_path),
                    "sha256": sha256_file(rule_path),
                },
                "records": records,
                "protocol_sha256": sha256_file(PROTOCOL),
                "script_sha256": sha256_file(SCRIPT),
                "source_git_commit": git_commit(),
                "environment": {"python": platform.python_version()},
                "governance": {
                    "validation_executed": False,
                    "controller_implemented": False,
                    "protected_confirmatory_touched": False,
                    "kcl7_started": False,
                },
            }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def validate_rule(rule: dict[str, Any]) -> bool:
    return bool(
        rule.get("rule") == "MRIG-Q-v1"
        and rule.get("experiment") == "KCL-6.5.9.6"
        and rule.get("primary_target") == TARGET_PRR
        and rule.get("diagnostic_targets") == [TARGET_PR, TARGET_A]
        and rule.get("mrig_features") == list(MRIG_FEATURES)
        and rule.get("feature_sets") == {
            k: list(v) for k, v in FEATURE_SETS.items()
        }
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and rule.get("script_sha256") == sha256_file(SCRIPT)
        and rule.get("training_seed_sha256") == TRAIN_SEED_SHA256
        and rule.get("validation_executed_before_freeze") is False
        and rule.get("controller_implemented") is False
        and rule.get("protected_confirmatory_touched") is False
        and rule.get("kcl7_started") is False
        and set(rule.get("models", {})) == set(TARGETS)
        and all(
            set(rule["models"][target]) == set(FEATURE_SETS)
            for target in TARGETS
        )
    )


def run_validation(output: Path, rule_path: Path) -> dict[str, Any]:
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if not validate_rule(rule):
        result = {
            "experiment": "KCL-6.5.9.6-VALIDATION",
            "status": "REVISE",
            "verdict": "MRIG_V1_VALIDATION_INVALID",
            "reason": "frozen rule contract invalid",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    records = build_records(VALIDATION_SEEDS)
    integrity = cohort_integrity(
        records,
        VALIDATION_SEEDS,
        expected_records=720,
        expected_seed_sha=VALIDATION_SEED_SHA256,
    )
    integrity.update({
        "rule_valid": True,
        "validation_refit": False,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })
    support = support_table(records)
    support_ok = primary_support_pass(
        support,
        min_count=VAL_MIN_COUNT,
        min_seeds=VAL_MIN_SEEDS,
    )

    hard = {
        k: v for k, v in integrity.items()
        if k not in {
            "validation_refit",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = (
        integrity["validation_refit"] is False
        and integrity["protected_confirmatory_touched"] is False
        and integrity["controller_implemented"] is False
        and integrity["kcl7_started"] is False
    )

    if not all(hard.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.6-VALIDATION",
            "status": "REVISE",
            "verdict": "MRIG_V1_VALIDATION_INVALID",
            "integrity": integrity,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.6-VALIDATION",
            "status": "NEGATIVE",
            "verdict": "MRIG_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT",
            "integrity": integrity,
            "support": support,
            "mrig_feature_summary": feature_summary(records),
            "records": records,
        }
    else:
        models = rule["models"]
        metrics, preds, probs = metrics_all(records, models)
        bootstrap = paired_bootstrap(records, preds, probs)
        adj = adjudicate(metrics, bootstrap)
        secondary = {
            "D_PR": (
                metrics[TARGET_PR]["S3"]["macro_recall"]
                - metrics[TARGET_PR]["S2"]["macro_recall"]
            ),
            "D_A": (
                metrics[TARGET_A]["S3"]["macro_recall"]
                - metrics[TARGET_A]["S2"]["macro_recall"]
            ),
        }
        result = {
            "experiment": "KCL-6.5.9.6-VALIDATION",
            **adj,
            "integrity": integrity,
            "support": support,
            "metrics": metrics,
            "bootstrap": bootstrap,
            "secondary_diagnostics": secondary,
            "mrig_feature_summary": feature_summary(records),
            "rule": {
                "path": str(rule_path),
                "sha256": sha256_file(rule_path),
                "source_git_commit": rule.get("source_git_commit"),
            },
            "records": records,
            "protocol_sha256": sha256_file(PROTOCOL),
            "script_sha256": sha256_file(SCRIPT),
            "source_git_commit": git_commit(),
            "environment": {"python": platform.python_version()},
            "governance": {
                "validation_refit": False,
                "controller_implemented": False,
                "protected_confirmatory_touched": False,
                "kcl7_started": False,
            },
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "validate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--rule",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl6596_rule.json"),
    )
    args = parser.parse_args()

    if args.phase == "train":
        result = run_train(args.output, args.rule)
    else:
        result = run_validation(args.output, args.rule)

    print(json.dumps({
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "support": result.get("support"),
        "integrity": result.get("integrity"),
        "primary": result.get("primary"),
        "metrics": result.get("metrics"),
        "bootstrap": result.get("bootstrap"),
        "secondary_diagnostics": result.get("secondary_diagnostics"),
        "mrig_feature_summary": result.get("mrig_feature_summary"),
        "rule": result.get("rule"),
    }, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
