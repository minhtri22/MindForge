# PIT-5 — Minimal Proof Experiment Design

## Status

Research design only.

No implementation.
No model training.
No benchmark execution.

## Research Question

Can a Personal Intelligence Teacher (PIT) generate useful teaching signals that improve future user-specific decisions?

PIT success is not measured by memory size or retrieval accuracy. It is measured by whether MindForge makes better future decisions with PIT-derived signals.

## Core Hypothesis

General Teacher + PPF + PIT teaching signals should improve personal decision quality compared with:

1. General Teacher only.
2. General Teacher + memory retrieval.
3. General Teacher + PPF only.

## Minimal PIT Loop

Experience -> Evidence -> Pattern Discovery -> Reflection -> Teaching Signal -> Future Decision Evaluation

## Experiment Unit

A decision case contains:

- context
- available choices
- historical evidence
- PIT signal
- selected action
- outcome
- human judgement

## Baselines

### Baseline 0
General Intelligence Teacher only.

### Baseline 1
General Intelligence Teacher + memory retrieval.

### Baseline 2
General Intelligence Teacher + PPF representation.

### Candidate
General Intelligence Teacher + PPF + PIT reflection and teaching signal.

## PIT Output Contract

PIT produces a teaching signal, not a final answer.

Minimum fields:

- context
- observed_pattern
- evidence
- confidence
- recommendation
- uncertainty
- expected_effect

## Evaluation Metrics

- Decision improvement
- Pattern accuracy
- Teaching signal usefulness
- Confidence calibration
- Adaptation after correction

## Failure Criteria

PIT fails if:

- memory retrieval provides the same benefit without PIT
- discovered patterns are unreliable
- teaching signals do not affect decisions
- PIT reinforces incorrect assumptions

## Data Requirements

Initial proof requires controlled experience cases, not raw chat history.

Experience record:

- context
- action
- outcome
- correction
- confidence

## Implementation Strategy

Phase 0: synthetic controlled cases.

Phase 1: human-reviewed personal cases.

Phase 2: real interaction evaluation.

## Model Strategy

PIT-5 does not select a model.

Candidate approaches remain open:

- Frontier LLM + PPF
- Dedicated small PIT model
- Hybrid PIT model + General Teacher

## Next Step

PIT-6 should implement a minimal simulator to validate the protocol before selecting models or training.
