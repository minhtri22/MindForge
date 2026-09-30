# MindForge Architecture Invariants

Status: **ARCHITECTURE DECISION / FROZEN UNTIL EXPLICITLY REVISED**

Decision scope: MindForge model/kernel boundary, extensions/plugins, PPF placement, and host/product composition.

## 1. Final architecture model

MindForge is organized into four distinct architectural roles:

```text
Host / Product
    |
    +-- composes Kernel + selected Plugins

Plugins / Extensions
    |
    +-- feature-specific mechanisms and semantics

MindForge Kernel
    |
    +-- only proven universal runtime primitives/contracts
    +-- operates the Model

MindForge Model
    |
    +-- learned representations/capabilities
    +-- Transformer / weights / neural computation
```

The four roles are intentionally different.

```text
The Model owns learned representations/capabilities.
The Kernel owns only proven universal primitives.
Plugins own feature-specific mechanisms and semantics.
Hosts own composition.
```

This replaces the earlier shorthand `Kernel owns primitives`, which was too broad and could be misread as permission to add feature-specific deterministic machinery to the kernel.

## 2. D1 — MindForge-Mobile is not the architectural center

MindForge-Mobile is one optional host/product branch of MindForge. It is not the primary architecture and must not become the place where cross-cutting MindForge capabilities are anchored by default.

A capability useful beyond one host must not be defined as a MindForge-Mobile feature merely because mobile is a convenient validation environment.

PPF therefore must not be architected as a MindForge-Mobile subsystem. MindForge-Mobile may later consume PPF, but only as one optional host/consumer.

## 3. D2 — Model is not the Kernel

The MindForge Model is the learned neural component: Transformer architecture, parameters/weights, and learned representations/capabilities.

The MindForge Kernel is the minimal generic runtime/core that operates the model and, only when separately proven necessary, exposes stable universal primitives/contracts to extensions and hosts.

Therefore:

```text
MindForge Model != MindForge Kernel
MindForge Model is operated by / contained within the MindForge Kernel runtime boundary
```

Current repository history may use `LLM kernel` as an umbrella phrase for the compact end-to-end research stack. For architecture decisions from this document onward, use the more precise terminology above.

Model-level primitives such as embeddings, attention, normalization, MLP blocks, residual paths, and LM head are neural/model internals. They are not the same thing as kernel/runtime primitives.

## 4. D3 — Kernel is an independent minimal core

The kernel must be independently operable and must not require any specific optional plugin.

Domain-specific, product-specific, host-specific, optional, or independently evolvable capabilities belong outside the kernel by default.

The kernel is not required to be artificially empty. A capability may enter the kernel only when it is a genuinely universal runtime primitive and passes the Kernel Admission Test.

The default rule is:

```text
domain/product/optional capability -> Plugin
host/platform-specific capability  -> Host / Adapter
learned/generalizable capability    -> first evaluate Model-level learning
universal runtime primitive         -> Kernel candidate, only after KAT proof
```

## 5. Capability placement decision tree

For every new capability, determine placement in this order.

### Step 1 — Learned/generalizable?

Can the capability reasonably be represented or learned by the Model rather than hard-coded as feature logic?

If YES, evaluate it first as a model/research question. Do not automatically encode it as a kernel primitive.

### Step 2 — Feature/domain-specific?

Does the capability carry feature-specific semantics, state, policy, or lifecycle?

If YES -> Plugin/Extension.

### Step 3 — Host/platform-specific?

Does it depend on mobile permissions, UI lifecycle, OS APIs, deployment packaging, device adapters, or product-specific policy?

If YES -> Host / Adapter.

### Step 4 — Truly universal runtime primitive?

Only if it is independent of one feature/host and cannot be cleanly externalized without violating generic correctness/runtime boundaries may it become a kernel candidate.

Then it must pass KAT-1..KAT-5 before implementation is authorized.

## 6. Kernel invariants

