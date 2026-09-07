"""OIR-PPV v0.13.7 simulator
Environment intervention stress stage.
"""
VERSION = "0.13.7"
FEATURES = ["cross_environment", "environment_intervention"]


def stress_test(environment, intervention):
    return {"environment": environment, "intervention": intervention}
