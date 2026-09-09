# HANDOFF_011_H3_v3 - H3 correction retry successor

## Status

`READY_FOR_QA_REVIEW`

Authority: `DEVELOPER_CANDIDATE_ONLY`

Branch: `oir-ppv-research`  
HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`

This v3 package is the independent retry successor to the preserved v2 correction, which remains `CORRECTION_FREEZE_INVALIDATED`. No v1 or v2 evidence was overwritten, edited, renamed, moved, or deleted.

## Why v3 exists

The v2 correction stopped after freeze because `H3_CLOSURE_REPORT_v2.md` did not enumerate the exact nuisance intervention triplet for every environment/seed pair. ENV-1 and ENV-4 values are seed-dependent. The v2 identity therefore remains preserved as failed correction evidence.

The only v3 reporting change is that the generated report now emits one exact intervention row for every frozen environment x seed pair and verifies learner pair target/value identity while writing the report. Scientific semantics remain unchanged.

## Frozen v3 identity

- v1 preservation manifest SHA256: `f7aa648559e66ec2d884406b960aff511d73af042af9e7c49d6a59402f8ddfeb`
- source manifest SHA256: `af52a6cebdf18e7032fb9ca5fa0255bbb400cc2a46af8069bf0ae8ea134142d4`
- runtime manifest SHA256: `7f4183f4c49777057469d9c6a5a289c047723ee753a772ec30c5f05bf03b2d74`
- execution manifest SHA256: `666f007c18df39fd27b6d9ffe42d691b3db18281aee9a053ff7c92b97caa969a`
- M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H3 v1 execution manifest SHA256: `045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad`

Frozen identity re-verification after execution: `PASS`.

## Execution result

- smoke: `PASS`
- matrix: `100` attempted exactly once
- complete: `75`
- failed: `0`
- inapplicable: `25`
- retry count: `0`
- comparable candidate-vs-L0 pairs: `60/60`
- v1/v3 scientific reconciliation: `EXACT_MATCH`
- reconciliation mismatches: `0`
- compared encoding bytes: `203118`
- exact-match encoding bytes: `203118`
- report exact intervention coverage: `20/20` environment x seed rows

ENV-3 remains inapplicable because its existing `do(N)` recomputes `Y` and task labels.

## Developer candidate result

Global candidate: `NOT_SUPPORTED`.

| Learner | Mean delta task degradation | Mean delta leak N | Mean delta predictive utility | Mean delta do(N) invariance | Degenerate | Candidate |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| L1 | 0.019716942690158782 | 0.02590022445133357 | -0.25966298368769564 | 0.07311450665481689 | true | `NOT_SUPPORTED` |
| L2 | 0.014342983379150076 | 0.09458967137324942 | -0.24025220144984652 | 0.0629858654001031 | true | `NOT_SUPPORTED` |
| L3 | 0.021214340414680687 | 0.025657312405416136 | -0.25107796685267875 | 0.07252247965771752 | true | `NOT_SUPPORTED` |
| L4 | 0.023407290001286354 | 0.025084617242134063 | -0.2611928128396695 | 0.07235422450587103 | true | `NOT_SUPPORTED` |

`DEGENERATE` is indicative co-occurrence only and is not causal or mechanistic proof.

## Claim boundary

Selected targets `background_noise` in ENV-1, `occlusion` in ENV-2, and `spurious_feature` in ENV-4; seeds `42, 123, 456, 789, 1011`; tested L1-L4 adapted/surrogate configurations versus frozen L0/PCA. ENV-3 is inapplicable because its `do(N)` changes `Y` and task labels.

Raw latent mean shift / derived invariance remains `SCALE_SENSITIVE_DIAGNOSTIC_ONLY`. Cross-learner raw latent shift is not independent invariance proof. ENV-1 mean raw-invariance delta is negative for L1-L4 versus L0; aggregate positive delta is not scale-controlled. The dependency probe is an adapted sensitivity/leakage proxy, not a canonical `N | I` classifier or direct predictive-information estimator.

## Verification

- compile: `PASS`
- focused v3 tests: `14 passed in 10.75s`
- required regression subset: `59 passed in 15.29s`
- post-correction v1 preservation verification: `208 files`, `0 mismatches`
- v2 spot-check hashes unchanged:
  - source manifest: `8edf260aafa71524181dcdc31bea8d892fc6aa6d32d8a74358e60c3f39361f72`
  - runtime manifest: `5c7d9d9fbb4aa1ccf4e5e71db095cc87d286a3538e4f928cf4a0d2dbd6e69f9b`
  - execution manifest: `4c4ea8d57234966760358bc5edf5b7bcf001c1e7a280617716873a2cd395dfa0`

## Principal v3 artifact hashes

- smoke: `a9312e608bfa71be9a07b396100ef86c6693fd541ac6c8bed1926f4b014c158c`
- reconciliation: `81664429b1401930cfd97b5799b3dfce7bd45756b301531e02828cde6a4be6a2`
- summary: `ae91e3e5b1b443159ec7d94b6c9fcb1bb5012566b6226788bfdb749238d665a0`
- closure report: `4e717c6863f0f06cfb0496b804828492b8bbb4402ce7f45cac6c3ea323ecc497`
- matrix execution: `7c5e16213428b85fc8fc6e59507b1534d4889586448dd37e1305b9eafc44cad5`
- execution log: `f75c769776ca277fe2984ad4e5e5dd8e25fbd4fc96904d5fef6723942ee96437`

## QA handoff

Independent QA should review v3 as the successor correction package while retaining v2 as invalidated audit evidence. Developer does not close H3, update `PLAN.md`, start H4, commit, or push before QA acceptance.
