# Q-H3R.1 Analysis Plan

Evidence classes are separated before interpretation:

- `POST_HOC_EXPLORATORY`: new statistics derived only from already-published H3R/H2/H1 outputs.
- `FRESH_NON_TEST_EXPLORATORY`: new diagnostics on fresh train/validation data generated with disjoint seeds.

Phase A extracts all 20 H3R v1.1 cells and computes overall, learner, ENV, seed, learner×ENV, and descriptive failure-frequency tables. Paired H3R effects are preserved exactly from published artifacts.

Phase B joins H2 and H3R only at `learner+environment` because their seed sets differ. H2 ENV-2 is not imputed because it is inapplicable for the H2 primary analysis. H1/H3R also uses explicit `learner+environment` joins. Pearson/Spearman correlations and bootstrap intervals are descriptive exploratory statistics.

Phase C uses diagnostic namespace `QH3R1_DIAGNOSTIC_V1` with seeds `610101`, `610103`, `610107`. Only `train` and `val` splits are accessed. Noise magnitude is 0.10 train-scale-normalized L-infinity on numeric observation channels only; categorical channels are preserved. Three deterministic noise replicates are used per validation row.

The primary shared task probe matches the H3R logistic-regression family/configuration. Auxiliary task-variable, relevant-Z, nuisance, support, latent-drift, and degree-2 interaction probes are diagnostic only. Near-zero-variance latent dimensions are excluded from auxiliary standardized-distance/probe calculations with a deterministic active-dimension rule to avoid numerical amplification; the primary H3R-style task probe is unchanged.

No threshold is tuned from frozen H3R outcomes and no new confirmatory claim is made.
