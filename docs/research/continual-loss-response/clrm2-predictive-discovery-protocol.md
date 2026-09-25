# CLRM-2 — Predictive Discovery Protocol

Status: **PREREGISTERED / PREDICTOR FITTING BLOCKED**

Parent:

```text
CLRM-1 PASS / CLOSED
PASS_LOSS_RESPONSE_SUPPORT
closure commit = 2dd27566961e6e31d9938b6d27084ef6a6e6e6ed
```

CLRM-2 asks exactly one question:

> Can the frozen observable pre-boundary state representation predict the six
> policy-specific CE-loss response channels materially better than the frozen
> strongest simple baseline on a sealed seed-grouped validation cohort, while
> satisfying the frozen point-calibration gate?

No controller is implemented.

## 1. Frozen target

Exactly the six CLRM direct response channels:

```text
A.current_loss
A.prior_mean_loss
B.current_loss
B.prior_mean_loss
C.current_loss
C.prior_mean_loss
```

The exact same-state CLRM-1 response extractor is reused unchanged.

Accuracy remains sentinel/diagnostic only.

No target may be dropped or reweighted after outcomes.

## 2. OBS11-v1 representation

The candidate and B2 use exactly one pre-existing observable representation,
derived from the historical KCL-6.5.9.2 PRIMARY_FEATURES contract.

Feature order:

```text
STAGE_2
STAGE_3
H1_M1_RMS
H2_SQRT_M2_RMS
H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS
H4_TASK_DRIFT_RELATIVE_L2
H5_PRESSURE_TO_DRIFT_RATIO
H6_DRIFT_PRESSURE_COSINE
H7_PRIOR_MEAN_ACCURACY
H8_PRIOR_WORST_ACCURACY
H9_CURRENT_TASK_LOSS
```

Definitions come from the frozen `kcl656_boundary_health_signal.py`
pre-boundary extractor.

`STAGE_2` and `STAGE_3` are one-hot indicators; stage 1 is the reference
state.

The extractor receives no next-task or policy-outcome input.

No localized S3/S4, future-probe, virtual-policy-response, or post-outcome
feature family is permitted in CLRM-2.

## 3. Candidate family — RBF-KRR-v1

Exactly one candidate family:

```text
multi-output RBF kernel ridge regression
```

For standardized feature vectors:

```text
K(x,z) = exp(-gamma * ||x-z||^2)
```

Fit all six raw loss outputs jointly with one shared kernel/hyperparameter pair:

```text
alpha = solve(K + lambda*I, Y)
prediction(x) = k(x,X_train) @ alpha
```

Feature standardization is fit on training data only.

No stochastic initialization exists.

Hyperparameter grid:

```text
gamma  ∈ {0.02, 0.10, 0.50}
lambda ∈ {1e-4, 1e-2, 1}
```

Choose exactly one global `(gamma, lambda)` using frozen 5-fold seed-grouped
D-train cross-validation.

Selection objective:

1. compute six OOF channel MAEs;
2. normalize each MAE by that channel's full D-train robust scale
   `max(p90-p10, 1e-12)`;
3. take the unweighted mean across six channels;
4. choose the minimum;
5. exact tie-break: smaller gamma, then smaller lambda.

No additional model family is authorized after D-train inspection.

## 4. Mandatory baselines

### B0 — policy-global mean

Six training means, no state.

### B1 — policy-by-stage mean

Six policy-response means separately by boundary stage.

### B2 — linear ridge state-response

Uses the exact OBS11-v1 vector.

Feature standardization uses training data only.

For each direct channel, choose its own lambda by frozen seed-grouped five-fold
OOF MAE:

```text
lambda ∈ {1e-6, 1e-4, 1e-2, 1, 100}
```

Final B2 is refit on all D-train using those six frozen lambdas.

## 5. Strongest-baseline selection

Before D-val exists, create OOF predictions for B0, B1 and tuned B2 over the
entire D-train cohort.

For each baseline family:

```text
score =
mean_j(
  MAE_j / max(Dtrain_p90_j - Dtrain_p10_j, 1e-12)
)
```

The baseline family with the smallest score becomes the single frozen
`strongest_baseline` used for sealed validation.

Exact tie-break preference:

```text
B2 > B1 > B0
```

This is deliberately conservative toward the richer comparator.

## 6. Fixed seed-grouped CV

Five folds.

For seed `s`:

```text
fold(s) =
uint64_be(SHA256("CLRM2-CV-v1|" + decimal(s))[0:8]) mod 5
```

All three boundaries from a seed stay in one fold.

All five folds must contain at least one seed or training stops for integrity.

## 7. Fresh discovery cohort

