"""KCL-1: qualify a controlled continual-learning forgetting substrate.

This experiment intentionally changes no MindForge model architecture. It reuses
mindforge.model.TransformerLM and tests whether sequential optimization produces
reproducible forgetting on a jointly representable pair of token-level tasks.

Protocol: docs/research/kernel-continual-learning/kcl0-kcl1-protocol.md
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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from mindforge.config import ModelConfig
from mindforge.model import TransformerLM, parameter_count


PROTOCOL = Path("docs/research/kernel-continual-learning/kcl0-kcl1-protocol.md")
QUALIFICATION_SEEDS = (404, 505)
CANDIDATE_ORDER = (
    "C1_TASK_PREFIX_CYCLIC",
    "C2_TASK_PREFIX_REVERSE",
    "C3_TASK_PREFIX_BLOCKSWAP",
)


@dataclass(frozen=True)
class KCL1Config:
    vocab_size: int = 96
    d_model: int = 16
    n_heads: int = 2
    n_layers: int = 1
    max_context: int = 2
    ff_mult: int = 4
    dropout: float = 0.0
    relations: int = 24
    batch_size: int = 16
    stage_steps: int = 250
    learning_rate: float = 3e-3
    weight_decay: float = 0.0


@dataclass(frozen=True)
class Gates:
    independent_accuracy_min: float = 0.95
    sequential_acquisition_min: float = 0.95
    forgetting_min: float = 0.50
    control_drift_abs_max: float = 0.10


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_model(config: KCL1Config, seed: int) -> TransformerLM:
    set_seed(seed)
    model_config = ModelConfig(
        vocab_size=config.vocab_size,
        d_model=config.d_model,
        n_heads=config.n_heads,
        n_layers=config.n_layers,
        max_context=config.max_context,
        ff_mult=config.ff_mult,
        dropout=config.dropout,
    )
    return TransformerLM(model_config).cpu()


def candidate_tasks(
    candidate: str, config: KCL1Config
) -> tuple[tuple[torch.Tensor, torch.Tensor], tuple[torch.Tensor, torch.Tensor]]:
    n = config.relations
    if n != 24:
        raise ValueError("KCL-1 frozen protocol requires exactly 24 relations")
    keys = torch.arange(10, 10 + n, dtype=torch.long)
    values_a = torch.arange(40, 40 + n, dtype=torch.long)
    if int(values_a.max()) >= config.vocab_size:
        raise ValueError("vocabulary too small for frozen KCL-1 mapping")

    if candidate == "C1_TASK_PREFIX_CYCLIC":
        values_b = values_a.roll(1)
    elif candidate == "C2_TASK_PREFIX_REVERSE":
        values_b = torch.flip(values_a, dims=[0])
    elif candidate == "C3_TASK_PREFIX_BLOCKSWAP":
        half = n // 2
        values_b = torch.cat([values_a[half:], values_a[:half]])
    else:
        raise ValueError(f"unknown candidate: {candidate}")

    input_a = torch.stack([torch.full_like(keys, 2), keys], dim=1)
    input_b = torch.stack([torch.full_like(keys, 3), keys], dim=1)
    return (input_a, values_a), (input_b, values_b)


def evaluate(model: TransformerLM, task: tuple[torch.Tensor, torch.Tensor]) -> dict[str, float]:
    x, y = task
    model.eval()
    with torch.no_grad():
        logits = model(x)[:, -1, :]
        loss = F.cross_entropy(logits, y)
        predicted = logits.argmax(dim=-1)
        accuracy = (predicted == y).float().mean()
    return {"loss": float(loss), "accuracy": float(accuracy)}


def train_stage(
    model: TransformerLM,
    optimizer: torch.optim.Optimizer,
    task: tuple[torch.Tensor, torch.Tensor],
    *,
    steps: int,
    batch_size: int,
    seed: int,
) -> None:
    x, y = task
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    model.train()
    for _ in range(steps):
        indices = torch.randint(0, len(y), (batch_size,), generator=generator)
        logits = model(x[indices])[:, -1, :]
        loss = F.cross_entropy(logits, y[indices])
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite KCL-1 training loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


def optimizer_for(model: TransformerLM, config: KCL1Config) -> torch.optim.AdamW:
    return torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )


def independent_run(
    task: tuple[torch.Tensor, torch.Tensor],
    *,
    config: KCL1Config,
    seed: int,
    stream_offset: int,
) -> dict[str, float]:
    model = build_model(config, seed)
    optimizer = optimizer_for(model, config)
    train_stage(
        model,
        optimizer,
        task,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + stream_offset,
    )
    return evaluate(model, task)


def sequential_run(
    task_a: tuple[torch.Tensor, torch.Tensor],
    task_b: tuple[torch.Tensor, torch.Tensor],
    *,
    config: KCL1Config,
    seed: int,
) -> dict[str, Any]:
    model = build_model(config, seed)
    optimizer = optimizer_for(model, config)

    train_stage(
        model,
        optimizer,
        task_a,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 101,
    )
    a_after_a = evaluate(model, task_a)

    control_model = copy.deepcopy(model)
    control_optimizer = optimizer_for(control_model, config)
    control_optimizer.load_state_dict(copy.deepcopy(optimizer.state_dict()))

    train_stage(
        control_model,
        control_optimizer,
        task_a,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 211,
    )
    a_after_a2 = evaluate(control_model, task_a)

    train_stage(
        model,
        optimizer,
        task_b,
        steps=config.stage_steps,
        batch_size=config.batch_size,
        seed=seed + 307,
    )
    a_after_b = evaluate(model, task_a)
    b_after_b = evaluate(model, task_b)

    forgetting = a_after_a["accuracy"] - a_after_b["accuracy"]
    control_drift = a_after_a["accuracy"] - a_after_a2["accuracy"]
    return {
        "a_after_a": a_after_a,
        "a_after_b": a_after_b,
        "b_after_b": b_after_b,
        "a_after_a2_control": a_after_a2,
        "forgetting_accuracy": forgetting,
        "control_drift_accuracy": control_drift,
    }


def seed_pass(result: dict[str, Any], gates: Gates) -> bool:
    values = [
        result["independent_a"]["accuracy"],
        result["independent_b"]["accuracy"],
        result["sequential"]["a_after_a"]["accuracy"],
        result["sequential"]["b_after_b"]["accuracy"],
        result["sequential"]["forgetting_accuracy"],
        result["sequential"]["control_drift_accuracy"],
    ]
    if not all(math.isfinite(float(v)) for v in values):
        return False
    return (
        result["independent_a"]["accuracy"] >= gates.independent_accuracy_min
        and result["independent_b"]["accuracy"] >= gates.independent_accuracy_min
        and result["sequential"]["a_after_a"]["accuracy"] >= gates.sequential_acquisition_min
        and result["sequential"]["b_after_b"]["accuracy"] >= gates.sequential_acquisition_min
        and result["sequential"]["forgetting_accuracy"] >= gates.forgetting_min
        and abs(result["sequential"]["control_drift_accuracy"]) <= gates.control_drift_abs_max
    )


def run_candidate(candidate: str, config: KCL1Config, gates: Gates) -> dict[str, Any]:
    task_a, task_b = candidate_tasks(candidate, config)
    per_seed: list[dict[str, Any]] = []
    for seed in QUALIFICATION_SEEDS:
        result = {
            "seed": seed,
            "independent_a": independent_run(task_a, config=config, seed=seed, stream_offset=17),
            "independent_b": independent_run(task_b, config=config, seed=seed, stream_offset=31),
            "sequential": sequential_run(task_a, task_b, config=config, seed=seed),
        }
        result["pass"] = seed_pass(result, gates)
        per_seed.append(result)
    return {
        "candidate": candidate,
        "seeds": list(QUALIFICATION_SEEDS),
        "per_seed": per_seed,
        "pass": all(item["pass"] for item in per_seed),
    }


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    config = KCL1Config()
    gates = Gates()
    results: list[dict[str, Any]] = []
    selected: str | None = None
    for candidate in CANDIDATE_ORDER:
        outcome = run_candidate(candidate, config, gates)
        results.append(outcome)
        if outcome["pass"]:
            selected = candidate
            break

    passed = selected is not None
    model = build_model(config, QUALIFICATION_SEEDS[0])
    return {
        "experiment": "KCL-1",
        "status": "PASS" if passed else "STOP",
        "verdict": (
            "VALID_FORGETTING_SUBSTRATE_ESTABLISHED"
            if passed
            else "VALID_FORGETTING_SUBSTRATE_NOT_ESTABLISHED"
        ),
        "selected_candidate": selected,
        "candidate_order": list(CANDIDATE_ORDER),
        "evaluated_candidates": [item["candidate"] for item in results],
        "qualification_seeds": list(QUALIFICATION_SEEDS),
        "config": asdict(config),
        "gates": asdict(gates),
        "model_parameter_count": parameter_count(model),
        "model_architecture_changed": False,
        "results": results,
        "protocol": str(PROTOCOL),
        "protocol_sha256": _sha256(PROTOCOL),
        "git_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "scope": {
            "external_api_calls": 0,
            "teacher_inference": 0,
            "reasoning_work": False,
            "pit": False,
            "oir_ppv": False,
            "ppf": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen MindForge KCL-1 substrate qualification")
    parser.add_argument(
        "--output",
        default="experiments/kernel_cl/results/kcl1_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
