# QA Report - HANDOFF_007_v5

## Scope

- Project: OIR-PPV Controlled Causal Benchmark
- Reviewed handoff: `HANDOFF_007_v5.md`
- Task under acceptance: `DEV_TASK_008_FIX_04.md`
- Branch: `research/pit`
- Candidate/executed SHA: `f7e446d64d1c040cd168ae859d04503509cfe8ec`
- Skills applied: `qa-core`, `qa-research`, `qa-software`
- Date: 2026-09-08

## Source of Truth

1. `benchmark/M3_PROTOCOL.md`
2. `tasks/DEV_TASK_008_FIX_04.md`
3. `HANDOFF_007_v5.md`
4. Fresh evidence under `artifacts/stress_test/m4_fix04/`

Frozen protocol identity independently verified:

- Version: `M3-Protocol-v1.0`
- SHA-256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`

## Independent QA Replay

Fresh QA execution produced:

- `tests/test_m4_fix04.py`: **6/6 PASS**
- full regression suite: **51/51 PASS**
- Windows CP1252 M2 CLI: **exit 0 / PASS**
- accepted source HEAD: `f7e446d64d1c040cd168ae859d04503509cfe8ec`
- relevant source paths clean at review time
- eight accepted stress artifact sets match expected HEAD and frozen protocol
- stress reproducibility: **4/4 scenarios PASS**
- artifact audit: `all_passed=true`

Independent Windows CLI evidence:

- `artifacts/qa_review/handoff_007_v5/m2_cli_output.txt`
- `artifacts/qa_review/handoff_007_v5/m2_cli/QA-V5-M2-CP1252/result.json`

## Acceptance Matrix

| # | Criterion | Independent observation | Verdict |
| ---: | --- | --- | --- |
| 1 | Frozen `< 0.5` causal failure semantics | Focused FIX_04 tests pass | PASS |
| 2 | Threshold and boundary tests | Included in 6/6 FIX_04 suite | PASS |
| 3 | Windows M2 CLI compatibility | Fresh CP1252 execution exits 0 | PASS |
| 4 | M2/M3/M4 regression | 51/51 PASS | PASS |
| 5 | Exact source traceability | HEAD and relevant source snapshot verified | PASS |
| 6 | Protocol identity in accepted runs | 8/8 artifact sets match frozen protocol | PASS |
| 7 | Protocol mismatch fail-fast | FIX_04 regression suite PASS | PASS |
| 8 | Four stress preflight assertions | Saved evidence + audit PASS | PASS |
| 9 | Four scenarios x two seed-42 repeats | `reproducibility_report.json`: 4/4 PASS | PASS |
| 10 | Runtime/source/config provenance | Verified across accepted provenance artifacts | PASS |
| 11 | Finite compact JSON / external arrays | Artifact audit PASS | PASS |
| 12 | Handoff traceability and limitations | v5 maps all criteria and retains negative findings | PASS |

## Findings

### P0

None.

### P1

None.

### Non-blocking research findings

The software/protocol closure does not establish robust invariant learning:

- context leakage remains detected in all four run-A stress scenarios;
- nuisance leakage remains detected in three of four scenarios;
- context stress retains `generalization_delta = -0.8304818308108504`;
- the retained FIX_03 comparison has trained predictive accuracy `0.848`, below PCA placeholder `0.984`.

Scientific conclusion: `NOT_SUPPORTED` for robust invariant/generalization quality under the currently tested learner.

## Overall QA Verdict

`PASS`

`DEV_TASK_008_FIX_04.md` is accepted as a software/protocol/reproducibility closure task.

This acceptance unblocks `DEV_TASK_008_1.md`. It does not authorize a claim that OIR-PPV has already demonstrated robust invariant learning.
