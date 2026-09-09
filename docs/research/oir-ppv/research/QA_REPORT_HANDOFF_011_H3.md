# QA_REPORT_HANDOFF_011_H3 - Independent QA Review

## Scope

Independent QA review of `DEV_TASK_011_H3_CLOSURE` and
`HANDOFF_011_H3.md` using `qa-core` and `qa-research`.

Reviewed evidence includes:

- `tasks/DEV_TASK_011_H3_CLOSURE.md`
- `H1_H4_CLOSURE_PLAN.md`
- `tasks/QA_TASK_001.md`
- `pipeline/run_h3_closure.py`
- `tests/test_h3_closure.py`
- `experiments/OIR_PPV/H3_Closure/EXP-H3-001/`
- `artifacts/h3_closure/EXP-H3-001/`
- the frozen `EXP-LRN-001` manifest and learner-cell configs

QA did not modify H3 source, paired evidence, matrix results, summary, report,
protocol, learner definitions, seeds, or `PLAN.md`. A direct semantic replay
regenerated four selected effective-config files byte-for-byte; their recorded
hashes remained unchanged.

## Source of Truth / Frozen Identity

- Branch: `oir-ppv-research`
- Base HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- Working tree: dirty
- Primary baseline: `L0` PCA
- Candidates: `L1`, `L2`, `L3`, `L4`
- Environments: `ENV-1..ENV-4`
- Seeds: `42, 123, 456, 789, 1011`
- M3 protocol SHA256:
  `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256:
  `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H3 execution manifest SHA256:
  `045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad`
- Current runner SHA256:
  `2e96c65fd158c03cbe114391cc41a039e426a0659d1e4f1f41593d053f733f4c`
- Current focused-test SHA256:
  `3047e18bb09366b8ab8e4b0c1799329fb0904f95ebecb8e78eac93f8222d9e0f`

## Independent Evidence Audit

QA independently parsed all full-matrix cell artifacts and found:

- exactly 100 unique learner/environment/seed cells;
- 75 `complete`, 0 `failed`, and 25 `inapplicable`;
- all 25 `inapplicable` cells are ENV-3;
- all 60 candidate-vs-L0 pairs on ENV-1, ENV-2, and ENV-4 have identical
  factual-observation hashes, label hashes, nuisance targets, and intervention
  values;
- 100/100 config and effective-config hashes match current files;
- 100/100 cell manifest/protocol/reference hashes reconcile;
- all four aggregate comparison vectors recompute exactly from paired evidence;
- handoff hashes for smoke, summary, and report match current files.

Recomputed comparison results:

| Learner | mean delta task degradation | mean delta leakage | mean delta utility | mean delta do(N) invariance | QA metric result |
| --- | ---: | ---: | ---: | ---: | --- |
| L1 | +0.019717 | +0.025900 | -0.259663 | +0.073115 | `NOT_SUPPORTED` |
| L2 | +0.014343 | +0.094590 | -0.240252 | +0.062986 | `NOT_SUPPORTED` |
| L3 | +0.021214 | +0.025657 | -0.251078 | +0.072522 | `NOT_SUPPORTED` |
| L4 | +0.023407 | +0.025085 | -0.261193 | +0.072354 | `NOT_SUPPORTED` |

The H3 result does not depend on the representation-invariance diagnostic:
every candidate already fails the frozen task-degradation and leakage conditions,
and factual predictive utility is lower on average.

## Causal / Intervention Semantics

Direct QA replay of seed 42 verified the implementation behavior:

| Environment | Selected target | State unchanged | Context unchanged | Labels unchanged | Nuisance changed | H3 eligibility |
| --- | --- | --- | --- | --- | --- | --- |
| ENV-1 | `background_noise` | yes | yes | yes | yes | eligible |
| ENV-2 | `occlusion` | yes | yes | yes | yes | eligible |
| ENV-3 | `do(N)` | yes | yes | no | yes | inapplicable |
| ENV-4 | `spurious_feature` | yes | yes | yes | yes | eligible |

