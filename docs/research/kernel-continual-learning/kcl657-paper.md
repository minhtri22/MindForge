# KCL-6.5.7 — Relational Boundary-State Representation

## Abstract

KCL-6.5.6 showed that no pre-registered single scalar boundary-health signal qualified, although task-relative parameter drift (H4) came close. KCL-6.5.7 therefore tests a relational / multivariate hypothesis:

> a compact representation combining task-relative drift, optimizer moment geometry, and retention risk can predict SAFE_RESET_OPPORTUNITY better than either boundary index or H4 drift alone.

The pre-registered representation, RBS-v1, uses six base variables:

```
D  = task-relative parameter drift
M1 = AdamW first-moment RMS
M2 = AdamW sqrt(second-moment) RMS
P  = bias-corrected Adam pressure RMS
G  = drift/pressure cosine
R  = 1 - prior worst-task accuracy
```

After fold-local standardization it adds five relational terms:

```
D×P
D×R
P×R
G×R
M1×M2
```

A deterministic L2-regularized logistic classifier is trained under leave-one-seed-out evaluation. All scaler statistics, weights and probability threshold are fit using training seeds only.

The result is negative.

RBS-v1 achieves:

```
balanced accuracy = 0.44865
sensitivity       = 0.63415
specificity       = 0.26316
accuracy          = 0.51667
```

The frozen baselines are:

```
stage-only BA = 0.60270
H4 drift BA   = 0.65533
```

RBS-v1 is therefore substantially worse than the strongest scalar signal and fails every primary discovery requirement except none.

Official result:

```
KCL-6.5.7 = NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED
```

No rule artifact is frozen and the untouched confirmatory cohort is not executed.

The scientific implication is narrower than “multivariate representations do not work.” It shows that this specific low-dimensional linear interaction model is not an adequate Boundary State Representation. Simply combining drift, global optimizer-moment summaries and retention reserve through standardized pairwise products does not recover the missing health state.

## 1. Upstream motivation

KCL-6.5.6 closed:

```
NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

The strongest scalar candidate was:

```
H4_TASK_DRIFT_RELATIVE_L2
```

with:

```
BA   = 0.65533
sens = 0.73171
spec = 0.57895
```

It exceeded the stage-only baseline by +0.05263 but failed the frozen specificity >=0.60 gate.

This motivated a relational hypothesis rather than another scalar threshold.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl657-protocol.md`

Protocol commit:

`850453e0798b2f6c2488c6618549aeb52fde5658`

Protocol SHA-256:

`50617d793cf129f0dc99b79e29e8e7b6ad165588269a65db5f4006039db76ec3`

Scientific source:

`af3f149364fa1fab48bb728ec33422ae27d56134`

No feature, interaction, regularization strength, threshold rule or qualification gate was changed after discovery.

## 3. Discovery data

KCL-6.5.7 reuses only the canonical KCL-6.5.6 discovery evidence.

```
20 seeds
3 boundaries / seed
60 boundary instances
```

The target remains:

```
SAFE_RESET_OPPORTUNITY
```

The untouched confirmatory seeds from KCL-6.5.6 are not used.

## 4. RBS-v1 representation

Base variables:

```
D  = H4_TASK_DRIFT_RELATIVE_L2
M1 = H1_M1_RMS
M2 = H2_SQRT_M2_RMS
P  = H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS
G  = H6_DRIFT_PRESSURE_COSINE
R  = 1 - H8_PRIOR_WORST_ACCURACY
```

Fold-local z-standardization is applied to all six variables.

Primary feature vector:

```
[
 zD,
 zM1,
 zM2,
 zP,
 zG,
 zR,
 zD*zP,
 zD*zR,
 zP*zR,
 zG*zR,
 zM1*zM2
]
```

Dimension:

`11`.

## 5. Classifier

Frozen model:

```
L2-regularized logistic regression
lambda = 1.0
```

Optimization:

```
deterministic Newton updates
max iterations = 100
tolerance = 1e-10
```

For every LOSO fold:

1. hold out one entire seed;
2. fit scaler on the remaining 19 seeds;
3. fit logistic weights on the remaining 19 seeds;
4. fit the probability threshold on training scores only;
5. predict all three boundaries of the held-out seed.

Thus scaler, representation weights and threshold are all out-of-seed.

## 6. Primary discovery result

RBS-v1:

```
TP = 26
TN = 5
FP = 14
FN = 15
```

Metrics:

```
balanced accuracy = 0.44865
sensitivity       = 0.63415
specificity       = 0.26316
accuracy          = 0.51667
```

