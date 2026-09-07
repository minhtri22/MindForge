"""OIR-PPV v0.13.6 simulator
Cross environment invariance stage.
"""
VERSION = "0.13.6"
FEATURES = ["causal_competition", "cross_environment_test"]


def transfer_score(invariant, environments):
    return {"invariant": invariant, "environments": environments}
