# PIT-2 Teacher Evaluation Protocol

## Status

PLANNING

## Purpose

Define how Personal Intelligence Teacher candidates should be evaluated before any model selection, training, or integration decision.

PIT-2 does not select a final teacher model.

PIT-2 defines the evaluation framework.

## Research Question

What properties make a model suitable as a Personal Intelligence Teacher?

A strong general LLM capability score is not sufficient.

The evaluation must measure whether a teacher can provide useful supervision for personal intelligence learning.

## Teacher Categories

### General Intelligence Teacher (GIT)

Examples:

- Qwen
- GPT
- Claude

Expected strengths:

- language capability
- reasoning
- coding
- world knowledge
- general assistant behavior

### Personal Intelligence Teacher (PIT Candidate)

Expected strengths:

- observing user patterns
- identifying stable preferences
- separating signal from noise
- detecting changes over time
- correcting wrong assumptions
- expressing uncertainty
- producing useful supervision signals

## Evaluation Dimensions

### T1 — Pattern Understanding

Can the teacher identify meaningful personal patterns from observations?

Measure:

- pattern extraction
- relevance
- stability

### T2 — Temporal Reasoning

Can the teacher reason about changes over time?

Measure:

- trend detection
- drift awareness
- historical context usage

### T3 — Correction Capability

Can the teacher update beliefs when new evidence contradicts previous assumptions?

Measure:

- correction quality
- resistance to false persistence

### T4 — Uncertainty Handling

Can the teacher distinguish known, unknown, and uncertain information?

Measure:

- confidence calibration
- abstention quality

### T5 — Supervision Quality

Can the teacher generate useful learning signals for MindForge?

Measure:

- actionability
- consistency
- noise level

### T6 — Personalization Safety

Can the teacher avoid harmful assumptions about the user?

Measure:

- over-personalization
- hallucinated preferences
- privacy boundaries

## Evaluation Protocol Principles

1. No teacher is accepted based on parameter count.
2. No teacher is accepted based only on general benchmark scores.
3. Teacher evaluation must separate capability from integration.
4. PIT evaluation must preserve PPF as the personal pattern representation layer.
5. MindForge runtime must remain unchanged during evaluation.

## Candidate Evaluation Output

Each candidate should produce:

- capability profile
- strengths
- weaknesses
- failure modes
- suitability verdict

Possible verdicts:

- QUALIFIED
- QUALIFIED_WITH_LIMITS
- NOT_SUITABLE

## Non Goals

PIT-2 will NOT:

- train models
- modify MindForge kernel
- modify TokenModel
- replace PPF
- choose final architecture

## Future Phases

PIT-3:

Candidate model evaluation

PIT-4:

Teacher supervision feasibility

PIT-5:

Distillation/integration research
