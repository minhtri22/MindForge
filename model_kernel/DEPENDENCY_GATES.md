# Model Kernel Dependency Gates

Status: **MK-0 FROZEN**

## 1. Purpose

This file defines when later Model Kernel phases may be designed, frozen, or executed.

The goal is to minimize duplicated scientific workload by allowing upstream research to eliminate unnecessary downstream experiments before expensive model training begins.

General policy:

~~~
parallelize analysis/protocol work
serialize expensive evidence
~~~

A dependency may be:

- **HARD** — phase execution is forbidden until satisfied;
- **SOFT-TO-EXECUTION** — design discussion may proceed, but final protocol freeze/training waits for upstream adjudication because the result can materially reduce workload;
- **NONE** — upstream branch is scientifically independent of this phase.

## 2. Global gates

Every Model Kernel scientific phase must satisfy all of the following before execution.

### G-MK-1 — Exact upstream re-audit

Re-read the latest source branch, append-only lineage, protocol, closure/adjudication artifact, and exact result state for every dependency named by that phase.

A status copied from MK-0 is not enough because upstream branches continue evolving.

### G-MK-2 — Prospective protocol

Freeze before scientific outcome:

- hypothesis;
- intervention;
- baselines;
- independent/dependent variables;
- data split;
- seed policy;
- parameter/compute matching;
- primary metrics;
- practical-effect thresholds;
- falsification conditions;
- stopping rules;
- evidence/provenance contract.

### G-MK-3 — One major causal variable

The primary study must not introduce multiple unproven mechanisms whose effects cannot be attributed separately.

### G-MK-4 — Fresh confirmatory evidence

Development/validation data used to design an intervention may not also serve as the final confirmatory set.

### G-MK-5 — No inherited-result substitution

Upstream evidence may motivate the study but cannot count as the Model Kernel result.

### G-MK-6 — B0 reconstruction

BASELINE_CONTRACT.md preflight must pass on the exact experiment branch.

### G-MK-7 — No hidden scope expansion

A phase may not silently add memory, continual learning, invariance objectives, sparse routing, runtime optimization, or other later mechanisms.

## 3. MK-1 — Learned Decision-State Representation

Target question:

> Can the compact MindForge model learn a structured decision-relevant representation from current observation/context that generalizes better than the relevant deterministic/direct baselines?

### Inputs

MK-1 is memory-free.

Allowed:

- current observation;
- current task/context;
- current belief/state when prospectively defined.

Forbidden:

- episodic retrieval;
- historical precedent;
- retrieved examples;
- memory-conditioned context.

### Dependencies

**PIT-19 — HARD scientific motivation already satisfied at MK-0 audit.**

Required transferable fact: pristine held-out deterministic representation showed a meaningful generalization bottleneck in its tested scope.

**CQG H-Q1/H-Q2 — HARD scientific motivation already satisfied at MK-0 audit.**

Required transferable fact: decision-relevant TaskState materially improved information-need ranking in the controlled benchmark and survived the specified frozen shifts.

**CQG J3.13 — FORMALLY CLOSED.**

CQG now contains the confirmatory report, finalized provenance, formal-result commit, and append-only lineage evidence for `CARDINAL_IDENTIFIABLE_BUT_CURRENT_LEARNER_CONTRACT_INSUFFICIENT`.

Scientific consequence:

- remove scalar/cardinal repair from the primary MK-1 question;
- do not add J3.13 G1/R2/RG merely to repeat its mechanism discrimination;
- strict observable cardinal nonidentifiability is not an admissible explanation under the tested contract.

**CQG J3.14 — SOFT-TO-EXECUTION, promoted to the current MK-1 workload-minimization gate.**

J3.14 prospectively distinguishes three explanations left by J3.13 using fresh data:

- H_DATA2X — sample/data limitation;
- H_CLASS — learner function-class / inductive-bias mismatch on the same R2/asinh representation;
- H_COMPOSITION — need for an explicit per-hypothesis compositional/contraction basis.

At the latest audit, corrected run `35453882566` is still in progress. Integrity, all fresh train/confirmatory collection jobs, freeze, and the C240 structured arm have completed successfully; other arm fitting remains unfinished.

Scientific consequence for Model Core:

- do not freeze a latent/compositional MK-1 architecture before J3.14 adjudication;
- if data doubling alone succeeds, avoid inventing extra model structure to solve a sample-size problem;
- if the function-class arm succeeds, prioritize learner/inductive-bias transfer tests over schema expansion;
- if only the explicit compositional arm succeeds, an explicit compositional-bias hypothesis becomes justified for a later Model Core study;
- if none succeeds, do not repeat the same remedies in MK-1 without a new substrate-specific hypothesis.

Conceptual MK-1 protocol work may continue, but final arm selection, preregistration freeze, and training remain blocked until J3.14 formal adjudication is reviewed.

### Opening rule

MK-1 may be formally opened only after:

1. J3.13 formal upstream report/lineage closure after the already-reviewed execution result;
2. a frozen MK-1 protocol;
3. B0 reconstruction;
4. clean fresh data/seed split;
5. no memory mechanism included.

## 4. MK-2 — Decision Sufficiency

Target question:

> Does the frozen representation produced by MK-1 actually preserve/improve the information needed for downstream typed/ranking decisions?

### HARD dependencies

