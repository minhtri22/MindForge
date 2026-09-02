# MindForge Personal Intelligence — Two-Track Research Direction

Status: **STRATEGIC DIRECTION / FOUNDATION RESEARCH ONLY**

This document freezes the current research direction without prematurely turning it into implementation architecture.

## Core thesis

MindForge should not try to make a tiny model "know everything".

The working edge/mobile thesis is:

> **Recognize me, not know everything.**

Personal intelligence is decomposed into two independent research tracks plus external capabilities:

```text
Track A — MindForge-Mobile         -> UNDERSTAND
Track B — Personal Pattern Foundation (PPF) -> RECOGNIZE ME
Apps / Agents                      -> KNOW & ACT
```

World knowledge and complex actions may be delegated to apps, OEM services or external agents. The local system should specialize in understanding the user, current context, personal state, personal patterns and routing.

---

# Track A — MindForge-Mobile

## Mission

Determine whether a very small model, with a target envelope around **<=20M parameters**, can become a useful local personal-intelligence router on mobile/edge hardware.

The target is not a general-purpose assistant that answers arbitrary world-knowledge questions.

The target is a model that is strong at:

1. personal intent recognition;
2. personal entity resolution;
3. contextual command understanding;
4. preference/routine-aware interpretation;
5. tool/app/agent selection;
6. argument extraction;
7. deciding local-vs-external handling;
8. interpreting returned results;
9. short local summarization/transformation where practical.

## Track-A research question

> What is the smallest model that is "personal enough" when world knowledge and persistent personal state are externalized?

Candidate sizes should be tested rather than assumed:

```text
5M / 10M / 20M / 50M
```

Potential evaluation dimensions include intent accuracy, personal-entity resolution, tool selection, argument extraction, clarification decisions, local-vs-external routing, latency, RAM and energy.

The 20M target is a hypothesis, not a success claim.

## Track-A non-goals for now

Do not yet add to the active kernel:

- Android/iOS integration;
- OEM permission layers;
- app-function integrations;
- agent frameworks;
- personal memory implementation;
- PPF integration;
- speculative mobile runtime architecture.

Track A must prove its capability envelope before deployment architecture is admitted.

---

# Track B — Personal Pattern Foundation (PPF)

## Mission

PPF is a **greenfield foundation research track**.

It is not a continuation, rewrite or salvage program for legacy PIS.

The primary question is:

> **How little machinery is required to reliably recognize one person over time from a personal/device event stream?**

No representation, algorithm, storage model, hierarchy or pattern engine is assumed in advance.

PPF starts from the problem definition and earns architecture only through evidence.

## Legacy PIS policy

Legacy PIS is **outside the PPF execution path**.

Do not spend PPF research time on:

- porting PIS;
- adapting PIS;
- salvaging PIS components;
- benchmarking PPF against PIS as a prerequisite;
- preserving HDC, SLM, repair, pattern taxonomies or other legacy structures;
- maintaining compatibility with the PIS codebase.

Legacy PIS may remain as historical research material, but PPF must be designed as if it does not exist.

This rule exists to keep PPF small, clean and free from sunk-cost architectural bias.

---

# PPF proof ladder — five layers

PPF must be proven sequentially through five layers.

Each layer should have a frozen question, protocol, benchmark or acceptance gate before implementation complexity is added.

A later layer must not compensate for a failure at an earlier layer.

```text
L1 Define "Recognize Me"
        |
        v
L2 Personal Event Foundation
        |
        v
L3 Ground-Truth Personal Pattern Benchmark
        |
        v
L4 Minimal Baselines
        |
        v
L5 Minimum Missing Mechanism
```

If the five layers prove feasible, their minimal proven contracts may then be composed into PPF.

Architecture follows evidence; evidence does not follow architecture.

---

## Layer 1 — Define "Recognize Me"

### Question

What observable outputs make a system meaningfully better at recognizing one user over time?