1. **Independent operation** — the kernel operates without any particular optional plugin.
2. **No plugin-specific dependency** — kernel code must not import, name, or require a specific feature plugin.
3. **Generic contracts only** — kernel-facing extension contracts must not encode one plugin's domain vocabulary.
4. **Minimality** — kernel growth requires evidence, not convenience.
5. **Model/Kernel separation** — learned neural capability and runtime primitive are distinct design categories.
6. **Plugin replaceability** — removing/replacing one plugin must not invalidate unrelated kernel operation.
7. **Composition outside the kernel** — hosts/products choose enabled extensions.
8. **Failure isolation goal** — plugin failure should be containable without redefining kernel semantics; exact mechanics remain a later decision.
9. **Independent evolution** — plugin internals may evolve while stable generic kernel contracts remain unchanged.
10. **Scale invariant** — feature count should scale primarily through plugins, not through proportional growth of kernel primitives.

Desired scaling behavior:

```text
number of features ↑
number of plugins ↑

kernel primitive set ~ small / slowly changing
```

If every new feature requires new kernel primitives, the architecture boundary is considered suspect and must be reviewed.

## 7. Kernel Admission Test (KAT)

Before moving any capability into the kernel, the proposal must answer all of the following.

### KAT-1 — Genericity

Is the capability independent of a specific domain, feature, product, or host?

If NO -> keep it outside the kernel.

### KAT-2 — Reuse / core necessity

Is the capability required by the kernel itself or broadly useful across multiple independently plausible extensions?

If NO -> plugin territory by default.

### KAT-3 — Externalization test

Can the capability live outside the kernel behind a stable contract without breaking generic correctness, lifecycle guarantees, isolation, or an essential runtime boundary?

If YES -> keep it outside the kernel.

### KAT-4 — Contract stability

Can the kernel-facing abstraction be defined without importing the semantics of one particular plugin?

If NO -> do not admit it.

### KAT-5 — Evidence

Is there measured or demonstrated evidence that the capability must be a kernel primitive rather than merely being convenient there?

If NO -> defer admission.

A kernel addition must pass all five tests before implementation is authorized.

## 8. What a kernel primitive is — and is not

A kernel primitive is deterministic generic runtime machinery, not manually hard-coded intelligence for a feature.

Potential future examples, only if separately proven necessary:

```text
extension lifecycle
bounded capability invocation
context exchange
resource boundary
opaque state-provider contract
```

These are examples, not authorized implementations.

A kernel primitive must not look like:

```text
recognize_personal_routine()
infer_food_preference()
manage_calendar_semantics()
mobile_permission_policy()
```

Those belong to plugins/hosts or, where appropriate, learned model capability.

The architecture must avoid a scaling model in which every feature adds feature-specific primitives to the kernel.

## 9. Model responsibility

The Model owns learned capabilities such as representations that may support language, generalization, reasoning, or other experimentally established learned behavior.

The architecture must not assume that every useful capability should be manually coded into deterministic runtime primitives.

Conversely, deterministic correctness/lifecycle boundaries should not be pushed into learned weights merely because the model can approximate them.

This creates a deliberate separation:

```text
learned/generalizable behavior -> Model candidate
universal deterministic runtime mechanics -> Kernel candidate
feature-specific mechanisms/semantics -> Plugin
host/platform integration -> Host / Adapter
```

## 10. Plugin / Extension invariants

An extension/plugin:

- owns feature-specific semantics and state;
- may depend on stable generic kernel contracts;
- must not require the kernel to know its domain vocabulary;
- should expose a bounded contract to hosts/authorized consumers;
- preserves its own validation, lifecycle, and feature-specific correctness rules;
- may be optional for a host/product;
- does not gain kernel status merely because it becomes important or widely used.

`Important` is not the same as `core`.

## 11. Host / Product responsibility

Hosts/products own composition.

Host responsibilities may include:

- selecting enabled plugins;
- providing OS/device adapters and permissions;
- wiring UI/product flows;
- deployment/runtime packaging;
- host-specific policy where kernel/plugin contracts intentionally stop.

A host-specific requirement is not evidence for a kernel primitive.

MindForge-Mobile is one such optional host/product branch. Other hosts can exist without changing this rule.

## 12. PPF placement decision

PPF is an optional MindForge extension/plugin, not a kernel subsystem and not a MindForge-Mobile subsystem.

```text
MindForge Host
    |
    +-- MindForge Kernel
    |      |
    |      +-- MindForge Model
    |
    +-- optional PPF Extension
```

PPF owns personal-pattern feature semantics and mechanisms.

The kernel must not acquire PPF-specific concepts merely to integrate PPF.

If PPF later identifies a missing capability:

