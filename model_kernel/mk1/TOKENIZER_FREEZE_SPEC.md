# MK-1 TRAIN-Only Tokenizer Freeze Specification v0.1

Status: **FROZEN BEFORE SCIENTIFIC TOKENIZER FIT**

Date: **2026-09-21**

## 1. Authorization basis

Scientific dataset gate:

`SCIENTIFIC_MATERIALIZATION_AND_DATA_AUDIT_PASS`

Canonical materialization:

- run: `35553551910`
- artifact id: `10619711251`
- artifact ZIP SHA-256: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Frozen split SHA-256:

- TRAIN: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- VALIDATION: `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`
- PRISTINE_CONFIRMATORY: `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`

No dataset regeneration is authorized.

## 2. Artifact retrieval

The tokenizer workflow must retrieve the immutable materialization artifact by:

- repository: `minhtri22/MindForge`;
- run id: `35553551910`;
- artifact id: `10619711251`.

Before using extracted bytes, the workflow must query the artifact metadata and require exact digest:

`sha256:b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

The download action must treat any server digest mismatch as an error.

## 3. Split verification before fit

Before any tokenizer fitting:

1. require all three frozen JSONL files;
2. SHA-256 each file;
3. require exact equality with section 1;
4. require exact surface counts:
   - TRAIN 4,000;
   - VALIDATION 800;
   - PRISTINE_CONFIRMATORY 1,200;
5. no generator function may be invoked.

Failure is:

`TOKENIZER_SOURCE_PROVENANCE_FAIL`

and tokenizer fitting is forbidden.

## 4. TRAIN-only fit corpus

Tokenizer fit corpus is constructed from exactly:

`TRAIN[*].input_text`

and nothing else.

Forbidden fit inputs:

- any TRAIN target/gold/schema metadata;
- VALIDATION text or metadata;
- PRISTINE_CONFIRMATORY text or metadata;
- PIT structured fields;
- external corpora;
- historical Phase-2 tokenizer/data.

The fit corpus contains all 4,000 TRAIN surface strings in frozen order, each followed by a single record-separator newline after preserving the string's own UTF-8 content.

Freeze:

- corpus record count;
- corpus byte count;
- corpus SHA-256.

## 5. Tokenizer procedure

Use unchanged:

`mindforge.tokenizer.train_tokenizer`

with:

- requested vocab size: `16,384`;
- BPE;
- NFC normalization;
- ByteLevel pre-tokenizer;
- ByteLevel decoder;
- special tokens exactly:
  - `<|endoftext|>`
  - `<|unk|>`

Fit exactly once.

No artificial/reserved tokens may be added to force vocabulary cardinality.

## 6. Freeze barrier

After TRAIN-only fitting:

1. save tokenizer JSON;
2. compute tokenizer SHA-256;
3. load and validate tokenizer metadata;
4. freeze tokenizer artifact identity.

Only after step 3 succeeds may code open VALIDATION or PRISTINE_CONFIRMATORY for tokenization.

The result evidence must record the ordered event sequence proving this barrier.

## 7. Tokenized-input manifests

After tokenizer freeze, encode all three frozen splits.

Rows are sorted by:

`(scene_id, renderer_family)`

For every surface freeze:

- scene_id;
- renderer_family;
- split;
- input_text SHA-256;
- exact token_ids;
- token_count;
- SHA-256 of canonical token-ID byte encoding.

Write one JSONL manifest per split and freeze each manifest SHA-256.

These manifests become the authoritative tokenized inputs for the later sample-order/token-budget gate.

## 8. Tokenizer admission gates

Required:

- `258 <= V_actual <= 16,384`;
- B0 model vocab remains `16,384`;
- both frozen special tokens exist;
- metadata is BPE + NFC + ByteLevel;
- every encoded sequence is non-empty;
- every token ID satisfies `0 <= id < 16,384`;
- maximum encoded length in every split <= `512`;
- source split hashes still match;
- tokenizer fit source count = exactly `4,000`;
- VALIDATION/PRISTINE opened only after tokenizer SHA freeze.

No truncation is allowed.

Any failure before or after fitting is preserved as evidence; do not silently refit another tokenizer under the same protocol.

## 9. Output evidence

Canonical tokenizer-freeze artifact must contain:

- `mk1-tokenizer.json`;
- `train_input_text.txt`;
- `tokenized_train.jsonl`;
- `tokenized_validation.jsonl`;
- `tokenized_pristine_confirmatory.jsonl`;
- `TOKENIZER_FREEZE_RESULT.json`.

The result records source artifact/run IDs, all source hashes, tokenizer metadata/hash, corpus hash, manifest hashes, per-split length statistics, maximum token ID, and event sequence.

## 10. Scientific boundary

This gate may fit the scientific tokenizer and encode inputs.

It may not:

- instantiate scientific model seed `71001..71005`;
- construct an optimizer;
- execute any model forward/backward pass;
- inspect validation model outcomes;
- inspect pristine-confirmatory model outcomes;
- train B0-DIRECT or M1-Z.

PASS authorizes only the next pre-training gate:

`PAIRED_INITIALIZATION_AND_EXACT_SAMPLE_TOKEN_BUDGET_AUDIT`.

It does not authorize training by itself.
