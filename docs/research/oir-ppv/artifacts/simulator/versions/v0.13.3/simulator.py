"""OIR-PPV v0.13.3 true intervention simulator.

Frozen change:
- adds intervention impact evaluation
- still lacks full competing hypothesis search
"""

VERSION = "0.13.3"
FEATURES = ["intervention_validation"]


def intervention_score(pattern):
    return pattern.get("intervention_effect", 0)


def select_pattern(patterns, budget=1):
    return sorted(patterns, key=intervention_score, reverse=True)[:budget]
