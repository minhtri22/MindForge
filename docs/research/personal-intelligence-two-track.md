# MindForge Personal Intelligence — Two-Track Research Direction

Status: **STRATEGIC DIRECTION / NOT YET AUTHORIZED FOR IMPLEMENTATION**

This document captures the research/product thesis agreed after Phase 2. It exists to preserve direction without prematurely turning it into kernel architecture.

## Core thesis

MindForge should not try to make a tiny model "know everything".

The more promising edge/mobile thesis is:

> **Recognize me, not know everything.**

A compact personal model can focus on understanding the user, current context, intent, local state and routing. World knowledge and complex actions can be delegated to apps, OEM services or external agents when required.

The resulting architecture is deliberately decomposed:

```text
MindForge-Mobile  -> UNDERSTAND
PIS               -> RECOGNIZE ME
Apps / Agents     -> KNOW & ACT
```

Personal intelligence is therefore not defined as a single gigantic neural model. It is the composition of a small language/intelligence kernel, explicit personal memory/state, learned behavioral patterns, current context, and controlled access to external capabilities.

---

# Track A — MindForge-Mobile

## Mission

Determine whether a very small model, with a target envelope of roughly **<=20M parameters**, can become a useful local personal-intelligence router on mobile/edge hardware.

The target is not a general-purpose assistant that answers arbitrary world-knowledge questions.

The target is a model that is excellent at:

1. personal intent recognition;
2. personal entity resolution;
3. contextual command understanding;
4. preference/routine-aware interpretation;
5. tool/app/agent selection;
6. argument extraction;
7. deciding local-vs-external handling;
8. interpreting returned results;
9. short local summarization/transformation where practical.

## Why <=20M may be viable

The model does not need to store all personal facts, long histories, behavioral patterns and world knowledge in its weights.

Conceptually:

```text
Personal Intelligence
=
Compact Base Model
+ Personal Facts / State
+ Personal Patterns
+ Current Context
+ Apps / Tools / External Agents
```

This separates four different jobs:

- **weights**: language/computation prior;
- **personal memory/state**: explicit facts and user-owned data;
- **PIS**: changing behavioral patterns, preferences, routines and exceptions;
- **apps/agents**: world knowledge and actions.

## Intended mobile behavior

MindForge-Mobile should be suitable for low-latency, privacy-preserving, frequently invoked local inference.

It should prefer local handling for simple/private tasks and delegate only when necessary:

```text
User request
    |
    v
MindForge-Mobile
    |
    +-- simple/personal/local --> local handling
    |
    +-- app action ------------> permitted app/system function
    |
    +-- complex/world query ---> external agent / OEM model / cloud model
```

External systems should receive the minimum task context required, not the user's entire personal history.

## OEM/system-layer opportunity

A normal application may be sandboxed and have limited cross-app context. The stronger product opportunity is therefore potentially an **OEM/system-level personal intelligence kernel**.

With user permission and OS-level mediation, an OEM integration could safely connect to capabilities such as:

- contacts;
- calendar;
- notifications;
- local files;
- device state;
- routines;
- location context;
- wearable/sensor context;
- app-exposed actions/functions/intents.

MindForge-Mobile should never assume unrestricted app access. Permission brokerage belongs to the OS/OEM/application boundary.

## Long-term deployment family

A possible model family, subject to evidence:

```text
MindForge-Tiny      ~5M–20M    mobile / embedded / always-ready
MindForge-Small     ~20M–100M  laptop / edge / richer local tasks
MindForge-Research  larger      training/scaling experiments
```

These are hypotheses, not committed product SKUs.

## Track-A first research question

> What is the smallest model that is "personal enough" when knowledge and persistent personal state are externalized?

A future benchmark should compare candidate sizes such as:

```text
5M / 10M / 20M / 50M
```

on fixed personal-assistant capabilities such as:

- intent classification;
- personal entity resolution;
- preference-conditioned interpretation;
- routine-aware interpretation;
- tool selection;
- argument extraction;
- clarification decision;
- local-vs-external routing;
- latency;
- RAM;
- energy where measurable.

The 20M target is a hypothesis to test, not a success claim.

## Track-A non-goals for now

Do not yet add to the active kernel:

- Android/iOS integration;
- AppFunctions/App Intents integrations;
- mobile runtime code;
- quantization stack;
- OEM permission layer;
- agent framework;
- personal memory implementation;
- PIS integration.

Track A should first prove the capability envelope.

---

# Track B — PIS Re-evaluation / Personal Pattern Intelligence

## Mission

Re-evaluate PIS from first principles for the new role:

> **PIS should help MindForge recognize the user over time without requiring continual fine-tuning of model weights.**

The existing PIS architecture must not be preserved merely because prior work exists. It may need substantial redesign or replacement.

The correct question is not:

> "How much of old PIS can we keep?"

It is:

> "What is the minimum pattern substrate required for reliable personal recognition on an event stream?"

## Minimum capabilities PIS must prove

A personal PIS should demonstrate at least six capabilities:

1. **Observe** — consume personal/device events and context over time;
2. **Discover** — propose routines, preferences, relationships, sequences and contextual behaviors;
3. **Distinguish** — separate meaningful patterns from coincidence/noise;
4. **Adapt** — reduce confidence in stale patterns and form new ones when behavior changes;
5. **Retrieve** — surface the right personal patterns for the current MindForge context;
6. **Explain / Forget** — show why a pattern exists and support complete removal when required.

