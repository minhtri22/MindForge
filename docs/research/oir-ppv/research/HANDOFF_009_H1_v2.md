# HANDOFF_009_H1_v2 - H1 Canonical Inference-State Accounting & Reporting Closure

## 1. Implementation summary

Implemented `DEV_TASK_009_FIX_01` as a derived accounting correction over the preserved `EXP-H1-001` evidence.

The correction does not rerun or overwrite the frozen 140-cell scientific matrix. It deterministically reconstructs the fitted learner state for the same frozen cell identity, serializes only the state required for representation inference `X -> I`, verifies representation replay and unchanged utility, and writes corrected complexity evidence under a versioned correction namespace.

Corrected canonical inference-state accounting:

- L0 PCA: fitted transform state only (`components_`, `mean_`) plus the fitted input table encoder.
- L1 MLP: normalization state plus encoder layers; classifier excluded.
- L2 VAE: normalization state plus encoder body and posterior-mean head; decoder and log-variance head excluded.
- L3 IRM-style surrogate: normalization state plus encoder layers; classifier excluded.
- L4 DANN: normalization state plus encoder layers; task head and domain head excluded.

Serialization is pickle protocol 5 over a deterministic, ordered pure-data payload containing the fitted table encoder state, numeric arrays, layer type metadata, and layer weights/biases. The payload is sufficient to replay the frozen representation path within absolute tolerance `1e-12`.

The common downstream LogisticRegression task head remains excluded from `C_total` exactly as frozen. `C_total` remains:

`C_total = model_bytes + retained_state_bytes`

No learner training objective, architecture, hyperparameter, environment, split, seed, epsilon, RAW semantics, MEM semantics, or fidelity label was changed.

## 2. Changed files

Source/tests:

- `pipeline/run_h1_closure.py`
- `tests/test_h1_closure.py`

Versioned derived outputs:

- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_comparison_v2.json`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/H1_CLOSURE_REPORT_v2.md`
- `artifacts/h1_closure/EXP-H1-001/correction_v2/original_evidence_manifest.json`
- `artifacts/h1_closure/EXP-H1-001/correction_v2/correction_summary.json`
- `artifacts/h1_closure/EXP-H1-001/correction_v2/cells/*/complexity_v2.json`
- `artifacts/h1_closure/EXP-H1-001/correction_v2/cells/*/provenance_v2.json`

Preserved infrastructure-failure attempts:

- `artifacts/h1_closure/EXP-H1-001/correction_v2_attempt_01_failed/`
- `artifacts/h1_closure/EXP-H1-001/correction_v2_attempt_02_failed/`

The original `h1_comparison.json`, `H1_CLOSURE_REPORT.md`, frozen protocol, frozen matrix manifest, and all original raw 140-cell evidence remain retained.

## 3. Commit SHA / Git state

Branch:

`oir-ppv-research`

Current HEAD:

`0521c5754a32e2625930de75fe2635c6ce5ec9a0`

Working tree is dirty. The repository already contained pre-existing working-tree coordination/research state, including a modified `PLAN.md`. This correction did not update the H1 state in `PLAN.md`.

Frozen identities remain unchanged:

