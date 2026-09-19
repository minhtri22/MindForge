# KCL-6.5.9.1 — Boundary Regime Replication

## Status

```
PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

KCL-6.5.9.1 independently replicates supported **positive-class boundary action
heterogeneity** on a fresh non-confirmatory cohort.

The exact preregistered replication route that passed is:

```
H-REP-ACTION = true
```

because both:

```
B_AND_C_SAFE
C_SAFE_ONLY
```

meet the unchanged KCL-6.5.9 support rule on fresh seeds.

The negative-class replication route did not pass:

```
H-REP-NEGATIVE = false
```

because `CARRY_CATASTROPHIC_FAILURE` did not reproduce with support.

An additional unexpected finding appeared:

```
B_SAFE_ONLY
```

which was absent in KCL-6.5.9 but became supported in replication. Per frozen
protocol this finding does not create the primary PASS, but must be carried
forward as a new preregistered regime-predictability target.

## 1. Motivation

KCL-6.5.9 decomposed the pooled binary target
`SAFE_RESET_OPPORTUNITY` into five frozen counterfactual regimes.

In the original 20-seed discovery cohort only:

- `C_SAFE_ONLY`;
- `A_SUFFICIENT`;

met the absolute support rule.

Two rare alternatives were observed but under-supported:

- `B_AND_C_SAFE`: 2 instances / 2 seeds;
- `CARRY_CATASTROPHIC_FAILURE`: 3 instances / 3 seeds.

Therefore the only authorized next step was fresh non-confirmatory replication,
without classifier or controller training.

## 2. Frozen protocol

Protocol:

```
docs/research/kernel-continual-learning/kcl6591-protocol.md
```

Protocol freeze commit:

```
a719585694232d1f9af71fb2ff9c4debbe42270f
```

Protocol SHA-256:

```
07579d30c661131bd3f7cca385d08a1bfaee5ea7e176546ed75c4dbc4c674b65
```

The protocol froze before scientific execution:

- 66 exact fresh seeds;
- 198 total boundary instances;
- unchanged KCL-6.5.9 taxonomy;
- unchanged A/B/C action criteria;
- unchanged support rule;
- exact replication routes;
- bootstrap procedure;
- STOP/PIVOT rules.

## 3. Cohort and sample-size rationale

Fresh replication cohort:

```
66 seeds × 3 boundaries = 198 boundary instances
```

The fresh seeds are disjoint from:

- all KCL-6.5.6→6.5.9 discovery seeds;
- the protected confirmatory cohort.

The sample size was frozen from the original rare-regime seed rates:

```
B_AND_C_SAFE                2/20 ~= 0.10
CARRY_CATASTROPHIC_FAILURE 3/20 ~= 0.15
```

With the unchanged minimum of five observed instances:

```
P[X >= 5 | n=66, p=0.10] ~= 0.8019
P[X >= 5 | n=66, p=0.15] ~= 0.9774
```

These values were planning assumptions only and never entered adjudication.

## 4. Execution harness

KCL-6.5.9.1 reused the frozen KCL-6.5.6 A/B/C counterfactual harness.

For every fresh seed and each boundary after T1/T2/T3:

- the same substrate was constructed;
- the same A reference trajectory was followed;
- the same A/B/C optimizer-boundary interventions were forked;
- next-task AUC/final accuracy and prior-task retention were measured;
- the unchanged KCL-6.5.9 regime truth table was applied.

No boundary classifier, regime classifier or controller was trained.

## 5. Canonical workflow

Scientific source commit:

```
5db5c3082cb4105d4a5f490423a9be04ebee4884
```

Official workflow run:

```
35413920993
```

Workflow conclusion:

```
SUCCESS
```

Focused tests:

```
10 passed — KCL-6.5.9.1
12 passed — KCL-6.5.9
```

Canonical artifact ID:

```
10574927587
```

Artifact ZIP SHA-256:

```
3271b13a875488f400cf41fba42d8d51489d9a471df0ee5173c59ceae2c57a75
```

Raw replication JSON SHA-256:

```
f76565028bf7eece05a676d8ff643160e00d91fb14583e0af5fe5ebff6d38295
```

Exact raw evidence was subsequently preserved from that artifact into the
repository by a preservation-only workflow.

Preservation workflow source commit:

```
6f156d2f38da99ed93fd1131199698843e904bda
```

Preserved evidence commit:

```
eedf0d98eaca4f2661986a7fdab9fddab610c248
```

No scientific rerun was performed during evidence preservation.

## 6. Integrity

All preregistered integrity conditions passed:

- 66 exact replication seeds;
- all seeds unique;
- exactly 198 records;
- exactly boundaries 1/2/3 per seed;
- no discovery-seed overlap;
- no protected-confirmatory overlap;
- all A/B/C counterfactual integrity checks valid;
- frozen KCL-6.5.9 contract matched;
- exactly-one regime assignment;
- assignment invariant to dictionary presentation order;
- no classifier trained;
- no controller implemented;
- protected confirmatory cohort untouched;
- KCL-7 not started.

## 7. Replication support table

| Regime | Count | Prevalence | Unique seeds | Supported | Boundary 1/2/3 |
|---|---:|---:|---:|---|---|
| `C_SAFE_ONLY` | 134 | 67.68% | 65 | YES | 50 / 52 / 32 |
| `A_SUFFICIENT` | 49 | 24.75% | 40 | YES | 16 / 14 / 19 |
| `B_AND_C_SAFE` | 9 | 4.55% | 9 | YES | 0 / 0 / 9 |
| `B_SAFE_ONLY` | 5 | 2.53% | 5 | YES | 0 / 0 / 5 |
| `CARRY_CATASTROPHIC_FAILURE` | 1 | 0.51% | 1 | NO | 0 / 0 / 1 |

The unchanged support rule was:

```
count >= 5
AND
unique_seed_count >= 3
```

## 8. Primary adjudication

Frozen primary routes:

```
H_REP_ACTION =
  supported(B_AND_C_SAFE)
  AND supported(C_SAFE_ONLY)

