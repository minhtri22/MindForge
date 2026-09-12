# H3R2-CONFIRMATORY-v2 Metric Registry

All verdict-relevant metrics are defined here before freeze. Risk means task error rate and is bounded in `[0,1]`; `LOWER_IS_BETTER`.

Indices: candidate `i ∈ {1,2,3,4}`, L0 control `0`, readout `p ∈ {linear, degree2}`, paired cell `c=(environment, historical_state_seed)`.

## Clean risk

`R_clean(i,p,c) = mean(1[prediction != label])` on the complete frozen test split for cell `c`.

Orientation: `LOWER_IS_BETTER`.

## Candidate-vs-L0 clean gap

`Gap_p(i,c) = R_clean(i,p,c) - R_clean(0,p,c)`.

Aggregate: unweighted mean across valid cells, with each environment contributing the mean of its valid historical-state-seed cells and the four environment means then equally weighted.

Positive means candidate is worse than L0.

## Primary estimand: NetRecovery

`NetRecovery(i,c) = Gap_linear(i,c) - Gap_degree2(i,c)`.

Equivalent form:

`NetRecovery(i,c) = [R_clean(i,linear,c)-R_clean(i,degree2,c)] - [R_clean(0,linear,c)-R_clean(0,degree2,c)]`.

`NetRecovery(i)` is the equal-environment aggregate.

Orientation: `HIGHER_IS_BETTER`.

Interpretation: positive values are candidate-specific nonlinear recovery after subtracting generic L0 nonlinear uplift.

## Canonical RelativeRecovery

Let `Gap_linear(i)` be the aggregated fresh linear clean gap.

If the multiplicity-adjusted lower CI of `Gap_linear(i)` is at least `0.05`:

`RelativeRecovery(i) = NetRecovery(i) / Gap_linear(i)`.

Otherwise RelativeRecovery is `NOT_ADJUDICABLE_FOR_RECOVERY` for that candidate.

Orientation: `HIGHER_IS_BETTER`.

Sign convention:

- `<0`: nonlinear readout worsens the candidate-specific gap relative to L0;
- `0`: no candidate-specific recovery;
- `(0,1)`: partial closure of the linear gap;
- `1`: full closure;
- `>1`: over-closure relative to L0.

## Reproducibility

Cell recovery indicator:

`I_recovery(i,c)=1[NetRecovery(i,c) >= 0.02]`.

`ReproducibilityFraction(i)=sum(I_recovery)/N_valid`.

Environment success requires at least `3/5` valid state-seed cells in that environment to satisfy the cell recovery indicator. Candidate reproducibility passes only with fraction `>=0.70` and at least `3/4` successful environments.

Orientation: `HIGHER_IS_BETTER`.

## Noise metric

`NoisePenalty(i,p,c)=R_noisy(i,p,c)-R_clean(i,p,c)`.

`NoiseGap(i,p,c)=NoisePenalty(i,p,c)-NoisePenalty(0,p,c)`.

`NoiseChange(i,c)=NoiseGap(i,degree2,c)-NoiseGap(i,linear,c)`.

Aggregate identically to NetRecovery.

Orientation: `NON_INFERIORITY / LOWER_IS_BETTER`; upper simultaneous CI must be `<=0.01`.

## Validation→test generalization

Validation uses deterministic five-fold out-of-fold predictions on historical training representations. No hyperparameter is selected from validation.

`GeneralizationGap(i)=max(0, NetRecovery_validation(i)-NetRecovery_test(i))`.

Orientation: `LOWER_IS_BETTER`; upper simultaneous CI must be `<=0.02`.

## Baseline-control criterion

Criterion E is the sign check on the same L0-controlled primary estimand: multiplicity-adjusted lower CI of `NetRecovery(i)` must be `>0`.

## Precision metric

`PrimaryCIHalfWidth(i)=(CI_high(NetRecovery)-CI_low(NetRecovery))/2`.

Orientation: `LOWER_IS_BETTER`; must be `<=0.02` for criterion A to resolve as PASS. Wider uncertainty produces `UNCERTAIN`, not support/falsification.

## Diagnostic-only metrics

Raw candidate uplift, raw L0 uplift, per-environment risks, per-seed risks, parameter counts, convergence diagnostics and row-weighted summaries are `DIAGNOSTIC_ONLY` unless explicitly used by the frozen criteria above. They cannot replace the primary estimand post-test.