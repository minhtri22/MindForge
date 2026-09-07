# OIR-PPV Failure History Review v0.11 → v0.13.10

## Purpose

This document freezes the adversarial review history before OIR-PPV Research Protocol v1.0.
The objective is not to prove the hypothesis, but to document why the hypothesis survived or failed each challenge.

## Frozen Research Hypothesis

OIR-PPV investigates whether a system can discover **minimal generative invariants** from experience:

- remove surface manifestations,
- identify causal principles,
- compress multiple solutions into a generator,
- predict unseen manifestations,
- validate through experiments.

---

# Failure Evolution

## v0.11 — Adversarial Reviewer Test

Failure:

High-frequency and high-reward patterns were selected over rare structural invariants.

Lesson:

`frequency != importance`

`reward != structural value`

Required change:
Introduce hierarchy and long-horizon evaluation.

---

## v0.12 — Invariant Challenger + Exploration

Failure:

The system could find rare candidates but could not distinguish deep invariants from useful shallow patterns.

Lesson:

Utility alone is insufficient.
Structural depth matters.

---

## v0.13 — Invariant Hierarchy

Success:

Patterns could be separated into structural levels:

- surface
- behavior
- strategy
- architecture

Lesson:

Invariant is not just a frequent pattern; it has structural consequence.

---

## v0.13.1 — Blind Hierarchy Discovery

Question:

Was hierarchy only an oracle label?

Result:

The system could infer hierarchy from impact, dependency and transfer signals.

Lesson:

Hierarchy must be discovered, not assigned.

---

## v0.13.2 — Dependency Graph Attack

Failure:

Dependency was confused with causality.

Lesson:

Correlation graphs are insufficient.
Intervention is required.

---

## v0.13.3 — True Intervention Validation

Partial success:

Simple correlations were rejected.

Remaining issue:
Strong proxies could survive intervention.

Lesson:

A single intervention is insufficient.
Alternative explanations are required.

---

## v0.13.4 — Confounder & Alternative Explanation Attack

Partial success:

Simple hidden causes were handled.

Remaining issue:
Multiple competing causal explanations remained.

---

## v0.13.5 — Competing Causal Hypothesis Test

Improvement:

Added competing explanations:

- direct cause
- hidden confounder
- downstream symptom

Remaining issue:
Causal does not automatically mean invariant.

---

## v0.13.6 — Cross-Environment Invariance Test

Failure:

Some patterns remained stable statistically but were not fundamental principles.

Lesson:

`stable != invariant`

---

## v0.13.7 — Environment Intervention Stress Test

Improvement:

Environment changes and mechanism perturbations removed many implementation-specific patterns.

Remaining issue:
Need to identify the minimal principle behind multiple implementations.

---

## v0.13.8 — Minimal Generative Invariant Test

Breakthrough:

Shift from selecting surviving patterns to discovering latent generators.

Invariant became:

> A minimal causal principle capable of generating multiple successful manifestations.

---

## v0.13.9 — Novel Manifestation Prediction Test

Validation:

A discovered invariant must explain existing observations and predict unseen manifestations.

Criterion:

`explain past + predict future`

---

## v0.13.10 — Hypothesis Generation & Self Experiment

Final capability added:

Observe → infer invariant → generate hypothesis → experiment → update.

This closes the invariant core loop.

---

# Final Research Definition

## Invariant

A minimal causal principle that:

- survives environment changes,
- remains valid under intervention,
- generates multiple manifestations,
- predicts unseen outcomes.

## Generator

The mechanism that maps an invariant into concrete implementations.

## Validation

Validation stack:

1. Observation
2. Intervention
3. Counterfactual reasoning
4. Cross-environment testing
5. Novel manifestation prediction
6. Experiment

## Current Status

OIR-PPV is:

`SUPPORTED IN SIMULATION`

It is not yet validated on real-world datasets.
