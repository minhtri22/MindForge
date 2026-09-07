# PIT-4 — Evaluation Protocol & Data Requirements

Status: RESEARCH DEFINITION

## Objective

Define how Personal Intelligence Teacher (PIT) should be evaluated before selecting models or implementing systems.

PIT success is not measured by memory size or retrieval accuracy alone. The primary question is:

> Does MindForge make better decisions because PIT exists?

## 1. Evaluation Principle

PIT is evaluated as a teaching system.

The evaluation target is improvement in downstream personal intelligence capability:

Experience → PIT → Teaching Signal → MindForge → Better future decision

## 2. What PIT Is Not Evaluated By

The following are insufficient alone:

- amount of stored memory
- retrieval precision only
- number of remembered facts
- language generation quality
- benchmark accuracy without personal context

These measure memory or general intelligence, not personal intelligence teaching.

## 3. PIT Evaluation Dimensions

### E1 — Pattern Discovery Quality

Question:

Can PIT discover meaningful user-specific patterns?

Measure:

- useful pattern discovery
- false pattern rate
- confidence calibration

### E2 — Teaching Signal Quality

Question:

Does PIT convert experience into useful learning signals?

Outputs:

- correction signals
- preference signals
- strategy suggestions
- uncertainty indicators

### E3 — Personal Decision Improvement

Question:

Does PIT improve future choices?

Primary metric:

future decision quality improvement compared with baseline without PIT.

### E4 — Adaptation Quality

Question:

Can PIT adapt when user behavior changes?

Measure:

- correction handling
- drift detection
- outdated preference removal

### E5 — Trust and Explainability

Question:

Can users understand why PIT produced a teaching signal?

Measure:

- evidence traceability
- confidence
- contradiction handling

## 4. Required Data Model

PIT requires more than chat history.

Minimum experience unit:

```
Experience
  timestamp
  context
  action
  outcome
  user feedback
  confidence
```

Derived layers:

```
Experience
    ↓
Evidence
    ↓
Pattern
    ↓
Reflection
    ↓
Teaching Signal
```

## 5. Required Data Categories

### Behavioral Data

Examples:

- repeated actions
- routines
- preferences

### Outcome Data

Examples:

- success/failure
- user correction
- satisfaction

### Context Data

Examples:

- time
- environment
- constraints

### Relationship Data

Examples:

- people
- projects
- long-term goals

## 6. Evaluation Protocol Concept

Future PIT experiments should compare:

Baseline:

General Intelligence Teacher only

versus:

General Intelligence Teacher + PIT

The experiment should measure whether PIT improves:

- personalization
- decision quality
- adaptation
- consistency

## 7. Data Generation Rules

Do not create synthetic personal truth without provenance.

Required principles:

- evidence first
- uncertainty preserved
- correction allowed
- deletion supported
- provenance recorded

## 8. Open Research Questions

1. How much personal data is required before PIT becomes useful?

2. What is the minimum representation needed for personal patterns?

3. How can teaching signals avoid reinforcing wrong beliefs?

4. How should personal improvement be measured objectively?

5. Does PIT require a dedicated model or can it emerge from orchestration?

## 9. Current Decision

PIT remains a research architecture, not a selected model.

Next step:

PIT-5 — Candidate System Design and Minimal Proof Experiment.

No model selection, training, or runtime integration is authorized yet.
