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

**Status:** NOT OPENED.

### Question

Can MindForge learn a structured, decision-relevant internal representation from **current** observation/context that generalizes better than deterministic/direct representation baselines?

### Initial motivation

- PIT provides negative evidence that deterministic semantic representation can hit a pristine-heldout generalization bottleneck.
- CQG Q1/Q2 provides positive evidence that an explicit decision-relevant TaskState can materially improve ranking/selection and remain useful under specified shifts.
- CQG J3.12 warns that strong ranking does not imply cardinal calibration.

### Initial scope

Memory-free.

Candidate primary intervention:

~~~
current input
    |
    v
B0 Transformer
    |
    v
learned structured decision-state
~~~

The exact state schema, supervision, parameter matching, and baseline set are **not frozen in MK-0**.

### Candidate comparisons

To be prospectively selected after dependency re-audit:

- direct/raw B0 representation;
- deterministic PIT-style representation;
- learned structured/typed representation.

A latent+typed arm is not automatically required. It should be added only if upstream evidence or MK-1 results justify it prospectively.

### Primary result type

Representation generalization, not final end-to-end task success.

### Stop logic

A clean MK-1 failure should prevent automatic progression to MK-2 unless the failure itself supports a new preregistered representation hypothesis.

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

This phase waits for final CQG J3.13 adjudication and any directly relevant successor study.

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

After MK-0:

~~~
1. do not train;
2. monitor/re-audit CQG J3.13;
3. monitor relevant KCL, OIR-PPV, ARN, and NEXUS closures;
4. when MK-1 dependencies are satisfied, write a separate prospective MK-1 protocol;
5. freeze that protocol before implementation/outcome;
6. only then authorize model experimentation.
~~~

MK-0 itself authorizes no further repository changes beyond governance maintenance and append-only lineage updates required to record dependency changes.