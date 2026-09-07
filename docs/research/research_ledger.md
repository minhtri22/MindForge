# Research Ledger

Append-only research milestones.

## PIT-6.1 Completion

Date: 2026-09-07

Milestone: PIT-6.1 — Adversarial Personal Pattern Simulator

Status: Completed

Summary:

Extended PIT simulator from simple repeated preference scenarios into adversarial personal intelligence scenarios.

Evidence:

Dataset: 150 cases

Seed: 42

Scenario coverage:

- Preference drift
- Conflicting evidence
- Rare exception
- User correction
- Insufficient evidence

Compared systems:

- Context only
- Memory retrieval only
- PIT teaching signal pipeline

Results:

Context only: 0.0

Memory retrieval: 0.6

PIT: 1.0

Decision improvement: 0.4

Interpretation:

PIT-6.1 demonstrates that a teaching signal can improve decisions in a controlled synthetic adversarial environment.

This validates the experimental direction.

This does not prove final PIT architecture, teacher model choice, production applicability, or MindForge integration strategy.

Key finding:

PIT value appears when reasoning over evolving preferences, contradictory evidence, conditional behavior, exceptions, and corrections.

Decision:

Proceed to next PIT research phase. Do not select model yet. Do not train yet.

Scope boundary:

No model downloaded. No training. No runtime changes. No PPF changes.


## PIT-7 Start / Completion

Date: 2026-09-07

Milestone: PIT-7 — Teacher Strategy Selection

Status: Completed

Summary:

Defined the PIT teacher strategy space before selecting any implementation candidate.

Analyzed candidate strategies:

- Memory-centric strategy
- Reflection-centric strategy
- Hybrid teacher strategy

Key finding:

PIT should be treated as a teaching capability and strategy layer, not as a single model choice.

Evaluation criteria defined:

- Decision improvement
- Pattern quality
- Correction recovery
- Drift handling
- Uncertainty calibration
- Evidence traceability

Decision:

Do not select a teacher model yet.
Proceed to teacher strategy evaluation protocol.

Scope boundary:

No model selection. No model download. No training. No runtime integration.
