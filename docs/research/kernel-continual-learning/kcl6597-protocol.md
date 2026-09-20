# MindForge Kernel Continual Learning — KCL-6.5.9.7 Temporal Mechanistic Representation Qualification

Status: **FROZEN BEFORE ANY KCL-6.5.9.7 SCIENTIFIC OUTCOME**

## 1. Trigger

KCL-6.5.9.6 closed:

```
NEGATIVE
MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION
```

The chain has now rejected:

1. global static boundary state as sufficient;
2. richer localized static S2 as sufficient;
3. mechanism-specific target refinement alone;
4. static observed-task reset-response geometry (MRIG-v1) as sufficient.

KCL-6.5.9.7 therefore tests a different representation class:

> whether **historically realized transition geometry across already completed
> boundaries** contains predictive information absent from a static boundary
> snapshot.

No controller or KCL-7 execution is authorized.

## 2. Temporal mechanistic hypothesis

### H-TRIG

At boundary t, the system has already observed the task transition that followed
boundary t-1.

Therefore, without using any future-task information for boundary t, it can ask:

> How did the virtual reset directions computed at boundary t-1 align with the
> gradient geometry of the task that actually arrived and is now already
> observed at boundary t?

This retrospective transfer geometry is available operationally at boundary t
and may reveal persistent transition structure that a static S3 snapshot cannot.

KCL-6.5.9.7 introduces:

```
TRIG-v1
Temporal Reset-Interference Geometry
```

TRIG-v1 is a history representation, not a classifier-capacity change.

## 3. Eligibility

Temporal history requires one completed prior transition.

Therefore primary records are **only**:

```
boundary 2
boundary 3
```

Boundary 1 is used only to initialize history and is never a prediction record.

Every eligible seed contributes exactly two prediction records.

## 4. Static probe state

At every boundary, before binding the next task, compute the exact frozen
KCL-6.5.9.6 MRIG probe state using only currently observed tasks:

- current-task gradient `g_cur,t`;
- observed-task retention gradient `g_ret,t`;
- virtual one-step updates `u_A,t`, `u_B,t`, `u_C,t`;
- frozen MRIG-v1 M1..M10.

The original model and optimizer must remain unchanged.

The full vectors are transient implementation state only. They must not be
serialized as predictor features or evidence payloads.

## 5. Retrospective transfer geometry

At eligible boundary t in {2,3}, let the archived probe from t-1 be:

```
g_cur,t-1
g_ret,t-1
u_A,t-1
u_B,t-1
u_C,t-1
```

and current observable gradients be:

```
g_cur,t
g_ret,t
```

All are historically available before the next task after boundary t is bound.

Define:

### 5.1 Gradient rotation

```
Q1_CURRENT_GRAD_ROTATION
  = cosine(g_cur,t-1, g_cur,t)

Q2_RETENTION_GRAD_ROTATION
  = cosine(g_ret,t-1, g_ret,t)
```

### 5.2 Retrospective adaptation alignment

For p in {A,B,C}:

```
X_p =
  - <g_cur,t, u_p,t-1>
    / (||g_cur,t|| ||u_p,t-1|| + eps)
```

Define reset contrasts versus A:

```
dX_B = X_B - X_A
dX_C = X_C - X_A
```

Predictor-visible exchange-symmetric summaries:

```
Q3_MIN_TRANSFER_PLASTICITY_CONTRAST = min(dX_B,dX_C)
Q4_MAX_TRANSFER_PLASTICITY_CONTRAST = max(dX_B,dX_C)
Q5_TRANSFER_PLASTICITY_GAP          = abs(dX_B-dX_C)
```

### 5.3 Retrospective retention alignment

For p in {A,B,C}:

```
Y_p =
  <g_ret,t, u_p,t-1>
  / (||g_ret,t|| ||u_p,t-1|| + eps)
```

Define:

```
dY_B = Y_B - Y_A
dY_C = Y_C - Y_A
```

Predictor-visible exchange-symmetric summaries:

```
Q6_MIN_TRANSFER_RETENTION_CONTRAST = min(dY_B,dY_C)
Q7_MAX_TRANSFER_RETENTION_CONTRAST = max(dY_B,dY_C)
Q8_TRANSFER_RETENTION_GAP          = abs(dY_B-dY_C)
```

### 5.4 Temporal change in static reset geometry

Using the already frozen B/C-symmetric MRIG-v1 features:

