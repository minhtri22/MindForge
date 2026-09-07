"""
OIR-PPV v0.13.11 Historical Failure Replay Runner

Purpose:
- Execute frozen failure cases against frozen simulator versions.
- Preserve provenance: same seed, same failure case, explicit simulator version.
- Produce raw execution records only.

This runner intentionally does not decide PASS/FAIL.
Analysis happens after raw outputs are committed.
"""

import json
from pathlib import Path


REPLAY_ROOT = Path(__file__).resolve().parents[2]


def load_failure_cases(folder):
    return sorted(Path(folder).glob("*.json"))


def load_case(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_execution_record(simulator_version, case):
    return {
        "simulator_version": simulator_version,
        "failure_case": case["id"],
        "seed": case["seed"],
        "attack": case["attack"]["type"],
        "execution_status": "NOT_RUN",
        "result": None,
    }


if __name__ == "__main__":
    print("OIR-PPV historical replay runner")
    print("Frozen cases must be executed with explicitly selected simulator versions.")
