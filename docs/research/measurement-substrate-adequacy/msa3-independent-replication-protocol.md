# MSA-3 — Independent Fresh Replication Protocol

Status: **PREREGISTERED / FRESH EXECUTION NOT AUTHORIZED**

Program: MSA — Measurement / Substrate Adequacy

Discovery claim to replicate:

```text
MSA-1
PASS
ACCURACY_COARSE_LOSS_INFORMATIVE
```

Discovery formal-result SHA-256:

```text
359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637
```

MSA-1 transition decision:

```text
MSA-2 = NOT AUTHORIZED / DEFERRED
MSA-3 = SELECTED NEXT MILESTONE
```

## 1. Replication question

> On a fully fresh cohort, with the exact same unchanged substrate, endpoint
> definitions, support/reliability gates, accuracy gates, loss gates and joint
> classification matrix used in MSA-1, does the canonical one-shot classifier
> again return `ACCURACY_COARSE_LOSS_INFORMATIVE`?

MSA-3 is a confirmatory replication. It does not explore alternative metrics,
thresholds, difficulty regimes, task structures or predictors.

## 2. Frozen scientific identity inherited unchanged from MSA-1

MSA-3 must preserve exactly:

```text
substrate:
  KCL1Config unchanged
  task order = T1_U1_A → T2_U1_B → T3_U3_A → T4_U3_B
  policies   = A_CARRY_ALL / B_RESET_ALL / C_CARRY_STEP_RESET_MOMENTS
  current samples/update = 15
  replay samples/update  = 1
  endpoint step          = 250
  CPU deterministic path

endpoint pair:
  terminal_accuracy
  terminal_cross_entropy_loss

population:
  72 seeds × 3 matched boundaries
  = 216 matched boundaries
  = 648 A/B/C endpoint pairs

reliability:
  first 6 frozen seeds repeated exactly

accuracy gates:
  SATURATED:
    ceiling_fraction >= 0.50
    p10 >= 23/24
  INFORMATIVE:
    unique_count >= 4
    robust_span >= 2/24
  global:
    same state in >=2/3 policies at every stage

loss gates:
  L95 = -ln(0.95)
  SATURATED:
    p90 <= L95
  INFORMATIVE:
    unique_count >= 10
    robust_span >= 0.02
    p90 > L95
  global:
    same state in >=2/3 policies at every stage
```

No scientific gate differs from MSA-1.

## 3. Frozen classification matrix

Exactly the MSA-1 matrix:

```text
ACCURACY_INFORMATIVE + LOSS_INFORMATIVE
→ ENDPOINT_MEASUREMENT_ADEQUATE

ACCURACY_SATURATED + LOSS_INFORMATIVE
→ ACCURACY_COARSE_LOSS_INFORMATIVE

ACCURACY_SATURATED + LOSS_SATURATED
→ CURRENT_SUBSTRATE_ENDPOINT_SATURATED

any other complete-data pattern
→ STOP_INTEGRITY_OR_SUPPORT
```

## 4. Replication-success criterion

The replication claim is frozen before MSA-3 fresh execution:

```text
REPLICATION_CONFIRMED
iff
canonical MSA-3 one-shot verdict
== ACCURACY_COARSE_LOSS_INFORMATIVE
```

Any other canonical verdict means:

```text
REPLICATION_NOT_CONFIRMED
```

If the underlying classifier returns `STOP_INTEGRITY_OR_SUPPORT`, the
replication is unadjudicable and also not confirmed.

No alternative partial-match, stage-specific rescue or threshold relaxation is
allowed after outcomes.

## 5. Fresh cohort

Exactly 72 fresh seeds:

```text
4632344,3715332,4702401,8249890,7222878,8766965,
8186980,3421287,7823696,7361523,5782374,3461192,
8672287,7946731,8039551,5898726,5530516,7304549,
4574050,2777688,6487687,2073202,2493669,6069173,
5380311,6749456,7186523,2822907,8679347,4723573,
5594742,4730662,5957069,5391391,6804821,4925724,
4489402,2373972,3373481,8495716,7878724,7620252,
4567757,6965735,8480204,3484189,2610959,8358070,
4332215,7468926,2250351,5806588,2693511,3617592,
4267044,2041109,3209463,3238873,7635919,5232304,
3408254,5059373,4701506,6837399,4842603,6283077,
6348697,6445575,8003159,5921802,6552527,7406131
```