```
Q9_PLASTICITY_GAP_DELTA
  = M6_t - M6_t-1

Q10_RETENTION_GAP_DELTA
  = M7_t - M7_t-1

Q11_BOTH_RETENTION_BADNESS_DELTA
  = M8_t - M8_t-1

Q12_STEP_SCALE_GAP_DELTA
  = M10_t - M10_t-1
```

Exactly twelve TRIG-v1 features are frozen.

No post-outcome feature deletion, addition or transformation is permitted.

## 6. Exchange-symmetry requirement

The primary mechanism target is B/C identity invariant.

Therefore all predictor-visible TRIG-v1 features must be invariant to exchanging
B and C in both the archived and current probe state.

Identity-specific X/Y values may be stored only in transient diagnostics and
must not enter the predictor.

## 7. Frozen targets

Primary:

```
Y_PRR:
POS := A_ONLY AND mechanism_signature == MECH{P+R,R}
NEG := otherwise
```

Secondary diagnostics:

```
Y_PR := MECH{P,R} within A_ONLY vs rest
Y_A  := A_ONLY vs rest
```

Exact KCL-6.5.9.4 taxonomy remains frozen.

Only Y_PRR controls the primary verdict.

## 8. Frozen representation arms

### S3 — static baseline

Exact frozen KCL-6.5.9.6 candidate representation definition:

```
S3 = S2 + MRIG-v1 M1..M10
```

### S4 — temporal candidate

```
S4 = S3 + TRIG-v1 Q1..Q12
```

Both arms are fitted from scratch on the same fresh KCL-6.5.9.7 TRAIN cohort.
No KCL-6.5.9.6 validation data are reused for fitting.

## 9. Frozen classifier family

Exactly the same low-capacity family as KCL-6.5.9.5/.6:

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

No nonlinear model, hidden layer, hyperparameter search, feature selection,
threshold tuning, oversampling, target-specific feature set, or validation
refit.

## 10. Fresh prospective cohort

Generate exactly 1080 fresh non-confirmatory seeds with:

```
Python 3.12
random.Random(6597).sample(range(7000001, 10000000), 1080)
```

Split in generated order:

```
first 720 = TRAIN
last  360 = VALIDATION
```

Every seed produces exactly two eligible records:

```
TRAIN      = 720 × 2 = 1440 records
VALIDATION = 360 × 2 =  720 records
```

Frozen SHA-256 of comma-joined decimal seed lists:

```
ALL:
8afb9745bdb6d7c7d0c7973076a486867a42cb5d232cd1d9db18a920b96667b3

TRAIN:
7fcd7b700060d22d1d4adae3534db7835a3c3425b78a736309d391f283335025

VALIDATION:
86508c96cc1872e7a171324192642ae09be6532f44dfb7f3a38acbb4b70736c7
```

Required:

- TRAIN ∩ VALIDATION = empty;
- no overlap with KCL-6.5.6 discovery/protected seeds;
- no overlap with KCL-6.5.9.1-.6 cohorts;
- protected confirmatory cohort untouched.

## 11. Support gates

For primary Y_PRR only:

### TRAIN

Both POS and NEG require:

```
count >= 50
unique_seed_count >= 40
```

### VALIDATION

Both POS and NEG require:

```
count >= 25
unique_seed_count >= 20
```

If TRAIN support fails:

```
NEGATIVE
TRIG_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT
```

Validation remains closed.

If VALIDATION support fails:

```
NEGATIVE
TRIG_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT
```

No seed extension is allowed.

## 12. Two-phase execution

### Phase A — TRAIN / FREEZE

Using TRAIN only:

1. execute sequential trajectories;
2. compute boundary-1 probe only for history initialization;
3. create eligible boundary-2/3 S3 + TRIG-v1 records;
4. verify anti-leakage/history lineage;
5. verify Y_PRR support;
6. fit S3/S4 for Y_PRR, Y_PR and Y_A;
7. freeze six model rules/scalers/class weights;
8. preserve exact train evidence and rule artifact.

Validation seeds remain unopened until the rule artifact is committed.

### Phase B — VALIDATION

Using only the committed frozen rule:

1. execute frozen validation seeds once;
2. no refit;
3. evaluate S3/S4;
4. perform frozen paired whole-seed bootstrap;
5. adjudicate.

## 13. Absolute qualification

For each binary target/arm, QUALIFIED iff all hold:

```
macro recall >= 0.60
macro F1 >= 0.50
POS recall >= 0.50
NEG recall >= 0.50
POS F1 >= 0.35
NEG F1 >= 0.35
whole-seed bootstrap 95% lower bound of macro recall > 0.45
```

