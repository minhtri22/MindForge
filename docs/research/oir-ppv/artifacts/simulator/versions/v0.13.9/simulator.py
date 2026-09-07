"""OIR-PPV v0.13.9 simulator
Novel manifestation prediction stage.
"""
VERSION = "0.13.9"
FEATURES = ["minimal_generator", "novel_manifestation_prediction"]


def predict(generator, unseen_context):
    return {"generator": generator, "prediction_context": unseen_context}