- H1 protocol SHA256: `8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`
- H1 matrix manifest SHA256: `55127d173e36028e069c841331b9807ee0dc4948241408c110b3a460be21823c`
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`

Original derived-output hashes captured before correction:

- `h1_comparison.json`: `936905d6f94dce5cc1fcbed6e2d47c8e251268dac48e76b9c4e7910635a538de`
- `H1_CLOSURE_REPORT.md`: `dfe0c4947902ae6254f0ce38fe75616dddde3b0a9acd76bf3cbd3d91abb749ac`

## 4. Commands executed

Syntax/focused verification:

```powershell
python -m py_compile pipeline/run_h1_closure.py
python -m pytest tests/test_h1_closure.py -q -p no:cacheprovider
```

Derived accounting correction:

```powershell
python -m pipeline.run_h1_closure correct-accounting
```

Aggregate/report regeneration:

```powershell
python -m pipeline.run_h1_closure aggregate-v2
```

Regression subset:

```powershell
python -m pytest tests/test_learner_contract.py tests/test_real_learners.py tests/test_benchmark_m2.py tests/test_pipeline.py -q -p no:cacheprovider
```

The first two correction attempts failed before producing accepted corrected evidence:

1. Attempt 01: direct pickle of torch modules was not byte-deterministic.
2. Attempt 02: manual PCA replay differed only by floating-point operation-order noise (`max_abs_error = 5.551115123125783e-16`).

Both attempts were preserved and the final implementation uses deterministic pure-data serialization plus replay tolerance `1e-12`.

## 5. Runtime environment

- OS: Windows 11
- Python: `3.13.12`
- Shell: PowerShell
- Per-cell corrected provenance records dependency versions through the existing `_dependency_versions()` path.

## 6. Generated / corrected artifacts

Correction mode:

`derived_accounting_deterministic_reconstruction`

Counts:

- original final scientific cells verified: `140`
- corrected learner complexity cells: `100`
- failed corrected learner cells: `0`
- inapplicable corrected learner cells: `0`
- original final scientific cells overwritten: `0`

Corrected-output hashes:

- `h1_comparison_v2.json`: `55c2873aa613ec877af6967c4f8272c16c5f9c9c95d420aab67518c3ba9ec1da`
- `H1_CLOSURE_REPORT_v2.md`: `31e3c671b130aed29cb2ae66025a11aa7b2441b9532b326e8fd116eccbd24100`
- `original_evidence_manifest.json`: `0df23244cd17030d9f10c3e677517767648cf984c308d47fc76330a70fbc2fa9`
- `correction_summary.json`: `7fda0d8218af7045bc0fbb6a6b680e287ac69ab42b0c3079c22a85d461ea66e1`

Corrected H1 paired success counts vs frozen MEM comparator:

| Learner | H1-success pairs | Total pairs |
|---|---:|---:|
| L0 PCA | 20 | 20 |
| L1 MLP | 19 | 20 |
| L2 VAE | 19 | 20 |
| L3 IRM-style surrogate | 20 | 20 |
| L4 DANN | 19 | 20 |

RAW utility non-inferiority counts are retained separately and materially constrain interpretation:

| Learner | Non-inferior vs RAW | Total pairs |
|---|---:|---:|
| L0 PCA | 15 | 20 |
| L1 MLP | 1 | 20 |
| L2 VAE | 2 | 20 |
| L3 IRM-style surrogate | 1 | 20 |
| L4 DANN | 1 | 20 |

RAW has frozen `C_total = 0`, so learner/RAW `C_total` ratios and compression ratios are encoded as JSON `null` with explicit reasons.

Developer candidate under the unchanged frozen H1 rule:

`SUPPORTED`

Authority:

`DEVELOPER_CANDIDATE_ONLY`

PM/QA owns final H1 acceptance and any `PLAN.md` status update.

## 7. Known limitations / failed or inapplicable evidence

1. MEM exact-row lookup has `0` test hits across all 20 MEM environment/seed cells, so MEM test utility comes entirely from the frozen global-majority fallback.
2. RAW has `C_total = 0` because raw input storage and the common downstream task head are excluded by the frozen accounting.
3. The evidence supports only the frozen H1 comparison against this exact-row MEM control within ENV-1..ENV-4 and seeds `42, 123, 456, 789, 1011`.
4. The evidence does not establish learned-representation superiority to RAW. Negative RAW comparisons remain present in v2 outputs.
5. L3 remains an IRM-style surrogate; L4 retains its existing adapted DANN fidelity label.
6. Canonical representation replay permits only numerical operation-order error up to absolute `1e-12`; final utility was independently reconstructed and required to match original utility within `1e-12`.
7. Two failed correction-infrastructure attempts are preserved. They did not alter original scientific evidence and are not scientific cell failures.
8. Known Windows pytest temporary-directory ACL warnings remain visible in repository status operations; the focused and declared regression suites executed successfully in this correction run.

## 8. Developer self-check against acceptance criteria

1. [x] Frozen hashes unchanged and all 140 historical cells verified against pre-correction file hashes.
2. [x] `model_bytes` now measures only canonical `X -> I` inference state for L0-L4.
3. [x] Training-only classifier/decoder/logvar/task/domain state excluded where unused by `encode()`.
4. [x] Canonical serialization deterministic and per-cell provenance complete.
5. [x] `C_total = model_bytes + retained_state_bytes` unchanged; corrected learner retained-state bytes remain zero.
6. [x] Learner behavior, seeds, ENV-1..4, epsilon, RAW/MEM semantics, fidelity labels, and EXP-LRN-001 evidence unchanged.
7. [x] v2 comparison contains complete MEM paired wins/losses/ties and mean/median/min/max summaries.
8. [x] v2 comparison contains RAW paired utility statistics, non-inferiority classification, and explicit zero-denominator `null` handling.
9. [x] Required summary statistics are present for all five learner families.
10. [x] Machine-readable and human-readable outputs explicitly retain MEM 0-hit and RAW interpretation limitations.
11. [x] Focused H1 tests: `18 passed`; regression subset: `53 passed`.
12. [x] This correction did not update H1 state in `PLAN.md`.
13. [x] H2 not started; MindForge not integrated.

### QA blocker correction table

| QA blocker | Original behavior | Corrected behavior | Evidence path | Status |
|---|---|---|---|---|
| Canonical inference-state accounting | Whole fitted extractor/wrapper serialized, including training-only L1-L4 state | Deterministic pure-data canonical `X -> I` payload with learner-specific training-only state excluded and replay verified | `artifacts/h1_closure/EXP-H1-001/correction_v2/` | PASS |
| Aggregate reporting completeness | Incomplete MEM/RAW paired summaries and no full zero-denominator handling | Full MEM and RAW wins/losses/ties, mean/median/min/max, non-inferiority, per-environment evidence, limitations, and RAW ratio `null` reasons | `experiments/OIR_PPV/H1_Closure/EXP-H1-001/h1_comparison_v2.json`, `H1_CLOSURE_REPORT_v2.md` | PASS |

Status: `READY_FOR_QA_REVIEW`

