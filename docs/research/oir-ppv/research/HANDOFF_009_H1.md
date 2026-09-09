# HANDOFF_009_H1 - H1 Compression / Complexity-Utility Closure

## 1. Implementation summary

Implemented `DEV_TASK_009_H1_CLOSURE` on branch `oir-ppv-research` without changing L0-L4 learner semantics, the frozen evaluator, environment generators, seed list, or `EXP-LRN-001` historical results.

Added:

- H1 protocol freeze and hash;
- RAW control;
- deterministic MEM exact-memorization control;
- common H1 complexity accounting;
- H1 smoke/reproducibility gate;
- frozen 140-cell matrix;
- full H1 execution;
- machine-readable comparison;
- H1 closure report;
- focused H1 tests.

Primary frozen complexity metric:

`C_total = model_bytes + retained_state_bytes`

The common downstream `LogisticRegression(max_iter=1000, random_state=seed)` task head is excluded from `C_total` for every condition.

## 2. Changed files

Source/tests:

- `pipeline/run_h1_closure.py`
- `tests/test_h1_closure.py`

Protocol/report artifacts:

- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_protocol_freeze.json`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_protocol_freeze.sha256`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/matrix_manifest.json`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/matrix_manifest.sha256`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_comparison.json`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/H1_CLOSURE_REPORT.md`

Runtime evidence:

- `artifacts/h1_closure/EXP-H1-001/smoke/`
- `artifacts/h1_closure/EXP-H1-001/full/`
- `artifacts/h1_closure/EXP-H1-001/full_run_summary.json`

`PLAN.md` hypothesis state was not modified by this task.

## 3. Commit SHA

Starting/current repository HEAD used by the frozen H1 protocol:

`0521c5754a32e2625930de75fe2635c6ce5ec9a0`

Branch:

`oir-ppv-research`

The H1 source/artifact changes are working-tree changes at handoff time. The execution provenance truthfully records the dirty state. A new Git commit was not created from this sandbox session.

Historical `EXP-LRN-001` provenance remains referenced exactly as recorded, including its pre-migration source SHA `8d57175...`.

## 4. Experiment commands

Protocol freeze:

```powershell
python -m pipeline.run_h1_closure freeze-protocol
```

Smoke/reproducibility:

```powershell
python -m pipeline.run_h1_closure smoke
```

Matrix freeze:

```powershell
python -m pipeline.run_h1_closure freeze-matrix
```

Full matrix:

```powershell
python -m pipeline.run_h1_closure full
```

Aggregate:

```powershell
python -m pipeline.run_h1_closure aggregate
```

Focused tests:

```powershell
python -m pytest tests/test_h1_closure.py -q -p no:cacheprovider
```

Regression subset without pytest `tmp_path` cases:

```powershell
python -m pytest tests/test_learner_contract.py tests/test_real_learners.py tests/test_benchmark_m2.py tests/test_pipeline.py -q -p no:cacheprovider
```

## 5. Runtime environment

Runtime/dependency versions are recorded per final cell in `provenance.json` using the existing `_dependency_versions()` path.

Observed platform during execution:

- Windows / PowerShell
- Python environment currently used by the accepted M3/M4 benchmark stack
- NumPy / scikit-learn / PyTorch / PyYAML versions captured in per-cell provenance

## 6. Generated artifacts

### Frozen protocol

H1 protocol freeze SHA256:

`8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`

Matrix manifest SHA256:

`55127d173e36028e069c841331b9807ee0dc4948241408c110b3a460be21823c`

Reference `EXP-LRN-001` manifest SHA256 recorded in H1 freeze:

`f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`

### Smoke

- 14/14 smoke executions complete
- 7/7 conditions reproducible at seed 42
- required smoke artifact/schema and `C_total` accounting check passed

### Full matrix

- expected: 140 cells
- completed: 140
- failed: 0
- inapplicable seen-utility cells: 0
- no replacement seeds
- no scientific retry

### Aggregate H1 evidence

Frozen non-inferiority tolerance:

`epsilon = 0.02` absolute accuracy

Paired H1 success counts against MEM:

| Condition | Paired cells | Lower C_total + non-inferior utility |
|---|---:|---:|
| L0 PCA | 20 | 20 |
| L1 MLP | 20 | 19 |
| L2 VAE | 20 | 19 |
| L3 IRM-style surrogate | 20 | 20 |
| L4 DANN | 20 | 19 |

Mean `C_total` deltas versus MEM were negative for every learner family. L0 and L3 satisfied the frozen H1 paired rule in all 20 environment/seed pairs.

Developer candidate classification:

`SUPPORTED`

This candidate applies only to the frozen H1 definition against MEM within ENV-1..ENV-4 and seeds `42, 123, 456, 789, 1011`. PM/QA owns the final scientific classification.

## 7. Known limitations / failed cells

Failed final cells:

`0`

Material limitations:

1. RAW has `C_total=0` under the frozen accounting because raw input itself is not retained model state and the common downstream task head is excluded. Therefore this result must not be interpreted as learned representations being more storage-efficient than RAW.
2. H1 primary comparator is MEM, per the task/freeze. The candidate `SUPPORTED` statement is strictly “lower representation/MEM inference state while utility is non-inferior to MEM under epsilon=0.02.”
3. L1/L2/L3/L4 can have materially lower utility than RAW even where they satisfy H1 versus MEM.
4. Pickle protocol 5 is the frozen canonical serialization used for representation inference-state bytes in this reference/control closure layer.
5. Peak process memory is `null` because reliable per-cell Windows measurement was not available.
6. MindForge is intentionally excluded from DEV_TASK_009.
7. Full pytest replay still encounters the known Windows sandbox ACL failure in tests using pytest `tmp_path`; this is retained as an environment blocker rather than classified as a software failure.

## 8. Developer self-check

- [x] Protocol semantics frozen before full matrix execution.
- [x] Utility tolerance frozen before full matrix execution.
- [x] RAW and MEM implemented without test-label access in MEM inference API.
- [x] L0-L4 reused via existing learner boundary.
- [x] `C_total` categories are mutually exclusive.
- [x] Same frozen seeds retained.
- [x] 140/140 final cells retained.
- [x] Per-cell `results.json`, `complexity.json`, `provenance.json`, `condition_config.json` produced by the final runner.
- [x] Aggregate per-environment/per-seed evidence produced.
- [x] H1 focused tests: 10/10 PASS.
- [x] Regression subset not using `tmp_path`: 53/53 PASS.
- [x] Full regression was attempted and the remaining blocker is pytest Windows `tmp_path` ACL behavior.
- [x] `PLAN.md` H1 state not changed.
- [x] MindForge not integrated.
- [x] H2 not started.

Status: `READY FOR INDEPENDENT PM/QA REVIEW`

