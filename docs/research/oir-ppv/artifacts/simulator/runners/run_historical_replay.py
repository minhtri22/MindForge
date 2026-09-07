"""
OIR-PPV v0.13.11 Historical Failure Replay Runner

Purpose:
- Execute frozen failure cases against frozen simulator versions.
- Preserve provenance: same seed, same failure case, explicit simulator version.
- Produce raw execution records only.

This runner intentionally does not decide PASS/FAIL.
Analysis happens after raw outputs are committed.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CASE_REGISTRY = Path("docs/research/oir-ppv/artifacts/cases")


def resolve_case(case_id):
    """Resolve stable case id into a version-controlled case artifact."""
    path = CASE_REGISTRY / f"{case_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Unknown failure case: {case_id}. Expected artifact: {path}"
        )
    return path


def load_case(case_id):
    path = resolve_case(case_id)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_execution_record(simulator_version, case):
    return {
        "experiment_id": "OIR-PPV-v0.13.11",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "simulator_version": simulator_version,
        "failure_case": case["id"],
        "seed": case["seed"],
        "attack": case["attack"]["type"],
        "execution_status": "RAW_EXECUTION_PENDING",
        "metrics": {},
        "raw_trace": []
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--simulator-version", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    case = load_case(args.case)
    record = create_execution_record(args.simulator_version, case)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
