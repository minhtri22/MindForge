"""KCL-6.5.9.3 — Boundary Action Identifiability Decomposition.

Compares four frozen information sets with one fixed low-capacity multiclass
model family.  S0/S1/S2 are pre-boundary; O adds a zero-step future-task
interaction probe and is diagnostic only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
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
from experiments.kernel_cl import kcl653_sequential_trajectory_isolation as k653
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl658_localized_boundary_state as k658
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6593-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6593_action_identifiability.py")

CLASS_ORDER = k6592.CLASS_ORDER

TRAIN_SEEDS = tuple(int(x) for x in "1987237,1619978,1292425,1065865,1467009,1404245,1122419,1596677,1657930,1703877,1874678,1896633,1715930,1653353,1182145,1011759,1523944,1718329,1401218,1740501,1322529,1574451,1625871,1578559,1231649,1316846,1090438,1160645,1666965,1995349,1038845,1967227,1316543,1602863,1914159,1092387,1914788,1211242,1214462,1683279,1434677,1427855,1940122,1044444,1738380,1594935,1060035,1424735,1828197,1451762,1520567,1314946,1152121,1367389,1671261,1363551,1407245,1576517,1138057,1214225,1605547,1194036,1773725,1686034,1258367,1164211,1309058,1745896,1048190,1572512,1061773,1517149,1562938,1579974,1940769,1405682,1238539,1252431,1930916,1919738,1787335,1475682,1313561,1181778,1844192,1860110,1707692,1739989,1354075,1353306,1652074,1292662,1803423,1560816,1178808,1838488,1249012,1815972,1772503,1555919,1229438,1289553,1588617,1728652,1721454,1063889,1621239,1341885,1140723,1242762,1799562,1011326,1212801,1800663,1019666,1642513,1023869,1865905,1052899,1438406,1885693,1790514,1075176,1178213,1302633,1117148,1134216,1574221,1760175,1057954,1548509,1615994,1409472,1619953,1919469,1448279,1026535,1482784,1173122,1619569,1733991,1529312,1477091,1390133,1933347,1151850,1224090,1964727,1110312,1990511,1088482,1387158,1620702,1645849,1966812,1822992,1233598,1177787,1623607,1591065,1467017,1491244,1546842,1923903,1318638,1373213,1672782,1435565,1557368,1429978,1400438,1116402,1728880,1101018,1339158,1653104,1225211,1077503,1363436,1652610,1383419,1496548,1818920,1747173,1134996,1773999,1700833,1935466,1999880,1403828,1688476,1765481,1094267,1623232,1241535,1258056,1307007,1578252,1551770,1171238,1942056,1241975,1838896,1535104,1563072,1585186,1315138,1362598,1290116,1927512,1663775,1922200,1001603,1393321,1404257,1228785,1611666,1383775,1264693,1948879,1189323,1066803,1620739,1344583,1568008,1232469,1298394,1594380,1471430,1040791,1090169,1962465,1766041,1208300,1074317,1049165,1769239,1242218,1763732,1544928,1898013,1575562,1312369,1244909,1227549,1833284,1885250,1759747,1069785,1802027,1146219,1089137,1112870,1624265,1862781,1291024,1909436,1254514,1947140,1655161,1014141,1354529,1033812,1738871,1146210,1803816,1571660,1318685,1930792,1050713,1739643,1388359,1661364,1656611,1353707,1931002,1222918,1731033,1910641,1736461,1601691,1972730,1589955,1467361,1004400,1966316,1841046,1039786,1461609,1870988,1821804,1141556,1984968,1708148,1624275,1531015,1791093,1694424,1748185,1097458".split(","))
VALIDATION_SEEDS = tuple(int(x) for x in "1948788,1545332,1865052,1261110,1385037,1614442,1652687,1002290,1201311,1143934,1902970,1469992,1481029,1687443,1694186,1312898,1852277,1531242,1245111,1586708,1601767,1629770,1238933,1272708,1712920,1779271,1420318,1087536,1199180,1927477,1391851,1668436,1649769,1199747,1684055,1529442,1559572,1425987,1308172,1964166,1031381,1811533,1607736,1136834,1912574,1623454,1770446,1609102,1822654,1443657,1676850,1619336,1155582,1771706,1472666,1354307,1224781,1144320,1319198,1067061,1966597,1447277,1080703,1353673,1210738,1164882,1585586,1798548,1172396,1883890,1017037,1901122,1942564,1060265,1394265,1564920,1703431,1859078,1800638,1710590,1791238,1523873,1853833,1522414,1442772,1301773,1590554,1873538,1047164,1074993,1555532,1811873,1003444,1358706,1169280,1973722,1188600,1581433,1557976,1294003,1174526,1029591,1986589,1691275,1538186,1822200,1920601,1558125,1170663,1361365,1067700,1414270,1008004,1970501,1837945,1780963,1737219,1383785,1498241,1156838,1659443,1335252,1249840,1776826,1423780,1777136,1764635,1279849,1823405,1429062,1708551,1574299,1857439,1779302,1220514,1746881,1695324,1839589,1916959,1119950,1794760,1338808,1713524,1699560,1035542,1494791,1063845,1567004,1020875,1774151".split(","))

S0_FEATURES = ("STAGE_2", "STAGE_3")
S1_FEATURES = k6592.PRIMARY_FEATURES
S2_FEATURES = S1_FEATURES + tuple(f"F{i}" for i in range(1, 14))
PROBE_FEATURES = (
    "P1_NEXT_TASK_LOSS",
    "P2_NEXT_GRAD_NORM",
    "P3_NEXT_GRAD_DRIFT_COSINE",
    "P4_NEXT_GRAD_PRESSURE_COSINE",
    "P5_NEXT_GRAD_RETENTION_COSINE",
    "P6_NEXT_GRAD_DRIFT_SHARE_OVERLAP",
    "P7_NEXT_GRAD_PRESSURE_SHARE_OVERLAP",
    "P8_NEXT_GRAD_RETENTION_SHARE_OVERLAP",
)
O_FEATURES = S2_FEATURES + PROBE_FEATURES

FEATURE_SETS = {
    "S0": S0_FEATURES,
    "S1": S1_FEATURES,
    "S2": S2_FEATURES,
    "O": O_FEATURES,
}

TRAIN_MIN_COUNT = 20
TRAIN_MIN_SEEDS = 20
VAL_MIN_COUNT = 10
VAL_MIN_SEEDS = 10

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 6593

QUAL_MACRO_RECALL = 0.60
QUAL_MACRO_F1 = 0.50
QUAL_CLASS_RECALL = 0.50
QUAL_CLASS_F1 = 0.35
QUAL_BOOTSTRAP_LOWER = 0.45

R_D21_MIN = 0.10
R_D21_CI_LOWER = 0.03
I_DO2_MIN = 0.15
I_DO2_CI_LOWER = 0.05
M_DO2_MIN = 0.10
M_DO2_CI_LOWER = 0.03


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    denom = float(torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b))
    if denom <= 1e-20:
        return 0.0
    return float(torch.dot(a, b) / denom)


def _recursive_equal(a: Any, b: Any) -> bool:
    if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
        return torch.equal(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_recursive_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_recursive_equal(x, y) for x, y in zip(a, b))
    return a == b


def _normalized(values: dict[str, float]) -> dict[str, float]:
    total = float(sum(values.values()))
    if not math.isfinite(total) or total <= 1e-20:
        raise RuntimeError("probe share denominator invalid")
    out = {k: float(v / total) for k, v in values.items()}
    if abs(sum(out.values()) - 1.0) > 1e-9:
        raise RuntimeError("probe shares do not sum to one")
    return out


def extract_future_probe(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    pre_task_model_state: dict[str, torch.Tensor],
    observed_tasks: list[tuple[str, tuple[torch.Tensor, torch.Tensor]]],
    next_task: tuple[torch.Tensor, torch.Tensor],
) -> dict[str, Any]:
    model_before = copy.deepcopy(model.state_dict())
    opt_before = copy.deepcopy(optimizer.state_dict())

    local_state = k658._group_vectors(
        model,
        optimizer,
        pre_task_model_state,
        observed_tasks,
    )
    groups = local_state["groups"]
    vec = local_state["vectors"]

    model.zero_grad(set_to_none=True)
    x, y = next_task
    next_loss = F.cross_entropy(model(x)[:, -1, :], y)
    next_loss.backward()

    params = dict(model.named_parameters())
    next_by_group: dict[str, torch.Tensor] = {}
    for group in k653.GROUP_ORDER:
        parts = []
        for name in groups[group]:
            g = params[name].grad
            ref = params[name].detach().float().reshape(-1)
            parts.append(
                torch.zeros_like(ref)
                if g is None
                else g.detach().float().reshape(-1)
            )
        next_by_group[group] = torch.cat(parts)

    q = _normalized({
        g: float(torch.linalg.vector_norm(next_by_group[g]))
        for g in k653.GROUP_ORDER
    })
    d = _normalized({g: float(vec[g]["D"]) for g in k653.GROUP_ORDER})
    p = _normalized({g: float(vec[g]["P"]) for g in k653.GROUP_ORDER})
    k = _normalized({g: float(vec[g]["K"]) for g in k653.GROUP_ORDER})

    next_vec = torch.cat([next_by_group[g] for g in k653.GROUP_ORDER])
    drift_vec = torch.cat([vec[g]["drift"] for g in k653.GROUP_ORDER])
    pressure_vec = torch.cat([vec[g]["pressure"] for g in k653.GROUP_ORDER])
    retention_vec = torch.cat([vec[g]["retention_grad"] for g in k653.GROUP_ORDER])

    features = {
        "P1_NEXT_TASK_LOSS": float(next_loss.detach()),
        "P2_NEXT_GRAD_NORM": float(torch.linalg.vector_norm(next_vec)),
        "P3_NEXT_GRAD_DRIFT_COSINE": _cosine(-next_vec, drift_vec),
        "P4_NEXT_GRAD_PRESSURE_COSINE": _cosine(-next_vec, -pressure_vec),
        "P5_NEXT_GRAD_RETENTION_COSINE": _cosine(-next_vec, -retention_vec),
        "P6_NEXT_GRAD_DRIFT_SHARE_OVERLAP": sum(q[g] * d[g] for g in k653.GROUP_ORDER),
        "P7_NEXT_GRAD_PRESSURE_SHARE_OVERLAP": sum(q[g] * p[g] for g in k653.GROUP_ORDER),
        "P8_NEXT_GRAD_RETENTION_SHARE_OVERLAP": sum(q[g] * k[g] for g in k653.GROUP_ORDER),
    }
    if not all(math.isfinite(float(v)) for v in features.values()):
        raise RuntimeError("non-finite FUTURE-PROBE-v1 feature")

    model.zero_grad(set_to_none=True)
    model_unchanged = _recursive_equal(model_before, model.state_dict())
    optimizer_unchanged = _recursive_equal(opt_before, optimizer.state_dict())
    gradients_cleared = all(p.grad is None for p in model.parameters())

    return {
        "features": features,
        "details": {
            "next_grad_share": q,
            "model_unchanged": model_unchanged,
            "optimizer_unchanged": optimizer_unchanged,
            "gradients_cleared": gradients_cleared,
        },
    }


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    prior = (
        set(k656.DISCOVERY_SEEDS)
        | set(k656.CONFIRM_SEEDS)
        | set(k6591.REPLICATION_SEEDS)
        | set(k6592.TRAIN_SEEDS)
        | set(k6592.VALIDATION_SEEDS)
    )
    return set(seeds).isdisjoint(prior)


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

            next_task = tasks[boundary_index]
            probe = extract_future_probe(
                model=model,
                optimizer=opt,
                pre_task_model_state=pre_task_model_state,
                observed_tasks=observed,
                next_task=next_task[1],
            )

            features = {k: float(v) for k, v in global_features.items()}
            for name in tuple(f"F{i}" for i in range(1, 14)):
                features[name] = float(localized["features"][name])
            features.update({k: float(v) for k, v in probe["features"].items()})

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
            target, flags = k6592.target_from_outcomes(counter["outcomes"])

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
                "target": target,
                "safe_flags": flags,
                "counterfactual_outcomes": counter["outcomes"],
                "localized_details": localized["details"],
                "probe_details": probe["details"],
                "integrity": {
                    "counterfactual_valid": bool(counter["integrity"]["valid"]),
                    "lrbs_shares_valid": bool(lrbs_shares_valid),
                    "probe_model_unchanged": bool(probe["details"]["model_unchanged"]),
                    "probe_optimizer_unchanged": bool(probe["details"]["optimizer_unchanged"]),
                    "probe_gradients_cleared": bool(probe["details"]["gradients_cleared"]),
                },
            })

            pre_task_model_state = copy.deepcopy(model.state_dict())
            model = counter["_reference_model"]
            opt = counter["_reference_optimizer"]
            memories = counter["_next_memories"]
            observed = tasks[: boundary_index + 1]

    return out


def support_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return k6592.support_table(records)


def support_pass(table: dict[str, dict[str, Any]], train: bool) -> bool:
    return k6592.support_pass(
        table,
        TRAIN_MIN_COUNT if train else VAL_MIN_COUNT,
        TRAIN_MIN_SEEDS if train else VAL_MIN_SEEDS,
    )


def cohort_integrity(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
    expected_records: int,
) -> dict[str, bool]:
    counts = Counter(int(r["seed"]) for r in records)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))

    return {
        "seed_count_exact": len(seeds) == len(set(seeds)),
        "record_count_exact": len(records) == expected_records,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(boundaries[s] == {1, 2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "features_finite": all(
            all(math.isfinite(float(v)) for v in r["features"].values())
            for r in records
        ),
        "target_valid": all(r["target"] in CLASS_ORDER for r in records),
        "counterfactual_integrity_valid": all(
            r["integrity"]["counterfactual_valid"] for r in records
        ),
        "lrbs_shares_valid": all(
            r["integrity"]["lrbs_shares_valid"] for r in records
        ),
        "probe_model_unchanged": all(
            r["integrity"]["probe_model_unchanged"] for r in records
        ),
        "probe_optimizer_unchanged": all(
            r["integrity"]["probe_optimizer_unchanged"] for r in records
        ),
        "probe_gradients_cleared": all(
            r["integrity"]["probe_gradients_cleared"] for r in records
        ),
    }


def fit_all(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        name: k6592.fit_softmax(records, features)
        for name, features in FEATURE_SETS.items()
    }


def metrics_all(
    records: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]], dict[str, np.ndarray]]:
    out, preds, probs = {}, {}, {}
    for name, model in models.items():
        p, pr = k6592.predict_model(records, model)
        preds[name] = p
        probs[name] = pr
        out[name] = k6592.metrics(records, p, pr)
    return out, preds, probs


def _percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q, method="linear"))


def paired_bootstrap(
    records: list[dict[str, Any]],
    preds: dict[str, list[str]],
    probs: dict[str, np.ndarray],
) -> dict[str, Any]:
    seeds = sorted({int(r["seed"]) for r in records})
    by_seed: dict[int, list[int]] = {s: [] for s in seeds}
    for i, r in enumerate(records):
        by_seed[int(r["seed"])].append(i)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    arm_recall = {name: [] for name in FEATURE_SETS}
    arm_f1 = {name: [] for name in FEATURE_SETS}
    deltas = {"D10": [], "D21": [], "DO2": []}

    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = rng.integers(0, len(seeds), size=len(seeds))
        idxs = [i for j in drawn for i in by_seed[seeds[int(j)]]]
        rr = [records[i] for i in idxs]
        mr: dict[str, float] = {}
        for name in FEATURE_SETS:
            pp = [preds[name][i] for i in idxs]
            pr = probs[name][idxs, :]
            m = k6592.metrics(rr, pp, pr)
            arm_recall[name].append(float(m["macro_recall"]))
            arm_f1[name].append(float(m["macro_f1"]))
            mr[name] = float(m["macro_recall"])
        deltas["D10"].append(mr["S1"] - mr["S0"])
        deltas["D21"].append(mr["S2"] - mr["S1"])
        deltas["DO2"].append(mr["O"] - mr["S2"])

    arms = {}
    for name in FEATURE_SETS:
        arms[name] = {
            "macro_recall": {
                "ci_lower": _percentile(arm_recall[name], 2.5),
                "ci_upper": _percentile(arm_recall[name], 97.5),
            },
            "macro_f1": {
                "ci_lower": _percentile(arm_f1[name], 2.5),
                "ci_upper": _percentile(arm_f1[name], 97.5),
            },
        }

    delta_out = {}
    for name, values in deltas.items():
        delta_out[name] = {
            "ci_lower": _percentile(values, 2.5),
            "ci_upper": _percentile(values, 97.5),
        }

    return {
        "arms": arms,
        "deltas": delta_out,
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
    }


def qualified(metrics: dict[str, Any], bootstrap_arm: dict[str, Any]) -> bool:
    return bool(
        metrics["macro_recall"] >= QUAL_MACRO_RECALL
        and metrics["macro_f1"] >= QUAL_MACRO_F1
        and all(
            metrics["per_class"][c]["recall"] >= QUAL_CLASS_RECALL
            and metrics["per_class"][c]["f1"] >= QUAL_CLASS_F1
            for c in CLASS_ORDER
        )
        and bootstrap_arm["macro_recall"]["ci_lower"] > QUAL_BOOTSTRAP_LOWER
    )


def adjudicate(
    metrics: dict[str, dict[str, Any]],
    bootstrap: dict[str, Any],
) -> dict[str, Any]:
    q = {
        name: qualified(metrics[name], bootstrap["arms"][name])
        for name in FEATURE_SETS
    }
    d10 = metrics["S1"]["macro_recall"] - metrics["S0"]["macro_recall"]
    d21 = metrics["S2"]["macro_recall"] - metrics["S1"]["macro_recall"]
    do2 = metrics["O"]["macro_recall"] - metrics["S2"]["macro_recall"]

    route_r = (
        not q["S1"]
        and q["S2"]
        and d21 >= R_D21_MIN
        and bootstrap["deltas"]["D21"]["ci_lower"] > R_D21_CI_LOWER
    )
    route_i = (
        not q["S2"]
        and q["O"]
        and do2 >= I_DO2_MIN
        and bootstrap["deltas"]["DO2"]["ci_lower"] > I_DO2_CI_LOWER
    )
    route_m = (
        q["S2"]
        and q["O"]
        and do2 >= M_DO2_MIN
        and bootstrap["deltas"]["DO2"]["ci_lower"] > M_DO2_CI_LOWER
    )

    if route_r:
        status = "PASS"
        verdict = "PREBOUNDARY_REPRESENTATION_GAP_IDENTIFIED"
    elif route_i:
        status = "PASS"
        verdict = "FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED"
    elif route_m:
        status = "PASS"
        verdict = "MIXED_PREBOUNDARY_AND_INTERACTION_INFORMATION_GAIN"
    else:
        status = "NEGATIVE"
        verdict = "BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE"

    return {
        "status": status,
        "verdict": verdict,
        "qualified": q,
        "routes": {
            "R_PREBOUNDARY_REPRESENTATION_GAP": bool(route_r),
            "I_FUTURE_INTERACTION_GAP": bool(route_i),
            "M_MIXED_INFORMATION_GAIN": bool(route_m),
        },
        "point_deltas_macro_recall": {
            "D10": d10,
            "D21": d21,
            "DO2": do2,
        },
        "thresholds": {
            "base": {
                "macro_recall_min": QUAL_MACRO_RECALL,
                "macro_f1_min": QUAL_MACRO_F1,
                "per_class_recall_min": QUAL_CLASS_RECALL,
                "per_class_f1_min": QUAL_CLASS_F1,
                "bootstrap_macro_recall_lower_strictly_gt": QUAL_BOOTSTRAP_LOWER,
            },
            "R": {"D21_min": R_D21_MIN, "D21_ci_lower_gt": R_D21_CI_LOWER},
            "I": {"DO2_min": I_DO2_MIN, "DO2_ci_lower_gt": I_DO2_CI_LOWER},
            "M": {"DO2_min": M_DO2_MIN, "DO2_ci_lower_gt": M_DO2_CI_LOWER},
        },
    }


def run_train(output: Path, rule_path: Path) -> dict[str, Any]:
    if set(TRAIN_SEEDS) & set(VALIDATION_SEEDS):
        raise RuntimeError("train/validation seed overlap")

    records = build_records(TRAIN_SEEDS)
    integ = cohort_integrity(records, TRAIN_SEEDS, 900)
    integ.update({
        "validation_seeds_executed": False,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })

    required_true = {
        k: v for k, v in integ.items()
        if k not in {
            "validation_seeds_executed",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = all(
        integ[k] is False for k in (
            "validation_seeds_executed",
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        )
    )
    support = support_table(records)
    support_ok = support_pass(support, train=True)

    if not all(required_true.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.3-TRAIN",
            "status": "REVISE",
            "verdict": "BOUNDARY_ACTION_IDENTIFIABILITY_INVALID",
            "integrity": integ,
            "support": support,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.3-TRAIN",
            "status": "NEGATIVE",
            "verdict": "IDENTIFIABILITY_TRAIN_SUPPORT_INSUFFICIENT",
            "integrity": integ,
            "support": support,
            "records": records,
        }
    else:
        models = fit_all(records)
        solvers_ok = all(m["solver"]["converged"] for m in models.values())
        integ["all_solvers_converged"] = bool(solvers_ok)
        if not solvers_ok:
            result = {
                "experiment": "KCL-6.5.9.3-TRAIN",
                "status": "REVISE",
                "verdict": "BOUNDARY_ACTION_IDENTIFIABILITY_INVALID",
                "reason": "frozen solver did not converge",
                "integrity": integ,
                "support": support,
                "solvers": {k: v["solver"] for k, v in models.items()},
                "records": records,
            }
        else:
            train_metrics, _, _ = metrics_all(records, models)
            result = {
                "experiment": "KCL-6.5.9.3-TRAIN",
                "status": "PASS",
                "verdict": "IDENTIFIABILITY_MODELS_TRAINED_AND_READY_TO_FREEZE",
                "cohort": {"seeds": list(TRAIN_SEEDS), "records": len(records)},
                "support": support,
                "train_metrics": train_metrics,
                "integrity": integ,
                "records": records,
                "protocol_sha256": sha256_file(PROTOCOL),
                "script_sha256": sha256_file(SCRIPT),
                "source_git_commit": git_commit(),
                "environment": {
                    "python": platform.python_version(),
                    "torch": torch.__version__,
                    "numpy": np.__version__,
                },
            }
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

            rule = {
                "experiment": "KCL-6.5.9.3-RULE",
                "status": "FROZEN_FROM_TRAIN_ONLY",
                "class_order": list(CLASS_ORDER),
                "feature_sets": {k: list(v) for k, v in FEATURE_SETS.items()},
                "models": models,
                "train_seeds": list(TRAIN_SEEDS),
                "validation_seeds": list(VALIDATION_SEEDS),
                "training_support": support,
                "training_metrics": train_metrics,
                "protocol_sha256": sha256_file(PROTOCOL),
                "script_sha256": sha256_file(SCRIPT),
                "training_evidence_sha256": sha256_file(output),
                "source_git_commit": git_commit(),
                "governance": {
                    "validation_executed_before_freeze": False,
                    "protected_confirmatory_touched": False,
                    "controller_implemented": False,
                    "kcl7_started": False,
                },
            }
            rule_path.write_text(json.dumps(rule, indent=2, sort_keys=True) + "\n")
            return result

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def validate_rule(rule: dict[str, Any]) -> bool:
    return bool(
        rule.get("experiment") == "KCL-6.5.9.3-RULE"
        and rule.get("status") == "FROZEN_FROM_TRAIN_ONLY"
        and tuple(rule.get("class_order", [])) == CLASS_ORDER
        and tuple(rule.get("train_seeds", [])) == TRAIN_SEEDS
        and tuple(rule.get("validation_seeds", [])) == VALIDATION_SEEDS
        and rule.get("feature_sets") == {k: list(v) for k, v in FEATURE_SETS.items()}
        and rule.get("protocol_sha256") == sha256_file(PROTOCOL)
        and set(rule.get("models", {})) == set(FEATURE_SETS)
        and rule.get("governance", {}).get("validation_executed_before_freeze") is False
        and rule.get("governance", {}).get("protected_confirmatory_touched") is False
        and rule.get("governance", {}).get("controller_implemented") is False
        and rule.get("governance", {}).get("kcl7_started") is False
    )


def run_validate(rule_path: Path, output: Path) -> dict[str, Any]:
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    rule_sha = sha256_file(rule_path)
    if not validate_rule(rule):
        result = {
            "experiment": "KCL-6.5.9.3-VALIDATION",
            "status": "REVISE",
            "verdict": "BOUNDARY_ACTION_IDENTIFIABILITY_INVALID",
            "reason": "frozen rule contract invalid",
            "rule_sha256": rule_sha,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    records = build_records(VALIDATION_SEEDS)
    integ = cohort_integrity(records, VALIDATION_SEEDS, 450)
    integ.update({
        "train_validation_overlap_absent": set(TRAIN_SEEDS).isdisjoint(VALIDATION_SEEDS),
        "rule_loaded_without_refit": True,
        "protected_confirmatory_touched": False,
        "controller_implemented": False,
        "kcl7_started": False,
    })
    required_true = {
        k: v for k, v in integ.items()
        if k not in {
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        }
    }
    governance_ok = all(
        integ[k] is False for k in (
            "protected_confirmatory_touched",
            "controller_implemented",
            "kcl7_started",
        )
    )

    support = support_table(records)
    support_ok = support_pass(support, train=False)

    if not all(required_true.values()) or not governance_ok:
        result = {
            "experiment": "KCL-6.5.9.3-VALIDATION",
            "status": "REVISE",
            "verdict": "BOUNDARY_ACTION_IDENTIFIABILITY_INVALID",
            "integrity": integ,
            "support": support,
            "rule_sha256": rule_sha,
        }
    elif not support_ok:
        result = {
            "experiment": "KCL-6.5.9.3-VALIDATION",
            "status": "NEGATIVE",
            "verdict": "IDENTIFIABILITY_VALIDATION_SUPPORT_INSUFFICIENT",
            "integrity": integ,
            "support": support,
            "rule_sha256": rule_sha,
            "records": records,
        }
    else:
        metrics, preds, probs = metrics_all(records, rule["models"])
        bootstrap = paired_bootstrap(records, preds, probs)
        decision = adjudicate(metrics, bootstrap)
        result = {
            "experiment": "KCL-6.5.9.3-VALIDATION",
            "status": decision["status"],
            "verdict": decision["verdict"],
            "cohort": {"seeds": list(VALIDATION_SEEDS), "records": len(records)},
            "support": support,
            "metrics": metrics,
            "bootstrap_95pct": bootstrap,
            "adjudication": decision,
            "integrity": integ,
            "rule": {
                "path": str(rule_path),
                "sha256": rule_sha,
                "source_git_commit": rule.get("source_git_commit"),
                "training_evidence_sha256": rule.get("training_evidence_sha256"),
            },
            "records": records,
            "environment": {
                "python": platform.python_version(),
                "torch": torch.__version__,
                "numpy": np.__version__,
            },
            "governance": {
                "refit_on_validation": False,
                "protected_confirmatory_touched": False,
                "controller_implemented": False,
                "kcl7_started": False,
            },
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "validate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--rule",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl6593_rule.json"),
    )
    args = parser.parse_args()

    if args.phase == "train":
        result = run_train(args.output, args.rule)
    else:
        result = run_validate(args.rule, args.output)

    summary = {
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "support": result.get("support"),
        "train_metrics": result.get("train_metrics"),
        "metrics": result.get("metrics"),
        "bootstrap_95pct": result.get("bootstrap_95pct"),
        "adjudication": result.get("adjudication"),
        "integrity": result.get("integrity"),
        "rule": result.get("rule"),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
