# KCL-6.5.1 — Stability–Plasticity Tradeoff Confirmation

## Abstract

KCL-6.5 confirmed a large retention benefit from targeted clarification over a matched placebo query, but failed its composite H-S4 gate because one of five fresh seeds showed a one-item T4 decrement for E relative to F. KCL-6.5.1 therefore froze the E/F policies unchanged and ran an independent 20-seed confirmation cohort to determine whether the apparent current-task cost is a reproducible stability–plasticity tradeoff or finite-seed variation.

The retention-specificity effect replicates strongly. Across all 20 fresh seeds, E final mean prior-task accuracy exceeds F. Mean paired retention gain is +0.26528 (+26.53 percentage points), with a frozen paired bootstrap 95% CI of [0.23403, 0.29375]. All 20/20 seeds are positive.

For current-task plasticity, mean paired T4 delta is only -0.00833 (-0.83 percentage points), with bootstrap 95% CI [-0.02292, 0.00417]. The interval includes zero and lies entirely above the pre-registered practical non-inferiority boundary of -1/24 = -0.04167. The frozen plasticity classifier therefore returns:

```
NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN
```

However, the milestone still closes FAIL because the pre-registered absolute E gate requires T4 >= 0.95 on every seed. Seed 9393 produces E T4 = 0.75. F also collapses on the same seed to T4 = 0.875. Thus the official verdict is:

```
KCL-6.5.1 = FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

The correct interpretation is mixed but informative: clarification specificity replicates very strongly; the small E-vs-F plasticity decrement seen in KCL-6.5 does **not** reproduce as a directional paired tradeoff; but the absolute current-task acquisition contract is not stable across the larger seed cohort because of seed 9393.

## 1. Why KCL-6.5.1 was opened

KCL-6.5 ended:

```
FAIL
TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS
```

with:

- H-S1 target specificity: PASS
- H-S2 matched-query null: PASS
- H-S3 retention specificity effect: PASS
- H-S4 composite plasticity/non-degradation: FAIL
- H-S5 query/storage integrity: PASS

The unresolved observation was:

```
mean DeltaR = +0.25556
mean DeltaP = -0.00833
```

where the negative T4 contrast came from one seed.

KCL-6.5.1 does not modify any earlier verdict.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl651-protocol.md`

Protocol commit:

`5aed0aec5dd7d45fbdce7dbe4a247b663d16da2e`

Protocol SHA-256:

`28ecce49bea54f688d0120179ee1932f1d7176df172ade9318742765f6cbeb54`

The E/F policies, replay budget, query budget, memory representation, decay schedule, task stream, optimizer, and strict T4 gate were unchanged.

## 3. Independent primary cohort

Fresh seeds:

```
5555
5757
5959
6161
6363
6565
6767
6969
7171
7373
7575
7777
7979
8181
8383
8585
8787
8989
9191
9393
```

N = 20.

The previous KCL-6.5 five-seed cohort was excluded from primary inference and retained only as secondary historical context.

## 4. Frozen inference

Paired endpoints:

```
DeltaR = E prior mean - F prior mean
DeltaP = E T4 - F T4
```

Bootstrap contract:

```
20,000 paired nonparametric resamples
RNG seed = 651651
95% percentile CI
```

Practical T4 margin:

```
M = 1/24 = 0.0416667
```

one evaluation item.

## 5. Retention specificity independently replicates

Primary DeltaR:

```
mean   = 0.26528
median = 0.28472
min    = 0.11111
max    = 0.34722
```

Bootstrap:

```
95% CI = [0.23403, 0.29375]
```

Directional seeds:

```
20/20 DeltaR > 0
```

The frozen replication gate required:

1. mean DeltaR >= 0.10;
2. bootstrap lower bound > 0;
3. at least 16/20 positive seeds.

All three pass.

Therefore the core KCL-6.5 finding is independently replicated:

> task-relevant clarification materially improves retention over a matched placebo query.

## 6. Paired plasticity result

Primary DeltaP:

```
mean   = -0.00833
median = 0
min    = -0.125
max    = +0.04167
```

Sign counts:

```
negative = 3
zero     = 16
positive = 1
```

Bootstrap:

```
95% CI = [-0.02292, +0.00417]
```

