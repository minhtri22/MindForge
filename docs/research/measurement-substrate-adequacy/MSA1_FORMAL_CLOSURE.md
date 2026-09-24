# MSA-1 Formal Closure

Status: **PASS / CLOSED**

Date: 2026-09-25

Canonical verdict:

```text
ACCURACY_COARSE_LOSS_INFORMATIVE
```

Canonical reason:

```text
ACCURACY_SATURATED_LOSS_INFORMATIVE
```

## Execution integrity

MSA-1 executed under the exact independently verified lock:

```text
c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657
```

Canonical workflow:

```text
36033469789
```

Frozen population:

```text
72/72 fresh seeds
216/216 matched boundaries
648 A/B/C endpoint pairs
72 boundaries per stage
6/6 deterministic reliability repeats exact
```

Integrity/support/reliability:

```text
PASS
```

Collection SHA-256:

```text
4b7269a5fb0ab6750e067cfd26d95913dabbe2181af4001a689a1cea85cdbcd4
```

Collection evidence commit:

```text
f5ec2e3a38813904a76290ff88f2df4fbc4b2167
```

Collection-before-adjudication artifact:

```text
ID = 10823599007
ZIP SHA-256 = 3ceb17a0add080d4fffd4c98e2b621c70021a56acc21baec6a9e3f7c21c87e08
```

Exactly one valid one-shot adjudication was executed.

Formal-result SHA-256:

```text
359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637
```

Formal-result evidence commit:

```text
42a549601f44e80ebc35c446123ae8191eee5b53
```

Complete execution artifact:

```text
ID = 10823374088
ZIP SHA-256 = 465356e0d173978fd7f6aeef894f9ccb41d5402ed7317bde8f37f5bcacb91458
```

No accuracy/loss/joint classification was inspected between collection and
one-shot adjudication.

No difficulty mutation occurred.

No predictor was fitted.

## Frozen classification outcome

Global endpoint states:

```text
accuracy_informative = false
accuracy_saturated   = true

loss_informative     = true
loss_saturated       = false
```

Therefore the frozen classification matrix returns:

```text
ACCURACY_SATURATED + LOSS_INFORMATIVE
→ ACCURACY_COARSE_LOSS_INFORMATIVE
```

### Accuracy aggregation detail

The preregistered global rule required the same state in at least 2 of 3
policies at each stage.

Saturated-policy counts by stage:

```text
stage 1 = 3/3
stage 2 = 3/3
stage 3 = 2/3
```

Informative-policy counts:

```text
stage 1 = 0/3
stage 2 = 0/3
stage 3 = 0/3
```

Thus accuracy is globally classified saturated under the frozen aggregation
rule.

This does **not** mean every individual accuracy cell was saturated. In
particular, A at stage 3 did not satisfy the frozen saturation criterion.

### Loss aggregation detail

Informative-policy counts by stage:

```text
stage 1 = 2/3
stage 2 = 2/3
stage 3 = 2/3
```

Saturated-policy counts by stage:

```text
stage 1 = 1/3
stage 2 = 1/3
stage 3 = 1/3
```

Thus terminal cross-entropy loss is globally informative under the frozen rule.

This does **not** mean every individual loss cell was informative. The C policy
qualified as loss-saturated at all three stages, while A/B supplied the
2-of-3 informative support required at each stage.

## Scientific interpretation

MSA-1 establishes, for the frozen current substrate and fresh cohort, that:

1. terminal accuracy is too coarse/ceiling-compressed to provide the required
   global non-degenerate endpoint geometry;
2. the pre-existing probability-sensitive terminal cross-entropy loss remains
   globally informative;
3. the current substrate is therefore **not** classified as jointly
   endpoint-saturated;
4. endpoint measurement is not absent; rather, the accuracy/loss pair exhibits
   a resolution mismatch at the frozen endpoint.

This is a measurement-adequacy result, not a predictor result.

## What MSA-1 does not establish

MSA-1 does not establish that:

- terminal accuracy should be deleted from future measurement contracts;
- terminal loss should replace all other endpoints;
- a response predictor will succeed;
- the accuracy/loss discordance generalizes to other task/substrate structures;
- MSA-2 is automatically justified;
- any task should be made harder;
- any controller is warranted.

## Data disposition

The 72-seed MSA-1 cohort is now:

```text
HISTORICAL / SPENT MSA-1 EVIDENCE
```

It may be preserved for provenance and exact reproduction.

It may not be used to:

- choose MSA-2 variants;
- tune difficulty;
- alter MSA-3 gates;
- choose a new endpoint metric;
- fit a predictor;
- tune or validate downstream models.
