# MindForge Kernel Continual Learning — KCL-6.5.6 Boundary Plasticity Health Signal Qualification Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.6 DISCOVERY OR CONFIRMATORY EXECUTION**

## 1. Trigger

KCL-6.5.5 closed by frozen-protocol adjudication:

```
FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

Key evidence:

- fixed carry-all A contains severe long-horizon acquisition failures;
- reset-all B can repair some failures but worsens acquisition AUC on average;
- carry-step/reset-moments C improves acquisition AUC but loses retention;
- no fixed global boundary action satisfies the joint plasticity/stability contract.

Therefore a boundary policy must become state-dependent.

KCL-6.5.6 does **not** implement an adaptive controller. It asks whether a non-oracular signal available at the boundary can predict when a reset-style intervention is safe and useful.

## 2. Scientific question

Given only information available immediately after completing task Ti and **before observing any data or outcome from task Ti+1**, can a frozen scalar boundary signal predict:

> whether at least one reset-style action (B or C) will safely improve next-task plasticity relative to carry-all A?

The signal may use:

- current model parameters;
- AdamW state;
- the model snapshot from the start of the just-completed task;
- performance on tasks already observed;
- current-task loss/accuracy.

The signal may **not** use:

- any Ti+1 examples;
- Ti+1 loss/gradient;
- Ti+1 identity/family metadata;
- Ti+1 outcome under A/B/C;
- future task order beyond the fact that a next task exists.

## 3. Matched one-boundary counterfactual dataset

For each seed, build a single reference trajectory using:

```
A = CARRY_ALL
```

with the frozen targeted-clarification reconstructive memory mechanism.

At each boundary after T1, T2 and T3:

1. snapshot the exact reference model, AdamW state and memories;
2. extract candidate signals from this boundary state;
3. fork the same boundary snapshot into A/B/C;
4. apply exactly one boundary action;
5. train only the immediately following task with lockstep identical data/replay;
6. measure next-task plasticity and prior-task retention;
7. continue the reference trajectory using the A fork only.

This creates three matched boundary instances per seed without recursively contaminating later boundary labels with B/C history.

## 4. Boundary actions

Exactly KCL-6.5.5:

### A — CARRY_ALL

Carry full AdamW state.

### B — RESET_ALL

Fresh AdamW state.

### C — CARRY_STEP_RESET_MOMENTS

Preserve step; zero `exp_avg` and `exp_avg_sq`.

No model parameter changes are allowed at the boundary.

## 5. Frozen memory/replay mechanism

Exactly KCL-6.5.5 E policy:

- exact → fuzzy decay;
- targeted clarification on replay selection;
- exact schema reactivation;
- 15 current + 1 replay;
- replay = 6.25%;
- no cue gradient;
- no raw cue storage.

Within each boundary counterfactual A/B/C receive exactly the same current examples and replay observations.

## 6. Primary target: SAFE_RESET_OPPORTUNITY

For a boundary and intervention P in {B,C}, relative to A define:

```
DeltaAUC_P = next_task_AUC(P) - next_task_AUC(A)
DeltaR_P   = prior_retention(P) - prior_retention(A)
```

P is a **SAFE_BENEFICIAL_RESET** iff all are true:

1. plasticity benefit:
   ```
   DeltaAUC_P >= 0.01
   ```
   OR:
   ```
   A final next-task accuracy < 0.95
   and
   P final next-task accuracy >= 0.95
   ```
2. retention:
   ```
   DeltaR_P >= -1/24
   ```
3. absolute acquisition:
   ```
   P final next-task accuracy >= 0.95
   ```

Primary binary label:

```
SAFE_RESET_OPPORTUNITY = 1
```

iff B or C is a SAFE_BENEFICIAL_RESET.

Otherwise:

```
SAFE_RESET_OPPORTUNITY = 0
```

This label is used only as supervised outcome for signal qualification. It is never an input feature.

## 7. Secondary labels

Report but do not use for signal selection:

### CARRY_PLASTICITY_FAILURE

```
A final next-task accuracy < 0.95
```

### BEST_SAFE_ACTION

Among safe beneficial B/C actions choose the one with larger next-task AUC; ties prefer B by frozen order.

If neither is safe beneficial:

```
BEST_SAFE_ACTION = A
```

These labels are diagnostic only.

## 8. Candidate boundary signals

All candidates are scalar and computed before Ti+1.

Frozen eligible candidate order:

### H1 — M1_RMS

Global RMS of POST-boundary AdamW `exp_avg`.

### H2 — SQRT_M2_RMS

Global RMS of `sqrt(exp_avg_sq)`.

### H3 — BIAS_CORRECTED_ADAM_PRESSURE_RMS

For each parameter element:

```
m_hat = exp_avg / (1 - beta1^step)
v_hat = exp_avg_sq / (1 - beta2^step)

