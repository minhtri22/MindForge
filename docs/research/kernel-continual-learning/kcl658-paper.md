# KCL-6.5.8 — Localized Relational Boundary-State Attribution

## Abstract

KCL-6.5.7 showed that a global multivariate representation of task-relative drift, AdamW moment geometry, and retention state did not predict `SAFE_RESET_OPPORTUNITY` better than the strongest scalar drift signal. KCL-6.5.8 tests a more localized structural hypothesis:

> safe boundary intervention is encoded not by global summaries but by where recent parameter drift, optimizer pressure, and retained-knowledge sensitivity co-localize across parameter groups.

The frozen LRBS-v1 representation partitions the model into four parameter groups:

- shared token/output state;
- position state;
- transformer block;
- final norm.

At each boundary, it computes group-wise shares of:

- parameter drift;
- bias-corrected Adam pressure;
- retention-loss gradient attribution;

plus overlap, mismatch, group-identity triple-attribution, and retention-weighted directional compatibility.

Discovery reconstructs the same 60 boundaries used by KCL-6.5.6. All 60 counterfactual labels/outcomes reproduce canonically and both frozen baselines reproduce exactly, establishing that the localized attribution machinery does not perturb the scientific substrate.

Despite this, LRBS-v1 performs substantially worse than the scalar H4 drift baseline.

```
LRBS-v1 balanced accuracy = 0.33697
sensitivity               = 0.46341
specificity               = 0.21053
accuracy                  = 0.38333
```

Frozen baselines:

```
stage-only BA = 0.60270
H4 drift BA   = 0.65533
```

All pre-registered ablations also remain below H4.

Therefore:

```
KCL-6.5.8 = NEGATIVE
LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED
```

No rule artifact is frozen and the untouched confirmatory cohort is not executed.

The result falsifies this exact co-localization hypothesis: parameter-group overlap between drift, global Adam pressure, and retention-gradient attribution is not sufficient to identify safe reset opportunity on this substrate.

## 1. Upstream chain

KCL-6.5.6:

```
NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

showed that no single scalar health signal qualified. The strongest candidate, task-relative drift, reached:

```
BA   = 0.65533
sens = 0.73171
spec = 0.57895
```

KCL-6.5.7 then tested a global multivariate RBS-v1 and closed:

```
NEGATIVE
RELATIONAL_BOUNDARY_STATE_NOT_DISCOVERY_QUALIFIED
```

with:

```
BA = 0.44865
```

KCL-6.5.8 therefore moves from global summary interactions to structured parameter-group attribution.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl658-protocol.md`

Protocol commit:

`afa2aa87510dc87c5fc781e705ba4077f35c20f8`

Protocol SHA-256:

`94adbc88b46cedf9d08629aa8c070b1205bc4c46dc2b00f27f0b671764e4cf8c`

Canonical scientific source:

`f5e9ae60e4cd9fdab02309e41b58b6463907888d`

No scientific feature, target, model family, threshold rule, discovery gate, or confirmatory seed was changed after canonical discovery began.

## 3. Pre-science QA history

Several auto-triggered workflow runs failed before scientific execution because focused reproduction tests were deliberately strict.

These were implementation/QA runs, not scientific looks.

### Run 35409806577

Focused tests failed. Scientific discovery step was skipped.

### Run 35409971713

QA diagnostic run; non-canonical.

### Run 35409983109

QA diagnostic run; non-canonical.

### Run 35410107951

H4 reproduction-order QA attempt; non-canonical.

### Run 35410280277

Focused tests failed because individual H4 floating values were required to match within `1e-9`, even though all A/B/C outcome deltas were exactly zero and labels matched.

The frozen protocol requires:

- A/B/C outcomes/labels to reproduce canonically;
- H4 to reproduce at the frozen LOSO baseline-metric level.

The final QA fix separated those two gates without changing any scientific hypothesis, feature, target, or threshold.

Canonical discovery then ran once at source commit `f5e9ae60...`.

## 4. Parameter groups

Exactly the KCL-6.5.3 grouping is reused:

```
G_TOKEN_SHARED
G_POSITION
G_TRANSFORMER
G_FINAL_NORM
```

All named model parameters are covered exactly once.

## 5. Localized state

At each boundary after task Ti:

### Drift share

For group g:

```
D_g = ||theta_post,g - theta_pre,g||_2
d_g = D_g / sum_h D_h
```

