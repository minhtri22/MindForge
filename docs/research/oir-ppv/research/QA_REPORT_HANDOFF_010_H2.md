# QA_REPORT_HANDOFF_010_H2 - Independent QA Review

## Scope

Independent QA review of `DEV_TASK_010_H2_CLOSURE` and `HANDOFF_010_H2.md`
using `qa-core`, `qa-research`, and `qa-software`.

Reviewed evidence includes:

- `pipeline/run_h2_closure.py`
- `tests/test_h2_closure.py`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/h2_protocol_freeze.json`
- `experiments/OIR_PPV/H2_Closure/EXP-H2-001/matrix_manifest.json`
- 60 derived H2 pair artifacts and provenance records
- frozen `EXP-LRN-001` source cells
- H1 RAW control cells
- `h2_comparison.json`
- `H2_CLOSURE_REPORT.md`

QA did not modify H2 scientific evidence, protocol, matrix, learner behavior, or
`PLAN.md` hypothesis state.

## Source of Truth / Frozen Identity

- Branch: `oir-ppv-research`
- Base HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- Working tree: dirty, explicitly recorded in H2 provenance
- M3 protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H1 protocol SHA256: `8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`
- H2 protocol SHA256: `5d851da06b06b36e1c3272c2d7dc4b1ad8f7c360a4654803945b05e3cd84c661`
- H2 matrix SHA256: `ffd96baa9f342cbcc830f1eef04bc99aff8c6835ac97ed9bf2c21bc9a416616e`
- Primary baseline: `L0` PCA
- Treatments: `L1`, `L2`, `L3`, `L4`
- Eligible environments: `ENV-1`, `ENV-3`, `ENV-4`
- Seeds: `42, 123, 456, 789, 1011`
- Primary metric: `Delta_OOD = unseen_environment_score(learner) - unseen_environment_score(L0)`

## Protocol Integrity

PASS.

The H2 protocol freeze predates the matrix, pair derivation, and decisive
aggregate output. File timestamps independently observed by QA:

```text
run_h2_closure.py       2026-09-09 00:32:32
h2_protocol_freeze.json 2026-09-09 00:32:42
matrix_manifest.json    2026-09-09 00:32:44
derive_summary.json     2026-09-09 00:32:55
h2_comparison.json      2026-09-09 00:32:59
```

The analysis script SHA256 recorded in all 60 pair provenance records is:

`41a9c9b6197ade1fb8fecffb35c8c8374d7d5cbf9bf11716f0175c925aad2395`

It matches the script independently inspected by QA.

Frozen statistical rules were preserved:

- paired unit: same environment + same seed;
- bootstrap: 10,000 deterministic resamples;
- bootstrap seed: `20260909`;
- CI: 95% percentile interval of paired mean delta;
- tie tolerance: `1e-12`;
- catastrophic regression: `Delta_OOD < -0.20`;
- no seed replacement or result-dependent exclusion.

No protocol deviation or post-hoc threshold change was found.

## Evidence Integrity

PASS.

Independent QA audit found:

- primary pair grid: exactly 60 unique pairs;
- 60/60 pair artifacts complete;
- failed/missing primary pairs: 0;
- ENV-2 inapplicable pairs: 20/20 explicitly recorded;
- frozen EXP-LRN-001 ENV-2 unseen score: null for 25/25 L0-L4 source cells;
- RAW provenance-compatible comparisons: 60/60;
- source artifact hashes: 60/60 verified against current immutable source files;
- pair protocol/matrix/reference hashes: 60/60 verified;
- `Delta_OOD` and `Delta_OOD_vs_RAW`: 60/60 independently recomputed exactly;
- RAW OOD split and shift-assertion identity: 60/60 verified.

No imputation, seed replacement, silent pair drop, retraining, or accepted-source
overwrite was found.

## Independent Statistical Replay

QA recomputed the paired summaries and bootstrap intervals directly from the 60
source-backed pair deltas using the frozen statistical rule.

| Learner | W/L/T | Mean Delta_OOD | 95% CI | Catastrophic | QA scientific result |
|---|---:|---:|---:|---:|---|
| L1 | 3/12/0 | -0.306940 | [-0.469786, -0.139865] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L2 | 2/13/0 | -0.380514 | [-0.522771, -0.234823] | 9 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L3 | 3/12/0 | -0.300413 | [-0.461760, -0.135588] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| L4 | 3/11/1 | -0.298932 | [-0.460752, -0.134385] | 7 | `FALSIFIED_UNDER_TESTED_CONDITIONS` |

All four independently replayed results match `h2_comparison.json` exactly.
Every CI is entirely below zero, losses exceed wins, and substantial catastrophic
regressions remain visible.

## Test Replay

- `python -m py_compile pipeline/run_h2_closure.py`: PASS
- focused H2 suite: `11 passed`
- regression subset: `53 passed`

The previously reported Windows pytest temporary-directory ACL failure is an
environment issue and did not recur in the project-managed focused suite. It is
retained as environment evidence and does not alter the scientific result.

## Acceptance Matrix

| Criterion | QA result |
|---|---|
| H2 semantics frozen before decisive analysis | PASS |
| L0 remains primary frozen baseline | PASS |
| ENV-1/3/4 OOD semantics unchanged | PASS |
| ENV-2 explicit inapplicable / no imputation | PASS |
| Five frozen seeds retained | PASS |
| No learner retraining/tuning | PASS |
| EXP-LRN-001/H1 source evidence preserved | PASS |
| Derived evidence mode explicit | PASS |
| Source/protocol/matrix hashes verified | PASS |
| 60/60 primary pairs reconcile | PASS |
| RAW provenance compatibility | PASS |
| Paired CI and catastrophic rule replay | PASS |
| Negative/positive/null evidence retained | PASS |
| Focused and regression tests | PASS |
| H2 wording within tested scope | PASS |
| H3/MindForge remain unopened by this task | PASS |
| `PLAN.md` remains PM-controlled | PASS |

## Findings

### P0

None.

### P1

None.

### P2

None blocking H2 closure.

### P3 / archival note

The repository is intentionally in a dirty research worktree and H2 source is
identified by base Git SHA plus content hashes rather than a dedicated committed
H2 SHA. Current evidence is independently reproducible in this workspace, but PM
should preserve/commit the accepted H2 source and evidence as part of the normal
project freeze/archive step.

## Scientific Assessment

The frozen H2 operational prediction is not supported by any tested non-PCA
learner. Under the pre-frozen falsification rule, all four tested learners satisfy
the condition for `FALSIFIED_UNDER_TESTED_CONDITIONS` relative to L0/PCA.

Scientific classification:

`FALSIFIED_UNDER_TESTED_CONDITIONS`

Defensible claim boundary:

> Within frozen synthetic ENV-1, ENV-3, ENV-4 and seeds 42, 123, 456, 789,
> 1011, the tested L1 MLP, L2 VAE, L3 IRM-style surrogate, and L4 DANN
> representations do not improve paired unseen/OOD performance over the frozen
> L0/PCA reference. Each instead shows a statistically negative paired effect
> under the frozen H2 rule.

This conclusion does not generalize to invariant learning methods, canonical IRM,
DANN, VAE, MLP architectures, MindForge, or external environment families not
tested here.

## Overall QA Verdict

Software / evidence integrity: `PASS`.

`DEV_TASK_010_H2_CLOSURE`: `PASS`.

H2 closure readiness: `PASS`.

Scientific H2 classification: `FALSIFIED_UNDER_TESTED_CONDITIONS`.

QA found no P0/P1 blocker. PM may freeze H2 with the above claim boundary and,
under the approved closure order, promote the separately scoped H3 task.
