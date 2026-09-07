# PPF-G2 Boundary & Runtime Isolation Proof

## Research Question

Can PPF remain isolated as an optional plugin capability without dependency leakage into MindForge Kernel, Model, or Host?

## Current Architecture Assumptions

Frozen invariant:

Model != Kernel

Kernel owns generic execution substrate, lifecycle primitives, plugin boundary, and resource contracts. Kernel does not own personal semantics, evidence interpretation, pattern meaning, or user preference.

Model provides optional learned representation assistance. Model does not own personal truth, evidence validity, or lifecycle decisions.

Host owns interaction, permissions, and device integration. Host does not own reasoning semantics.

PPF remains an optional plugin / extension.

## Dependency Direction

Required direction:

Host
 |
 v
PPF Plugin
 |
 v
Contracts
 |
 v
Kernel primitives

Forbidden direction:

Kernel -> PPF semantics

Host -> personal reasoning logic

## Component Responsibility Matrix

| Component | May depend on | Must not depend on |
|---|---|---|
| Kernel | generic contracts, lifecycle primitives, resources | PPF semantics, personal meaning |
| PPF Plugin | Kernel contracts, event/evidence contracts | Kernel internals, host implementation details |
| Model | optional capability requests | personal truth, evidence ownership |
| Host | plugin API, permissions, device APIs | reasoning rules, semantic decisions |

## Lifecycle Ownership

Kernel lifecycle:
- load
- start
- stop
- resource ownership

PPF lifecycle:
- initialize semantic state
- consume permitted events
- produce plugin outputs

Host lifecycle:
- user session
- permissions
- device availability

No lifecycle ownership conflict is identified.

## Isolation Analysis

Q1: Can PPF be removed without breaking Kernel?

YES. Kernel only depends on generic contracts. PPF is an optional capability provider.

Q2: Can Model implementation change without invalidating PPF contract?

YES. PPF contracts define semantic boundaries independently from model implementation.

Q3: Can Host application change without changing PPF semantics?

YES. Host provides interaction and permissions only.

Q4: Can another plugin replace PPF without Kernel changes?

YES. A plugin boundary allows capability replacement without modifying kernel primitives.

## Risks

- Contract design must prevent accidental promotion of personal semantics into Kernel primitives.
- Plugin outputs must remain explicitly scoped to avoid becoming hidden reasoning authority.
- Future runtime implementation must preserve dependency direction.

## PASS / FAIL Decision

PASS

Criteria satisfied:

- Kernel remains independent from PPF.
- PPF remains replaceable.
- Model remains optional.
- Host remains composition layer.
- Dependency direction is one-way.
- No implementation dependency introduced.

## Recommendation for G3

Proceed to PPF-G3 Minimal Plugin Prototype Feasibility.

G3 should remain limited to proving contract flow only and must not introduce recognizers, ML training, LLM reasoning loops, or production runtime integration.
