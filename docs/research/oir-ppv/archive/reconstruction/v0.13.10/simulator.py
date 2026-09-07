"""OIR-PPV v0.13.10 treatment simulator.

Frozen treatment architecture:
- causal persistence
- generative value
- hypothesis validation

This file is intentionally separate from earlier versions.
"""

VERSION = "0.13.10"
FEATURES = [
    "causal_validation",
    "cross_environment_stability",
    "minimal_generative_invariant",
    "novel_manifestation_prediction",
    "self_experiment",
]


def invariant_score(pattern):
    return (
        pattern.get("causal", 0) * 0.35
        + pattern.get("transfer", 0) * 0.25
        + pattern.get("generation", 0) * 0.25
        + pattern.get("stability", 0) * 0.15
    )


def select_pattern(patterns, budget=1):
    return sorted(patterns, key=invariant_score, reverse=True)[:budget]
