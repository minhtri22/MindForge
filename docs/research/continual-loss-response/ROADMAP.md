# CLRM Roadmap

Status: **FINITE ROADMAP v0.1**

## CLRM-0 — Specification Foundation

Governance/specification only.

Freeze origin, evidence inheritance, exact response vector, sentinel role,
population, baselines, partitions, qualification gates, exclusions and STOP
roadmap.

No scientific execution.

## CLRM-1 — Loss Response Support Qualification

Fresh support-only cohort.

Purpose:

- verify exact extraction of `L_current_end` and `L_prior_mean_end`;
- verify A/B/C matched integrity;
- verify deterministic reliability;
- verify all-boundary support;
- qualify non-degenerate geometry of all six direct channels.

No predictor fitting.

Only `PASS_LOSS_RESPONSE_SUPPORT` opens CLRM-2 design.

## CLRM-2 — Predictive Discovery

Fresh discovery cohort with seed-grouped D-train and sealed D-val.

Freeze before outcomes:

- observable pre-boundary representation;
- candidate model family;
- preprocessing;
- hyperparameters/search procedure;
- B0/B1/B2 baselines;
- Gate-2 metrics;
- bootstrap procedure.

Fit only after all locks/preflight requirements pass.

Failure triggers convergence review; no automatic model rescue.

## CLRM-3 — Independent Fresh Replication

Fresh Role-R cohort.

No tuning.

Exact discovery-qualified predictor contract must reproduce Gate-2 PASS.

Failure closes the active predictive formulation.

## CLRM-4 — Downstream Decision Governance

Governance-only.

If CLRM-3 PASS, decide whether a separately preregistered decision/value study
is scientifically justified.

CLRM-4 is not itself a controller experiment.

## Controller prohibition

Until a later separately authorized post-CLRM decision study:

```text
online A/B/C selector = CLOSED
controller            = CLOSED
KCL-7                 = CLOSED
```

No predictive milestone may silently become a policy-selection experiment.
