# CPRM-0 — Falsification Gates

Status: **FROZEN PROGRAM TRANSITION GATES v0.1**

## Gate 0 — Program identity / zero-science integrity

PASS only if:

- branch is `research/continual-policy-response`;
- CPRM is explicitly not ACO-2;
- parent ACO closure is `0700601f9196d3c5989fa8eb5169f28b1bb01799`;
- no CPRM scientific runner/result exists;
- no fresh scientific seed manifest is consumed;
- ACO-1 spent seeds and protected KCL cohort remain excluded;
- controller/KCL-7 remain closed.

Failure:

```text
STOP_CPRM_SCOPE_INTEGRITY
```

## Gate 1 — Response-support qualification

The first scientific milestone must establish that the frozen continuous
response measurements are available, non-degenerate enough for prospective
modeling, and supported across the preregistered all-boundary population.

This gate must be designed before execution and may not condition on Y_PRR or
another derived hard label.

Possible outcomes:

```text
PASS_RESPONSE_SUPPORT
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
STOP_INTEGRITY_OR_SUPPORT
```

No predictor/controller qualification occurs at Gate 1.

## Gate 2 — Predictive qualification

Only after Gate 1 PASS.

A candidate state-response model must:

1. use seed-grouped train/validation separation;
2. predict frozen continuous targets/contrasts;
3. beat the strongest frozen applicable baseline by a preregistered material
   margin on primary validation metrics;
4. satisfy any preregistered calibration gate;
5. preserve complete provenance.

Failure:

```text
CONTINUOUS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

No automatic feature/model rescue is authorized.

## Gate 3 — Policy-conditioned factorization

Conditional only.

A separate study may ask whether preserving B/C policy-specific structure adds
value beyond a simpler shared-response representation, but only after Gate 2
qualifies at least one primary response/contrast.

Failure closes factorization without invalidating previously qualified
quantities.

## Gate 4 — Independent fresh replication

Any discovery-qualified response model must reproduce on a fresh cohort frozen
before replication.

No tuning, target changes, baseline changes or materiality changes after
discovery.

Failure:

```text
NO_REPLICATED_CONTINUOUS_RESPONSE_MODEL
```

and controller remains closed.

## Gate 5 — Decision qualification

Only after Gate 4 PASS.

A separately preregistered decision study may evaluate policy value/regret,
plasticity floor, retention, robustness, abstention and resource cost.

This is the earliest point at which an adaptive controller may be
scientifically evaluated.

## Program STOP rules

Stop the active CPRM formulation if:

- all-boundary response support cannot be qualified under a frozen design;
- matched A/B/C integrity fails irreparably;
- predictive models do not materially beat frozen simple baselines;
- discovery gains fail independent replication;
- the program drifts back into hard-label rescue;
- continuation becomes an unbounded feature/model rescue ladder.