Before defining algorithms, specify the behavioral contract.

A useful response may expose concepts such as:

```text
current context
likely personal pattern(s)
confidence
relevant exception(s)
uncertainty / abstention
supporting evidence summary
```

Example:

```text
Context:
Friday, 17:35, leaving office

Likely patterns:
- usually goes home after work: confidence 0.82
- Friday has frequent alternative destination: confidence 0.61
- usually messages spouse before commute: confidence 0.76

Uncertainty:
Friday behavior is less stable than Mon–Thu.
```

Layer 1 must define what success means without choosing how the system achieves it.

### Gate

PASS only if the output contract, failure modes, uncertainty semantics and useful personal-pattern categories can be specified independently of an implementation.

---

## Layer 2 — Personal Event Foundation

### Question

What is the minimum event/context model required to support reliable personal-pattern inference?

Candidate primitives may include:

```text
timestamp
event_type
source
actor/device
entity/person
context
action
result
explicit vs observed
availability / observability
```

A critical distinction must exist between:

```text
OBSERVED EVENT
OPPORTUNITY
NON-OCCURRENCE
UNKNOWN / NOT OBSERVABLE
```

Example:

```text
25 observable after-work opportunities
18 -> Maps -> Home
4  -> other destination
2  -> no Maps action
1  -> telemetry unavailable
```

This is more informative than merely recording 18 occurrences.

Layer 2 must avoid prematurely encoding a particular pattern algorithm into the event contract.

### Gate

PASS only if the event representation can express positive evidence, opportunity denominators, negative evidence, missing observations, explicit corrections and contextual conditions without ambiguity.

---

## Layer 3 — Ground-Truth Personal Pattern Benchmark

### Question

Can we evaluate personal-pattern recognition against histories whose true underlying behavior is known in advance?

Build controlled synthetic or semi-synthetic personal histories where the generator owns hidden ground truth.

Benchmark families should include at least:

```text
routine formation
routine absence / coincidence
routine drift
preference emergence
preference reversal
conditional preference
rare but important exception
relationship-conditioned behavior
temporal sequence
context -> action association
conflicting evidence
user correction
deletion / forgetting
insufficient evidence / abstention
contextual retrieval
```

The benchmark should include adversarial cases designed to induce false conclusions.

Examples:

```text
correlated events without stable personal intent
small-sample 3/3 coincidences
missing telemetry that must not count as negative evidence
conditional preferences hidden by global averages
rare critical exceptions
behavioral reversals
```

### Gate

PASS only if ground truth, event streams, expected discoveries, expected abstentions, counterexamples and metrics are frozen before candidate algorithms are evaluated.

---

## Layer 4 — Minimal Baselines

### Question

How much of "recognize me" can be solved with deliberately simple machinery?

Start with small baselines such as:

```text
A. frequency/count + threshold
B. frequency + exponential decay
C. context-conditioned counts/rules
D. simple sequence statistics / Markov model, only if needed
```

Prefer a few hundred transparent lines over a framework.

Primary quality dimensions may include:

```text
pattern precision
pattern recall
false discovery rate
false promotion rate
abstention accuracy
confidence calibration
exception recall
drift adaptation lag
reversal detection
contextual retrieval accuracy
```

Primary systems dimensions may include:

```text
memory footprint
local storage growth
update latency
query latency
background CPU cost
deletion correctness
```

### Gate

If simple baselines already satisfy the useful product envelope, STOP adding complexity.

The simplest sufficient solution wins.

---

## Layer 5 — Minimum Missing Mechanism

### Question

Where do the minimal baselines fail, and what is the smallest additional mechanism that closes a measured gap?

Examples of possible gaps:

```text
conditional context composition
similar-but-not-identical situations
long temporal dependencies
better confidence calibration
contextual retrieval
compact generalized representation
```

Only after a concrete failure is demonstrated may a mechanism be proposed.

