# MK-1 TRAIN-Only Tokenizer Freeze Result v0.1

Status: **PASS / SCIENTIFIC TOKENIZER AND TOKENIZED INPUTS FROZEN**

Date: **2026-09-21**

Formal verdict:

`TOKENIZER_FREEZE_PASS`

## 1. Canonical execution

Valid tokenizer-freeze run:

`35562370974`

Execution head:

`cad02173faed046dba2907b83fa32ee2ddf9c951`

The earlier run `35562245262` is excluded as:

`INVALID_BEFORE_TOKENIZER_FIT`

because it failed on missing package runtime dependency before the tokenizer runner initialized and before any fit event occurred.

## 2. Canonical evidence artifact

- artifact name: `mk1-tokenizer-freeze-v0-1`
- artifact id: `10622602143`
- artifact ZIP SHA-256: `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`
- size: `739394` bytes

The artifact contains:

- `mk1-tokenizer.json`;
- `train_input_text.txt`;
- `tokenized_train.jsonl`;
- `tokenized_validation.jsonl`;
- `tokenized_pristine_confirmatory.jsonl`;
- `TOKENIZER_FREEZE_RESULT.json`.

## 3. Source provenance

Source materialization:

- run: `35553551910`;
- artifact id: `10619711251`;
- artifact ZIP SHA-256: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`.

Verified split hashes:

- TRAIN: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`;
- VALIDATION: `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`;
- PRISTINE_CONFIRMATORY: `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`.

Surface counts:

- TRAIN: `4000`;
- VALIDATION: `800`;
- PRISTINE_CONFIRMATORY: `1200`.

## 4. TRAIN-only fit contract

Fit source:

`TRAIN.input_text_only`

Fit surface records:

`4000`

Frozen corpus:

- bytes: `3895370`;
- SHA-256: `3d154a62ad134c1ff72e7295bee68212282b2f83db9be39f1c432d5f7c4db566`.

Explicit evidence:

- `validation_used_for_fit = false`;
- `pristine_confirmatory_used_for_fit = false`.

No TRAIN target/gold/schema metadata was intentionally included in the fit corpus.

## 5. Freeze barrier

Observed event order:

1. `TOKENIZER_GATE_STARTED`
2. `SOURCE_SPLIT_HASHES_AND_COUNTS_VERIFIED`
3. `TRAIN_INPUT_TEXT_ONLY_CORPUS_FROZEN`
4. `TOKENIZER_FIT_STARTED_TRAIN_ONLY`
5. `TOKENIZER_JSON_SAVED`
6. `TOKENIZER_SHA256_FROZEN`
7. `TOKENIZER_METADATA_VALIDATED`
8. `POST_TOKENIZER_FREEZE_SPLIT_PARSE_STARTED`
9. `VALIDATION_AND_PRISTINE_OPENED_AFTER_TOKENIZER_FREEZE`
10. `ALL_SPLITS_TOKENIZED_AND_MANIFESTS_FROZEN`

Therefore VALIDATION and PRISTINE_CONFIRMATORY were not opened for tokenization until after tokenizer SHA-256 freeze.

Result:

**PASS**

## 6. Frozen tokenizer identity

Tokenizer SHA-256:

`e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

Contract:

- model: BPE;
- normalizer: NFC;
- pre-tokenizer: ByteLevel;
- decoder: ByteLevel;
- requested vocabulary: `16384`;
- actual vocabulary: `3261`;
- B0 vocabulary: `16384`;
- `<|endoftext|>` id: `0`;
- `<|unk|>` id: `1`.

Cardinality gate:

`258 <= 3261 <= 16384`

Result:

**PASS**

## 7. Frozen tokenized-input manifests

### TRAIN

- manifest SHA-256: `7be5c48156329e2239ac7345845f705a9b934d7bcc7e940e7dd128c0603a934e`;
- surfaces: `4000`;
- minimum tokens: `132`;
- maximum tokens: `183`;
- mean tokens: `161.4315`;
- p95 tokens: `181`;
- total tokens: `645726`;
- maximum token id: `3260`;
- empty sequences: `0`;
- over-context sequences: `0`.

### VALIDATION

- manifest SHA-256: `2b4fbbba5c6d5b975dc010d13f460b0f318c7a7b873bfc116258ddf20f96c16a`;
- surfaces: `800`;
- minimum tokens: `133`;
- maximum tokens: `187`;
- mean tokens: `162.77`;
- p95 tokens: `184`;
- total tokens: `130216`;
- maximum token id: `2160`;
- empty sequences: `0`;
- over-context sequences: `0`.

### PRISTINE_CONFIRMATORY

- manifest SHA-256: `005a8421bed215037c47901e30d091342ac9e9ee096b3982bc4d779f789f35ce`;
- surfaces: `1200`;
- minimum tokens: `133`;
- maximum tokens: `217`;
- mean tokens: `178.28666666666666`;
- p95 tokens: `210`;
- total tokens: `213944`;
- maximum token id: `2289`;
- empty sequences: `0`;
- over-context sequences: `0`.

## 8. Global encoded-input gates

Observed:

- maximum encoded length: `217`;
- maximum token id: `3260`;
- all sequences non-empty: true;
- all lengths <=512: true;
- all token ids <16384: true.

Result:

**PASS**

No truncation was required.

## 9. Scientific boundary

The canonical result records:

- `scientific_model_seed_instantiated = false`;
- `model_forward_executed = false`;
- `optimizer_constructed = false`;
- `training_executed = false`.

Therefore this gate establishes tokenizer/input compatibility only.

It does not establish H1a, H1b, H1c, learnability, or any model-quality outcome.

## 10. Authorization after PASS

The next and only newly authorized stage is:

`PAIRED_INITIALIZATION_AND_EXACT_SAMPLE_TOKEN_BUDGET_AUDIT`

It may:

- instantiate the frozen B0 initialization for seeds `71001..71005`;
- prove paired arm initialization identity;
- compute exact deterministic TRAIN sample schedules without optimizer/model training;
- bind exact sample IDs and processed token budgets for both B0-DIRECT and M1-Z.

It may not:

- execute scientific optimizer steps;
- perform scientific model training;
- use validation model outcomes;
- run pristine-confirmatory inference.

Scientific training remains blocked until that gate receives a separate PASS.
