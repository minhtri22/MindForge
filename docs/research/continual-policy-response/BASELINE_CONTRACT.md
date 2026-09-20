# CPRM-0 — Baseline Contract

Status: **FROZEN MINIMUM BASELINE FAMILY**

The first predictive CPRM protocol must compete against simple baselines strong
enough to falsify the need for a learned state-response model.

## 1. Mandatory no-state baselines

At minimum:

### B0 — action-global mean

For each policy and response component, predict the training-partition mean.

### B1 — action-by-stage mean

For each policy, boundary stage and response component, predict the
training-partition stage-conditioned mean.

For A-relative contrasts, use the corresponding training-partition contrast
means.

These baselines use no learned pre-boundary state representation.

## 2. Mandatory low-capacity learned baseline

### B2 — linear state-response baseline

A low-capacity linear or ridge-style model must be included using exactly the
same frozen observable pre-boundary representation supplied to any richer
candidate model.

Its exact regularization and fitting procedure must be frozen in the future
scientific protocol without outcome-driven tuning on the final validation set.

## 3. Strongest-baseline rule

Qualification is always relative to the strongest applicable frozen baseline,
not a preferred weak comparator.

A richer model does not qualify merely by beating B0 if B1 or B2 performs
better.

## 4. Minimum evaluation dimensions

A future predictive protocol must predeclare metrics covering:

- absolute prediction error;
- scale-normalized error;
- calibration / interval reliability when uncertainty is claimed;
- direction accuracy for A-relative contrasts;
- per-stage diagnostics without promoting post-hoc stage winners.

## 5. Material superiority

The numeric material-superiority margin is not set in CPRM-0.

It must be preregistered in the first predictive scientific protocol before any
fresh outcomes are generated.

After observation it may not be relaxed.

## 6. No rescue ladder

Failure against the strongest frozen baseline does not automatically authorize:

- more hidden layers;
- larger capacity;
- extra feature families;
- post-hoc stage-specific models;
- threshold tuning;
- extra seeds.

A new representation/model family requires a separately justified uncertainty,
not merely failure of the previous candidate.
