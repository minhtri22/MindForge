# OIR-PPV M4 Handoff 007 v4

## Status

`READY FOR PM/QA RE-REVIEW`

This handoff closes `DEV_TASK_008_FIX_03`. It replaces the rejected
`HANDOFF_007_v3.md`. M4 executability and evidence gates pass. The measured
learner quality limitations remain visible and are not promoted to a research
quality claim.

## 1. Implementation summary

- Restored `pipeline/run_m3_experiment.py` as an importable and executable
  entrypoint with strict learner factories.
- Added fitted train-only table encoders and actual runtime component
  provenance.
- Repaired ENV-4 split-specific nuisance/shortcut generation.
- Removed OOD holdouts from ordinary train/validation/test splits in ENV-1 and
  ENV-3.
- Stabilized categorical observation schemas during interventions.
- Replaced the crashing controlled comparison with explicit placeholder,
  initialized-untrained, and trained evaluation paths.
- Externalized causal invariant arrays to compressed NPZ files.
- Added preflight shift assertions, seen/OOD performance,
  `generalization_delta`, finite-value handling, shortcut metric status, and
  two-run reproducibility checks.

## 2. Changed files

### Pipeline

- `pipeline/run_m3_experiment.py`
- `pipeline/controlled_comparison.py`
- `pipeline/preflight_stress.py`
- `pipeline/run_m4_stress_suite.py`
- `pipeline/causal_validation.py`
- `pipeline/dependency_analysis.py`
- `pipeline/learners.py`
- `pipeline/stress_nuisance.yaml`
- `pipeline/stress_context.yaml`
- `pipeline/stress_shortcut.yaml`
- `pipeline/stress_ood.yaml`

### Environments

- `environments/env1_generator.py`
- `environments/env3_generator.py`
- `environments/env4_generator.py`

### Tests and handoff

- `tests/test_m4_fix03.py`
- `HANDOFF_007_v4.md`

## 3. Repository provenance

- Git root: `D:/WORK/RESEARCH/MindForge`
- Branch: `research/pit`
- HEAD: `8a1628d0fba93029f9b9bd6825865145278ff0c9`
- Worktree dirty at execution: `true`

The worktree contains pre-existing unrelated changes. No reset, cleanup,
commit, or staging operation was performed.

## 4. Verification commands

```powershell
python -m py_compile pipeline\run_m3_experiment.py pipeline\controlled_comparison.py pipeline\causal_validation.py
python -c "import pipeline.run_m3_experiment; import pipeline.controlled_comparison; print('IMPORT_OK')"
python -m pytest tests\test_m4_fix03.py -k "runner_factories" -q
python -m pytest tests\test_m4_fix03.py -k "controlled_comparison_smoke" -q
python pipeline\controlled_comparison.py --output artifacts\stress_test\m4_fix03 --max-train 500 --max-test 250 --epochs 15
python -m pipeline.preflight_stress pipeline\stress_nuisance.yaml pipeline\stress_context.yaml pipeline\stress_shortcut.yaml pipeline\stress_ood.yaml --output artifacts\stress_test\m4_fix03\preflight
python -m pipeline.run_m4_stress_suite --output artifacts\stress_test\m4_fix03
python -m pytest -q
```

Observed results:

- compile/import: PASS (`IMPORT_OK`)
- strict factory tests: 2 PASS
- controlled comparison smoke: 1 PASS
- shift preflight: 4/4 PASS
- stress repeats: 4 scenarios x 2 runs completed
- reproducibility: 4/4 PASS
- full regression: 45/45 PASS

## 5. Runtime environment

- Python `3.13.12`
- NumPy `2.4.4`
- PyYAML `6.0.3`
- scikit-learn `1.8.0`
- SciPy `1.17.1`

Each full-run `provenance.json` also records the dependency versions, exact
command, artifact directory, effective config hash, override hash, Git state,
requested component type, runtime wrapper type, and wrapped learner type.

## 6. Evidence package

Root: `artifacts/stress_test/m4_fix03/`

- `controlled_comparison.json`
- `controlled_comparison.md`
- `reproducibility_report.json`
- `preflight/<experiment-id>/shift_assertions.json`
- `run_a/<experiment-id>/...`
- `run_b/<experiment-id>/...`

Each repeat contains:

- `effective_env_config.yaml`
- `shift_assertions.json`
- `evaluation.json`
- `causal_validation.json`
- `causal_arrays.npz`
- `dependency_analysis.json`
- `generated.npz`
- `results.json`
- `provenance.json`

Largest JSON in the evidence package is below 20 KB. Large invariant and
generation arrays are present only in compressed NPZ artifacts and are
referenced from JSON by path, shape, dtype, and SHA-256.

## 7. Evidence results and limitations

### Shift assertions

| Scenario | Assertion evidence | Result |
| --- | --- | --- |
| Nuisance | train/test mean shift `2.8905` | PASS |
| Context | train/OOD total variation `1.0` | PASS |
| Shortcut | label correlation `+0.7451` to `-0.8514` | PASS |
| OOD | 192 OOD samples; train/OOD overlap `0` | PASS |

### Controlled comparison

| Variant | Reconstruction MSE | Predictive accuracy |
| --- | ---: | ---: |
| Placeholder | 0.594214 | 0.984 |
| Untrained | 0.281605 | 0.800 |
| Trained | 0.238156 | 0.848 |

Encoder loss decreased from `1.104712` to `0.836269`; decoder loss decreased
from `0.988331` to `0.633736`. The recorded rule therefore sets
`learning_demonstrated=true`. The trained representation does not outperform
PCA predictive accuracy, so this evidence supports learner execution and
training only.

### Stress metrics from run A

| Scenario | Overall | Invariant preservation | Generalization delta |
| --- | ---: | ---: | ---: |
| Context | 0.840564 | 0.891415 | -0.830482 |
| Nuisance | 0.790263 | 0.856385 | -0.017778 |
| OOD | 0.722482 | 0.780209 | 0.000000 |
| Shortcut | 0.827551 | 0.820886 | -0.004444 |

`generalization_delta` is defined as unseen-environment score minus
train-environment score. The context result shows severe OOD degradation.
Dependency analysis also flags context leakage in all four scenarios and
nuisance leakage in context, nuisance, and shortcut scenarios. These are
learner findings and remain open research limitations. All shortcut metrics
have explicit `valid` status; no evidence JSON contains `NaN`.

## 8. Acceptance-criterion traceability

| Criterion | Evidence | Result |
| --- | --- | --- |
| Runner compiles/imports | commands in section 4 | PASS |
| Factory and comparison coverage | `tests/test_m4_fix03.py`; 45-test suite | PASS |
| Unknown types rejected | `test_runner_factories_reject_unknown_types` | PASS |
| Truthful controlled comparison | comparison JSON and Markdown | PASS |
| Per-scenario shifts asserted | preflight and repeat `shift_assertions.json` | PASS |
| Required metrics | repeat `evaluation.json`, `dependency_analysis.json`, `causal_validation.json` | PASS |
| Runtime/Git provenance | repeat `provenance.json` | PASS |
| Reproducibility | `reproducibility_report.json` | PASS |
| Large arrays externalized | `generated.npz`, `causal_arrays.npz`; compact JSON audit | PASS |
| Consistent handoff | this document contains no known syntax or crash blocker | PASS |

`DEV_TASK_008_1.md` remains blocked until independent PM/QA review accepts M4.
