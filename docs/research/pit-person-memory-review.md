# Repository Review

## Identity

Repository: Hubujiu/person-memory

Paper: Not identified from repository README.

Purpose: Local-first evidence-grounded memory for agents.

## Research Question

How can an agent remember a person while preserving evidence, uncertainty, and change over time?

## Architecture Overview

Input

User messages and evidence records

↓

Processing

Conservative extraction into structured memories

↓

Memory / Representation

Local SQLite records containing source evidence, confidence, importance, and history

↓

Output

Targeted recall of relevant personal context

## PIT Capability Mapping

| Capability | Assessment |
|---|---|
| PIT-R1 Personal Observation | STRONG |
| PIT-R2 Pattern Discovery | PARTIAL |
| PIT-R3 Temporal Reasoning | PARTIAL |
| PIT-R4 Correction Learning | PARTIAL |
| PIT-R5 Uncertainty / Abstention | STRONG |
| PIT-R6 Contextual Personal Reasoning | PARTIAL |
| PIT-R7 Supervision Quality | WEAK |

## Components Worth Reusing

Evidence-first memory records, provenance, local-first storage, conservative updates.

## Components NOT Suitable

It is a memory foundation, not a teacher or supervision source.

## Relationship to PPF

PPF foundation.

## Final Verdict

KEEP FOR PPF
