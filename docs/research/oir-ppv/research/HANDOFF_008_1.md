# DEV_TASK_008_1 - OIR-PPV Standard Learner Benchmark Integration Handoff

## Status

`READY FOR PM/QA REVIEW`

The reference learner benchmark completed its gated smoke, reproducibility,
artifact audit, matrix freeze, and full `EXP-LRN-001` execution. This handoff
does not claim that OIR-PPV or MindForge is superior to the reference methods.

## 1. Implementation summary

Five literature-grounded learner families now run through the same accepted
`EncoderLearner.fit/encode/get_output_dim/get_config_hash` contract and the
same M3 evaluator:

| ID | Runtime implementation | Research source | Fidelity | Declared deviation |
| --- | --- | --- | --- | --- |
| L0 | `PCAEncoder` | Pearson (1901), principal component analysis | faithful | Uses the maintained scikit-learn adapter. |
| L1 | `MLPEncoderTrainable` | Rumelhart, Hinton and Williams (1986) | adapted | Compact full-batch supervised encoder and task head. |
| L2 | `VAEEncoder` | Kingma and Welling (2013), arXiv:1312.6114 | adapted | Compact full-batch VAE; posterior mean is the deterministic representation. |
| L3 | `IRMStyleEncoderSurrogate` | Arjovsky et al. (2019), arXiv:1907.02893 | surrogate | Cross-domain task-risk variance penalty; explicitly not canonical IRMv1. |
| L4 | `DANNSurrogateEncoder` | Ganin et al. (2016), JMLR 17(59) | adapted | Compact task head, domain head and gradient reversal implementation. |

The production runner imports all reference learner registrations itself. It
does not depend on test import side effects. ENV-2 now exposes context and
nuisance metadata and rebuilds observations after interventions. Prediction
metrics use class probabilities for AUROC and write inapplicable R2/OOD values
as `null` with a reason.

`pipeline/run_learner_benchmark.py` enforces the sequence smoke, seed-42
repeat, artifact/schema/provenance audit, matrix freeze, full execution, and
report generation. Existing evidence cannot be overwritten silently.

## 2. Changed files

- `pipeline/learners_extended.py`: trainable MLP, VAE, IRM-style surrogate and
  DANN implementations plus registry wiring.
- `pipeline/run_m3_experiment.py`: production registry import, classification
  metric semantics, composition holdout assertion, dependency provenance and
  JSON/YAML numeric-key-safe override merge.
- `pipeline/run_learner_benchmark.py`: gated benchmark orchestration, fixed
  matrix, smoke reproducibility, audits and aggregate reporting.
- `environments/env2_generator.py`: context/nuisance metadata and functional
  factor/nuisance intervention rebuild.
- `pipeline/learners.py`: safe fixed-width output for the legacy MLP placeholder
  path retained for backward compatibility.
- `tests/test_learner_contract.py`: common contract, fidelity, deterministic
  seed, production registry and manifest round-trip regression tests.
- `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/`: generated configs,
  frozen manifest, manifest hash and comparison report.
- `artifacts/learner_benchmark/EXP-LRN-001/`: canonical smoke and full evidence.

`PLAN.md` was not changed. MindForge was not implemented or evaluated.

## 3. Commit SHA and source identity

- Reference learner implementation: `33da43667ecf3288058fd0aaf77889aa0c1f2fd6`
- ENV-4 manifest round-trip correction: `8d57175f5b5ce7195b6132fec7863331080ac1fe`
- Canonical evidence source HEAD: `8d57175f5b5ce7195b6132fec7863331080ac1fe`
- Scoped source tree SHA-256:
  `2bf9390a7a590fa88c86007195b1071e675a122fe283edd5af42ab4f381b9cb2`
- Scoped paths: `benchmark`, `environments`, `pipeline`
- Scoped source status during smoke/full runs: clean

The wider MindForge repository remained dirty because it contains unrelated
untracked research, archive and artifact files. Per-run provenance records this
truthfully while the task-scoped source snapshot remains clean and hash-linked.

## 4. Execution commands

```powershell
python -m pytest -q -p no:cacheprovider --basetemp D:\WORK\RESEARCH\MindForge\docs\research\oir-ppv\research\artifacts\pytest_full_fix_env4
python -m pipeline.run_learner_benchmark smoke
python -m pipeline.run_learner_benchmark freeze
python -m pipeline.run_learner_benchmark full
python -m pipeline.run_learner_benchmark report
```

Pytest required an unsandboxed invocation on this Windows host because the
managed sandbox denied pytest's `tmp_path` ACL creation/cleanup. No test was
skipped or weakened.

## 5. Runtime environment

- OS: Windows 11, build 26200, AMD64
- CPU runtime: Intel64 Family 6 Model 189; PyTorch CPU build
- Python: 3.13.12
- NumPy: 2.4.4
- PyYAML: 6.0.3
- scikit-learn: 1.8.0
- SciPy: 1.17.1
- PyTorch: 2.12.0+cpu
- Frozen seeds: `42, 123, 456, 789, 1011`
- Full-run summed cell duration: 103.77 seconds
- Mean/max cell duration: 1.04 / 3.89 seconds

