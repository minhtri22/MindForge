# MindForge Kernel Continual Learning — KCL-6.5.8 Localized Relational Boundary-State Attribution Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.8 DISCOVERY OR CONFIRMATORY EXECUTION**

## 1. Trigger

KCL-6.5.7 closed:

```
NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED
```

Its global RBS-v1 representation combined:

```
task-relative drift
× optimizer moment geometry
× retention risk
```

but achieved only:

```
balanced accuracy = 0.44865
```

versus the strongest scalar H4 drift baseline:

```
0.65533
```

Therefore KCL-6.5.8 tests a narrower structural hypothesis:

> the missing boundary-health information is not in global summaries, but in **where** recent parameter drift, optimizer pressure, and retained-knowledge sensitivity co-localize across parameter groups.

## 2. Hypothesis

### H-LRBS

A localized relational boundary-state representation can predict `SAFE_RESET_OPPORTUNITY` better than global drift alone when it encodes the overlap between:

```
task-relative drift
× optimizer moment geometry
× retention attribution
```

across fixed parameter groups.

Representation name:

```
LRBS-v1
Localized Relational Boundary State v1
```

## 3. Parameter groups

Reuse exactly the frozen KCL-6.5.3 grouping:

### G_TOKEN_SHARED

```
token_embedding.weight
```

The tied LM head is the same tensor.

### G_POSITION

```
position_embedding.weight
```

### G_TRANSFORMER

All parameters whose names begin:

```
layers.
```

### G_FINAL_NORM

All parameters whose names begin:

```
norm.
```

Coverage must include every named parameter exactly once.

## 4. Discovery and target

Discovery uses the same 20 discovery seeds as KCL-6.5.6 / KCL-6.5.7:

```
9595
9797
9999
10201
10403
10605
10807
11009
11211
11413
11615
11817
12019
12221
12423
12625
12827
13029
13231
13433
```

Each seed contributes boundaries after T1, T2 and T3:

```
N = 20 × 3 = 60
```

Primary target remains exactly:

```
SAFE_RESET_OPPORTUNITY
```

with the KCL-6.5.6 definition unchanged.

## 5. Discovery counterfactual reproduction

Because KCL-6.5.8 needs new localized features not stored in KCL-6.5.6 evidence, discovery boundaries are reconstructed using the frozen KCL-6.5.6 counterfactual harness.

For every `(seed,boundary)`, KCL-6.5.8 must reproduce the canonical KCL-6.5.6 discovery target label exactly.

Required:

```
60 / 60 SAFE_RESET_OPPORTUNITY labels identical
```

Also require exact matching of:

- A/B/C next-task final accuracy;
- A/B/C next-task AUC;
- A/B/C prior retention;

within tolerance:

```
1e-9
```

Any mismatch:

```
KCL-6.5.8 = REVISE
LOCALIZED_BOUNDARY_RECONSTRUCTION_INVALID
```

## 6. Anti-leakage

All LRBS features are extracted immediately after task Ti and before Ti+1 is bound or sampled.

Allowed information:

- current model state;
- model snapshot from before Ti;
- current AdamW state;
- full datasets of tasks T1..Ti already observed;
- current accuracies/losses on T1..Ti.

Forbidden:

- Ti+1 tensors;
- Ti+1 task name/family;
- Ti+1 gradient/loss;
- future A/B/C outcomes;
- `SAFE_RESET_OPPORTUNITY` itself.

## 7. Local drift state

For each parameter group g:

```
D_g = ||theta_post,g - theta_pre,g||_2
```

Convert to a nonnegative share:

```
d_g = D_g / sum_h D_h
```

Required:

```
sum_g d_g = 1
```

within `1e-9`.

## 8. Local optimizer moment geometry

For each parameter tensor at the boundary:

```
m_hat = exp_avg / (1 - beta1^step)
v_hat = exp_avg_sq / (1 - beta2^step)

pressure = m_hat / (sqrt(v_hat) + eps)
```

For each group g:

```
P_g = ||pressure_g||_2
```

Pressure share:

```
p_g = P_g / sum_h P_h
```

Required:

```
sum_g p_g = 1
```

within `1e-9`.

## 9. Protected-retention attribution

Define the already-observed retention objective at boundary i:

```
L_ret =
mean over tasks T1..Ti
  CE(model(task_inputs), task_targets)
```

Each task contributes its full canonical dataset once.

Compute:

```
grad_ret = gradient_theta L_ret
```

No optimizer step is performed.

For each group g:

```
K_g = ||grad_ret,g||_2
```

Retention-attribution share:

```
k_g = K_g / sum_h K_h
```

Required:

```
sum_g k_g = 1
```

within `1e-9`.

After extraction all parameter gradients must be cleared before any counterfactual training.

## 10. Directional compatibility

For every group with nonzero norms define:

### Drift–pressure compatibility

```
C_DP,g =
cos(
  theta_post,g - theta_pre,g,
  -pressure_g
)
```

### Pressure–retention compatibility

The retention-preserving local descent direction is:

```
-grad_ret,g
```

Define:

```
C_PK,g =
cos(
  -pressure_g,
  -grad_ret,g
)
```

For zero-norm cases, cosine is frozen to `0`.

## 11. LRBS-v1 feature vector

Use exactly the following 13 features.

### Cross-group distribution overlaps

```
F1  = sum_g d_g * p_g
F2  = sum_g d_g * k_g
F3  = sum_g p_g * k_g
F4  = sum_g d_g * p_g * k_g
```

### Distribution mismatch

Use total-variation distance:

```
TV(a,b) = 0.5 * sum_g |a_g-b_g|
```

```
F5 = TV(d,p)
F6 = TV(d,k)
F7 = TV(p,k)
```

### Global retention reserve

