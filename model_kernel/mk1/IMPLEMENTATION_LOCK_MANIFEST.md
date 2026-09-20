# MK-1 Implementation Lock Manifest v0.1

Status: **PENDING INDEPENDENT STATIC REVIEW / ZERO-FRESH NOT AUTHORIZED YET**

Date: **2026-09-21**

Implementation source HEAD before this manifest:

`4df8742a552345c49c8f651b4d545cbd11591d67`

Formal candidate state:

`MK1_IMPLEMENTATION_HASH_BOUND_PENDING_REVIEW`

## 1. Scope

This manifest binds the complete MK-1 implementation candidate before canonical zero-fresh execution.

No scientific data have been materialized.

No scientific tokenizer has been fitted.

No scientific training seed has been instantiated for training.

No MK-1 neural scientific training has occurred.

## 2. Governing implementation lock

Current IMPLEMENTATION_LOCK_SPEC.md:

- Git blob: `82a8eef1c5b86fd6591e2f680302d763db87afb5`
- SHA-256: `97714c1111b1d69945666945e64141fe8d11afbf203cc54e9b16b467a79e1835`

The pre-manifest H1c clarification froze an exact PIT-v3 common-field mapping and H1c bootstrap seed before scientific model outcomes. It did not inspect any scientific result.

## 3. Exact implementation binding

| Path | Git blob | SHA-256 |
|---|---|---|
| `mindforge/model.py` | `b585945631a027fb1f124c780fc5f7fd330c0287` | `7562951b9a62e99ecc2c275061662911e339c95b9913c627b9f74dfcc2974a22` |
| `experiments/model_core/mk1/__init__.py` | `2b9cbb4ca4660e46693c18483693be070a68399b` | `d249266caefa54b8c6b987d0ab90d2353c354c8c94d08fb6f10d719b936cba78` |
| `experiments/model_core/mk1/contracts.py` | `cb9d8c067586dfc52b8b23cac7b88868b7498a9f` | `4ece6dd85d2fea2a5c46d6e6058f71ca7ffeaebadaee1a5bf462fae1f1816e7c` |
| `experiments/model_core/mk1/modeling.py` | `f6f79e044a7787d604b46b41a0c68b423cc600ab` | `37f27824b29167b1320fa363ff035a7b4637253c20d0caedff9381c0aea073a7` |
| `experiments/model_core/mk1/losses.py` | `c1f3106417ab1d3e03b7a6961b6a5439cbba83d9` | `1abb1e83acf551f792b9807336429027a867c67a53afdb1fde1395bc1c7b72a2` |
| `experiments/model_core/mk1/recompose.py` | `5e1ce91c4e6c176f7b6392adc35d96b36851219a` | `c307c8fc883e0e33fbfb580eafbe6df5a1faa0bdb09df6ad7843eda42674cf5c` |
| `experiments/model_core/mk1/data_contract.py` | `4f1df6c7003033dada47acde5d53e5992e37e2c7` | `d7bfe52497122960383db1faa6a07a82e543c7e8f0c937ab505f27bf2c3f63ff` |
| `experiments/model_core/mk1/trainer.py` | `195cbecef37e091e61e20a2020ba9a90ed7ce2a0` | `5c705878efbc1604d4faaa10242aab32833196dcb7f2e35dd95abc07aedd7f1b` |
| `experiments/model_core/mk1/metrics.py` | `1cef3437ec47e6278ea0c18e9a021d99dc2f919d` | `ceeabec8c7819acd4472c35437c1abe09588e9da4d94da9fe8e5786dfa6cf737` |
| `experiments/model_core/mk1/preflight.py` | `28114012ab87bef76e8e0b236eb87d37da8d352d` | `868a3205c20d54fd123522d5076cad9ecc51d0a06ed213c679706271717cd3ee` |
| `tests/test_model_core_mk1_preflight.py` | `02b79405bd27ebbe5081fe426a793615713cb8b6` | `db5f45a816413e2d8c278ad8685da5880e9ab5c3a39a530a6a82feff57c0c534` |
| `.github/workflows/mk1-zero-fresh-preflight.yml` | `82048174ed43911f6a291f7c87a6bb86a70d6007` | `ce6566beb8aea3e9d0cca8fd976d0d1e0c50266ec49f1a7084e4418e1d103289` |