## Principles worth preserving from legacy PIS

Even if implementation is rebuilt, retain these research/governance principles unless falsified:

```text
candidate != truth
promotion requires evidence
counterexamples matter
confidence can decay
correlation is not authority
host/user retains action authority
auditability matters
patterns must be removable
```

## Areas explicitly open to replacement

Do not assume that the following legacy choices remain appropriate:

- HDC-centric architecture;
- numeric-trace-first assumptions;
- broad multi-domain abstraction;
- complex pattern-family taxonomy;
- generic repair machinery;
- SLM layers without demonstrated personal-value benefit;
- production-substrate ambitions before the personal use case is proven.

## Initial personal pattern types

Start with a very small vocabulary of pattern semantics:

```text
Routine
Preference
Relationship
Sequence
Context -> Action
Exception
Change / Drift
```

Example:

```text
Context:
weekday, ~17:30, leaving office

Observed sequence:
open Maps -> navigate home -> play playlist A -> message person X

Candidate:
commute-home routine

Evidence:
17 occurrences / 21 opportunities

Counterexamples:
Friday behavior often differs

Confidence:
0.81
```

The output to MindForge should expose both likely pattern and meaningful uncertainty/exception, not a hard autonomous assumption.

## Facts are not patterns

The architecture should distinguish at least:

- **fact/memory**: "person X is my spouse";
- **pattern**: "after leaving work I usually message person X";
- **preference**: "when dining with person X I often choose Japanese food";
- **exception**: "with children present I usually choose something else".

PIS should primarily own evolving behavioral structure, not become a generic storage bucket for every personal fact.

## Avoid continual weight training by default

Preferred initial adaptation path:

```text
new behavior
    |
    v
observation
    |
    v
pattern candidate
    |
    v
evidence + counterevidence
    |
    v
confidence / drift update
```

rather than:

```text
new behavior -> fine-tune base model weights
```

This is especially attractive for mobile because it is cheaper, reversible, explainable, deletable and less exposed to catastrophic forgetting in model weights.

## Track-B first research artifact

Before rebuilding PIS, define a **Personal Pattern Benchmark**.

It should include controlled cases such as:

- routine formation;
- routine absence / false correlation;
- routine drift;
- preference emergence;
- preference reversal;
- conditional preference;
- rare-but-important exception;
- relationship-conditioned behavior;
- contextual retrieval;
- conflicting evidence;
- deliberate deletion/forgetting;
- user correction;
- insufficient-evidence abstention.

Legacy PIS should be run as a baseline against this benchmark before deciding whether to reuse, salvage or rebuild.

Possible decisions:

```text
KEEP      legacy design already meets the new gates
SALVAGE   retain only proven primitives
REBUILD   replace architecture, preserve useful principles/tests
STOP      personal-pattern substrate does not show value
```

No implementation decision is pre-authorized by this document.

---

# Track A + Track B convergence

The two tracks remain independent until each has evidence.

Target composition:

```text
              Personal / Device Event Stream
                         |
                         v
                    PIS (Track B)
              patterns / confidence /
             exceptions / drift context
                         |
                         v
                 MindForge-Mobile
                    (Track A)
                         |
              understand / decide / route
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
   Local state      App/System action   External agent
                                        / world model
```

A future interface between PIS and MindForge-Mobile should be defined only after both sides establish their minimal useful outputs.

Do not create a speculative generic plugin bus now.

## Personalization thesis

A useful personal model may not require continuous neural fine-tuning.

A future operational definition could be:

```text
Personal Model(t)
=
Base MindForge
+ Personal Memory(t)
+ Personal Patterns(t)
+ Current Context(t)
```

The changing part of the system can therefore live largely outside immutable base weights.

---

# Product / OEM thesis

If the technical hypotheses survive testing, the product is not simply "a small mobile chatbot".

The stronger proposition is:

> **A small, private, always-available personal intelligence kernel that recognizes the user locally and delegates world knowledge or actions to permitted apps/agents only when necessary.**

Potential advantages to an OEM, subject to measurement:

- lower cloud inference frequency;
- lower latency for common personal interactions;
- lower bandwidth/server cost;
- stronger privacy boundary;
- always-ready behavior with a small memory footprint;
- cross-device reuse of the same personal-intelligence concepts;
- differentiation through personalization rather than generic model size.

Possible device surfaces include mobile, wearable, automotive, TV/home devices and other edge hardware, but none is yet committed.

---

# Research discipline and reopening rules

This document does **not** reopen the stopped Phase-0 continual-learning or memory hypotheses.

It creates two new questions with different framing:

- Track A asks whether a compact model can perform personal understanding/routing when knowledge is externalized.
- Track B asks whether explicit pattern learning on personal event streams provides useful, reliable, reversible personalization without continual weight updates.

Any future work must follow the MindForge process:

```text
question
-> frozen benchmark/protocol
-> smallest experiment
-> evidence
-> PASS / REVISE / STOP
-> only then architecture
```

No track becomes active implementation merely because this strategic document exists.

---

# Current decision

```text
Track A — MindForge-Mobile
STATUS: RESEARCH DIRECTION / BENCHMARK REQUIRED

Track B — PIS Personal Pattern Intelligence
STATUS: RE-EVALUATE FROM FIRST PRINCIPLES / BENCHMARK REQUIRED

Integration
STATUS: NOT AUTHORIZED
```

The next roadmap decision should be made only after Phase 2 is fully closed and reviewed.