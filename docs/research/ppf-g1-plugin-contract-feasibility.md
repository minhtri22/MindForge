# PPF-G1 Plugin Contract Feasibility

## Purpose

Evaluate whether PPF can exist as an isolated optional plugin capability without contaminating Kernel, Model, or Host.

## Boundary Analysis

### Plugin lifecycle contract

Ownership: PPF plugin.

The plugin owns activation, state lifecycle, and participation contracts. Kernel only provides generic lifecycle primitives.

### PersonalEvent contract boundary

Ownership: PPF plugin contract layer.

Personal event semantics remain outside Kernel. Kernel may transport generic events but does not interpret personal meaning.

### Evidence contract boundary

Ownership: PPF plugin.

Evidence interpretation belongs to PPF. Kernel provides storage/execution primitives only.

### Observation Eligibility contract boundary

Ownership: PPF plugin.

The current proven primitive can be represented as an optional semantic capability without requiring Kernel changes.

### Semantic state/output contract boundary

Ownership: PPF plugin output contract.

Host consumes outputs through defined interfaces and does not contain reasoning semantics.

## Dependency Direction

Allowed:

Host
|
PPF Plugin
|
Contracts
|
Kernel primitives

Forbidden:

- Kernel -> PPF semantics
- Model -> PPF implementation dependency
- Host -> reasoning logic

## Responsibility Ownership

| Component | Responsibility |
|---|---|
| Kernel | generic runtime primitives, lifecycle contracts, plugin interface |
| PPF Plugin | personal event semantics, evidence interpretation, eligibility, semantic state |
| Model | unchanged model capability |
| Host | interaction and device integration |

## Unresolved Questions

- Whether future PPF capabilities require additional contracts remains open.
- Real-world interface feasibility is deferred to later roadmap stages.

## G1 Verdict

PASS

G1 criteria:

- Kernel does not depend on personal semantics: PASS
- PPF does not require model implementation: PASS
- Host does not contain reasoning semantics: PASS
- Plugin contract represents Observation Eligibility primitive: PASS
- No new mechanism introduced: PASS

Next authorized step: PPF-G2 Boundary & Runtime Isolation Proof.
