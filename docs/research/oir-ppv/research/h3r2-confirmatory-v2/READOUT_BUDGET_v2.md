# H3R2-CONFIRMATORY-v2 Readout Budget

## Representation input

The verified H3R reconstruction records `output_dim=8` for L0-L4. The freeze task must verify that this remains true for every bound state before accepting this readout contract.

Representation fitting/updating is prohibited.

## Linear readout

Historical-compatible logistic regression:

- solver: `lbfgs`
- penalty: `l2`
- `C=1.0`
- `max_iter=1000`
- `random_state=historical_state_seed`
- architecture search: `0`
- hyperparameter search: `0`

## Nonlinear readout

Exactly one family:

`PolynomialFeatures(degree=2, include_bias=false)` followed by the same logistic-regression specification above.

No degree search, architecture search, learner selection, or hyperparameter tuning is permitted.

For common representation dimension 8, the feature map has `8 + 8*9/2 = 44` degree<=2 non-bias features. Parameter counts must be recorded from the fitted estimator. The degree-2 readout necessarily has greater trainable capacity than the linear readout; this is frozen explicitly rather than hidden.

## Equal-budget definition

Equality means, for each learner/cell:

- identical historical training rows and labels;
- identical deterministic validation folds;
- one fixed configuration per readout (`search_count=1` each; no tuning loop);
- identical logistic solver, regularization coefficient, max iterations and convergence tolerance;
- identical historical-state seed budget;
- identical final fit/evaluation schedule;
- identical fresh test observations and noise realizations;
- no test-informed checkpoint or readout selection.

Exact trainable-parameter equality is not asserted because the intervention being tested is nonlinear decoder expressivity. The generic capacity uplift is controlled prospectively through L0 and the primary difference-in-differences NetRecovery estimand. Because all L0-L4 representations have common output dimension 8, degree-2 capacity is also equal across learners.

## Validation separation

Five-fold out-of-fold validation is deterministic and uses historical training data only. Validation does not choose hyperparameters. Final linear and degree-2 readouts are each refit once on the complete historical training representation before fresh test access.