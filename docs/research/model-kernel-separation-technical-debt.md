# Model / Kernel Separation Technical Debt

Status: **ARCHITECTURE TRANSITION / TECHNICAL DEBT — NON-BLOCKING FOR PPF**

This note records a known mismatch between the current physical code layout and the newer MindForge architecture invariants. It is intentionally non-blocking for the active PPF research branch.

## 1. Current implementation state

The current `mindforge/` package was built and validated as a compact end-to-end local LLM kernel. It currently colocates:

```text
mindforge/
  model.py
  config.py
  tokenizer.py
  train.py
  checkpoint.py
  evaluate.py
  generate.py
  experiment.py
  ...
```

`model.py` is already a separate source module containing the learned Transformer implementation, but the model is not yet separated as an architectural component behind a model/kernel contract.

`KernelConfig` currently contains data, model, and training configuration, and training/runtime code imports `TransformerLM` directly. Therefore:

```text
Code-level model modularity: YES
Architectural model/kernel separation: NO
Package separation: NO
Stable model contract: NO
```

This is not considered a defect in the completed Phase-1/Phase-2 evidence. It reflects the original thin end-to-end kernel goal.

## 2. Target architecture

The target conceptual structure is:

```text
MindForge
├── Model Component
│   ├── learned architecture
│   ├── weights/checkpoint representation
│   └── model-facing inference capabilities
│
├── Kernel Runtime
│   ├── orchestration
│   ├── proven universal runtime primitives
│   └── generic extension/plugin boundary
│
├── Plugins / Extensions
│   └── feature-specific mechanisms such as PPF
│
├── Hosts / Products
│   └── Mobile / CLI / other compositions
│
└── Research / Tooling
    ├── training
    ├── evaluation
    └── experiments
```

Architectural rule:

```text
Model != Kernel Runtime
```

The Kernel Runtime may use a model, but it must depend on a stable **Model Contract**, not on a particular Transformer implementation.

## 3. Responsibility split

### Model Component

Owns learned/model-specific concerns such as:

```text
model architecture
weights
forward/inference behavior
model-specific capability declaration
model-specific loading/adaptation
```

The Model Component must not own:

```text
plugin semantics
PPF semantics
host/mobile semantics
generic extension orchestration
```

### Kernel Runtime

Owns only proven universal runtime primitives and orchestration required independently of a specific feature plugin.

The Kernel Runtime must not depend on:

```text
Transformer internals
n_layers / n_heads / d_model
PPF-specific concepts
host-specific/mobile-specific logic
```

### Research / Tooling

Training, evaluation, and experiment machinery need not be part of the future runtime kernel. Their final physical placement remains undecided until a real separation task is authorized.

## 4. Model Contract principle

The intended boundary is:

```text
Kernel Runtime <-> Model Contract <-> Model Component
```

The kernel should depend on **what the model can do**, not **how the model is built**.

Possible capability dimensions may eventually include things such as generation support, context limits, input/output modality, or structured-output support, but no concrete API is frozen by this note.

Do not prematurely freeze methods such as `load()`, `infer()`, exact tensor types, checkpoint formats, or capability enums without a dedicated proof task.

## 5. Pivot/replaceability goal

A successful separation should allow the learned model to change without forcing redesign of the kernel, plugins, or hosts when the Model Contract remains compatible.

Examples of possible future model pivots include:

```text
different Transformer size
distilled model
different neural architecture
external/local model adapter
other learned model implementations
```

These examples are not roadmap commitments.

## 6. Scale invariant

Model evolution must not cause feature architecture to leak into the kernel.

Likewise, feature growth should primarily increase plugins, not kernel primitives.

Target relationship:

```text
model implementations may change
feature/plugin count may grow
kernel primitives remain small and slow-growing
```

## 7. Do not refactor by folders first

The transition must **not** begin by merely moving files into new folders/packages.

Required order when this debt is eventually activated:

```text
1. Define the smallest Model Contract from demonstrated use cases.
2. Freeze compatibility/behavior tests for the current model through that contract.
3. Adapt the current Transformer implementation to satisfy the contract.
4. Prove existing training/eval/generation evidence remains intact where applicable.
5. Only then consider physical package separation.
```

A folder move without a proven contract does not count as architectural separation.

## 8. Activation gate

This technical debt may be worked on in parallel with PPF because it is orthogonal to PPF semantic/benchmark research, provided the work does not modify PPF contracts or claim PPF evidence.

However, implementation/refactor is **not automatically authorized** by this note.

Before actual model/kernel refactor, a dedicated task must establish:

```text
MKS-G1 — concrete reason to separate now
MKS-G2 — minimal model/kernel behavioral contract
MKS-G3 — compatibility test suite
MKS-G4 — current Transformer adapter path
MKS-G5 — no regression to frozen kernel evidence
MKS-G6 — no PPF/plugin semantics in Model Contract
MKS-G7 — no speculative universal plugin framework
```

PASS is required before physical restructuring.

## 9. Relationship to PPF

PPF remains an optional plugin/extension research track.

This technical debt:

```text
does not block PPF-L3/L4/L5
does not alter PPF truth semantics
does not authorize PPF integration
does not move PPF into the kernel or model
```

PPF and model/kernel separation may proceed as independent parallel tracks.

If a future PPF integration proposes a kernel capability, the architecture invariants and Kernel Admission Test remain authoritative.

## 10. Current decision

```text
TECHNICAL DEBT IDENTIFIED: YES
MODEL SOURCE MODULE ALREADY SEPARATE: YES
MODEL ARCHITECTURAL COMPONENT SEPARATE: NO
MODEL CONTRACT DEFINED: NO
PHYSICAL REFACTOR AUTHORIZED: NO
PPF BLOCKED BY THIS DEBT: NO
PARALLEL RESEARCH/PLANNING ALLOWED: YES
```

See also:

- `docs/research/mindforge-architecture-invariants.md`
- `PLAN.md`
