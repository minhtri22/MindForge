"""KCL-6.2: reconstructive replay-memory A/B/C experiment."""

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
    KCL1Config, build_model, evaluate, optimizer_for, parameter_count, train_stage
)
from experiments.kernel_cl.kcl6_long_horizon import TASK_ORDER, task_sequence, replay_task_index
from experiments.kernel_cl import kcl61_weighted_replay_ab as k61

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl62-protocol.md")
KCL6_EVIDENCE = Path("experiments/kernel_cl/results/kcl6_summary.json")
KCL61_EVIDENCE = Path("experiments/kernel_cl/results/kcl61_summary.json")

FINAL_SEEDS = (3333, 3535, 3737, 3939, 4141)
CURRENT_PER_BATCH = 15
REPLAY_PER_BATCH = 1
BATCH_SIZE = 16
REPLAY_FRACTION = 1 / 16
CORE_SCHEMA_BYTES = 41
RESIDUAL_BYTES = 24
BEHAVIOR_TOLERANCE = 1 / 24
T4_ACCURACY_MIN = 0.95
A_OVER_C_BYTE_COMPRESSION_MIN = 2.0
C_RESIDUAL_RATE_MAX = 0.25

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
    k6 = json.loads(KCL6_EVIDENCE.read_text(encoding="utf-8"))
    k61e = json.loads(KCL61_EVIDENCE.read_text(encoding="utf-8"))
    k6_ok = (
        k6.get("status") == "PASS"
        and k6.get("verdict") == "FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON"
        and k6.get("task_order") == list(TASK_ORDER)
        and abs(float(k6["replay"]["fraction"]) - REPLAY_FRACTION) < 1e-12
    )
    k61_ok = (
        k61e.get("status") == "NEGATIVE"
        and k61e.get("verdict")
        == "EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE"
        and k61e.get("task_order") == list(TASK_ORDER)
        and abs(float(k61e["replay"]["fraction"]) - REPLAY_FRACTION) < 1e-12
    )
    return {
        "valid": k6_ok and k61_ok,
        "kcl6_valid": k6_ok,
        "kcl61_valid": k61_ok,
        "kcl6_sha256": _sha256(KCL6_EVIDENCE),
        "kcl61_sha256": _sha256(KCL61_EVIDENCE),
    }


def task_observations(task: tuple[torch.Tensor, torch.Tensor]) -> list[Observation]:
    x, y = task
    return [(int(x[i, 0]), int(x[i, 1]), int(y[i])) for i in range(len(y))]


@dataclass(frozen=True)
class AffineSchema:
    varying_position: int
    constant_token: int
    key_min: int
    output_min: int
    modulus: int
    multiplier: int
    offset: int
    support_count: int

    def observation(self, key: int) -> Observation:
        target = self.output_min + (
            (self.multiplier * (key - self.key_min) + self.offset) % self.modulus
        )
        if self.varying_position == 0:
            return (key, self.constant_token, target)
        return (self.constant_token, key, target)


@dataclass
class ReconstructiveStore:
    schema: AffineSchema
    keys: list[int]
    residuals: dict[int, Observation]
    original: list[Observation]

    @classmethod
    def from_task(cls, task: tuple[torch.Tensor, torch.Tensor]) -> "ReconstructiveStore":
        obs = task_observations(task)
        c0, c1 = len({o[0] for o in obs}), len({o[1] for o in obs})
        if (c0 == 1) == (c1 == 1):
            raise ValueError("requires exactly one varying input position")
        varying = 1 if c0 == 1 else 0
        constant = 1 - varying
        constant_values = {o[constant] for o in obs}
        if len(constant_values) != 1:
            raise ValueError("constant position is not constant")
        token = next(iter(constant_values))
        keys = sorted({o[varying] for o in obs})
        if len(keys) != len(obs) or keys != list(range(keys[0], keys[0] + len(keys))):
            raise ValueError("keys must be unique and contiguous")
        n = len(keys)
        output_min = min(o[2] for o in obs)
        if any(not (output_min <= o[2] < output_min + n) for o in obs):
            raise ValueError("targets must lie in contiguous width-N band")
        by_key = {o[varying]: o for o in obs}

        best = (-1, 0, 0)
        for a in range(n):
            for b in range(n):
                matches = sum(
                    by_key[k][2]
                    == output_min + ((a * (k - keys[0]) + b) % n)
                    for k in keys
                )
                if matches > best[0]:
                    best = (matches, a, b)

        schema = AffineSchema(
            varying, token, keys[0], output_min, n, best[1], best[2], best[0]
        )
        residuals = {
            k: by_key[k]
            for k in keys
            if schema.observation(k) != by_key[k]
        }
        store = cls(schema, keys, residuals, obs)
        if store.reconstructed() != store.canonical_original():
            raise ValueError("schema plus residuals did not reconstruct exactly")
        return store

    def canonical_original(self) -> list[Observation]:
        p = self.schema.varying_position
        return sorted(self.original, key=lambda o: o[p])

    def observation_at_rank(self, rank: int) -> Observation:
        key = self.keys[rank]
        return self.residuals.get(key, self.schema.observation(key))

    def reconstructed(self) -> list[Observation]:
        return [self.observation_at_rank(i) for i in range(len(self.keys))]

    @property
    def coverage(self) -> float:
        return self.schema.support_count / len(self.keys)

    @property
    def residual_rate(self) -> float:
        return len(self.residuals) / len(self.keys)

    @property
    def logical_bytes(self) -> int:
        return CORE_SCHEMA_BYTES + len(self.residuals) * RESIDUAL_BYTES


