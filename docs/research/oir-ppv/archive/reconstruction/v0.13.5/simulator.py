"""OIR-PPV v0.13.5 simulator
Competing causal hypothesis stage.
"""
VERSION = "0.13.5"
FEATURES = ["hierarchy", "intervention", "confounder", "competing_hypothesis"]


def compare_hypotheses(hypotheses):
    return {"candidates": hypotheses, "evaluation": "causal_competition"}
