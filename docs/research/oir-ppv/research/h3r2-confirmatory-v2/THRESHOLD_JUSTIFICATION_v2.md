# H3R2-CONFIRMATORY-v2 Threshold Justification

No threshold below was selected to make H3R2-R v1.0 pass. v1.0 numerical outcomes are not acceptance evidence for v2.

| Threshold | Value | Unit / direction | Scientific meaning | Provenance category |
|---|---:|---|---|---|
| baseline_gap_min | 0.05 | error-rate; lower CI >= | at least five percentage points of fresh linear deficit must exist before asking whether it was recovered | PRACTICAL |
| clean_recovery_margin | 0.02 | error-rate; lower CI >= | nonlinear readout must close at least two percentage points of candidate-vs-L0 gap beyond L0 uplift | PRACTICAL |
| relative_recovery_min | 0.25 | fraction; lower CI >= | at least one quarter of the fresh linear candidate-vs-L0 deficit is recovered | PRACTICAL |
| reproducibility_fraction | 0.70 | fraction >= | strong majority of valid cells show at least the clean recovery margin | PRACTICAL |
| environment_coverage | 3/4 | environments >= | recovery must span most predeclared environments rather than one environment | PRACTICAL |
| noise_noninferiority_margin | 0.01 | error-rate; upper CI <= | nonlinear readout may add at most one percentage point candidate-specific noise penalty; one half of clean margin | FORMAL/PRACTICAL |
| validation_test_tolerance | 0.02 | error-rate; upper CI <= | test recovery may not degrade from validation by more than the entire minimum meaningful clean recovery | FORMAL/PRACTICAL |
| family_alpha | 0.05 | probability | familywise error budget for four candidates | SCIENTIFIC |
| candidate_alpha | 0.0125 | probability | Bonferroni `0.05/4`; 98.75% two-sided candidate CI | FORMAL |
| minimum_valid_cells | 18/20 | cells >= | retain at least 90% of planned paired cells | PRACTICAL |
| minimum_valid_per_environment | 4/5 | cells/env >= | prevent one environment from being represented by too few state seeds | PRACTICAL |
| max_primary_ci_half_width | 0.02 | error-rate <= | uncertainty in primary NetRecovery cannot exceed the minimum meaningful recovery | SCIENTIFIC/PRACTICAL |

## Power / precision policy

The primary inferential population is fixed by the exact reconstructed H3R states: four tested environments and five historical representation-state seeds. Creating extra representation seeds would change the frozen representation object and is prohibited. Therefore planned `N=20` paired state/environment cells is fixed prospectively.

The protocol uses a precision gate rather than adaptive sample-size expansion: if the multiplicity-adjusted NetRecovery CI half-width exceeds `0.02`, the candidate is `UNCERTAIN` and the overall experiment may be `INCONCLUSIVE`. No rerun or extra cells may be added after evidence access.

H3R2-R v1.0 may be cited only as pilot/development history. This review does not use its observed effect size to set any boundary above.