# HANDOFF_011_H3_v2 - H3 Provenance / Causal-Isolation Correction

Status: `CORRECTION_FREEZE_INVALIDATED`

## 1. Correction summary

Implemented the versioned H3 correction through v1 preservation, v2 source/runtime/execution freeze, causal-isolation smoke, one controlled 100-cell replay, aggregation, exact v1/v2 scientific reconciliation, focused tests, regression tests, and post-correction v1 integrity verification.

The replay itself reproduced v1 exactly, but the final developer self-audit found one reporting-contract gap: `H3_CLOSURE_REPORT_v2.md` does not enumerate the exact three intervention values for every seed/environment combination. Numeric selected values vary by seed in ENV-1 and ENV-4, so the report cannot satisfy the task wording by showing only one representative value triplet. Correcting this requires changing reporting source after the v2 source freeze. Under `DEV_TASK_011_FIX_01`, that requires stopping with `CORRECTION_FREEZE_INVALIDATED`; no patch/retry is permitted under the same v2 identity.

## 2. Changed / created files

- `pipeline/run_h3_correction_v2.py`
- `tests/test_h3_correction_v2.py`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/v1_preservation_manifest.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/source_manifest_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/runtime_environment_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/h3_execution_manifest_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/h3_execution_manifest_v2.sha256`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/h3_smoke_evidence_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/artifact_reconciliation_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/h3_summary_v2.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v2/H3_CLOSURE_REPORT_v2.md`
- `artifacts/h3_closure/EXP-H3-001/correction_v2/matrix_execution_v2.json`
- `artifacts/h3_closure/EXP-H3-001/correction_v2/execution_log_v2.jsonl`
- `artifacts/h3_closure/EXP-H3-001/correction_v2/effective_configs/*`
- `artifacts/h3_closure/EXP-H3-001/correction_v2/full/<CELL_ID>/paired_evidence_v2.json`

Local coordination task `tasks/DEV_TASK_011_FIX_01.md` was not modified, committed, or pushed.

## 3. Git / frozen identity

- Branch: `oir-ppv-research`
- HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- Working tree: dirty (pre-existing plus local correction outputs)
- Scoped dirty inventory SHA256 at freeze: `e6260f66fcdbd68066e62fbfef614acf113a2c154552de525e6222b8ce9e1595`
- No commit or push performed.

## 4. v1 preservation before / after

- v1 preservation inventory: `208` files
- v1 paired evidence: `100/100`
- v1 effective configs: `100/100`
- Before correction: `0` mismatches
- After correction: `0` mismatches
- v1 preservation manifest SHA256: `f7aa648559e66ec2d884406b960aff511d73af042af9e7c49d6a59402f8ddfeb`

Frozen handoff hashes reverified before correction:
- `h3_smoke_evidence.json`: `9fa875b86802c123eab437a4e0046e45b39b2a6e18c987698cd47abeb043bddf`
- `h3_summary.json`: `a53230cd033c05a4d765a2997d2d4b60fdd9af6b0dd223d0cededad33dc81ee8`
- `H3_CLOSURE_REPORT.md`: `5f3d03ba29fc0793139c29401b13315a38e61f4c6969fd3a42cf168dc92943b9`

## 5. v2 provenance hashes

- `source_manifest_v2.json`: `8edf260aafa71524181dcdc31bea8d892fc6aa6d32d8a74358e60c3f39361f72`
- `runtime_environment_v2.json`: `5c7d9d9fbb4aa1ccf4e5e71db095cc87d286a3538e4f928cf4a0d2dbd6e69f9b`
- `h3_execution_manifest_v2.json`: `4c4ea8d57234966760358bc5edf5b7bcf001c1e7a280617716873a2cd395dfa0`
- `h3_smoke_evidence_v2.json`: `a9312e608bfa71be9a07b396100ef86c6693fd541ac6c8bed1926f4b014c158c`
- `artifact_reconciliation_v2.json`: `99f7ca1bcd152cbdbc4fc30a286d6e2ca3228c745c9ed8ea22c2fe9bedeb0d77`
- `h3_summary_v2.json`: `ae91e3e5b1b443159ec7d94b6c9fcb1bb5012566b6226788bfdb749238d665a0`
- `H3_CLOSURE_REPORT_v2.md`: `312135c1aa2f15ec1ad83ad23731ce7eaa0ce54dfd199fa1899e7cbdbc3a7297`
- `matrix_execution_v2.json`: `34a7f795676d0520d57073c0154ebdcc4830ebec1d583b2ed53e0c665d2ea52e`
- `execution_log_v2.jsonl`: `23b2d3d799c6733740597d14b0433889b5f479fe27b5b4b9c79693034b3c97ae`
- M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H3 v1 execution manifest SHA256: `045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad`

The source manifest covers the correction runner, v1 runner/tests, correction tests, M3 runner, causal/dependency modules, learner modules, environment generators/base, M3 protocol, EXP-LRN-001 manifest, all 100 learner-cell configs, and all four base environment configs.

## 6. Runtime / commands

- Python executable: `C:\Users\minht\miniforge3\python.exe`
- Python: `3.13.12 | packaged by conda-forge | (main, Feb  5 2026, 05:41:12) [MSC v.1944 64 bit (AMD64)]`
- numpy: `2.4.4`
- scipy: `1.17.1`
- scikit_learn: `1.8.0`
- pyyaml: `6.0.3`

Exact frozen commands:
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

Observed verification output: focused correction suite `13 passed in 10.17s`; required regression subset `58 passed in 15.93s`; compile PASS.

## 7. Smoke and causal isolation

