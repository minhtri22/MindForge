"""
OIR-PPV v0.11 baseline simulator scaffold.

Purpose:
Replay reconstructed failure scenarios.
This intentionally represents the weaker architecture:
- reward/frequency driven selection
- no causal intervention
- no generative invariant compression

This file is part of the reproducibility artifact.
"""

from dataclasses import dataclass


@dataclass
class Pattern:
    name: str
    reward: float
    frequency: float
    causal_depth: float


def select_pattern(patterns):
    """Baseline v0.11 selection rule."""
    return max(patterns, key=lambda p: p.reward * 0.7 + p.frequency * 0.3)


def run(seed_case):
    return {
        "architecture": "v0.11",
        "seed_case": seed_case,
        "selection_rule": "reward_frequency",
    }
