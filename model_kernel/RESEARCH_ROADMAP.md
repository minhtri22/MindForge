# Model Kernel Research Roadmap

Status: **MK-0 FROZEN ROADMAP**

## 1. Program strategy

Model Kernel is an evidence-gated model-science track.

The program does **not** attempt to combine all existing MindForge/CQG/ARN/NEXUS findings into one architecture.

Instead:

~~~
upstream result
    |
    v
new falsifiable model hypothesis
    |
    v
one controlled intervention
    |
    v
fresh evidence
~~~

Expensive scientific execution is serialized. Protocol analysis and dependency monitoring may proceed in parallel.

## 2. Phase map

~~~
MK-0  Governance / provenance
  |
  v
MK-1  Learned Decision-State Representation
  |
  v
MK-2  Decision Sufficiency
  |
  v
MK-3  Typed Decision / Joint Optimization      [optional]
  |
  v
MK-4  Cardinal Value / Calibration             [dependency-gated]

Independent later branches:
  MK-5   Continual Learning                     [KCL-gated]
  MK-6   Invariance / Counterfactual Learning   [OIR-gated]
  MK-M1  Memory Admission                       [ARN-gated]
  MK-7   Systems / Runtime Interaction          [NEXUS/runtime-gated]
~~~

No arrow means automatic authorization. DEPENDENCY_GATES.md is authoritative.

## 3. MK-0 — Governance and baseline

**Status:** COMPLETE / FROZEN after creation of the six MK-0 documents.

Purpose:

- preserve MKS-1 Model/Kernel separation;
- freeze B0;
- record scientific inheritance;
- record pending dependencies;
- prevent cross-branch semantic combination from becoming untested architecture;
- define when future phases may open.

Scientific outcome:

**None.**

No model is trained in MK-0.

## 4. MK-1 — Learned Decision-State Representation

**Status:** PREREGISTERED / ZERO-SCIENCE QA PASS; IMPLEMENTATION AND TRAINING NOT AUTHORIZED.

### Question

Can MindForge learn a structured, decision-relevant internal representation from **current** raw observation/context that generalizes beyond deterministic and matched direct learned baselines?

### Upstream narrowing now closed for MK-1

- PIT-19 provides pristine negative evidence against further blind deterministic rule accumulation.
- CQG Q1/Q2 supports the usefulness of explicit decision-relevant state in its controlled substrate.
- CQG J3.12/J3.13 separates strong ranking from poor generic cardinal fidelity and rules out strict observable nonidentifiability in that tested setup.
- CQG J3.14 rejects data-doubling and generic function-class rescue under its frozen gates.
- CQG J3.15 shows the structured arm's raw-Spearman failure is a near-tie/numerical pathology, not material-order failure.
- CQG J3.16 formally supports structured observable ECV on a fresh cohort.
- KCL-6.5.9.x formally converged: real structural heterogeneity does not guarantee predictability from current observables, hard labels can hide mechanisms, and repeated representation rescue without a new uncertainty must stop.

CQG J3.17+ resource-controller studies and KCL post-convergence pivots are downstream/separate and do not block MK-1 representation specification.

### Frozen MK-1 v0.1 scope

MK-1 is memory-free and representation-only.

The preregistered target is:

~~~
current raw input
    |
    v
shared B0 Transformer
    |
    +--> Z1 semantic primitives
    +--> Z2 normalized arguments
    +--> Z3 scope state
    +--> Z4 support/composition relations
~~~

Final action labels, scalar utility, memory, continual-learning control, resource control, invariance objectives, sparse routing, and runtime optimization are excluded.

### Frozen comparison set

Exactly:

- B0-DIRECT — matched learned monolithic/direct representation;
- D-PIT — frozen deterministic PIT-v3 comparator;
- M1-Z — learned structured/factorized representation.

No latent rescue arm is authorized in MK-1 v0.1.

### Preconditions before implementation/training

Already satisfied:

- target ontology frozen;
- target-margin/stability audit contract frozen;
- observable-identifiability contract frozen;
- structured/factorized Z schema frozen;
- baseline/capacity/compute matching frozen;
- fresh/pristine split and falsification rules frozen;
- zero-science QA PASS.

Still required:

- exact B0 reconstruction PASS;
- implementation lock binding code/data structures to the frozen specification;
- zero-fresh preflight PASS.

### Stop logic

A valid MK-1 failure is not followed by automatic feature/history/capacity expansion. A new attempt requires a new preregistered scientific uncertainty.

A full MK-1 PASS authorizes only designing MK-2 Decision Sufficiency. It does not authorize a controller.

## 5. MK-2 — Decision Sufficiency

**Status:** BLOCKED by MK-1.

### Question

Does the frozen MK-1 state preserve or improve the information required for downstream typed/ranking decisions?

### Core design

Freeze MK-1 representation first.

Then compare:

~~~
raw/direct representation -> same downstream learner
deterministic state        -> same downstream learner
MK-1 learned state         -> same downstream learner
~~~

The downstream learner family/capacity should be matched whenever feasible.

### Candidate endpoints

Depending on the final task contract:

- candidate ranking;
- top-k selection;
- retained attainable value;
- positive-value selection;
- distractor robustness;
- intervention sensitivity.

### Key prohibition

Do not jointly fine-tune MK-1 representation and the downstream decision learner in the primary MK-2 sufficiency test.

That would collapse representation quality and decision-model capacity into one intervention.

## 6. MK-3 — Typed Decision / Joint Optimization

**Status:** OPTIONAL / BLOCKED.

