# PIT-8 — Teacher Strategy Evaluation Protocol

Status: Research Protocol

## Purpose

Define the evaluation protocol for comparing PIT teacher strategies before selecting a model, training approach, or implementation path.

PIT-6.1 validated the experimental direction with adversarial synthetic scenarios. It did not select a teacher architecture.

## Research Question

Which PIT strategy can produce reliable teaching signals that improve future decisions while preserving evidence, uncertainty, and correction handling?

## Strategies Under Evaluation

### Memory-Centric

Experience history -> pattern extraction -> teaching signal

Evaluation focus:

- evidence grounding
- stable pattern discovery
- traceability

### Reflection-Centric

Experience -> reflection -> hypothesis -> evaluation -> teaching signal

Evaluation focus:

- outcome learning
- strategy evolution
- correction recovery

### Hybrid

Memory grounding combined with reflection and evaluation.

Evaluation focus:

- temporal reasoning
- conditional preferences
- uncertainty handling

## Evaluation Dimensions

### Pattern Understanding

Can the strategy identify meaningful personal patterns from experience?

### Temporal Reasoning

Can the strategy detect preference changes and avoid stale assumptions?

### Contradiction Handling

Can the strategy represent conditional behavior when evidence conflicts?

### Correction Recovery

Can the strategy update beliefs after explicit user correction?

### Uncertainty Management

Can the strategy abstain when evidence is insufficient?

### Teaching Signal Quality

Can the generated signal improve future decisions without introducing unsupported assumptions?

## Evaluation Metrics

- decision improvement
- pattern precision
- false pattern rate
- drift detection accuracy
- correction recovery
- abstention accuracy
- confidence calibration
- evidence traceability

## Evaluation Rules

- No model is selected by this protocol alone.
- No training is performed during evaluation.
- No MindForge runtime changes are allowed.
- PPF remains the personal pattern representation boundary.

## Output

Each evaluated strategy should produce:

- capability profile
- strengths
- weaknesses
- failure modes
- suitability assessment

Possible outcomes:

- preferred research direction
- qualified with limitations
- not suitable

## Scope Boundary

No model downloaded.

No training.

No production integration.

No kernel, TokenModel, or PPF changes.
