# PIT-12 — Candidate Qualification Evidence Generation

Status: Research Evidence Generation

## Purpose

Generate evidence artifacts required by PIT-11.2 candidate qualification execution.

PIT-12 evaluates teaching signal evidence using the frozen PIT-10 evaluation contract.

## Evidence Structure

Each candidate evaluation evidence item must record:

- Scenario input
- Observation
- Inference
- Confidence
- Applicability Boundary
- Revision Trigger
- Outcome assessment

## Evaluation Coverage

Evidence must cover:

- stable preference
- preference drift
- conflicting evidence
- user correction
- rare exception
- insufficient evidence

## Qualification Dimensions

Evidence is evaluated against:

- Pattern understanding
- Temporal reasoning
- Correction recovery
- Uncertainty calibration
- Supervision quality
- Evidence traceability
- Pattern Lifecycle Quality

## Key Finding

Candidate teacher quality must be determined from teaching signal evidence and lifecycle behavior.

General model capability alone is insufficient for Personal Intelligence Teacher qualification.

## Decision Boundary

PIT-12 does not:

- select a final teacher
- integrate a model
- start training
- modify MindForge runtime
- modify PPF

## Next Step

Complete candidate evidence generation and prepare qualification review.

## Candidate Execution Constraints

External frontier candidates:

Role:

General Intelligence Teacher reference.

Requirement:

Stable API access required.

Local candidates:

Requirement:

Must fit MindForge local deployment envelope:

Hardware:

- Intel Core Ultra 7 258V
- RAM 32GB
- Intel Arc 140V 16GB GPU

Runtime:

- llama.cpp / Vulkan

Hybrid candidates:

External teacher capability may bootstrap local PIT capability.


## Execution Strategy Constraint

Teaching capability qualification must happen before local deployment optimization.

Local LLM evaluation is a final feasibility step, not the first capability filter.