H_REP_NEGATIVE =
  supported(CARRY_CATASTROPHIC_FAILURE)
  AND supported(A_SUFFICIENT)
```

Observed:

```
H_REP_ACTION   = true
H_REP_NEGATIVE = false
PRIMARY_REPLICATION = true
```

Therefore:

```
KCL-6.5.9.1 = PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

## 9. Seed-cluster bootstrap prevalence

Frozen bootstrap:

```
20,000 seed-cluster resamples
RNG seed = 6591
95% percentile interval
```

Results:

| Regime | Replication prevalence | 95% interval |
|---|---:|---|
| `C_SAFE_ONLY` | 0.6768 | [0.6162, 0.7374] |
| `A_SUFFICIENT` | 0.2475 | [0.1919, 0.3030] |
| `B_AND_C_SAFE` | 0.0455 | [0.0202, 0.0758] |
| `B_SAFE_ONLY` | 0.0253 | [0.0051, 0.0505] |
| `CARRY_CATASTROPHIC_FAILURE` | 0.0051 | [0.0000, 0.0152] |

Intervals are descriptive and did not alter the support decision.

## 10. Discovery → replication comparison

| Regime | Discovery | Replication | Difference |
|---|---:|---:|---:|
| `C_SAFE_ONLY` | 0.6500 | 0.6768 | +0.0268 |
| `A_SUFFICIENT` | 0.2667 | 0.2475 | -0.0192 |
| `B_AND_C_SAFE` | 0.0333 | 0.0455 | +0.0121 |
| `B_SAFE_ONLY` | 0.0000 | 0.0253 | +0.0253 |
| `CARRY_CATASTROPHIC_FAILURE` | 0.0500 | 0.0051 | -0.0449 |

The dominant `C_SAFE_ONLY` and `A_SUFFICIENT` proportions remain broadly
similar descriptively.

