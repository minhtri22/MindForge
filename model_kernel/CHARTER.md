# MindForge Model Kernel Research Charter

Status: **MK-0 GOVERNANCE FREEZE / RESEARCH ONLY**

Branch: **research/model_kernel**

## 1. Purpose

This track studies the learned neural core of MindForge.

"Model Kernel" is a research-track name for the learned model core. It does **not** redefine the frozen MindForge Kernel runtime boundary.

The architectural invariant remains:

~~~
MindForge Model != MindForge Kernel
~~~

The MindForge Model owns learned representations, parameters, and learned capabilities. The MindForge Kernel owns only the minimal proven runtime contract and universal runtime primitives.

## 2. MK-0 scope

MK-0 is governance-only.

Authorized work in MK-0 is limited to exactly these six research documents:

- CHARTER.md
- LINEAGE.md
- INHERITANCE_REGISTRY.md
- BASELINE_CONTRACT.md
- DEPENDENCY_GATES.md
- RESEARCH_ROADMAP.md

MK-0 does not authorize:

- model-code changes;
- new model heads;
- loss-function changes;
- dataset generation;
- training;
- confirmatory execution;
- GitHub Actions experiments;
- benchmark modification;
- memory/retrieval integration;
- continual-learning integration;
- invariant-loss integration;
- sparse/entity architecture integration;
- runtime optimization;
- cherry-picking implementation from other research branches.

## 3. Scientific objective

The first prospective model-level question is whether MindForge can learn a compact internal decision-relevant state from current observations/context, and whether that state is genuinely useful for downstream decisions.

The intended causal decomposition is:

~~~
current observation/context
        |
        v
learned decision-state representation
        |
        v
downstream typed/ranking decision
~~~

The early model studies must separate two questions:

1. **Representation formation** — can the model form a better decision-relevant state?
2. **Decision sufficiency** — is the frozen state actually sufficient/useful for downstream decisions?

These questions must not be collapsed into one end-to-end optimization study.

## 4. Initial memory boundary

MK-1 and MK-2 are **memory-free by design**.

Their input may include current observation, current task/context, and current belief/state when explicitly defined by protocol.

They must not include episodic retrieval, historical precedent, retrieved examples, or memory-conditioned context.

Memory admission is a separate future research line and remains blocked by ARN evidence gates defined in DEPENDENCY_GATES.md.

## 5. Evidence inheritance rule

Results from PIT, CQG, KCL, OIR-PPV, PPF, Track-A, ARN, NEXUS, ArcLLM, or any other research track may:

- motivate a hypothesis;
- define a known failure mode;
- provide a benchmark or semantic contract;
- provide a comparison baseline;
- remove a downstream experiment that upstream evidence has already made unnecessary.

They do **not** count as evidence that a new MindForge model mechanism works.

Every model-level claim requires its own prospectively frozen model experiment.

## 6. One causal variable per study family

A model study should change one major causal variable at a time whenever feasible.

Examples:

- representation mechanism;
- decision head;
- calibration geometry;
- continual-learning mechanism;
- invariance objective;
- memory-admission mechanism.

A study must not combine several unproven mechanisms merely because they are semantically compatible.

## 7. Workload policy

The program follows:

~~~
parallelize analysis/protocol work
serialize expensive scientific evidence
~~~

Upstream PASS/FAIL results should be used to eliminate unnecessary downstream experiments before training is authorized.

A future phase may open only when its dependency gate is satisfied or an explicit governance amendment documents why the dependency is scientifically independent.

## 8. Governance

- LINEAGE.md is append-only after MK-0 creation.
- Failed preregistered gates remain failed.
- Exploratory observations cannot rescue failed confirmatory gates.
- Cross-project findings retain their original scope and population.
- No source branch may be rewritten or merged merely to simplify Model Kernel provenance.
- Before using an external/upstream result, its latest lineage and exact evidence state must be re-audited because research branches can advance independently.

## 9. MK-0 terminal state

When these six documents exist and are internally consistent:

~~~
MK-0 = COMPLETE / GOVERNANCE FROZEN
MK-1 = NOT OPENED
MODEL TRAINING = NOT AUTHORIZED
~~~

The next action is dependency monitoring and protocol design only.