```
F8 = 1 - worst_accuracy(T1..Ti)
```

### Group-identity triple attribution

In frozen group order:

```
F9  = d_TOKEN * p_TOKEN * k_TOKEN
F10 = d_POSITION * p_POSITION * k_POSITION
F11 = d_TRANSFORMER * p_TRANSFORMER * k_TRANSFORMER
F12 = d_FINAL_NORM * p_FINAL_NORM * k_FINAL_NORM
```

### Retention-weighted directional compatibility

```
F13 = sum_g k_g * C_DP,g
```

No feature may be added, removed, or transformed after discovery.

## 12. Descriptive directional diagnostic

Report but do not include in the primary model:

```
sum_g k_g * C_PK,g
```

This tests whether optimizer pressure aligns with the local direction that would reduce already-observed retention loss.

It cannot alter qualification.

## 13. Classifier

Use the same deterministic L2 logistic framework as KCL-6.5.7:

```
p(y=1|x) = sigmoid(b + w^T z(x))
```

where all 13 LRBS features are standardized fold-locally.

Frozen:

```
lambda = 1.0
max Newton iterations = 100
convergence tolerance = 1e-10
Hessian jitter = 1e-8
```

No regularization or classifier search.

## 14. Fold-local fitting

Discovery uses leave-one-SEED-out CV.

For each held seed:

1. fit LRBS feature means/stds on other 19 seeds;
2. fit logistic weights on other 19 seeds;
3. fit score threshold on training scores only;
4. predict all three boundaries from the held seed.

No held-seed contribution to scaler, model or threshold.

## 15. Baselines

Evaluate under the exact same LOSO seed split:

### Baseline S

```
BOUNDARY_INDEX
```

### Baseline H4

```
TASK_DRIFT_RELATIVE_L2
```

Canonical KCL-6.5.6 expected values:

```
stage BA = 0.60270
H4 BA    = 0.65533
```

The reconstructed dataset must reproduce these baseline metrics exactly within `1e-9`.

## 16. Discovery qualification

LRBS-v1 discovery-qualifies iff all are true:

```
balanced_accuracy >= 0.70
sensitivity >= 0.65
specificity >= 0.65
balanced_accuracy >= max(BA_stage, BA_H4) + 0.03
```

If not:

```
KCL-6.5.8 = NEGATIVE
LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED
```

No confirmatory run is authorized.

## 17. Frozen ablations

Ablations are descriptive only.

### A-OVERLAP

```
F1,F2,F3,F4
```

### A-MISMATCH

```
F5,F6,F7,F8
```

### A-IDENTITY

```
F9,F10,F11,F12
```

### A-NO-DIRECTION

```
F1..F12
```

Ablations cannot replace LRBS-v1 after outcome inspection.

## 18. Final discovery rule

If LRBS-v1 qualifies, refit on all 60 discovery instances and freeze:

- LRBS feature order;
- scaler means/stds;
- logistic weights/intercept;
- score threshold;
- discovery metrics;
- H4 and stage baseline rules;
- protocol SHA;
- canonical discovery-evidence SHA.

Artifact:

```
experiments/kernel_cl/results/kcl658_rule.json
```

The rule commit must precede confirm workflow creation.

## 19. Confirmatory cohort

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

No scaler, coefficient or threshold refit.

## 20. Confirmatory bootstrap

Seed-cluster bootstrap:

```
20,000 resamples
RNG seed = 658658
95% percentile CI
```

Primary CI is LRBS-v1 balanced accuracy.

## 21. Confirmatory qualification

PASS iff all are true:

```
balanced_accuracy >= 0.70
bootstrap CI lower bound > 0.55
sensitivity >= 0.65
specificity >= 0.65
balanced_accuracy >= max(confirm_stage_BA, confirm_H4_BA) + 0.03
```

Then:

```
KCL-6.5.8 = PASS
LOCALIZED_RELATIONAL_BOUNDARY_STATE_QUALIFIED
```

Discovery PASS + confirmation fail:

```
KCL-6.5.8 = NEGATIVE
LOCALIZED_RELATIONAL_STATE_NOT_GENERALIZED
```

## 22. Interpretation guardrails

PASS supports a localized:

```
Boundary State Encoder
```

but does not authorize online A/B/C action selection by itself.

NEGATIVE does not falsify all structured state representations. It falsifies this exact parameter-group co-localization hypothesis.

No post-outcome merging with KCL-6.5.7 features is permitted.

## 23. Scope exclusions

KCL-6.5.8 does not:

- implement adaptive policy control;
- modify memory E;
- tune replay;
- add neural encoders;
- use next-task probes as inputs;
- open KCL-7;
- open reasoning.

## 24. Required artifacts

```
docs/research/kernel-continual-learning/kcl658-protocol.md
experiments/kernel_cl/kcl658_localized_boundary_state.py
tests/test_kernel_cl_kcl658.py
.github/workflows/kernel-cl-kcl658-discovery.yml
experiments/kernel_cl/results/kcl658_discovery.json
experiments/kernel_cl/results/kcl658_rule.json       # only if discovery qualifies
.github/workflows/kernel-cl-kcl658-confirm.yml       # only after rule freeze
experiments/kernel_cl/results/kcl658_confirm.json    # only if confirmation authorized
docs/research/kernel-continual-learning/kcl658-paper.md
```

## 25. Closure

Discovery-negative path:

- protocol freeze;
- implementation + tests;
- one official discovery run;
- evidence preserved;
- no rule / no confirm workflow;
- paper + append-only Lineage.

Confirmatory path:

- protocol freeze;
- discovery qualify;
- rule artifact committed/frozen;
- confirm workflow created only after rule commit;
- one official untouched-seed confirm run;
- evidence preserved;
- paper + append-only Lineage.