def _sample_current(
    task: tuple[torch.Tensor, torch.Tensor], gen: torch.Generator
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = task
    idx = torch.randint(0, len(y), (CURRENT_PER_BATCH,), generator=gen)
    return x[idx], y[idx]


def _train_c_stage(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    previous: list[ReconstructiveStore],
    current: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    seed: int,
    stage: int,
) -> dict[str, Any]:
    current_gen = torch.Generator(device="cpu")
    current_gen.manual_seed(seed + 1000 * stage + 101)
    rank_gens = []
    for i in range(len(previous)):
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed + 1000 * stage + 503 + 37 * i)
        rank_gens.append(gen)

    replay_counts = [0 for _ in previous]
    model.train()
    for step in range(steps):
        cx, cy = _sample_current(current, current_gen)
        source = replay_task_index(step, len(previous))
        replay_counts[source] += 1
        rank = int(torch.randint(0, len(previous[source].keys), (1,), generator=rank_gens[source]).item())
        obs = previous[source].observation_at_rank(rank)
        rx, ry = k61.observation_to_tensors(obs)
        x = torch.cat([cx, rx], dim=0)
        y = torch.cat([cy, ry], dim=0)
        loss = F.cross_entropy(model(x)[:, -1, :], y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite C replay loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    return {"replay_counts": replay_counts, "total_replay": sum(replay_counts)}


def _evaluate_all(
    model: torch.nn.Module,
    tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    count: int,
) -> dict[str, dict[str, float]]:
    return {name: evaluate(model, task) for name, task in tasks[:count]}


def run_c(seed: int, config: KCL1Config) -> dict[str, Any]:
    tasks = task_sequence(config)
    names = [n for n, _ in tasks]
    model = build_model(config, seed)
    optimizer = optimizer_for(model, config)
    train_stage(
        model, optimizer, tasks[0][1],
        steps=config.stage_steps, batch_size=config.batch_size, seed=seed + 101
    )
    stores = [ReconstructiveStore.from_task(tasks[0][1])]
    matrices = {"after_T1": _evaluate_all(model, tasks, 1)}
    accounting = {}

    for idx in range(1, len(tasks)):
        stage = idx + 1
        accounting[f"after_T{stage}"] = _train_c_stage(
            model, optimizer, stores, tasks[idx][1],
            steps=config.stage_steps, seed=seed, stage=stage
        )
        matrices[f"after_T{stage}"] = _evaluate_all(model, tasks, idx + 1)
        stores.append(ReconstructiveStore.from_task(tasks[idx][1]))

    final = {n: matrices["after_T4"][n]["accuracy"] for n in names}
    prior = names[:3]
    return {
        "final_accuracy": final,
        "mean_prior_accuracy": statistics.fmean(final[n] for n in prior),
        "worst_prior_accuracy": min(final[n] for n in prior),
        "average_accuracy_all_tasks": statistics.fmean(final.values()),
        "T4_accuracy": final[names[3]],
        "stores": [
            {
                "task": names[i],
                "varying_position": s.schema.varying_position,
                "constant_token": s.schema.constant_token,
                "key_min": s.schema.key_min,
                "output_min": s.schema.output_min,
                "modulus": s.schema.modulus,
                "multiplier": s.schema.multiplier,
                "offset": s.schema.offset,
                "coverage": s.coverage,
                "residual_count": len(s.residuals),
                "residual_rate": s.residual_rate,
                "logical_bytes": s.logical_bytes,
                "reconstruction_exact": s.reconstructed() == s.canonical_original(),
            }
            for i, s in enumerate(stores)
        ],
        "logical_bytes": sum(s.logical_bytes for s in stores),
        "residual_rate": sum(len(s.residuals) for s in stores) / sum(len(s.keys) for s in stores),
        "stage_accounting": accounting,
    }


def relearning_probe(
    task_name: str,
    task: tuple[torch.Tensor, torch.Tensor],
    store: ReconstructiveStore,
    config: KCL1Config,
    seed: int,
) -> dict[str, Any]:
    original = store.canonical_original()
    reconstructed = store.reconstructed()
    dataset_equal = original == reconstructed

    def to_task(obs: list[Observation]) -> tuple[torch.Tensor, torch.Tensor]:
        return (
            torch.tensor([[o[0], o[1]] for o in obs], dtype=torch.long),
            torch.tensor([o[2] for o in obs], dtype=torch.long),
        )

    original_task, reconstructed_task = to_task(original), to_task(reconstructed)
    models = [build_model(config, seed), build_model(config, seed)]
    opts = [optimizer_for(models[0], config), optimizer_for(models[1], config)]
    curves = [[], []]
    previous = 0
    for checkpoint in (0, 50, 100, 150, 200, 250):
        if checkpoint > previous:
            delta = checkpoint - previous
            stream_seed = seed + 700 + previous
            train_stage(models[0], opts[0], original_task, steps=delta, batch_size=config.batch_size, seed=stream_seed)
            train_stage(models[1], opts[1], reconstructed_task, steps=delta, batch_size=config.batch_size, seed=stream_seed)
            previous = checkpoint
        curves[0].append({"step": checkpoint, **evaluate(models[0], original_task)})
        curves[1].append({"step": checkpoint, **evaluate(models[1], reconstructed_task)})

    states_equal = all(
        torch.equal(models[0].state_dict()[n], models[1].state_dict()[n])
        for n in models[0].state_dict()
    )
    return {
        "task": task_name,
        "dataset_equal": dataset_equal,
        "curves_equal": curves[0] == curves[1],
        "final_model_states_equal": states_equal,
        "pass": dataset_equal and curves[0] == curves[1] and states_equal,
        "original_curve": curves[0],
        "reconstructed_curve": curves[1],
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    config = KCL1Config()
    anchors = _load_anchors()
    tasks = task_sequence(config)

    stores = [ReconstructiveStore.from_task(task) for _, task in tasks]
    schema_validation = [
        {
            "task": tasks[i][0],
            "coverage": s.coverage,
            "residual_count": len(s.residuals),
            "residual_rate": s.residual_rate,
            "logical_bytes": s.logical_bytes,
            "reconstruction_exact": s.reconstructed() == s.canonical_original(),
            "schema": {
                "varying_position": s.schema.varying_position,
                "constant_token": s.schema.constant_token,
                "key_min": s.schema.key_min,
                "output_min": s.schema.output_min,
                "modulus": s.schema.modulus,
                "multiplier": s.schema.multiplier,
                "offset": s.schema.offset,
            },
        }
        for i, s in enumerate(stores)
    ]
    schema_valid = all(r["reconstruction_exact"] for r in schema_validation)

    probes = []
    if anchors["valid"] and schema_valid:
        probes = [
            relearning_probe(name, task, stores[i], config, 5000 + 100 * i)
            for i, (name, task) in enumerate(tasks)
        ]
    probe_valid = bool(probes) and all(p["pass"] for p in probes)

    rows = []
    if anchors["valid"] and schema_valid and probe_valid:
        for seed in FINAL_SEEDS:
            ab = k61.run_seed(seed, config)
            c = run_c(seed, config)
            a_final = ab["final_accuracy"]["A_raw"]
            b_final = ab["final_accuracy"]["B_weighted_exact"]
            c_final = c["final_accuracy"]
            delta_ca = {n: c_final[n] - a_final[n] for n in TASK_ORDER}
            delta_cb = {n: c_final[n] - b_final[n] for n in TASK_ORDER}
            a_mean = ab["final_summary"]["A_mean_prior_accuracy"]
            b_mean = ab["final_summary"]["B_mean_prior_accuracy"]
            c_mean = c["mean_prior_accuracy"]
            a_bytes = ab["storage_by_stage"]["after_T4"]["A_raw"]["logical_bytes"]
            b_bytes = ab["storage_by_stage"]["after_T4"]["B_weighted_exact"]["logical_bytes"]
            a_over_c = a_bytes / c["logical_bytes"]
            storage_pass = (
                a_over_c >= A_OVER_C_BYTE_COMPRESSION_MIN
                and c["residual_rate"] <= C_RESIDUAL_RATE_MAX
            )
            behavior_pass = (
                all(abs(v) <= BEHAVIOR_TOLERANCE for v in delta_ca.values())
                and abs(c_mean - a_mean) <= BEHAVIOR_TOLERANCE
                and c["T4_accuracy"] >= T4_ACCURACY_MIN
            )
            rows.append({
                "seed": seed,
                "A": {"final_accuracy": a_final, "mean_prior_accuracy": a_mean, "logical_bytes": a_bytes},
                "B": {"final_accuracy": b_final, "mean_prior_accuracy": b_mean, "logical_bytes": b_bytes},
                "C": c,
                "delta_C_minus_A": delta_ca,
                "delta_C_minus_B": delta_cb,
                "A_over_C_byte_compression_ratio": a_over_c,
                "B_over_C_byte_compression_ratio": b_bytes / c["logical_bytes"],
                "gates": {
                    "behavioral_equivalence_pass": behavior_pass,
                    "storage_effect_pass": storage_pass,
                },
            })

    integrity = anchors["valid"] and schema_valid and probe_valid and bool(rows)
    behavior = (
        integrity
        and all(r["gates"]["behavioral_equivalence_pass"] for r in rows)
        and abs(statistics.fmean(r["C"]["mean_prior_accuracy"] for r in rows)
                - statistics.fmean(r["A"]["mean_prior_accuracy"] for r in rows))
        <= BEHAVIOR_TOLERANCE
    )
    storage = integrity and all(r["gates"]["storage_effect_pass"] for r in rows)

    if not integrity:
        status, verdict = "REVISE", "RECONSTRUCTIVE_CONTRAST_INVALID"
    elif not behavior:
        status, verdict = "FAIL", "RECONSTRUCTIVE_SCHEMA_CHANGES_CL_BEHAVIOR"
    elif storage:
        status, verdict = "PASS", "RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS"
    else:
        status, verdict = "NEGATIVE", "RECONSTRUCTIVE_SCHEMA_VALID_BUT_NOT_STORAGE_EFFECTIVE"

    aggregates = {}
    if rows:
        for arm in ("A", "B"):
            aggregates[f"{arm}_final_mean_prior_accuracy"] = _stats([r[arm]["mean_prior_accuracy"] for r in rows])
        aggregates["C_final_mean_prior_accuracy"] = _stats([r["C"]["mean_prior_accuracy"] for r in rows])
        aggregates["delta_C_minus_A_mean_prior"] = _stats([r["C"]["mean_prior_accuracy"] - r["A"]["mean_prior_accuracy"] for r in rows])
        aggregates["A_over_C_byte_compression_ratio"] = _stats([r["A_over_C_byte_compression_ratio"] for r in rows])
        aggregates["B_over_C_byte_compression_ratio"] = _stats([r["B_over_C_byte_compression_ratio"] for r in rows])
        aggregates["C_residual_rate"] = _stats([r["C"]["residual_rate"] for r in rows])

    return {
        "experiment": "KCL-6.2",
        "status": status,
        "verdict": verdict,
        "arms": {"A": "RAW_EPISODIC", "B": "WEIGHTED_EXACT", "C": "RECONSTRUCTIVE_SCHEMA_PLUS_RESIDUALS"},
        "final_seeds": list(FINAL_SEEDS),
        "task_order": list(TASK_ORDER),
        "historical_anchors": anchors,
        "schema_validation": schema_validation,
        "relearning_trace_probe": probes,
        "per_seed": rows,
        "aggregates": aggregates,
        "gates": {
            "behavior_tolerance": BEHAVIOR_TOLERANCE,
            "T4_accuracy_min": T4_ACCURACY_MIN,
            "A_over_C_byte_compression_min": A_OVER_C_BYTE_COMPRESSION_MIN,
            "C_residual_rate_max": C_RESIDUAL_RATE_MAX,
            "reconstruction_exact_required": True,
        },
        "integrity": {
            "historical_anchors_valid": anchors["valid"],
            "schema_validation_pass": schema_valid,
            "relearning_trace_probe_pass": probe_valid,
            "paired_contrast_valid": integrity,
            "model_architecture_changed": False,
            "family_formula_or_name_used_by_schema_fitter": False,
        },
        "model_parameter_count": parameter_count(build_model(config, FINAL_SEEDS[0])),
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {"python": platform.python_version(), "torch": torch.__version__, "platform": platform.platform()},
        "scope": {"kcl7_started": False, "fuzzy_decay_started": False, "reasoning_work": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="experiments/kernel_cl/results/kcl62_summary.json")
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
