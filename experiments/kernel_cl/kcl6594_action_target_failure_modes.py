"""KCL-6.5.9.4 — Action-Target Failure-Mode Decomposition.

Outcome/target decomposition only. No predictor, representation selection,
controller, or protected-confirmatory execution is authorized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.kernel_cl.kcl1_substrate import KCL1Config
from experiments.kernel_cl import kcl656_boundary_health_signal as k656
from experiments.kernel_cl import kcl659_boundary_regime_decomposition as k659
from experiments.kernel_cl import kcl6591_boundary_regime_replication as k6591
from experiments.kernel_cl import kcl6592_regime_predictability as k6592
from experiments.kernel_cl import kcl6593_action_identifiability as k6593

PROTOCOL = Path("docs/research/kernel-continual-learning/kcl6594-protocol.md")
SCRIPT = Path("experiments/kernel_cl/kcl6594_action_target_failure_modes.py")

DISCOVERY_SEEDS = tuple(int(x) for x in """2838987,2260592,2786574,2479853,2849829,2852497,2908145,2080106,2286404,2923169,2986655,2477765,2436718,2531113,2891994,2941301,2085125,2386776,2836284,2549218,2338458,2784786,2329345,2410357,2345916,2062582,2791619,2285711,2551197,2442934,2151929,2588465,2157141,2834675,2571303,2599700,2970554,2216653,2965635,2821119,2709055,2542053,2428100,2192579,2183894,2648510,2774048,2136955,2181100,2727385,2325116,2174117,2210080,2470384,2013173,2372554,2424797,2393968,2151760,2730988,2532283,2392389,2230993,2983541,2925089,2487584,2097508,2142666,2597042,2366001,2504330,2989512,2123595,2762808,2883383,2233773,2050678,2029919,2711889,2704446,2596340,2830290,2958432,2854038,2616299,2190666,2554806,2640809,2927117,2417880,2057149,2987294,2416967,2773190,2450486,2288025,2783391,2949568,2624351,2302243,2075928,2455045,2726968,2210745,2925313,2305862,2813366,2944679,2760931,2416608,2689954,2665406,2740781,2016948,2272065,2769628,2247070,2647996,2907796,2470203,2693296,2333491,2113978,2362450,2335654,2541679,2772355,2554840,2077445,2521311,2777826,2180893,2154552,2849592,2361135,2857454,2569352,2377537,2856913,2258271,2096314,2061725,2240941,2474862,2283101,2454961,2286917,2886307,2359945,2769515,2494437,2374346,2064652,2647283,2364659,2342239,2701993,2736318,2577030,2629436,2922194,2635262,2172441,2220601,2595902,2360852,2646141,2553403,2283006,2738301,2755583,2001544,2908099,2917404,2753311,2691245,2181318,2534370,2458667,2648886,2038185,2406340,2893445,2595257,2109243,2441882,2268569,2145664,2843344,2787643,2027519,2218282,2260691,2447928,2245448,2814432,2536964,2845106,2218531,2323234,2956473,2333783,2104934,2757138,2461385,2177700,2279584,2103367,2834059,2861663,2744191,2352342,2091361,2588936,2697988,2181857,2278784,2814232,2813593,2514473,2371123,2033483,2259710,2029515,2699583,2059981,2239769,2550088,2449329,2510737,2224245,2903218,2892533,2023362,2289489,2227855,2636528,2648244,2035272,2648660""".split(","))

REPLICATION_SEEDS = tuple(int(x) for x in """2035692,2263915,2655053,2528233,2922969,2918842,2071656,2540777,2092438,2352149,2963136,2648628,2172504,2578521,2486484,2316485,2962298,2726493,2024815,2733605,2224063,2262954,2470224,2069954,2216219,2072573,2819666,2530061,2452773,2781148,2395423,2191726,2733983,2841608,2022881,2857621,2499287,2614848,2265971,2863799,2511932,2488257,2329170,2148536,2003957,2832096,2443980,2580789,2460825,2373072,2945123,2613283,2705434,2717252,2885414,2642547,2846737,2599958,2964189,2363316,2259815,2972088,2450919,2175593,2832782,2665328,2124147,2234675,2459396,2395082,2991148,2564279,2179031,2081756,2852890,2444777,2410931,2054090,2449515,2830727,2805804,2017057,2459845,2626913,2147944,2009603,2493186,2090507,2442975,2276976,2651759,2299249,2629017,2079205,2181039,2541142,2565778,2248481,2375714,2391088,2045831,2072841,2264631,2521218,2603703,2479603,2647359,2938188,2861181,2939371,2866933,2395241,2741432,2781366,2249594,2924061,2173166,2143518,2158890,2267168,2628089,2739204,2523827,2454644,2273811,2673889,2055498,2652152,2480569,2777475,2675520,2917155,2074810,2718380,2779397,2401884,2668796,2901199,2629863,2601117,2694783,2262423,2821568,2568151,2619440,2380974,2847500,2628201,2724004,2320365,2828047,2817238,2649069,2592655,2545805,2007014,2324586,2614370,2085908,2832615,2681706,2319939,2128916,2682585,2520020,2437099,2474455,2171918,2624287,2391873,2356084,2250958,2762081,2713295,2790136,2515489,2798844,2544810,2270714,2786656,2856705,2027670,2046968,2601035,2249520,2216878,2473424,2519548,2066190,2252381,2984397,2113894,2629241,2036049,2960474,2691059,2271308,2804781,2466294,2316216,2759275,2902572,2570037,2242884,2605334,2682645,2803730,2987332,2562137,2525274,2348540,2432806,2411940,2680915,2955452,2479019,2713189,2315154,2254742,2128442,2455763,2615050,2869162,2600750,2279766,2706960,2212275,2414878,2899952,2372196,2078180,2361339,2246457,2012451,2803978,2223355,2158266,2763657,2162434,2008759""".split(","))

A_ONLY_MIN_COUNT = 150
A_ONLY_MIN_SEEDS = 100
MODE_MIN_COUNT = 12
MODE_MIN_SEEDS = 10
MODE_MIN_PREVALENCE = 0.05
STABILITY_ABS_DELTA_MAX = 0.10
BOOTSTRAP_RESAMPLES = 20_000
DISCOVERY_BOOTSTRAP_SEED = 659401
REPLICATION_BOOTSTRAP_SEED = 659402
DELTA_BOOTSTRAP_SEED = 659403

P_REASON = "PLASTICITY_SHORTFALL"
R_REASON = "RETENTION_MARGIN_VIOLATION"
A_REASON = "STRICT_ACCURACY_FAILURE"
REASON_ORDER = (P_REASON, R_REASON, A_REASON)
CODE_TOKEN = {
    P_REASON: "P",
    R_REASON: "R",
    A_REASON: "A",
}


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


def percentile_linear(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("empty percentile input")
    xs = sorted(float(v) for v in values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def entropy_bits(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    n = len(labels)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c)


def failure_reasons(components: dict[str, Any]) -> tuple[str, ...]:
    reasons = []
    if not bool(components["plasticity_gain"]):
        reasons.append(P_REASON)
    if not bool(components["retention_ok"]):
        reasons.append(R_REASON)
    if not bool(components["absolute_ok"]):
        reasons.append(A_REASON)
    return tuple(reasons)


def cause_code(reasons: tuple[str, ...]) -> str:
    if not reasons:
        raise ValueError("unsafe policy must have at least one failure reason")
    if any(r not in REASON_ORDER for r in reasons):
        raise ValueError("unknown failure reason")
    return "+".join(CODE_TOKEN[r] for r in REASON_ORDER if r in reasons)


def mechanism_signature(code_b: str, code_c: str) -> str:
    a, b = sorted((code_b, code_c))
    return f"MECH{{{a},{b}}}"


def ordered_signature(code_b: str, code_c: str) -> str:
    return f"B:{code_b}|C:{code_c}"


def target_from_decomposition(d: dict[str, Any]) -> str:
    safe_b = bool(d["safe_B"])
    safe_c = bool(d["safe_C"])
    if safe_b and safe_c:
        return "B_AND_C_SAFE"
    if safe_b:
        return "B_ONLY"
    if safe_c:
        return "C_ONLY"
    return "A_ONLY"


def prior_overlap_absent(seeds: tuple[int, ...]) -> bool:
    prior = (
        set(k656.DISCOVERY_SEEDS)
        | set(k656.CONFIRM_SEEDS)
        | set(k6591.REPLICATION_SEEDS)
        | set(k6592.TRAIN_SEEDS)
        | set(k6592.VALIDATION_SEEDS)
        | set(k6593.TRAIN_SEEDS)
        | set(k6593.VALIDATION_SEEDS)
    )
    return set(seeds).isdisjoint(prior)


def build_phase_records(seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    cfg = KCL1Config()
    records: list[dict[str, Any]] = []
    for seed in seeds:
        rows = k656.build_boundary_records(seed, cfg)
        for row in rows:
            d = k659.decompose_outcomes(row["counterfactual_outcomes"])
            target = target_from_decomposition(d)
            base = {
                "seed": int(seed),
                "boundary_index": int(row["boundary_index"]),
                "after_task": row.get("after_task"),
                "target": target,
                "safe_B": bool(d["safe_B"]),
                "safe_C": bool(d["safe_C"]),
                "counterfactual_integrity_valid": bool(row["integrity"]["valid"]),
            }
            if target != "A_ONLY":
                records.append(base)
                continue

            bcomp = d["policy_components"][k659.B]
            ccomp = d["policy_components"][k659.C]
            b_reasons = failure_reasons(bcomp)
            c_reasons = failure_reasons(ccomp)
            code_b = cause_code(b_reasons)
            code_c = cause_code(c_reasons)
            margins = {
                "B": {
                    "auc_delta_vs_A": float(bcomp["auc_delta_vs_A"]),
                    "final_accuracy_delta_vs_A": float(bcomp["final_accuracy_delta_vs_A"]),
                    "retention_delta_vs_A": float(bcomp["retention_delta_vs_A"]),
                },
                "C": {
                    "auc_delta_vs_A": float(ccomp["auc_delta_vs_A"]),
                    "final_accuracy_delta_vs_A": float(ccomp["final_accuracy_delta_vs_A"]),
                    "retention_delta_vs_A": float(ccomp["retention_delta_vs_A"]),
                },
            }
            finite = all(
                math.isfinite(float(v))
                for p in margins.values()
                for v in p.values()
            )
            records.append({
                **base,
                "failure_reasons": {
                    "B": list(b_reasons),
                    "C": list(c_reasons),
                },
                "cause_codes": {"B": code_b, "C": code_c},
                "ordered_signature": ordered_signature(code_b, code_c),
                "mechanism_signature": mechanism_signature(code_b, code_c),
                "same_cause_set": code_b == code_c,
                "margins": margins,
                "failure_integrity": {
                    "B_nonempty": bool(b_reasons),
                    "C_nonempty": bool(c_reasons),
                    "B_exact_complement": set(b_reasons) == {
                        r for r, ok in (
                            (P_REASON, bool(bcomp["plasticity_gain"])),
                            (R_REASON, bool(bcomp["retention_ok"])),
                            (A_REASON, bool(bcomp["absolute_ok"])),
                        ) if not ok
                    },
                    "C_exact_complement": set(c_reasons) == {
                        r for r, ok in (
                            (P_REASON, bool(ccomp["plasticity_gain"])),
                            (R_REASON, bool(ccomp["retention_ok"])),
                            (A_REASON, bool(ccomp["absolute_ok"])),
                        ) if not ok
                    },
                    "both_policies_unsafe": not bool(d["safe_B"]) and not bool(d["safe_C"]),
                    "margins_finite": finite,
                },
            })
    return records


def phase_integrity(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> dict[str, bool]:
    counts = Counter(int(r["seed"]) for r in records)
    boundaries: dict[int, set[int]] = defaultdict(set)
    for r in records:
        boundaries[int(r["seed"])].add(int(r["boundary_index"]))

    a_only = [r for r in records if r["target"] == "A_ONLY"]
    failure_ok = all(all(r["failure_integrity"].values()) for r in a_only)

    return {
        "seed_count_exact": len(seeds) == 240 and len(set(seeds)) == 240,
        "record_count_exact": len(records) == 720,
        "three_records_per_seed": all(counts[s] == 3 for s in seeds),
        "boundaries_1_2_3_per_seed": all(boundaries[s] == {1, 2, 3} for s in seeds),
        "prior_overlap_absent": prior_overlap_absent(seeds),
        "counterfactual_integrity_valid": all(
            r["counterfactual_integrity_valid"] for r in records
        ),
        "targets_valid": all(
            r["target"] in {"A_ONLY", "C_ONLY", "B_AND_C_SAFE", "B_ONLY"}
            for r in records
        ),
        "a_only_failure_integrity_valid": failure_ok,
        "mechanism_exchange_invariant": all(
            mechanism_signature(r["cause_codes"]["C"], r["cause_codes"]["B"])
            == r["mechanism_signature"]
            for r in a_only
        ),
    }


def a_only_support(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [r for r in records if r["target"] == "A_ONLY"]
    return {
        "count": len(rows),
        "unique_seed_count": len({int(r["seed"]) for r in rows}),
        "passed": (
            len(rows) >= A_ONLY_MIN_COUNT
            and len({int(r["seed"]) for r in rows}) >= A_ONLY_MIN_SEEDS
        ),
    }


def mode_table(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = [r for r in records if r["target"] == "A_ONLY"]
    denom = len(rows)
    signatures = sorted({r["mechanism_signature"] for r in rows})
    out: dict[str, dict[str, Any]] = {}
    for sig in signatures:
        rr = [r for r in rows if r["mechanism_signature"] == sig]
        by_boundary = Counter(int(r["boundary_index"]) for r in rr)
        count = len(rr)
        uniq = len({int(r["seed"]) for r in rr})
        prevalence = count / denom if denom else 0.0
        out[sig] = {
            "count": count,
            "unique_seed_count": uniq,
            "prevalence_among_A_ONLY": prevalence,
            "boundary_counts": {
                "1": by_boundary[1],
                "2": by_boundary[2],
                "3": by_boundary[3],
            },
            "supported": bool(
                count >= MODE_MIN_COUNT
                and uniq >= MODE_MIN_SEEDS
                and prevalence >= MODE_MIN_PREVALENCE
            ),
        }
    return out


def descriptive_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [r for r in records if r["target"] == "A_ONLY"]
    ordered = Counter(r["ordered_signature"] for r in rows)
    b_codes = Counter(r["cause_codes"]["B"] for r in rows)
    c_codes = Counter(r["cause_codes"]["C"] for r in rows)
    atomic_b = Counter()
    atomic_c = Counter()
    same = 0
    for r in rows:
        atomic_b.update(r["failure_reasons"]["B"])
        atomic_c.update(r["failure_reasons"]["C"])
        same += int(bool(r["same_cause_set"]))
    labels = [r["mechanism_signature"] for r in rows]
    h = entropy_bits(labels)
    return {
        "ordered_signature_counts": dict(sorted(ordered.items())),
        "per_policy_cause_code_counts": {
            "B": dict(sorted(b_codes.items())),
            "C": dict(sorted(c_codes.items())),
        },
        "atomic_reason_counts": {
            "B": dict(sorted(atomic_b.items())),
            "C": dict(sorted(atomic_c.items())),
        },
        "same_cause_set_count": same,
        "different_cause_set_count": len(rows) - same,
        "mechanism_entropy_bits": h,
        "effective_mode_count_2_pow_H": 2 ** h,
    }


def cluster_bootstrap_prevalence(
    records: list[dict[str, Any]],
    *,
    rng_seed: int,
    signatures: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    rows = [r for r in records if r["target"] == "A_ONLY"]
    seeds = sorted({int(r["seed"]) for r in records})
    by_seed: dict[int, list[dict[str, Any]]] = {s: [] for s in seeds}
    for r in rows:
        by_seed[int(r["seed"])].append(r)
    if signatures is None:
        signatures = sorted({r["mechanism_signature"] for r in rows})

    rng = random.Random(rng_seed)
    draws = {sig: [] for sig in signatures}
    used = 0
    for _ in range(BOOTSTRAP_RESAMPLES):
        sampled = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        sample_rows = [r for s in sampled for r in by_seed[s]]
        if not sample_rows:
            continue
        used += 1
        cnt = Counter(r["mechanism_signature"] for r in sample_rows)
        n = len(sample_rows)
        for sig in signatures:
            draws[sig].append(cnt[sig] / n)

    return {
        sig: {
            "ci_lower": percentile_linear(vals, 0.025),
            "ci_upper": percentile_linear(vals, 0.975),
            "resamples_used": used,
            "seed": rng_seed,
        }
        for sig, vals in draws.items()
    }


def independent_delta_bootstrap(
    discovery_records: list[dict[str, Any]],
    replication_records: list[dict[str, Any]],
    signatures: list[str],
) -> dict[str, dict[str, Any]]:
    d_seeds = sorted({int(r["seed"]) for r in discovery_records})
    r_seeds = sorted({int(r["seed"]) for r in replication_records})
    d_by: dict[int, list[dict[str, Any]]] = {s: [] for s in d_seeds}
    r_by: dict[int, list[dict[str, Any]]] = {s: [] for s in r_seeds}
    for row in discovery_records:
        if row["target"] == "A_ONLY":
            d_by[int(row["seed"])].append(row)
    for row in replication_records:
        if row["target"] == "A_ONLY":
            r_by[int(row["seed"])].append(row)

    rng = random.Random(DELTA_BOOTSTRAP_SEED)
    draws = {sig: [] for sig in signatures}
    used = 0
    for _ in range(BOOTSTRAP_RESAMPLES):
        ds = [d_seeds[rng.randrange(len(d_seeds))] for _ in d_seeds]
        rs = [r_seeds[rng.randrange(len(r_seeds))] for _ in r_seeds]
        dr = [x for s in ds for x in d_by[s]]
        rr = [x for s in rs for x in r_by[s]]
        if not dr or not rr:
            continue
        used += 1
        dc = Counter(x["mechanism_signature"] for x in dr)
        rc = Counter(x["mechanism_signature"] for x in rr)
        for sig in signatures:
            draws[sig].append(rc[sig] / len(rr) - dc[sig] / len(dr))

    return {
        sig: {
            "ci_lower": percentile_linear(vals, 0.025),
            "ci_upper": percentile_linear(vals, 0.975),
            "resamples_used": used,
            "seed": DELTA_BOOTSTRAP_SEED,
        }
        for sig, vals in draws.items()
    }


def phase_payload(
    records: list[dict[str, Any]],
    seeds: tuple[int, ...],
    phase: str,
) -> dict[str, Any]:
    integ = phase_integrity(records, seeds)
    support = a_only_support(records)
    modes = mode_table(records)
    bootstrap = cluster_bootstrap_prevalence(
        records,
        rng_seed=(
            DISCOVERY_BOOTSTRAP_SEED
            if phase == "discovery"
            else REPLICATION_BOOTSTRAP_SEED
        ),
    )
    return {
        "phase": phase,
        "cohort": {
            "seeds": list(seeds),
            "records": len(records),
        },
        "integrity": integ,
        "A_ONLY_support": support,
        "mechanism_modes": modes,
        "bootstrap_prevalence_95pct": bootstrap,
        "descriptive": descriptive_summary(records),
        "records": records,
    }


def run_discovery(output: Path) -> dict[str, Any]:
    if set(DISCOVERY_SEEDS) & set(REPLICATION_SEEDS):
        raise RuntimeError("discovery/replication overlap")
    records = build_phase_records(DISCOVERY_SEEDS)
    payload = phase_payload(records, DISCOVERY_SEEDS, "discovery")

    if not all(payload["integrity"].values()):
        status = "REVISE"
        verdict = "ACTION_TARGET_FAILURE_MODE_DECOMPOSITION_INVALID"
        authorized = False
    elif not payload["A_ONLY_support"]["passed"]:
        status = "NEGATIVE"
        verdict = "A_ONLY_FAILURE_MODE_DISCOVERY_SUPPORT_INSUFFICIENT"
        authorized = False
    else:
        supported = [
            sig
            for sig, v in payload["mechanism_modes"].items()
            if v["supported"]
        ]
        authorized = len(supported) >= 2
        if authorized:
            status = "PASS"
            verdict = "A_ONLY_FAILURE_MODE_DISCOVERY_SUPPORTS_REPLICATION"
        else:
            status = "NEGATIVE"
            verdict = "NO_SUPPORTED_A_ONLY_FAILURE_MODE_HETEROGENEITY"

    result = {
        "experiment": "KCL-6.5.9.4-DISCOVERY",
        "status": status,
        "verdict": verdict,
        **payload,
        "discovery_supported_modes": [
            sig
            for sig, v in payload["mechanism_modes"].items()
            if v["supported"]
        ],
        "replication_authorized": bool(authorized),
        "protocol_sha256": sha256_file(PROTOCOL),
        "script_sha256": sha256_file(SCRIPT),
        "source_git_commit": git_commit(),
        "environment": {
            "python": platform.python_version(),
        },
        "governance": {
            "classifier_trained": False,
            "controller_implemented": False,
            "protected_confirmatory_touched": False,
            "kcl7_started": False,
            "replication_executed": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def validate_discovery_for_replication(discovery: dict[str, Any]) -> bool:
    return bool(
        discovery.get("experiment") == "KCL-6.5.9.4-DISCOVERY"
        and discovery.get("status") == "PASS"
        and discovery.get("verdict")
        == "A_ONLY_FAILURE_MODE_DISCOVERY_SUPPORTS_REPLICATION"
        and discovery.get("replication_authorized") is True
        and discovery.get("protocol_sha256") == sha256_file(PROTOCOL)
        and len(discovery.get("discovery_supported_modes", [])) >= 2
        and all(discovery.get("integrity", {}).values())
        and discovery.get("governance", {}).get("replication_executed") is False
        and discovery.get("governance", {}).get("protected_confirmatory_touched") is False
        and discovery.get("governance", {}).get("kcl7_started") is False
    )


def run_replication(discovery_path: Path, output: Path) -> dict[str, Any]:
    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    if not validate_discovery_for_replication(discovery):
        result = {
            "experiment": "KCL-6.5.9.4-REPLICATION",
            "status": "REVISE",
            "verdict": "ACTION_TARGET_FAILURE_MODE_REPLICATION_INVALID",
            "reason": "discovery authorization contract invalid",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result

    records = build_phase_records(REPLICATION_SEEDS)
    payload = phase_payload(records, REPLICATION_SEEDS, "replication")

    if not all(payload["integrity"].values()):
        status = "REVISE"
        verdict = "ACTION_TARGET_FAILURE_MODE_REPLICATION_INVALID"
        stable: dict[str, Any] = {}
    elif not payload["A_ONLY_support"]["passed"]:
        status = "NEGATIVE"
        verdict = "A_ONLY_FAILURE_MODE_REPLICATION_SUPPORT_INSUFFICIENT"
        stable = {}
    else:
        supported_discovery = list(discovery["discovery_supported_modes"])
        discovery_records = discovery["records"]
        delta_ci = independent_delta_bootstrap(
            discovery_records,
            records,
            supported_discovery,
        )
        stable = {}
        for sig in supported_discovery:
            dmode = discovery["mechanism_modes"][sig]
            rmode = payload["mechanism_modes"].get(sig, {
                "count": 0,
                "unique_seed_count": 0,
                "prevalence_among_A_ONLY": 0.0,
                "supported": False,
            })
            rep_supported = bool(
                int(rmode["count"]) >= MODE_MIN_COUNT
                and int(rmode["unique_seed_count"]) >= MODE_MIN_SEEDS
                and float(rmode["prevalence_among_A_ONLY"]) >= MODE_MIN_PREVALENCE
            )
            delta = (
                float(rmode["prevalence_among_A_ONLY"])
                - float(dmode["prevalence_among_A_ONLY"])
            )
            ci = delta_ci[sig]
            is_stable = bool(
                rep_supported
                and abs(delta) <= STABILITY_ABS_DELTA_MAX
                and float(ci["ci_lower"]) <= 0.0 <= float(ci["ci_upper"])
            )
            stable[sig] = {
                "discovery_supported": True,
                "replication_supported": rep_supported,
                "discovery_prevalence": float(dmode["prevalence_among_A_ONLY"]),
                "replication_prevalence": float(rmode["prevalence_among_A_ONLY"]),
                "point_delta_rep_minus_disc": delta,
                "delta_bootstrap_95pct": ci,
                "stably_replicated": is_stable,
            }

        stable_count = sum(
            int(v["stably_replicated"]) for v in stable.values()
        )
        if stable_count >= 2:
            status = "PASS"
            verdict = "A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY"
        else:
            status = "NEGATIVE"
            verdict = "A_ONLY_FAILURE_MODE_HETEROGENEITY_NOT_REPLICATED"

    result = {
        "experiment": "KCL-6.5.9.4-REPLICATION",
        "status": status,
        "verdict": verdict,
        **payload,
        "discovery": {
            "path": str(discovery_path),
            "sha256": sha256_file(discovery_path),
            "source_git_commit": discovery.get("source_git_commit"),
            "supported_modes": discovery.get("discovery_supported_modes", []),
        },
        "replication_of_discovery_modes": stable,
        "stably_replicated_modes": [
            sig for sig, v in stable.items() if v.get("stably_replicated")
        ],
        "protocol_sha256": sha256_file(PROTOCOL),
        "script_sha256": sha256_file(SCRIPT),
        "source_git_commit": git_commit(),
        "environment": {
            "python": platform.python_version(),
        },
        "governance": {
            "classifier_trained": False,
            "controller_implemented": False,
            "protected_confirmatory_touched": False,
            "kcl7_started": False,
            "replication_executed_after_discovery_authorization": True,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("discovery", "replication"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--discovery",
        type=Path,
        default=Path("experiments/kernel_cl/results/kcl6594_discovery.json"),
    )
    args = parser.parse_args()

    if args.phase == "discovery":
        result = run_discovery(args.output)
    else:
        result = run_replication(args.discovery, args.output)

    print(json.dumps({
        "experiment": result.get("experiment"),
        "status": result.get("status"),
        "verdict": result.get("verdict"),
        "A_ONLY_support": result.get("A_ONLY_support"),
        "discovery_supported_modes": result.get("discovery_supported_modes"),
        "replication_authorized": result.get("replication_authorized"),
        "stably_replicated_modes": result.get("stably_replicated_modes"),
        "mechanism_modes": result.get("mechanism_modes"),
        "replication_of_discovery_modes": result.get("replication_of_discovery_modes"),
        "integrity": result.get("integrity"),
    }, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "NEGATIVE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
