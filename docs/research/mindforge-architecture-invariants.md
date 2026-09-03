# MindForge Architecture Invariants

Status: **ARCHITECTURE DECISION / FROZEN UNTIL EXPLICITLY REVISED**

Decision scope: MindForge core architecture, extensions/plugins, PPF placement, and host/product composition.

## 1. Decisions

### D1 — MindForge-Mobile is not the architectural center

MindForge-Mobile is one optional host/product branch of MindForge. It is not the primary architecture and must not become the place where cross-cutting MindForge capabilities are anchored by default.

A capability that is useful beyond one host must not be defined as a MindForge-Mobile feature merely because mobile is a convenient validation environment.

PPF therefore must not be architected as a MindForge-Mobile subsystem. MindForge-Mobile may later consume PPF, but only as one optional host/consumer.

### D2 — Kernel is an independent minimal core; feature capabilities live outside it

The MindForge kernel is an independently operable minimal core.

Domain-specific, product-specific, optional, or independently evolvable capabilities belong outside the kernel behind extension/plugin contracts.

The architectural direction is:

```text
MindForge Kernel
    |
    +-- stable generic extension/service boundary
            |
            +-- optional extension/plugin A
            +-- optional extension/plugin B
            +-- PPF extension/plugin
            +-- ...

Hosts/products compose the kernel with the extension set they require.
```

This yields the shorthand:

```text
Kernel owns primitives.
Plugins own features.
Hosts own composition.
```

## 2. Important qualification: "feature outside core" is not absolute

The kernel is not required to be artificially empty.

A capability may belong in the kernel if it is a genuinely generic primitive required for core correctness or for a stable extension runtime and cannot be cleanly externalized without violating the core boundary.

Therefore the architecture is **not**:

```text
everything except a tiny dispatcher must be a plugin
```

The architecture is:

```text
domain/product/optional capability -> plugin by default
universal minimal primitive -> kernel only after explicit admission proof
```

This qualification prevents "minimal kernel" from becoming an underpowered kernel that pushes generic invariants into every plugin repeatedly.

## 3. Kernel invariants

The following are architecture invariants unless explicitly revised by a later architecture decision.

1. **Independent operation** — the kernel must be able to operate without any specific optional plugin installed.
2. **No plugin-specific dependency** — kernel code must not import, name, or require a specific feature plugin.
3. **Generic contracts only** — extension boundaries exposed by the kernel must use generic contracts rather than domain-specific feature semantics.
4. **Minimality** — a primitive enters the kernel only when evidence shows that keeping it outside would violate a generic correctness, lifecycle, isolation, or runtime requirement.
5. **Plugin replaceability** — removing or replacing one optional plugin must not invalidate unrelated kernel operation.
6. **Composition outside the kernel** — hosts/products choose which optional extensions are enabled.
7. **Failure isolation goal** — a plugin failure should be containable without redefining kernel semantics; exact runtime isolation mechanics remain a later implementation decision.
8. **Independent evolution** — plugin implementation details may evolve without forcing kernel redesign when the generic contract remains stable.

## 4. Kernel Admission Test

Before moving any capability into the kernel, the proposal must answer all of the following.

### KAT-1 — Genericity

Is the capability independent of a specific domain, feature, product, or host?

If NO -> plugin territory.

### KAT-2 — Reuse / core necessity

Is the capability required by the core itself or broadly useful across multiple independently plausible extensions?

If NO -> plugin territory by default.

### KAT-3 — Externalization test

Can the capability live outside the kernel behind a stable contract without breaking correctness, lifecycle guarantees, isolation, or an essential runtime boundary?

If YES -> keep it outside the kernel.

### KAT-4 — Contract stability

Can the kernel-facing abstraction be defined without importing the semantics of one particular plugin?

If NO -> do not admit the feature-specific abstraction into the kernel.

### KAT-5 — Evidence

Is there measured or demonstrated evidence that the primitive is necessary in the kernel rather than merely convenient there?

If NO -> defer admission.

A proposed kernel addition should pass all five tests before implementation is authorized.

## 5. Plugin / Extension invariants

An extension/plugin:

- owns feature-specific semantics and state;
- may depend on stable generic kernel contracts;
- must not require the kernel to know its domain vocabulary;
- should expose a bounded contract to hosts/other authorized consumers;
- should preserve its own validation, lifecycle, and feature-specific correctness rules;
- may be optional for a host/product;
- should not gain kernel status merely because it becomes important or widely used.

"Important" is not the same as "core".

## 6. Host / Product responsibility

Hosts/products own composition.

Examples of host responsibility include:

- selecting enabled plugins;
- providing host-specific adapters or permissions;
- wiring UI/product flows;
- deciding deployment/runtime packaging;
- applying host-specific policy where the kernel/plugin contracts deliberately do not.

