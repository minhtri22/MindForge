# MSA-3 Formal Replication Closure

Status: **REPLICATION CONFIRMED / CLOSED**

Date: 2026-09-25

## Discovery claim

MSA-1 discovery verdict:

```text
ACCURACY_COARSE_LOSS_INFORMATIVE
```

Discovery formal-result SHA-256:

```text
359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637
```

## Canonical MSA-3 execution

Workflow:

```text
36051817225
```

Exact verified lock:

```text
bd8deb49030d98d2c11254d792065ceaef2e4e53d8db35489efb2c15570d66a7
```

Population:

```text
72/72 fresh seeds
216/216 matched boundaries
648/648 A/B/C endpoint pairs
72 boundaries per stage
6/6 deterministic reliability repeats exact
```

Integrity/support/reliability:

```text
PASS
```

Collection SHA-256:

```text
a4943f33cf36627d2ba27572e2e9ff15fc4b1acebd1509fa24587c677c9cd282
```

Collection evidence commit:

```text
78b3b5d4fe6af7795e12c4b1b40de1d9acb1afea
```

Collection-before-adjudication artifact:

```text
ID = 10830733270
ZIP SHA-256 = fdcf17b2861fdf4e253d8236dd6495dc4922ab863dfe3068f2d73209ce4f6748
```

The collection was preserved before any endpoint classification was inspected.

Exactly one unchanged MSA-1 classifier call was executed.

Formal result SHA-256:

```text
823f9c5f225f95eb69cfa940c96733257c9130ac1926533b847645bd46e8c5a6
```

Formal-result evidence commit:

```text
a0ceff49b54ab389d5d98a934a31486ffce4f669
```

Complete replication artifact:

```text
ID = 10830678339
ZIP SHA-256 = ccb947cf15f621ae3b75c05ed2b9635200e9d771f634bad40067cec11af7802c
```

## Canonical replication result

Observed verdict:

```text
ACCURACY_COARSE_LOSS_INFORMATIVE
```

Frozen replication rule:

```text
observed verdict == ACCURACY_COARSE_LOSS_INFORMATIVE
→ REPLICATION_CONFIRMED
```

Therefore:

```text
MSA-3 = REPLICATION_CONFIRMED
```

## Replicated global endpoint state

```text
terminal accuracy:
  informative = false
  saturated   = true

terminal cross-entropy loss:
  informative = true
  saturated   = false
```

Accuracy qualifying-policy counts:

```text
SATURATED:
  stage 1 = 3/3
  stage 2 = 3/3
  stage 3 = 2/3

INFORMATIVE:
  stage 1 = 0/3
  stage 2 = 0/3
  stage 3 = 0/3
```

Loss qualifying-policy counts:

```text
INFORMATIVE:
  stage 1 = 2/3
  stage 2 = 2/3
  stage 3 = 2/3

SATURATED:
  stage 1 = 1/3
  stage 2 = 1/3
  stage 3 = 1/3
```

The replication preserves the same aggregate pattern seen in MSA-1.

## What is now supported

Within the frozen current synthetic substrate:

1. terminal argmax accuracy is reproducibly coarse / ceiling-compressed under
   the preregistered global rule;
2. terminal cross-entropy loss reproducibly retains non-degenerate endpoint
   information;
3. the substrate is not jointly endpoint-saturated;
4. making the task harder is not required merely to recover an informative
   endpoint measurement.

## What is not supported

MSA-3 does not establish:

- that terminal loss is the only valid future endpoint;
- that terminal accuracy should disappear from diagnostics;
- that a response predictor will succeed;
- that any prior CPRM target should be revived;
- that MSA-2 should be opened;
- that a controller is justified.

## Data disposition

The complete MSA-3 cohort is now:

```text
HISTORICAL / SPENT CONFIRMATORY EVIDENCE
```

It may be retained for provenance and exact reproduction only.

It may not be used for:

- target selection in a future modeling program;
- feature selection;
- hyperparameter tuning;
- model fitting;
- threshold tuning;
- validation;
- future replication qualification.
