# MK-1 Training Input Bundle Result v0.1

Status: **PASS / IMMUTABLE TRAINING-ONLY BUNDLE FROZEN**

Date: **2026-09-21**

Formal verdict:

`TRAINING_INPUT_BUNDLE_PASS`

## Canonical execution

- run: `35581007427`
- head: `362836e664a6074f37fc51763c5bf1c406db8065`
- artifact: `10629399106`
- artifact name: `mk1-training-input-bundle-v0-1`
- ZIP SHA-256: `56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af`
- size: `192746933` bytes
- uploaded files: `14`

## Exact bundle contents

Frozen scientific inputs:

- `train.jsonl`
- `validation.jsonl`
- `mk1-tokenizer.json`
- `paired_init_seed_71001.pt`
- `paired_init_seed_71002.pt`
- `paired_init_seed_71003.pt`
- `paired_init_seed_71004.pt`
- `paired_init_seed_71005.pt`
- `schedule_seed_71001.jsonl`
- `schedule_seed_71002.jsonl`
- `schedule_seed_71003.jsonl`
- `schedule_seed_71004.jsonl`
- `schedule_seed_71005.jsonl`

Plus:

- `TRAINING_BUNDLE_MANIFEST.json`

No other file is admitted.

## Frozen hashes

- TRAIN: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- VALIDATION: `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`
- tokenizer: `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

Paired init:

- 71001 `b74b7ab8a67a11c076a94f9df5325a616231acdb99639c3a94424d65382dd8e8`
- 71002 `7b2dcc6ab1cd377fedc6a0eb32809719fcac911cfb4cbd235684f9b4f10b621e`
- 71003 `774ad2e2e5f0dddac8bfd67ee04537854309c983043314c82d5841e7a82ca860`
- 71004 `25a96874e33828d9e9dd5de85a98a12028632d138c40c6f3a70760e0ff0b3d32`
- 71005 `76c427debc7e68012fe5be6b5bf409c8ac49fff9bc2346e6b022befdf37c3730`

Schedules:

- 71001 `18262d3bec5fde01ebdb43bac7afb8142c32dd2aecff8245800435202270eaac`
- 71002 `8de8516dd6802106d4cf7fe36745a8636e888d9c5c711d76c7870fc2582f64b3`
- 71003 `3e5eb4ba3dbb297ce2176361544773db54ca8a1c3e3ddb89aa1367049bd18077`
- 71004 `e4839585f54ad14f02bd8c029d3461b6cb25063f044408cc5eeee08a8d064c5e`
- 71005 `52b5ce49529db34761d093cc8aa5c0a04ae19e6224e5d80e8bcf998f8dc435d9`

## Scientific boundary

Bundle construction:

- copied and hash-verified existing frozen bytes only;
- did not regenerate data;
- did not fit tokenizer;
- did not instantiate model weights;
- did not regenerate paired initializations;
- did not regenerate schedules;
- did not construct an optimizer;
- did not execute model forward/backward;
- did not execute scientific training.

The bundle intentionally excludes confirmatory data and confirmatory tokenized inputs.

## Consequence

The candidate scientific training workflow must download only artifact `10629399106` by exact run/artifact/digest.

It must not download the three upstream artifacts directly.

Scientific training remains forbidden until the final execution lock passes independent static QA.
