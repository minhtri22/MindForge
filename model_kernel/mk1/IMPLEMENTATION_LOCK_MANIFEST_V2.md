# MK-1 Implementation Lock Manifest V2

Status: **PENDING INDEPENDENT STATIC REVIEW / ZERO-FRESH V0.2 NOT AUTHORIZED YET**

Date: **2026-09-21**

Implementation source HEAD before this manifest:

`0792ed3dc8c0695f855e60db4d7508b7e5b53e25`

Formal candidate state:

`MK1_IMPLEMENTATION_V2_HASH_BOUND_PENDING_REVIEW`

## 1. Scientific boundary

This V2 lock is prospective to the first scientific data materialization.

At this point:

- reserved scientific scene namespaces have not been materialized;
- the scientific tokenizer has not been fitted;
- scientific training seeds have not been used for training;
- no MK-1 neural scientific training has occurred;
- no validation/pristine model outcome exists.

V1 manifest/result remain historical implementation evidence and are not rewritten.

## 2. Governing prospective corrections

Amendment 003:

- Git blob: `37ca2a2d12f0e385566113ce66f07cc058e0b0c3`
- SHA-256: `4c0ddb6494a85d327f5e7f47c66dd0ceefc99c1b449133e0b50872f8181e490f`

Observable field registry:

- Git blob: `2384169ab0af09b9a33283fd251ac820cd81d052`
- SHA-256: `437ae40a58cf9c02036a35829c3551b2ee305837a35240d4ae5e359af58ff8dd`

Current implementation-lock specification:

- Git blob: `bc3dbfb4f2ddad425643b28a45073d620b2c6ec7`
- SHA-256: `84f7828ee1fdf37b00c3db6bd1221a305f0cb8e56d088cc2c7edd3406e30b805`

## 3. Complete implementation binding

| Path | Git blob | SHA-256 |
|---|---|---|
| `mindforge/model.py` | `b585945631a027fb1f124c780fc5f7fd330c0287` | `7562951b9a62e99ecc2c275061662911e339c95b9913c627b9f74dfcc2974a22` |
| `experiments/model_core/mk1/__init__.py` | `2b9cbb4ca4660e46693c18483693be070a68399b` | `d249266caefa54b8c6b987d0ab90d2353c354c8c94d08fb6f10d719b936cba78` |
| `experiments/model_core/mk1/contracts.py` | `cb9d8c067586dfc52b8b23cac7b88868b7498a9f` | `4ece6dd85d2fea2a5c46d6e6058f71ca7ffeaebadaee1a5bf462fae1f1816e7c` |
| `experiments/model_core/mk1/modeling.py` | `f6f79e044a7787d604b46b41a0c68b423cc600ab` | `37f27824b29167b1320fa363ff035a7b4637253c20d0caedff9381c0aea073a7` |
| `experiments/model_core/mk1/losses.py` | `c1f3106417ab1d3e03b7a6961b6a5439cbba83d9` | `1abb1e83acf551f792b9807336429027a867c67a53afdb1fde1395bc1c7b72a2` |
| `experiments/model_core/mk1/recompose.py` | `5e1ce91c4e6c176f7b6392adc35d96b36851219a` | `c307c8fc883e0e33fbfb580eafbe6df5a1faa0bdb09df6ad7843eda42674cf5c` |
| `experiments/model_core/mk1/data_contract.py` | `2c396bfea3740fc88418b01e0a405fb7730c1557` | `551d6decd85ef21e3f5d0d600f38a00fe740eb9b1cf0c94c8301d18c45b0b033` |
| `experiments/model_core/mk1/trainer.py` | `195cbecef37e091e61e20a2020ba9a90ed7ce2a0` | `5c705878efbc1604d4faaa10242aab32833196dcb7f2e35dd95abc07aedd7f1b` |
| `experiments/model_core/mk1/metrics.py` | `22e97e9ad29f3b483b8f100a363a934dc7612e1b` | `ce55ecbe4db075ac6e20d39c8aa38e5ea8cdc2b0913112eb65f3660edb02f1b2` |
| `experiments/model_core/mk1/preflight.py` | `24f708c1775145559d4c730cb47af500937ccf8c` | `dd6bcf5e2c21efbd6f64b474d18661424079987e6045ca874506b910a20931be` |
| `tests/test_model_core_mk1_preflight.py` | `d729bbf17477098515a96b3990715e0e7600c936` | `512353c92368b7cccdaadc32fabb553ee131b2e80dbf68d5a30f57dc54b3a874` |
| `.github/workflows/mk1-zero-fresh-preflight.yml` | `3a21d834057c1c8d471677ad550b493aea61a6ba` | `62fb1c339052281116967bd894d5ca70f512e81f12750802fb1597253e74fb93` |
| `.github/workflows/mk1-materialization-audit.yml` | `f25733b89ad3b66ae1ff67351affa2f03084fdd7` | `e93957b3c68573b687ef9135fdb596bf86fc09ee3e0f65b16e18dd5fe3722d6e` |