Smoke `L1-vs-L0 / ENV-4 / seed 42`: `PASS`. Same factual rows, labels, selected target, intervention values, task state, and context; both learners satisfy all six causal-isolation booleans.

Across the full v2 matrix, eligible ENV-1/2/4 interventions record before/after hashes for observations, labels, task state, context, full nuisance metadata, target nuisance, and non-target nuisance. Tests verify all five seeds. ENV-3 remains inapplicable and explicitly shows state/context preserved while `do(N)` changes labels.

Selected targets remain frozen: ENV-1=`background_noise`, ENV-2=`occlusion`, ENV-3=`do(N)`, ENV-4=`spurious_feature`.

## 8. Matrix execution

- Attempted cells: `100`
- Complete: `75`
- Failed: `0`
- Inapplicable: `25` (all ENV-3)
- Comparable candidate-vs-L0 pairs on ENV-1/2/4: `60/60`
- One-attempt/no-retry policy: enforced

## 9. v1/v2 reconciliation

- Status: `EXACT_MATCH`
- Mismatch count: `0`
- Reconciliation records: `104` (100 cells + 4 aggregate fields)
- Compared scientific encoding bytes: `203118`
- Exact-match encoding bytes: `203118`
- Scientific result replay: exact; no cell or aggregate scientific field changed.

## 10. Developer scientific candidates

| Learner | mean Δ task degradation | mean Δ leakage | mean Δ utility | Degenerate | Candidate |
| --- | ---: | ---: | ---: | --- | --- |
| L1 | +0.019717 | +0.025900 | -0.259663 | `true` | `NOT_SUPPORTED` |
| L2 | +0.014343 | +0.094590 | -0.240252 | `true` | `NOT_SUPPORTED` |
| L3 | +0.021214 | +0.025657 | -0.251078 | `true` | `NOT_SUPPORTED` |
| L4 | +0.023407 | +0.025085 | -0.261193 | `true` | `NOT_SUPPORTED` |

Authority: `DEVELOPER_CANDIDATE_ONLY`. Global scientific direction remains `NOT_SUPPORTED`.

## 11. Claim boundary

Selected targets `background_noise` in ENV-1, `occlusion` in ENV-2, and `spurious_feature` in ENV-4; seeds 42, 123, 456, 789, and 1011; tested L1-L4 adapted/surrogate configurations versus frozen L0/PCA. ENV-3 is inapplicable because its `do(N)` changes `Y` and task labels.

No claim extends to untested nuisance targets, canonical external learner implementations, external environment families, MindForge, H4, or nuisance robustness in general.

## 12. Diagnostic / probe limitations

- Raw latent mean shift and derived invariance remain `SCALE_SENSITIVE_DIAGNOSTIC_ONLY`; cross-learner raw latent shift is not an independent success criterion.
- `DEGENERATE` remains only an indicative co-occurrence of higher aggregate raw diagnostic and utility loss; it is not a causal/mechanistic finding.
- Frozen dependency analysis is an adapted sensitivity/leakage proxy, not a canonical `N | I` classifier or direct estimator of `predictive_information(N | I)`.

## 13. Tests

```text
python -m py_compile pipeline/run_h3_closure.py pipeline/run_h3_correction_v2.py
PASS
python -m pytest tests/test_h3_correction_v2.py -q -p no:cacheprovider --basetemp artifacts/h3_v2_pytest_focused_20260909
13 passed in 10.17s
python -m pytest tests/test_h3_closure.py tests/test_h2_closure.py tests/test_learner_contract.py tests/test_real_learners.py tests/test_h3_correction_v2.py -q -p no:cacheprovider --basetemp artifacts/h3_v2_pytest_regression_20260909
58 passed in 15.93s
python pipeline/run_h3_correction_v2.py verify-v1-after
VERIFIED_AFTER_CORRECTION: 208 files, 0 mismatches
```

## 14. Blocking limitation / stop evidence

Post-freeze self-audit found the generated corrected report does not explicitly enumerate the exact three selected intervention values for every seed/environment row. Because ENV-1 and ENV-4 numeric intervention values are seed-dependent, a representative seed-42 triplet is insufficient for the explicit reporting acceptance criterion. Fixing report generation requires changing `pipeline/run_h3_correction_v2.py`, which is frozen in `source_manifest_v2.json`.

Per the task stop rule, the v2 identity is therefore invalidated for further modification. Existing replay/reconciliation evidence is preserved and MUST NOT be overwritten or retried under this v2 identity.

## 15. Acceptance self-check

1. [x] Original v1 unchanged before/after: `PASS`
2. [x] v2 source/runtime/commands/config/protocol frozen before smoke/replay: `PASS`
3. [x] drift guard implemented: `PASS`
4. [x] one controlled attempt per cell: `PASS`
5. [x] 100 explicit cells: `PASS`
6. [x] 75/0/25 counts reproduced: `PASS`
7. [x] 60/60 pair identity checks: `PASS`
8. [x] matrix-level causal isolation evidence: `PASS`
9. [x] v1/v2 scientific reconciliation zero mismatch: `PASS`
10. [x] aggregates/labels recomputed from v2 cells: `PASS`
11. [ ] corrected report exact target/value wording: `FAIL - per-seed value enumeration incomplete`
12. [x] focused/regression tests: `PASS`
13. [x] H1/H2 unchanged: `PASS`
14. [x] PLAN.md H3 status untouched by this task: `PASS`
15. [x] H4/MindForge unopened: `PASS`
16. [x] directly checkable handoff: `PASS with blocking status`

Final status: `CORRECTION_FREEZE_INVALIDATED`

No `PLAN.md` update. No H3 closure. No H4 start. No MindForge integration. No commit/push.
