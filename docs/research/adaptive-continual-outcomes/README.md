# Adaptive Continual Outcome Modeling (ACO)

Status: **PROGRAM STOPPED AFTER ACO-1 SUPPORT GATE**

Branch: `research/adaptive-continual-outcomes`

Parent research closure: `research/kernel-cl@a9159ae8f17693453e7b6378c92deb5effc4a56f`

## Purpose

ACO is a post-KCL research program for the original MindForge continual/adaptive-learning objective.

It does **not** continue KCL-6.5.9.x numbering and does **not** attempt another feature/representation rescue for `Y_PRR`.

The new research object is:

```text
observable pre-boundary state
        ↓
policy-specific continuous outcomes
        ↓
action contrasts / uncertainty
        ↓
later, only if independently qualified:
decision rule
```

The first scientific milestone is **ACO-1 Target-Stability Qualification**. No controller is authorized.

## Canonical documents

- `ORIGIN_AUDIT.md` — why KCL existed and how its objective evolved.
- `CHARTER.md` — why ACO exists and what it may/not do.
- `EVIDENCE_INHERITANCE.md` — exact KCL evidence inherited and excluded.
- `RESEARCH_QUESTION.md` — primary falsifiable research question.
- `FALSIFICATION_GATES.md` — phase-transition and STOP rules.
- `ROADMAP.md` — finite research sequence.
- `aco1-target-stability-protocol.md` — frozen first diagnostic protocol.
- `LINEAGE.md` — append-only execution/decision history.
- `ACO1_PREFLIGHT_QA.md` — zero-science implementation qualification.
- `ACO1_EXECUTION_LOCK.json` — immutable machine-readable execution contract.
- `ACO1_EXECUTION_LOCK_VERIFICATION.md` — independent lock-verification closure.

## Current status

ACO-1 completed its locked fresh execution and one-shot adjudication.

Canonical result:

```text
STOP
TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

The frozen support gate required at least 30 canonical Y_PRR boundaries across at least two stages; the adjudicator found 12 across all three stages.

Canonical closure: `ACO1_FORMAL_CLOSURE.md`.

The finite roadmap's insufficient-support STOP condition is therefore active.

Authorized now:

```text
formal convergence review only
documentation / provenance closure
```

Not authorized:

```text
additional ACO-1 seeds
ACO-1 threshold/support relaxation
ACO-2 outcome-model fitting
controller implementation
KCL-7
protected KCL confirmatory cohort use
```
