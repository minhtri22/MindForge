# MK-1 Scientific Training Execution Enforcement Specification v0.1

Status: **FROZEN BEFORE TRAINING-EXECUTION ENFORCEMENT CODE / OPTIMIZER STEP 1 FORBIDDEN**

Date: **2026-09-21**

## 1. Purpose

This specification closes two execution-capability gaps discovered before any scientific optimizer step:

1. the existing `train_arm` path reconstructs the deterministic sample schedule from the seed instead of consuming the already-frozen schedule artifact;
2. the canonical materialization artifact contains PRISTINE_CONFIRMATORY, so a training workflow that downloads that artifact cannot prove absence of PRISTINE access capability.

These are execution-enforcement gaps only.

They do not change:

- scientific data;
- tokenizer;
- paired initializations;
- frozen schedules;
- model architecture;
- losses;
- optimizer hyperparameters;
- learning-rate schedule;
- validation cadence;
- checkpoint selector;
- hypotheses or thresholds.

## 2. Frozen scientific inputs

Materialization artifact:

- run `35553551910`
- artifact `10619711251`
- ZIP SHA-256 `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Tokenizer artifact:

- run `35562370974`
- artifact `10622602143`
- ZIP SHA-256 `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Paired-init/schedule artifact:

- run `35572770344`
- artifact `10626846126`
- ZIP SHA-256 `01579c6643003aab615dfd9c530f5c1a0868250072f7e922e8aa90968af88ff3`

## 3. Frozen file identities

TRAIN:

`5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`

VALIDATION:

`8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`

Tokenizer:

