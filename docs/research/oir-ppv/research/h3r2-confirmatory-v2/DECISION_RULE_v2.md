# H3R2-CONFIRMATORY-v2 Decision Rule

Status: `REVIEWED / NOT_FROZEN`

Verdict set is finite:

- `SUPPORTED_UNDER_TESTED_CONDITIONS`
- `PARTIALLY_SUPPORTED`
- `FALSIFIED_UNDER_TESTED_CONDITIONS`
- `INCONCLUSIVE`
- `PROTOCOL_FAILURE`

## Integrity gate

Before scientific criteria are evaluated, require all frozen hashes/identities to match, `representation_changed=false`, no test leakage, one authorized evidence transition `0 -> 1`, and `rerun_count=0` after evidence consumption. Failure returns `PROTOCOL_FAILURE` immediately.

## Data gate

Expected cells: `4 environments × 5 historical-state seeds = 20`.

Scientific adjudication requires at least `18/20` valid cells and at least `4/5` valid cells in every environment. Missing/invalid cells are never silently dropped or rerun after evidence access. Below this threshold returns `INCONCLUSIVE` unless an integrity rule was violated, in which case `PROTOCOL_FAILURE` takes precedence.

## Candidate eligibility

Fresh linear deficit must exist. Candidate is eligible only if the multiplicity-adjusted lower CI of `Gap_linear(i)` is `>=0.05`.

If the upper CI is `<0.05`, status is `NOT_ELIGIBLE`. If the CI crosses `0.05`, status is `UNCERTAIN`. If all candidates are `NOT_ELIGIBLE`, overall verdict is `INCONCLUSIVE` because the failure phenomenon to be explained did not reproduce.

## Criteria A-E

A. Clean recovery: lower simultaneous CI of `NetRecovery >= 0.02`, lower simultaneous CI of `RelativeRecovery >= 0.25`, and NetRecovery CI half-width `<=0.02`.

B. Reproducibility: `ReproducibilityFraction >=0.70` and successful environments `>=3/4`.

C. Noise non-inferiority: upper simultaneous CI of `NoiseChange <=0.01`.

D. Generalization: upper simultaneous CI of `GeneralizationGap <=0.02`.

E. L0 baseline control: lower simultaneous CI of `NetRecovery >0`. This is algebraically embedded in A but is emitted separately for auditability.

For CI-based criteria: entirely on pass side = PASS; entirely on fail side = FAIL; crossing the threshold = UNCERTAIN.

## Candidate state

- `FULL_SUPPORT`: A,B,C,D,E all PASS.
- `PARTIAL_SUPPORT`: A,D,E PASS and exactly one of B/C FAIL while the other PASS.
- `DEFINITIVE_FAIL`: any of A,D,E is definitively FAIL, or both B and C FAIL after A,D,E pass.
- `UNCERTAIN`: any verdict-relevant CI crosses its boundary, precision fails, or valid-cell threshold fails.
- `NOT_ELIGIBLE`: fresh linear deficit is definitively below baseline-gap threshold.

## Multiple-candidate rule

The prospective hypothesis is `ANY_ONE`, matching the pre-existing H3R.2 prediction. L1-L4 are all evaluated; no candidate is selected after test. Four candidate confirmatory CIs use Bonferroni familywise correction.

Overall rule, in priority order:

1. integrity failure -> `PROTOCOL_FAILURE`;
2. any `FULL_SUPPORT` -> `SUPPORTED_UNDER_TESTED_CONDITIONS`;
3. else any `PARTIAL_SUPPORT` -> `PARTIALLY_SUPPORTED`;
4. else any `UNCERTAIN` -> `INCONCLUSIVE`;
5. else all candidates `NOT_ELIGIBLE` -> `INCONCLUSIVE`;
6. else -> `FALSIFIED_UNDER_TESTED_CONDITIONS`.

No reviewer discretion is permitted.