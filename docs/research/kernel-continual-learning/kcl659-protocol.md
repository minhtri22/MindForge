# MindForge Kernel Continual Learning — KCL-6.5.9 Boundary Regime Decomposition Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.9 SCIENTIFIC EXECUTION**

## 1. Trigger

KCL-6.5.8 closed:

```
NEGATIVE
LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED
```

Across KCL-6.5.6 → KCL-6.5.8, the pooled binary target

```
SAFE_RESET_OPPORTUNITY
```

did not yield a discovery-qualified predictor. The strongest lead remained
`H4_TASK_DRIFT_RELATIVE_L2`, while both global and localized multivariate
representations degraded out-of-seed performance.

The next question is therefore upstream of representation learning:

> Does the binary SAFE_RESET_OPPORTUNITY target collapse multiple distinct
> counterfactual response regimes into one label?

KCL-6.5.9 is a **decomposition / characterization milestone only**.

It does not train a classifier, choose an online action, tune a representation,
or open KCL-7.

## 2. Scientific hypothesis

### H-BRD

The frozen binary boundary target hides multiple action-relevant causal regimes
defined by the A/B/C counterfactual response pattern.

A regime is causal here only in the narrow intervention-response sense:
the same frozen boundary state is forked into the already-defined optimizer
boundary interventions A/B/C, and the regime records which interventions are
safe/beneficial under the frozen KCL-6.5.6 criteria.

This milestone does **not** claim a deeper structural causal model.

## 3. Source data is frozen

Use only the canonical KCL-6.5.8 discovery evidence:

```
experiments/kernel_cl/results/kcl658_discovery.json
```

Frozen Git blob SHA:

```
0a956a70ddb65d12a413176f84910ce889359973
```

Expected source contract:

- KCL-6.5.8 status = `NEGATIVE`;
- verdict = `LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED`;
- exactly 60 discovery records;
- exactly the 20 KCL-6.5.6 discovery seeds;
- 3 boundaries per seed;
- no confirmatory seed;
- every record has valid counterfactual A/B/C outcomes;
- every record has canonical integrity = true.

No model training or counterfactual rerun is permitted in KCL-6.5.9.

## 4. Untouched confirmatory cohort

The following seeds remain forbidden:

```
13635
13837
14039
14241
14443
14645
14847
15049
15251
15453
15655
15857
16059
16261
16463
16665
16867
17069
17271
17473
```

They may not be used for taxonomy discovery, support estimation, feature
engineering, threshold setting, classifier fitting, or hypothesis refinement.

## 5. Frozen upstream action criteria

Reuse the KCL-6.5.6 definitions exactly.

Policies:

```
A = A_CARRY_ALL
B = B_RESET_ALL
C = C_CARRY_STEP_RESET_MOMENTS
```

Constants:

```
STRICT_CURRENT_MIN      = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN       = 1/24
```

For reset policy P in {B,C} relative to A:

```
plasticity_gain(P) =
    P.auc - A.auc >= 0.01
    OR
    (A.final_accuracy < 0.95 AND P.final_accuracy >= 0.95)

retention_ok(P) =
    P.retention - A.retention >= -(1/24)

absolute_ok(P) =
    P.final_accuracy >= 0.95

safe_beneficial(P) =
    plasticity_gain(P)
    AND retention_ok(P)
    AND absolute_ok(P)
```

Define:

```
safe_B = safe_beneficial(B)
safe_C = safe_beneficial(C)
carry_failure = A.final_accuracy < 0.95
```

All quantities come only from already-canonical counterfactual outcomes.

## 6. Primary mutually-exclusive taxonomy

Every discovery boundary must be assigned to **exactly one** primary regime.

Assignment is defined as a truth table, not a priority heuristic:

### R1 — B_AND_C_SAFE

```
safe_B = true
safe_C = true
```

### R2 — B_SAFE_ONLY

```
safe_B = true
safe_C = false
```

### R3 — C_SAFE_ONLY

```
safe_B = false
safe_C = true
```

### R4 — CARRY_CATASTROPHIC_FAILURE

```
safe_B = false
safe_C = false
carry_failure = true
```

### R5 — A_SUFFICIENT

```
safe_B = false
safe_C = false
carry_failure = false
```

Here `A_SUFFICIENT` means only that carry-all meets the frozen absolute
next-task acquisition threshold `final_accuracy >= 0.95`; it does not mean A
is globally optimal.

The taxonomy must be:

- mutually exclusive;
- collectively exhaustive;
- deterministic;
- invariant to dictionary/order presentation of A/B/C outcomes.

## 7. Binary-label reconstruction

The primary regimes must reconstruct the old pooled target exactly:

```
SAFE_RESET_OPPORTUNITY = true
    iff regime in {B_AND_C_SAFE, B_SAFE_ONLY, C_SAFE_ONLY}
```

and false otherwise.

Required:

```
60 / 60 binary labels reproduced exactly
```

Any mismatch is `REVISE`, not a scientific negative result.

## 8. Secondary mechanistic flags

Secondary flags are **not additional primary regimes** and may overlap.

For each reset policy P in {B,C}, record:

- `P_PLASTICITY_GAIN`;
- `P_RETENTION_OK`;
- `P_ABSOLUTE_OK`;
- `P_SAFE_BENEFICIAL`.

Also define:

### RESET_PLASTICITY_GAIN_RETENTION_COST

True iff at least one of B or C:

```
plasticity_gain(P) = true
absolute_ok(P) = true
retention_ok(P) = false
```

This flag captures the mechanism already suggested by KCL-6.5.5 without making
the primary taxonomy overlap.

### RESET_RESCUES_CARRY_FAILURE_WITH_RETENTION_COST

True iff:

```
carry_failure = true
```

