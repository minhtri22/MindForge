# MindForge Kernel Continual Learning — KCL-6.5.9.5 Mechanism-Specific Target Identifiability

Status: **FROZEN BEFORE ANY KCL-6.5.9.5 TRAIN OR VALIDATION OUTCOME**

## 1. Trigger

KCL-6.5.9.4 closed:

```
PASS
A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY
```

Two mechanism-multiset signatures were independently and stably replicated:

```
M_PR  = MECH{P,R}
M_PRR = MECH{P+R,R}
```

where:

```
P = PLASTICITY_SHORTFALL
R = RETENTION_MARGIN_VIOLATION
```

The scientific question is now:

> Are these two causally more specific failure targets more identifiable /
> predictable from pre-boundary information than the monolithic A_ONLY target?

This milestone tests target specificity, not classifier complexity.

## 2. Frozen target family

Every boundary receives three independent binary labels over the same full
boundary population.

### Y_A

```
POS := SAFE_ACTION_SET-v1 == A_ONLY
NEG := otherwise
```

### Y_PR

```
POS := A_ONLY AND mechanism_signature == MECH{P,R}
NEG := otherwise
```

### Y_PRR

```
POS := A_ONLY AND mechanism_signature == MECH{P+R,R}
NEG := otherwise
```

The mechanism signature is computed with the exact frozen KCL-6.5.9.4 failure
taxonomy and B/C exchange-invariant multiset rule.

No target merging, relabeling, thresholding, or rare-class regrouping is
allowed after outcomes are observed.

## 3. Frozen information sets

No new representation is introduced.

### S0 — stage only, diagnostic

```
STAGE_2
STAGE_3
```

### S1 — exact KCL-6.5.9.2 global state, diagnostic

```
STAGE_2
STAGE_3
H1_M1_RMS
H2_SQRT_M2_RMS
H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS
H4_TASK_DRIFT_RELATIVE_L2
H5_PRESSURE_TO_DRIFT_RATIO
H6_DRIFT_PRESSURE_COSINE
H7_PRIOR_MEAN_ACCURACY
H8_PRIOR_WORST_ACCURACY
H9_CURRENT_TASK_LOSS
```

### S2 — PRIMARY

S2 is the exact pre-boundary KCL-6.5.9.3 representation:

```
S1 + frozen LRBS-v1 F1..F13
```

No FUTURE-PROBE/O arm is used. The primary question is operational
pre-boundary predictability.

## 4. Frozen model family

For every target × information-set pair use exactly:

```
class-balanced L2 binary logistic regression
ridge lambda = 1.0
float64
train-only standardization
train-only class weights
deterministic PyTorch LBFGS
lr = 1.0
max_iter = 200
history_size = 20
tolerance_grad = 1e-9
tolerance_change = 1e-12
line_search = strong_wolfe
```

No:

- nonlinear model;
- hyperparameter search;
- feature selection;
- target-specific representation;
- threshold tuning;
- oversampling;
- validation refit;
- post-outcome seed extension.

The only intended primary difference is the target definition.

## 5. Fresh prospective cohort

Generate exactly 720 fresh non-confirmatory seeds with:

```
Python 3.12
random.Random(6595).sample(range(3000001, 5000000), 720)
```

Split in generated order:

```
first 480 = TRAIN
last  240 = VALIDATION
```

Each seed contributes exactly three boundaries.

Therefore:

```
TRAIN      = 480 × 3 = 1440 boundaries
VALIDATION = 240 × 3 = 720 boundaries
```

Frozen cohort checksums over comma-joined decimal seed strings:

```
ALL:
5463cd9804c8f4e857a5e5a32a85119f0ab459e5857dcc6a5123123c28b22318

TRAIN:
9ed96c29e86613ac10572f4079b080c5ae70638aa70c3080b4d1773e1736e2d7

VALIDATION:
c4f5b8d112cc8fbe7235a22e32ccfe33dcca0c265baca496c440a1517c67df0d
```

Required:

- train ∩ validation = empty;
- no overlap with KCL-6.5.6 discovery/protected seeds;
- no overlap with KCL-6.5.9.1, .2, .3, or .4 cohorts;
- protected confirmatory seeds remain untouched.

## 6. Label generation

For each boundary:

1. extract S0/S1/S2 features before the future counterfactual outcome;
2. execute the unchanged KCL-6.5.6 A/B/C counterfactual harness;
3. derive `SAFE_ACTION_SET-v1`;
4. if A_ONLY, derive the exact KCL-6.5.9.4 mechanism signature;
5. assign Y_A, Y_PR, Y_PRR.

Target/outcome data must never enter predictor features.

## 7. Support gates

For each binary target independently:

### Training

Both POS and NEG require:

```
count >= 50
unique_seed_count >= 40
```

### Validation

Both POS and NEG require:

```
count >= 25
unique_seed_count >= 20
```

If any target fails TRAIN support:

```
NEGATIVE
MECHANISM_TARGET_TRAIN_SUPPORT_INSUFFICIENT
```

Validation is not authorized.

If any target fails VALIDATION support:

```
NEGATIVE
MECHANISM_TARGET_VALIDATION_SUPPORT_INSUFFICIENT
```

No seed extension is allowed.

## 8. Two-phase execution

### Phase A — TRAIN / FREEZE

Using TRAIN only:

- generate records;
- verify integrity/support;
- fit S0/S1/S2 models for Y_A, Y_PR, Y_PRR;
- freeze all nine model rules including scalers and class weights;
- preserve exact train evidence and rule artifact.

Validation seeds must not execute before the frozen rule is committed.