The two originally rare findings diverged:

- `B_AND_C_SAFE` increased enough to become independently supported;
- `CARRY_CATASTROPHIC_FAILURE` nearly disappeared and did not replicate.

## 11. Unexpected supported B_SAFE_ONLY finding

KCL-6.5.9 observed:

```
B_SAFE_ONLY = 0 / 60
```

Fresh replication observed:

```
B_SAFE_ONLY = 5 / 198
             5 unique seeds
             all at boundary 3
```

Thus:

```
UNEXPECTED_SUPPORTED_B_SAFE_ONLY = true
```

Per protocol this finding did not count toward the primary replication PASS.

However it materially strengthens the conclusion that the positive binary class
is not a single action regime:

- C-only-safe;
- B-and-C-safe;
- B-only-safe;

are all now supported on the replication cohort.

This is a new scientific question for the next preregistered milestone, not a
license for post-hoc controller construction.

## 12. Boundary localization

All `B_AND_C_SAFE` replication cases occurred at boundary 3:

```
0 / 0 / 9
```

All `B_SAFE_ONLY` replication cases also occurred at boundary 3:

```
0 / 0 / 5
```

This suggests a strong stage/trajectory interaction for reset-policy
interchangeability/selectivity.

It is descriptive only. No boundary-index rule is qualified here.

## 13. Negative-class result

`CARRY_CATASTROPHIC_FAILURE` did not replicate with support:

```
discovery:   3 / 60 = 5.00%
replication: 1 / 198 = 0.51%
```

Therefore KCL-6.5.9.1 does not support the hypothesis that negative
`SAFE_RESET_OPPORTUNITY=false` boundaries require a stable catastrophic-carry
subregime.

The supported negative class remains dominated by `A_SUFFICIENT`.

## 14. Secondary mechanism counts

Replication observed:

```
RESET_PLASTICITY_GAIN_RETENTION_COST = 53
RESET_RESCUES_CARRY_FAILURE_WITH_RETENTION_COST = 2
```

These remain secondary descriptive flags and do not alter the PASS verdict.

## 15. Scientific interpretation

The KCL-6.5.9 NEGATIVE result was caused by insufficient support, not by absence
of positive-class heterogeneity.

Fresh replication now establishes that at least two distinct positive action
regimes are supported:

```
C_SAFE_ONLY
B_AND_C_SAFE
```

and unexpectedly a third positive action regime also reaches support:

```
B_SAFE_ONLY
```

Therefore the pooled binary target:

```
SAFE_RESET_OPPORTUNITY
```

is too coarse for the next stage of action selection research.

This does **not** mean a controller is ready. It means the next scientific
target should distinguish which safe action regime applies before future
outcomes are observed.

## 16. Architectural consequence

Evidence now supports moving from:

```
predict whether any reset is safe
```

toward the more specific question:

```
predict which boundary action regime is active
```

But do not yet:

- deploy A/B/C online selection;
- train on protected confirmatory seeds;
- use future-task outcomes as features;
- tune taxonomy from these results;
- open KCL-7.

The controller remains **not qualified**.

## 17. Verdict

```
KCL-6.5.9.1 = PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

The replicated evidence supports a real positive-class boundary-regime
structure, while rejecting stable replication of the catastrophic-carry branch
at the current cohort size.

## 18. Next scientific step

The next admissible milestone is:

```
KCL-6.5.9.2 — Boundary Regime Predictability Qualification
```

Before execution it must freeze:

- the prediction target derived from the now-supported positive regimes;
- a fresh non-confirmatory train/validation cohort;
- strict boundary-time anti-leakage features;
- whole-seed splitting;
- baselines including boundary index and H4 drift;
- class-imbalance handling fixed before outcomes;
- qualification metrics and confidence intervals;
- STOP/PIVOT rules.

The protected confirmatory cohort must remain untouched until a regime predictor
qualifies and is frozen.

KCL-7 remains **NOT STARTED**.
