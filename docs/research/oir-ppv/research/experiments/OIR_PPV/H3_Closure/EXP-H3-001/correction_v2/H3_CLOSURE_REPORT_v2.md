# H3 Closure Report v2 — EXP-H3-001 correction

Status: `READY_FOR_QA_REVIEW`  
Authority: `DEVELOPER_CANDIDATE_ONLY`
Global developer candidate: `NOT_SUPPORTED`

## Exact intervention coverage

| Environment | Selected target | Three frozen values | Eligibility |
| --- | --- | --- | --- |
| ENV-1 | `background_noise` | `[-0.13230397117893647, 0.00442170029001831, 0.12414274167932847]` | task-preserving eligible |
| ENV-2 | `occlusion` | `['heavy', 'none', 'partial']` | task-preserving eligible |
| ENV-3 | `do(N)` | `[-0.5, 0.0, 0.5]` | inapplicable: do(N) changes Y/task labels |
| ENV-4 | `spurious_feature` | `[-1.7985198387132053, 0.040322987365344606, 1.9124792614892996]` | task-preserving eligible |

Learner fidelity: L0=`faithful`; L1=`adapted`; L2=`adapted`; L3=`surrogate`; L4=`adapted`.

The dependency diagnostic is an **adapted sensitivity/leakage proxy**, not a canonical classifier of `N | I` and not a direct estimator of `predictive_information(N | I)`.

Raw latent mean shift / derived invariance is retained exactly as frozen but is `SCALE_SENSITIVE_DIAGNOSTIC_ONLY`. It is not an independent cross-learner success criterion. ENV-1 mean raw-invariance delta is negative for L1-L4 relative to L0; the aggregate positive delta is not scale-controlled.

`DEGENERATE` is only an indicative pattern: higher aggregate raw diagnostic coincides with utility loss. It does not establish causation or mechanism-level invariance.

## Candidate comparisons

| Learner | task degradation W/L/T | leakage W/L/T | utility W/L/T | mean Δ task | mean Δ leak | mean Δ utility | Candidate |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| L1 | 4/11/0 | 3/12/0 | 0/15/0 | 0.019717 | 0.025900 | -0.259663 | `NOT_SUPPORTED` |
| L2 | 5/10/0 | 0/15/0 | 2/13/0 | 0.014343 | 0.094590 | -0.240252 | `NOT_SUPPORTED` |
| L3 | 4/11/0 | 4/11/0 | 0/14/1 | 0.021214 | 0.025657 | -0.251078 | `NOT_SUPPORTED` |
| L4 | 4/11/0 | 3/12/0 | 1/14/0 | 0.023407 | 0.025085 | -0.261193 | `NOT_SUPPORTED` |

Matrix: `{'complete': 75, 'failed': 0, 'inapplicable': 25}`. v1/v2 reconciliation: `EXACT_MATCH`, mismatches=`0`.

## Per-seed evidence

