"""KCL-6.5.4: decompose AdamW boundary state on the frozen POST-T1 model."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from experiments.kernel_cl.kcl1_substrate import (
    KCL1Config, optimizer_for, parameter_count
)
from experiments.kernel_cl.kcl6_long_horizon import task_sequence
from experiments.kernel_cl import kcl652_t4_failure_decomposition as k652
from experiments.kernel_cl import kcl653_sequential_trajectory_isolation as k653

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl654-protocol.md")
KCL653_EVIDENCE = Path("experiments/kernel_cl/results/kcl653_summary.json")

SEED = 9393
STRICT_T4_MIN = 0.95
REPRO_TOLERANCE = 1e-9
T4_STREAM_SEED = 13700
COMPONENTS = ("S", "M", "V")
ARM_BITS = tuple("".join(bits) for bits in itertools.product("01", repeat=3))


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
    return k652._deep_equal(a, b)


def _model_state_equal(a: dict[str, torch.Tensor], b: dict[str, torch.Tensor]) -> bool:
    return a.keys() == b.keys() and all(torch.equal(a[k], b[k]) for k in a)


def _load_anchor() -> dict[str, Any]:
    raw = json.loads(KCL653_EVIDENCE.read_text(encoding="utf-8"))
    factorial = raw.get("factorial_2x2", {})
    valid = (
        raw.get("status") == "PASS"
        and raw.get("verdict") == "MODEL_OPTIMIZER_INTERACTION_ONLY"
        and raw.get("trigger_transition", {}).get("j_star") == 1
        and abs(float(factorial["X10_POST_MODEL_PRE_OPT"]["final_accuracy"]) - 1.0) <= REPRO_TOLERANCE
        and abs(float(factorial["X11_POST_MODEL_POST_OPT"]["final_accuracy"]) - 0.9166666865348816) <= REPRO_TOLERANCE
    )
    return {
        "valid": valid,
        "status": raw.get("status"),
        "verdict": raw.get("verdict"),
        "sha256": _sha256(KCL653_EVIDENCE),
    }


def _post_t1(config: KCL1Config) -> tuple[torch.nn.Module, dict[str, Any]]:
    snapshots, _ = k653._prefix_snapshots(config)
    snap = snapshots[1]
    return copy.deepcopy(snap["model"]), copy.deepcopy(snap["optimizer_state"])


def _name_pid_map(model: torch.nn.Module, opt_state: dict[str, Any]) -> dict[str, int]:
    names = [name for name, _ in model.named_parameters()]
    pids = list(opt_state["param_groups"][0]["params"])
    if len(names) != len(pids):
        raise RuntimeError("named-parameter / optimizer-id count mismatch")
    return dict(zip(names, pids))


def _validate_post_state(model: torch.nn.Module, opt_state: dict[str, Any]) -> dict[str, Any]:
    mapping = _name_pid_map(model, opt_state)
    steps = []
    for name, pid in mapping.items():
        state = opt_state["state"].get(pid)
        if state is None:
            raise RuntimeError(f"missing AdamW state for {name}")
        if set(state) != {"step", "exp_avg", "exp_avg_sq"}:
            raise RuntimeError(f"unexpected AdamW keys for {name}: {sorted(state)}")
        if not torch.is_tensor(state["step"]):
            raise RuntimeError("AdamW step must be tensor")
        steps.append(float(state["step"].item()))
        for key in ("exp_avg", "exp_avg_sq"):
            if not torch.isfinite(state[key]).all():
                raise RuntimeError(f"non-finite {key}")
    return {
        "parameter_state_count": len(mapping),
        "step_min": min(steps),
        "step_max": max(steps),
        "step_unique": sorted(set(steps)),
        "all_steps_250": all(x == 250.0 for x in steps),
    }


def _variant_state(post_state: dict[str, Any], bits: str) -> dict[str, Any]:
    if len(bits) != 3 or any(ch not in "01" for ch in bits):
        raise ValueError(bits)
    keep_s, keep_m, keep_v = (ch == "1" for ch in bits)
    out = copy.deepcopy(post_state)
    for state in out["state"].values():
        if not keep_s:
            state["step"].zero_()
        if not keep_m:
            state["exp_avg"].zero_()
        if not keep_v:
            state["exp_avg_sq"].zero_()
    return out


def _curve_point(model: torch.nn.Module, task: tuple[torch.Tensor, torch.Tensor], step: int) -> dict[str, Any]:
    metric = k653.evaluate(model, task)
    return {"step": step, "accuracy": metric["accuracy"], "loss": metric["loss"]}


def _run_t4(
    post_model: torch.nn.Module,
    config: KCL1Config,
    *,
    optimizer_state: dict[str, Any] | None,
    empty_fresh: bool = False,
) -> dict[str, Any]:
    task = task_sequence(config)[3][1]
    model = copy.deepcopy(post_model)
    opt = optimizer_for(model, config)
    if not empty_fresh:
        if optimizer_state is None:
            raise ValueError("optimizer_state required unless empty_fresh")
        opt.load_state_dict(copy.deepcopy(optimizer_state))

    x, y = task
    gen = torch.Generator(device="cpu")
    gen.manual_seed(T4_STREAM_SEED)
    curve = [_curve_point(model, task, 0)]
    first_train_loss = None
    first_update_l2 = None

    for step in range(1, 251):
        idx = torch.randint(0, len(y), (16,), generator=gen)
        loss = F.cross_entropy(model(x[idx])[:, -1, :], y[idx])
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite T4 loss")
        if step == 1:
            first_train_loss = float(loss)
            before = [p.detach().clone() for p in model.parameters()]
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step == 1:
            sq = 0.0
            for p0, p1 in zip(before, model.parameters()):
                d = (p1.detach() - p0).float()
                sq += float(torch.sum(d * d))
            first_update_l2 = math.sqrt(sq)
        if step in k652.CHECKPOINTS:
            curve.append(_curve_point(model, task, step))

    summary = k652._curve_summary(curve)
    return {
        "curve": curve,
        **summary,
        "first_train_loss": first_train_loss,
        "first_step_update_l2": first_update_l2,
        "_final_model_state": copy.deepcopy(model.state_dict()),
        "_final_optimizer_state": copy.deepcopy(opt.state_dict()),
    }


def _public_run(run: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in run.items() if not k.startswith("_")}


def carried_set(bits: str) -> frozenset[str]:
    return frozenset(c for c, bit in zip(COMPONENTS, bits) if bit == "1")


def minimal_sufficient_sets(arms: dict[str, dict[str, Any]]) -> list[list[str]]:
    failing = {
        carried_set(bits)
        for bits, result in arms.items()
        if result["final_accuracy"] < STRICT_T4_MIN
    }
    minimal = []
    for s in failing:
        if all(t not in failing for t in failing if t < s):
            minimal.append(s)
    minimal.sort(key=lambda x: (len(x), tuple(sorted(x))))
    return [sorted(x) for x in minimal]


def classify_pattern(minimal: list[list[str]]) -> str:
    sets = [frozenset(x) for x in minimal]
    singles = [s for s in sets if len(s) == 1]
    pairs = [s for s in sets if len(s) == 2]
    if len(singles) == 1 and len(sets) == 1:
        c = next(iter(singles[0]))
        return {
            "S": "STEP_ONLY_SUFFICIENT",
            "M": "FIRST_MOMENT_ONLY_SUFFICIENT",
            "V": "SECOND_MOMENT_ONLY_SUFFICIENT",
        }[c]
    if len(singles) >= 2:
        return "MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT"
    if len(pairs) == 1 and len(sets) == 1:
        p = pairs[0]
        if p == frozenset({"S", "M"}):
            return "STEP_FIRST_MOMENT_INTERACTION"
        if p == frozenset({"S", "V"}):
            return "STEP_SECOND_MOMENT_INTERACTION"
        if p == frozenset({"M", "V"}):
            return "FIRST_SECOND_MOMENT_INTERACTION"
    if len(pairs) >= 2 and not singles:
        return "MULTIPLE_PAIR_INTERACTIONS"
    if sets == [frozenset({"S", "M", "V"})]:
        return "THREE_WAY_ADAMW_INTERACTION_REQUIRED"
    return "ADAMW_COMPONENT_PATTERN_MIXED"


def architecture_mapping(cls: str) -> str:
    return {
        "STEP_ONLY_SUFFICIENT": "OPTIMIZER_AGE_BIAS_CORRECTION_GOVERNANCE",
        "FIRST_MOMENT_ONLY_SUFFICIENT": "FIRST_MOMENT_BOUNDARY_GOVERNANCE",
        "SECOND_MOMENT_ONLY_SUFFICIENT": "SECOND_MOMENT_PRECONDITIONER_GOVERNANCE",
        "STEP_FIRST_MOMENT_INTERACTION": "AGE_MOMENTUM_BOUNDARY_COORDINATION",
        "STEP_SECOND_MOMENT_INTERACTION": "AGE_VARIANCE_BOUNDARY_COORDINATION",
        "FIRST_SECOND_MOMENT_INTERACTION": "MOMENT_PAIR_BOUNDARY_COORDINATION",
        "THREE_WAY_ADAMW_INTERACTION_REQUIRED": "FULL_ADAMW_BOUNDARY_STATE_COORDINATION",
        "MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT": "ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION",
        "MULTIPLE_PAIR_INTERACTIONS": "ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION",
        "ADAMW_COMPONENT_PATTERN_MIXED": "ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION",
    }[cls]


def moment_diagnostics(
    model: torch.nn.Module,
    post_state: dict[str, Any],
) -> dict[str, Any]:
    mapping = _name_pid_map(model, post_state)
    groups = k653.parameter_groups(model)
    out: dict[str, Any] = {}
    for group, names in groups.items():
        m1s, m2s = [], []
        for name in names:
            st = post_state["state"][mapping[name]]
            m1s.append(st["exp_avg"].detach().float().reshape(-1))
            m2s.append(st["exp_avg_sq"].detach().float().reshape(-1))
        m1 = torch.cat(m1s)
        m2 = torch.cat(m2s)
        out[group] = {
            "element_count": int(m1.numel()),
            "exp_avg_l2": float(torch.linalg.vector_norm(m1)),
            "exp_avg_max_abs": float(m1.abs().max()),
            "exp_avg_sq_l2": float(torch.linalg.vector_norm(m2)),
            "exp_avg_sq_max_abs": float(m2.abs().max()),
            "finite": bool(torch.isfinite(m1).all() and torch.isfinite(m2).all()),
        }
    return out


def run_experiment() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    anchor = _load_anchor()
    config = KCL1Config()
    if not anchor["valid"]:
        return {
            "experiment": "KCL-6.5.4",
            "status": "REVISE",
            "verdict": "ADAMW_BOUNDARY_DECOMPOSITION_INVALID",
            "reason": "KCL-6.5.3 anchor invalid",
        }

    post_model, post_state = _post_t1(config)
    post_validation = _validate_post_state(post_model, post_state)

    fresh = _run_t4(post_model, config, optimizer_state=None, empty_fresh=True)
    internal_arms: dict[str, dict[str, Any]] = {}
    for bits in ARM_BITS:
        internal_arms[bits] = _run_t4(
            post_model,
            config,
            optimizer_state=_variant_state(post_state, bits),
        )

    o000 = internal_arms["000"]
    o111 = internal_arms["111"]

    fresh_equiv = (
        fresh["curve"] == o000["curve"]
        and _model_state_equal(fresh["_final_model_state"], o000["_final_model_state"])
        and _deep_equal(fresh["_final_optimizer_state"], o000["_final_optimizer_state"])
    )
    reproduction = (
        abs(o000["final_accuracy"] - 1.0) <= REPRO_TOLERANCE
        and abs(o111["final_accuracy"] - 0.9166666865348816) <= REPRO_TOLERANCE
    )

    arms = {bits: _public_run(run) for bits, run in internal_arms.items()}
    minimal = minimal_sufficient_sets(arms)
    pattern = classify_pattern(minimal)
    necessity = {
        "S_step": arms["011"]["final_accuracy"] >= STRICT_T4_MIN,
        "M_exp_avg": arms["101"]["final_accuracy"] >= STRICT_T4_MIN,
        "V_exp_avg_sq": arms["110"]["final_accuracy"] >= STRICT_T4_MIN,
    }

    finite = all(
        math.isfinite(float(point["loss"])) and math.isfinite(float(point["accuracy"]))
        for run in [fresh, *internal_arms.values()]
        for point in run["curve"]
    )
    moment_diag = moment_diagnostics(post_model, post_state)
    moments_finite = all(x["finite"] for x in moment_diag.values())

    valid = (
        post_validation["all_steps_250"]
        and fresh_equiv
        and reproduction
        and finite
        and moments_finite
    )

    if not valid:
        status = "REVISE"
        verdict = "ADAMW_BOUNDARY_DECOMPOSITION_INVALID"
        architecture = None
    else:
        status = "PASS"
        verdict = pattern
        architecture = architecture_mapping(pattern)

    return {
        "experiment": "KCL-6.5.4",
        "status": status,
        "verdict": verdict,
        "seed": SEED,
        "historical_anchor": anchor,
        "post_T1_state_validation": post_validation,
        "fresh_empty_control": _public_run(fresh),
        "factorial_bits_order": "SMV = step / exp_avg / exp_avg_sq",
        "factorial_2x3": arms,
        "minimal_sufficient_failing_sets": minimal,
        "component_necessity_in_111_context": necessity,
        "optimizer_state_class": pattern if valid else None,
        "architecture_gap_candidate": architecture,
        "moment_diagnostics_by_parameter_group": moment_diag,
        "integrity": {
            "fresh_empty_equals_O000": fresh_equiv,
            "O000_reproduces_reset_endpoint": abs(o000["final_accuracy"] - 1.0) <= REPRO_TOLERANCE,
            "O111_reproduces_carry_all_endpoint": abs(o111["final_accuracy"] - 0.9166666865348816) <= REPRO_TOLERANCE,
            "all_step_values_250": post_validation["all_steps_250"],
            "all_metrics_finite": finite and moments_finite,
            "model_fixed_POST_T1_across_arms": True,
            "T4_stream_fixed": True,
            "architecture_changed": False,
            "optimizer_hyperparameters_changed": False,
            "kcl7_started": False,
        },
        "model_parameter_count": parameter_count(post_model),
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
        default="experiments/kernel_cl/results/kcl654_summary.json",
    )
    args = parser.parse_args()
    result = run_experiment()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
