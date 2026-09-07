# PIT-7 — Teacher Strategy Selection

Status: Research Planning

## Purpose

Define the evaluation framework for selecting a future PIT teacher strategy after PIT-6.1 validation.

PIT-6.1 showed that teaching signals can improve decisions in a controlled synthetic adversarial environment. This does not select a final teacher architecture, model, or implementation approach.

## Current Research Position

Completed:

- PIT-1 Teacher Requirements
- PIT-2 Literature and Repository Qualification
- PIT-3 Candidate Architecture and Teacher Strategy
- PIT-4 Evaluation Protocol and Data Requirements
- PIT-5 Minimal Proof Experiment Design
- PIT-6 Minimal PIT Simulator
- PIT-6.1 Adversarial Personal Pattern Simulator

## Candidate Strategies Under Review

### Memory-Centric Strategy

Experience history -> pattern extraction -> teaching signal

Focus:

- grounded personal patterns
- explainability
- evidence tracking

### Reflection-Centric Strategy

Experience -> reflection -> hypothesis -> evaluation -> teaching signal

Focus:

- learning from outcomes
- strategy evolution
- correction handling

### Hybrid Strategy

Memory grounding combined with reflection and evaluation.

Focus:

- personal pattern discovery
- uncertainty handling
- future decision improvement

## PIT-7 Scope

Evaluate teacher strategies using:

- decision improvement
- pattern quality
- correction recovery
- drift handling
- uncertainty calibration
- evidence traceability

## Constraints

No model selection.

No training.

No MindForge integration.

No runtime changes.

## Next Step

Design the PIT teacher strategy evaluation protocol before selecting any implementation candidate.
