# CLRM-0 — Falsification and Predictive Qualification Gates

Status: **FROZEN PROGRAM GATES v0.1**

## Gate 0 — Specification integrity

PASS only if:

- branch is `research/continual-loss-response`;
- exact parent MSA closure
  `64138ab9cb09dcb56a387d3b1f500063eff8302d` is an ancestor;
- CLRM is explicitly not CPRM-2;
- exact two-axis CE-loss response vector is frozen;
- accuracy is sentinel-only;
- all-boundary population is frozen;
- baseline/partition/exclusion/roadmap contracts exist;
- no CLRM fresh seed manifest exists;
- no CLRM scientific runner/result exists;
- predictor/controller/KCL-7 are closed.

Failure:

```text
STOP_CLRM_SCOPE_INTEGRITY
```

## Gate 1 — CLRM-1 response-support qualification

Before any predictor is fit, CLRM-1 must prospectively qualify:

- exact same-state extraction of both primary loss components;
- matched A/B/C fork integrity;
- deterministic reliability;
- complete all-boundary support;
- sufficient non-degenerate response geometry for all six direct channels.

The exact numeric support thresholds and fresh manifest must be preregistered
before CLRM-1 execution.

Possible results:

```text
PASS_LOSS_RESPONSE_SUPPORT
NEGATIVE_LOSS_RESPONSE_GEOMETRY
STOP_INTEGRITY_OR_SUPPORT
```

Only `PASS_LOSS_RESPONSE_SUPPORT` can authorize CLRM-2 design.

## Gate 2 — CLRM-2 predictive discovery

Use the frozen six direct outputs.

For each output channel `j` on sealed validation:

```text
MAE_candidate_j
MAE_baseline_j
ratio_j = MAE_candidate_j / MAE_baseline_j
```

If any frozen strongest-baseline MAE is exactly zero, predictive superiority
for that channel is impossible and Gate 2 cannot PASS.

Define:

```text
macro_ratio = mean(ratio_j over all 6 direct channels)
relative_gain = 1 - macro_ratio
```

### Baseline-superiority gate

PASS requires all:

```text
relative_gain >= 0.10

whole-seed paired bootstrap 95% upper CI of macro_ratio < 1.0

for every direct channel:
ratio_j <= 1.05
```

Thus aggregate improvement must be at least 10%, statistically paired by seed,
and no direct response channel may degrade by more than 5%.

### Point-calibration gate

For each direct channel, assess without recalibration:

```text
observed_y = alpha_j + beta_j * predicted_y
```

using sealed-validation observations.

PASS requires for every direct channel:

```text
0.80 <= beta_j <= 1.20

abs(alpha_j) / MAE_baseline_j <= 0.10
```

The calibration fit is assessment only. Its coefficients may not be applied
back to predictions.

### Required contrast diagnostics

For both B-A and C-A and both loss components, report:

- contrast MAE;
- sign accuracy;
- rank correlation;
- per-stage diagnostics.

Contrast diagnostics may not be promoted post hoc into an alternate PASS if
the direct-response superiority/calibration gates fail.

Gate-2 PASS:

```text
LOSS_RESPONSE_PREDICTABILITY_QUALIFIED
```

Otherwise:

```text
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

No model-family rescue is automatic after failure.

## Gate 3 — CLRM-3 independent replication

Freeze the discovery-qualified model/representation/preprocessing/baseline and
all Gate-2 metrics before Role-R outcomes exist.

Replication PASS requires the exact Gate-2 qualification to PASS again without
tuning.

Failure:

```text
NO_REPLICATED_LOSS_RESPONSE_MODEL
```

and triggers convergence review.

## Gate 4 — downstream governance only

Only after Gate 3 PASS may a governance review ask whether a separate decision
study is justified.

Gate 4 itself does not authorize a controller.

## Program STOP rules

Formal convergence review is mandatory after:

- Gate 1 NEGATIVE/STOP;
- Gate 2 failure;
- Gate 3 replication failure;
- any request to change the frozen target merely because prediction failed.

No CLRM-2.1/2.2 rescue ladder is permitted.
