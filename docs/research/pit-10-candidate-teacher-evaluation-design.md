# PIT-10 — Candidate Teacher Evaluation Design

Status: Research Design

## Purpose

Define the execution design for evaluating PIT candidate teacher strategies under the frozen PIT-8 evaluation protocol.

PIT-10 does not select a teacher model, start training, or integrate any candidate into MindForge.

## Evaluation Approach

Candidate strategies are evaluated through controlled scenarios designed around personal intelligence requirements.

Evaluation must separate:

- general reasoning capability
- personal pattern understanding
- teaching signal quality
- uncertainty handling

## Scenario Categories

### Stable Preference

Measure whether a candidate can identify durable user patterns from repeated evidence.

### Preference Drift

Measure whether a candidate can detect changes instead of preserving outdated assumptions.

### Conflicting Evidence

Measure whether a candidate can resolve contradictory observations with evidence tracking.

### User Correction

Measure whether a candidate can update previous beliefs after explicit feedback.

### Rare Exception

Measure whether a candidate can preserve exceptions without incorrectly changing general patterns.

### Insufficient Evidence

Measure whether a candidate can abstain when confidence is low.

## Output Requirements

Each candidate evaluation should produce:

- capability profile
- strengths
- weaknesses
- failure modes
- teaching signal examples
- qualification verdict

## Qualification Verdicts

Possible outcomes:

- QUALIFIED
- QUALIFIED_WITH_LIMITS
- NOT_SUITABLE

## Constraints

No model selection.

No training.

No MindForge runtime changes.

No Kernel changes.

No TokenModel changes.

No PPF changes.

## Next Step

Apply PIT-10 design to candidate teacher strategy evaluation after review approval.
