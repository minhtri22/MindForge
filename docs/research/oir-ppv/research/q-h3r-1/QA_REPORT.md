# Q-H3R.1 Independent Self-Review

## Research reviewer

- Post-hoc H3R/H1/H2 statistics are explicitly labeled exploratory.
- Fresh diagnostics are train/validation only with new seeds.
- No causal wording upgrades correlation or probe recoverability to proof.
- Competing explanations M1-M10 are retained and ranked with contrary evidence.
- H3R v1.1 verdict and one-shot closure remain unchanged.

## QA

- `9 passed` focused integrity tests.
- H3R access-log hash before/after: `f4eb053696095c18c2d873107ebf1823b49cfb871b7a24e190a2cb76766d4bbb` → identical.
- H3R decisive raw-tree hash before/after: `26eeee35501dcf2cbd0471d555b0429080b14956065ecaa547b7d7e0932f9e62` → identical.
- diagnostic seeds `610101, 610103, 610107` are disjoint from 15 historical/frozen seeds discovered from manifests.
- categorical observation channels are asserted unchanged; numeric perturbations are asserted `<=0.10` train-scale-normalized L-infinity.
- H2/H3R and H1/H3R joins use explicit `learner+environment` keys; no seed imputation.
- auxiliary latent/probe diagnostics use a deterministic active-dimension rule after a numerical QA correction for near-zero PCA latent variance. The primary H3R-style task probe was not changed.
- pytest emitted only a cache-path `WinError 5` warning; test verdict is unaffected.

## PM / governance

- H3R v1.1: remains `CLOSED_WITH_LIMITS / NO_RERUN`.
- H4: remains `NOT_OPENED / DEFERRED_BY_OWNER`.
- Q-H3R.1: `PARTIAL_MECHANISM_DIAGNOSIS`.
- `NEXT_HYPOTHESES.md` contains candidates only; none is opened or executed.

## Findings by severity

- P0: `0`.
- P1: `0`.
- P2: `2`.
  1. The requested target branch `research/oir-ppv` does not contain the H3R publication package; analysis therefore uses an immutable snapshot of `oir-ppv-research@e8cf4a9` as source evidence and records the cross-branch provenance explicitly.
  2. `Q_H3R_1_QUESTION.md` was materialized after initial source verification. The owner task had already frozen the exact question before result inspection, so no outcome-dependent question change occurred.

No issue invalidates the exploratory analysis.