## 4. Frozen unchanged runtime dependencies

| Path | Git blob | SHA-256 |
|---|---|---|
| `mindforge/config.py` | `91a3f92ea2449a82fb2d03e0442cbf6e72980caf` | `95e784b83bab57e0618aa52e0c826204609c1ae2d80a6ab47f4cf2b4c4d96169` |
| `mindforge/tokenizer.py` | `68c7d687c684c800c98344e26be7c75425ea528f` | `3315abd29e7ff086df1a67db5f15f2ae161a2f7d7e9b58913f14572fcc2c8c6e` |
| `mindforge/train.py` | `f9e9e0839979bd25cac6b0cc9d356dbea5868127` | `7b6bedb17ea7906ef06b825efd789a5d662cc2bf067f37a262c1a8063cfebac6` |
| `mindforge/device.py` | `29dde1a34753444837e7b0a1f146947fee038e0b` | `e6ff1b87824f3d56fe4d06f1df9437351f872483d101d0d5624fec5e5a08dd1f` |
| `mindforge/model_contract.py` | `b4e6cd04fb84f31c839ada199aa50ac1ca48f0f2` | `d651b304366dcc9c6e512e9e77cb6881a0e8613c861e532997bcda99aa919545` |
| `tests/test_mks_model_kernel.py` | `969200c2c5fe555b3746be0ca0bc8a29111cd7e5` | `9b075dcc9ef5e6fe9717de4278d3eecf1e482e203d317b9a094c3cce16178de9` |

## 5. Amendment-003 implementation intent

V2 changes are limited to pre-materialization integrity:

- one global ordinal across the three reserved splits;
- complete prospective target-class schedules;
- reachable conflict+resolution state;
- all four MK-1 scope-relation classes;
- injective bounded scalar schedule across 3,000 prospective ordinals;
- PIT-v3 contextual scope-relation exclusion from H1c relation scoring;
- fixture-only projected support/integrity QA;
- independent observable-text reconstruction for later materialized Z/C audit;
- one-shot materialization/audit execution mode;
- separate one-shot materialization workflow.

No B0 architecture, representation-head dimensions, loss family, optimizer schedule, scientific training seed, training step count, H1a/H1b acceptance threshold, or D-PIT runtime is changed.

## 6. Static scope review

Relative to canonical zero-fresh v0.1 execution head:

`22d8c7cf813f114a3573adad5a358e4a926fb0d9`

the repository contains only:

- Amendment-003 governance/evidence documentation;
- observable field registry;
- the implementation files listed above;
- the new gated materialization workflow;
- append-only lineage/result documentation from the completed v0.1 gate.

There is still no materialized scientific data file.

## 7. V2 authorization sequence

Independent static review must prove all hashes in sections 2–4 and no unauthorized source path change.

Only after that may status become:

`IMPLEMENTATION_LOCK_MANIFEST_V2_PASS`

Then the only authorized execution is:

`CANONICAL_ZERO_FRESH_PREFLIGHT_V0_2`

The scientific materialization trigger remains forbidden until a separate v0.2 zero-fresh PASS result is committed.
