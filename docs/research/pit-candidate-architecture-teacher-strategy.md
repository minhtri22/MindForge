# PIT-3 — Candidate Architecture & Teacher Strategy

Status: Research Definition

## Objective

Define candidate Personal Intelligence Teacher (PIT) architectures before selecting models, training methods, or runtime integration.

PIT is not a smaller Qwen replacement. PIT is a supervision system that generates personal intelligence learning signals for MindForge.

## Core Separation

General Intelligence Teacher (GIT):

- Qwen
- GPT
- Claude class models

Responsibilities:

- general reasoning
- coding assistance
- knowledge
- language understanding
- world knowledge

Personal Intelligence Teacher (PIT):

Responsibilities:

- personal pattern discovery
- experience interpretation
- reflection
- preference evolution
- teaching signal generation

## Candidate Architecture A — Memory-Centric PIT

Pattern:

User Experience -> Memory System -> Pattern Extraction -> Teaching Signals

Inspired by:

- person-memory
- Personal World Models

Strengths:

- strong grounding
- explainable
- suitable for PPF

Weakness:

- memory retrieval alone does not create intelligence evolution

## Candidate Architecture B — Reflection-Centric PIT

Pattern:

Experience -> Reflection Model -> Hypothesis -> Evaluation -> Teaching Signal

Inspired by:

- MIA concepts

Strengths:

- learns from outcomes
- can evolve strategies

Weakness:

- requires reliable evaluation loop

## Candidate Architecture C — Hybrid PIT (preferred research direction)

Pattern:

Raw Experience
        |
        v
Personal Memory Layer
        |
        v
Pattern Discovery
        |
        v
Reflection / Reasoning Layer
        |
        v
Teaching Signal Generator
        |
        v
MindForge Personal Model

This separates:

- storage
- understanding
- reflection
- supervision

## Teacher Strategy

Qwen/GPT/Claude should not directly teach personal behavior.

They provide:

- reasoning capability
- language capability
- general knowledge

PIT provides:

- personal adaptation signals
- preference evolution
- behavioral understanding

## Candidate Model Roles

### General Teacher

Examples:

- Qwen3.8-27B
- GPT-class models
- Claude-class models

Role:

General intelligence supervision.

### Personal Teacher

Potential future candidates:

- small language model with memory/reasoning loop
- world-model inspired architecture
- hybrid symbolic + neural system

No final model selected.

## PIT Capability Requirements

PIT-C1 Observation

Capture user events and outcomes.

PIT-C2 Pattern Extraction

Identify recurring personal structures.

PIT-C3 Reflection

Explain why patterns occur.

PIT-C4 Teaching Signal Generation

Convert experience into training/evaluation signals.

PIT-C5 Evolution

Handle correction, drift, forgetting and contradiction.

PIT-C6 Personal Reasoning

Select actions appropriate for this individual.

## Rejected Directions

Do not build:

- another general LLM
- simple RAG memory
- chatbot memory plugin
- model registry
- premature agent framework

## Decision

Proceed with Hybrid PIT as the research hypothesis.

Next stage:

PIT-4 — Evaluation Protocol & Data Requirements.

No model selection, training, or MindForge runtime change is authorized at this stage.
