# KCL-6.5-Q — Clarification Specificity Control Qualification

## Verdict

```
KCL-6.5-Q = PASS
MATCHED_QUERY_CONTROL_QUALIFIED
```

## Purpose

Before testing whether KCL-6.4 succeeded because it asked the *right* clarification rather than merely because a query occurred, KCL-6.5-Q qualifies a placebo matched-query control.

The key design issue is specific to the affine diagnostic substrate: any exact observation from the same fuzzy task is sufficient to recover the missing offset. Therefore a same-task "irrelevant observation" is not a valid placebo.

The qualified control instead receives an exact observation from the current task at the same query opportunity. It has the same tuple shape and timing but cannot resolve the selected prior fuzzy memory.

## Q1 — Targeted cue identifiability

For T1/T2/T3 fuzzy memories:

```
candidate offsets before = 4
candidate offsets after targeted same-task key_min cue = 1
```

Recovered offsets:

- T1: 1
- T2: 3
- T3: 4

All 24 observations reconstruct exactly.

Result: **PASS**.

## Q2 — Placebo non-identifiability

Placebo opportunities:

- T3 replaying fuzzy T1, cue from current T3;
- T4 replaying fuzzy T1, cue from current T4;
- T4 replaying fuzzy T2, cue from current T4.

For every opportunity:

```
candidate offsets before = 4
candidate offsets after  = 4
```

The prior-task resolver rejects the placebo because the cue identity does not belong to the queried fuzzy memory.

Result: **PASS**.

## Q3 — Equal query envelope

Targeted and placebo controls have equal:

- query timing;
- response tuple arity = 3;
- replay budget;
- optimizer steps;
- processed examples.

Neither query enters gradient or persistent memory.

Result: **PASS**.

## Q4 — Placebo operational null

Qualification seed:

`5151`

A deterministic D-vs-F run showed after every stage:

- replay observations equal;
- model states equal;
- optimizer states equal.

Query schedule:

```
T2 = 0
T3 = 1
T4 = 2
```

Thus a placebo query has no operational effect on training under the frozen contract.

Result: **PASS**.

## Q5 — No hidden cross-task resolver

The control forbids:

- inferring a prior offset from another task;
- task-ID/offset correlations;
- family formulas;
- historical raw observations.

The resolver only accepts a cue whose input identity belongs to the same queried prior fuzzy memory.

Result: **PASS**.

## Scientific consequence

The main KCL-6.5 experiment may now compare:

- E — targeted clarification, uncertainty `4→1`;
- F — matched placebo query, uncertainty `4→4`.

Because Q4 establishes that F is operationally null-equivalent to D, the main A/B can test whether KCL-6.4's rescue depends on **task-relevant disambiguating information**, not merely query occurrence, response payload shape, or query timing.

## Provenance

- protocol commit: `7911fc005254332af66ca50a83cf1911481dcc5a`
- source commit: `0aeeeafb2df289bb53becc2b19645bd4427657f5`
- run: `35351589288`
- tests: `6 passed`
- artifact: `10549729971`
- artifact SHA-256: `635f4fc7677640211531aa2bb21165e0561dc9eb8a2143ecc9c9a219ce625da2`