Open only if MK-2 establishes a useful representation or a new hypothesis independently justifies joint learning.

Possible questions:

- Can typed decisions be learned end-to-end without losing the representation/generalization properties established in MK-1/MK-2?
- Can the model produce bounded outputs such as candidate choice, ASK/ABSTAIN, or other typed actions more reliably than generation-first interfaces?

Potential objective family:

~~~
representation objective
+
typed/ranking decision objective
~~~

Exact losses are not authorized by MK-0.

If MK-2 already provides sufficient performance with a simple frozen-state learner, MK-3 may be unnecessary.

## 7. MK-4 — Cardinal Value / Calibration

**Status:** BLOCKED.

This phase is intentionally downstream because CQG has shown a stable separation between strong ranking and poor absolute value fidelity under its tested learner contract.

Potential questions:

- Can MindForge learn calibrated probability/value in absolute units?
- Does a representation or target-geometry change improve cardinal fidelity without degrading ranking?
- Is calibration useful enough to justify threshold/resource interfaces?

J3.13 is formally closed and narrows the mechanism: strict cardinal nonidentifiability is falsified in that setup, while the tested frozen learner contract remains insufficient. J3.14 is the current upstream mechanism-qualification study for data quantity versus learner class versus explicit compositional bias. MK-4 waits for J3.14 adjudication and for Model Core to establish a supported ranking/decision representation.

A ranking PASS never counts as calibration PASS.

## 8. MK-5 — Continual Learning

**Status:** BLOCKED by KCL dependency.

Purpose:

Qualify how an already-supported Model Kernel representation behaves under sequential learning.

Potential questions:

- stability vs plasticity;
- forgetting/retention;
- optimizer boundary-state effects;
- replay/update selection;
- whether KCL-observed regime heterogeneity transfers to the new model substrate.

Strategy:

1. port the frozen model mechanism into a KCL-style harness;
2. test transfer of upstream phenomena;
3. only then consider KCL-derived adaptive mechanisms.

Do not import a controller first and test it afterward.

## 9. MK-6 — Invariance / Counterfactual Learning

**Status:** BLOCKED by OIR-PPV dependency.

Potential question:

Can an already-useful decision representation become more stable under context/nuisance changes through a prospectively defined invariance objective?

Possible later form:

~~~
task objective
+
invariance/counterfactual objective
~~~

No invariant head/loss is authorized until the relevant OIR-PPV target and boundary are scientifically closed enough to transfer.

## 10. MK-M1 — Memory Admission

**Status:** BLOCKED by ARN R3.

This is separate from MK-1/MK-2.

Potential question:

Can the model estimate the causal utility of retrieved episodic memory before that memory is allowed to influence reasoning/state, and does the controller beat equal-cost extra reasoning?

The exact direction depends on ARN R3 closure:

- no heterogeneous utility -> stop memory-controller line;
- heterogeneous utility but no oracle headroom -> stop unless new task-family hypothesis exists;
- oracle headroom but assessor failure -> learned/internal memory-utility representation becomes justified;
- deployable ARN route PASS -> perform transfer qualification rather than rediscovery.

Until then, MK-1/MK-2 remain memory-free.

## 11. MK-7 — Systems / Runtime Interaction

**Status:** BLOCKED.

This phase is not a model-architecture starting point.

Open only when:

1. a supported model mechanism creates measurable conditional/sparse work; and
2. NEXUS/ArcLLM or another runtime has a sufficiently closed mechanism relevant to that workload.

Possible later factorial question:

~~~
baseline model × baseline runtime
conditional model × baseline runtime
baseline model × sparse/optimized runtime
conditional model × sparse/optimized runtime
~~~

This is where model/runtime interaction becomes a scientific variable.

Runtime speedup alone is not a model-quality result.

## 12. Workload minimization rules

The roadmap explicitly prefers **not running an experiment** when upstream evidence has already made the answer unnecessary.

Examples:

- if CQG resolves a candidate cardinal mechanism cleanly, do not repeat all rejected mechanism arms in MindForge;
- if MK-1 typed representation is sufficient and robust, do not automatically add a latent variant;
- if KCL falsifies a fixed boundary policy and the relevant finding transfers, do not rerun that policy as a serious candidate;
- if ARN shows no practical oracle headroom for memory control, do not build a learned memory controller;
- if NEXUS rules out a runtime mechanism in the relevant regime, do not make that mechanism a model-design requirement.

A downstream replication is justified only when the model substrate change itself is the scientific question.

## 13. Evidence status vocabulary

Future roadmap entries should use:

- **NOT OPENED**
- **PREREGISTERED**
- **IMPLEMENTED / NO OUTCOME**
- **PILOT / INSTRUMENT ONLY**
- **CONFIRMATORY PASS**
- **CONFIRMATORY FAIL**
- **UNRESOLVED**
- **STOP**
- **CLOSED**

Do not replace these with vague progress labels.

## 14. Immediate next action

MK-1 preregistration is frozen and zero-science QA has passed.

Next:

~~~
1. do not materialize scientific data;
2. do not train;
3. reconstruct exact B0 source/config/runtime/checkpoint state;
4. prove B0-DIRECT and M1-Z can satisfy the frozen parameter/compute matching contract;
5. freeze the implementation mapping and exact hashes;
6. run zero-fresh implementation preflight;
7. only after all of the above PASS may fresh data materialization and training be authorized.
~~~

CQG J3.17+ resource-controller work, KCL post-convergence pivots, ARN memory work, OIR invariance work, and NEXUS runtime work remain separate later-phase dependencies and do not block this preflight sequence.