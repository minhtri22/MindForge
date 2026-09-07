"""OIR-PPV v0.11 baseline simulator.

Frozen baseline:
- ranks patterns using reward and frequency only
- intentionally lacks causal validation
"""

VERSION = "0.11"
FEATURES = ["reward", "frequency"]


def select_pattern(patterns, budget=1):
    scored = sorted(
        patterns,
        key=lambda p: p.get("reward", 0) * p.get("frequency", 0),
        reverse=True,
    )
    return scored[:budget]
