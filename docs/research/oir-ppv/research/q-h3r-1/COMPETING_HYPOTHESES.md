# Q-H3R.1 Competing Mechanisms

| ID | Classification | Evidence |
| --- | --- | --- |
| M1 TASK-SIGNAL LOSS | `WEAKLY_SUPPORTED` | Published clean-risk gaps vs L0 are large for all candidates (`+0.178` to `+0.214` mean). Fresh linear clean accuracy is `0.813–0.834` vs L0 `0.978`. However nonlinear probes recover substantial accuracy, so the missing linear utility is not pure information destruction. |
| M2 NOISE AMPLIFICATION | `WEAKENED` | Published mean `E_noise` is negative for every candidate (`-0.0135` to `-0.0178`), and fresh task degradation is about `-0.0021` to `+0.0055`. Candidate latent drift→task-degradation correlation is only `r=0.267`. |
| M3 SHORTCUT / NUISANCE DEPENDENCE | `WEAKENED` | Fresh nuisance recoverability is lower than L0 for L1/L3/L4 and similar for L2; nuisance recoverability vs task degradation is `r=-0.085`. ENV-4's injected shortcut is not independently isolated by a dedicated intervention here, so this is not a full refutation. |
| M4 RELEVANT-Z SUPPRESSION | `REFUTED_WITHIN_DIAGNOSTIC_SCOPE` | In the applicable causal ENV-3 diagnostic, relevant-Z recovery is ~`1.0` for L0-L3 and `0.994` for L4 clean, remaining ~`0.993–1.0` under noise. |
| M5 REPRESENTATION BOTTLENECK | `WEAKENED` | L0 and candidates all use 8-D outputs, yet L0 is much stronger. H1 compression ratio vs H3R clean gap has Pearson `r=0.098` with CI spanning zero. Compression alone does not explain the failure. |
| M6 DECODER / PROBE DEPENDENCE | `SUPPORTED` | A degree-2 shared diagnostic probe improves candidate clean accuracy by `+0.086` to `+0.111` on average; L0 uplift is `-0.003`. L2 rises from `0.833` linear to `0.943` nonlinear, shrinking its clean gap vs nonlinear L0 to `-0.031`. |
| M7 NONLINEAR INTERACTION FAILURE | `SUPPORTED` | Candidate task-variable recoverability remains `0.867–0.950`, while nonlinear readout strongly improves task prediction. Interaction uplift vs linear clean accuracy is strongly negative (`r=-0.872`), consistent with useful information being encoded in a less linearly accessible form. |
| M8 DISTRIBUTIONAL SUPPORT FAILURE | `WEAKENED` | Candidate support shift is ~`0.035–0.036`, not larger than L0 `0.040`; support shift vs task degradation is `r=0.016`. ENV-2 has the largest support shift (~`0.101`) while retaining ~`0.99` clean task accuracy and near-zero degradation. |
| M9 MODEL-SPECIFIC FAILURE | `WEAKENED` | All L1-L4 violate the H3R clean utility guard in all 20 descriptive cells; no single family accounts for the aggregate falsification. |
| M10 BENCHMARK-LEVEL FAILURE MODE | `WEAKLY_SUPPORTED` | Published robustness effect is heterogeneous by ENV: ENV-2 gives ~`-0.05` mean `E_noise` for all candidates while ENV-1/4 are near zero. Fresh between-ENV variance exceeds between-seed variance for clean accuracy and support shift. This affects effect size but does not erase the shared clean-utility problem. |

Overall ranking: **M6 ≈ M7 > residual M1 > M10 > M2/M3/M5/M8/M9, with M4 weakened most strongly within its applicable scope.**
