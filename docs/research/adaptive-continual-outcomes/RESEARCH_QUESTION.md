# ACO Research Question

Status: **FROZEN PROGRAM QUESTION v0.1**

## Primary question

> Tại một continual-learning task boundary, liệu observable pre-boundary state có cho phép dự đoán **calibrated policy-specific continuous outcomes** của các action A/B/C trên fresh data tốt hơn các frozen simple baselines, trước khi các outcome đó bị threshold thành hard safe-action/mechanism labels hay không?

## Primary outcome object

For each boundary `X` and policy `a`:

```text
Y(X,a) = [
  plasticity_auc,
  final_current_accuracy,
  prior_retention,
  worst_prior_accuracy
]
```

Primary contrasts:

```text
C_B(X) = Y(X,B) - Y(X,A)
C_C(X) = Y(X,C) - Y(X,A)
```

The model is not asked to predict `Y_PRR` directly in the first outcome-prediction study.

## Why this question is falsifiable

ACO fails as a predictive program if, under a frozen fresh validation design:

- action-conditioned continuous outcomes do not beat simple stage/reference baselines by the preregistered material margin;
- calibration is poor;
- action contrasts are not directionally reliable;
- gains disappear on fresh replication;
- support is insufficient for the preregistered outcome ranges.

A negative result closes the corresponding formulation. It does not authorize extra features by default.

## Required prerequisite

Before fitting any ACO outcome model, ACO-1 must quantify whether the historical hard target is materially concentrated near its frozen decision margins.

ACO-1 does not change any KCL threshold.

## Non-question

ACO is **not** asking:

> Can we find any model that picks A/B/C correctly after enough tuning?

That is downstream and currently unauthorized.