ENV-3 is correctly excluded from the primary H3 comparison because its variable
`N` enters the structural equation for `Y`; intervening on it changes the task
target and labels.

The frozen artifacts, however, record only factual-observation and label hashes.
They do not record factual/intervened state hashes, context hashes, or the
non-target nuisance hashes. The focused test also checks label preservation but
does not assert state/context identity. Therefore the required nuisance-only
isolation is confirmed by current-code inspection and one QA replay, but is not
fully preserved as matrix-level frozen evidence.

## Protocol Integrity

The H3 manifest predates the decisive matrix and freezes learners, environments,
seeds, baseline, pairing rule, metrics, failure policy, and closure rule. No
missing or failing cell was removed or replaced.

The aggregation uses the pre-run frozen paired mean rule. QA found no arithmetic
drift, seed substitution, imputation, or post-hoc label change.

Two interpretation limits must be retained:

1. Only one nuisance target is intervened in each eligible environment. ENV-1
   does not test `lighting`, ENV-2 does not test `texture_noise`, and ENV-4 does
   not test `background_color` or `rotation`.
2. `mean_shift = mean(abs(I_factual - I_intervened))` is not normalized across
   learner-specific latent scales. Its cross-learner delta cannot independently
   establish that L1-L4 are more invariant than L0. It may be retained as the
   frozen diagnostic, but the `DEGENERATE` interpretation is indicative rather
   than a scale-controlled causal result.

The frozen dependency probe is also an adapted sensitivity score. Its
`predictability_r2` component predicts `I` from `N`, while the theory notation is
`predictive_information(N | I)`. This pre-existing frozen-probe limitation does
not reverse the current negative H3 result, but it prevents interpreting
`Leak_N` as a canonical nuisance classifier without qualification.

## Provenance Finding

The decisive H3 package does not satisfy the project provenance contract.

`pipeline/run_h3_closure.py` and `tests/test_h3_closure.py` are untracked, so the
recorded Git HEAD does not identify them. The H3 manifest and cell provenance do
not contain:

- runner/analysis-script SHA256;
- environment and learner implementation hashes;
- exact execution commands;
- Python/runtime and dependency versions;
- a hash manifest for all raw and derived H3 artifacts.

Observed local timestamps add material ambiguity:

```text
h3_execution_manifest.json  2026-09-09 01:23:17 +07
matrix_execution.json       2026-09-09 01:26:09 +07
run_h3_closure.py           2026-09-09 01:28:11 +07
h3_summary.json             2026-09-09 01:28:21 +07
```

The current runner was modified after the matrix completed. Without a runner
hash captured at matrix execution or a versioned deterministic replay, QA cannot
prove that the current source is byte-identical to the source that generated the
75 complete and 25 inapplicable cells.

This is a P1 reproducibility blocker for final H3 freeze. It does not show that
the reported metrics are wrong; it breaks the immutable trace from source to
decisive evidence.

## Test Replay

QA replayed:

```text
python -m py_compile pipeline/run_h3_closure.py
python -m pytest tests/test_h3_closure.py -q -p no:cacheprovider --basetemp artifacts/qa_h3_tmp_focused_20260909_retry
python -m pytest tests/test_h3_closure.py tests/test_h2_closure.py tests/test_learner_contract.py tests/test_real_learners.py -q -p no:cacheprovider --basetemp artifacts/qa_h3_tmp_regression_20260909_retry
```

Results:

- syntax compile: PASS;
- focused H3 tests: `3 passed`;
- regression subset: `45 passed`.

The Windows `tmp_path` ACL problem did not recur with an explicit project-local
`--basetemp`.

## Acceptance Matrix

