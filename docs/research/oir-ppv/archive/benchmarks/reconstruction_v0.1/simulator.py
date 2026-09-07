"""
OIR-PPV v0.11 baseline simulator reconstruction.

Purpose:
Reconstruct the baseline failure mode before causal and invariant mechanisms.

Architecture:
- reward scoring
- frequency bias
- no hierarchy
- no intervention
- no generator discovery
"""

VERSION = "v0.11"
FEATURES = ["reward", "frequency"]


def select_pattern(patterns, budget=1):
    """Baseline selector intentionally optimized for local signals only."""
    scored = sorted(
        patterns,
        key=lambda p: p.get("reward", 0) * p.get("frequency", 0),
        reverse=True,
    )
    return scored[:budget]


def run(observations):
    return {
        "architecture": VERSION,
        "features": FEATURES,
        "selected": select_pattern(observations),
    }