### Phase B — VALIDATION

Using only the committed frozen rules:

- generate the frozen validation cohort once;
- do not refit;
- compute all metrics;
- run the frozen whole-seed bootstrap;
- adjudicate.

## 9. Metrics

For every target × information set report:

- confusion matrix;
- accuracy;
- precision/recall/F1 for POS and NEG;
- macro precision;
- macro recall;
- macro F1;
- log loss.

Primary metric:

```
macro recall = balanced accuracy for the binary target
```

This is chosen prospectively because the three targets have different
prevalence.

## 10. Absolute S2 qualification

An S2 target is QUALIFIED iff all hold:

```
macro recall >= 0.60
macro F1 >= 0.50
POS recall >= 0.50
NEG recall >= 0.50
POS F1 >= 0.35
NEG F1 >= 0.35
whole-seed bootstrap 95% lower bound of macro recall > 0.45
```

These are the same base qualification floors used in KCL-6.5.9.3, now applied
to each binary target.

S0/S1 are diagnostic only and cannot substitute for S2 in the primary
adjudication.

## 11. Primary target-specific improvement

On the same validation seeds and same S2 representation define:

```
D_PR  = macro_recall(S2, Y_PR)  - macro_recall(S2, Y_A)
D_PRR = macro_recall(S2, Y_PRR) - macro_recall(S2, Y_A)
```

Use:

```
20,000 paired whole-seed bootstrap resamples
all three boundaries travel with each sampled seed
RNG seed = 6595
no refit inside bootstrap
```

A mechanism target has TARGET-SPECIFIC IDENTIFIABILITY GAIN iff:

```
its S2 model is QUALIFIED
AND point delta >= 0.10
AND paired bootstrap 95% CI lower bound > 0.03
```

The A_ONLY model is always evaluated under the identical S2/model contract.

## 12. Primary hypotheses

### H-PR

`MECH{P,R}` is more identifiable than `A_ONLY` under the frozen S2 contract.

### H-PRR

`MECH{P+R,R}` is more identifiable than `A_ONLY` under the frozen S2
contract.

### Family-level PASS

Both H-PR and H-PRR must pass.

This conjunction avoids claiming that mechanism-specific decomposition
generally resolves identifiability when only one mechanism happens to be
predictable.

## 13. Adjudication

### PASS

If both mechanism targets achieve TARGET-SPECIFIC IDENTIFIABILITY GAIN:

```
PASS
BOTH_REPLICATED_MECHANISM_TARGETS_MORE_IDENTIFIABLE_THAN_A_ONLY
```

### NEGATIVE — mixed

If exactly one target achieves the gain:

```
NEGATIVE
MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN_NOT_GENERALIZED_ACROSS_BOTH_TARGETS
```

The individual positive route remains reported but does not justify the broad
family-level claim.

### NEGATIVE — none

If neither target achieves the gain:

```
NEGATIVE
NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN
```

### REVISE

Only technical/provenance/integrity defects may produce REVISE.

Scientific threshold failure is NEGATIVE.

## 14. Secondary diagnostics

Without changing the verdict, report:

- S0/S1/S2 metrics for every target;
- S2-S0 and S2-S1 macro-recall deltas;
- target prevalence and boundary-index distribution;
- train/validation calibration/log loss;
- whether any apparent gain is already available from stage alone.

No secondary diagnostic may replace the frozen primary gate.

## 15. Integrity requirements

Each phase requires:

1. exact frozen cohort checksum;
2. exact seed count;
3. exactly three boundaries per seed;
4. boundaries exactly {1,2,3};
5. train/validation disjoint;
6. all prior/protected overlap absent;
7. all S2 features finite and pre-boundary;
8. all LRBS-v1 share sums valid;
9. all A/B/C counterfactual integrity checks valid;
10. exact SAFE_ACTION_SET-v1 truth table;
11. exact KCL-6.5.9.4 mechanism taxonomy;
12. Y_PR and Y_PRR positives are strict subsets of Y_A positives;
13. no future-probe feature;
14. no validation refit;
15. no controller;
16. protected confirmatory cohort untouched;
17. KCL-7 not started.

## 16. Scope exclusions

KCL-6.5.9.5 does not:

- invent a new representation;
- use FUTURE-PROBE-v1;
- train nonlinear models;
- change the safe-action thresholds;
- redefine KCL-6.5.9.4 mechanisms;
- implement a controller;
- consume protected confirmatory seeds;
- open KCL-7.

## 17. STOP / PIVOT

### If PASS

Freeze the two qualified mechanism-specific predictors as **research evidence
only**, not a controller.

The next question may test whether a mechanism-specific decision rule improves
actual boundary intervention outcomes on a separately preregistered cohort.

### If NEGATIVE

Do not increase classifier capacity post hoc.

Use the route-level result to distinguish:

- target decomposition helped neither mode;
- or it helped only one mechanism and therefore does not generalize.

A new scientific hypothesis is required before another predictor study.

## 18. Required artifacts

```
docs/research/kernel-continual-learning/kcl6595-protocol.md
experiments/kernel_cl/kcl6595_mechanism_target_identifiability.py
tests/test_kernel_cl_kcl6595.py
.github/workflows/kernel-cl-kcl6595-train.yml
experiments/kernel_cl/results/kcl6595_train.json
experiments/kernel_cl/results/kcl6595_rule.json
.github/workflows/kernel-cl-kcl6595-validate.yml
experiments/kernel_cl/results/kcl6595_validation.json
docs/research/kernel-continual-learning/kcl6595-paper.md
Lineage.md
README.md
```

No controller artifact is authorized.
