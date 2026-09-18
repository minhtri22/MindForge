# MindForge Kernel Continual Learning — KCL-6.5.7 Relational Boundary-State Representation Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.7 DISCOVERY OR CONFIRMATORY EXECUTION**

## 1. Trigger

KCL-6.5.6 closed:

```
NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

The strongest scalar candidate was:

```
H4_TASK_DRIFT_RELATIVE_L2
```

with leave-one-seed-out:

```
balanced accuracy = 0.65533
sensitivity       = 0.73171
specificity       = 0.57895
```

It passed balanced-accuracy, sensitivity, and stage-superiority gates but failed the frozen specificity >=0.60 gate.

Therefore KCL-6.5.7 tests a new hypothesis:

> boundary health is not encoded by one scalar; it is encoded by a relational state involving task-relative parameter drift, optimizer moment geometry, and retained-knowledge reserve.

KCL-6.5.7 does not add another scalar H10/H11 and does not implement an adaptive controller.

## 2. Hypothesis

### H-RBS

A low-dimensional multivariate boundary-state representation available before the next task can predict `SAFE_RESET_OPPORTUNITY` better than both:

1. boundary index alone;
2. the strongest KCL-6.5.6 scalar H4 task-relative drift.

The representation is called:

```
RBS-v1
Relational Boundary State v1
```

## 3. Data and target

Discovery reuses the canonical KCL-6.5.6 discovery records only:

```
experiments/kernel_cl/results/kcl656_discovery.json
```

No discovery counterfactuals are rerun.

Primary target remains unchanged:

```
SAFE_RESET_OPPORTUNITY
```

with exactly the KCL-6.5.6 definition.

Discovery cohort:

```
20 seeds × 3 boundaries = 60 instances
```

Confirmatory cohort remains the untouched KCL-6.5.6 confirmatory seeds and is not run unless RBS-v1 discovery-qualifies and its complete model artifact is committed first.

## 4. Anti-leakage

RBS-v1 may use only feature values already emitted by KCL-6.5.6 before next-task counterfactual execution.

It may not use:

- future-task tensors;
- future task name/family;
- A/B/C future outcomes;
- `BEST_SAFE_ACTION`;
- `CARRY_PLASTICITY_FAILURE`;
- any future-task loss/gradient.

The only supervised value is the discovery target `SAFE_RESET_OPPORTUNITY`.

## 5. RBS-v1 base variables

Use exactly these six KCL-6.5.6 boundary features:

### D — task-relative drift

```
D = H4_TASK_DRIFT_RELATIVE_L2
```

### M1 — first-moment magnitude

```
M1 = H1_M1_RMS
```

### M2 — second-moment scale

```
M2 = H2_SQRT_M2_RMS
```

### P — bias-corrected Adam pressure

```
P = H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS
```

### G — drift / pressure direction

```
G = H6_DRIFT_PRESSURE_COSINE
```

### R — retention risk

```
R = 1 - H8_PRIOR_WORST_ACCURACY
```

H7 prior mean is not included, to keep the representation compact and avoid redundant retention summaries.

## 6. Fold-local standardization

For every training fold, compute mean and population standard deviation for each base variable using training instances only.

For variable X:

```
zX = (X - mean_train(X)) / max(std_train(X), 1e-12)
```

Held-out instances use training-fold statistics.

No global discovery statistics may leak into a held-out fold.

## 7. RBS-v1 feature vector

After standardizing the six base variables, construct exactly:

```
phi =
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

```
11
```

Interpretation:

- zD*zP: parameter drift under optimizer pressure;
- zD*zR: drift conditioned on retention reserve;
- zP*zR: optimizer pressure conditioned on retention reserve;
- zG*zR: directional compatibility conditioned on retention risk;
- zM1*zM2: first/second moment coupling.

No feature term may be added, removed, or replaced after discovery.

## 8. Classifier

Use deterministic L2-regularized logistic regression.

For feature vector phi:

```
p(y=1|phi) = sigmoid(b + w^T phi)
```

Objective:

```
mean binary cross entropy
+
(lambda/2) * ||w||_2^2
```

Frozen:

```
lambda = 1.0
intercept b is not regularized
max Newton iterations = 100
convergence tolerance = 1e-10
Hessian jitter = 1e-8
```

No lambda search or model-family search is allowed.

## 9. Score threshold

The logistic probability threshold is not fixed to 0.5.

Within each training fold:

1. fit scaler;
2. fit logistic weights;
3. compute training probabilities;
4. choose a threshold maximizing balanced accuracy using the exact frozen threshold search/tie-break procedure from KCL-6.5.6.

The held-out seed is then predicted with that frozen fold model and threshold.

## 10. Discovery evaluation

Use leave-one-SEED-out cross-validation over the same 20 discovery seeds.

Each fold holds out all three boundaries from one seed.

Report:

- confusion matrix;
- balanced accuracy;
- sensitivity;
- specificity;
- accuracy.

## 11. Baselines

Two baselines are evaluated by the same LOSO-seed procedure.

### Baseline S — boundary index

```
BOUNDARY_INDEX
```

### Baseline D — scalar drift

```
H4_TASK_DRIFT_RELATIVE_L2
```

Use the exact scalar-threshold procedure from KCL-6.5.6.

RBS-v1 must outperform both.

## 12. Discovery qualification

RBS-v1 discovery-qualifies iff all are true:

```
balanced_accuracy >= 0.70
sensitivity >= 0.65
specificity >= 0.65
balanced_accuracy >= max(BA_stage, BA_H4) + 0.03
```

These thresholds are intentionally stricter than KCL-6.5.6 because RBS-v1 has greater representational capacity.

If discovery fails:

```
KCL-6.5.7 = NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED
```

No confirmatory execution is authorized.

## 13. Final discovery model artifact

If discovery qualifies, refit RBS-v1 on all 60 discovery instances.

Freeze and commit:

- base feature order;
- scaler means;
- scaler standard deviations;
- 11 logistic weights;
- intercept;
- probability threshold;
- discovery metrics;
- stage/H4 baseline rules;
- protocol SHA;
- discovery evidence SHA.

Artifact:

```
experiments/kernel_cl/results/kcl657_rule.json
```

This commit must occur before confirmatory workflow creation/execution.

## 14. Confirmatory cohort

Only after rule freeze, use the still-untouched seeds:

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

The confirmatory records must be generated with the frozen KCL-6.5.6 counterfactual protocol.

No scaler, coefficient, intercept, or threshold refit is permitted.

## 15. Confirmatory baselines

The stage-only and H4 scalar baseline rules are frozen from discovery and applied unchanged to confirmation.

## 16. Confirmatory bootstrap

Seed-cluster bootstrap:

```
20,000 resamples
RNG seed = 657657
95% percentile CI
```

Resample whole seeds with replacement, carrying all three boundary instances.

Primary CI:

```
balanced accuracy of RBS-v1
```

## 17. Confirmatory qualification

RBS-v1 is confirmed iff all are true:

```
balanced_accuracy >= 0.70
bootstrap 95% CI lower bound > 0.55
sensitivity >= 0.65
specificity >= 0.65
balanced_accuracy >= max(confirm_stage_BA, confirm_H4_BA) + 0.03
```

If all pass:

```
KCL-6.5.7 = PASS
RELATIONAL_BOUNDARY_STATE_QUALIFIED
```

If discovery qualified but confirmation fails:

```
KCL-6.5.7 = NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_GENERALIZED
```

## 18. Representation ablations

Ablations are descriptive only and cannot select the model.

Using the same discovery LOSO procedure, report:

### A-DP

```
[zD, zP, zD*zP]
```

### A-DR

```
[zD, zR, zD*zR]
```

### A-MOMENT

```
[zM1, zM2, zM1*zM2]
```

### A-NO-RETENTION

RBS-v1 with:

```
zR,
zD*zR,
zP*zR,
zG*zR
```

removed.

Ablations do not alter qualification or feature selection.

## 19. Representation-value criterion

As a descriptive secondary analysis, RBS-v1 should preferably exceed:

```
max(all ablation balanced accuracies)
```

This is not a hard PASS gate because interactions may be redundant.

## 20. Integrity

Discovery integrity requires:

- canonical KCL-6.5.6 evidence status NEGATIVE;
- exactly 60 discovery records;
- no confirmatory seed appears in discovery records;
- all required features finite;
- target labels unchanged;
- held-out seed never contributes to scaler/weights/threshold.

Confirmatory integrity additionally requires:

- rule SHA fixed before confirm run;
- no refit on confirmation;
- KCL-6.5.6 counterfactual integrity PASS for all fresh boundaries.

Any integrity failure:

```
KCL-6.5.7 = REVISE
RELATIONAL_BOUNDARY_STATE_INVALID
```

## 21. Architectural implication

PASS would support adding a:

```
Boundary State Encoder
```

whose output is a predictive health representation consumed by a later adaptive boundary controller.

NEGATIVE means the current relational variables are still insufficient; controller implementation remains unjustified.

KCL-6.5.7 does not choose A/B/C online.

## 22. No tuning rule

After freeze do not change:

- six base variables;
- eleven RBS-v1 terms;
- logistic lambda;
- solver settings;
- threshold fitting;
- discovery/confirm cohorts;
- LOSO split;
- qualification gates;
- bootstrap settings;
- target definition.

No new interaction or model family may be introduced after discovery.

## 23. Scope exclusions

KCL-6.5.7 does not:

- implement adaptive control;
- train a neural boundary encoder;
- tune replay;
- modify memory E;
- use future-task probes as inputs;
- open KCL-7;
- open reasoning.

## 24. Required artifacts

```
docs/research/kernel-continual-learning/kcl657-protocol.md
experiments/kernel_cl/kcl657_relational_boundary_state.py
tests/test_kernel_cl_kcl657.py
.github/workflows/kernel-cl-kcl657-discovery.yml
experiments/kernel_cl/results/kcl657_discovery.json
experiments/kernel_cl/results/kcl657_rule.json   # only if discovery qualifies
.github/workflows/kernel-cl-kcl657-confirm.yml   # only after rule freeze
experiments/kernel_cl/results/kcl657_confirm.json # only if confirm authorized
docs/research/kernel-continual-learning/kcl657-paper.md
```

## 25. Closure

### Discovery-negative path

- protocol freeze;
- implementation/tests;
- one official discovery analysis;
- evidence preserved;
- no confirm workflow;
- paper + append-only Lineage.

### Confirmatory path

- protocol freeze;
- discovery qualifies;
- rule artifact committed/frozen;
- confirm workflow created only after rule commit;
- one official confirmatory run on untouched seeds;
- evidence preserved;
- paper + append-only Lineage.