Exactly 240 fresh seeds:

```text
D-train = 160 seeds = 480 boundaries
D-val   =  80 seeds = 240 boundaries
```

Both manifests are frozen before any CLRM-2 scientific outcome exists.

Generation phrase:

```text
MindForge|CLRM-2|predictive-discovery|v1
```

Hashes:

```text
ALL:
05b7d1a077b3b4a152882fc42e67f6189d3f66d55ff0dc50b859ffd022480374

D-train:
bc7f7dd941a5ec280156e9cbfc3f1501565213db7efa3b940dd4d189891b93e8

D-val:
a2287c490acf6c8a94cff56be1a5eb4aaa0115fce26675312ac590d5bfe6ee96
```

Mandatory disjointness includes all historical KCL, protected KCL, ACO-1,
CPRM-1, MSA-1, MSA-3 and spent CLRM-1 Role-S.

No seed substitution or extra seed is allowed after outcomes.

## 8. Two-lock anti-leakage execution

### CLRM2-A — Training lock

Before D-train execution, independently verify:

- protocol/source/feature/substrate blobs;
- both D-train and D-val manifests;
- all exclusions;
- candidate/baseline/CV procedures;
- no D-train/D-val result exists;
- no predictor has been fit on fresh CLRM-2 data.

Only after CLRM2-A PASS may D-train be collected and fitted.

### Candidate freeze

Using D-train only:

1. collect exactly 160 seeds / 480 boundaries;
2. fit/tune RBF-KRR-v1 by frozen CV;
3. tune B2 by frozen CV;
4. select strongest baseline by frozen OOF rule;
5. refit final candidate and selected baseline on all D-train;
6. preserve `CLRM2_DISCOVERY_CANDIDATE.json`.

The package must contain all fitted scalers, hyperparameters, candidate
coefficients/training support vectors and baseline parameters required for
prediction.

Once preserved, D-train may not be rerun.

### CLRM2-B — Validation lock

Before any D-val seed is executed, independently verify:

- exact candidate package hash;
- candidate was produced only from D-train;
- D-val remains absent/unobserved;
- D-val manifest exact;
- Gate-2 adjudicator exact.

Only then may D-val be collected.

This prevents D-val outcomes from affecting representation, hyperparameters,
baseline identity or fitted parameters.

## 9. Sealed-validation Gate 2

For each direct channel `j`:

```text
MAE_candidate_j
MAE_baseline_j
ratio_j = MAE_candidate_j / MAE_baseline_j
```

If any strongest-baseline MAE equals zero:

```text
STOP_INTEGRITY_OR_BASELINE
```

Define:

```text
macro_ratio = mean(ratio_j)
relative_gain = 1 - macro_ratio
```

Baseline-superiority PASS requires all:

```text
relative_gain >= 0.10

whole-seed paired bootstrap 95% percentile interval
upper endpoint (97.5th percentile) of macro_ratio < 1.0

every direct channel:
ratio_j <= 1.05
```

Bootstrap:

```text
20,000 resamples
RNG seed = 72002
sample 80 D-val seeds with replacement
include all three boundaries for each sampled seed
```

## 10. Point calibration

For every direct channel on sealed D-val, fit assessment-only OLS:

```text
observed_y = alpha_j + beta_j * predicted_y
```

No recalibration is applied.

PASS requires every channel:

```text
0.80 <= beta_j <= 1.20
abs(alpha_j) / MAE_baseline_j <= 0.10
```

Zero/near-zero prediction variance makes calibration fail.

## 11. Diagnostic contrasts

After one-shot Gate-2 adjudication, report for B-A and C-A, for each loss axis:

- MAE;
- sign accuracy;
- Spearman rank correlation;
- per-stage diagnostics.

Contrast diagnostics are non-gating and cannot rescue Gate-2.

Accuracy sentinel distributions are also diagnostic only and are revealed only
after adjudication.

## 12. One-shot validation verdict

Allowed final verdicts:

```text
LOSS_RESPONSE_PREDICTABILITY_QUALIFIED
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
STOP_INTEGRITY_OR_BASELINE
```

PASS iff both baseline-superiority and calibration gates pass.

No model-family rescue, new feature family, threshold relaxation or extra
validation seeds are permitted after D-val outcomes.

## 13. Downstream

```text
LOSS_RESPONSE_PREDICTABILITY_QUALIFIED
→ authorize CLRM-3 DESIGN ONLY

LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
or STOP_INTEGRITY_OR_BASELINE
→ mandatory formal convergence review
```

Even PASS does not authorize a controller.

CLRM-3 must independently replicate the exact discovery-qualified predictor
contract with no tuning.
