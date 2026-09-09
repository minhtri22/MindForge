# QA Report — HANDOFF_008_1 / EXP-LRN-001

## Scope

- Project: OIR-PPV Research v1.0
- Branch: `research/pit`
- Reviewed source HEAD: `8d57175f5b5ce7195b6132fec7863331080ac1fe`
- Developer handoff: `HANDOFF_008_1.md`
- Benchmark: `EXP-LRN-001`
- Skills applied: `qa-core`, `qa-research`, `qa-software`

## QA verdict

`PASS_WITH_LIMITS`

M4.1 is acceptable as a reference-learner benchmark freeze. The evidence is sufficient to show that the benchmark executes five distinct learner families under one frozen matrix and produces materially different outcomes.

This verdict does not close H1-H4. The benchmark is a reference evidence layer for later hypothesis closure.

## Source of truth

- `PLAN.md`
- `theory.md`
- `benchmark/M3_PROTOCOL.md`
- `tasks/DEV_TASK_008_1.md`
- `HANDOFF_008_1.md`
- `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json`
- `artifacts/learner_benchmark/EXP-LRN-001/`

## Acceptance matrix

| Criterion | Observed | Verdict |
| --- | --- | --- |
| Common contract for L0-L4 | PCA, MLP, VAE, IRM-style, DANN are registered through the benchmark learner contract | PASS |
| Real training for L1-L4 | Runtime classes and learner implementation are trainable; developer fidelity labels retained | PASS |
| Frozen evaluator/protocol | Manifest records `M3-Protocol-v1.0` and the frozen protocol hash | PASS |
| Same matrix | 5 learners × 4 environments × 5 seeds = 100 cells | PASS |
| Failed cells preserved | First failed ENV-4 attempt is archived separately; canonical rerun contains 100/100 complete | PASS |
| Fidelity disclosure | L0 faithful; L1/L2/L4 adapted; L3 surrogate | PASS |
| Provenance/artifact audit | Canonical audit reports 100/100 PASS; independent verification reports PASS | PASS |
| Learner discrimination | Accuracy, OOD/generalization and leakage differ materially across learner families | PASS |
| MindForge excluded | EXP-LRN-001 contains only L0-L4 | PASS |

## Independent findings relevant to H1-H4

### H1 — Compression

Current benchmark does not contain the required complexity/utility comparison against raw/context memorization.

Available evidence includes latent dimensionality/effective rank, but that is insufficient to establish:

`C(I) < C(M)` while preserving `Performance_I >= Performance_M`.

Scientific state: `INCONCLUSIVE`.

### H2 — Transfer

The current reference learners do not support a general transfer-uplift claim over PCA.

Across the available OOD environments, the non-PCA learners are usually below PCA on unseen score. Prior direct paired QA calculation over ENV-1/3/4 found mean unseen-score deltas versus PCA of approximately:

- L1: `-0.307`
- L2: `-0.381`
- L3: `-0.300`
- L4: `-0.299`

The reference benchmark therefore supplies strong negative evidence for the present compact learners.

Scientific state for the tested reference learners: `NOT_SUPPORTED`.

This does not yet falsify the broader OIR-PPV/MindForge H2 claim because MindForge has not been evaluated.

### H3 — Nuisance Robustness

PCA has fewer nuisance leakage runs than the compact learned representations overall. Direct QA aggregation found:

- L0 PCA: 3 nuisance leakage runs
- L1 MLP: 7
- L2 VAE: 12
- L3 IRM-style: 6
- L4 DANN: 8

The explicit invariance/domain objectives therefore do not demonstrate superior nuisance robustness in this configuration.

Scientific state for the tested reference learners: `NOT_SUPPORTED`.

### H4 — Counterfactual / Causal Accuracy

EXP-LRN-001 reports `do(N)` and `do(Z)` representation-response/invariance metrics, but its comparison rows do not contain a ground-truth counterfactual error metric `D_cf`.

The frozen M3 protocol declares `do(A)` and counterfactual evaluation, while the M4.1 benchmark matrix intentionally freezes only `do(N)` and `do(Z)` for this learner-comparison task. Therefore EXP-LRN-001 is insufficient to establish:

`D_cf(I) < D_cf(M)`.

Scientific state: `INCONCLUSIVE`.

## Material limitations

1. L3 is an IRM-style surrogate, not canonical IRMv1.
2. L1/L2/L4 are compact four-epoch project-owned adaptations, not paper-scale reproductions.
3. ENV-2 has no non-empty OOD split, so OOD/generalization metrics are null there by design.
4. The common decoder means manifestation metrics measure the encoder-decoder pair.
5. Independent pytest replay in the managed Windows sandbox is limited by the existing `tmp_path` ACL failure. The current QA review therefore relies on direct source/artifact inspection plus the retained canonical test evidence. This is an environment limitation, not a scientific PASS signal.

## QA decision

Freeze `EXP-LRN-001` as the accepted M4.1 reference benchmark.

Advance to a dedicated H1-H4 closure sequence. Do not reinterpret the negative reference-learner result as a benchmark failure: the benchmark is discriminative and the negative outcomes are useful evidence.

