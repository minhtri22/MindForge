# HANDOFF_011_H3 - H3 Paired Nuisance Robustness Closure

## 1. Implementation / execution summary

Implemented `DEV_TASK_011_H3_CLOSURE` by operationalizing the existing frozen H3 contract over the accepted `EXP-LRN-001` learner definitions and seeds.

The H3 execution identity was frozen before decisive execution:

- primary baseline: `L0` PCA;
- candidates: `L1..L4`;
- environments: `ENV-1..ENV-4`;
- seeds: `42, 123, 456, 789, 1011`;
- downstream predictor semantics: `LogisticRegression(max_iter=1000, random_state=seed)`, matching M3;
- primary metric: `Delta_N = Perf_factual - Perf_do(N)`, with smaller absolute degradation better;
- leakage: frozen `DependencyAnalyzer` nuisance probe;
- `do_N_response`: mean representation shift and `1/(1+mean_shift)` invariance;
- predictive utility: factual downstream classification accuracy;
- ENV-4 shortcut-learning score retained;
- frozen failure threshold `< 0.5` retained for intervention-level invariance failures.

No learner, seed, baseline, environment, threshold, M3 protocol, H1/H2 artifact, or `PLAN.md` H3 status was changed.

## 2. Task-preserving intervention result

Focused semantic checks established:

- `ENV-1`: task-preserving nuisance intervention supported;
- `ENV-2`: task-preserving nuisance intervention supported;
- `ENV-4`: task-preserving nuisance/shortcut intervention supported;
- `ENV-3`: existing `do(N)` recomputes `Y` and task labels, so it is retained as `INAPPLICABLE` for decisive task-preserving H3 evidence.

No semantic repair was applied to ENV-3 because doing so would change the frozen intervention semantics.

Smoke evidence on `L1-vs-L0 / ENV-4 / seed 42` passed all required pair-identity checks:

- same factual rows;
- same task labels;
- same nuisance target;
- same intervention values;
- task labels preserved for both baseline and candidate.

## 3. Changed / created files

Source/tests:

- `pipeline/run_h3_closure.py`
- `tests/test_h3_closure.py`

Frozen H3 execution identity:

- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/h3_execution_manifest.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/h3_execution_manifest.sha256`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/h3_smoke_evidence.json`

Evidence/reporting:

