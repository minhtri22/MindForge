# KCL-6.5.9.2 — Boundary Regime Predictability Qualification

## Status

```
NEGATIVE
BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED
```

KCL-6.5.9.2 tested whether the replicated safe-action regimes from
KCL-6.5.9.1 are predictable **at the boundary before future-task
counterfactual outcomes are observed**.

The frozen low-capacity predictor RPQ-v1 did not qualify.

This is a scientific negative, not an implementation failure:

- the four-class target remained adequately supported in fresh training and
  validation cohorts;
- the train/validation split remained whole-seed and disjoint;
- the frozen train-only rule artifact was loaded without refit;
- all validation integrity checks passed;
- protected confirmatory seeds remained untouched.

## 1. Trigger

KCL-6.5.9.1 closed:

```
PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

Fresh evidence supported multiple positive action regimes:

```
C_ONLY
B_AND_C_SAFE
B_ONLY
```

with `A_ONLY` completing the exhaustive safe-action target.

The next admissible question was therefore not whether action regimes exist,
but whether regime identity is predictable from state observable at the
boundary.

## 2. Frozen target

KCL-6.5.9.2 used:

```
SAFE_ACTION_SET-v1
```

with four exhaustive classes:

```
A_ONLY
C_ONLY
B_AND_C_SAFE
B_ONLY
```

The target was reconstructed from the unchanged A/B/C counterfactual safety
predicates.

No future "best-action" optimization target was introduced.

## 3. Frozen protocol

Protocol:

```
docs/research/kernel-continual-learning/kcl6592-protocol.md
```

Protocol freeze commit:

```
6d01ad18028a1eed507c4c5582132cb75e28ed98
```

Protocol SHA-256:

```
ad5dd1de4187a700be603c4af0c3c34e8deb381677457ca00938409a2c87b4f1
```

The protocol froze before train or validation outcomes:

- exact 240 whole-seed training cohort;
- exact 120 whole-seed validation cohort;
- four-class SAFE_ACTION_SET-v1 target;
- boundary-time-only global feature contract;
- RPQ-v1 model family/hyperparameters;
- stage/H4 baselines;
- train and validation support gates;
- exact qualification thresholds;
- whole-seed bootstrap;
- two-stage anti-leakage execution;
- STOP/PIVOT conditions.

## 4. Frozen cohorts

Total fresh non-confirmatory cohort:

```
360 seeds
1080 boundary instances
```

Split:

```
training   = 240 seeds × 3 = 720 boundaries
validation = 120 seeds × 3 = 360 boundaries
```

Generation provenance:

```
Python 3.12
random.Random(6592).sample(range(300001, 900000), 360)
```

The explicit seed lists in the protocol are authoritative.

The cohorts are disjoint from:

- KCL-6.5.6 discovery seeds;
- KCL-6.5.9.1 replication seeds;
- the protected confirmatory cohort;
- each other.

## 5. Boundary-time representation

RPQ-v1 used only frozen boundary-time global state:

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

Forbidden:

- next-task identity or tensors;
- A/B/C future outcomes;
- safe labels;
- future gradients/loss;
- validation statistics during fitting;
- KCL-6.5.8 localized features.

## 6. Frozen model

RPQ-v1:

```
class-balanced L2 multinomial logistic regression
lambda = 1.0
deterministic PyTorch LBFGS
train-only standardization
train-only class weights
no hyperparameter search
no feature selection
no validation tuning
```

Baselines:

```
B-STAGE
B-H4
B-STAGE-H4
```

The strongest baseline by validation macro recall was the qualification
baseline.

## 7. Phase A — train/freeze

Successful canonical train/freeze workflow:

```
run 35416050982
source commit 9d1db04afde8fb4adf354ca45e1c82ae1c4a676e
```

Training evidence SHA-256:

```
295bcae868e7989481e38c24eb87b007d8fa1afb98b15854b2fc5d006982d66e
```

Frozen rule SHA-256:

```
a243ec57d7e9f28f361597eb0a25da1ec2373f2f06458b9a3c73bd618021b89b
```

Training workflow artifact:

```
Artifact ID: 10576042235
ZIP SHA-256:
3f4f14b4056e0a764da7ff8a0218f11e41acba042a67160d879c0120466faee8
```

Training support:

| Class | Count | Unique seeds |
|---|---:|---:|
| `A_ONLY` | 202 | 154 |
| `C_ONLY` | 461 | 232 |
| `B_AND_C_SAFE` | 34 | 34 |
| `B_ONLY` | 23 | 23 |

All classes exceeded:

```
count >= 10
unique_seed_count >= 10
```

Therefore validation was authorized.

Validation seeds executed before freeze:

```
NO
```

## 8. Training diagnostics

Training metrics were descriptive only.

RPQ-v1 training:

```
accuracy     = 0.5250
macro recall = 0.5084
macro F1     = 0.3416
```

Training per-class recall:

```
A_ONLY       = 0.0891
C_ONLY       = 0.7028
B_AND_C_SAFE = 0.6765
B_ONLY       = 0.5652
```

The training behavior already suggested that `A_ONLY` was poorly separated
by the frozen global representation. No model changes were allowed after this
observation.

## 9. Phase B — canonical validation

Validation workflow source commit:

```
ea9dc4d2f3f911c4ef10b45afab17419b66709e5
```

Official validation run:

```
35443075722
```

Workflow conclusion:

```
SUCCESS
```

Focused tests:

```
10 passed — KCL-6.5.9.2
10 passed — KCL-6.5.9.1
```

Canonical validation artifact:

```
Artifact ID: 10584905824
ZIP SHA-256:
1092b57ee27653fe858e764f7c7aa2344cc01c4f6d3917d941c95764fdb6eb19
```

Raw validation JSON SHA-256:

```
f9432d514cc584a0b826759dc203a3186945c80e189f7e61d0a2d90039d03eda
```

Exact raw evidence was subsequently preserved into the repository without a
scientific rerun.

Preservation workflow source commit:

```
1919f88538f3b8f8af7d3a752a9d548c6773a622
```

Machine-readable validation evidence commit:

```
c025d87bec94f623007c4eb6400ad2dce5560ed0
```

## 10. Validation integrity

All integrity requirements passed:

- exactly 120 validation seeds;
- exactly 360 validation records;
- exactly three boundaries per seed;
- train/validation overlap absent;
- prior discovery/replication overlap absent;
- protected confirmatory cohort untouched;
- frozen rule SHA verified;
- rule loaded without refit;
- scaler unchanged;
- class weights unchanged;
- all features finite;
- target truth table valid;
- all A/B/C counterfactual integrity checks valid;
- no controller implemented;
- KCL-7 not started.

## 11. Validation target support

Validation support:

| Class | Count | Unique seeds | Boundary 1/2/3 |
|---|---:|---:|---|
| `A_ONLY` | 115 | 83 | 30 / 33 / 52 |
| `C_ONLY` | 212 | 116 | 90 / 87 / 35 |
| `B_AND_C_SAFE` | 18 | 18 | 0 / 0 / 18 |
| `B_ONLY` | 15 | 15 | 0 / 0 / 15 |

Every class exceeded:

```
count >= 5
unique_seed_count >= 5
```

Therefore:

```
REGIME_PREDICTABILITY_VALIDATION_SUPPORT_INSUFFICIENT
```

does **not** apply.

The scientific negative cannot be attributed to inadequate validation support.

## 12. RPQ-v1 validation performance

RPQ-v1:

```
accuracy        = 0.513889
macro precision = 0.318482
macro recall    = 0.419725
macro F1        = 0.311669
log loss        = 1.101829
```

Per-class results:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| `A_ONLY` | 0.2800 | **0.0609** | **0.1000** |
| `C_ONLY` | 0.7354 | 0.7736 | 0.7540 |
| `B_AND_C_SAFE` | 0.1633 | **0.4444** | **0.2388** |
| `B_ONLY` | 0.0952 | **0.4000** | **0.1538** |

Confusion matrix in frozen class order
`[A_ONLY, C_ONLY, B_AND_C_SAFE, B_ONLY]`:

```
[[  7, 59, 17, 32],
 [ 15,164, 17, 16],
 [  1,  0,  8,  9],
 [  2,  0,  7,  6]]
