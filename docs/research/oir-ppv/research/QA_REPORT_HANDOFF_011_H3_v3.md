# QA_REPORT_HANDOFF_011_H3_v3 - Independent QA Re-Review

## Scope

Independent QA re-review of the `correction_v3` successor package described by
`HANDOFF_011_H3_v3.md`, using `qa-core`, `qa-research`, and `qa-software`.

Primary sources reviewed:

- `tasks/DEV_TASK_011_FIX_01.md`;
- `QA_REPORT_HANDOFF_011_H3.md`;
- `HANDOFF_011_H3_v2.md`;
- `HANDOFF_011_H3_v3.md`;
- `pipeline/run_h3_correction_v3.py`;
- `tests/test_h3_correction_v3.py`;
- H3 v1, correction v2, and correction v3 evidence packages.

QA did not change H3 source, protocol, learner definitions, matrix, seeds,
scientific evidence, `PLAN.md`, or H4 state. QA test replay created only separate
project-local pytest temporary directories.

## Overall QA Verdict

`PASS_WITH_LIMITS`

- Software and regression replay: `PASS`.
- Frozen source/runtime/protocol identity: `PASS`.
- v1 preservation: `PASS`.
- Matrix and one-attempt evidence: `PASS`.
- Causal-isolation evidence: `PASS`.
- v1/v3 scientific reconciliation: `PASS`.
- Report and claim boundary: `PASS_WITH_LIMITS`.
- `DEV_TASK_011_FIX_01`: `PASS_WITH_LIMITS`.
- H3 closure readiness: `PASS_WITH_LIMITS`.
- Scientific H3 classification: `NOT_SUPPORTED`.

No P0 or P1 blocker remains. PM may close H3 with the claim boundary and metadata
limitations in this report. A new H3 matrix run is neither required nor justified
to address the remaining metadata issue.

## Source of Truth / Frozen Identity

- Branch: `oir-ppv-research`
- HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- Working tree: dirty and recorded
- Handoff SHA256:
  `d837112092ddafe0393772133b118ab1888d63de555725330966ab85ef59fea9`
- v1 preservation manifest SHA256:
  `f7aa648559e66ec2d884406b960aff511d73af042af9e7c49d6a59402f8ddfeb`
- v3 source manifest SHA256:
  `af52a6cebdf18e7032fb9ca5fa0255bbb400cc2a46af8069bf0ae8ea134142d4`
- v3 runtime manifest SHA256:
  `7f4183f4c49777057469d9c6a5a289c047723ee753a772ec30c5f05bf03b2d74`
- v3 execution manifest SHA256:
  `666f007c18df39fd27b6d9ffe42d691b3db18281aee9a053ff7c92b97caa969a`
- M3 protocol SHA256:
  `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- EXP-LRN-001 manifest SHA256:
  `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H3 v1 execution manifest SHA256:
  `045da7b6b9b1ac0cb0045d72e0166d22f71839c895928ca9d129396ce72c5aad`

The stored v3 execution-manifest hash matches the current manifest. The runtime
drift guard was independently invoked by QA and returned
`FROZEN_IDENTITY_PASS`.

The source ordering is valid:

```text
run_h3_correction_v3.py last modified  2026-09-09 04:23:28 UTC
source/execution freeze created        2026-09-09 04:28:16 UTC
matrix completed                       2026-09-09 04:30:08 UTC
report/reconciliation completed        2026-09-09 04:30:40 UTC
```

This closes the prior P1 issue where the H3 runner was modified after the v1
matrix without an execution-time source hash.

## v2 Failure Preservation and v3 Retry Identity

Correction v2 remains preserved as:

`CORRECTION_FREEZE_INVALIDATED`

Its source, runtime, and execution manifests still match the hashes recorded in
`HANDOFF_011_H3_v2.md`:

- source: `8edf260aafa71524181dcdc31bea8d892fc6aa6d32d8a74358e60c3f39361f72`;
- runtime: `5c7d9d9fbb4aa1ccf4e5e71db095cc87d286a3538e4f928cf4a0d2dbd6e69f9b`;
- execution: `4c4ea8d57234966760358bc5edf5b7bcf001c1e7a280617716873a2cd395dfa0`.

V3 uses new source, runtime, execution, artifact, and report identities. The
v2-to-v3 source diff is limited to namespace/version substitutions and the
report-generation change that enumerates exact environment/seed intervention
triplets. V3 is therefore a new correction identity rather than a hidden retry
under the invalidated v2 freeze.