Canonical comma-joined SHA-256:

```text
5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8
```

Generation provenance:

```text
phrase = MindForge|MSA-3|independent-fresh-replication|v1

candidate_i = 2,000,000 + (
  uint64_be(SHA256(phrase + "|" + decimal(i))[0:8]) mod 7,000,000
)

accept candidates in counter order if not already accepted
stop at 72 unique seeds
```

No scientific outcome informed seed generation.

## 6. Collision exclusions

Before fresh execution the 72-seed cohort must be disjoint from:

1. all historical KCL scientific seeds;
2. protected KCL confirmatory cohort;
3. spent ACO-1 cohort;
4. spent CPRM-1 cohort;
5. spent MSA-1 cohort;
6. any other prior MSA scientific cohort.

A collision discovered before science invalidates the MSA-3 seed manifest and
requires a new preregistration + lock.

No seed substitution is permitted after fresh outcome generation begins.

## 7. Same-state endpoint extraction

MSA-3 uses the exact MSA-1 extraction implementation.

For each boundary, A/B/C fork the same pre-boundary model/optimizer/memory
state. The next task runs through the existing KCL-6.5.5 lockstep training path
for exactly 250 steps.

Both endpoint values are taken from the same canonical step-250 curve point:

```text
terminal_accuracy
terminal_cross_entropy_loss
```

No extra gradient update, alternate evaluation set, difficulty change or
additional endpoint metric is permitted.

## 8. Support and reliability

Expected:

```text
72/72 fresh seeds
216/216 matched boundaries
72/72 boundaries per stage
648/648 A/B/C endpoint pairs
```

Support is all-or-nothing.

Reliability repeats are exactly the first six MSA-3 seeds:

```text
4632344,3715332,4702401,8249890,7222878,8766965
```

Require:

```text
terminal_accuracy max_abs_diff = 0
terminal_cross_entropy_loss max_abs_diff = 0
boundary/policy/integrity structure identical
```

## 9. One-shot replication adjudication

Pre-adjudication validation may inspect only:

- collection completeness;
- seed/stage support;
- A/B/C structural integrity;
- deterministic repeat equality;
- collection hash/provenance.

Pre-adjudication inspection of accuracy/loss classification is prohibited.

The canonical classifier runs exactly once on the complete preserved
collection.

MSA-3 then records:

```text
underlying_verdict
replication_status
```

where:

```text
underlying_verdict == ACCURACY_COARSE_LOSS_INFORMATIVE
→ REPLICATION_CONFIRMED

otherwise
→ REPLICATION_NOT_CONFIRMED
```

## 10. Technical retry policy

Collection retry is allowed only after a technical failure and before a
complete valid 216-boundary collection exists.

Rules:

- same seed, same immutable lock;
- no seed substitution;
- no source/substrate/gate/difficulty change;
- no endpoint-classification inspection before retry;
- once a complete valid collection exists, collection must never be rerun.

Adjudication:

- exactly one valid one-shot run;
- retry only if no valid MSA-3 formal result exists;
- retry must use the same preserved input and exact lock;
- once a valid formal result exists, adjudication must never be rerun.

## 11. Downstream governance

`REPLICATION_CONFIRMED` permits only MSA-4 downstream governance review.

`REPLICATION_NOT_CONFIRMED` triggers mandatory convergence review.

Neither result automatically opens:

- MSA-2;
- predictor fitting;
- controller work;
- KCL-7.

## 12. Execution authorization

Fresh MSA-3 science remains prohibited until:

1. MSA-3 implementation + synthetic tests are frozen;
2. exact execution lock is created;
3. zero-science preflight closes PASS;
4. independent verification of that exact lock closes PASS.

This preregistration does not itself authorize fresh execution.
