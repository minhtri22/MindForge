# PIT-1 — Personal Intelligence Teacher Requirements

## Status

DEFINED

## Purpose

Define the minimum capability requirements for a Personal Intelligence Teacher (PIT) before selecting models, running benchmarks, or starting training.

This document is a requirements specification only.

No teacher model is selected.
No benchmark is defined.
No training is started.

---

## Research Question

What capabilities must a teacher possess in order to provide useful supervision for a Personal Intelligence model?

---

## Core Principle

General Intelligence Teacher != Personal Intelligence Teacher

A model that is strong at language, reasoning, coding, and world knowledge is not automatically suitable for learning personal identity, preferences, routines, or behavioral patterns.

---

# PIT Capability Requirements

## PIT-R1 — Personal Observation Understanding

The teacher must understand personal observations as structured events rather than simple text facts.

Required concepts:

- event
- context
- time
- source
- confidence
- missing observation
- observed non-occurrence

The teacher must distinguish:

NO_OBSERVATION

from:

OBSERVABLE_NON_OCCURRENCE

---

## PIT-R2 — Pattern Discovery

The teacher must identify candidate personal patterns from repeated evidence.

Required reasoning:

observation

-> candidate pattern

-> evidence evaluation

-> confidence update

The teacher must avoid promoting isolated events into stable personal traits.

---

## PIT-R3 — Temporal Reasoning

The teacher must understand that personal patterns evolve over time.

Required capabilities:

- preference emergence
- preference change
- routine drift
- stale patterns
- historical context

Example:

Previous preference != current preference

without treating the history as contradictory data.

---

## PIT-R4 — Correction Learning

The teacher must correctly incorporate user correction.

Example:

System inference:

"User likes running."

User correction:

"I only ran last month because of a challenge."

Expected:

reduce confidence

record correction evidence

avoid repeating the previous assumption.

---

## PIT-R5 — Uncertainty and Abstention

The teacher must know when evidence is insufficient.

Required behavior:

- do not invent personality traits
- preserve uncertainty
- request clarification when needed
- distinguish unknown from false

Expected output states may include:

- supported
- insufficient
- conflicting
- stale
- unknown
- deleted

---

## PIT-R6 — Contextual Personal Reasoning

The teacher must reason about relationships between:

- person
- activity
- environment
- time
- goal
- outcome

A personal pattern is not only frequency.

It is context-conditioned behavior.

---

## PIT-R7 — Supervision Quality

The teacher output must be useful for training or guiding a smaller Personal Intelligence model.

Required properties:

- consistent labels
- explainable evidence
- uncertainty preservation
- correction awareness
- reproducibility

---

# Non-Requirements

PIT does NOT require:

- world knowledge dominance
- maximum parameter count
- general chatbot capability
- autonomous agent behavior
- plugin architecture
- replacement of PPF

---

# Relationship With Existing Research

## MKS

MKS defines model/kernel separation.

PIT must not modify kernel architecture.

## PPF

PPF defines personal pattern representation.

PIT provides potential supervision sources for PPF-compatible learning.

## Track-A

Track-A evaluated general LLM suitability.

Its result motivates teacher separation.

---

# Future Decisions

PIT-2:

Define evaluation protocol for teacher capability.

PIT-3:

Evaluate candidate teacher families.

PIT-4:

Study distillation feasibility.

---

# Current Decision

PIT is a research track for discovering the correct supervision source for Personal Intelligence.

No teacher model has been selected.
