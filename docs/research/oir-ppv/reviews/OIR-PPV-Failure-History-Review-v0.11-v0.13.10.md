# OIR-PPV Failure History Review v0.11 → v0.13.10

## Purpose

This review freezes the adversarial learning history before OIR-PPV Research Protocol v1.0. It records why the hypothesis changed after each failure.

## Frozen hypothesis

OIR-PPV studies whether a system can discover minimal generative invariants from experience, validate them causally, and preserve compact representations that explain existing observations and predict novel manifestations.

---

## Failure evolution

### v0.11 — Adversarial Reviewer Test

Failure: reward and frequency trap.

High-frequency and high-reward patterns were mistaken for important patterns.

Lesson:

`Popularity != Structural importance`

---

### v0.12 — Invariant Challenger + Exploration

Failure: useful patterns were confused with deep invariants.

Lesson: utility alone is insufficient. Structural depth is required.

---

### v0.13 — Invariant Hierarchy

Introduced structural ranking between surface, behavior, strategy and architecture-level patterns.

Lesson: invariant is not a pattern; it is a pattern with structural consequences.

---

### v0.13.1 — Blind Hierarchy Discovery

Removed explicit hierarchy labels.

Result: structural importance can be inferred from impact, reuse and dependencies.

---

### v0.13.2 — Dependency Graph Attack

Failure: dependency was confused with causality.

Lesson: correlation graphs are insufficient; intervention is required.

---

### v0.13.3 — True Intervention Validation

Improved causal validation but strong proxy variables survived.

Lesson: intervention alone does not eliminate hidden explanations.

---

### v0.13.4 — Confounder & Alternative Explanation Attack

Added hidden cause analysis.

Lesson: competing causal hypotheses are required.

---

### v0.13.5 — Competing Causal Hypothesis Test

Tested direct cause, confounder and downstream symptom explanations.

Lesson: causal does not automatically mean fundamental.

---

### v0.13.6 — Cross-Environment Invariance Test

Failure: statistical stability was not enough.

Lesson:

`Robust != Fundamental`

---

### v0.13.7 — Environment Intervention Stress Test

Added environment perturbation.

Lesson: implementation details must be separated from underlying principles.

---

### v0.13.8 — Minimal Generative Invariant Test

Major transition:

From:

"Which pattern survives?"

To:

"Which latent principle generates multiple successful manifestations?"

---

### v0.13.9 — Novel Manifestation Prediction

Invariant must explain the past and predict unseen manifestations.

---

### v0.13.10 — Hypothesis Generation & Self-Experiment

Closed the loop:

```
Observe
 -> Infer invariant
 -> Generate hypothesis
 -> Design experiment
 -> Update belief
```

---

# Frozen definitions

## Invariant

A minimal causal principle that survives environment changes, survives intervention, generates multiple manifestations and predicts unseen manifestations.

## Generator

The latent mechanism mapping an invariant into concrete implementations.

## Validation stack

1. Observation
2. Intervention
3. Counterfactual analysis
4. Cross-environment testing
5. Novel manifestation prediction
6. Self experiment

## Research status

SUPPORTED IN SIMULATION

NOT YET VALIDATED ON REAL DATA