| Learner | Env | Seed | Status | Target | |Delta_N| | Leak_N | Utility |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| L0 | ENV-1 | 42 | complete | background_noise | 0.000000 | 0.213046 | 1.000000 |
| L0 | ENV-1 | 123 | complete | background_noise | 0.000000 | 0.175574 | 1.000000 |
| L0 | ENV-1 | 456 | complete | background_noise | 0.000000 | 0.196239 | 1.000000 |
| L0 | ENV-1 | 789 | complete | background_noise | 0.000000 | 0.189042 | 1.000000 |
| L0 | ENV-1 | 1011 | complete | background_noise | 0.000000 | 0.202596 | 1.000000 |
| L0 | ENV-2 | 42 | complete | occlusion | 0.000000 | 0.222841 | 0.750000 |
| L0 | ENV-2 | 123 | complete | occlusion | 0.068750 | 0.261835 | 0.706250 |
| L0 | ENV-2 | 456 | complete | occlusion | 0.049583 | 0.277040 | 0.726250 |
| L0 | ENV-2 | 789 | complete | occlusion | 0.067917 | 0.213582 | 0.671250 |
| L0 | ENV-2 | 1011 | complete | occlusion | 0.000000 | 0.281683 | 0.750000 |
| L0 | ENV-3 | 42 | inapplicable | do(N) | null | 0.345576 | 0.972222 |
| L0 | ENV-3 | 123 | inapplicable | do(N) | null | 0.397586 | 0.920000 |
| L0 | ENV-3 | 456 | inapplicable | do(N) | null | 0.340079 | 0.940000 |
| L0 | ENV-3 | 789 | inapplicable | do(N) | null | 0.344538 | 0.964706 |
| L0 | ENV-3 | 1011 | inapplicable | do(N) | null | 0.339967 | 0.940000 |
| L0 | ENV-4 | 42 | complete | spurious_feature | 0.055556 | 0.322749 | 0.944444 |
| L0 | ENV-4 | 123 | complete | spurious_feature | 0.083333 | 0.264219 | 0.916667 |
| L0 | ENV-4 | 456 | complete | spurious_feature | 0.022222 | 0.299464 | 0.977778 |
| L0 | ENV-4 | 789 | complete | spurious_feature | 0.044444 | 0.283637 | 0.955556 |
| L0 | ENV-4 | 1011 | complete | spurious_feature | 0.050000 | 0.291943 | 0.950000 |
| L1 | ENV-1 | 42 | complete | background_noise | 0.034364 | 0.264594 | 0.484536 |
| L1 | ENV-1 | 123 | complete | background_noise | 0.055556 | 0.333857 | 0.750000 |
| L1 | ENV-1 | 456 | complete | background_noise | 0.026667 | 0.233331 | 0.660000 |
| L1 | ENV-1 | 789 | complete | background_noise | 0.029412 | 0.216696 | 0.627451 |
| L1 | ENV-1 | 1011 | complete | background_noise | 0.026515 | 0.247393 | 0.806818 |
| L1 | ENV-2 | 42 | complete | occlusion | 0.056667 | 0.225096 | 0.391250 |
| L1 | ENV-2 | 123 | complete | occlusion | 0.067083 | 0.202212 | 0.361250 |
| L1 | ENV-2 | 456 | complete | occlusion | 0.055833 | 0.292731 | 0.352500 |
| L1 | ENV-2 | 789 | complete | occlusion | 0.029167 | 0.226425 | 0.172500 |
| L1 | ENV-2 | 1011 | complete | occlusion | 0.043333 | 0.317110 | 0.402500 |
| L1 | ENV-3 | 42 | inapplicable | do(N) | null | 0.223857 | 0.738889 |
| L1 | ENV-3 | 123 | inapplicable | do(N) | null | 0.154373 | 0.780000 |
| L1 | ENV-3 | 456 | inapplicable | do(N) | null | 0.256166 | 0.713333 |
| L1 | ENV-3 | 789 | inapplicable | do(N) | null | 0.408360 | 0.835294 |
| L1 | ENV-3 | 1011 | inapplicable | do(N) | null | 0.384707 | 0.630000 |
| L1 | ENV-4 | 42 | complete | spurious_feature | 0.074074 | 0.239153 | 0.877778 |
| L1 | ENV-4 | 123 | complete | spurious_feature | 0.077778 | 0.305289 | 0.883333 |
| L1 | ENV-4 | 456 | complete | spurious_feature | 0.020370 | 0.311502 | 0.966667 |
| L1 | ENV-4 | 789 | complete | spurious_feature | 0.046296 | 0.395743 | 0.900000 |
| L1 | ENV-4 | 1011 | complete | spurious_feature | 0.094444 | 0.272861 | 0.816667 |
| L2 | ENV-1 | 42 | complete | background_noise | 0.058419 | 0.348916 | 0.505155 |
| L2 | ENV-1 | 123 | complete | background_noise | 0.030864 | 0.380068 | 0.490741 |
| L2 | ENV-1 | 456 | complete | background_noise | 0.036667 | 0.269153 | 0.660000 |
| L2 | ENV-1 | 789 | complete | background_noise | 0.039216 | 0.286839 | 0.843137 |
| L2 | ENV-1 | 1011 | complete | background_noise | 0.030303 | 0.292431 | 0.829545 |
| L2 | ENV-2 | 42 | complete | occlusion | 0.040833 | 0.302602 | 0.192500 |
| L2 | ENV-2 | 123 | complete | occlusion | 0.054167 | 0.265764 | 0.323750 |
| L2 | ENV-2 | 456 | complete | occlusion | 0.042083 | 0.411478 | 0.501250 |
| L2 | ENV-2 | 789 | complete | occlusion | 0.068333 | 0.279425 | 0.368750 |
| L2 | ENV-2 | 1011 | complete | occlusion | 0.041250 | 0.332857 | 0.446250 |
| L2 | ENV-3 | 42 | inapplicable | do(N) | null | 0.307104 | 0.788889 |
| L2 | ENV-3 | 123 | inapplicable | do(N) | null | 0.176281 | 0.860000 |
| L2 | ENV-3 | 456 | inapplicable | do(N) | null | 0.234315 | 0.820000 |
| L2 | ENV-3 | 789 | inapplicable | do(N) | null | 0.574311 | 0.770588 |
| L2 | ENV-3 | 1011 | inapplicable | do(N) | null | 0.202079 | 0.570000 |
| L2 | ENV-4 | 42 | complete | spurious_feature | 0.062963 | 0.350634 | 0.872222 |
| L2 | ENV-4 | 123 | complete | spurious_feature | 0.072222 | 0.376232 | 0.816667 |
| L2 | ENV-4 | 456 | complete | spurious_feature | 0.074074 | 0.423387 | 0.900000 |
| L2 | ENV-4 | 789 | complete | spurious_feature | 0.000000 | 0.455981 | 1.000000 |
| L2 | ENV-4 | 1011 | complete | spurious_feature | 0.005556 | 0.338566 | 0.994444 |
| L3 | ENV-1 | 42 | complete | background_noise | 0.034364 | 0.261156 | 0.484536 |
| L3 | ENV-1 | 123 | complete | background_noise | 0.061728 | 0.342299 | 0.750000 |
| L3 | ENV-1 | 456 | complete | background_noise | 0.033333 | 0.234300 | 0.640000 |
| L3 | ENV-1 | 789 | complete | background_noise | 0.022876 | 0.202290 | 0.627451 |
| L3 | ENV-1 | 1011 | complete | background_noise | 0.026515 | 0.251287 | 0.795455 |
| L3 | ENV-2 | 42 | complete | occlusion | 0.068333 | 0.183123 | 0.436250 |
| L3 | ENV-2 | 123 | complete | occlusion | 0.038750 | 0.194079 | 0.401250 |
| L3 | ENV-2 | 456 | complete | occlusion | 0.057500 | 0.294013 | 0.367500 |
| L3 | ENV-2 | 789 | complete | occlusion | 0.018750 | 0.288638 | 0.260000 |
| L3 | ENV-2 | 1011 | complete | occlusion | 0.094167 | 0.295091 | 0.386250 |
| L3 | ENV-3 | 42 | inapplicable | do(N) | null | 0.224698 | 0.738889 |
| L3 | ENV-3 | 123 | inapplicable | do(N) | null | 0.154446 | 0.786667 |
| L3 | ENV-3 | 456 | inapplicable | do(N) | null | 0.228203 | 0.713333 |
| L3 | ENV-3 | 789 | inapplicable | do(N) | null | 0.414574 | 0.835294 |
| L3 | ENV-3 | 1011 | inapplicable | do(N) | null | 0.388155 | 0.640000 |
| L3 | ENV-4 | 42 | complete | spurious_feature | 0.075926 | 0.237761 | 0.872222 |
| L3 | ENV-4 | 123 | complete | spurious_feature | 0.075926 | 0.303642 | 0.872222 |
| L3 | ENV-4 | 456 | complete | spurious_feature | 0.012963 | 0.310211 | 0.977778 |
| L3 | ENV-4 | 789 | complete | spurious_feature | 0.044444 | 0.396029 | 0.900000 |
| L3 | ENV-4 | 1011 | complete | spurious_feature | 0.094444 | 0.286430 | 0.811111 |
| L4 | ENV-1 | 42 | complete | background_noise | 0.024055 | 0.246830 | 0.515464 |
| L4 | ENV-1 | 123 | complete | background_noise | 0.055556 | 0.344978 | 0.740741 |
| L4 | ENV-1 | 456 | complete | background_noise | 0.013333 | 0.199289 | 0.660000 |
| L4 | ENV-1 | 789 | complete | background_noise | 0.042484 | 0.208168 | 0.656863 |
| L4 | ENV-1 | 1011 | complete | background_noise | 0.026515 | 0.273097 | 0.806818 |
| L4 | ENV-2 | 42 | complete | occlusion | 0.100000 | 0.188766 | 0.402500 |
| L4 | ENV-2 | 123 | complete | occlusion | 0.043333 | 0.193815 | 0.287500 |
| L4 | ENV-2 | 456 | complete | occlusion | 0.066667 | 0.291178 | 0.375000 |
| L4 | ENV-2 | 789 | complete | occlusion | 0.022083 | 0.214667 | 0.173750 |
| L4 | ENV-2 | 1011 | complete | occlusion | 0.076667 | 0.326961 | 0.395000 |
| L4 | ENV-3 | 42 | inapplicable | do(N) | null | 0.225178 | 0.772222 |
| L4 | ENV-3 | 123 | inapplicable | do(N) | null | 0.149867 | 0.786667 |
| L4 | ENV-3 | 456 | inapplicable | do(N) | null | 0.235914 | 0.733333 |
| L4 | ENV-3 | 789 | inapplicable | do(N) | null | 0.393923 | 0.852941 |
| L4 | ENV-3 | 1011 | inapplicable | do(N) | null | 0.338346 | 0.730000 |
| L4 | ENV-4 | 42 | complete | spurious_feature | 0.096296 | 0.239138 | 0.844444 |
| L4 | ENV-4 | 123 | complete | spurious_feature | 0.085185 | 0.315578 | 0.850000 |
| L4 | ENV-4 | 456 | complete | spurious_feature | 0.012963 | 0.302999 | 0.983333 |
| L4 | ENV-4 | 789 | complete | spurious_feature | 0.040741 | 0.398450 | 0.900000 |
| L4 | ENV-4 | 1011 | complete | spurious_feature | 0.087037 | 0.327846 | 0.838889 |