pressure = m_hat / (sqrt(v_hat) + eps)
```

Signal = global RMS of pressure.

### H4 — TASK_DRIFT_RELATIVE_L2

For just-completed task Ti:

```
||theta_post - theta_pre||_2
/
max(||theta_pre||_2, 1e-12)
```

### H5 — PRESSURE_TO_DRIFT_RATIO

```
||pressure||_2
/
max(||theta_post-theta_pre||_2, 1e-12)
```

### H6 — DRIFT_PRESSURE_COSINE

Cosine between:

```
theta_post - theta_pre
```

and the negative bias-corrected Adam pressure vector.

### H7 — PRIOR_MEAN_ACCURACY

Mean accuracy over all already observed tasks at the boundary.

### H8 — PRIOR_WORST_ACCURACY

Worst accuracy over all already observed tasks at the boundary.

### H9 — CURRENT_TASK_LOSS

Loss on the just-completed task at the boundary.

No candidate may be added after discovery outcomes are observed.

## 9. Stage-only baseline

A non-eligible baseline is also evaluated:

```
BOUNDARY_INDEX = 1,2,3
```

corresponding to after T1/T2/T3.

A signal cannot qualify merely by encoding task age.

Discovery selected signal must exceed the stage-only leave-one-seed-out balanced accuracy by at least:

```
0.05
```

The same superiority margin is required on confirmation.

## 10. Discovery cohort

Discovery uses the already-observed KCL-6.5.5 fresh seeds:

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

N = 20 seeds × 3 boundaries = 60 boundary instances.

Because KCL-6.5.5 outcomes are already known, this cohort is discovery/training only and cannot provide confirmatory evidence.

## 11. Frozen threshold fitting

Each scalar signal is converted to a binary rule:

```
signal >= threshold
```

or:

```
signal <= threshold
```

Threshold candidates on a training set are:

- midpoint between every pair of consecutive unique observed values;
- one value below the minimum;
- one value above the maximum.

For each candidate threshold and both directions compute balanced accuracy.

Tie-break order:

1. highest balanced accuracy;
2. highest min(sensitivity, specificity);
3. direction `>=` before `<=`;
4. lower numeric threshold.

No logistic regression, tree fitting, or learned multivariate combination is allowed in KCL-6.5.6.

## 12. Discovery model selection

For each signal H1–H9:

- perform leave-one-SEED-out cross-validation;
- for each held-out seed, fit threshold/direction using the other 19 seeds;
- predict all 3 held-out boundaries;
- aggregate all 60 out-of-seed predictions.

Compute:

- balanced accuracy;
- sensitivity;
- specificity.

Also evaluate BOUNDARY_INDEX using the same procedure.

A candidate is discovery-qualified iff:

```
balanced_accuracy >= 0.65
sensitivity >= 0.60
specificity >= 0.60
balanced_accuracy >= stage_baseline + 0.05
```

Select among qualified candidates by:

1. highest LO-seed balanced accuracy;
2. highest min(sensitivity,specificity);
3. frozen candidate order H1→H9.

Then refit threshold/direction for the selected signal on all 60 discovery instances.

The resulting:

```
signal name
direction
threshold
```

is frozen in a separate rule artifact/commit before confirmatory execution.

If no signal discovery-qualifies:

```
KCL-6.5.6 = NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

and no confirmatory run is authorized.

## 13. Confirmatory cohort

Only after the rule is frozen, run 20 new seeds:

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

N = 20 × 3 = 60 fresh boundary instances.

No threshold refitting is permitted.

## 14. Confirmatory metrics

Apply the frozen rule directly.

