# CLRM-0 — Data Role and Partition Contract

Status: **FROZEN**

CLRM separates four scientific data roles.

## Role S — support qualification

CLRM-1 uses a fresh support-only cohort to determine whether the exact two-axis
loss response vector has sufficient measurement support/reliability for
predictive work.

Role S is spent after CLRM-1.

It may not later be used for model fitting, feature selection, hyperparameter
selection, sealed validation or replication.

## Role D-train — predictive development

Only after CLRM-1 PASS, a new fresh CLRM-2 discovery cohort is frozen.

Its training partition may be used for:

- model fitting;
- feature standardization;
- training-only grouped cross-validation;
- candidate hyperparameter selection;
- strongest-baseline selection.

## Role D-val — sealed validation

A disjoint seed-grouped subset of the CLRM-2 discovery cohort is sealed before
any fitting.

It is opened once for the preregistered final candidate and frozen strongest
baseline.

No tuning may follow sealed-validation inspection.

## Role R — independent replication

CLRM-3 uses a completely fresh cohort that is disjoint from S, D-train and
D-val and from all historical exclusions.

The discovery-qualified representation, target, baselines, preprocessing,
model family, fitted-procedure specification, hyperparameters, metrics and
gates are frozen before Role R outcomes exist.

## Split rules

- seed is the grouping unit;
- all three boundaries from a seed remain in one role;
- exact seed counts/manifests must be preregistered before each scientific
  milestone;
- CLRM-0 generates no fresh manifest and consumes no seed.
