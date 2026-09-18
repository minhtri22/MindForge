# KCL-6.5.6 — Boundary Plasticity Health Signal Qualification

## Abstract

KCL-6.5.5 falsified the hypothesis that one fixed AdamW boundary policy can satisfy plasticity, retention, and robustness simultaneously. KCL-6.5.6 therefore asks a narrower prerequisite question:

> can a non-oracular scalar signal available immediately at a task boundary predict whether a reset-style optimizer intervention will be both useful for next-task plasticity and safe for prior-task retention?

The experiment pre-registers nine candidate signals derived only from already-observed model/optimizer/task state. For each of 20 discovery seeds and each of three boundaries after T1/T2/T3, a matched one-boundary counterfactual is run from a common carry-all reference state. The target label, `SAFE_RESET_OPPORTUNITY`, is positive only when reset-all B or carry-step/reset-moments C either improves next-task acquisition AUC by at least 0.01 or repairs a <95% acquisition failure, while also preserving retention within 1/24 and ending the next task at >=95%.

Signal selection is performed by leave-one-seed-out threshold fitting, with a frozen stage-only baseline and minimum balanced-accuracy, sensitivity, specificity, and baseline-superiority gates.

No candidate satisfies all discovery gates.

The best candidate is:

```
H4_TASK_DRIFT_RELATIVE_L2
```

with out-of-seed:

```
balanced accuracy = 0.65533
sensitivity       = 0.73171
specificity       = 0.57895
```

The stage-only baseline balanced accuracy is:

```
0.60270
```

so H4 exceeds it by approximately:

```
+0.05263
```

and passes the balanced-accuracy, sensitivity, and stage-superiority requirements. However, the frozen specificity gate is:

```
>= 0.60
```

and H4 reaches only:

```
0.57895
```

Therefore the official result is:

```
KCL-6.5.6 = NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

Per protocol, no rule is frozen and no fresh confirmatory cohort is run.

The scientific implication is not that boundary health is unpredictable. Rather, the current evidence says that none of the pre-registered **single scalar** summaries of optimizer moments, model drift, current-task loss, or retained accuracy is sufficient to qualify as a robust standalone health sensor. Task-relative parameter drift is the strongest lead, but it still produces too many false positives.

## 1. Upstream trigger

KCL-6.5.5 closed by frozen-protocol adjudication:

```
FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

The three fixed policies produced distinct tradeoffs:

- carry-all A preserved more retention than C but suffered severe acquisition failures;
- reset-all B repaired some failures and preserved retention, but reduced acquisition AUC on average;
- carry-step/reset-moments C improved plasticity AUC but harmed retention and did not repair every failure.

This made a fixed boundary action scientifically inadequate.