### Optimizer-pressure share

Using bias-corrected AdamW state:

```
m_hat = exp_avg / (1-beta1^step)
v_hat = exp_avg_sq / (1-beta2^step)

pressure = m_hat / (sqrt(v_hat)+eps)
```

For group g:

```
P_g = ||pressure_g||_2
p_g = P_g / sum_h P_h
```

### Retention attribution

On all already-observed tasks:

```
L_ret = mean CE(model(T1..Ti))
```

Then:

```
K_g = ||grad_g L_ret||_2
k_g = K_g / sum_h K_h
```

The gradient is cleared before any counterfactual next-task training.

## 6. LRBS-v1 features

The frozen 13-dimensional representation contains:

### Distribution overlaps

```
F1 = sum d_g p_g
F2 = sum d_g k_g
F3 = sum p_g k_g
F4 = sum d_g p_g k_g
```

### Distribution mismatch

```
F5 = TV(d,p)
F6 = TV(d,k)
F7 = TV(p,k)
```

### Retention reserve

```
F8 = 1 - worst prior-task accuracy
```

### Group-identity triple overlap

```
F9  = TOKEN       d*p*k
F10 = POSITION    d*p*k
F11 = TRANSFORMER d*p*k
F12 = FINAL_NORM  d*p*k
```

### Directional compatibility

```
F13 = sum_g k_g * cos(drift_g, -pressure_g)
```

No post-outcome feature was added.

## 7. Canonical reconstruction integrity

The discovery harness reconstructs all 60 KCL-6.5.6 boundary instances.

Required:

- identical SAFE_RESET_OPPORTUNITY label;
- identical A/B/C next-task AUC;
- identical A/B/C final next-task accuracy;
- identical A/B/C prior retention;
- exact replay/counterfactual integrity;
- gradients cleared after retention attribution.

Observed:

```
60 / 60 canonical boundaries reproduced
```

Both frozen baseline metrics also reproduce exactly.

Therefore LRBS-v1 is evaluated on the same scientific target as KCL-6.5.6.

## 8. Baseline reproduction

### Boundary-index baseline

```
accuracy          = 0.65000
balanced accuracy = 0.60270
sensitivity       = 0.73171
specificity       = 0.47368
```

### H4 task-relative drift

```
accuracy          = 0.68333
balanced accuracy = 0.65533
sensitivity       = 0.73171
specificity       = 0.57895
```

These match canonical KCL-6.5.6 discovery values.

## 9. LRBS-v1 result

Confusion matrix:

```
TP = 19
TN = 4
FP = 15
FN = 22
```

Metrics:

```
accuracy          = 0.38333
balanced accuracy = 0.33697
sensitivity       = 0.46341
specificity       = 0.21053
```

Frozen discovery gates:

```
BA   >= 0.70
sens >= 0.65
spec >= 0.65
BA   >= best baseline + 0.03
```

Best baseline:

```
0.65533
```

Required LRBS-v1 BA:

```
>= 0.68533
```

Observed:

```
0.33697
```

LRBS-v1 therefore fails decisively.

## 10. Frozen ablations

Ablations are descriptive only.

### A-OVERLAP

```
F1,F2,F3,F4
BA = 0.34082
```

### A-MISMATCH

```
F5,F6,F7,F8
BA = 0.33890
```

### A-IDENTITY

```
F9,F10,F11,F12
BA = 0.43389
```

This is the strongest ablation, but still far below H4.

### A-NO-DIRECTION

```
F1..F12
BA = 0.36329
```

No ablation approaches the scalar drift baseline.

## 11. Scientific interpretation

The result falsifies the specific hypothesis:

> safe reset opportunity is determined by coarse parameter-group co-localization of task drift, Adam pressure, and retention-gradient sensitivity.

The failure is stronger than KCL-6.5.7 because even after introducing localization and a direct gradient-based retention attribution, generalization becomes worse rather than better.

This suggests the missing variable is not simply:

```
which broad layer/group is moving
×
where Adam pressure is large
×
where retention loss is sensitive
```

## 12. What this does not prove

KCL-6.5.8 does not prove that local structure is irrelevant.

It does not test:

- neuron/head/channel-level attribution;
- low-rank parameter subspaces;
- Fisher/Hessian curvature;
- replay-gradient versus current-gradient conflict;
- task-specific protected subspaces;
- nonlinear learned representations;
- temporal trajectories inside a task rather than endpoint snapshots.

