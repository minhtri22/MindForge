"""OIR-PPV v0.12 simulator.

Adds exploration/uncertainty awareness over v0.11.
Still lacks:
- hierarchy
- causal validation
- generator discovery
"""

VERSION = "0.12"
FEATURES = ["reward", "frequency", "exploration"]


def select_pattern(patterns, budget=1):
    def score(p):
        return (
            p.get("reward", 0)
            + p.get("frequency", 0)
            + p.get("uncertainty_bonus", 0)
        )

    return sorted(patterns, key=score, reverse=True)[:budget]
