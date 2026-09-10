# Q-H3R.1 Results

## 1. Question

Which information required for robust prediction is lost, distorted, or improperly encoded under observation noise in the H3R-tested representations?

## 2. Evidence sources

Immutable H3R v1.1 closure/evidence, historical H1/H2 evidence, and fresh `QH3R1_DIAGNOSTIC_V1` train/validation diagnostics. Exact sources and hashes are in `SOURCE_INVENTORY.md` and `provenance.json`.

## 3. Historical H3R status

- scientific verdict: `FALSIFIED_UNDER_TESTED_CONDITIONS`
- closure: `CLOSED_WITH_LIMITS / NO_RERUN`
- decisive scientific access: exactly `1`
- P0/P1: `0/0`
- H3R v1.0: `CLOSED / PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT`
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`

## 4. Published H3R forensic findings

All four candidates fail the retained-clean-utility component. Mean clean-risk gaps vs L0 are L1 `+0.2141`, L2 `+0.1780`, L3 `+0.2115`, L4 `+0.2096`, with all adjusted intervals far above the `+0.02` utility margin. Descriptively, all `20/20` cells per candidate exceed the cell-level `0.02` clean-gap threshold.

The observation-noise effect itself is not a broad candidate collapse. Mean `E_noise` is negative for every candidate: L1 `-0.0178`, L2 `-0.0167`, L3 `-0.0158`, L4 `-0.0135`. None clears the required adjusted practical-support margin, but the direction contradicts a simple noise-amplification account. ENV-2 is the strongest negative-noise-effect environment (~`-0.05` for every candidate), while ENV-1 and ENV-4 are near zero.

Across 80 candidate cells, larger clean-risk gaps are moderately associated with more negative `E_noise` (Pearson `-0.414`, bootstrap 95% CI `[-0.601,-0.190]`; Spearman `-0.390`). This is post-hoc and not causal.

## 5. H1/H2/H3R cross-analysis

H2 and H3R have disjoint seed sets, so only explicit `learner+environment` aggregate joins are used. There are `12` matched H2/H3R learner×ENV rows; ENV-2 is not imputed. H2 `Delta_OOD` vs H3R clean gap has Pearson `-0.761` with bootstrap interval excluding zero, but Spearman uncertainty is wide; this is descriptive evidence that historically weaker transfer often co-occurs with a larger clean gap in the later H3R setup. H2 `Delta_OOD` vs `E_noise` is less stable (`r=-0.494`, interval spans zero).

H1/H3R provides `16` learner×ENV matches. H1 compression ratio vs H3R clean gap is near zero (`r=0.098`, interval spans zero), weakening compression magnitude as the main explanation. This does not negate H1's bounded compression result.

## 6. Fresh diagnostic results

Fresh seeds: `610101`, `610103`, `610107`; 12 datasets; 60 learner rows; train/validation only; three deterministic noise replicates; test access unchanged.

Primary shared linear task accuracy is L0 `0.978`, versus L1 `0.829`, L2 `0.833`, L3 `0.834`, L4 `0.813`. Yet mean noise degradation is tiny: L1 `+0.0055`, L2 `-0.0021`, L3 `+0.0029`, L4 `+0.0008` versus L0 `+0.0045`.

Task-variable recoverability remains materially higher than linear task accuracy for several candidates: L1 `0.867`, L2 `0.950`, L3 `0.869`, L4 `0.884`. A degree-2 diagnostic probe raises clean task accuracy to L1 `0.918`, L2 `0.943`, L3 `0.920`, L4 `0.916`, versus nonlinear L0 `0.975`. The remaining nonlinear candidate gap is `-0.057`, `-0.031`, `-0.055`, `-0.059` respectively. Therefore much, but not all, of the clean deficit is recoverable with a richer readout.

Relevant-Z recoverability in applicable ENV-3 is essentially preserved (`~0.993–1.0`). Candidate nuisance recoverability is not higher than L0 in aggregate. Candidate support shifts are ~`0.035–0.036` versus L0 `0.040`; support shift vs task degradation is `r=0.016`. Latent drift is somewhat larger for candidates (`0.160–0.182` vs L0 `0.140`) but its relationship to task degradation is weak (`r=0.267`). Interaction uplift vs linear clean accuracy is strong and negative (`r=-0.872`), while task-variable recoverability vs clean accuracy is positive (`r=0.646`).

## 7. Failure-mechanism ranking

Strongest: M6 decoder/probe dependence and M7 nonlinear interaction failure. Residual M1 task-signal loss remains plausible because nonlinear decoding does not fully match L0. M10 environment heterogeneity is present but secondary. M2, M3, M5, M8, and M9 are weakened; M4 is refuted within the limited relevant-Z diagnostic scope.

## 8. What is supported

The H3R v1.1 falsification is best explained, within current exploratory evidence, by a **clean representation/readout problem rather than observation-noise amplification**. Candidate representations often preserve useful task variables, but useful structure is less linearly accessible than in L0. A richer readout recovers a large portion of the deficit.

## 9. What remains unresolved

The present diagnostics cannot causally separate M6 from M7, cannot determine whether the residual post-nonlinear gap is true information loss versus another decoder mismatch, and do not isolate ENV-4's injected spurious shortcut with a dedicated intervention. Three fresh diagnostic seeds are sufficient for exploratory convergence checks but not a new confirmatory benchmark.

## 10. Claim boundary

H3R v1.1 remains closed and falsified under its tested conditions. Q-H3R.1 does not revise it and does not authorize H4 or a rerun.

## 11. Recommended next hypothesis

Priority P1 is `H3R.2`: prospectively freeze an equal-budget nonlinear readout in a successor protocol with fresh test identity to determine how much of the H3R clean-utility failure is decoder/readout-limited.

Q-H3R.1 classification: `PARTIAL_MECHANISM_DIAGNOSIS`.
