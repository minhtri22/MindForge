# MK-1 Paired Initialization and Exact Sample/Token Budget Audit Result v0.1

Status: **PASS / SCIENTIFIC INITIALIZATIONS AND SCHEDULES FROZEN**

Date: **2026-09-21**

Formal verdict:

`PAIRED_INIT_AND_TOKEN_BUDGET_PASS`

## 1. Canonical execution

Workflow:

`.github/workflows/mk1-pretraining-audit.yml`

Run:

`35572770344`

Execution head:

`dccccbf9eebccde581bd92031650a4b88c39a795`

Fixture-only implementation QA:

`2 passed in 2.35s`

## 2. Canonical evidence artifact

- artifact name: `mk1-paired-init-token-budget-v0-1`
- artifact id: `10626846126`
- artifact ZIP SHA-256: `01579c6643003aab615dfd9c530f5c1a0868250072f7e922e8aa90968af88ff3`
- size: `192001281` bytes

The artifact contains five paired initialization files, five exact schedule JSONL files, and `PAIRED_INIT_AND_TOKEN_BUDGET_RESULT.json`.

## 3. Frozen upstream provenance

Scientific materialization:

- run: `35553551910`
- artifact id: `10619711251`
- ZIP SHA-256: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Scientific tokenizer:

- run: `35562370974`
- artifact id: `10622602143`
- ZIP SHA-256: `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Frozen TRAIN identities:

- source SHA-256: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- tokenizer SHA-256: `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`
- tokenized TRAIN manifest SHA-256: `7be5c48156329e2239ac7345845f705a9b934d7bcc7e940e7dd128c0603a934e`

## 4. Exact TRAIN-index alignment

Observed:

- surface records: `4000`
- index alignment: `EXACT`
- exact token IDs re-encoded: true
- one-pass tokens: `645726`
- maximum token id: `3260`

Result:

**PASS**

The frozen tokenized manifest therefore has the same row-index semantics as the existing trainer's sorted TRAIN records.

## 5. Scientific seeds and paired initializations

Exactly:

`71001, 71002, 71003, 71004, 71005`

No replacement seed was used.

| Seed | Paired-init file SHA-256 | B0 state/backbone SHA-256 |
|---:|---|---|
| 71001 | `b74b7ab8a67a11c076a94f9df5325a616231acdb99639c3a94424d65382dd8e8` | `c8a7fbf63e0df8a827ff7c9291d4955db9a59b14ad1d28387fffa00e0b7a2ad7` |
| 71002 | `7b2dcc6ab1cd377fedc6a0eb32809719fcac911cfb4cbd235684f9b4f10b621e` | `04cd00ce71965649281c618212c120c165d6283519eab2d9f13beb22110f674d` |
| 71003 | `774ad2e2e5f0dddac8bfd67ee04537854309c983043314c82d5841e7a82ca860` | `f3ffadfa63e011bf691ac2e0f86a67eb023606d19a875104b77ea40d35577beb` |
| 71004 | `25a96874e33828d9e9dd5de85a98a12028632d138c40c6f3a70760e0ff0b3d32` | `2f1d93bf7119ffb67c939e3c6235054232854d59ab4151e5b95ae6e2828d931d` |
| 71005 | `76c427debc7e68012fe5be6b5bf409c8ac49fff9bc2346e6b022befdf37c3730` | `e553c8aa984a7b7040e392776f5a35aa6925658dbb932bc5777a0e5f35d326ab` |

For every seed:

- DIRECT backbone SHA-256 == paired B0 state SHA-256;
- M1-Z backbone SHA-256 == paired B0 state SHA-256;
- DIRECT readout all-zero: true;
- M1-Z readout all-zero: true;
- DIRECT parameters: `10,350,114`;
- M1-Z parameters: `10,361,670`.

Result:

**PASS**

These five scientific initialization states are now frozen and must not be regenerated/replaced merely because later outcomes are unfavorable.

## 6. Exact deterministic schedules

| Seed | Schedule SHA-256 |
|---:|---|
| 71001 | `18262d3bec5fde01ebdb43bac7afb8142c32dd2aecff8245800435202270eaac` |
| 71002 | `8de8516dd6802106d4cf7fe36745a8636e888d9c5c711d76c7870fc2582f64b3` |
| 71003 | `3e5eb4ba3dbb297ce2176361544773db54ca8a1c3e3ddb89aa1367049bd18077` |
| 71004 | `e4839585f54ad14f02bd8c029d3461b6cb25063f044408cc5eeee08a8d064c5e` |
| 71005 | `52b5ce49529db34761d093cc8aa5c0a04ae19e6224e5d80e8bcf998f8dc435d9` |

Schedule-hash collisions across the five seeds:

`0`

For every seed:

- steps: `5000`
- accumulation: `8`
- scheduled samples: `40000`
- unique TRAIN sample keys: `4000`
- minimum multiplicity: `10`
- maximum multiplicity: `10`
- DIRECT schedule bytes == M1-Z schedule bytes: true
- DIRECT schedule SHA == M1-Z schedule SHA: true

Result:

**PASS**

## 7. Exact token-budget matching

One complete frozen TRAIN pass:

`645726` tokens

Ten complete cycles:

`6457260` tokens

For every seed:

- DIRECT total tokens: `6457260`
- M1-Z total tokens: `6457260`
- absolute token gap: `0`
- relative token gap: `0.0`

This is stricter than the frozen <=1% compute-matching allowance.

Result:

**PASS**

## 8. Execution boundary

Canonical result records:

- optimizer constructed: false
- model forward executed: false
- model backward executed: false
- training executed: false
- validation model outcome used: false
- pristine-confirmatory model inference: false

Result:

**PASS**

This gate instantiated scientific model weights but did not produce any model-performance outcome.

## 9. Scientific interpretation

Supported:

- exact same B0 initialization is available to DIRECT and M1-Z for each scientific seed;
- zero-readout symmetry holds;
- exact training sample order is frozen for each seed;
- exact token budget is identical across paired arms;
- frozen tokenizer/data index semantics match the existing trainer.

Not supported:

- learnability of Z;
- H1a;
- H1b;
- H1c;
- validation performance;
- confirmatory performance.

## 10. Authorization after PASS

All pre-training evidence gates are now satisfied.

The next required stage is not immediate optimizer execution. It is a separate explicit:

`MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK`

That lock must bind, without scientific changes:

- artifact `10626846126` and all five paired-init file/state hashes;
- all five schedule hashes;
- tokenizer artifact `10622602143`;
- materialization artifact `10619711251`;
- exact frozen trainer implementation;
- exact optimizer/schedule/checkpoint-selection rules;
- full VALIDATION use only at frozen intervals;
- zero PRISTINE_CONFIRMATORY access during training/checkpoint selection;
- a training workflow that cannot regenerate initializations, schedules, data, or tokenizer.

Only after that lock receives independent PASS may optimizer step 1 be authorized.