Frozen gates:

```
BA   >= 0.70
sens >= 0.65
spec >= 0.65
BA   >= max(stage,H4) + 0.03
```

RBS-v1 fails qualification.

## 7. Baselines

### Stage-only

```
BA   = 0.60270
sens = 0.73171
spec = 0.47368
```

### H4 task-relative drift

```
BA   = 0.65533
sens = 0.73171
spec = 0.57895
```

Best baseline:

```
0.65533
```

Required RBS-v1 superiority:

```
>= 0.68533
```

Observed:

```
0.44865
```

Therefore relational complexity did not improve generalization.

## 8. Frozen ablations

Ablations were descriptive only and were not eligible to replace RBS-v1.

### A-DP

```
[zD, zP, zD*zP]
BA = 0.50128
```

### A-DR

```
[zD, zR, zD*zR]
BA = 0.45058
```

### A-MOMENT

```
[zM1, zM2, zM1*zM2]
BA = 0.49936
```

### A-NO-RETENTION

RBS-v1 without retention terms:

```
BA = 0.53979
```

The best ablation remains worse than H4.

Notably, removing retention terms improves over full RBS-v1, but the protocol forbids selecting this post-outcome as a replacement model.

## 9. Interpretation

The result falsifies the specific hypothesis:

> a global low-dimensional linear representation of drift × optimizer moments × retention is sufficient to expose safe reset opportunity.

The result does **not** establish that relational state is irrelevant.

Several reasons remain scientifically plausible:

1. the useful state may be parameter-group or subspace specific rather than global;
2. interactions may be strongly nonlinear;
3. absolute moment magnitudes may be less important than alignment with particular model-update directions;
4. retention may need structural attribution to the parameters/moments being modified rather than one worst-task scalar;
5. the binary SAFE_RESET_OPPORTUNITY target may compress distinct boundary regimes that require different representations.

KCL-6.5.7 does not test these alternatives.

## 10. Architectural consequence

A simple learned linear Boundary State Encoder is not justified.

The evidence currently supports a more conservative architecture statement:

> the missing boundary-health state is not captured by either one global scalar or a small linear combination of global state summaries.

Before implementing a controller, the next hypothesis should investigate **localized / structured state**, not merely add more global interactions.

Candidate directions include:

- parameter-group-specific drift and moment geometry;
- layer/subspace-specific compatibility;
- protected-memory gradient overlap;
- retention attribution to parameter groups;
- boundary-state clustering into distinct regimes.

These require new pre-registration and must not reuse the untouched confirmatory cohort until a discovery rule is frozen.

## 11. Confirmatory phase

Discovery qualification failed.

Therefore:

```
rule artifact = NOT CREATED
confirm workflow = NOT CREATED
confirmatory seeds = UNTOUCHED
```

This follows the frozen protocol.

## 12. Integrity

All integrity checks pass:

- canonical KCL-6.5.6 discovery evidence loaded;
- exactly 60 discovery instances;
- confirmatory seeds absent;
- whole-seed holdout;
- fold-local scaler;
- fold-local logistic weights;
- fold-local threshold;
- future outcomes not used as features;
- KCL-7 not started.

## 13. Verdict

```
KCL-6.5.7 = NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED
```

This is a scientific negative result, not a pipeline failure.

## 14. Provenance

Protocol:

`850453e0798b2f6c2488c6618549aeb52fde5658`

Implementation:

`9f273b418d1eeb38ce3d7d02939991859f5091f4`

Contract tests:

`a0eb8959e0beb7429a5bcdc787e10d12113a1cbb`

Canonical scientific source:

`af3f149364fa1fab48bb728ec33422ae27d56134`

Official discovery workflow:

`35383442729`

Focused tests:

`20 passed (10 KCL-6.5.7 + 10 KCL-6.5.6)`

Artifact:

`10562674440`

Artifact ZIP SHA-256:

`4616dc689c9bad741de46dd33868fbc80d7157e0eb64d72123660fd01cbce2ff`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl657_discovery.json`

## 15. Next scientific requirement

Do not tune RBS-v1, regularization, threshold, or interaction set.

If the research continues, the next hypothesis should move from **global summary representation** to **localized boundary-state structure**.

A defensible next milestone is:

```
parameter-group drift
× parameter-group moment geometry
× protected-retention attribution
```

with discovery and confirmation governance defined before execution.

The untouched confirmatory cohort must remain untouched until that new discovery rule qualifies and is frozen.