Report:

- confusion matrix;
- balanced accuracy;
- sensitivity;
- specificity;
- accuracy;
- positive prevalence.

Use seed-cluster bootstrap:

```
20,000 resamples
RNG seed = 656656
95% percentile CI
```

Each bootstrap draw resamples whole seeds with replacement and includes all three boundaries for each sampled seed.

Primary CI is for balanced accuracy.

## 15. Confirmation gate

The boundary health signal is confirmed iff all are true:

```
balanced_accuracy >= 0.65
bootstrap 95% CI lower bound > 0.50
sensitivity >= 0.60
specificity >= 0.60
balanced_accuracy >= confirmatory stage-only baseline + 0.05
```

The stage-only baseline is fit on discovery only and frozen exactly like any other threshold rule, then evaluated on confirmation without refitting.

## 16. Anti-leakage integrity

For every boundary feature record:

- signal extraction occurs before next-task samples are drawn;
- feature function receives no Ti+1 tensors;
- feature function receives no A/B/C next-stage outcomes;
- task name/family for Ti+1 is not passed;
- only already-observed task evaluations are permitted.

Implementation must structurally separate:

```
extract_boundary_features(...)
```

from:

```
run_next_task_counterfactual(...)
```

Any leakage => REVISE.

## 17. Counterfactual integrity

At every boundary:

- A/B/C fork from identical model state;
- A/B/C see matched current minibatches;
- A/B/C see matched replay source/rank/observation;
- query events are identical;
- boundary actions do not alter model parameters;
- exact replay match rate = 1.0.

Any failure => REVISE.

## 18. Interpretation

### PASS

```
KCL-6.5.6 = PASS
BOUNDARY_HEALTH_SIGNAL_QUALIFIED
```

The selected signal is a validated non-oracular predictor of safe reset opportunity on this synthetic CL substrate.

This authorizes, but does not itself implement, a next adaptive-policy experiment.

### Confirmatory failure

```
KCL-6.5.6 = NEGATIVE
BOUNDARY_HEALTH_SIGNAL_NOT_GENERALIZED
```

No adaptive controller may be justified from these candidate signals.

### Integrity failure

```
KCL-6.5.6 = REVISE
BOUNDARY_SIGNAL_QUALIFICATION_INVALID
```

## 19. Architecture implication

PASS supports introducing a **Boundary Health Sensor** as an explicit input to a later Task-Boundary Plasticity/Retention Controller.

NEGATIVE means the current state variables are insufficient; additional measurable state must be identified before adaptive control.

KCL-6.5.6 does not select A/B/C actions online.

## 20. No tuning rule

After protocol freeze do not change:

- candidates H1–H9;
- target definition;
- discovery cohort;
- confirmatory cohort;
- threshold fitting algorithm;
- CV split;
- candidate selection rule;
- stage baseline;
- qualification thresholds;
- bootstrap seed/resamples.

No new signal or composite may be added after discovery.

## 21. Scope exclusions

KCL-6.5.6 does not:

- implement adaptive optimizer policy;
- tune replay;
- modify memory E;
- use future-task probes as signal;
- open KCL-7;
- open reasoning.

## 22. Required artifacts

```
docs/research/kernel-continual-learning/kcl656-protocol.md
experiments/kernel_cl/kcl656_boundary_health_signal.py
tests/test_kernel_cl_kcl656.py
.github/workflows/kernel-cl-kcl656-discovery.yml
experiments/kernel_cl/results/kcl656_discovery.json
experiments/kernel_cl/results/kcl656_rule.json
.github/workflows/kernel-cl-kcl656-confirm.yml
experiments/kernel_cl/results/kcl656_confirm.json
docs/research/kernel-continual-learning/kcl656-paper.md
```

## 23. Closure

KCL-6.5.6 closes only after either:

### Discovery-negative path

- protocol frozen;
- discovery workflow complete;
- no candidate qualifies;
- evidence preserved;
- paper + Lineage closure.

### Confirmatory path

- protocol frozen;
- discovery workflow complete;
- rule artifact committed/frozen;
- confirmatory workflow created only after rule freeze;
- one official fresh confirmatory run;
- evidence preserved;
- paper + Lineage closure.
