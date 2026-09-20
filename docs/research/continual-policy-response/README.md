# Continual Policy Response Modeling (CPRM)

Status: **CPRM-0 PASS / CLOSED — SCIENTIFIC EXECUTION NOT YET AUTHORIZED**

Branch: `research/continual-policy-response`

Parent governance closure:

```text
research/adaptive-continual-outcomes
0700601f9196d3c5989fa8eb5169f28b1bb01799
ACO_FORMAL_CONVERGENCE_REVIEW = CLOSED
ACO_PROGRAM = TERMINATED
NEXT_DIRECTION = OPTION_2
```

## Purpose

CPRM is a separately named post-ACO research program.

It does not continue ACO numbering and it is not ACO-2.

Its research object is the prospectively defined continuous response of canonical
continual-learning boundary policies over an all-eligible-boundary population:

```text
observable pre-boundary state X
        ↓
policy a ∈ {A,B,C}
        ↓
continuous response Y(X,a)
        ↓
A-relative policy contrasts
        ↓
only after discovery + fresh replication:
decision qualification
```

CPRM-0 contains specification/governance only.

## CPRM-0 canonical documents

- `ORIGIN.md` — why CPRM exists and why it is not ACO-2.
- `EVIDENCE_INHERITANCE.md` — exact findings inherited, excluded and spent.
- `PRIMARY_TARGET_CONTRACT.md` — continuous response object and contrasts.
- `ELIGIBLE_POPULATION_CONTRACT.md` — prospective all-boundary population rules.
- `BASELINE_CONTRACT.md` — minimum simple baselines and anti-rescue rules.
- `FALSIFICATION_GATES.md` — program transition/STOP rules.
- `ROADMAP.md` — finite milestone sequence.
- `LINEAGE.md` — append-only program lineage.

## Current authorization

CPRM-0 zero-science specification QA is **PASS / CLOSED**.

Canonical QA: `CPRM0_SPEC_QA.md`.

Authorized next:

```text
design + preregistration of CPRM-1 protocol
CPRM-1 zero-science implementation/preflight work only after protocol freeze
```

Still not authorized:

```text
fresh scientific seed execution
scientific data collection
response-model fitting
feature selection from outcomes
hyperparameter tuning from fresh outcomes
controller implementation
KCL-7
protected KCL cohort use
ACO-1 spent-data reuse for learning
```