```text
PPF needs capability X
       |
       v
Can X remain inside PPF?
       | yes
       +--> keep X in PPF
       |
       no
       v
Is X host/platform-specific?
       | yes
       +--> Host / Adapter
       |
       no
       v
Is X fundamentally learned/generalizable?
       | yes
       +--> separate Model-level research
       |
       no / runtime concern
       v
Does X pass KAT-1..KAT-5?
       | no
       +--> redesign boundary / keep outside kernel
       |
       yes
       v
separate kernel-primitive proof + architecture decision
```

PPF research never self-authorizes a kernel or model change.

## 13. Consequence for the PPF research ladder

The PPF research ladder remains independent until feasibility is established:

```text
L1 semantic foundation
 -> L2 event foundation
 -> L3 benchmark
 -> L4 minimal baselines
 -> L5 minimum missing mechanism
 -> PPF feasibility decision
```

After feasibility:

```text
PPF feasibility decision
 -> PPF plugin/extension contract
 -> classify each required capability as Model / Kernel / Plugin / Host
 -> apply KAT to any kernel candidate
 -> separately prove any Model-level change
 -> reference integration
 -> optional host validation
```

Default expectation: **zero kernel changes and zero model changes unless evidence proves they are necessary**.

## 14. Architectural risks and countermeasures

### Risk A — Kernel becomes a feature registry

If each plugin need becomes a new kernel primitive, kernel size scales with product breadth.

Countermeasure: feature-specific semantics remain plugins; KAT must reject convenience-driven admission.

### Risk B — Plugin architecture becomes a dumping ground

Different plugins may duplicate truly generic lifecycle/state/isolation machinery.

Countermeasure: repeated generic need is evidence to investigate a universal primitive, not permission to copy indefinitely.

### Risk C — Model and runtime semantics are confused

A learned capability may be manually hard-coded, or a deterministic correctness boundary may be delegated to probabilistic model behavior.

Countermeasure: run the Model/Kernel/Plugin/Host placement decision tree before implementation.

### Risk D — `Optional plugin` hides hard coupling

Core behavior may silently assume a plugin exists.

Countermeasure: future kernel tests must include plugin-absent operation.

### Risk E — Over-general plugin framework

A universal marketplace/runtime may be designed before real extension needs exist.

Countermeasure: define only the smallest generic boundary justified by independently proven extensions.

### Risk F — Host-specific needs leak into core

Mobile/device concerns may pressure the kernel.

Countermeasure: keep them in Host/Adapter unless a separately proven universal primitive passes KAT.

## 15. Non-decisions

This decision does not yet choose:

- plugin loading mechanism;
- in-process vs out-of-process plugins;
- IPC/RPC mechanism;
- package format;
- service discovery;
- dependency-injection framework;
- lifecycle API;
- version negotiation;
- sandboxing/security model;
- plugin marketplace;
- PPF runtime API;
- any concrete kernel primitive;
- any concrete model modification.

These require separate evidence and authorization.

## 16. Mandatory read rule for future work

Any future Codex task that may affect PPF integration, MindForge model/kernel boundaries, extension/plugin architecture, host composition, or a proposed kernel/model capability **must fetch and read this document completely before planning or modifying code/docs**:

```text
docs/research/mindforge-architecture-invariants.md
```

The task must explicitly acknowledge:

```text
Model != Kernel.
The Model owns learned representations/capabilities.
The Kernel owns only proven universal primitives.
Plugins own feature-specific mechanisms and semantics.
Hosts own composition.
MindForge-Mobile is an optional host, not the architectural center.
PPF is an optional MindForge extension/plugin.
Any proposed kernel addition must pass KAT-1..KAT-5.
PPF work cannot self-authorize kernel or model changes.
```

If requested work conflicts with these invariants, Codex must stop the conflicting scope and report the conflict rather than silently changing architecture.

## 17. Decision status

```text
D1 MindForge-Mobile is an optional host/product branch: ACCEPTED
D2 Model and Kernel are distinct architectural roles: ACCEPTED
D3 Kernel is independent/minimal and owns only proven universal primitives: ACCEPTED
D4 Feature-specific mechanisms and semantics belong to plugins by default: ACCEPTED
D5 Hosts own composition and platform integration: ACCEPTED
PPF placement as optional extension/plugin: ACCEPTED
Kernel Admission Test KAT-1..KAT-5: REQUIRED
```

These decisions remain frozen until an explicit architecture-review task revises them with evidence.
