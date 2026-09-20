# MindForge Kernel Continual Learning — KCL-6.5.9.6 Mechanistic Representation Qualification

Status: **FROZEN BEFORE ANY KCL-6.5.9.6 SCIENTIFIC OUTCOME**

## 1. Trigger

KCL-6.5.9.5 closed:

```
NEGATIVE
NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN
```

The chain now supports two distinct statements:

1. `A_ONLY` is structurally heterogeneous — KCL-6.5.9.4 PASS.
2. Target refinement alone does not solve identifiability under frozen S2 —
   KCL-6.5.9.5 NEGATIVE.

The unresolved mechanism is especially:

```
MECH{P+R,R}
```

where one unsafe reset jointly exhibits plasticity shortfall + retention-margin
violation while the other exhibits retention-margin violation.

The scientific question is:

> Does pre-boundary state become materially more informative when it represents
> the **counterfactual optimizer response geometry** induced by the exact
> boundary-reset interventions, while using only already-observed tasks?

No controller is authorized.

## 2. Mechanistic representation hypothesis

### H-MRIG

Frozen S2 loses information because its LRBS-v1 features summarize drift,
optimizer pressure and retention gradients primarily through normalized
shares/overlaps. They do not directly represent how the exact reset policies
B/C transform a plausible adaptation update and its retention cost.

KCL-6.5.9.6 introduces:

```
MRIG-v1
Mechanistic Reset-Interference Geometry
```

The hypothesis is that `MECH{P+R,R}` becomes identifiable when the
representation explicitly measures, before the future task is bound:

- how B/C resets change the effective update along an observed adaptation
  gradient;
- how those same virtual updates interact with the observed retention
  objective;
- whether one reset exhibits joint plasticity/retention badness while both
  exhibit retention badness.

This is a representation hypothesis, not a classifier-capacity hypothesis.

## 3. Anti-leakage probe contract

All MRIG-v1 quantities are computed **before the next/future task is bound**.

At boundary t, define from already-observed tasks only:

### 3.1 Current-task gradient

```
g_cur = gradient of full current observed task cross-entropy
```

where current observed task is the latest task already learned at that
boundary.

### 3.2 Retention gradient

```
g_ret = gradient of mean cross-entropy over all observed tasks
```

This is the same observed-task retention objective used by LRBS-v1.

No future-task examples, labels, gradients, losses, policy outcomes, safe flags
or KCL-6.5.9.4/5 target labels enter the probe.

## 4. Exact virtual reset intervention

For each frozen policy:

```
A = A_CARRY_ALL
B = B_RESET_ALL
C = C_CARRY_STEP_RESET_MOMENTS
```

perform the following on deep copies only:

1. clone the current model and optimizer;
2. apply the exact KCL-6.5.5 boundary policy to the cloned optimizer;
3. copy `g_cur` into the cloned model gradients;
4. execute exactly one AdamW `optimizer.step()`;
5. define the virtual parameter update:

```
u_p = theta_after_virtual_step - theta_boundary
```

No training batch is sampled.
No replay is consumed.
No original model/optimizer state is mutated.
No future task is bound.

The virtual step is only a representation probe and is never continued as the
reference trajectory.

## 5. Per-policy mechanistic responses

For p in {A,B,C}, define with epsilon = 1e-12:

### Adaptation response

```
I_p = - <g_cur, u_p> / (||g_cur||^2 + eps)
```

Larger positive values mean a larger first-order descent response along the
already-observed adaptation direction.

### Retention cost

```
R_p = <g_ret, u_p> / (||g_ret||^2 + eps)
```

Positive values imply first-order increase in the observed retention objective;
negative values imply first-order decrease.

### Step scale

```
S_p = ||u_p|| / (||g_cur|| + eps)
```

Define reset contrasts versus A:

```
dI_B = I_B - I_A
dI_C = I_C - I_A

dR_B = R_B - R_A
dR_C = R_C - R_A

lS_B = log((S_B + eps) / (S_A + eps))
lS_C = log((S_C + eps) / (S_A + eps))
```

## 6. MRIG-v1 feature set

Predictor-visible MRIG-v1 is intentionally **B/C exchange-symmetric**, matching
the identity-invariant mechanism multiset target.

Exactly ten features are frozen:

```
M1_CURRENT_RETENTION_GRAD_COSINE
  = cosine(g_cur, g_ret)

M2_MIN_PLASTICITY_CONTRAST
  = min(dI_B, dI_C)

M3_MAX_PLASTICITY_CONTRAST
  = max(dI_B, dI_C)

M4_MIN_RETENTION_COST_CONTRAST
  = min(dR_B, dR_C)

M5_MAX_RETENTION_COST_CONTRAST
  = max(dR_B, dR_C)

M6_PLASTICITY_CONTRAST_GAP
  = abs(dI_B - dI_C)

M7_RETENTION_CONTRAST_GAP
  = abs(dR_B - dR_C)

M8_BOTH_RETENTION_BADNESS
  = min(max(dR_B,0), max(dR_C,0))

M9_MAX_JOINT_BADNESS
  = max(
      max(-dI_B,0) * max(dR_B,0),
      max(-dI_C,0) * max(dR_C,0)
    )

M10_STEP_SCALE_LOG_GAP
  = abs(lS_B - lS_C)
```

Interpretive mapping:

- M8 tests whether both resets simultaneously carry retention-cost signal;
- M9 tests whether at least one reset simultaneously carries adaptation
  shortfall + retention-cost signal;
- M6/M7 encode asymmetry required to distinguish mixed mechanism structure;
- M10 captures B-vs-C optimizer-state response-scale divergence without
  exposing policy identity.

No feature selection or post-outcome feature deletion/addition is allowed.

Identity-specific `I_p/R_p/S_p` may be stored in diagnostic details but may
not be predictor inputs.

## 7. Frozen targets

### Primary target

```
Y_PRR:
POS := A_ONLY AND mechanism_signature == MECH{P+R,R}
NEG := otherwise
```

computed with the exact frozen KCL-6.5.9.4 taxonomy.

### Secondary diagnostic targets

```
Y_PR:
POS := A_ONLY AND mechanism_signature == MECH{P,R}
NEG := otherwise

Y_A:
POS := A_ONLY
NEG := otherwise
```

Only Y_PRR determines the primary KCL-6.5.9.6 verdict.

## 8. Frozen representation arms

### S2 — baseline

Exact frozen KCL-6.5.9.5 primary representation:

```
stage + H1..H9 + LRBS-v1 F1..F13
```

### S3 — mechanistic candidate

```
S3 = S2 + MRIG-v1 M1..M10
```

No other representation arm is primary.

## 9. Frozen model family

For every target × arm use exactly the KCL-6.5.9.5 binary model family:

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
- hidden layer;
- hyperparameter search;
- threshold tuning;
- feature selection;
- oversampling;
- validation refit;
- target-specific feature set.

Thus the primary experimental difference is representation S2 vs S3.

## 10. Fresh prospective cohort

Generate exactly 720 fresh non-confirmatory seeds with:

```
Python 3.12
random.Random(6596).sample(range(5000001, 7000000), 720)
```

Split in generated order:

```
first 480 = TRAIN
last  240 = VALIDATION
```

Each seed contributes exactly three boundaries:

```
TRAIN      = 1440 boundaries
VALIDATION =  720 boundaries
```

Frozen cohort checksums over comma-joined decimal seed strings:

```
ALL:
f96a7f4c5c8f45234c9108a6eb184b941bcd464398f34e2d5798fe722a24aade

TRAIN:
3c2b02dccac5f7344daf2ffdb22b2dd7f581af5bbdd92c5c8481c001e0ed19d6

VALIDATION:
f036e088b316f8988df27bbb088f87d50ac52efa062ad5058ccf8a35b0151051
```

Required:

- train ∩ validation = empty;
- no overlap with KCL-6.5.6 protected/discovery cohort;
- no overlap with KCL-6.5.9.1/.2/.3/.4/.5 cohorts;
- protected confirmatory seeds remain untouched.

## 11. Support gates

For Y_PRR:

### Train

Both classes:

```
count >= 50
unique_seed_count >= 40
```

### Validation

Both classes:

```
count >= 25
unique_seed_count >= 20
```

The same thresholds are reported for Y_PR and Y_A diagnostics, but only Y_PRR
support can authorize/stop the primary study.

If Y_PRR train support fails:

```
NEGATIVE
MRIG_PRIMARY_TARGET_TRAIN_SUPPORT_INSUFFICIENT
```

Validation remains closed.

If Y_PRR validation support fails:

```
NEGATIVE
MRIG_PRIMARY_TARGET_VALIDATION_SUPPORT_INSUFFICIENT
```

No seed extension is allowed.

## 12. Two-phase execution

### Phase A — TRAIN / FREEZE

Using TRAIN only:

1. build S2 + MRIG-v1 records;
2. verify anti-leakage and virtual-probe state preservation;
3. verify Y_PRR support;
4. fit S2 and S3 models for Y_PRR, Y_PR and Y_A;
5. freeze all six model rules, scalers and class weights;
6. preserve exact train evidence + rule artifact.

Validation seeds may not execute before the rule artifact is committed.

### Phase B — VALIDATION

Using the committed frozen rule only:

1. generate frozen validation cohort once;
2. no refit;
3. evaluate all frozen models;
4. run frozen paired whole-seed bootstrap;
5. adjudicate.

## 13. Absolute qualification

For a binary target/arm, QUALIFIED iff all hold:

```
macro recall >= 0.60
macro F1 >= 0.50
POS recall >= 0.50
NEG recall >= 0.50
POS F1 >= 0.35
NEG F1 >= 0.35
whole-seed bootstrap 95% lower bound of macro recall > 0.45
```

These are unchanged from KCL-6.5.9.5.

## 14. Primary representation-gain test

For Y_PRR on the same validation seeds:

```
D_MRIG = macro_recall(Y_PRR,S3) - macro_recall(Y_PRR,S2)
```

Frozen paired bootstrap:

```
20,000 whole-seed resamples
all three boundaries travel with sampled seed
RNG seed = 6596
no refit
```

### H-MRIG PASS predicate

All must hold:

```
S3(Y_PRR) is QUALIFIED
D_MRIG >= +0.10
95% paired bootstrap CI lower(D_MRIG) > +0.03
```

The S2 baseline itself need not qualify; the test asks whether MRIG-v1 resolves
the previously observed representation gap.

## 15. Primary adjudication

### PASS

If H-MRIG passes:

```
PASS
MRIG_V1_QUALIFIES_MECH_PRR_REPRESENTATION
```

### NEGATIVE — qualified but insufficient gain

If S3 qualifies but the gain gate fails:

```
NEGATIVE
MRIG_V1_QUALIFIED_BUT_NO_MATERIAL_GAIN_OVER_S2
```

### NEGATIVE — unqualified

If S3 does not qualify:

```
NEGATIVE
MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION
```

### REVISE

Only technical/provenance/integrity failure may produce REVISE.

Scientific threshold failure is NEGATIVE.

## 16. Secondary diagnostics

Report without changing the verdict:

- S2/S3 metrics for Y_PR and Y_A;
- `D_PR = S3(Y_PR)-S2(Y_PR)`;
- `D_A = S3(Y_A)-S2(Y_A)`;
- S2/S3 log loss;
- target prevalence and boundary-index counts;
- MRIG-v1 feature distributions;
- identity-specific virtual-response details;
- whether gains are concentrated by boundary index.

No secondary diagnostic may rescue the primary verdict.

## 17. Integrity requirements

Each phase requires:

1. exact frozen seed checksums;
2. exact seed/record counts;
3. exactly boundaries {1,2,3} per seed;
4. prior/protected overlap absent;
5. all S2/MRIG features finite;
6. exact KCL-6.5.9.4 mechanism taxonomy;
7. Y_PRR and Y_PR strict subsets of Y_A;
8. virtual probe uses only current/observed tasks;
9. future task not bound during MRIG extraction;
10. original model unchanged by MRIG extraction;
11. original optimizer unchanged by MRIG extraction;
12. gradients cleared after MRIG extraction;
13. all B/C-visible predictor features exchange-symmetric;
14. A/B/C scientific counterfactual integrity valid;
15. LRBS-v1 share sums valid;
16. validation rule exact/frozen;
17. no validation refit;
18. no controller;
19. protected confirmatory untouched;
20. KCL-7 not started.

## 18. Scope exclusions

KCL-6.5.9.6 does not:

- use future-task probes;
- tune MRIG features after outcomes;
- alter the safe-action contract;
- alter failure-mode taxonomy;
- increase classifier capacity;
- implement a controller;
- consume protected confirmatory seeds;
- open KCL-7.

## 19. STOP / PIVOT

### If PASS

MRIG-v1 is qualified as a research representation for `MECH{P+R,R}`.
Do not immediately implement a controller.

The next study must independently replicate the representation gain or test a
mechanism-informed decision rule on another separately preregistered cohort.

### If NEGATIVE

Do not add more MRIG features post hoc and do not increase model capacity.

Use the frozen result to decide whether the remaining gap requires:

- a future-task interaction representation;
- a temporal/multi-boundary representation;
- or a reformulation of the mechanistic hypothesis.

A new preregistration is required.

## 20. Required artifacts

```
docs/research/kernel-continual-learning/kcl6596-protocol.md
experiments/kernel_cl/kcl6596_mechanistic_representation.py
tests/test_kernel_cl_kcl6596.py
.github/workflows/kernel-cl-kcl6596-train.yml
experiments/kernel_cl/results/kcl6596_train.json
experiments/kernel_cl/results/kcl6596_rule.json
.github/workflows/kernel-cl-kcl6596-validate.yml
experiments/kernel_cl/results/kcl6596_validation.json
docs/research/kernel-continual-learning/kcl6596-paper.md
Lineage.md
README.md
```

No controller artifact is authorized.
