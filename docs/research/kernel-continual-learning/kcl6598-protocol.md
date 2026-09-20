# MindForge Kernel Continual Learning — KCL-6.5.9.8 Mechanism-Specific Future-Interaction Qualification

Status: **FROZEN BEFORE ANY KCL-6.5.9.8 SCIENTIFIC OUTCOME**

## 1. Trigger

KCL-6.5.9.7 closed:

```
NEGATIVE
TRIG_V1_DOES_NOT_QUALIFY_TEMPORAL_MECH_PRR_REPRESENTATION
```

The active KCL-6.5.9.x chain has now rejected, under the frozen low-capacity
model family:

1. global static boundary state as sufficient;
2. localized static S2 as sufficient;
3. mechanism-specific hard-target refinement alone;
4. static observed-task reset-response MRIG-v1 as sufficient;
5. one-transition historical TRIG-v1 as sufficient.

KCL-6.5.9.3 previously observed the only notable positive information increment:

```
FUTURE-PROBE-v1 O - S2 macro recall = +0.08347
95% CI = [-0.01100,+0.17835]
```

on the broad four-class SAFE_ACTION_SET-v1 target. It did not qualify there.

The still-unanswered question is narrower and mechanism-specific:

> Does controlled zero-step interaction with the actual next task materially
> identify the replicated hard mechanism `MECH{P+R,R}`?

KCL-6.5.9.8 is the terminal information-class discriminator for the active
KCL-6.5.9.x sequence.

No controller or KCL-7 execution is authorized.

## 2. Frozen hypothesis

### H-FUTURE

The unresolved `MECH{P+R,R}` target may depend on interaction between the
current boundary state and the actual next-task gradient.

If that information is materially necessary, then adding the already-existing
FUTURE-PROBE-v1 representation to frozen S2 should:

1. produce a qualified Y_PRR predictor;
2. improve macro recall by a large preregistered margin;
3. show a positive paired whole-seed confidence bound.

This is an information-availability test, not a feature-search or
classifier-capacity test.

## 3. Exact future probe

Reuse **exactly** the pre-existing KCL-6.5.9.3 FUTURE-PROBE-v1 feature contract:

```
P1_NEXT_TASK_LOSS
P2_NEXT_GRAD_NORM
P3_NEXT_GRAD_DRIFT_COSINE
P4_NEXT_GRAD_PRESSURE_COSINE
P5_NEXT_GRAD_RETENTION_COSINE
P6_NEXT_GRAD_DRIFT_SHARE_OVERLAP
P7_NEXT_GRAD_PRESSURE_SHARE_OVERLAP
P8_NEXT_GRAD_RETENTION_SHARE_OVERLAP
```

The implementation must call/reuse the frozen KCL-6.5.9.3 probe logic rather
than redesigning P1-P8.

No P9, P10, action-specific future geometry, feature selection, or post-outcome
transformation is allowed.

## 4. Probe semantics

At each boundary:

1. compute legal pre-boundary S2 state;
2. expose the actual next task only to the zero-step probe;
3. compute next-task loss and gradient-derived P1-P8;
4. do **not** perform an optimizer step;
5. verify model and optimizer are unchanged;
6. clear all gradients;
7. only then execute frozen A/B/C scientific counterfactual outcomes to derive
   the target.

The probe may not read:

- A/B/C counterfactual outcomes;
- safe_B / safe_C;
- final next-task accuracy;
- retention outcomes;
- mechanism label.

## 5. Frozen target

Primary:

```
Y_PRR:
POS := A_ONLY AND mechanism_signature == MECH{P+R,R}
NEG := otherwise
```

Secondary diagnostics:

```
Y_PR := A_ONLY AND MECH{P,R} vs rest
Y_A  := A_ONLY vs rest
```

Exact KCL-6.5.9.4 taxonomy remains frozen.

Only Y_PRR controls the primary verdict.

## 6. Frozen information arms

### S2 — pre-boundary baseline

Exact frozen KCL-6.5.9.5 S2:

```
stage + H1..H9 + LRBS-v1 F1..F13
```

### FUT — controlled future-interaction arm

```
FUT = S2 + exact FUTURE-PROBE-v1 P1..P8
```

Both arms are fitted from scratch on the same fresh KCL-6.5.9.8 TRAIN cohort.

MRIG-v1 and TRIG-v1 are intentionally excluded because their fresh validations
were NEGATIVE and including them would confound the information-class
comparison.

## 7. Frozen model family

Exactly the KCL-6.5.9.5-.7 low-capacity binary model family:

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

- nonlinear classifier;
- neural/tree/kernel rescue;
- hyperparameter search;
- threshold tuning;
- feature selection;
- oversampling;
- target-specific representation;
- validation refit.

## 8. Fresh prospective cohort

Generate exactly 720 fresh non-confirmatory seeds with:

```
Python 3.12
random.Random(6598).sample(range(10000001, 12000000), 720)
```

Split in generated order:

```
first 480 = TRAIN
last  240 = VALIDATION
```

Each seed contributes exactly three boundaries:

```
TRAIN      = 480 × 3 = 1440 records
VALIDATION = 240 × 3 =  720 records
```

Frozen SHA-256 of comma-joined decimal seed lists:

```
ALL:
6071784d3447116db94576f93ae55c8bfc00aa5b67582b4a3ca65461bcc9c222

TRAIN:
12478ab48bb834c536c652e5d89cd03d1e701518e774f70d5fde6483f2df45e9

VALIDATION:
866c24667f3c2ea4d5317fc4f6c40e9050c255b00e65e4129e5026320a3f7f49
```

Required:

- TRAIN ∩ VALIDATION = empty;
- no overlap with KCL-6.5.6 discovery/protected cohorts;
- no overlap with KCL-6.5.9.1-.7 cohorts;
- protected confirmatory seeds remain untouched.

## 9. Support gates

Primary Y_PRR:

### TRAIN

Both classes require:

```
count >= 50
unique_seed_count >= 40
```

### VALIDATION

Both classes require:

```
count >= 25
unique_seed_count >= 20
```

If TRAIN support fails:

```
NEGATIVE
FUTURE_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT
```

Validation remains closed.

If VALIDATION support fails:

```
NEGATIVE
FUTURE_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT
```

No seed extension is allowed.

## 10. Two-phase execution

### Phase A — TRAIN / FREEZE

Using TRAIN only:

1. generate S2;
2. apply exact FUTURE-PROBE-v1 P1-P8;
3. verify zero-step nonmutation/gradient cleanup;
4. execute A/B/C counterfactuals only after feature extraction;
5. derive Y_PRR/Y_PR/Y_A;
6. verify Y_PRR support;
7. fit S2 and FUT for all three targets;
8. freeze six model/scaler/class-weight rules;
9. preserve exact train evidence + rule artifact.

Validation seeds may not execute before the rule artifact is committed.

### Phase B — VALIDATION

Using only committed frozen rules:

1. execute exactly 240 validation seeds once;
2. no refit;
3. evaluate S2 and FUT;
4. perform frozen paired whole-seed bootstrap;
5. adjudicate.

## 11. Absolute qualification

For each target/arm, QUALIFIED iff all hold:

```
macro recall >= 0.60
macro F1 >= 0.50
POS recall >= 0.50
NEG recall >= 0.50
POS F1 >= 0.35
NEG F1 >= 0.35
whole-seed bootstrap 95% lower bound of macro recall > 0.45
```

Unchanged from KCL-6.5.9.5-.7.

## 12. Primary future-information gain

```
D_FUTURE =
macro_recall(Y_PRR,FUT)
-
macro_recall(Y_PRR,S2)
```

Frozen paired bootstrap:

```
20,000 whole-seed resamples
all three boundaries travel with each sampled seed
RNG seed = 6598
no refit
```

The strict future-information gate reuses the substantive Route-I magnitude
from KCL-6.5.9.3:

```
FUT(Y_PRR) is QUALIFIED
D_FUTURE >= +0.15
95% paired bootstrap CI lower(D_FUTURE) > +0.05
```

