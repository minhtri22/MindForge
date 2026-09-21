# MK-1 Tokenizer Freeze Implementation Lock v0.1

Status: **PASS / TOKENIZER FREEZE IMPLEMENTATION HASH LOCKED / REPLACEMENT FIT AUTHORIZED**

Date: **2026-09-21**

Source HEAD before this lock:

`9459429b122f165bccf6902e3f001866d1dff73f`

Candidate state:

`TOKENIZER_FREEZE_IMPLEMENTATION_LOCK_PASS`

## 1. Bound specification and evidence

| Path | Git blob | SHA-256 |
|---|---|---|
| `model_kernel/mk1/TOKENIZER_FREEZE_SPEC.md` | `74df8e6b9f2ee3a3985c5a003a1573e17390feae` | `fa9d5110e7d65df42b8fdf4e77308e27c4361c5fa000200226eaeff8a98b81ec` |
| `experiments/model_core/mk1/tokenizer_freeze.py` | `ac9456d80935133cae27ebe91fed886479d8501b` | `42d5556d1bc40638abb6058fcad11a79cdd699d3c2ccc91ed84bcd17a5efa9aa` |
| `.github/workflows/mk1-tokenizer-freeze.yml` | `2ff7db93aaba9e8059ccc6a0f3c2120e3baeddae` | `391889ccbe6a384f38b268a03c65385995dd18158412ad4306b9fa734935b7a0` |
| `mindforge/tokenizer.py` | `68c7d687c684c800c98344e26be7c75425ea528f` | `3315abd29e7ff086df1a67db5f15f2ae161a2f7d7e9b58913f14572fcc2c8c6e` |
| `model_kernel/mk1/MATERIALIZATION_AND_DATA_AUDIT_RESULT.md` | `1c12495fabdc1429416b000b6f7c87034bc4eebe` | `0fd89e02b47bf69fb05aa749abb00679d3448270b3a4d994c84d86c088a9c093` |

## 2. Frozen source artifact identity

- repository: `minhtri22/MindForge`
- source run: `35553551910`
- artifact id: `10619711251`
- artifact ZIP SHA-256: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Split hashes remain exactly:

- TRAIN: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- VALIDATION: `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`
- PRISTINE_CONFIRMATORY: `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`

No generator invocation is present in the tokenizer workflow or runner.

## 3. Frozen execution order

The bound runner enforces:

1. verify all three split file hashes and counts;
2. parse TRAIN only;
3. create `TRAIN[*].input_text` corpus;
4. fit exactly one tokenizer;
5. save tokenizer JSON;
6. compute tokenizer SHA-256;
7. validate tokenizer metadata;
8. only then parse VALIDATION and PRISTINE_CONFIRMATORY;
9. encode and freeze exact token IDs for all three splits;
10. adjudicate vocabulary/token-ID/context gates.

This ordering is part of the lock.

## 4. Frozen tokenizer procedure

The unchanged `mindforge/tokenizer.py` provides:

- BPE;
- NFC;
- ByteLevel pre-tokenizer;
- ByteLevel decoder;
- `<|endoftext|>`;
- `<|unk|>`;
- requested maximum vocabulary 16,384.

No artificial token padding is authorized.

## 5. Frozen tokenized-manifest representation

For every surface:

- scene ID;
- renderer family;
- split;
- input-text SHA-256;
- exact token ID list;
- exact token count;
- SHA-256 of token IDs serialized as little-endian unsigned 32-bit integers.

Rows are sorted by:

`(scene_id, renderer_family)`.

The three tokenized JSONL files are intended to become authoritative inputs for the later sample-order/token-budget audit.

## 6. Workflow boundary

The workflow can run only from:

`model_kernel/mk1/TOKENIZER_FREEZE_TRIGGER_v0.1.md`

and requires:

- `TOKENIZER_FREEZE_IMPLEMENTATION_LOCK_PASS`;
- `SCIENTIFIC_MATERIALIZATION_AND_DATA_AUDIT_PASS`;
- `TRIGGER_TRAIN_ONLY_TOKENIZER_FREEZE_v0.1`.

The workflow has read-only contents/actions permissions.

It downloads the exact prior artifact by artifact ID + run ID and requests download-artifact digest mismatch failure.

## 7. Explicitly absent operations

The runner/workflow contain no authorization for:

- scientific model seeds `71001..71005`;
- model construction;
- model forward/backward;
- optimizer construction;
- scientific training;
- validation model evaluation;
- pristine-confirmatory model inference;
- dataset regeneration.

## 8. Independent review gates

Before PASS, review must establish:

1. all five bindings in section 1 match HEAD exactly;
2. no tokenizer trigger exists yet;
3. workflow listens only to the tokenizer trigger path;
4. runner source contains the TRAIN-only freeze barrier;
5. `mindforge/tokenizer.py` is unchanged;
6. source artifact/run/split identities match the formal data-audit closure.

Only then may status become:

`TOKENIZER_FREEZE_IMPLEMENTATION_LOCK_PASS`

and exactly one scientific tokenizer-fit run may be triggered.


## 9. Independent review closure

Independent review after candidate-lock creation established:

- candidate-lock commit changed only this lock document;
- tokenizer trigger did not exist during review;
- workflow blob remained `fc7b5c310a6e6b37fa45e84ca0eddc044f8d778b`;
- runner blob remained `ac9456d80935133cae27ebe91fed886479d8501b`;
- workflow references the tokenizer trigger path exactly for push watch and authorization guard;
- runner source orders TRAIN-only fit -> tokenizer JSON save -> tokenizer SHA freeze -> metadata validation -> post-freeze VALIDATION/PRISTINE parsing;
- unchanged Git blobs preserve the previously computed SHA-256 bindings for spec, workflow, runner, tokenizer source and data-audit closure.

Formal verdict:

`TOKENIZER_FREEZE_IMPLEMENTATION_LOCK_PASS`

Exactly one canonical tokenizer-freeze execution is now authorized.

Scientific model initialization and training remain forbidden.


## 10. Invalid pre-fit execution and CI dependency repair

The first tokenizer workflow run:

`35562245262`

at head:

`416a2b48a67d09baffe51e1964397cea21d25747`

passed:

- authorization guard;
- immutable source artifact metadata check;
- exact artifact download;
- Python setup;
- tokenizers dependency installation;
- static source compilation.

It then failed before runner initialization because importing the MindForge package transitively imported `mindforge.model`, which requires PyTorch.

Observed exception:

`ModuleNotFoundError: No module named 'torch'`

No runner event was emitted.

No TRAIN corpus was created.

No tokenizer fit started.

No tokenizer JSON/result artifact existed.

Scientific classification:

`INVALID_BEFORE_TOKENIZER_FIT`

This run is excluded from tokenizer evidence.

The workflow-only repair at:

`dd7322ec6b081d6e76914cbd6db2ba54b2cdc476`

adds the frozen CPU runtime dependency:

`torch==2.12.1`

from the PyTorch CPU index.

It changes none of:

- source artifact/data;
- tokenizer runner;
- tokenizer procedure;
- vocabulary contract;
- fit corpus;
- tokenization gates;
- model/training scientific state.

Updated workflow binding:

- Git blob: `2ff7db93aaba9e8059ccc6a0f3c2120e3baeddae`
- SHA-256: `391889ccbe6a384f38b268a03c65385995dd18158412ad4306b9fa734935b7a0`

Before a replacement fit is authorized, independent review must prove the workflow-only nature of this repair and unchanged runner/spec/tokenizer/data-result bindings.


## 11. CI dependency rebind review closure

Independent review after the runtime-dependency repair proved:

- repair commit changed only `.github/workflows/mk1-tokenizer-freeze.yml`;
- post-repair manifest update changed only this lock document;
- tokenizer runner blob remains `ac9456d80935133cae27ebe91fed886479d8501b`;
- tokenizer spec blob remains `74df8e6b9f2ee3a3985c5a003a1573e17390feae`;
- `mindforge/tokenizer.py` remains `68c7d687c684c800c98344e26be7c75425ea528f`;
- materialization/data-audit result remains `1c12495fabdc1429416b000b6f7c87034bc4eebe`;
- repaired workflow blob is `2ff7db93aaba9e8059ccc6a0f3c2120e3baeddae`;
- the only scientific-execution blocker repaired was the missing package runtime dependency before runner import.

Formal verdict restored:

`TOKENIZER_FREEZE_IMPLEMENTATION_LOCK_PASS`

One replacement tokenizer-freeze execution is authorized. Run `35562245262` remains excluded as `INVALID_BEFORE_TOKENIZER_FIT`.