and at least one of B/C reaches `final_accuracy >= 0.95` while violating the
retention margin.

These flags are descriptive only.

## 9. Minimum support criterion

A primary regime is **SUPPORTED** only if both are true:

```
instance_count >= 5
unique_seed_count >= 3
```

This support rule is frozen before inspecting KCL-6.5.9 regime frequencies.

Observed regimes below this threshold remain real observations but are labeled
`RARE/UNDER-SUPPORTED` and cannot alone justify architecture changes.

## 10. Primary heterogeneity tests

Define positive-class regimes:

```
{B_AND_C_SAFE, B_SAFE_ONLY, C_SAFE_ONLY}
```

Define negative-class regimes:

```
{CARRY_CATASTROPHIC_FAILURE, A_SUFFICIENT}
```

### HET-ACTION

`SUPPORTED_ACTION_HETEROGENEITY = true` iff at least two distinct
positive-class regimes are SUPPORTED.

### HET-NEGATIVE

`SUPPORTED_NEGATIVE_HETEROGENEITY = true` iff both negative-class regimes are
SUPPORTED.

### HET-BINARY

`SUPPORTED_BINARY_HETEROGENEITY = HET-ACTION OR HET-NEGATIVE`.

The primary hypothesis H-BRD passes iff `SUPPORTED_BINARY_HETEROGENEITY` is
true.

## 11. Frozen scientific verdicts

If source/integrity/taxonomy reconstruction fails:

```
REVISE
BOUNDARY_REGIME_DECOMPOSITION_INVALID
```

If HET-BINARY is true:

```
PASS
BINARY_SAFE_RESET_TARGET_HIDES_SUPPORTED_CAUSAL_REGIMES
```

If HET-BINARY is false:

```
NEGATIVE
NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY
```

No threshold may be changed after seeing frequencies.

## 12. Statistical / characterization outputs

KCL-6.5.9 must report all of the following.

### 12.1 Regime support table

For every R1..R5:

- count;
- prevalence;
- unique seed count;
- support status;
- counts by boundary index 1/2/3.

### 12.2 Seed-cluster bootstrap prevalence intervals

Resample the 20 discovery seeds with replacement and keep all three boundaries
from each sampled seed.

Frozen:

```
resamples = 20,000
RNG seed = 659659
95% percentile interval
```

Report a prevalence CI for each R1..R5.

These intervals are descriptive and do not alter the support gate.

### 12.3 Binary compression information loss

Compute Shannon entropy in bits:

```
H(REGIME)
H(SAFE_RESET)
H(REGIME | SAFE_RESET)
```

Because SAFE_RESET is a deterministic function of REGIME, the conditional
entropy quantifies how much regime information is lost by collapsing to the old
binary label.

This metric is descriptive and has no pass/fail threshold.

### 12.4 Existing-state characterization only

For each primary regime report, without fitting a model:

- median and IQR of `H4_TASK_DRIFT_RELATIVE_L2`;
- boundary-index distribution.

No new features, thresholds, classifiers, or post-hoc selected combinations are
allowed.

## 13. Integrity tests required before scientific output

The implementation must prove:

1. canonical KCL-6.5.8 source blob SHA matches the frozen SHA;
2. source has 60 records;
3. source has exactly 20 discovery seeds × 3 boundaries;
4. confirmatory seeds are absent;
5. all source records have valid integrity;
6. safe_B/safe_C recomputation uses only frozen outcome thresholds;
7. old `SAFE_RESET_OPPORTUNITY` reproduces 60/60;
8. primary regime assignment is exactly-one for every record;
9. taxonomy is collectively exhaustive;
10. regime assignment is invariant to A/B/C dictionary ordering;
11. no model training is invoked;
12. no confirmatory workflow or rule artifact is created.

Failure of any integrity test prevents scientific adjudication.

## 14. Scope exclusions

KCL-6.5.9 does not:

- modify KCL-6.5.8;
- rerun A/B/C counterfactual training;
- train a boundary classifier;
- tune H4;
- add H10/H11 or new LRBS features;
- create a neural encoder;
- implement adaptive controller logic;
- use confirmatory seeds;
- open KCL-7;
- open reasoning, agents, RAG, OIR-PPV, or Local2API.

## 15. STOP / PIVOT conditions

### If PASS

STOP training another pooled binary `SAFE_RESET_OPPORTUNITY` controller.

PIVOT the next scientific milestone to **regime predictability qualification**:
first freeze a fresh, non-confirmatory train/validation design and test whether
pre-boundary state can distinguish the supported regimes.

The untouched confirmatory cohort remains untouched.

### If NEGATIVE

Do not create a regime-first controller.

If rare regimes were observed but under-supported, the only allowed next step is
a fresh non-confirmatory replication cohort with the same frozen taxonomy.

If essentially one regime dominates with no supported split, return to the
representation/target hypothesis rather than adding classifier complexity.

### If REVISE

Fix only implementation/provenance defects and rerun the same frozen protocol.
Do not alter taxonomy or support thresholds.

## 16. Required artifacts

```
docs/research/kernel-continual-learning/kcl659-protocol.md
experiments/kernel_cl/kcl659_boundary_regime_decomposition.py
tests/test_kernel_cl_kcl659.py
.github/workflows/kernel-cl-kcl659.yml
experiments/kernel_cl/results/kcl659_decomposition.json
docs/research/kernel-continual-learning/kcl659-paper.md
Lineage.md
```

No `kcl659_rule.json` and no confirmatory workflow are authorized.

## 17. Closure rule

A complete KCL-6.5.9 closure requires:

1. protocol freeze commit;
2. implementation + tests;
3. official GitHub Actions run;
4. raw evidence preserved;
5. paper written from canonical evidence;
6. append-only Lineage update;
7. KCL-7 remains NOT STARTED.
