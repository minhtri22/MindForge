# Adaptive Continual Outcome Modeling (ACO)

Status: **NEW PREREGISTERED RESEARCH PROGRAM — NO SCIENTIFIC EXECUTION YET**

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

## Current authorization

ACO-1 implementation and zero-science preflight are now **PASS / CLOSED**.

Canonical QA: `ACO1_PREFLIGHT_QA.md`.

ACO-1 Execution Lock is now **independently verified PASS**.

Canonical lock: `ACO1_EXECUTION_LOCK.json`.

Canonical verification: `ACO1_EXECUTION_LOCK_VERIFICATION.md`.

The next scientific step may execute the frozen 40-seed ACO-1 collection under that exact lock, followed by exactly one adjudication only after complete collection.

Not authorized:

```text
any ACO-1 execution that changes the verified lock
ACO-2 outcome-model fitting
controller implementation
KCL-7
consumption of the protected KCL confirmatory cohort
```
