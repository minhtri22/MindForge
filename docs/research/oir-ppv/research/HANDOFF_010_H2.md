# HANDOFF_010_H2 - H2 Paired OOD Transfer Closure

## 1. Implementation / analysis summary

Implemented `DEV_TASK_010_H2_CLOSURE` as a **derived paired analysis** over accepted immutable `EXP-LRN-001` evidence. No learner was retrained and no accepted EXP-LRN-001 or H1 artifact was overwritten.

H2 operational semantics were frozen before decisive classification:

- primary baseline: `L0` PCA;
- treatments: `L1..L4`;
- eligible OOD environments: `ENV-1`, `ENV-3`, `ENV-4`;
- seeds: `42, 123, 456, 789, 1011`;
- primary pair: same environment + same seed + learner vs L0;
- primary metric: `Delta_OOD = unseen_environment_score(learner) - unseen_environment_score(L0)`;
- deterministic paired bootstrap CI of mean delta, 10,000 repetitions, seed `20260909`, 95% percentile interval;
- tie tolerance: `1e-12`;
- catastrophic regression: `Delta_OOD < -0.20`.

`ENV-2` is explicitly `INAPPLICABLE_FOR_H2_PRIMARY` because the frozen benchmark has null `unseen_environment_score`; no value was imputed.

RAW is retained only as secondary control. Its comparison requires reference-manifest identity, same environment/seed, same OOD split name, and exact shift-assertion identity. All 60 eligible treatment pairs had provenance-compatible RAW control evidence.

## 2. Changed files

Source/tests:

- `pipeline/run_h2_closure.py`
- `tests/test_h2_closure.py`

Frozen H2 protocol/matrix:

- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/h2_protocol_freeze.json`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/h2_protocol_freeze.sha256`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/matrix_manifest.json`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/matrix_manifest.sha256`

Derived evidence/reporting:

- `artifacts/h2_closure/EXP-H2-001/pairs/*/pair_result.json`
- `artifacts/h2_closure/EXP-H2-001/pairs/*/provenance.json`
- `artifacts/h2_closure/EXP-H2-001/derive_summary.json`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/h2_comparison.json`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/H2_CLOSURE_REPORT.md`

This task did not update H2 state in `PLAN.md` and did not start H3 or MindForge integration.

## 3. Git / source provenance

Branch:

`oir-ppv-research`

Current HEAD:

`0521c5754a32e2625930de75fe2635c6ce5ec9a0`

Working tree is dirty and contained substantial pre-existing research/coordination state before H2. H2 provenance records current branch/SHA/dirty state separately from the historical EXP-LRN-001 source provenance.

Frozen identities:

- M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H2 protocol freeze SHA256: `5d851da06b06b36e1c3272c2d7dc4b1ad8f7c360a4654803945b05e3cd84c661`
- H2 matrix manifest SHA256: `ffd96baa9f342cbcc830f1eef04bc99aff8c6835ac97ed9bf2c21bc9a416616e`

Derived-output hashes:

- `h2_comparison.json`: `d8aa2a8bd035a73f0c9be32c877ebace9b88b4b11ee1ed6b311ef942ddfa098e`
- `H2_CLOSURE_REPORT.md`: `6a9e265de65f995d4a57ab3ceb43886abb5cc59e4ccc6e872b830cacd6b075bc`
- `derive_summary.json`: `097f59f724be90f7ee882dbdd49fc5f50de8a688ae21942ea08c840db779145e`

## 4. Exact commands

```powershell
python -m py_compile pipeline/run_h2_closure.py
python -m pipeline.run_h2_closure freeze-protocol
python -m pipeline.run_h2_closure freeze-matrix
python -m pipeline.run_h2_closure derive
python -m pipeline.run_h2_closure aggregate
python -m pytest tests/test_h2_closure.py -q -p no:cacheprovider
python -m pytest tests/test_learner_contract.py tests/test_real_learners.py tests/test_benchmark_m2.py tests/test_pipeline.py -q -p no:cacheprovider
```

An initial H2 focused-test run executed 10 tests successfully but one `tmp_path`-based test failed during fixture setup with Windows `PermissionError` under the user temp directory. This was recorded as environment evidence, not a scientific/software assertion. The test was moved to a project-managed temporary path and the complete focused suite then passed.