## 13. Primary adjudication

### PASS — future interaction closes an unqualified pre-boundary gap

If:

```
S2 is NOT QUALIFIED
AND future-information gate passes
```

then:

```
PASS
FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED_FOR_MECH_PRR
```

Interpretation: the tested pre-boundary state family is insufficient, while
zero-step interaction with the actual next task supplies material identifying
information.

### PASS — future interaction materially improves an already-qualified S2

If:

```
S2 is QUALIFIED
AND future-information gate passes
```

then:

```
PASS
FUTURE_INTERACTION_MATERIAL_GAIN_FOR_MECH_PRR
```

Interpretation: future interaction is materially useful but is not necessary
for base qualification.

### NEGATIVE — FUT qualifies but strict gain fails

```
NEGATIVE
FUTURE_INTERACTION_QUALIFIED_BUT_NO_MATERIAL_GAIN
```

### NEGATIVE — FUT does not qualify

```
NEGATIVE
FUTURE_INTERACTION_DOES_NOT_QUALIFY_MECH_PRR
```

### REVISE

Only technical/provenance/integrity failure may produce REVISE.

Scientific threshold failure is NEGATIVE.

## 14. Secondary diagnostics

Report without changing the verdict:

- S2/FUT metrics for Y_PR and Y_A;
- D_PR and D_A;
- S2/FUT log loss;
- P1-P8 feature distributions;
- boundary-index support/performance;
- S2 qualification stability relative to prior cohorts.

No secondary result may rescue the primary verdict.

## 15. Integrity requirements

Each phase requires:

1. exact frozen seed hashes;
2. exact seed/record counts;
3. exactly boundaries {1,2,3} per seed;
4. prior/protected overlap absent;
5. exact S2 + P1-P8 feature contract;
6. all features finite;
7. exact KCL-6.5.9.4 mechanism taxonomy;
8. Y_PR/Y_PRR strict subsets of Y_A;
9. probe uses actual next task but no future outcomes;
10. probe performs zero optimizer/model updates;
11. model state unchanged by probe;
12. optimizer state unchanged by probe;
13. gradients cleared before counterfactual execution;
14. A/B/C scientific counterfactual integrity valid;
15. LRBS share sums valid;
16. validation rule exact/frozen;
17. no validation refit;
18. no controller;
19. protected confirmatory untouched;
20. KCL-7 not started.

## 16. Scope exclusions

KCL-6.5.9.8 does not:

- create new future-probe features;
- combine MRIG/TRIG with FUTURE-PROBE-v1;
- use action outcomes as features;
- tune thresholds/model capacity;
- derive a controller;
- consume protected confirmatory seeds;
- execute reverse-synthesis backlog items;
- open KCL-7.

## 17. Terminal decision rule for active KCL-6.5.9.x

### If PASS

Do not immediately implement a controller.

Next:

1. independently replicate the future-interaction gain on a new preregistered
   cohort;
2. then conduct convergence review;
3. only after successful replication may a probe→observe→decide architecture
   become eligible for a controller qualification study.

### If NEGATIVE

Close the active KCL-6.5.9.x sequence.

Do not add KCL-6.5.9.9 as another feature/representation rescue.

Proceed to formal convergence review.

The separately preserved reverse-synthesis backlog may be considered only as
new post-review research programs.

## 18. Required artifacts

```
docs/research/kernel-continual-learning/kcl6598-protocol.md
experiments/kernel_cl/kcl6598_future_interaction.py
tests/test_kernel_cl_kcl6598.py
.github/workflows/kernel-cl-kcl6598-train.yml
experiments/kernel_cl/results/kcl6598_train.json
experiments/kernel_cl/results/kcl6598_rule.json
.github/workflows/kernel-cl-kcl6598-validate.yml
experiments/kernel_cl/results/kcl6598_validation.json
docs/research/kernel-continual-learning/kcl6598-paper.md
Lineage.md
README.md
```

No controller artifact is authorized.
