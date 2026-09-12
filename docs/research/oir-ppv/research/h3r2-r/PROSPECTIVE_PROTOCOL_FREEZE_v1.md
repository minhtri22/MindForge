# H3R2-R Prospective Protocol Freeze v1

Status: FROZEN BEFORE PROSPECTIVE TEST EXECUTION

## Scientific boundary

Historical reconstruction and prospective generalization are separate claims.

Historical reconstruction is established for the H3R source snapshot `e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51`: all 100 learner/environment/seed train-representation SHA-256 values were reproduced exactly. The reconstruction manifest SHA-256 is `aa0b534db0d5f7220f29e25d6e68e596f45735db8fa55b1a0e73bc0185d75d7c`.

H3R2-R tests the new claim that those frozen historical representation states generalize to fresh, disjoint prospective data.

## Frozen design

- Environments: ENV-1 through ENV-4.
- Historical state seeds: 223691, 965182, 537173, 538839, 124586.
- Frozen representation learners: L0 through L4 from the reconstructed historical state manifest.
- Prospective cells: 20 environment/state-seed pairs.
- Each cell uses one fresh prospective test seed from `PROSPECTIVE_SEED_REGISTRY_v1.json`.
- Prospective test seeds are unique and disjoint from all historical state seeds.
- Representation learners are loaded from frozen serialized state and MUST NOT be fitted, updated, or tuned during H3R2-R.
- Readouts are fitted only from the corresponding frozen historical training representation and historical training labels.
- Two readout families are allowed: linear and frozen degree-2 nonlinear readout.
- No architecture sweep, representation retraining, learner selection, readout-family selection, or hyperparameter selection may use prospective test inputs or labels.
- Prospective test data remains unopened until protocol, seed registry, runner contract, and pre-test QA are frozen in Git history.
- Every evaluated cell records source commit, reconstruction-manifest identity, frozen-state SHA-256, dataset/split identities, prospective seed, readout specification, predictions, metrics, and output hashes.

## Pre-test gate

Execution is allowed only when QA demonstrates all of the following:

1. The 20 prospective seeds are unique and disjoint from historical seeds.
2. Every loaded frozen-state SHA-256 equals the reconstruction manifest.
3. No representation-learner fit/update path is reachable during prospective evaluation.
4. Prospective labels are not read by representation or readout selection logic.
5. Readout specifications and selection budget are identical across learners.
6. A deterministic dry run that does not open prospective test labels reproduces the same identities/hashes on rerun where applicable.

Any pre-test gate failure blocks prospective result execution and must be repaired in a new pre-result commit.

## Decision rule

The result report must distinguish representation generalization from readout expressivity. Linear and degree-2 results are reported separately for every learner and environment before aggregate interpretation. Historical 100/100 reconstruction is provenance evidence only and is not counted as prospective support for H3.

