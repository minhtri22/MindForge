"""OIR-PPV v0.13 simulator.

Frozen transition:
- introduces structural hierarchy
- separates surface patterns from deeper patterns
- does not include causal intervention
"""

VERSION = "0.13"
FEATURES = [
    "pattern_hierarchy",
    "structural_depth",
]


def hierarchy_score(pattern):
    return pattern.get("depth", 0)


def select_pattern(patterns, budget=1):
    return sorted(patterns, key=hierarchy_score, reverse=True)[:budget]
