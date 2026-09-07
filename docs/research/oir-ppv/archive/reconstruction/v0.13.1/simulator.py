"""OIR-PPV v0.13.1 blind hierarchy simulator.

Frozen change from v0.13:
- removes explicit hierarchy labels
- estimates structural depth from observed properties
"""

VERSION = "0.13.1"
FEATURES = ["blind_hierarchy_discovery"]


def hierarchy_score(pattern):
    return (
        pattern.get("dependency_depth", 0) * 0.5
        + pattern.get("impact_scope", 0) * 0.5
    )


def select_pattern(patterns, budget=1):
    return sorted(patterns, key=hierarchy_score, reverse=True)[:budget]
