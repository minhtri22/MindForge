# KCL-6.5-Q — Clarification Specificity Qualification

Status: PRE-A/B QUALIFICATION. Must close before KCL-6.5 main A/B.

## Goal

Validate that a matched-query placebo control can isolate **clarification specificity** rather than merely query count, payload presence, timing, or extra external information.

KCL-6.4 established that targeted clarification E rescues the failed fuzzy-memory policy D. KCL-6.5 asks whether the rescue depends on asking the **right missing information**.

## Frozen base

- KCL-6.3 D remains FAIL.
- KCL-6.4 E remains PASS.
- Fuzzy representation unchanged:
  - bucket width = 4;
  - missing field = exact offset b;
  - support count absent;
  - same decay schedule;
  - same model/tasks/seeds/replay budget.

## Candidate matched-query control F

F uses the same query timing as E:

- T2: 0 queries;
- T3: 1 query;
- T4: 2 queries.

At each E clarification opportunity, F also receives one exact 3-tuple observation, but from the **current task being trained**, at that current task's key_min.

Thus F response has the same payload shape:

```
(input_token_0, input_token_1, target)
```

and is ground-truth data from the environment, but it is not an observation of the fuzzy prior-task memory currently being replayed.

The F cue:

- does not enter the batch;
- receives no gradient;
- is not stored;
- is not allowed to update the queried prior-task fuzzy schema.

## Q1 — Targeted cue identifiability

For every frozen fuzzy task, before targeted clarification:

```
|candidate offsets| = 4
```

A same-task exact cue at key_min must reduce:

```
4 -> 1
```

and reconstruct all 24 task observations exactly.

PASS iff true for T1/T2/T3.

## Q2 — Placebo cue non-identifiability

For every frozen fuzzy replay source, an exact key_min observation from the current task must leave the queried prior-task candidate set unchanged:

```
4 -> 4
```

The F cue must not be accepted by the prior-task reactivation function because its task/context input does not match the fuzzy memory's key_min observation identity.

PASS iff true for every T3/T4 query opportunity.

## Q3 — Equal query envelope

E and F must have identical:

- query count;
- query timing;
- response tuple arity/type;
- no-gradient rule;
- no-storage rule;
- replay slots;
- optimizer steps;
- processed-example count.

PASS iff all equal.

## Q4 — Placebo operational null

Given identical post-T1 state, current batches, replay source schedule, replay ranks, and D fuzzy RNG:

F must produce the same replay observations, gradients, and post-stage model state as D because its placebo cue cannot change memory or training data.

Required deterministic check:

```
D model state == F model state
D optimizer state == F optimizer state
D replay observations == F replay observations
```

for a frozen qualification seed.

This is an implementation/mechanism qualification, not the main scientific A/B.

## Q5 — No hidden cross-task resolver

The F control must not use any cross-task rule such as:

- inferring prior offset from current-task offset;
- correlating task IDs with offsets;
- consulting task-family formulas;
- using historical raw observations.

The prior-task uncertainty resolver may consume only:

- the prior fuzzy schema;
- a cue whose input identity belongs to that same prior task.

PASS iff enforced by code contract and tests.

## Qualification seed

Use exactly:

```
5151
```

This seed is qualification-only and must not appear in the main KCL-6.5 A/B seeds.

## Qualification verdict

All Q1–Q5 PASS:

```
KCL-6.5-Q = PASS
MATCHED_QUERY_CONTROL_QUALIFIED
```

Any failure:

```
KCL-6.5-Q = REVISE
MATCHED_QUERY_CONTROL_INVALID
```

Main KCL-6.5 must not execute unless Q PASSes.

## Required artifacts

- `experiments/kernel_cl/kcl65q_specificity_qualification.py`
- `experiments/kernel_cl/results/kcl65q_summary.json`
- `tests/test_kernel_cl_kcl65q.py`
- `docs/research/kernel-continual-learning/kcl65q-paper.md`
- `.github/workflows/kernel-cl-kcl65q.yml`
