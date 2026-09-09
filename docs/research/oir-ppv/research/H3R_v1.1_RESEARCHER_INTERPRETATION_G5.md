# H3R v1.1 G5 RESEARCHER INTERPRETATION

Date: 2026-09-09
Role: Researcher / scientific interpretation
Experiment: `EXP-H3R-002`

## Scientific verdict

`FALSIFIED_UNDER_TESTED_CONDITIONS`

Under the frozen H3R v1.1 protocol, none of L1-L4 jointly demonstrates the required observation-noise robustness improvement over L0/PCA while preserving clean utility.

The learned candidates show negative mean `E_noise` values, so they are directionally less degraded by the frozen observation-noise family than L0/PCA on average. That signal is insufficient for H3R support: the multiplicity-adjusted upper CIs do not clear the required `-0.01` practical improvement margin, and all four candidates incur large clean-risk penalties relative to L0/PCA. The clean-utility failure alone satisfies the predeclared falsification rule for every candidate.

The result therefore rejects the tested operational claim that these frozen L1-L4 learner definitions provide a useful robustness advantage over L0/PCA under the H3R v1.1 observation-noise regime.

## Claim boundary

This verdict is limited to:

- L1-L4 historical learner definitions retrained from scratch under H3R v1.1;
- L0/PCA as the frozen baseline;
- ENV-1..ENV-4;
- H3R seeds `223691, 965182, 537173, 538839, 124586`;
- generator-native frozen test support;
- `delta=0.10` train-scale-normalized L_inf observation noise on numeric channels only;
- four noise replicates;
- shared frozen LogisticRegression probe;
- frozen multiplicity, utility, veto, and classification rules.

It does not establish that PCA is generally more robust than learned invariants, does not falsify invariant learning generally, and does not establish claims about canonical IRM/DANN/VAE/MLP implementations, mechanism-changing interventions, counterfactual reasoning, MindForge product behavior, real-world robustness, or H4-H6.

The negative result is retained as scientific evidence. No rescue experiment or post-hoc tuning is authorized under H3R v1.1.