- `artifacts/h3_closure/EXP-H3-001/full/*/paired_evidence.json`
- `artifacts/h3_closure/EXP-H3-001/matrix_execution.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/h3_summary.json`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/H3_CLOSURE_REPORT.md`

The local coordination task file remains local-only and was not committed/pushed by this task.

## 4. Git / source provenance

Branch:

`oir-ppv-research`

Source HEAD used for H3 freeze/execution:

`0521c5754a32e2625930de75fe2635c6ce5ec9a0`

Working tree:

`dirty`

The tree already contained substantial pre-existing research/coordination changes. No unrelated cleanup/reset was performed.

Frozen identities:

- M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H3 execution manifest SHA256: `045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad`

Derived output hashes:

- `h3_smoke_evidence.json`: `9fa875b86802c123eab437a4e0046e45b39b2a6e18c987698cd47abeb043bddf`
- `h3_summary.json`: `a53230cd033c05a4d765a2997d2d4b60fdd9af6b0dd223d0cededad33dc81ee8`
- `H3_CLOSURE_REPORT.md`: `5f3d03ba29fc0793139c29401b13315a38e61f4c6969fd3a42cf168dc92943b9`

## 5. Matrix identity and counts

Frozen matrix:

- learners: `L0, L1, L2, L3, L4`;
- environments: `ENV-1, ENV-2, ENV-3, ENV-4`;
- seeds: `42, 123, 456, 789, 1011`;
- total learner/environment/seed cells: `100`.

Execution result:

- complete task-preserving cells: `75`;
- failed cells: `0`;
- inapplicable ENV-3 cells: `25`;
- comparable candidate-vs-L0 pairs: `60/60` across ENV-1, ENV-2, ENV-4;
- intervention-level failure cases below frozen `0.5` invariance threshold: `0` in complete cells.

## 6. Developer scientific candidates

All labels below are `DEVELOPER_CANDIDATE_ONLY` and require independent QA acceptance.

| Learner | Complete pairs | mean Δ task degradation vs L0 | mean Δ leakage vs L0 | mean Δ predictive utility vs L0 | mean Δ do(N) invariance vs L0 | Degenerate | Developer candidate |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| L1 | 15/15 | +0.019717 | +0.025900 | -0.259663 | +0.073115 | `true` | `NOT_SUPPORTED` |
| L2 | 15/15 | +0.014343 | +0.094590 | -0.240252 | +0.062986 | `true` | `NOT_SUPPORTED` |
| L3 | 15/15 | +0.021214 | +0.025657 | -0.251078 | +0.072522 | `true` | `NOT_SUPPORTED` |
| L4 | 15/15 | +0.023407 | +0.025085 | -0.261193 | +0.072354 | `true` | `NOT_SUPPORTED` |

Global developer candidate:

`NOT_SUPPORTED`

Interpretation within the frozen H3 contract:

- all four candidates show higher mean `do(N)` invariance than L0;
- all four have worse mean task degradation than L0;
- all four have worse mean nuisance leakage than L0;
- all four lose substantial factual predictive utility relative to L0;
- therefore apparent representation invariance is accompanied by loss of useful task signal and is flagged `DEGENERATE`.

The `DEGENERATE` flag is evidence only; final H3 label remains within the frozen label set and is `NOT_SUPPORTED` for all four candidates.

## 7. Per-environment evidence

`h3_summary.json` and `H3_CLOSURE_REPORT.md` include learner × environment aggregates for:

- mean absolute `Delta_N`;
- `Leak_N`;
- factual predictive utility;
- mean `do(N)` invariance;
- ENV-4 shortcut-learning score;
- intervention failure count.

ENV-3 rows remain explicit with `0/5` complete seeds and `5/5` inapplicable seeds for every learner.

## 8. Verification

Focused H3 semantics tests:

`3 passed`

Relevant regression subset:

`45 passed`

Regression command covered:

- `tests/test_h3_closure.py`
- `tests/test_h2_closure.py`
- `tests/test_learner_contract.py`
- `tests/test_real_learners.py`

`python -m py_compile pipeline/run_h3_closure.py` also passed.

Pytest emitted the existing Windows cache ACL warning because `.pytest_cache` could not be created; tests themselves completed successfully.

## 9. Limitations / claim boundary

1. H3 evidence is limited to the tested synthetic environments and five frozen seeds.
2. ENV-3 cannot supply decisive H3 task-preserving nuisance evidence under its existing frozen `do(N)` implementation because the intervention changes the task target/labels.
3. L3 remains an IRM-style surrogate; L1, L2 and L4 retain adapted fidelity labels.
4. The result does not establish that nuisance invariance is unnecessary or sufficient in general.
5. The result does not generalize to canonical MLP/VAE/IRM/DANN implementations outside the frozen benchmark.
6. This closure does not answer Q-H2.1 beyond showing that higher representation invariance without retained task signal is insufficient under these tested conditions.
7. H4 was not started and MindForge integration was not performed.
8. `PLAN.md` was not updated by this task; PM owns H3 status closure.

## 10. Developer self-check

1. [x] H3 execution identity frozen before decisive matrix.
2. [x] L0 retained as frozen primary baseline.
3. [x] Learner definitions/hyperparameters unchanged.
4. [x] Seeds unchanged.
5. [x] ENV-1/2/4 pair semantics verified task-preserving.
6. [x] ENV-3 invalid task-preserving semantics retained as inapplicable evidence.
7. [x] Same factual rows/labels/intervention values verified between baseline and candidate smoke pair.
8. [x] `Delta_N`, leakage, `do_N_response`, predictive utility and ENV-4 shortcut diagnostics recorded.
9. [x] Failed/null/inapplicable evidence retained; no seed replacement or silent retry.
10. [x] 75 complete / 0 failed / 25 inapplicable learner cells.
11. [x] 60/60 comparable candidate-vs-L0 pairs available.
12. [x] All four candidates flagged `DEGENERATE` and classified `NOT_SUPPORTED` as developer candidates.
13. [x] Focused tests and relevant regression subset passed.
14. [x] No H1/H2 artifact altered.
15. [x] No H4 start, no MindForge integration, no H3 `PLAN.md` status update.

Status: `READY_FOR_QA_REVIEW`
