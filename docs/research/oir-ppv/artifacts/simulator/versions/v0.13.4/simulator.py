"""OIR-PPV v0.13.4 simulator
Confounder and alternative explanation validation stage.
"""
VERSION = "0.13.4"
FEATURES = ["hierarchy", "dependency", "intervention", "confounder_attack"]


def evaluate(pattern):
    return {
        "pattern": pattern,
        "checks": ["intervention", "confounder_rejection"],
    }