## Frozen provenance

v1 preservation SHA256: `f7aa648559e66ec2d884406b960aff511d73af042af9e7c49d6a59402f8ddfeb`  
source manifest SHA256: `8edf260aafa71524181dcdc31bea8d892fc6aa6d32d8a74358e60c3f39361f72`  
runtime manifest SHA256: `5c7d9d9fbb4aa1ccf4e5e71db095cc87d286a3538e4f928cf4a0d2dbd6e69f9b`  
v2 execution manifest SHA256: `4c4ea8d57234966760358bc5edf5b7bcf001c1e7a280617716873a2cd395dfa0`  
M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`  
EXP-LRN-001 SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`

Commands:
```text
python pipeline/run_h3_correction_v2.py freeze
python pipeline/run_h3_correction_v2.py smoke
python pipeline/run_h3_correction_v2.py run
python pipeline/run_h3_correction_v2.py aggregate
python pipeline/run_h3_correction_v2.py reconcile
python pipeline/run_h3_correction_v2.py verify-v1-after
python -m py_compile pipeline/run_h3_closure.py pipeline/run_h3_correction_v2.py
python -m pytest tests/test_h3_correction_v2.py -q -p no:cacheprovider --basetemp artifacts/h3_v2_pytest_focused_20260909
python -m pytest tests/test_h3_closure.py tests/test_h2_closure.py tests/test_learner_contract.py tests/test_real_learners.py tests/test_h3_correction_v2.py -q -p no:cacheprovider --basetemp artifacts/h3_v2_pytest_regression_20260909
```

Runtime: `3.13.12 | packaged by conda-forge | (main, Feb  5 2026, 05:41:12) [MSC v.1944 64 bit (AMD64)]`; NumPy `2.4.4`; SciPy `1.17.1`; scikit-learn `1.8.0`; PyYAML `6.0.3`.

## Claim boundary

Selected targets background_noise in ENV-1, occlusion in ENV-2, spurious_feature in ENV-4; seeds 42/123/456/789/1011; tested L1-L4 adapted/surrogate configurations versus frozen L0/PCA. ENV-3 is inapplicable because do(N) changes Y and task labels.

No claim extends to untested nuisance targets, canonical external implementations, external environment families, MindForge, H4, or nuisance robustness in general.