```

The dominant failure is not only rare-class confusion.

`A_ONLY`, with 115 validation instances, is almost never recognized:

```
recall(A_ONLY) = 0.0609
```

This strongly constrains interpretations based solely on rare-class sample
size.

## 13. Frozen baselines

Validation macro recall:

```
B-H4       = 0.330078
B-STAGE    = 0.458726
B-STAGE-H4 = 0.428171
RPQ-v1     = 0.419725
```

Strongest frozen baseline:

```
B-STAGE
macro recall = 0.458726
```

Required superiority:

```
RPQ macro recall >= best baseline + 0.05
                 >= 0.508726
```

Observed:

```
0.419725
```

Therefore RPQ-v1 did not merely fail to clear a large absolute threshold. It
also failed to outperform the stage-only baseline.

This is an important scientific result: the additional frozen global optimizer
and retention-state variables do not provide enough generalizable information
to justify the current multiclass prediction hypothesis.

## 14. Bootstrap uncertainty

Frozen validation bootstrap:

```
20,000 whole-seed resamples
RNG seed = 6592
no model refit
```

95% percentile intervals:

```
accuracy:
[0.4750, 0.5500]

macro F1:
[0.263788, 0.358430]

macro recall:
[0.333678, 0.508191]
```

Required:

```
bootstrap 95% macro-recall lower > 0.45
```

Observed:

```
0.333678
```

This gate failed decisively.

## 15. Qualification adjudication

Frozen gates required:

```
macro recall >= 0.60
macro F1 >= 0.50

