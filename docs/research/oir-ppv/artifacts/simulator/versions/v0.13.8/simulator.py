"""OIR-PPV v0.13.8 simulator
Minimal generative invariant stage.
"""
VERSION = "0.13.8"
FEATURES = ["environment_intervention", "minimal_generator_discovery"]


def discover_generator(manifestations):
    return {"manifestations": manifestations, "representation": "minimal_generator"}