Unchanged from KCL-6.5.9.5/.6.

## 14. Primary temporal gain test

For Y_PRR:

```
D_TRIG =
macro_recall(Y_PRR,S4)
-
macro_recall(Y_PRR,S3)
```

Bootstrap:

```
20,000 paired whole-seed resamples
both eligible boundaries travel with each sampled seed
RNG seed = 6597
no refit
```

### H-TRIG PASS

All must hold:

```
S4(Y_PRR) is QUALIFIED
D_TRIG >= +0.10
95% paired bootstrap CI lower(D_TRIG) > +0.03
```

## 15. Primary adjudication

### PASS

```
PASS
TRIG_V1_QUALIFIES_TEMPORAL_MECH_PRR_REPRESENTATION
```

### NEGATIVE — S4 qualifies but gain insufficient

```
NEGATIVE
TRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S3
```

### NEGATIVE — S4 unqualified

```
NEGATIVE
TRIG_V1_DOES_NOT_QUALIFY_TEMPORAL_MECH_PRR_REPRESENTATION
```

### REVISE

Only technical, provenance or integrity failure may produce REVISE.

Scientific gate failure is NEGATIVE.

## 16. Secondary diagnostics

Without changing the primary verdict report:

- S3/S4 metrics for Y_PR and Y_A;
- `D_PR = S4(Y_PR)-S3(Y_PR)`;
- `D_A = S4(Y_A)-S3(Y_A)`;
- S3/S4 log loss;
- boundary-2 vs boundary-3 metrics;
- TRIG feature distributions;
- retrospective X/Y identity-specific diagnostic values;
- whether temporal gain is concentrated at one eligible boundary.

Secondary findings cannot rescue the primary result.

## 17. Integrity requirements

Each phase requires:

1. exact frozen seed hashes;
2. exact seed count;
3. exactly two prediction records per seed;
4. prediction boundaries exactly {2,3};
5. boundary 1 used only to initialize history;
6. previous probe belongs to same seed and immediately preceding boundary;
7. no prior/protected overlap;
8. all S3/TRIG features finite;
9. exact KCL-6.5.9.4 target taxonomy;
10. Y_PR/Y_PRR strict subsets of Y_A;
11. current probe computed before next task is bound;
12. temporal features use only archived prior-boundary probe + current observed gradients;
13. no previous counterfactual policy outcome/label enters TRIG;
14. original model/optimizer unchanged by probes;
15. gradients cleared;
16. predictor-visible features B/C exchange-symmetric;
17. scientific counterfactual harness valid;
18. LRBS share sums valid;
19. frozen validation rule exact;
20. no validation refit;
21. no controller;
22. protected confirmatory untouched;
23. KCL-7 not started.

## 18. Scope exclusions

KCL-6.5.9.7 does not:

- use current-boundary future-task features;
- use previous scientific target labels or A/B/C outcomes as predictor history;
- tune temporal features after outcomes;
- alter safe-action thresholds;
- alter mechanism taxonomy;
- increase classifier capacity;
- implement a controller;
- consume protected confirmatory seeds;
- open KCL-7.

## 19. STOP / PIVOT

### If PASS

TRIG-v1 becomes a qualified temporal research representation.

Do not build a controller immediately. The next KCL-6.5.9.x milestone must
independently replicate the temporal gain on another fresh cohort before any
decision-rule study.

### If NEGATIVE

Do not add temporal features post hoc.

The result would reject both static observed-task reset geometry and one-step
historical transition geometry under the current model family.

The next hypothesis must move to a genuinely different information class
(e.g. controlled observable future-task interaction or longer-horizon
transition state), or the 6.5.9.x line should close for convergence review if no
mechanistically distinct hypothesis remains.

## 20. Required artifacts

```
docs/research/kernel-continual-learning/kcl6597-protocol.md
experiments/kernel_cl/kcl6597_temporal_mechanistic_representation.py
tests/test_kernel_cl_kcl6597.py
.github/workflows/kernel-cl-kcl6597-train.yml
experiments/kernel_cl/results/kcl6597_train.json
experiments/kernel_cl/results/kcl6597_rule.json
.github/workflows/kernel-cl-kcl6597-validate.yml
experiments/kernel_cl/results/kcl6597_validation.json
docs/research/kernel-continual-learning/kcl6597-paper.md
Lineage.md
README.md
```

No controller artifact is authorized.