per-class recall >= 0.50
per-class F1 >= 0.35

macro recall >= best baseline macro recall + 0.05

bootstrap macro-recall lower > 0.45
```

Failed gates:

```
macro_recall
macro_f1
recall:A_ONLY
f1:A_ONLY
recall:B_AND_C_SAFE
f1:B_AND_C_SAFE
recall:B_ONLY
f1:B_ONLY
baseline_superiority
bootstrap_macro_recall_lower
```

Passed per-class recall/F1 only for:

```
C_ONLY
```

Therefore:

```
KCL-6.5.9.2 = NEGATIVE
BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED
```

## 16. Scientific interpretation

KCL-6.5.9.1 established that multiple positive action regimes are real enough
to replicate.

KCL-6.5.9.2 now shows that this does **not** imply those regimes are
predictable from the currently frozen global boundary representation.

Two explanations remain scientifically live:

1. **representation insufficiency**
   - the action regime may be predictable in principle, but H1–H9 plus stage
     do not encode the discriminating state;

2. **target/action identifiability limitation**
   - safe-action regime may depend substantially on future-task interaction
     that is not identifiable from pre-boundary state alone at this level of
     abstraction.

KCL-6.5.9.2 does not distinguish these explanations.

It would be post hoc to conclude that nonlinear models or previously failed
localized features are the answer.

## 17. What this result rules out

The current evidence does not support:

- a controller driven by RPQ-v1;
- using the four-class predictor operationally;
- claiming H1–H9 global boundary state is sufficient;
- adding nonlinear models after seeing this validation;
- tuning lambda or thresholds on the validation cohort;
- adding KCL-6.5.8 localized F1–F13 features to rescue RPQ-v1;
- consuming the protected confirmatory cohort;
- opening KCL-7 from this line of evidence.

## 18. Relationship to earlier negatives

The result is consistent with, but stronger than, the earlier predictor
failures:

- KCL-6.5.6: no single scalar boundary-health signal qualified;
- KCL-6.5.7: global relational state failed discovery qualification;
- KCL-6.5.8: localized relational state failed discovery qualification;
- KCL-6.5.9: pooled binary target decomposition suggested hidden action
  heterogeneity;
- KCL-6.5.9.1: that heterogeneity replicated;
- KCL-6.5.9.2: even the better action-set target is not qualified as a
  boundary-time prediction problem under the frozen global representation.

Thus changing the target from pooled binary reset safety to replicated
safe-action regimes was scientifically useful, but it did not solve the
predictability problem.

## 19. STOP / PIVOT

Per frozen protocol:

### STOP

Stop RPQ-v1.

Do not:

- tune the same model;
- run nonlinear rescue models;
- add localized features post hoc;
- append more validation seeds;
- touch protected confirmatory seeds;
- implement a policy controller.

### PIVOT

Return to the representation/target hypothesis.

The next experiment must be separately preregistered and explicitly
distinguish whether failure is caused primarily by:

```
representation insufficiency
vs
pre-boundary target non-identifiability
```

without reusing the KCL-6.5.9.2 validation cohort for model selection.

## 20. Recommended next scientific milestone

Candidate:

```
KCL-6.5.9.3 — Boundary Action Identifiability Decomposition
```

The purpose should **not** be to train a stronger classifier immediately.

It should prospectively ask what information is necessary for action-regime
identification.

A defensible design should freeze at least three information sets on a new
non-confirmatory cohort:

1. `S0 = stage only`;
2. `S1 = current frozen global boundary state`;
3. `S2 = a separately justified richer pre-boundary representation`.

A separate oracle-information arm may measure the ceiling when future-task
interaction information is exposed, but oracle features must never enter an
operational predictor.

The scientific question becomes:

```
Does richer pre-boundary state materially close the identifiability gap,
or does most discriminative information only appear after future-task
interaction?
```

Only after that distinction is resolved should another predictor/controller
architecture be considered.

Protected confirmatory seeds remain untouched.

KCL-7 remains **NOT STARTED**.
