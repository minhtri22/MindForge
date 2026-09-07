# PIT-2.3 Architecture Synthesis & Capability Definition

Status: DEFINED

## Purpose

This document defines the research boundary for Personal Intelligence Teacher (PIT).

PIT is not a replacement for a general LLM, a memory database, or the Personal Pattern Foundation (PPF). PIT is a supervision mechanism that transforms personal experience and observations into useful learning signals for a personal intelligence system.

## Core Separation

### General Intelligence Teacher

Examples:

- Qwen
- GPT
- Claude

Responsibilities:

- language understanding
- general reasoning
- coding assistance
- world knowledge
- general problem solving

### Personal Intelligence Teacher

PIT responsibilities:

- understand user-specific experience
- discover personal patterns
- generate reflection and correction signals
- support adaptation of personal intelligence

### Personal Pattern Foundation

PPF responsibilities:

- represent personal patterns
- store evidence
- maintain confidence and uncertainty
- support evolution and forgetting

## PIT Is Not

PIT is not:

- a larger general LLM
- a simple memory database
- a RAG system
- a chatbot persona layer
- a replacement for PPF

## Capability Model

### PIT-C1 Personal Observation

Input:

- user events
- interactions
- outcomes
- context

Output:

- structured observations
- evidence candidates

### PIT-C2 Pattern Extraction

Input:

- historical observations

Output:

- candidate routines
- preferences
- behavioral patterns

### PIT-C3 Reflection

Input:

- events
- outcomes
- patterns

Output:

- explanations
- hypotheses
- possible improvements

### PIT-C4 Teaching Signal Generation

Input:

- personal experience
- reflection
- corrections

Output:

- learning signals
- examples
- preference updates

### PIT-C5 Long-Term Evolution

Required handling:

- correction
- contradiction
- confidence changes
- forgetting
- preference drift

### PIT-C6 Personal Reasoning

Ability to reason about:

- likely user preferences
- context-dependent decisions
- personal strategies

## Architecture Pattern Synthesized From Literature

Common pattern:

Experience

↓

Memory / Representation

↓

Pattern Discovery

↓

Reflection

↓

Teaching Signal

↓

Personal Model Adaptation

## Relationship To Existing Research

Person-memory and Personal World Models provide evidence for personal representation and PPF foundations.

MIA provides evidence for memory lifecycle and experience-driven adaptation patterns.

MIB provides an evaluation principle: memory quality should be measured by improvement in future decisions, not only retrieval accuracy.

No reviewed repository provides a complete PIT solution.

## Open Research Questions

1. How can PIT avoid creating false beliefs about a user?

2. How can personal knowledge be separated from temporary behavior?

3. How can teaching signals be evaluated objectively?

4. What part requires a model and what part requires structured systems?

5. How should PIT interact with PPF without becoming the source of truth?

## Evaluation Principle

The fundamental PIT question is:

"Does MindForge perform better because PIT exists?"

Success should be measured by downstream improvement:

- better decisions
- better adaptation
- fewer incorrect assumptions
- improved personal task performance

Not by:

- memory size
- number of stored facts
- retrieval accuracy alone

## Model Selection Status

No PIT candidate model has been selected.

No training has started.

Further work requires capability-based evaluation before choosing architecture or model.
