# H3R2-R Prospective Protocol Freeze v1

Status: `FROZEN_BEFORE_PROSPECTIVE_TEST_EXECUTION`

## Scientific boundary

Historical reconstruction and prospective generalization are separate claims.

Historical reconstruction is established for source snapshot `e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51`: all 100 learner/environment/seed train-representation SHA-256 values were reproduced exactly in the local reconstruction audit. The reconstruction-manifest SHA-256 is `aa0b534db0d5f7220f29e25d6e68e596f45735db8fa55b1a0e73bc0185d75d7c`.

H3R2-R tests the new claim that the frozen historical representation states generalize to fresh, disjoint prospective data.

## Frozen design

- Environments: `ENV-1` through `ENV-4`.
- Historical state seeds: `223691`, `965182`, `537173`, `538839`, `124586`.
- Representation learners: `L0` through `L4` from the historical learner manifest.
- Prospective cells: 20 environment/state-seed pairs.
- Each cell uses exactly one fresh prospective test seed from `PROSPECTIVE_SEED_REGISTRY_v1.json`.
- Prospective test seeds are unique and disjoint from all historical state seeds.
- Representation learners are loaded from frozen serialized state and MUST NOT be fitted, updated, tuned, or selected during prospective evaluation.
- Readouts are fitted only from the corresponding frozen historical training representation and historical training labels.
- Two readout families are evaluated for every learner with equal budget:
  - `linear`: multinomial/binary logistic regression as applicable; `solver=lbfgs`, `C=1.0`, `max_iter=1000`.
  - `degree2`: `PolynomialFeatures(degree=2, include_bias=false)` followed by the same logistic-regression contract.
- No architecture sweep, representation retraining, learner selection, readout-family selection, or hyperparameter selection may use prospective inputs or labels.
- Prospective data remains unopened until protocol, seed registry, reconstruction freeze, runner contract, and pre-test QA are committed.
- Every evaluated cell records source commit, reconstruction identity, frozen-state SHA-256, dataset/split identities, prospective seed, readout specification, predictions, metrics, and output hashes.

## Reconstruction gate

The committed reconstruction stage must reproduce all 100 historical train-representation hashes exactly before the prospective gate can open. A reconstruction mismatch blocks H3R2-R and no prospective data may be generated.

## Pre-test gate

Execution is allowed only when QA demonstrates all of the following:

1. The 20 prospective seeds are unique and disjoint from historical seeds.
2. Every loaded frozen-state SHA-256 equals the committed reconstruction manifest.
3. The reconstruction manifest records exactly `100/100` exact historical train-representation matches.
4. The prospective runner has no representation-learner construction, fit, update, or tuning path.
5. Prospective labels are used only for final metric computation, never for representation/readout selection.
6. Both readout families run for every learner with identical fixed hyperparameters.
7. Deterministic identity checks reproduce before metric execution.

Any gate failure blocks result execution and must be repaired in a new pre-result commit.

## Evidence and interpretation

For each learner and readout family, report prospective error rate and accuracy per cell and aggregated by environment and across all 20 paired cells. Report paired deltas against `L0` for the same environment/state-seed/prospective-seed cell. Report linear and degree-2 results separately before any aggregate interpretation.

The experiment may establish fresh-data transfer evidence and may diagnose readout expressivity. It must not treat the historical `100/100` reconstruction result as prospective support. It must not upgrade the broader OIR-PPV architecture from provisional to established solely from H3R2-R.
