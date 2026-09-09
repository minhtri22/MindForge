# OIR-PPV M4 Handoff 007 v5

## Status

`READY FOR PM/QA RE-REVIEW`

This handoff closes the implementation scope of `DEV_TASK_008_FIX_04.md`.
It supersedes `HANDOFF_007_v4.md` for M4 protocol-compliance evidence.

`DEV_TASK_008_1.md` remains **BLOCKED** until independent PM/QA accepts this
handoff and explicitly closes M4.

## 1. Scope closed by FIX_04

FIX_04 addressed the four QA blockers only:

1. Causal `failure_cases` now use the frozen `< 0.5` threshold for both
   nuisance and context interventions.
2. The M2 benchmark CLI no longer emits Unicode status glyphs that fail on a
   default Windows CP1252 console.
3. The OIR-PPV M4 code/config/protocol snapshot is now traceable to Git.
4. Every accepted M4 stress run records and validates the frozen
   `M3-Protocol-v1.0` identity, path, and SHA-256.

No learner-quality claim is upgraded by this closure.

## 2. Implementation changes

### Causal threshold compliance

- `pipeline/causal_validation.py`
  - defines `FAILURE_THRESHOLD = 0.5`;
  - uses the same threshold for nuisance and context failure collection.
- `tests/test_m4_fix04.py`
  - proves context score `0.49` is recorded as a failure;
  - proves boundary score `0.5` is not recorded as a failure.

### Windows M2 CLI compatibility

- `benchmark/run_benchmark.py`
  - replaces Unicode success/failure glyphs with ASCII `PASS` / `FAIL` output;
  - preserves command exit-code behavior.
- `tests/test_m4_fix04.py`
  - exercises the real CLI path under `PYTHONIOENCODING=cp1252` and
    `PYTHONUTF8=0`.

### Frozen protocol identity

- `pipeline/run_m3_experiment.py`
  - requires `M3_PROTOCOL` / `M3-Protocol-v1.0` / `benchmark/M3_PROTOCOL.md`;
  - rejects missing or mismatched protocol identity before experiment output
    creation;
  - verifies the frozen protocol file declaration;
  - records protocol SHA-256 in `results.json` and `provenance.json`.
- Stress configs now declare the protocol explicitly:
  - `pipeline/stress_nuisance.yaml`
  - `pipeline/stress_context.yaml`
  - `pipeline/stress_shortcut.yaml`
  - `pipeline/stress_ood.yaml`

### Source traceability

The previously untracked OIR-PPV implementation needed for M4 was committed as
a traceable source snapshot. Operational task files, handoffs, artifacts, agent
folders, and unrelated repository dirt were not added to the source snapshot.

Source commits:

- `9533ce5ab608dcc4131a6880115787c0737c2f80`
  - `fix(oir-ppv): close M4 protocol compliance gaps`
- `f7e446d64d1c040cd168ae859d04503509cfe8ec`
  - `test(oir-ppv): enforce protocol identity at entrypoint`

Final source HEAD used for the accepted FIX_04 stress evidence:

`f7e446d64d1c040cd168ae859d04503509cfe8ec`

## 3. Frozen protocol identity

- Name: `M3_PROTOCOL`
- Version: `M3-Protocol-v1.0`
- Path: `benchmark/M3_PROTOCOL.md`
- SHA-256:
  `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`

Protocol mismatch is rejected before the requested experiment output directory
is created.

Evidence:

- `artifacts/stress_test/m4_fix04/protocol_identity_pytest.txt`
- `tests/test_m4_fix04.py`
- each accepted run's `results.json` and `provenance.json`

Focused result:

```text
3 passed, 3 deselected
```

## 4. Git and source provenance

- Git root: `D:/WORK/RESEARCH/MindForge`
- Branch: `research/pit`
- Executed HEAD:
  `f7e446d64d1c040cd168ae859d04503509cfe8ec`

Relevant source snapshot:

- covered paths: `benchmark`, `environments`, `pipeline`
- file count: `44`
- tree SHA-256:
  `18acaaa5ef46b9ccdd8b2af72f1b4bd99e2c660e8d6018995c312c2fa25bcb83`
- relevant source snapshot dirty: `false`

The repository root still contains unrelated untracked files, so individual
run provenance records root `git.dirty=true`. Each accepted run separately
records `source_snapshot.dirty=false`, the exact relevant source-tree hash, and
the executed HEAD. This prevents unrelated repository files from being confused
with the M4 source under test.

Evidence:

- `artifacts/stress_test/m4_fix04/source_traceability.json`
- each accepted run's `provenance.json`

