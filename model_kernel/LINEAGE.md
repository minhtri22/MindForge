# MindForge Model Kernel Lineage

> **APPEND-ONLY SCIENTIFIC RECORD**
>
> After the MK-0 initialization commit sequence, historical entries in this file must not be edited, reordered, deleted, compressed, or silently reinterpreted. Corrections must be appended as new entries.

## Entry schema

Each future entry should record:

- date;
- phase / step;
- question;
- upstream dependencies inspected;
- frozen hypothesis or governance decision;
- evidence;
- result;
- gate;
- scientific consequence;
- next authorized step;
- provenance.

---

## MK0-000 — Model-level research track opened

**Date:** 2026-09-19  
**Phase / Step:** MK-0 — Governance initialization  
**Question:** Can MindForge open a model-level research track without changing the frozen Model/Kernel architecture or prematurely importing mechanisms from other research branches?

**Architectural parent:** current state of branch **refactor/mks-1-model-kernel-separation** at Model Kernel branch creation.

**Parent architectural evidence:**

- docs/research/model-kernel-separation-closure.md — **MKS-1 PASS / CLOSED — FULL LOCAL EVIDENCE VALIDATED**;
- docs/research/mindforge-architecture-invariants.md — Model and Kernel are distinct architectural roles;
- docs/research/model-contract-adr.md — TokenModel is a bounded PyTorch runtime contract v0, not a universal model ABI.

**Decision:** Open **research/model_kernel** as a learned-model research track only.

**Boundary:** "Model Kernel" names the research track for the learned neural core and does not rename or redefine the MindForge Kernel runtime.

**Gate:** PASS — governance initialization only.

**Scientific impact:** None. No new model hypothesis has been tested.

**Next authorized step:** Build and freeze MK-0 governance documents only.

---

## MK0-010 — Cross-track evidence review recorded

**Date:** 2026-09-19  
**Phase / Step:** MK-0 — Inheritance review  
**Question:** Which existing research results can constrain or motivate later Model Kernel studies without being mistaken for model-level evidence?

### MindForge PIT

PIT-19 pristine held-out validation produced the frozen verdict:

**DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED**

The dominant observed errors were upstream representation-acquisition failures rather than downstream Guardrail-policy errors.

**Use in Model Kernel:** motivates a prospective learned-representation study.

**Not inherited:** no claim that a neural representation already solves PIT generalization.

### CQG

Frozen upstream evidence includes:

- H-Q1 PASS: explicit TaskState materially improved WHAT-to-ask selection versus DirectContext and non-semantic baselines in the controlled benchmark;
- H-Q2 PASS: the frozen TaskState selector retained most attainable question value across five preregistered shifts;
- J3.12: target/validator integrity PASS and strong observable ranking, but **OBSERVABLE_ECV_ABSOLUTE_FIDELITY_FAILURE**;
- J3.13: prospectively designed mechanism discrimination was preregistered/implemented at the audit point but had no inspected fresh-seed outcome.

**Use in Model Kernel:** motivates decision-relevant intermediate state and warns against assuming that ranking learnability implies calibrated/cardinal-value learnability.

**Not inherited:** no CQG learner is automatically a MindForge model component.

### MindForge KCL

KCL provides learning-dynamics and continual-learning evidence, including optimizer/boundary-state effects and failures of several fixed/coarse boundary representations.

At the audit point, KCL-6.5.9.2 had a trained/frozen regime-predictor artifact but validation evidence had not yet been completed.

**Use in Model Kernel:** later continual-learning diagnostics and transfer questions.

**Not inherited:** no adaptive controller or predictor is admitted into the model before its relevant KCL chain closes and transfers prospectively.

### MindForge OIR-PPV

OIR-PPV provides invariant-oriented discovery, replay, falsification, provenance, and counterfactual methodology. Several frontier questions remain governed by their own closure/admission rules.

**Use in Model Kernel:** later invariance hypotheses and research methodology.

**Not inherited:** no invariant loss, invariant head, or latent mechanism is treated as established model architecture.

### ARN

ARN R1/R2 were downgraded by ARN's own audit to mechanism-discovery/hypothesis-generating evidence.

ARN R3 is the clean causal pivot using paired NONE / SHAM / HELP / HARM memory interventions and a cost-matched NM2 baseline.

At the audit point:

- first real-model pilot completed;
- the frozen difficulty gate required the single preregistered ceiling repair;
- R3 v1.3 was **READY_FOR_REPAIRED_REAL_PILOT**;
- no confirmatory R3 outcome existed.

**Use in Model Kernel:** hard dependency for any future model-level episodic-memory admission mechanism.

**Immediate consequence:** MK-1 and MK-2 remain memory-free.

### NEXUS

Canonical NEXUS evidence currently concerns semantic/runtime/sparse-execution systems questions. H2 remained unresolved at the audit point and R5 learnability was blocked.

The separate event-ledger branch had encouraging mechanism evidence at EL-L1 and ongoing representation/contention work, but canonical H2 impact remained NONE.

**Use in Model Kernel:** future execution substrate only after a model mechanism demonstrably creates conditional/sparse work.

**Not inherited:** entity/event-ledger structure is not a model architecture prior.

### Other MindForge tracks

PPF, Track-A, and teacher-learning work may supply semantic contracts, benchmarks, controlled tasks, or weak mechanism evidence as recorded in INHERITANCE_REGISTRY.md.

They do not self-authorize model changes.

**Gate:** PASS — evidence classified by transfer role.

**Scientific impact:** None. This is a governance classification, not a synthesis result.

**Next authorized step:** Freeze explicit inheritance and dependency rules.

---

## MK0-020 — MK-0 governance package frozen

**Date:** 2026-09-19  
**Phase / Step:** MK-0 — Governance closure

**Files authorized by MK-0:**

- model_kernel/CHARTER.md
- model_kernel/LINEAGE.md
- model_kernel/INHERITANCE_REGISTRY.md
- model_kernel/BASELINE_CONTRACT.md
- model_kernel/DEPENDENCY_GATES.md
- model_kernel/RESEARCH_ROADMAP.md

**Scope guard:** No model code, dataset, experiment, workflow, training run, memory integration, continual-learning mechanism, invariance mechanism, or systems integration is authorized by this closure.

**Decision:**

~~~
MK-0 = COMPLETE / GOVERNANCE FROZEN
MK-1 = NOT OPENED
MK-2 = NOT OPENED
MODEL TRAINING = NOT AUTHORIZED
~~~

**Next authorized work:** monitor upstream dependency closures and prepare prospective protocol text only when allowed by DEPENDENCY_GATES.md.

**Provenance:** this entry is frozen by the commit sequence that creates the MK-0 document set on branch **research/model_kernel**.

---

## MK0-030 — Research branch renamed to model_core

**Date:** 2026-09-19  
**Phase / Step:** MK-0 — Governance metadata correction  
**Change:** The active research branch was renamed logically from **research/model_kernel** to **research/model_core**.  
**Reason:** Avoid branch-name ambiguity with the frozen MindForge Kernel runtime concept while preserving the existing `model_kernel/` MK-0 document directory and all scientific content unchanged.  
**Scientific impact:** NONE. No hypothesis, baseline, dependency, gate, model code, dataset, experiment, or result changed.  
**Historical note:** Earlier lineage entries retain the original branch name because LINEAGE.md is append-only. This entry supersedes those branch-name references for all future work.  
**Active branch:** **research/model_core**.