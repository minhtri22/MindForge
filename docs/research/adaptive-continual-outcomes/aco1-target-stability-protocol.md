# ACO-1 — Target-Stability Qualification Protocol

Status: **PREREGISTERED BEFORE ANY ACO-1 SCIENTIFIC EXECUTION**

Program: Adaptive Continual Outcome Modeling (ACO)

## 1. Scientific question

The hard KCL target `Y_PRR = MECH{P+R,R}` is derived from thresholded continuous counterfactual outcomes.

ACO-1 asks:

> Is a material fraction of the hard target determined by boundaries lying within one natural decision-resolution unit of the already-frozen plasticity/retention/accuracy thresholds?

ACO-1 is diagnostic only.

It does not fit a predictor, redesign features, modify thresholds, or implement a controller.

## 2. Frozen parent policy contract

Policies:

```text
A = CARRY_ALL
B = RESET_ALL
C = CARRY_STEP_RESET_MOMENTS
```

Frozen thresholds inherited unchanged:

```text
STRICT_CURRENT_MIN     = 0.95
PLASTICITY_BENEFIT_MIN = 0.01 AUC
RETENTION_MARGIN       = 1/24
```

For P ∈ {B,C}:

```text
plasticity_gain =
    auc_delta_vs_A >= 0.01
    OR
    (A.final_accuracy < 0.95 AND P.final_accuracy >= 0.95)

retention_ok =
    retention_delta_vs_A >= -(1/24)

absolute_ok =
    P.final_accuracy >= 0.95

safe_P =
    plasticity_gain AND retention_ok AND absolute_ok
```

No threshold changes are permitted.

## 3. Fresh cohort

ACO-1 uses exactly 40 fresh seeds:

```text
714845,799297,471852,671302,797856,
525370,494800,333039,618491,662800,
265044,434671,501990,723350,393434,
774787,806053,890854,613906,707487,
415555,641958,505262,776960,428051,
767077,464825,448672,416287,770416,
596609,359597,454064,431281,705347,
294795,641624,345481,326782,242385
```

These seeds were deterministically generated from `SHA256("ACO1|i")` and frozen in this protocol.

Preflight must reject execution if any seed collides with any historical KCL scientific seed or protected KCL cohort.

The protected KCL cohort is never substituted.

## 4. Experimental unit

For each seed and each canonical boundary after T1/T2/T3:

1. construct the exact matched pre-boundary state;
2. fork A/B/C from that same state;
3. execute the canonical next-task policy branch;
4. record all continuous outcomes required by the frozen safety predicates;
5. derive the historical hard labels only after continuous outcomes are written.

Expected design:

```text
40 seeds × 3 boundaries × 3 policies
```

No ACO model is trained.

## 5. Margin definitions

For each P ∈ {B,C}:

```text
m_auc(P) = auc_delta_vs_A - 0.01
m_ret(P) = retention_delta_vs_A + 1/24
m_acc(P) = P.final_accuracy - 0.95
```

When `A.final_accuracy < 0.95`, also record the repair margin:

```text
m_repair(P) = P.final_accuracy - 0.95
```

The exact hard predicate remains unchanged.

## 6. Frozen natural resolution bands

Diagnostic near-margin bands:

```text
epsilon_auc = 0.01
epsilon_ret = 1/24
epsilon_acc = 1/24
```

A policy predicate is `NEAR_MARGIN` when at least one decisive active margin has absolute value <= its corresponding epsilon.

These bands are for diagnosis only and do not replace the KCL thresholds.

## 7. Label-sensitivity diagnostic

For each boundary, recompute the derived hard label under one-at-a-time diagnostic perturbations of the threshold by ± one frozen resolution band.

This is a sensitivity analysis, not a threshold change.

Define:

```text
flip = 1
```

if any one-at-a-time perturbation changes the hard mechanism label.

Primary population: boundaries whose canonical label is `Y_PRR`.

## 8. Primary statistics

For canonical `Y_PRR` boundaries:

1. `near_margin_rate`;
2. `label_flip_rate`;
3. distribution of minimum normalized margin:
   `min(|m_j| / epsilon_j)`.

Use whole-seed bootstrap, 10,000 resamples, 95% percentile intervals.

Seeds are the resampling unit; individual boundaries are not independently resampled.

## 9. Support gate

ACO-1 scientific adjudication requires at least:

```text
30 canonical Y_PRR boundaries
```

across at least two of the three boundary stages.

Otherwise:

```text
ACO-1 = STOP
TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

No extra seeds may be added after outcome inspection.

## 10. Materiality gates

Pre-registered materiality floors:

```text
near_margin_rate >= 0.20
label_flip_rate  >= 0.10
```

Adjudication:

### PASS — instability supported

```text
HARD_TARGET_MARGIN_INSTABILITY_SUPPORTED
```

iff both whole-seed bootstrap 95% CI lower bounds are at or above their materiality floors.

### NEGATIVE — instability not supported

```text
HARD_TARGET_MARGIN_INSTABILITY_NOT_SUPPORTED
```

iff both 95% CI upper bounds are below their materiality floors.

### INCONCLUSIVE

```text
TARGET_STABILITY_INCONCLUSIVE
```

for all mixed/overlapping cases.

No threshold may be relaxed.

## 11. Interpretation rules

PASS means:

> hard-label instability near frozen continuous thresholds is a material contributor on the fresh cohort.

It does **not** mean the thresholds are wrong.

NEGATIVE means:

> the near-margin explanation is not supported at the preregistered materiality level.

It does **not** mean continuous outcomes are uninformative.

ACO-2 remains a separate hypothesis because it changes the prediction object to quantities directly aligned with the original continual-learning objective.

## 12. Integrity requirements

Before execution:

- exact source SHA recorded;
- exact protocol SHA-256 recorded;
- historical seed collision audit PASS;
- protected-cohort absence PASS;
- parent policy/threshold identity tests PASS;
- matched fork identity before action PASS;
- no outcome-model code path reachable from ACO-1 runner;
- one-shot adjudicator implemented and tested on synthetic fixtures only.

Scientific execution is unauthorized until this preflight closes.
