"""
OIR-PPV v0.13.11 historical replay runner skeleton.

Loads frozen seed cases and compares versioned simulator outputs.
This file intentionally does not contain experiment results.
Results must be generated and committed separately.
"""

import json
from pathlib import Path


def load_failure_cases(root):
    return sorted(Path(root).glob("*.json"))


def run_case(case_file):
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    cases = load_failure_cases("../failure_cases")
    for case in cases:
        print(case.name)
