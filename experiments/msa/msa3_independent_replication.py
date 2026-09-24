"""MSA-3 independent fresh replication.

This wrapper deliberately reuses the exact frozen MSA-1 measurement and
classification implementation. MSA-3 changes only the fresh cohort and adds a
predeclared replication-success decision around the unchanged MSA-1 verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import torch

from experiments.msa import msa1_endpoint_adequacy as m1

PROGRAM = "MSA-3"
DISCOVERY_VERDICT = "ACCURACY_COARSE_LOSS_INFORMATIVE"
PROTOCOL = Path("docs/research/measurement-substrate-adequacy/msa3-independent-replication-protocol.md")
EXECUTION_LOCK = Path("docs/research/measurement-substrate-adequacy/MSA3_EXECUTION_LOCK.json")
LOCK_VERIFICATION = Path("docs/research/measurement-substrate-adequacy/MSA3_EXECUTION_LOCK_VERIFICATION.md")
DEFAULT_RECORDS = Path("experiments/msa/results/msa3_fresh_endpoints.json")
DEFAULT_FORMAL = Path("experiments/msa/results/MSA3_FORMAL_RESULT.json")

FRESH_SEEDS = (
    4632344,3715332,4702401,8249890,7222878,8766965,
    8186980,3421287,7823696,7361523,5782374,3461192,
    8672287,7946731,8039551,5898726,5530516,7304549,
    4574050,2777688,6487687,2073202,2493669,6069173,
    5380311,6749456,7186523,2822907,8679347,4723573,
    5594742,4730662,5957069,5391391,6804821,4925724,
    4489402,2373972,3373481,8495716,7878724,7620252,
    4567757,6965735,8480204,3484189,2610959,8358070,
    4332215,7468926,2250351,5806588,2693511,3617592,
    4267044,2041109,3209463,3238873,7635919,5232304,
    3408254,5059373,4701506,6837399,4842603,6283077,
    6348697,6445575,8003159,5921802,6552527,7406131,
)
SEED_MANIFEST_SHA256 = "5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8"
SEED_GENERATION_PHRASE = "MindForge|MSA-3|independent-fresh-replication|v1"
RELIABILITY_SEEDS = FRESH_SEEDS[:6]

SPENT_MSA1_SEEDS = tuple(m1.FRESH_SEEDS)
EXPECTED_SEEDS = 72
EXPECTED_BOUNDARIES = 216
EXPECTED_PER_STAGE = 72
EXPECTED_ENDPOINT_PAIRS = 648
HISTORICAL_PROBE_SEED = 9595


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_manifest_sha256(values=FRESH_SEEDS) -> str:
    return hashlib.sha256(",".join(str(int(x)) for x in values).encode()).hexdigest()


def regenerate_seeds() -> tuple[int, ...]:
    accepted = []
    seen = set()
    i = 0
    while len(accepted) < EXPECTED_SEEDS:
        digest = hashlib.sha256(f"{SEED_GENERATION_PHRASE}|{i}".encode()).digest()
        candidate = 2_000_000 + (int.from_bytes(digest[:8], "big") % 7_000_000)
        if candidate not in seen:
            accepted.append(candidate)
            seen.add(candidate)
        i += 1
    return tuple(accepted)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _historical_seed_candidates() -> set[int]:
    paths = [Path("Lineage.md")]
    for base in (
        Path("docs/research/kernel-continual-learning"),
        Path("experiments/kernel_cl"),
        Path("docs/research/adaptive-continual-outcomes"),
        Path("docs/research/continual-policy-response"),
        Path("docs/research/measurement-substrate-adequacy"),
        Path("experiments/msa"),
    ):
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file())
    out = set()
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


def validate_seed_manifest() -> dict[str, Any]:
    fresh = set(FRESH_SEEDS)
    historical = _historical_seed_candidates() - fresh
    checks = {
        "count_72": len(FRESH_SEEDS) == EXPECTED_SEEDS,
        "unique_72": len(fresh) == EXPECTED_SEEDS,
        "manifest_hash": seed_manifest_sha256() == SEED_MANIFEST_SHA256,
        "deterministic_regeneration": regenerate_seeds() == FRESH_SEEDS,
        "historical_disjoint": fresh.isdisjoint(historical),
        "protected_disjoint": fresh.isdisjoint(set(m1.PROTECTED_KCL_SEEDS)),
        "aco_spent_disjoint": fresh.isdisjoint(set(m1.SPENT_ACO_SEEDS)),
        "cprm_spent_disjoint": fresh.isdisjoint(set(m1.SPENT_CPRM_SEEDS)),
        "msa1_spent_disjoint": fresh.isdisjoint(set(SPENT_MSA1_SEEDS)),
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "historical_collisions": sorted(fresh & historical),
        "protected_collisions": sorted(fresh & set(m1.PROTECTED_KCL_SEEDS)),
        "aco_spent_collisions": sorted(fresh & set(m1.SPENT_ACO_SEEDS)),
        "cprm_spent_collisions": sorted(fresh & set(m1.SPENT_CPRM_SEEDS)),
        "msa1_spent_collisions": sorted(fresh & set(SPENT_MSA1_SEEDS)),
        "manifest_sha256": seed_manifest_sha256(),
    }


def execution_authorized() -> bool:
    if not EXECUTION_LOCK.exists() or not LOCK_VERIFICATION.exists():
        return False
    text = LOCK_VERIFICATION.read_text(encoding="utf-8")
    return (
        "MSA3_EXECUTION_LOCK_VERIFICATION_PASS" in text
        and sha256_file(EXECUTION_LOCK) in text
    )


def preflight() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    seeds = validate_seed_manifest()
    substrate = m1.frozen_substrate_snapshot()

    first = m1.build_endpoint_records(HISTORICAL_PROBE_SEED)
    second = m1.build_endpoint_records(HISTORICAL_PROBE_SEED)
    repeat = m1.compare_repeat(first, second)
    probe_ok = (
        len(first) == 3
        and all(m1._row_valid(r) for r in first)
        and repeat["exact"]
        and HISTORICAL_PROBE_SEED not in set(FRESH_SEEDS)
    )

    lock_exists = EXECUTION_LOCK.exists()
    checks = {
        "seed_manifest_valid": seeds["valid"],
        "substrate_exact": substrate["valid"],
        "historical_probe_integrity_repeat": probe_ok,
        "fresh_records_absent": not DEFAULT_RECORDS.exists(),
        "formal_result_absent": not DEFAULT_FORMAL.exists(),
        "independent_verification_absent": not LOCK_VERIFICATION.exists(),
        "fresh_execution_blocked": not execution_authorized(),
        "execution_lock_exists": lock_exists,
    }

    if lock_exists:
        lock = json.loads(EXECUTION_LOCK.read_text(encoding="utf-8"))
        checks["lock_program_exact"] = lock.get("program") == PROGRAM
        checks["lock_seed_hash_exact"] = (
            lock.get("seed_manifest", {}).get("sha256") == SEED_MANIFEST_SHA256
        )
        checks["lock_protocol_blob_exact"] = (
            lock.get("protocol", {}).get("git_blob_sha")
            == git("hash-object", str(PROTOCOL))
        )
        checks["lock_wrapper_blob_exact"] = (
            lock.get("implementation", {}).get("wrapper_git_blob_sha")
            == git("hash-object", str(Path(__file__)))
        )

    ok = all(checks.values())
    return {
        "schema": "MSA3-ZERO-SCIENCE-PREFLIGHT-v1",
        "program": PROGRAM,
        "status": "PASS" if ok else "FAIL",
        "verdict": "MSA3_ZERO_SCIENCE_PREFLIGHT_PASS" if ok else "MSA3_ZERO_SCIENCE_PREFLIGHT_FAIL",
        "git_commit": git("rev-parse", "HEAD"),
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest": seeds,
        "substrate": substrate,
        "historical_probe": {
            "seed": HISTORICAL_PROBE_SEED,
            "repeat": repeat,
            "fresh_seed_used": HISTORICAL_PROBE_SEED in set(FRESH_SEEDS),
        },
        "checks": checks,
        "fresh_seed_execution_attempted": False,
        "scientific_outcome_generated": False,
        "difficulty_mutation_performed": False,
        "predictor_fitting_performed": False,
    }


def collect_fresh() -> dict[str, Any]:
    if not execution_authorized():
        raise RuntimeError("MSA-3 fresh execution is not independently authorized")
    seeds = validate_seed_manifest()
    substrate = m1.frozen_substrate_snapshot()
    if not seeds["valid"] or not substrate["valid"]:
        raise RuntimeError("MSA-3 frozen identity invalid")

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    records = []
    reliability = []
    for seed in FRESH_SEEDS:
        first = m1.build_endpoint_records(seed)
        records.extend(first)
        if seed in RELIABILITY_SEEDS:
            second = m1.build_endpoint_records(seed)
            reliability.append({"seed": seed, **m1.compare_repeat(first, second)})

    return {
        "schema": "MSA3-FRESH-COLLECTION-v1",
        "program": PROGRAM,
        "protocol_sha256": sha256_file(PROTOCOL),
        "seed_manifest_sha256": seed_manifest_sha256(),
        "records": records,
        "reliability_checks": reliability,
    }


def adjudicate_replication(records, reliability_checks) -> dict[str, Any]:
    underlying = m1.adjudicate_records(
        records,
        reliability_checks,
        expected_seeds=FRESH_SEEDS,
    )
    confirmed = underlying["verdict"] == DISCOVERY_VERDICT
    return {
        "underlying_msa1_classifier": underlying,
        "replication_status": (
            "REPLICATION_CONFIRMED"
            if confirmed else
            "REPLICATION_NOT_CONFIRMED"
        ),
        "replication_confirmed": confirmed,
        "discovery_verdict": DISCOVERY_VERDICT,
        "observed_verdict": underlying["verdict"],
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
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
        p.error("--input required")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    result = adjudicate_replication(raw["records"], raw["reliability_checks"])
    _write(args.output, {
        "schema": "MSA3-FORMAL-RESULT-v1",
        "program": PROGRAM,
        "protocol_sha256": sha256_file(PROTOCOL),
        "source_records_sha256": sha256_file(args.input),
        "adjudication": result,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
