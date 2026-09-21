# MK-1 Scientific Training Execution Lock v0.1

Status: **PENDING INDEPENDENT FINAL REVIEW / OPTIMIZER STEP 1 FORBIDDEN**

Date: **2026-09-21**

Formal candidate:

`MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK_PENDING_REVIEW`

## 1. Frozen scientific artifacts

Materialization:

- run `35553551910`
- artifact `10619711251`
- ZIP SHA-256 `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Tokenizer:

- run `35562370974`
- artifact `10622602143`
- ZIP SHA-256 `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Paired initialization / exact schedules:

- run `35572770344`
- artifact `10626846126`
- ZIP SHA-256 `01579c6643003aab615dfd9c530f5c1a0868250072f7e922e8aa90968af88ff3`

Training-only execution bundle:

- run `35581007427`
- artifact `10629399106`
- ZIP SHA-256 `56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af`

The scientific training workflow is allowed to download only artifact `10629399106`.

## 2. Frozen bundle file identities

- TRAIN: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- VALIDATION: `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`
- tokenizer: `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

Paired-init file hashes:

- 71001 `b74b7ab8a67a11c076a94f9df5325a616231acdb99639c3a94424d65382dd8e8`
- 71002 `7b2dcc6ab1cd377fedc6a0eb32809719fcac911cfb4cbd235684f9b4f10b621e`
- 71003 `774ad2e2e5f0dddac8bfd67ee04537854309c983043314c82d5841e7a82ca860`
- 71004 `25a96874e33828d9e9dd5de85a98a12028632d138c40c6f3a70760e0ff0b3d32`
- 71005 `76c427debc7e68012fe5be6b5bf409c8ac49fff9bc2346e6b022befdf37c3730`

Paired B0 state hashes:

- 71001 `c8a7fbf63e0df8a827ff7c9291d4955db9a59b14ad1d28387fffa00e0b7a2ad7`
- 71002 `04cd00ce71965649281c618212c120c165d6283519eab2d9f13beb22110f674d`
- 71003 `f3ffadfa63e011bf691ac2e0f86a67eb023606d19a875104b77ea40d35577beb`
- 71004 `2f1d93bf7119ffb67c939e3c6235054232854d59ab4151e5b95ae6e2828d931d`
- 71005 `e553c8aa984a7b7040e392776f5a35aa6925658dbb932bc5777a0e5f35d326ab`

Exact schedule hashes:

- 71001 `18262d3bec5fde01ebdb43bac7afb8142c32dd2aecff8245800435202270eaac`
- 71002 `8de8516dd6802106d4cf7fe36745a8636e888d9c5c711d76c7870fc2582f64b3`
- 71003 `3e5eb4ba3dbb297ce2176361544773db54ca8a1c3e3ddb89aa1367049bd18077`
- 71004 `e4839585f54ad14f02bd8c029d3461b6cb25063f044408cc5eeee08a8d064c5e`
- 71005 `52b5ce49529db34761d093cc8aa5c0a04ae19e6224e5d80e8bcf998f8dc435d9`

## 3. Exact execution implementation bindings

| Path | Git blob | SHA-256 |
|---|---|---|
| `model_kernel/mk1/SCIENTIFIC_TRAINING_EXECUTION_ENFORCEMENT_SPEC.md` | `57d8a6a95ae5fd1fdd15ed74feec293a13aebea1` | `e75a6b78efa03b44e9a33b0023d68af4d0c71c3273f5b8e11bacff201850fbc8` |
| `model_kernel/mk1/TRAINING_BUNDLE_RESULT.md` | `40ac9be84c8b18eaeaa26252c6c4be955274f749` | `cd26575107f20b8cf711ebd5b4b2647d98fcbefa1f980badf16333b57cdc26ac` |
| `experiments/model_core/mk1/trainer.py` | `a6add27a9751b4d34ca54eb81f54b0e3ac32bb18` | `15b48da5ecd88f857afd12cd8103af9f90ba532122d90d6c5588d65953deffad` |
| `experiments/model_core/mk1/training_execution.py` | `1b0fc2baab1b19bc7812fc453006d89f2bca7aa6` | `c651a90f6c7e5c104d4f65d51580ce2367524184db8c9ae552050e975840720d` |
| `tests/test_model_core_mk1_training_execution.py` | `03913f769ea5db4302684460a5c1393aa391d9ab` | `c3949e2900d2a09a7bc5f30633b9afbe71bb5d8e8a57afdc7d1de7c2348cfef0` |
| `.github/workflows/mk1-scientific-training.yml` | `c2fe4076c237002c7da54b0099d93906370455e6` | `cd40f59d79b0f946f05968aecd6a5a3bb23118b0e30762e4fa875c91d318e39d` |

## 4. Frozen scientific dependency bindings

| Path | Git blob | SHA-256 |
|---|---|---|
| `experiments/model_core/mk1/contracts.py` | `cb9d8c067586dfc52b8b23cac7b88868b7498a9f` | `4ece6dd85d2fea2a5c46d6e6058f71ca7ffeaebadaee1a5bf462fae1f1816e7c` |
| `experiments/model_core/mk1/modeling.py` | `f6f79e044a7787d604b46b41a0c68b423cc600ab` | `37f27824b29167b1320fa363ff035a7b4637253c20d0caedff9381c0aea073a7` |
| `experiments/model_core/mk1/losses.py` | `c1f3106417ab1d3e03b7a6961b6a5439cbba83d9` | `1abb1e83acf551f792b9807336429027a867c67a53afdb1fde1395bc1c7b72a2` |
| `experiments/model_core/mk1/metrics.py` | `22e97e9ad29f3b483b8f100a363a934dc7612e1b` | `ce55ecbe4db075ac6e20d39c8aa38e5ea8cdc2b0913112eb65f3660edb02f1b2` |
| `experiments/model_core/mk1/recompose.py` | `5e1ce91c4e6c176f7b6392adc35d96b36851219a` | `c307c8fc883e0e33fbfb580eafbe6df5a1faa0bdb09df6ad7843eda42674cf5c` |
| `mindforge/config.py` | `91a3f92ea2449a82fb2d03e0442cbf6e72980caf` | `95e784b83bab57e0618aa52e0c826204609c1ae2d80a6ab47f4cf2b4c4d96169` |
| `mindforge/model.py` | `b585945631a027fb1f124c780fc5f7fd330c0287` | `7562951b9a62e99ecc2c275061662911e339c95b9913c627b9f74dfcc2974a22` |
| `mindforge/device.py` | `29dde1a34753444837e7b0a1f146947fee038e0b` | `e6ff1b87824f3d56fe4d06f1df9437351f872483d101d0d5624fec5e5a08dd1f` |
| `mindforge/tokenizer.py` | `68c7d687c684c800c98344e26be7c75425ea528f` | `3315abd29e7ff086df1a67db5f15f2ae161a2f7d7e9b58913f14572fcc2c8c6e` |
| `mindforge/train.py` | `f9e9e0839979bd25cac6b0cc9d356dbea5868127` | `7b6bedb17ea7906ef06b825efd789a5d662cc2bf067f37a262c1a8063cfebac6` |

## 5. Arm parameter contracts

Frozen:

- B0: `10,339,200`
- DIRECT: `10,350,114`
- M1-Z: `10,361,670`

For each seed, both arms load the exact same paired B0 state hash from section 2.

Both arm readouts begin all-zero.

## 6. Frozen optimization contract

From `TRAINING_LOCK` and `train_arm`:

- optimizer: AdamW
- learning rate: `3e-4`
- weight decay: `0.1`
- gradient clip: `1.0`
- optimizer steps: `5000`
- micro-batch: `1`
- accumulation: `8`
- effective examples per optimizer step: `8`
- warmup fraction: `0.05`
- cosine decay through `mindforge.train.learning_rate_multiplier`
- minimum LR fraction: `0.1`
- max context: `512`
- dtype: float32
- device: auto
- no early stopping.

The learning-rate helper is frozen as:

- linear warmup for `max(1, int(steps * warmup_fraction))`;
- cosine decay after warmup;
- floor set by `min_lr_fraction`.

## 7. Frozen schedule consumption

Fresh scientific training no longer reconstructs the schedule from RNG.

`train_arm` requires:

- `schedule_path`
- `expected_schedule_sha256`

and calls `load_frozen_schedule`.

The scientific `train_arm` function contains zero calls to:

`deterministic_sample_indices`.

Before optimizer execution it verifies:

- exact schedule SHA-256;
- exactly 5,000 rows;
- exact sequential step numbers;
- exactly eight sample keys and token counts per row;
- every key exists in frozen TRAIN;
- per-step frozen token totals.

During execution every encoded sample token count must equal the frozen schedule token count.

## 8. Frozen validation / checkpoint selector

VALIDATION is the only held-out split accessible to training.

Evaluation occurs exactly when:

`completed % TRAINING_LOCK.validation_interval == 0`

with interval `250`.

The full frozen VALIDATION surface set is evaluated.

Canonical-C balanced score is used for both arms:

- DIRECT: decoded direct C;
- M1-Z: parameter-free R(Z).

Best checkpoint update is strictly:

`if score > best_score`

Therefore an exact tie retains the earlier checkpoint.

Training loop has no early-stop/break condition and always targets 5,000 steps.

## 9. Static workflow capability QA

Candidate workflow:

`.github/workflows/mk1-scientific-training.yml`

Observed static QA:

- training trigger file exists: **false**
- matrix entries: `10`
- DIRECT entries: `5`
- M1-Z entries: `5`
- bundle artifact `10629399106`: hard-bound
- bundle run `35581007427`: hard-bound
- upstream materialization artifact ID occurrences: `0`
- upstream tokenizer artifact ID occurrences: `0`
- upstream paired-init/schedule artifact ID occurrences: `0`
- case-insensitive forbidden confirmatory-path term occurrences: `0`
- data-generator invocation terms: `0`
- tokenizer-fit invocation terms: `0`
- paired-init generation invocation terms: `0`
- schedule-RNG invocation terms: `0`

Every matrix entry hard-binds the matching seed-specific paired-init file SHA and schedule SHA.

The workflow downloads only the immutable training-input bundle.

## 10. Static wrapper QA

`training_execution.py`:

- regeneration-function terms: `0`
- calls `train_arm`: exactly `1`
- direct upstream artifact IDs: `0`
- verifies exact bundle file set and all file SHA-256 values;
- verifies paired-init file SHA and B0 state SHA;
- verifies seed-specific schedule SHA;
- requires completed processed-token total = `6,457,260`.

## 11. Confirmatory isolation

The candidate scientific training workflow has no path, argument, artifact ID, or file name for the confirmatory split.

The immutable training bundle itself contains only:

- TRAIN;
- VALIDATION;
- tokenizer;
- five paired initializations;
- five schedules;
- manifest.

Therefore confirmatory isolation is an execution-capability property.

## 12. Authorization state

This candidate lock does not yet authorize training.

Independent final review must prove after this commit:

1. this commit changed only the lock document;
2. all section-3 and section-4 Git blob/SHA-256 bindings still match;
3. scientific training trigger still does not exist;
4. workflow static QA in section 9 still holds;
5. wrapper/trainer static QA in sections 7 and 10 still holds;
6. bundle artifact/run/digest still match GitHub artifact metadata.

Only then may status become:

`MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK_PASS`

Even after PASS, no optimizer step occurs unless a separate explicit scientific-training trigger is created.