## Independent Provenance Audit

QA independently verified:

- v1 preservation inventory: 208 files;
- v1 preservation mismatches: 0;
- v1 paired evidence: 100/100;
- v1 effective configs: 100/100;
- v3 source/config manifest: 120 files;
- current source/config hash mismatches: 0;
- learner identity rows: 5/5;
- v3 manifest/runtime/source hashes in all 100 cells: 100/100 valid;
- cell config and effective-config hashes: 100/100 valid;
- v2 frozen manifest spot checks: 3/3 valid.

The source manifest includes the correction runner/tests, v1 runner/tests, M3
runner, causal and dependency analysis, learner modules, environment generators,
M3 protocol, EXP-LRN-001 manifest, all 100 learner configs, and all four base
environment configs.

Reproducibility classification: `REPRODUCIBLE_WITH_RECORDED_ENVIRONMENT`.

## Matrix / One-Attempt Audit

The v3 full evidence contains exactly the frozen grid:

```text
5 learners x 4 environments x 5 seeds = 100 cells
```

Independent counts:

- complete: 75;
- failed: 0;
- inapplicable: 25, all ENV-3;
- missing cells: 0;
- extra cells: 0.

The execution log contains 102 `cell_attempt` records: two expected smoke-cell
attempts followed by 100 full-matrix attempts. After the smoke marker, QA found
100 matrix attempts, 100 unique cell IDs, and zero duplicates. This supports the
claim that no full-matrix cell was retried or substituted.

## Causal-Isolation Audit

Every eligible cell contains three intervention records:

```text
75 eligible cells x 3 interventions = 225 intervention records
```

QA verified all 225 records satisfy:

```text
task_state_same == true
context_same == true
labels_same == true
target_nuisance_changed == true
non_target_nuisance_same == true
observations_changed == true
```

For all 25 ENV-3 cells and 75 ENV-3 intervention records, task state and context
remain unchanged while labels change and `task_preserving == false`. ENV-3 is
therefore correctly retained as `inapplicable` rather than imputed or repaired.

For the 60 candidate-vs-L0 eligible pairs, QA checked identical:

- factual observations;
- labels;
- task state;
- context;
- full nuisance state;
- selected target nuisance;
- non-target nuisance;
- intervention target and values.

Pair identity mismatches: 0.

This closes the prior missing matrix-level state/context evidence blocker.

## Scientific Reconciliation

QA independently projected every v3 cell onto the v1 scientific schema, excluding
only additive provenance and causal-isolation fields.

Results:

- compared cells: 100/100;
- compared scientific encoding bytes: 203118;
- exact-match encoding bytes: 203118;
- cell-level scientific mismatches: 0;
- v1 aggregate scientific fields: exact match;
- reconciliation status: `EXACT_MATCH`.

V3 adds wins/losses/ties fields to comparison rows. These are additive reporting
fields; all comparison fields inherited from v1 remain exact.

The independently confirmed candidate values are unchanged:

| Learner | Mean delta task degradation | Mean delta leakage | Mean delta utility | Candidate |
| --- | ---: | ---: | ---: | --- |
| L1 | +0.019717 | +0.025900 | -0.259663 | `NOT_SUPPORTED` |
| L2 | +0.014343 | +0.094590 | -0.240252 | `NOT_SUPPORTED` |
| L3 | +0.021214 | +0.025657 | -0.251078 | `NOT_SUPPORTED` |
| L4 | +0.023407 | +0.025085 | -0.261193 | `NOT_SUPPORTED` |

## Report Audit

`H3_CLOSURE_REPORT_v3.md` contains:

- 20/20 environment x seed intervention-coverage rows;
- exact selected target and three values for each row;
- 100/100 learner/environment/seed evidence rows;
- task-degradation, leakage, and utility wins/losses/ties;
- frozen provenance hashes and exact commands;
- runtime/dependency versions;
- learner fidelity labels;
- ENV-3 inapplicability;
- target-specific claim boundary;
- `SCALE_SENSITIVE_DIAGNOSTIC_ONLY` qualification;
- non-causal interpretation of `DEGENERATE`;
- adapted dependency-probe limitation.

The v2 report omission is closed.

## Test Replay

QA ran:

```text
python -c "from pipeline import run_h3_correction_v3 as v3; v3._verify_frozen_identity(); print('FROZEN_IDENTITY_PASS')"
python -m py_compile pipeline/run_h3_closure.py pipeline/run_h3_correction_v3.py
python -m pytest tests/test_h3_correction_v3.py -q -p no:cacheprovider --basetemp artifacts/qa_h3_v3_focused_20260909_retry
python -m pytest tests/test_h3_closure.py tests/test_h2_closure.py tests/test_learner_contract.py tests/test_real_learners.py tests/test_h3_correction_v3.py -q -p no:cacheprovider --basetemp artifacts/qa_h3_v3_regression_20260909_retry
```

Observed results:

- frozen identity: PASS;
- compile: PASS;
- focused correction tests: `14 passed`;
- required regression subset: `59 passed`.

The known Windows pytest ACL problem did not recur with new project-local
`--basetemp` directories.

## Acceptance Matrix

| Criterion | QA result |
| --- | --- |
| Preserve all v1 H3 evidence | PASS |
| Preserve invalidated v2 evidence | PASS |
| New v3 identity frozen before replay | PASS |
| Source/runtime/config/protocol drift guard | PASS |
| One full-matrix attempt per cell | PASS |
| 100 explicit cells and frozen counts | PASS |
| 60/60 full candidate-vs-L0 pair identity | PASS |
| Matrix-level causal-isolation evidence | PASS |
| ENV-3 remains explicit inapplicable evidence | PASS |
| v1/v3 scientific reconciliation | PASS |
| Aggregate candidate labels recomputed | PASS |
| Exact target/value report coverage | PASS |
| Scale-sensitive diagnostic qualification | PASS |
| Focused and regression tests | PASS |
| H1/H2 unchanged | PASS |
| `PLAN.md` remains PM-controlled | PASS |
| H4 and MindForge remain unopened | PASS |
| Embedded v3 summary version metadata | PASS_WITH_LIMITS |

## Findings

### P0

None.

### P1

None. The two blocking classes from `QA_REPORT_HANDOFF_011_H3.md` are closed.

### P2

1. `h3_summary_v3.json` contains the embedded field `"version": 2`, inherited
   from `_compute_summary()` in `run_h3_correction_v3.py`, despite belonging to
   the v3 namespace. The artifact path, filename, source/runtime/execution hashes,
   and cell provenance all identify correction v3 correctly, so this does not
   alter or ambiguate the scientific values reviewed here. PM should preserve a
   metadata erratum when archiving H3 and must not overwrite the frozen v3
   summary merely to correct this field.

### P3

1. The report provides all 100 per-seed rows and the machine-readable summary
   contains all 20 learner x environment aggregates, but the Markdown report does
   not repeat a dedicated learner x environment aggregate table. This is a
   presentation limitation, not missing evidence.

## Scientific Assessment

All L1-L4 configurations fail the frozen H3 success rule relative to L0/PCA:

- mean absolute nuisance task degradation is worse;
- mean frozen leakage proxy is worse;
- factual predictive utility is lower.

Scientific H3 classification:

`NOT_SUPPORTED`

`DEGENERATE=true` is accepted only as an indicative co-occurrence flag. The raw
latent-shift diagnostic is scale-sensitive and does not establish a causal or
mechanistic explanation.

Defensible claim boundary:

> Under selected targets `background_noise` in ENV-1, `occlusion` in ENV-2, and
> `spurious_feature` in ENV-4, across seeds 42, 123, 456, 789, and 1011, the
> tested L1-L4 adapted/surrogate configurations do not improve the frozen paired
> H3 criteria over L0/PCA. ENV-3 is inapplicable because its `do(N)` changes `Y`
> and task labels.

This does not generalize to untested nuisance targets, canonical external learner
implementations, external environments, MindForge, or nuisance robustness in
general.

## PM Handoff

PM may record H3 as:

```text
H3: CLOSED_WITH_LIMITS / NOT_SUPPORTED
Evidence authority: correction_v3 accepted with metadata limits
```

The archived state must retain:

- invalidated v2 evidence;
- accepted v3 hashes;
- the embedded-summary-version erratum;
- exact target-specific claim boundary;
- scale-sensitive and adapted-probe limitations.

After PM records closure, the dependency order permits creation of a separately
scoped H4 closure task. This QA report does not itself update `PLAN.md` or start
H4.
