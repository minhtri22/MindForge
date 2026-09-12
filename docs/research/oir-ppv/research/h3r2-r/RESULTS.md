# H3R2-R Closure Results

Status: **PROTOCOL_DEVIATION**

This document closes the H3R2-R prospective execution without changing the frozen raw evidence. All numerical results below are descriptive. They are not used to manufacture a confirmatory verdict after results access.

## Evidence integrity

- Historical reconstruction: **100/100 exact train-representation SHA-256 matches**, `mismatch_count=0`.
- Historical source commit: `e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51`.
- Reconstruction aggregate SHA-256: `aa0b534db0d5f7220f29e25d6e68e596f45735db8fa55b1a0e73bc0185d75d7c`.
- Prospective seeds: 20 fresh seeds, unique and disjoint from the historical seed set.
- Prospective execution: 20/20 cells complete, 800 rows total.
- Scientific evidence access: `0 -> 1`.
- Prospective labels/metrics accessed: `true`.
- Rerun count: `0`.
- First result consumption: `2026-09-11T23:34:59Z`.

## Descriptive aggregate risk

Aggregation is the unweighted mean over 20 fresh seeds x 4 environments = 80 test-environment values per learner/readout mode. Lower risk is better.

| Readout | Learner | Clean risk | Noisy risk | Noise delta |
|---|---:|---:|---:|---:|
| linear | L0 | 0.0873603489389054 | 0.10138412821963019 | +0.014023779280724791 |
| linear | L1 | 0.32583070799027714 | 0.3278364005241486 | +0.002005692533871461 |
| linear | L2 | 0.2925528228008455 | 0.2940572007021707 | +0.0015043779013252377 |
| linear | L3 | 0.32556466259275524 | 0.3310153040555959 | +0.005450641462840633 |
| linear | L4 | 0.33021662476034064 | 0.3319656323726244 | +0.0017490076122837488 |
| degree2 | L0 | 0.1807593377935888 | 0.17642729884485134 | -0.00433203894873746 |
| degree2 | L1 | 0.3139523626176444 | 0.3146795834217823 | +0.0007272208041378958 |
| degree2 | L2 | 0.28090751327375196 | 0.28276221913354876 | +0.0018547058597968018 |
| degree2 | L3 | 0.3201036658566553 | 0.3193969811232824 | -0.0007066847333728752 |
| degree2 | L4 | 0.3222100975036945 | 0.3246097872508979 | +0.0023996897472033933 |

The linear L0 control by environment is:

| Environment | Clean risk | Noisy risk | Noise delta |
|---|---:|---:|---:|
| ENV-1 | 0.06918078072108705 | 0.08608844370228921 | +0.016907662981202165 |
| ENV-2 | 0.08592421854917223 | 0.104956751424897 | +0.01903253287572476 |
| ENV-3 | 0.1063756403498299 | 0.12153445470622615 | +0.015158814356396252 |
| ENV-4 | 0.08796075613553235 | 0.09295634304510836 | +0.004995586909576008 |

## RelativeRecovery

`RelativeRecovery` has no definition in the frozen H3R2-R protocol and no repository definition was found under the frozen evidence branch. Therefore there is **no protocol-faithful RelativeRecovery value to report**. Introducing a formula after prospective metrics were accessed would be a post-hoc metric definition. No such value is used for closure.

## Confirmatory adjudication

`PROSPECTIVE_PROTOCOL_FREEZE_v1.md` did not freeze the requested quantitative acceptance/statistical criteria before result access: clean-recovery margin, reproducibility fraction, noise non-inferiority margin, validation-to-test tolerance, baseline-control rule, or CI/statistical decision plan.

Because the decisive prospective evidence has already been consumed once, these criteria cannot be backfilled without contaminating confirmatory interpretation. The H3R2-R result is therefore closed as **PROTOCOL_DEVIATION**, not `SUPPORTED`, `PARTIALLY_SUPPORTED`, or `FALSIFIED`.

Historical statuses remain unchanged:

- H3R: `FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Q-H3R.1: `PARTIAL_MECHANISM_DIAGNOSIS`.
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`.
- Recommended next state: `REVIEW_BEFORE_H4`.
