# H3R2-R Runner Contract v1

Status: `FROZEN_BEFORE_PROSPECTIVE_LABEL_ACCESS`

## Purpose

This contract binds prospective H3R2-R execution to the committed historical reconstruction freeze. Historical reconstruction and prospective evidence remain separate claims.

## Representation boundary

For every `ENV-1..ENV-4` / historical-state-seed / learner cell:

1. Load the exact serialized state named by `H3R_RECONSTRUCTION_FREEZE_v1.json`.
2. Verify the serialized-state SHA-256, preprocessing SHA-256, historical train-representation SHA-256, source commit, and historical dataset identity before prospective evaluation.
3. Transform prospective observations only through the already-fitted `TableEncoder.transform()` and historical encoder `encode()` methods.
4. No representation constructor, representation `fit`, `fit_transform`, update, tuning, or model selection path is permitted in prospective execution.
5. Prospective labels are never passed into the representation path.

## Readout boundary

Readouts are fitted only from the corresponding frozen historical training representation and regenerated historical training labels after the historical dataset identity is verified.

Both readout families run for every learner with equal fixed budget:

- `linear`: logistic regression, `solver=lbfgs`, `penalty=l2`, `C=1.0`, `max_iter=1000`, `random_state=<historical_state_seed>`.
- `degree2`: `PolynomialFeatures(degree=2, include_bias=false)` followed by the exact same logistic-regression specification.

Prospective inputs or labels cannot select a learner, readout family, polynomial degree, or hyperparameter.

## Prospective data and noise boundary

- Use exactly the 20 mappings in `PROSPECTIVE_SEED_REGISTRY_v1.json`.
- Generate each prospective environment from the recovered historical source snapshot and frozen H3R environment-generation overrides.
- Use the prospective train observations only to derive the numeric-channel mask and train scale for the frozen H3R v1.1 observation-noise intervention.
- Use the prospective test split for clean/noisy evaluation.
- Generate the noisy test observations once per cell and share those exact observations across L0-L4 and both readout families.
- Preserve categorical channels and the historical H3R v1.1 `TRAIN_SCALE_NORMALIZED_L_INF` perturbation bound.

## Gate order

1. `historical-smoke` must reproduce the historical clean and noisy prediction hashes for state seed `223691` across ENV-1..ENV-4 without refitting a representation.
2. Runner, this contract, QA tests, seed registry, protocol freeze, and reconstruction freeze must be tracked and clean in Git.
3. `preflight` validates all frozen state/artifact hashes and source lineage, regenerates every prospective observation/noise identity twice, and writes `PROSPECTIVE_IDENTITY_LOCK_v1.json` plus `PRETEST_QA_v1.json` without reading prospective labels.
4. The identity lock and pre-test QA must then be committed and clean in Git.
5. `execute` may open prospective labels exactly after those gates pass. Existing execution output causes refusal instead of overwrite/rerun.

## Evidence output

Every prospective cell records:

- historical state seed and fresh prospective seed,
- reconstruction and identity-lock identities,
- frozen state/preprocessing/train-representation hashes,
- clean/noisy prospective representation hashes,
- clean/noisy prediction hashes for both readout families,
- realized-noise validator evidence,
- clean/noisy error and accuracy,
- paired deltas against L0.

The summary reports linear and degree-2 results separately. No support/falsification threshold may be invented after prospective results are visible.
