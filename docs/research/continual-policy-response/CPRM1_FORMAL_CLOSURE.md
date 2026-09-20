# CPRM-1 Formal Closure

Status: **NEGATIVE / CLOSED**

Date: 2026-09-20

Canonical verdict:

```text
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
```

## Execution integrity

CPRM-1 executed under the independently verified execution lock.

- workflow run: `35518986215`
- lock SHA-256: `26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274`
- protocol SHA-256: `2663cb2b28f73e02bbac19c537e16632f978d2d754488932924bf37e7c8ea084`
- seed-manifest SHA-256: `d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3`
- fresh seeds: `60/60`
- complete matched boundaries: `180/180`
- response vectors: `540`
- stage counts: `60/60/60`
- deterministic reliability repeats: `6/6 exact`
- collection integrity/support: **PASS**
- collection SHA-256: `d3c3b70f3ab1c412c18477bf69d12d3bc8cdbd56130515fa64d70c377fb808af`
- collection evidence commit: `cda98d319753cdeaaa748cdef124b13be202a2e6`
- collection-before-adjudication artifact ID: `10607618079`
- collection artifact ZIP SHA-256: `11bebada98a228bd4a5a25ae45fd7bfd92df93f346d98e66bc5ed0bfc62b8fd5`
- one-shot adjudicator calls: `1`
- formal-result SHA-256: `fb3e27b7b63e7057c11958bddedefd783fb0f15339d25027377349a9fca1ac07`
- formal-result evidence commit: `7f2dbb70c896ea5fb115f1eb12cebadfc9e4268e`
- complete execution artifact ID: `10607937544`
- complete execution artifact ZIP SHA-256: `b8e1b9e7e6799f4c51506e76f974c773d7a9487b40d37db2152eaf9b529e57ab`

No response/contrast geometry was inspected between collection and one-shot
adjudication.

## Formal result

Support/integrity/reliability all passed.

Response-component qualification:

```text
plasticity_auc             PASS
prior_task_retention       PASS
worst_prior_accuracy       PASS
final_current_accuracy     FAIL
```

Therefore:

```text
all four components qualified = false
```

Both preregistered policy-contrast families qualified:

```text
B - A   PASS
C - A   PASS
```

The joint CPRM-1 contract required all four response components to qualify.
The contract therefore returns:

```text
CPRM-1 = NEGATIVE
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
```

## Why final_current_accuracy failed

The canonical one-shot result shows endpoint accuracy is heavily ceiling
concentrated under this substrate.

For example, the stage-1 and stage-2 cells for A are exactly `1.0` at both
p10 and p90, and corresponding B/C cells are similarly concentrated.

Across all nine policy×stage cells:

```text
qualified final_current_accuracy cells = 0/9
```

This is a descriptive observation from the frozen adjudicator result, not a
post-hoc permission to change the target contract.

## What the result establishes

CPRM-1 establishes that the **joint four-component continuous-response object
frozen by CPRM-0/1 does not have the required non-degenerate geometry under the
tested substrate**.

It also establishes that:

- collection support is complete;
- measurement integrity is valid;
- deterministic repeat reliability is exact;
- plasticity AUC has qualified geometry;
- mean prior retention has qualified geometry;
- worst-prior accuracy has qualified geometry;
- both B-A and C-A contrast families have qualified geometry.

## What the result does not establish

It does not establish that:

- the three qualified components may now replace the frozen four-component
  target;
- final_current_accuracy should be dropped;
- a lower endpoint threshold/resolution should be adopted;
- a predictor would succeed on the qualified components;
- CPRM-2 may be opened;
- more seeds may be added;
- the same cohort may be reused for a redesigned target;
- a controller is justified.

Any such move inside CPRM would be post-outcome target rescue.

## Governance consequence

Per the frozen protocol:

```text
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
→ CPRM-2 NOT AUTHORIZED
→ FORMAL CONVERGENCE REVIEW REQUIRED
```

The complete CPRM-1 collection is now historical/spent scientific evidence.
It must not be reused to fit/tune/validate a replacement predictive target.
