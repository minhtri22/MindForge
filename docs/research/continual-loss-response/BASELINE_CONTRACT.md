# CLRM-0 — Frozen Simple Baseline Contract

Status: **FROZEN**

Any CLRM predictive discovery study must include all three baseline families
below.

All baseline fitting uses training-partition data only.

## B0 — policy-global mean

For each of the six direct response channels, predict the training-partition
mean for that policy/component.

No boundary-state information is used.

## B1 — policy-by-stage mean

For each direct response channel and canonical boundary stage, predict the
training-partition policy×stage mean.

This is the mandatory strongest no-state structural baseline.

## B2 — ridge state-response baseline

Use exactly the same frozen observable pre-boundary feature vector supplied to
the candidate model.

For each direct response channel fit ridge regression after standardizing
features using training data only.

Frozen regularization grid:

```text
lambda ∈ {1e-6, 1e-4, 1e-2, 1, 100}
```

Choose lambda using seed-grouped five-fold inner cross-validation on the
training partition only.

No sealed-validation outcome may influence lambda, feature scaling, feature
selection or baseline choice.

## Strongest-baseline selection

Before sealed validation is opened, select the strongest of B0/B1/B2 using
training-only grouped cross-validation and the frozen macro relative-MAE
objective defined in `QUALIFICATION_GATES.md`.

That baseline identity is then frozen for sealed validation.

## Contrast baselines

B-A and C-A contrast predictions are derived from each baseline's direct A/B/C
response predictions.

No separate post-hoc contrast model is allowed as a weaker comparator.