`e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

Paired-init file SHA-256:

- 71001: `b74b7ab8a67a11c076a94f9df5325a616231acdb99639c3a94424d65382dd8e8`
- 71002: `7b2dcc6ab1cd377fedc6a0eb32809719fcac911cfb4cbd235684f9b4f10b621e`
- 71003: `774ad2e2e5f0dddac8bfd67ee04537854309c983043314c82d5841e7a82ca860`
- 71004: `25a96874e33828d9e9dd5de85a98a12028632d138c40c6f3a70760e0ff0b3d32`
- 71005: `76c427debc7e68012fe5be6b5bf409c8ac49fff9bc2346e6b022befdf37c3730`

B0 state SHA-256:

- 71001: `c8a7fbf63e0df8a827ff7c9291d4955db9a59b14ad1d28387fffa00e0b7a2ad7`
- 71002: `04cd00ce71965649281c618212c120c165d6283519eab2d9f13beb22110f674d`
- 71003: `f3ffadfa63e011bf691ac2e0f86a67eb023606d19a875104b77ea40d35577beb`
- 71004: `2f1d93bf7119ffb67c939e3c6235054232854d59ab4151e5b95ae6e2828d931d`
- 71005: `e553c8aa984a7b7040e392776f5a35aa6925658dbb932bc5777a0e5f35d326ab`

Schedule SHA-256:

- 71001: `18262d3bec5fde01ebdb43bac7afb8142c32dd2aecff8245800435202270eaac`
- 71002: `8de8516dd6802106d4cf7fe36745a8636e888d9c5c711d76c7870fc2582f64b3`
- 71003: `3e5eb4ba3dbb297ce2176361544773db54ca8a1c3e3ddb89aa1367049bd18077`
- 71004: `e4839585f54ad14f02bd8c029d3461b6cb25063f044408cc5eeee08a8d064c5e`
- 71005: `52b5ce49529db34761d093cc8aa5c0a04ae19e6224e5d80e8bcf998f8dc435d9`

## 4. Training-input bundle

Before the training execution lock may PASS, create exactly one immutable derived bundle.

The bundle may be constructed only from the three canonical upstream artifacts in section 2.

It contains exactly:

- frozen TRAIN JSONL;
- frozen VALIDATION JSONL;
- frozen tokenizer JSON;
- five frozen paired-init `.pt` files;
- five frozen schedule JSONL files;
- one bundle manifest JSON.

It must not contain:

- PRISTINE_CONFIRMATORY JSONL;
- tokenized PRISTINE manifest;
- materialization generator code outputs beyond TRAIN/VALIDATION;
- any regenerated tokenizer/init/schedule.

The bundle builder may read the canonical upstream artifacts only to verify/copy frozen bytes. It may not instantiate a model, optimizer, tokenizer trainer, schedule RNG, or data generator.

The bundle manifest freezes SHA-256 of every included file and proves the exact expected file set.

## 5. Frozen-schedule consumption in training

The scientific training path must consume the frozen schedule JSONL corresponding to the seed.

It must not call `deterministic_sample_indices` during a fresh scientific training execution.

Required training function inputs include:

- `schedule_path`;
- `expected_schedule_sha256`.

Before model/optimizer execution, training must:

1. SHA-256 the schedule file and require exact expected hash;
2. parse exactly 5,000 rows;
3. require row `step` = 1..5000;
4. require exactly eight ordered sample keys per row;
5. resolve each key against the frozen sorted TRAIN rows;
6. require every schedule key exists;
7. require no duplicate key ambiguity;
8. consume those exact eight records at each optimizer step.

Resume may skip already-completed schedule rows by step count, but may not reconstruct earlier/later schedule from RNG.

The existing `deterministic_sample_indices` helper remains available for historical/pretraining audit evidence but is forbidden in the scientific training path.

## 6. Frozen optimization contract

Unchanged:

- optimizer: AdamW;
- LR: `3e-4`;
- weight decay: `0.1`;
- gradient clip: `1.0`;
- optimizer steps: `5000`;
- micro-batch: `1`;
- accumulation: `8`;
- warmup fraction: `0.05`;
- cosine learning-rate decay through existing `mindforge.train.learning_rate_multiplier`;
- minimum LR fraction: `0.1`;
- dtype: float32;
- device: auto.

No early stopping.

## 7. Validation and checkpoint selection

Training workflow may expose only TRAIN and VALIDATION data.

VALIDATION evaluation occurs exactly at:

`250, 500, ..., 5000`

for the full frozen VALIDATION surface set.

Checkpoint selector remains the same canonical-C balanced score for both arms:

- DIRECT: direct C;
- M1-Z: R(Z);
- strict score improvement replaces best;
- exact tie retains earliest checkpoint.

All 5,000 steps execute regardless of validation score.

## 8. PRISTINE capability exclusion

The scientific training workflow must not:

- download artifact `10619711251`;
- download artifact `10622602143` directly;
- download artifact `10626846126` directly;
- contain the string `pristine` or `PRISTINE` in any executable path/argument;
- receive a file whose bundle manifest names PRISTINE_CONFIRMATORY;
- invoke confirmatory evaluation.

Instead it downloads only the derived training-input bundle by exact artifact ID/run ID/digest.

This makes PRISTINE absence an execution capability property, not merely a procedural promise.

## 9. Training workflow

The candidate workflow is inert until a separate final trigger exists.

Before any trigger may be created it must pass static QA proving:

- only the exact training bundle is downloaded;
- bundle digest and internal manifest are verified;
- only frozen `train_arm` / execution wrapper is invoked;
- no generator function is imported/called;
- no tokenizer fit function is imported/called;
- no paired-init preparation function is called;
- no schedule generator is called;
- no PRISTINE path/artifact is present;
- matrix contains exactly 10 jobs = 2 arms × 5 frozen seeds;
- each matrix job selects the correct paired-init/schedule hashes.

## 10. Implementation allowlist

Before execution-lock PASS, changes are limited to:

- prospective enforcement-only edit to `experiments/model_core/mk1/trainer.py`;
- new `experiments/model_core/mk1/training_execution.py`;
- new `tests/test_model_core_mk1_training_execution.py`;
- new `.github/workflows/mk1-training-bundle.yml`;
- new `.github/workflows/mk1-scientific-training.yml`;
- bundle/lock governance documents and triggers for bundle construction only.

No model, loss, metric, data generator, tokenizer implementation, or scientific target contract may change.

## 11. Stop rule

Any need to alter a scientific value, seed, dataset row, tokenizer, paired initialization state, schedule order, optimization hyperparameter, validation cadence, or checkpoint selector stops this execution-enforcement repair.

Optimizer step 1 remains forbidden until:

1. training bundle is frozen;
2. enforcement implementation is hash-bound;
3. candidate training workflow passes static execution QA;
4. `MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK = PASS`.
