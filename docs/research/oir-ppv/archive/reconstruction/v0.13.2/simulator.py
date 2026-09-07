"""OIR-PPV v0.13.2 dependency graph attack simulator.

Frozen change from v0.13.1:
- models dependency relationships
- intentionally does not claim causality
"""

VERSION = "0.13.2"
FEATURES = ["dependency_graph"]


def dependency_score(pattern):
    return pattern.get("dependency_centrality", 0)


def select_pattern(patterns, budget=1):
    return sorted(patterns, key=dependency_score, reverse=True)[:budget]