Candidate mechanisms are not predetermined. They might include a better statistical model, contextual feature composition, compact embeddings, Bayesian treatment, lightweight sequence modeling or another small mechanism.

No technology is protected in advance.

### Gate

A mechanism is admitted only if it provides a measurable benefit over Layer-4 baselines that justifies its complexity, memory and latency cost.

---

# Feasibility and composition rule

The five layers are not five modules that must automatically exist in the final product.

They are five proof stages.

The process is:

```text
prove L1
-> prove L2
-> prove L3
-> prove L4
-> prove L5 only if necessary
```

Then:

```text
minimal proven contracts
        +
minimal proven mechanisms
        |
        v
      PPF
```

If a layer is unnecessary, it should not create architecture merely to preserve the roadmap shape.

If a layer fails, stop and revise the foundation instead of hiding the failure behind later complexity.

---

# PPF design constraints

PPF should optimize for:

```text
small
local-first
CPU-friendly
incremental
reversible
explainable
deletable
context-aware
confidence-aware
low-latency
low-memory
```

PPF must not automatically execute user actions.

The preferred future authority boundary is:

```text
PPF produces personal pattern context/evidence
MindForge-Mobile interprets and routes
OS / host permission layer authorizes actions
```

---

# Track A + Track B convergence

Track A and Track B remain independent until each proves its own minimal contract.

Target composition, if both tracks succeed:

```text
        Personal / Device Context
                  |
        +---------+---------+
        |                   |
        v                   v
 MindForge-Mobile          PPF
    UNDERSTAND         RECOGNIZE ME
        |                   |
        +---------+---------+
                  |
                  v
           Personal Router
                  |
        +---------+---------+
        |                   |
        v                   v
  Local / App Action    External Agent
                       KNOW & ACT
```

Do not define a generic integration bus before the two independent contracts are proven.

---

# Personalization thesis

A useful personal system may not require continuous neural fine-tuning.

A future operational model may look like:

```text
Personal Intelligence(t)
=
Base MindForge-Mobile
+ Personal Facts / State(t)
+ PPF-derived Personal Patterns(t)
+ Current Context(t)
+ Permitted Apps / Agents
```

The changing personal state can therefore live largely outside immutable model weights.

---

# Product / OEM thesis

If the technical hypotheses survive testing, the target is not simply a small mobile chatbot.

The stronger proposition is:

> **A small, private, always-available personal intelligence kernel that understands locally, recognizes the user over time, and delegates world knowledge or actions only when necessary.**

Potential OEM benefits remain hypotheses to measure:

- fewer cloud inference calls;
- lower latency for common personal interactions;
- lower bandwidth/server cost;
- stronger privacy boundaries;
- small always-ready footprint;
- personalization without requiring a giant on-device general model.

---

# Research discipline

This direction does not reopen stopped Phase-0 continual-learning or memory hypotheses.

Track A and Track B ask new questions under different assumptions.

All future work follows:

```text
question
-> frozen protocol / benchmark
-> smallest experiment
-> evidence
-> PASS / REVISE / STOP
-> only then architecture
```

---

# Current decision

```text
Track A — MindForge-Mobile
STATUS: RESEARCH DIRECTION / CAPABILITY ENVELOPE NOT YET PROVEN

Track B — Personal Pattern Foundation (PPF)
STATUS: RESET / GREENFIELD FOUNDATION RESEARCH

PPF proof ladder:
L1 Define Recognize Me
L2 Personal Event Foundation
L3 Ground-Truth Personal Pattern Benchmark
L4 Minimal Baselines
L5 Minimum Missing Mechanism

Legacy PIS:
STATUS: OUTSIDE PPF EXECUTION PATH / HISTORICAL ONLY

PPF implementation:
STATUS: NOT AUTHORIZED

Track A + PPF integration:
STATUS: NOT AUTHORIZED
```

The immediate Track-B task is to freeze the Layer-1 / Layer-2 foundation problem before implementing a pattern engine.