## 5. Runtime / dependencies

- Windows 11 / PowerShell
- Python `3.13.12`
- NumPy version is recorded in every H2 pair provenance alongside platform identity.
- Source EXP-LRN-001 per-cell provenance retains its original Python/NumPy/scikit-learn/SciPy/PyTorch versions.

Evidence mode:

`derived`

No new learner training was executed for H2.

## 6. Artifact paths, counts, and scientific candidate

Primary matrix:

- expected treatment pairs: `60`
- completed treatment pairs: `60`
- failed/missing treatment pairs: `0`
- ENV-2 inapplicable treatment pairs recorded in manifest: `20`
- RAW comparable pairs: `60/60`

Per-learner frozen paired results vs L0:

| Learner | Fidelity | W/L/T | Mean Delta_OOD | 95% bootstrap CI | Catastrophic | Developer candidate |
|---|---|---|---:|---|---:|---|
| L1 | adapted | 3/12/0 | -0.306940 | [-0.469786, -0.139865] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L2 | adapted | 2/13/0 | -0.380514 | [-0.522771, -0.234823] | 9 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L3 | surrogate | 3/12/0 | -0.300413 | [-0.461760, -0.135588] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L4 | adapted | 3/11/1 | -0.298932 | [-0.460752, -0.134385] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |

All four learner CIs are entirely below zero and losses dominate wins. Catastrophic regressions are retained explicitly and are not averaged away.

Global developer candidate:

`FALSIFIED_UNDER_TESTED_CONDITIONS`

Authority for every label:

`DEVELOPER_CANDIDATE_ONLY`

QA/PM owns final H2 acceptance and any `PLAN.md` change.

## 7. Known limitations / failed / inapplicable evidence

1. H2 is limited to the controlled synthetic benchmark and only ENV-1, ENV-3, ENV-4 plus the five frozen seeds.
2. ENV-2 is scientifically inapplicable to the primary H2 metric because accepted evidence contains no unseen score. It remains null and is never imputed.
3. L3 is an IRM-style surrogate, not canonical IRM. L1, L2, and L4 retain adapted fidelity labels.
4. RAW is only a secondary control; it does not replace L0 as the frozen H2 reference.
5. Positive ENV-3 cells exist for some learners and are preserved. They do not offset the globally negative paired effect under the pre-frozen classification rule.
6. Catastrophic regressions are substantial: L1=7, L2=9, L3=7, L4=7 of 15 pairs.
7. No result establishes a universal statement about invariant learning, IRM, DANN, VAE, or MLP architectures outside the tested implementations/environment families.
8. The initial focused-test run hit the known Windows pytest temp ACL blocker; after removing dependency on `tmp_path`, focused H2 tests executed completely and passed.

## 8. Developer self-check

1. [x] H2 protocol semantics frozen before decisive classification.
2. [x] L0 remains the primary frozen baseline.
3. [x] ENV-1/3/4 OOD semantics unchanged and read directly from accepted evidence.
4. [x] ENV-2 explicitly inapplicable; no imputation.
5. [x] Five frozen seeds retained with same-seed/same-environment pair identity.
6. [x] No learner objective, architecture, hyperparameter, environment, or split changed.
7. [x] EXP-LRN-001 and H1 evidence read-only; H2 artifacts are new derived evidence.
8. [x] Evidence mode explicitly `derived`; no learner rerun.
9. [x] Every pair carries protocol/matrix/reference hashes and source artifact hashes/provenance.
10. [x] Aggregate includes per-seed evidence, per-environment summaries, deterministic paired CI, mean/median/std/min/max.
11. [x] Catastrophic regressions listed by exact pair and included in classification logic.
12. [x] Negative/null/positive results retained without seed replacement or silent drop.
13. [x] Focused H2 tests: `11 passed`; regression subset: `53 passed`. Initial Windows temp ACL setup error is separately documented.
14. [x] Candidate wording is restricted to tested OOD scope and marked `DEVELOPER_CANDIDATE_ONLY`.
15. [x] H2 state remains PM-controlled; this task did not update `PLAN.md`.
16. [x] H3 not started; MindForge not integrated.

Status: `READY_FOR_QA_REVIEW`