## 5. Verification results

### Frozen causal threshold

Command:

```powershell
python -m pytest tests/test_m4_fix04.py -k "context_failure" -q
```

Result:

```text
2 passed, 4 deselected
```

Evidence:

- `artifacts/stress_test/m4_fix04/causal_threshold_pytest.txt`

### Windows CP1252 M2 CLI regression

Focused regression result:

```text
1 passed, 5 deselected
```

Evidence:

- `artifacts/stress_test/m4_fix04/windows_m2_cli_pytest.txt`

Real M2 command output under normal Windows execution:

```text
PASS FIX04-M2-B0: {'accuracy': 0.32709113607990015,
'f1_macro': 0.317081886887109,
'f1_micro': 0.32709113607990015,
'auroc': 0.4927118640490214}
exit_code=0
```

Evidence:

- `artifacts/stress_test/m4_fix04/m2_cli/windows_cli_output.txt`
- `artifacts/stress_test/m4_fix04/m2_cli/FIX04-M2-B0/result.json`

### Full regression

Command:

```powershell
python -m pytest -q
```

Result:

```text
51 passed
```

Evidence:

- `artifacts/stress_test/m4_fix04/full_regression_pytest.txt`

## 6. Stress preflight and reproducibility

Fresh FIX_04 evidence root:

`artifacts/stress_test/m4_fix04/`

All four saved stress assertions pass:

| Scenario | Saved shift evidence | Result |
| --- | --- | --- |
| Nuisance | train/test nuisance mean shift `2.8904995726800506` | PASS |
| Context | train/OOD total variation `1.0` | PASS |
| Shortcut | correlation `+0.7451087561423203` -> `-0.851428901996846` | PASS |
| OOD | `192` OOD samples, train/OOD overlap `0` | PASS |

Exact evidence:

- `artifacts/stress_test/m4_fix04/preflight/EXP-M4-STRESS-NUISANCE/shift_assertions.json`
- `artifacts/stress_test/m4_fix04/preflight/EXP-M4-STRESS-CONTEXT/shift_assertions.json`
- `artifacts/stress_test/m4_fix04/preflight/EXP-M4-STRESS-SHORTCUT/shift_assertions.json`
- `artifacts/stress_test/m4_fix04/preflight/EXP-M4-STRESS-OOD/shift_assertions.json`

The four stress scenarios were executed twice with seed `42`:

- `artifacts/stress_test/m4_fix04/run_a/`
- `artifacts/stress_test/m4_fix04/run_b/`

Reproducibility comparison policy:

```text
exact canonical JSON and exact decoded array content;
timestamps, commands, paths, and container-file hashes excluded
```

Result: `4/4 PASS`, `all_passed=true`.

Evidence:

- `artifacts/stress_test/m4_fix04/reproducibility_report.json`

## 7. Artifact/provenance audit

`artifacts/stress_test/m4_fix04/artifact_audit.json` reports all checks PASS:

- reproducibility all passed;
- relevant source snapshot clean;
- Git HEAD matches executed source;
- all protocol identities match the frozen protocol;
- all run provenance HEADs match;
- all source-tree hashes are identical across accepted runs;
- all saved shift assertions pass;
- no `NaN`, `Infinity`, or `-Infinity` JSON tokens;
- large causal arrays are externalized from JSON.

Audit summary:

- JSON files checked: `55`
- largest JSON: `20144` bytes
- largest JSON path:
  `artifacts/stress_test/m4_fix04/run_b/EXP-M4-STRESS-OOD/results.json`
- causal arrays: externalized to `causal_arrays.npz`
- generated/invariant arrays: externalized to `generated.npz`
- audit verdict: `all_passed=true`

Each accepted `provenance.json` records the requested component type, runtime
wrapper type, wrapped learner type, effective environment config and overrides,
dependencies, exact command, artifact path, Git state, relevant source snapshot,
and protocol identity/hash.

## 8. Controlled comparison disposition

The controlled comparison was not regenerated for FIX_04 because the FIX_04
changes affect protocol validation/provenance, causal failure classification,
Windows CLI output, and source traceability. They do not materially change the
controlled-comparison learner training path.

The last valid FIX_03 controlled comparison remains the learner-quality
reference for this handoff:

| Variant | Reconstruction MSE | Predictive accuracy |
| --- | ---: | ---: |
| Placeholder | 0.594214 | 0.984 |
| Untrained | 0.281605 | 0.800 |
| Trained | 0.238156 | 0.848 |

Training/reconstruction improved, but trained predictive accuracy remained
below the PCA placeholder. This is retained as a research limitation.

