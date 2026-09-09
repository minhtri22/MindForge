# Q-H2.1 Transferability Analysis

## Question

`Q-H2.1 — What makes an invariant transferable?`

This is a post-H2 research analysis over accepted/current evidence only. It does
not amend H1, H2, H3, any frozen protocol, matrix, seed list, metric, threshold,
learner, or environment definition.

## Evidence used

- `EXP-LRN-001` frozen reference learner benchmark
- accepted H1 closure evidence, including corrected inference-state complexity
- accepted H2 closure evidence and `QA_REPORT_HANDOFF_010_H2.md`
- H3 closure design in `H1_H4_CLOSURE_PLAN.md`
- H3 QA contract in `tasks/QA_TASK_001.md`
- available nuisance/intervention diagnostics already emitted by `EXP-LRN-001`

Repository state for this analysis:

- branch: `oir-ppv-research`
- HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- EXP-LRN-001 manifest SHA256:
  `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- H1 protocol SHA256:
  `8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`
- H2 protocol SHA256:
  `5d851da06b06b36e1c3272c2d7dc4b1ad8f7c360a4654803945b05e3cd84c661`

No new learner run or scientific artifact was created for this analysis.

## What H1 + H2 already establish

H1 showed that small retained inference state can satisfy the frozen complexity
criterion versus exact-row MEM. H2 then showed that this does not imply OOD
transfer superiority over L0/PCA.

Across the 15 H2-relevant ENV/seed cells, corrected mean `C_total` is:

| Learner | Mean C_total bytes |
|---|---:|
| L0 PCA | 1205 |
| L1 MLP | 2608.3 |
| L2 VAE | 2641.3 |
| L3 IRM-style | 2633.3 |
| L4 DANN | 2645.3 |

The more complex L1-L4 representations all had negative frozen H2 paired OOD
effects against L0. Therefore representational complexity or method class alone
does not identify a transferable invariant in this benchmark.

## Descriptive evidence for candidate properties

The analysis below compares each L1-L4 cell to the same ENV/seed L0 cell across
the 60 frozen H2 treatment pairs. Correlations are descriptive post-hoc summaries,
not new acceptance metrics and not causal proof.

### 1. Retain task-relevant signal

This is the strongest current candidate explanation.

- Across all 60 pairs, delta in existing `predictive_utility` has descriptive
  correlation `r ~= 0.749` with frozen H2 `Delta_OOD`.
- Mean predictive-utility delta versus L0 is negative for every tested learner:
  - L1: `-0.163`
  - L2: `-0.204`
  - L3: `-0.166`
  - L4: `-0.176`
- H2-positive individual cells still exist while predictive utility is sometimes
  lower than L0, so retained predictive utility is not proven sufficient or
  necessary from this evidence alone.

Interpretation: losing task-relevant signal is a plausible contributor to poor
transfer, and the current evidence supports keeping retained utility as a hard
co-condition in H3. It does not identify the causal representation content that
must be retained.

### 2. Suppress nuisance / shortcut information

Current evidence is directionally suggestive but inconsistent.

- Existing nuisance-sensitivity delta is available for 40/60 H2 pairs; lower is
  better. Its descriptive correlation with `Delta_OOD` is about `r = -0.352`.
- Mean nuisance-sensitivity delta is worse than L0 for every tested learner where
  the field is available:
  - L1: `+0.0248`
  - L2: `+0.0762`
  - L3: `+0.0246`
  - L4: `+0.0197`
- Nuisance leakage is detected more often in the tested candidates than in L0
  across the 15 eligible cells per learner:
  - L1: `6` candidate cells vs `3` L0 cells
  - L2: `9` vs `3`
  - L3: `6` vs `3`
  - L4: `7` vs `3`
- However, the 11 H2-positive treatment cells do not show a consistent
  lower-leakage signature. Some positive cells still leak more nuisance than L0.

Interpretation: nuisance suppression remains a plausible property of a useful
invariant, but current evidence does not establish it as necessary or sufficient
for transfer.

### 3. Stability under task-preserving `do(N)` intervention

Existing `avg_nuisance_invariance` is also mixed.

- Across 60 pairs, delta in existing average nuisance invariance has descriptive
  correlation `r ~= 0.520` with `Delta_OOD`.
- But the 11 H2-positive cells have mean nuisance-invariance delta about `-0.012`
  versus L0, while the 48 negative cells average about `+0.032`.
- Therefore current representation-level invariance diagnostics do not provide a
  clean monotonic explanation of the transfer result.

Most importantly, the decisive H3 quantity has not yet been executed:

`Delta_N = Perf_factual - Perf_do(N)`

with retained predictive utility as a simultaneous condition. Existing
representation stability cannot substitute for that H3 test.

### 4. Preserve minimal sufficient structure

H1/H2 provide only a boundary, not a solution.

- L0 is materially smaller in retained inference state than L1-L4 on the relevant
  H2 cells and transfers better under the frozen H2 comparison.
- This rejects the idea that added representation complexity is itself evidence
  of transferable structure.
- The current evidence does not identify which latent dimensions or causal/task
  factors are minimally sufficient. That requires ablation/sufficiency evidence
  beyond Q-H2.1 and is later H5 territory.

## Q-H2.1 classification

`UNRESOLVED`

Reason:

The accepted evidence supports a partial explanation that transferable
representations must avoid losing task-relevant signal, and it leaves nuisance
suppression as a plausible contributing property. But the evidence does not show
that nuisance robustness or current `do(N)` representation stability is a
necessary or sufficient mechanism for transfer. Positive H2 cells do not carry a
consistent nuisance-robustness signature, and the decisive H3 task-preserving
intervention metric has not yet been run.

The strongest current working interpretation is therefore:

```text
transferability likely requires retained task/causal signal
                    +
          robustness to nuisance variation
                    +
   no unnecessary representation burden that adds no transferable signal
```

This is a research hypothesis for interpretation only. The conjunction is not yet
supported as a scientific claim.

## Consequence for H3

Continue the existing H3 closure unchanged.

H3 remains responsible for the decisive question already frozen in the closure
design:

- does task performance degrade less under matched `do(N)` intervention than the
  primary baseline;
- is nuisance leakage lower/equal;
- is predictive utility retained;
- are degenerate invariant solutions rejected.

Q-H2.1 introduces no new H3 metric, threshold, environment, seed, baseline,
learner, or success rule. Its status remains `UNRESOLVED` until later accepted
evidence is strong enough to revisit it under a separately governed research
decision.
