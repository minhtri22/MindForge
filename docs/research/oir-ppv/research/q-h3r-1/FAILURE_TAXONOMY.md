# Q-H3R.1 Failure Taxonomy

| ID | Mechanism | Observable signature | Supporting evidence | Weakening evidence | Published H3R usable? | Fresh diagnostics needed? |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | TASK-SIGNAL LOSS | lower clean task utility; weak task-variable recoverability before noise | positive clean-risk gap vs L0; low task-variable probe | nonlinear probe recovers most of the gap | yes | yes |
| M2 | NOISE AMPLIFICATION | candidate task risk increases more than L0; latent drift tracks task degradation | positive `E_noise`; strong drift→degradation relation | negative/near-zero `E_noise`; noisy accuracy stable | yes | yes |
| M3 | SHORTCUT / NUISANCE DEPENDENCE | nuisance recoverability high and associated with failure | nuisance probe high; ENV-4 concentration | nuisance recoverability lower/equal to L0; weak relation to degradation | partly | yes |
| M4 | RELEVANT-Z SUPPRESSION | causal/context Z recoverability lower than L0 and task performance falls | reduced ENV-3 Z recovery | Z remains recoverable clean/noisy | partly | yes |
| M5 | REPRESENTATION BOTTLENECK | stronger compression/limited capacity tracks clean/noisy degradation | compression correlates with failure | same 8-D L0 succeeds; compression correlation weak | H1/H3R cross-analysis | yes |
| M6 | DECODER / PROBE DEPENDENCE | same representation improves materially with richer shared decoder | nonlinear/shared diagnostic probe closes large clean gap | richer probe gives no uplift | H3R identifies shared LR | yes |
| M7 | NONLINEAR INTERACTION FAILURE | single variables remain recoverable but linear task readout fails; pairwise/nonlinear probe helps | nonlinear uplift + retained task-variable signal | linear and nonlinear probes fail equally | no decisive causal proof | yes |
| M8 | DISTRIBUTIONAL SUPPORT FAILURE | noisy points move farther from train support and support shift tracks task degradation | positive support shift correlated with degradation | support shift large without degradation; near-zero correlation | no | yes |
| M9 | MODEL-SPECIFIC FAILURE | one learner family dominates clean/noisy failure | single-family concentration | all L1-L4 fail similarly | yes | yes |
| M10 | BENCHMARK-LEVEL FAILURE MODE | effect concentrated by ENV/seed/configuration | high between-ENV heterogeneity | same failure direction broadly across cells/learners | yes | yes |

No mechanism is assumed true a priori. All Q-H3R.1 classifications are exploratory.