Reference evidence:

- `artifacts/stress_test/m4_fix03/controlled_comparison.json`
- `artifacts/stress_test/m4_fix03/controlled_comparison.md`

## 9. Scientific findings retained after FIX_04

### Software/protocol infrastructure verdict

`PASS FOR PM/QA RE-REVIEW`

The FIX_04 implementation is executable under the frozen protocol, traceable to
the executed source snapshot, reproducible under the documented comparison
policy, and compatible with the tested Windows M2 CLI path.

### Research learner-quality conclusion

`ROBUST INVARIANT / GENERALIZATION CLAIM: NOT_SUPPORTED`

The regenerated FIX_04 evidence retains the earlier limitations:

- context leakage is detected in all four run-A stress scenarios;
- nuisance leakage is detected in three of four scenarios;
- OOD is the only scenario without nuisance leakage;
- context stress has severe generalization degradation:
  `generalization_delta = -0.8304818308108504`;
- the FIX_03 controlled comparison showed training/reconstruction improvement,
  but trained predictive accuracy `0.848` remained below the PCA placeholder
  `0.984`.

Therefore FIX_04 supports protocol-compliant executability and reproducibility.
It does not establish robust invariant learning.

Evidence for leakage/generalization:

- `artifacts/stress_test/m4_fix04/artifact_audit.json`
- `artifacts/stress_test/m4_fix04/run_a/EXP-M4-STRESS-CONTEXT/results.json`
- `artifacts/stress_test/m4_fix04/run_a/EXP-M4-STRESS-CONTEXT/dependency_analysis.json`
- corresponding run-A `results.json` / `dependency_analysis.json` for
  NUISANCE, SHORTCUT, and OOD.

## 10. FIX_04 acceptance-criterion traceability

| # | Acceptance criterion | Exact evidence | Result |
| ---: | --- | --- | --- |
| 1 | `failure_cases` matches frozen `< 0.5` semantics | `pipeline/causal_validation.py`; `tests/test_m4_fix04.py`; `causal_threshold_pytest.txt` | PASS |
| 2 | Threshold and `0.5` boundary regressions pass | `artifacts/stress_test/m4_fix04/causal_threshold_pytest.txt` | PASS |
| 3 | Real M2 CLI exits 0 on supported Windows console path | `m2_cli/windows_cli_output.txt`; `m2_cli/FIX04-M2-B0/result.json`; `windows_m2_cli_pytest.txt` | PASS |
| 4 | Existing M2/M3/M4 regression passes | `artifacts/stress_test/m4_fix04/full_regression_pytest.txt` (`51 passed`) | PASS |
| 5 | Exact M4 source snapshot is traceable | `source_traceability.json`; executed HEAD `f7e446d...`; source tree `18acaaa...` | PASS |
| 6 | Every accepted stress run records frozen protocol identity/path/hash | run-A and run-B `results.json` / `provenance.json`; `artifact_audit.json` | PASS |
| 7 | Protocol mismatch fails before execution output | `tests/test_m4_fix04.py`; `protocol_identity_pytest.txt` | PASS |
| 8 | Four saved preflight shift assertions pass | four `preflight/<experiment-id>/shift_assertions.json`; `artifact_audit.json` | PASS |
| 9 | Four full scenarios execute twice at seed 42 and reproduce | `run_a/`; `run_b/`; `reproducibility_report.json` | PASS |
| 10 | Runtime provenance captures requested/runtime/config/override/dependency/command/Git/artifact fields | each accepted `provenance.json`; `artifact_audit.json` | PASS |
| 11 | Arrays externalized and JSON finite | `generated.npz`; `causal_arrays.npz`; `artifact_audit.json` | PASS |
| 12 | New handoff maps all criteria and retains failed learner findings | this `HANDOFF_007_v5.md` | PASS |

## 11. Deliverables

- corrected M4 source/config/protocol implementation committed at executed HEAD
  `f7e446d64d1c040cd168ae859d04503509cfe8ec`;
- fresh FIX_04 evidence root:
  `artifacts/stress_test/m4_fix04/`;
- focused threshold, protocol, Windows CLI, and full-regression test logs;
- source traceability record;
- two-repeat stress/reproducibility evidence;
- artifact/provenance audit;
- this `HANDOFF_007_v5.md`.

## 12. Gate

Target state achieved by Dev:

`READY FOR PM/QA RE-REVIEW`

`DEV_TASK_008_1.md` remains blocked pending independent PM/QA acceptance of
`HANDOFF_007_v5.md`.