The interval:

- includes zero;
- stays above the practical boundary -0.04167.

Therefore the pre-registered classification is:

```
NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN
```

This means the small negative mean observed in KCL-6.5 is not confirmed as a directional paired plasticity cost on the independent N=20 cohort.

## 7. Absolute E plasticity failure

The protocol separately retained the older hard contract:

```
E final T4 >= 0.95
```

for every seed.

Nineteen seeds satisfy the intended operating region, but seed 9393 does not:

```
seed 9393:
E T4 = 0.750
F T4 = 0.875
DeltaP = -0.125
DeltaR = +0.19444
```

This single seed forces:

```
absolute_E_plasticity.pass = false
```

and therefore the overall protocol status:

```
FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

No seed was removed and the strict gate was not relaxed.

## 8. Why seed 9393 matters scientifically

Seed 9393 is not simply another instance of E losing to F.

Both arms fail the historical 95% current-task floor:

```
E = 75.0%
F = 87.5%
```

while E still retains a positive prior-retention advantage:

```
DeltaR = +19.44 percentage points
```

This pattern raises a new possibility:

> the absolute failure may involve current-task acquisition instability of the diagnostic trajectory/substrate at that seed, rather than an E-specific clarification cost.

KCL-6.5.1 does not prove that explanation. A separate controlled acquisition diagnostic is required.

## 9. Historical pooled context

For descriptive context only, combining the historical KCL-6.5 five seeds with the new twenty seeds gives:

```
N = 25
mean DeltaR = +0.26333
mean DeltaP = -0.00833
```

These pooled values were not used for the primary classification.

## 10. Integrity

All paired contract checks passed:

- historical KCL-6.5 anchor valid;
- E/F policies unchanged;
- candidate-set behavior unchanged;
- query schedule unchanged;
- no query enters gradient/storage;
- E exact replay contract preserved;
- replay budget unchanged;
- final persistent memory unchanged;
- model architecture unchanged.

Thus the scientific failure is not an implementation/integrity failure.

## 11. Artifact serialization note

The canonical workflow artifact contains the complete JSON object followed by a literal two-character `\n` suffix due to a writer serialization bug.

No scientific rerun was performed after observing the result.

The committed machine-readable evidence was recovered by removing **only** that trailing suffix. No scientific value was modified.

Canonical artifact SHA remains preserved.

## 12. Scientific interpretation

KCL-6.5.1 resolves one question and opens another.

### Resolved

The retention-specificity effect is robust:

```
DeltaR mean = +26.53 pp
95% CI      = [+23.40, +29.38] pp
20/20 positive
```

### Also resolved

The earlier small E-vs-F T4 decrement is not independently confirmed as a reproducible paired tradeoff:

```
DeltaP mean = -0.83 pp
95% CI      = [-2.29, +0.42] pp
```

which remains inside the one-item practical margin.

### Still unresolved

The absolute current-task contract itself is unstable on seed 9393.

That issue must be isolated before model-scale transfer.

## 13. Verdict

Official milestone verdict:

```
KCL-6.5.1 = FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

Secondary pre-registered plasticity classification:

```
NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN
```

Retention specificity replication:

```
PASS
```

These statements are complementary, not contradictory.

## 14. Provenance

Canonical workflow:

`35353568473`

Canonical scientific source:

`d75173f661d01e2cc9f2d852445c4852f1a94ae6`

Focused tests:

`15 passed (9 KCL-6.5.1 + 6 KCL-6.5)`

Artifact ID:

`10551212217`

Artifact ZIP SHA-256:

`e819421c9a82c1adc9c09bf549cef8d5244e1d9add84a0b767b61026b88610a1`

Machine-readable recovered evidence:

`experiments/kernel_cl/results/kcl651_summary.json`

## 15. Next scientific requirement

Do not tune E, F, replay ratio, or the 95% gate.

The next experiment should isolate seed-9393 current-task acquisition:

- exact/current-only acquisition control;
- exact reconstructive C reference;
- E targeted clarification;
- F placebo/fuzzy control;
- same seed and frozen task trajectory;
- determine whether T4 acquisition collapse occurs independently of clarification policy.

Only after that causal source is identified should KCL-7 model-scale transfer reopen.