## 4. Frozen unchanged runtime dependencies

| Path | Git blob | SHA-256 |
|---|---|---|
| `mindforge/config.py` | `91a3f92ea2449a82fb2d03e0442cbf6e72980caf` | `95e784b83bab57e0618aa52e0c826204609c1ae2d80a6ab47f4cf2b4c4d96169` |
| `mindforge/tokenizer.py` | `68c7d687c684c800c98344e26be7c75425ea528f` | `3315abd29e7ff086df1a67db5f15f2ae161a2f7d7e9b58913f14572fcc2c8c6e` |
| `mindforge/train.py` | `f9e9e0839979bd25cac6b0cc9d356dbea5868127` | `7b6bedb17ea7906ef06b825efd789a5d662cc2bf067f37a262c1a8063cfebac6` |
| `mindforge/device.py` | `29dde1a34753444837e7b0a1f146947fee038e0b` | `e6ff1b87824f3d56fe4d06f1df9437351f872483d101d0d5624fec5e5a08dd1f` |
| `mindforge/model_contract.py` | `b4e6cd04fb84f31c839ada199aa50ac1ca48f0f2` | `d651b304366dcc9c6e512e9e77cb6881a0e8613c861e532997bcda99aa919545` |
| `tests/test_mks_model_kernel.py` | `969200c2c5fe555b3746be0ca0bc8a29111cd7e5` | `9b075dcc9ef5e6fe9717de4278d3eecf1e482e203d317b9a094c3cce16178de9` |

## 5. Static scope result before manifest

Compared with initial implementation-lock-spec commit:

`f3aac3a87327d51320e1b56d8c7b246a889ac013`

the implementation source HEAD changes only:

- the twelve implementation paths in section 3;
- IMPLEMENTATION_LOCK_SPEC.md for the pre-manifest H1c clarification.

There are:

- zero scientific-data changes outside `experiments/model_core/mk1/`;
- zero changes to other `mindforge/` production files;
- zero changes to model width/depth/normalization/attention/MLP/token embedding/position embedding/LM-head tying.

## 6. Implementation mapping frozen

The bound code implements:

- B0 hidden-state exposure with unchanged LM-logit path;
- B0-DIRECT 320 -> 34, zero-initialized;
- M1-Z 320 -> 70, zero-initialized;
- exact Z/C tensor slices;
- exact factor losses;
- deterministic parameter-free R;
- deterministic canonical-scene generator;
- no exact target-name leakage in rendered neural surfaces;
- shared PIT-compatible structured view generated from the same scene text;
- deterministic paired sample schedule;
- paired initialization helper;
- full 5,000-step locked trainer;
- exact processed-input-token accounting;
- common canonical-C checkpoint selection;
- H1a metric bundle;
- H1b whole-scene paired bootstrap;
- H1c exact PIT common-field mapping and whole-scene bootstrap;
- synthetic-only zero-fresh preflight.

## 7. Invalid pre-lock workflow executions

The workflow initially contained a push trigger and GitHub automatically started pre-manifest runs.

Known run IDs include:

- `35528445838`
- `35528568383`
- `35528581759`
- `35528608614`
- `35528655281`
- `35528657593`

These executions occurred before this manifest and are **INVALID AS IMPLEMENTATION-LOCK EVIDENCE**, regardless of conclusion.

No result from those runs was used to tune:

- target schema;
- model architecture;
- loss;
- metric threshold;
- scientific seed;
- data namespace.

The workflow was changed to manual-only at:

`4df8742a552345c49c8f651b4d545cbd11591d67`

Canonical zero-fresh execution is forbidden until this manifest receives independent static PASS.

## 8. Manifest review gates

Independent static review must prove:

1. all section-3 blobs match HEAD;
2. all section-3 SHA-256 values match file bytes;
3. all section-4 dependency bindings still match;
4. no implementation path outside the allowlist changed;
5. no scientific data file was created;
6. workflow is manual-only;
7. no scientific run/seed/result is needed to establish the review.

Only then may status become:

`IMPLEMENTATION_LOCK_MANIFEST_PASS`

and canonical ZERO-FRESH PREFLIGHT may be manually dispatched.