| Criterion | QA result |
| --- | --- |
| Correct branch and frozen upstream identities | PASS |
| Frozen 5 x 4 x 5 matrix and seed list | PASS |
| 100/100 cell presence and status accounting | PASS |
| 60/60 candidate-vs-L0 pair identity | PASS |
| ENV-3 retained as explicit inapplicable evidence | PASS |
| Aggregate arithmetic and candidate labels | PASS |
| No seed replacement, imputation, or silent cell drop | PASS |
| Current code preserves state/context in QA smoke | PASS |
| Matrix-level frozen state/context isolation evidence | PARTIAL |
| Exact source/runtime/command provenance | FAIL |
| Cross-learner latent-shift interpretation | PARTIAL |
| Focused and regression replay | PASS |
| Claim boundary names exact nuisance targets | PARTIAL |
| H4/MindForge remain unopened | PASS |
| `PLAN.md` remains PM-controlled for H3 closure | PASS |

## Findings

### P0

None.

### P1

1. The decisive matrix is not tied to a frozen runner/source/runtime identity.
   The runner is untracked, lacks an execution-time hash, and was modified after
   matrix completion. Final H3 acceptance is blocked until a versioned correction
   establishes that trace without overwriting the existing evidence.

### P2

1. Frozen pair evidence does not preserve state/context/non-target-nuisance hashes,
   and focused tests assert labels rather than the full nuisance-only invariant.
2. Cross-learner raw latent mean-shift is scale-confounded. The current aggregate
   `DEGENERATE` flag is useful as a warning, but not as a scale-controlled causal
   finding.
3. The report does not name the single selected nuisance target per environment,
   which makes its claim boundary broader than the executed interventions.
4. The frozen dependency probe is an adapted sensitivity metric rather than a
   direct canonical estimator of `predictive_information(N | I)`.

### P3

1. `HANDOFF_011_H3.md` states test counts but does not preserve the exact original
   pytest commands or runtime/dependency inventory.

## Required Correction Gate

Before PM closes H3, a separately scoped `DEV_TASK_011_FIX_01` should:

1. preserve and hash every current H3 v1 artifact before any correction;
2. create a versioned correction namespace rather than overwrite v1;
3. freeze runner, test, environment, learner, protocol, config, command, runtime,
   and dependency identities;
4. perform a deterministic source-backed replay into the correction namespace
   and compare every scientific field with v1, retaining all mismatches;
5. add state/context/target-nuisance/non-target-nuisance hashes to paired evidence
   and tests across all eligible environments and frozen seeds;
6. name the exact intervention target/value coverage in the corrected report;
7. retain raw latent shift only as a scale-sensitive diagnostic and qualify the
   `DEGENERATE` flag accordingly;
8. leave H1/H2, `PLAN.md`, H4, and MindForge unchanged.

## Scientific Assessment

The existing paired artifacts consistently show that none of L1-L4 meets the
frozen H3 success rule relative to L0/PCA. Each candidate has worse mean absolute
task degradation, worse mean leakage, and lower mean factual utility over the 15
eligible environment/seed pairs.

Metric-level scientific direction: `NOT_SUPPORTED`.

Defensible current claim boundary:

> Under the selected nuisance targets `background_noise` in ENV-1, `occlusion`
> in ENV-2, and `spurious_feature` in ENV-4, across seeds 42, 123, 456, 789, and
> 1011, the tested L1-L4 configurations do not improve the frozen paired H3
> criteria over L0/PCA. ENV-3 is inapplicable because its `do(N)` changes `Y` and
> task labels.

This does not generalize to untested nuisance targets, canonical external
implementations of MLP/VAE/IRM/DANN, external environment families, MindForge,
or nuisance robustness in general.

## Overall QA Verdict

Software/test replay: `PASS`.

Artifact arithmetic and matrix completeness: `PASS`.

`DEV_TASK_011_H3_CLOSURE`: `PARTIAL`.

H3 closure readiness: `BLOCKED`.

Scientific direction from current artifacts: `NOT_SUPPORTED`.

PM must not close H3 or open H4 until the P1 provenance blocker is corrected and
independently re-reviewed. The correction must preserve the current negative
evidence and must not change the frozen H3 thresholds, learners, environments,
seeds, or primary comparison rule.