A valid adaptive controller would require a signal available before future-task outcome is known.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl656-protocol.md`

Protocol commit:

`c50c79b5a7b8952033a6847c5519400d36ea344f`

Protocol SHA-256:

`484b9be90c0e746af839a7dc4ff184efdf8be1874f14dec73481f272f0bfd55c`

Discovery scientific source:

`abf90a5ccd24659d60c3eda88ec3fa4556184521`

The protocol froze before discovery:

- candidate signals;
- outcome label;
- discovery seeds;
- confirmatory seeds;
- threshold-fitting algorithm;
- leave-one-seed-out split;
- stage-only baseline;
- qualification gates;
- confirmatory bootstrap.

No candidate or threshold was added after discovery.

## 3. Discovery cohort

Discovery seeds are the already-observed KCL-6.5.5 cohort:

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

Each seed contributes three boundary instances:

```
after T1
after T2
after T3
```

Total:

```
20 × 3 = 60 boundary instances
```

Because these seeds had already been used in KCL-6.5.5, they are explicitly discovery-only.

## 4. Matched boundary construction

The reference trajectory always follows:

```
A = CARRY_ALL
```

At each boundary:

1. extract features before any next-task tensor is passed;
2. clone exact model / optimizer / memory state;
3. apply A/B/C;
4. train one next task with identical current and replay samples;
5. compute counterfactual next-task plasticity and prior retention;
6. continue only the A branch as the reference trajectory.

Thus later boundary labels are not contaminated by recursively applying B or C.

Counterfactual integrity passes for all 60 instances.

## 5. Anti-leakage architecture

The implementation structurally separates:

```
extract_boundary_features(...)
```

from:

```
run_next_task_counterfactual(...)
```

The feature function receives:

- current model;
- current optimizer;
- pre-task model snapshot;
- already-observed tasks;
- current completed task;
- boundary index.

It does not receive:

- next task;
- future task name/family;
- next-task tensors;
- future gradients;
- future A/B/C outcomes.

The test suite explicitly verifies that the feature extractor has no `next_task` or `future_task` parameter.

## 6. Primary target

For P in {B,C}:

```
DeltaAUC_P = AUC_P - AUC_A
DeltaR_P   = retention_P - retention_A
```

P is a safe beneficial reset iff:

- `DeltaAUC_P >= 0.01`, or P repairs an A final accuracy below 95%;
- `DeltaR_P >= -1/24`;
- P final next-task accuracy >=95%.

Primary label:

```
SAFE_RESET_OPPORTUNITY = 1
```

iff B or C satisfies these conditions.

Discovery label distribution:

```
positive = 41
negative = 19
```

Positive prevalence:

```
68.33%
```

Carry-all absolute next-task failures:

```
3 / 60 boundaries
```

The target therefore mostly captures safe plasticity improvement opportunities, not only catastrophic carry failures.

## 7. Stage-only baseline

The frozen non-eligible baseline uses only:

```
BOUNDARY_INDEX ∈ {1,2,3}
```

under the same leave-one-seed-out threshold fitting procedure.

Observed:

```
balanced accuracy = 0.60270
sensitivity       = 0.73171
specificity       = 0.47368
accuracy          = 0.65000
```

This demonstrates that task age/stage alone contains some information, but is not strong enough to qualify.

Any candidate had to beat this baseline by at least 0.05 balanced accuracy.

## 8. Candidate results

Frozen candidates:

### H1 — M1_RMS

```
BA   = 0.26380
sens = 0.31707
spec = 0.21053
```

No evidence of useful standalone prediction.

### H2 — SQRT_M2_RMS

```
BA   = 0.52567
sens = 0.68293
spec = 0.36842
```

Second-moment magnitude alone is not sufficiently discriminative.

### H3 — BIAS_CORRECTED_ADAM_PRESSURE_RMS

```
BA   = 0.34852
sens = 0.17073
spec = 0.52632
```

Global Adam pressure magnitude does not predict safe intervention opportunity.

### H4 — TASK_DRIFT_RELATIVE_L2

```
BA   = 0.65533
sens = 0.73171
spec = 0.57895
accuracy = 0.68333
```

This is the strongest candidate.

Against stage baseline:

```
0.65533 - 0.60270 = +0.05263
```

H4 passes:

- BA >=0.65;
- sensitivity >=0.60;
- stage superiority >=0.05.

But fails:

```
specificity >=0.60
```

because:

```
specificity = 0.57895
```

The failure is small numerically but the gate was frozen before execution and cannot be relaxed.

### H5 — PRESSURE_TO_DRIFT_RATIO

```
BA   = 0.57125
sens = 0.19512
spec = 0.94737
```

This signal is highly conservative: it identifies negatives well but misses most safe reset opportunities.

### H6 — DRIFT_PRESSURE_COSINE

```
BA   = 0.22529
sens = 0.29268
spec = 0.15789
```

Not useful as a standalone scalar.

### H7 — PRIOR_MEAN_ACCURACY

```
BA   = 0.34082
sens = 0.36585
spec = 0.31579
```

Observed-task mean accuracy does not reveal future boundary action suitability.

### H8 — PRIOR_WORST_ACCURACY

```
BA   = 0.36906
sens = 0.31707
spec = 0.42105
```

Worst retained accuracy is also inadequate alone.

### H9 — CURRENT_TASK_LOSS

```
BA   = 0.44608
sens = 0.36585
spec = 0.52632
```

Current-task loss is not a reliable future-plasticity health signal.

## 9. Discovery qualification

Frozen candidate requirements:

```
balanced accuracy >= 0.65
sensitivity       >= 0.60
specificity       >= 0.60
BA                >= stage baseline + 0.05
```

No H1–H9 candidate satisfies all four.

Therefore:

```
selected signal = NONE
```

No final threshold/direction is frozen.

No `kcl656_rule.json` is created.

## 10. Why confirmatory execution is forbidden

The protocol states:

> If no signal discovery-qualifies, close KCL-6.5.6 NEGATIVE and do not authorize the fresh confirmatory cohort.

Therefore the pre-registered confirmatory seeds:

```
13635 ... 17473
```

remain untouched.

No confirmatory workflow is created.

This avoids converting a failed discovery screen into post-hoc feature engineering on nominally fresh data.

## 11. Scientific interpretation

The result falsifies a simple but important hypothesis:

> one scalar derived from current model/AdamW/boundary performance state is sufficient to decide whether reset-style intervention is safe and useful.

The tested scalar families cover:

- first-moment magnitude;
- second-moment magnitude;
- bias-corrected Adam pressure;
- task parameter drift;
- optimizer-pressure / drift scale;
- drift-pressure direction;
- prior retained accuracy;
- current-task loss.

None qualifies.

## 12. The strongest remaining clue: task-relative drift

H4 is meaningfully different from the other candidates:

```
BA = 0.6553
stage baseline = 0.6027
```

and it is the only candidate that simultaneously passes the frozen BA, sensitivity, and stage-superiority conditions.

Its weakness is false-positive control:

```
specificity = 0.5789
```

This suggests parameter drift contains real boundary-health information, but its meaning depends on context.

A large or small drift alone is insufficient.

The missing information may be relational, for example:

- drift conditioned on optimizer moment geometry;
- drift conditioned on retention reserve;
- parameter-group-specific drift rather than global drift;
- directional overlap between drift and protected/replayed knowledge;
- local curvature/update sensitivity.

KCL-6.5.6 does not test these composites.

## 13. Why moment magnitudes alone fail despite KCL-6.5.4

KCL-6.5.4 causally established that old `exp_avg` and `exp_avg_sq` can each produce failure under specific counterfactual pairings with a fixed model state.

KCL-6.5.6 shows something different:

> their global magnitudes do not tell us when reset will be safe and beneficial across diverse boundary states.

There is no contradiction.

Causal sufficiency of a component is not equivalent to predictive usefulness of its scalar norm.

The relevant variable may be compatibility between moment tensors and the current parameter/representation state rather than moment magnitude itself.

## 14. Architectural consequence

KCL-6.5.5 suggested an adaptive boundary controller.

KCL-6.5.6 now shows that a controller cannot yet be justified from a single simple health scalar.

The architecture should therefore **not** implement:

```
if drift > threshold: reset
```

or:

```
if moment_norm > threshold: reset
```

at this stage.

The evidence instead points toward a richer **Boundary State Representation** from which health may need to be inferred.

## 15. What is now missing

The architecture appears to need two distinct pieces:

### 1. Boundary State Encoder / Representation

Represent interactions among:

- model transition;
- optimizer moment geometry;
- retention state;
- perhaps parameter groups/subspaces.

### 2. Boundary Policy Controller

Use that representation to choose a boundary action.

KCL-6.5.6 only tested whether piece 1 could collapse to one scalar. It cannot, under the frozen candidate set and gates.

## 16. Verdict

```
KCL-6.5.6 = NEGATIVE
NO_DISCOVERY_BOUNDARY_HEALTH_SIGNAL
```

This is a valid scientific negative result, not an implementation failure.

No confirmatory run is authorized.

## 17. Provenance

Protocol commit:

`c50c79b5a7b8952033a6847c5519400d36ea344f`

Implementation initial commit:

`005485cb877afdfd9343318e96da7f7cbe3eb3e6`

Pre-execution drift-snapshot correction:

`7179e09889c9c97bf0d93e0417eb7dee82269e9c`

Contract tests:

`70fc83e5c965f16d24295a2f6e0a4d64278ec07b`

Canonical discovery source:

`abf90a5ccd24659d60c3eda88ec3fa4556184521`

Canonical workflow:

`35379614417`

Focused tests:

`20 passed (10 KCL-6.5.6 + 10 KCL-6.5.5)`

Artifact:

`10561158655`

Artifact ZIP SHA-256:

`d3e316b62684e26d1a5c10ed164def7ca9d85ae2fbeb4163f443d5bf733930d3`

Machine-readable discovery evidence:

`experiments/kernel_cl/results/kcl656_discovery.json`

## 18. Next scientific requirement

Do not relax H4 specificity and do not manually combine signals from discovery outcomes.

A new milestone, if opened, must pre-register a richer hypothesis before touching the untouched confirmatory cohort.

The most defensible next direction is to test **relational / multivariate boundary state hypotheses**, especially combinations involving:

```
task-relative parameter drift
×
optimizer moment geometry
×
retention state
```

with a new discovery/confirmation split or nested protocol that preserves the untouched KCL-6.5.6 confirmatory seeds.

Only after a representation generalizes should an adaptive boundary controller be implemented.
