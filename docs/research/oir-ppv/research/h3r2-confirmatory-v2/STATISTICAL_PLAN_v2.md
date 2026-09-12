# H3R2-CONFIRMATORY-v2 Statistical Plan

Status: `REVIEWED / NOT_FROZEN`

## Scope

Inference is explicitly conditional on the four H3R environments and the five exact reconstructed historical state seeds. No population claim outside these tested conditions is implied.

## Primary unit and pairing

Primary unit: paired `environment × historical_state_seed` cell. Planned cells: `4 × 5 = 20`.

Within each cell, L0-L4 and both readout families evaluate the same fresh test identity and the same clean/noisy observations. All primary comparisons are paired.

## Aggregation

Within environment, mean the valid state-seed cell metrics. Overall metric is the unweighted mean of the four environment means. Row-weighted aggregation is diagnostic only.

## Confidence intervals

Use a 20,000-replicate nonparametric stratified paired bootstrap:

1. hold the four environment identities fixed;
2. independently resample the five historical state-seed cell indices with replacement within each environment;
3. reuse the same bootstrap indices across learners, readouts and paired metrics;
4. compute each candidate metric from the paired replicate;
5. use percentile two-sided intervals.

The bootstrap RNG seed is deterministically derived at the future freeze step from `SHA256(frozen_protocol_bundle_hash || "bootstrap-v2")`; no seed is generated in this review.

## Multiplicity

Family alpha `0.05` across L1-L4. Bonferroni candidate alpha is `0.0125`; all candidate confirmatory intervals are `98.75%` two-sided. The candidate rule is `ANY_ONE`, so no best candidate may be chosen after test.

## Precision

Primary NetRecovery CI half-width must be `<=0.02` to resolve criterion A. Wider intervals yield `UNCERTAIN`; they are not interpreted as support or falsification.

## Validation

Readout hyperparameters/architecture are fixed and not selected from validation. Historical training representations use deterministic five-fold out-of-fold validation solely to estimate preregistered validation NetRecovery. Final readouts are then fit to the complete historical training representation before fresh test evaluation.

`GeneralizationGap=max(0,NetRecovery_validation-NetRecovery_test)`; upper simultaneous CI must be `<=0.02`.

## Missingness

Expected 20 cells. Minimum 18 valid overall and 4 valid per environment. A missing/invalid cell cannot be silently removed and replaced after access. Below the minimum produces `INCONCLUSIVE`; hash/identity/leakage/rerun violations produce `PROTOCOL_FAILURE`.

## Stopping and rerun

Maximum decisive execution count: `1`. Test evidence access must transition atomically `0 -> 1`. If a technical failure occurs before any label/metric access and byte-identical preflight confirms access remains 0, the same locked execution may restart. Once access is 1, no scientific rerun on that evidence identity is allowed; a new experiment requires a new protocol version and new evidence identity.