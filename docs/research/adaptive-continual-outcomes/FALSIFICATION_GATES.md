# ACO Falsification Gates

Status: **FROZEN PROGRAM TRANSITION GATES v0.1**

These gates govern phase transitions. A later milestone-specific protocol may add stricter numeric gates, but may not weaken these after observing outcomes.

## Gate 0 — Origin / scope integrity

PASS only if:

- KCL-6.5.9.x remains closed;
- no KCL-6.5.9.9 is opened;
- protected KCL confirmatory cohort remains untouched;
- ACO is a separately named branch/program;
- no controller exists in the ACO initialization commit.

Failure: `STOP_SCOPE_INTEGRITY`.

## Gate 1 — ACO-1 target-stability integrity

ACO-1 may execute only if:

- exact KCL A/B/C policies and thresholds are reproduced;
- fresh ACO seeds are disjoint from all historical/protected seeds;
- all three policy branches start from matched pre-boundary state;
- no outcome-model fitting occurs;
- perturbation bands and adjudication are frozen in `aco1-target-stability-protocol.md`.

Scientific outcomes:

- `HARD_TARGET_MARGIN_INSTABILITY_SUPPORTED`;
- `HARD_TARGET_MARGIN_INSTABILITY_NOT_SUPPORTED`;
- `TARGET_STABILITY_INCONCLUSIVE`;
- or `STOP_INTEGRITY_OR_SUPPORT`.

A negative target-instability result does **not** resurrect the hard-label controller program.

## Gate 2 — ACO-2 continuous outcome predictability

ACO-2 requires a separate protocol committed after ACO-1 closure and before fresh ACO-2 outcomes.

Minimum program-level requirements:

1. predict continuous policy-specific outcomes/contrasts, not derived labels as the primary target;
2. include frozen simple baselines, at minimum stage-only/mean-by-stage and a low-capacity linear baseline;
3. use seed-grouped train/validation separation;
4. report absolute error, normalized error, calibration, and contrast-direction accuracy;
5. define a material baseline-superiority margin before execution;
6. no controller derivation in the same milestone.

If the frozen primary metric does not materially beat the strongest baseline:

```text
ACO-2 = NEGATIVE
CONTINUOUS_OUTCOME_PREDICTABILITY_NOT_QUALIFIED
```

and no representation rescue is automatically authorized.

## Gate 3 — Policy-conditioned factorization

Only admissible if ACO-2 qualifies and replicates at least one continuous quantity/contrast.

Must test whether preserving B/C identity improves predictive quality over an exchange-invariant alternative.

Failure closes factorization; it does not invalidate any already-qualified continuous quantity.

## Gate 4 — Independent replication

No decision study may start from discovery-only qualification.

At least one fresh replication cohort must reproduce:

- material prediction gain;
- calibration;
- directional contrast reliability;
- integrity/provenance.

Failure:

```text
NO_REPLICATED_OUTCOME_MODEL
CONTROLLER_REMAINS_CLOSED
```

## Gate 5 — Decision/controller study

Only after Gate 4 PASS.

A controller study must be separately preregistered and evaluated on:

- policy value / regret or equivalent direct decision utility;
- plasticity floor;
- retention margin;
- robustness;
- abstention/uncertainty behavior if included;
- compute/memory overhead.

No controller may be merged into stable MindForge architecture from ACO discovery evidence alone.