- MK-1 must close with a supported representation result.
- The MK-1 encoder/representation contract must be frozen before MK-2 learner fitting.
- CQG Q1/Q2 evidence must be re-audited for task/metric transfer design.
- J3.13 is closed; J3.14 must also be reviewed if MK-2 design would inherit its function-class/compositional conclusions.

### Required isolation

MK-2 must compare representations using the same downstream learner family/capacity whenever feasible.

The MK-1 encoder must not be jointly fine-tuned from MK-2 outcome during the primary sufficiency test.

### Stop rule

If MK-1 fails its primary representation gate, MK-2 is not opened.

## 5. MK-3 — Typed Decision / Joint Optimization

This phase is optional.

Potential scope:

- typed classification/ranking heads;
- ASK/ABSTAIN-like decisions;
- end-to-end representation + decision optimization after frozen sufficiency evidence exists.

### HARD dependencies

- MK-2 PASS or a new independently justified hypothesis;
- frozen decision target and baseline;
- no episodic memory unless MK-M1 has separately authorized it.

MK-3 is not automatically required after MK-2.

## 6. MK-4 — Cardinal Value / Calibration

Potential question:

> Can a model estimate calibrated/cardinal decision value, not merely ordering?

### HARD dependencies

- CQG J3.13 final adjudication;
- latest CQG lineage review for any downstream follow-up that supersedes J3.13;
- an already supported ranking/decision representation in Model Kernel.

### Prohibited shortcut

Strong Spearman/ranking or retained-value performance may not be used as evidence of cardinal calibration.

## 7. MK-5 — Continual Learning

Potential scope:

- stability/plasticity;
- optimizer/boundary-state transfer;
- replay/update policies;
- retention/forgetting under the Model Kernel representation.

### HARD dependencies

- relevant KCL frontier chain must be scientifically closed enough to state what is supported, falsified, and still pending;
- KCL findings must be requalified on the Model Kernel substrate before any KCL-derived controller is adopted;
- model representation used by MK-5 must already be frozen.

### Default rule

Import KCL **questions and diagnostics first**, not controllers.

## 8. MK-6 — Invariance / Counterfactual Representation

Potential scope:

- learned invariant representation;
- counterfactual consistency;
- invariant regularization/objectives.

### HARD dependencies

- relevant OIR-PPV invariant target/validation chain must have a closed transferable result;
- exact invariant definition and nuisance/context boundary must be frozen prospectively;
- no OIR-PPV harness result may be treated as proof that a neural invariant objective will work.

## 9. MK-M1 — Memory Admission

This is a separate branch of model science, not part of MK-1/MK-2.

Potential question:

> Should retrieved episodic memory be admitted into reasoning/model state, and can its causal utility be predicted better than spending the same budget on additional reasoning?

### HARD dependency

ARN R3 must close with a confirmatory adjudication or an explicit scientific stop.

Decision consequences:

- **H3-A fails:** do not open a learned memory-utility controller from this evidence line.
- **H3-A passes but ORACLE_ROUTE <= NM2:** memory-specific control lacks demonstrated practical headroom; do not build a controller without a new hypothesis/task family.
- **ORACLE_ROUTE > NM2 but ROUTE <= NM2:** assessor/controller quality becomes a justified model research target.
- **ROUTE > NM2 by frozen criterion:** open only a transfer-qualification study; do not rediscover the entire ARN mechanism tree.

Until this gate is satisfied, feeding retrieved episodic memory into the MK-1/MK-2 representation is forbidden.

## 10. MK-7 — Systems / Runtime Interaction

Potential scope:

- conditional computation;
- sparse activation;
- runtime/model interaction;
- ArcLLM/NEXUS deployment studies.

### HARD dependencies

1. Model Kernel must first demonstrate a learned mechanism that actually creates conditional/sparse work.
2. Latest canonical NEXUS H2 status must be adjudicated/reviewed.
3. If event-ledger or another noncanonical NEXUS scheduler is proposed, that mechanism must have its own closed evidence chain.
4. Runtime gains must be evaluated separately from model-quality gains.

NEXUS or ArcLLM may not determine the early model architecture merely because a runtime can execute some structure efficiently.

## 11. Current activation matrix

| Phase | Status after MK-0 | Blocking dependency |
|---|---|---|
| MK-0 | COMPLETE / FROZEN | none |
| MK-1 | NOT OPENED | CQG J3.14 formal adjudication + prospective MK-1 protocol |
| MK-2 | BLOCKED | MK-1 supported/frozen |
| MK-3 | BLOCKED / OPTIONAL | MK-2 |
| MK-4 | BLOCKED | CQG J3.13/J3.14 + supported Model Kernel decision representation |
| MK-5 | BLOCKED | relevant KCL closure + Model Kernel substrate |
| MK-6 | BLOCKED | relevant OIR-PPV closure |
| MK-M1 | BLOCKED | ARN R3 confirmatory closure/stop |
| MK-7 | BLOCKED | model conditional-work evidence + NEXUS/runtime closure |

## 12. Governance amendment rule

A dependency may be removed or weakened only by appending a lineage entry that explains:

- why the dependency is scientifically independent;
- what workload/result uncertainty is no longer relevant;
- what new leakage/confounding risk is introduced;
- which protocol gates replace the old dependency.

No dependency may disappear merely for schedule convenience.