A host must not be used as an excuse to move host-specific logic into the kernel.

MindForge-Mobile is one such host/product branch. Other hosts may exist without changing this architecture rule.

## 7. PPF placement decision

PPF is an optional MindForge extension/plugin, not a kernel subsystem and not a MindForge-Mobile subsystem.

The intended future relationship is:

```text
MindForge Kernel
      |
      +-- generic extension boundary
               |
               +-- PPF Extension

MindForge-Mobile (optional host)
      |
      +-- MindForge Kernel
      +-- optionally enables/consumes PPF Extension
```

PPF owns personal-pattern feature semantics.

The kernel must not acquire PPF-specific concepts such as personal-pattern recognition merely to integrate PPF.

If later PPF work identifies a missing capability, the decision path is:

```text
PPF needs capability X
       |
       v
Can X remain entirely inside PPF?
       | yes
       +--> keep X in PPF
       |
       no
       v
Does X pass KAT-1..KAT-5 as a generic kernel primitive?
       | no
       +--> redesign extension boundary / keep feature-specific logic outside
       |
       yes
       v
separate kernel-primitive proof and architecture decision
```

PPF research does not itself authorize a kernel change.

## 8. Consequence for the PPF research ladder

The PPF research ladder remains independent until feasibility is established.

```text
L1 semantic foundation
 -> L2 event foundation
 -> L3 benchmark
 -> L4 minimal baselines
 -> L5 minimum missing mechanism
 -> PPF feasibility decision
```

After that, the default integration path is:

```text
PPF feasibility decision
 -> PPF plugin/extension contract
 -> evaluate required generic MindForge capabilities
 -> apply Kernel Admission Test to any proposed kernel primitive
 -> reference integration
 -> optional host validation
```

The default outcome should be **zero kernel changes** unless evidence demonstrates a genuinely generic missing primitive.

## 9. Architectural risks and countermeasures

### Risk A — Plugin architecture becomes a dumping ground

If every cross-cutting concern is pushed into plugins, different plugins may duplicate generic lifecycle, scheduling, state, or isolation machinery.

Countermeasure: use the Kernel Admission Test. Repeated generic need is evidence to investigate a kernel primitive, not permission to copy infrastructure everywhere.

### Risk B — Kernel grows through convenience

A feature can be moved into core because direct access is easier or faster to implement.

Countermeasure: convenience is not evidence. Kernel admission requires genericity, externalization failure, stable abstraction, and demonstrated necessity.

### Risk C — "Optional plugin" hides hard coupling

A plugin may be called optional while core behavior quietly assumes it exists.

Countermeasure: kernel tests must eventually include operation with the plugin absent. Exact tests belong to later implementation work.

### Risk D — Overly generic extension API

Designing a universal plugin framework too early can become architecture speculation.

Countermeasure: define the smallest generic boundary required by independently proven extensions. Do not build a general marketplace/plugin ecosystem without evidence.

### Risk E — Host-specific needs leak into core

Mobile permissions, UI lifecycle, device adapters, or product flows may pressure the kernel boundary.

Countermeasure: host-specific concerns remain host/adapters unless a separately proven generic primitive passes the Kernel Admission Test.

## 10. Non-decisions

This architecture decision does **not** yet choose:

- plugin loading mechanism;
- in-process vs out-of-process plugins;
- IPC/RPC mechanism;
- plugin package format;
- service discovery;
- dependency injection framework;
- lifecycle API;
- version negotiation;
- sandboxing/security model;
- plugin marketplace;
- PPF runtime API;
- any concrete kernel change.

Those require separate evidence and authorization.

## 11. Mandatory read rule for future work

Any future Codex task that may affect PPF integration, MindForge kernel boundaries, extension/plugin architecture, host composition, or a proposed kernel capability **must fetch and read this document before planning or modifying code/docs**:

```text
docs/research/mindforge-architecture-invariants.md
```

The task must explicitly acknowledge these invariants before execution:

```text
Kernel = independent minimal core.
Domain/product/optional features = plugins/extensions by default.
Hosts own composition.
MindForge-Mobile is an optional host, not the architectural center.
PPF is an optional MindForge extension/plugin.
Any proposed kernel addition must separately pass KAT-1..KAT-5.
```

If a requested task conflicts with these invariants, Codex must stop that conflicting scope and report the conflict rather than silently changing the architecture.

## 12. Decision status

```text
D1 MindForge-Mobile is an optional host/product branch: ACCEPTED
D2 Kernel independent; feature capabilities outside core by default: ACCEPTED WITH QUALIFICATION
PPF placement as optional extension/plugin: ACCEPTED
Kernel Admission Test KAT-1..KAT-5: REQUIRED FOR FUTURE KERNEL CHANGES
```

These decisions remain frozen until an explicit architecture-review task revises them with evidence.