It only rejects the frozen four-group LRBS-v1 formulation.

## 13. Stronger emerging clue

Across KCL-6.5.6–6.5.8, the simple H4 task-relative drift scalar remains the strongest discovered predictor:

```
H4 BA = 0.65533
```

Adding:

- global optimizer geometry;
- global retention summary;
- pairwise global interactions;
- four-group moment localization;
- four-group retention-gradient attribution;

has not improved out-of-seed performance.

This indicates that the extra state variables, as currently summarized, primarily add variance/noise rather than the missing causal information.

## 14. Architectural consequence

An adaptive Task-Boundary Controller is still not justified.

Neither of these are supported:

```
single scalar threshold controller
```

nor:

```
small global/localized logistic Boundary State Encoder
```

The next research step should therefore not keep increasing feature count around the same binary target.

A more defensible move is to decompose the **target regimes themselves**.

`SAFE_RESET_OPPORTUNITY` currently merges distinct causal situations:

- B reset-all may be safe;
- C reset-moments may be safe;
- both may be safe;
- A may already be sufficient;
- a carry failure may be reparable or unreparable;
- plasticity gain may exist without retention safety.

These regimes may not share one health representation.

## 15. Recommended next hypothesis

Before another predictive model, decompose the boundary outcome space into causally distinct classes.

A candidate next milestone is:

```
KCL-6.5.9 — Boundary Regime Decomposition
```

Questions:

1. Are B-safe and C-safe opportunities statistically/mechanistically separable?
2. Are carry-all catastrophic failures a distinct regime from mild AUC improvements?
3. Does H4 drift predict one regime well but fail when regimes are pooled?
4. Can each regime be assigned a simpler mechanism-specific signal?
5. Only after separate hypotheses qualify should policy selection be A/B tested.

This follows the user's governance rule: uncertain architectural hypotheses should be proved separately before combining them.

## 16. Confirmatory phase

Discovery failed.

Therefore:

```
kcl658_rule.json          = NOT CREATED
kcl658-confirm.yml        = NOT CREATED
confirmatory seeds        = UNTOUCHED
```

The untouched seeds remain:

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

## 17. Integrity

All canonical scientific integrity gates pass:

- 60/60 boundaries reproduced;
- stage baseline reproduced;
- H4 baseline reproduced;
- parameter groups cover model;
- gradient attribution cleared before training;
- whole-seed LOSO;
- fold-local scaler, weights, threshold;
- future task excluded from features;
- confirmatory seeds absent;
- KCL-7 not started.

## 18. Verdict

```
KCL-6.5.8 = NEGATIVE
LOCALIZED_RELATIONAL_STATE_NOT_DISCOVERY_QUALIFIED
```

This is a valid negative scientific result.

## 19. Provenance

Protocol:

`afa2aa87510dc87c5fc781e705ba4077f35c20f8`

Initial implementation:

`58168de3be4d9788316eef9a0f0438e29b704f82`

Initial tests:

`edd53b946bee60f4412d4bce72a60626dc1db1e8`

Initial workflow:

`63ef1aea9761305ced9285aa45b248badd25f090`

Pre-science QA/diagnostic commits:

```
698ea817525d5477fa297d17652ca1c3d5eefc74
0b295b0757bd6d2f83c1b4ed363a3b20d4bc904d
1ed930015c64f772200cbd139e0b825e042d1a23
e3e24091efda2dda4d07819d489febb6d1eeba1b
```

Canonical scientific source:

`f5e9ae60e4cd9fdab02309e41b58b6463907888d`

Official scientific workflow:

`35412021383`

Focused tests:

`20 passed (10 KCL-6.5.8 + 10 KCL-6.5.7)`

Artifact:

`10574064516`

Artifact ZIP SHA-256:

`7e90caedb232987b46e8f283eded5c88410c6b57d49e1002a40f345f56b30b3f`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl658_discovery.json`

## 20. Next scientific requirement

Do not tune LRBS-v1 and do not add more localized features to the same pooled target.

The next scientifically justified step is to test whether `SAFE_RESET_OPPORTUNITY` is itself masking multiple causal regimes.

If opened, KCL-6.5.9 should pre-register separate regime hypotheses before any new classifier is trained.
