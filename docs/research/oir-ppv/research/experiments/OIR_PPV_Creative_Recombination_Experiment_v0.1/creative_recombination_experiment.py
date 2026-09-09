# OIR-PPV Creative Recombination Experiment v0.1

def invariant_generation(experience, context):
    # Extract latent function from experience
    invariant = experience["latent_function"]
    # Recombine with unseen context
    return {"manifestation": invariant + "_" + context}

def baseline_memory(experience, context):
    # Surface memorization only
    return experience["surface_form"]