## 6. Generated artifacts and validation evidence

Canonical experiment definition:

- `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json`
- `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.sha256`
- `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/comparison_report.md`
- Manifest SHA-256:
  `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`

Canonical evidence:

- `artifacts/learner_benchmark/EXP-LRN-001/smoke/smoke_report.json`
- `artifacts/learner_benchmark/EXP-LRN-001/smoke/smoke_artifact_audit.json`
- `artifacts/learner_benchmark/EXP-LRN-001/full_run_summary.json`
- `artifacts/learner_benchmark/EXP-LRN-001/full_artifact_audit.json`
- `artifacts/learner_benchmark/EXP-LRN-001/independent_verification.json`
- `artifacts/learner_benchmark/EXP-LRN-001/comparison_results.json`
- 100 per-cell directories under `artifacts/learner_benchmark/EXP-LRN-001/full/`

Validation results:

- Focused learner/override tests: `13/13 PASS`
- Full regression after final correction: `64/64 PASS`
- Smoke execution: `10/10 complete`
- Seed-42 repeat: `5/5 learners reproducible`, JSON equal and arrays all-close
  at `rtol=1e-6`, `atol=1e-7`
- Smoke artifact/schema/provenance audit: `10/10 PASS`
- Full matrix: `100/100 complete`, `0 failed`
- Full artifact/schema/provenance audit: `100/100 PASS`
- Independent provenance/hash verification: `100/100 PASS`

Matrix-cell disposition (`complete/failed/skipped`):

| Learner | ENV-1 | ENV-2 | ENV-3 | ENV-4 |
| --- | --- | --- | --- | --- |
| L0 PCA | 5/0/0 | 5/0/0 | 5/0/0 | 5/0/0 |
| L1 MLP | 5/0/0 | 5/0/0 | 5/0/0 | 5/0/0 |
| L2 VAE | 5/0/0 | 5/0/0 | 5/0/0 | 5/0/0 |
| L3 IRM-style | 5/0/0 | 5/0/0 | 5/0/0 | 5/0/0 |
| L4 DANN | 5/0/0 | 5/0/0 | 5/0/0 | 5/0/0 |

The first full attempt is retained at
`artifacts/learner_benchmark/EXP-LRN-001_ATTEMPT_01_PROTOCOL_FAILURE/`.
It contains `75 complete / 25 failed` because frozen JSON stringified numeric
ENV-4 class keys. The entire attempt was archived before the corrected sequence
was rerun; individual failed cells were not selectively retried.

## 7. Known limitations and scientific findings

- L3 is an IRM-style risk-variance surrogate and cannot be cited as canonical
  IRMv1 evidence.
- L1, L2 and L4 are compact project-owned implementations with four full-batch
  epochs. They validate protocol compatibility and learner discrimination;
  they are not tuned reproductions of paper-scale results.
- ENV-2 uses a compositional held-out test set and has no separate non-empty OOD
  split. `unseen_environment_score` and `generalization_delta` are therefore
  `null` with a reason for all ENV-2 cells.
- Constant latent dimensions produce expected undefined-correlation warnings.
  Serialized metrics remain finite or explicit `null`; strict JSON audit passed.
- Some ENV-3 folds have very small minority classes, producing scikit-learn
  cross-validation warnings. Results are retained without seed selection.
- The shared conditional MLP decoder is trained for every encoder, so generated
  quality reflects the encoder-decoder pair rather than the encoder alone.

The benchmark distinguishes learners, supporting H-L1 at the protocol level.
The explicit invariance/domain learners did not consistently reduce leakage or
improve OOD generalization relative to PCA. H-L2 is therefore not supported by
this compact configuration. This contrary result is retained and must not be
rewritten as an OIR-PPV or learner superiority claim.

## 8. Developer self-check and acceptance traceability

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| One contract for L0-L4 | PASS | `tests/test_learner_contract.py`; all 100 runtime provenance records |
| Actual training for L1-L4 | PASS | learner fidelity tests and per-run invariant metadata |
| Frozen evaluator/protocol retained | PASS | manifest protocol hash and per-run `protocol` identity |
| Smoke before full matrix | PASS | `smoke_report.json` timestamps and frozen manifest evidence links |
| Identical environment/seed matrix | PASS | frozen manifest; 100 unique matrix cells |
| Correct metric null/probability semantics | PASS | per-run `evaluation.generalization.task_metrics` |
| Complete artifacts and provenance | PASS | `full_artifact_audit.json` and `independent_verification.json` |
| Seed-42 reproducibility | PASS | five comparisons in `smoke_report.json` |
| M2/M3 regression | PASS | `64 passed in 14.94s` |
| Honest fidelity/failure/null reporting | PASS | comparison report and Sections 6-7 above |
| MindForge excluded | PASS | frozen manifest contains only L0-L4 |

Developer verdict: implementation and evidence are complete for independent
PM/QA review. Acceptance of this handoff may authorize a separate MindForge
integration task; it does not itself authorize or perform that integration.
