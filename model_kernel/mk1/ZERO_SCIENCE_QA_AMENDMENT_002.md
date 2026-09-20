# MK-1 Zero-Science QA — Amendment 002

Status: **PASS**

Date: **2026-09-21**

Formal verdict:

`ZERO_SCIENCE_QA_AMENDMENT_002_PASS`

This QA evaluates only the tokenizer-cardinality amendment. No MK-1 scientific data, tokenizer fitting, model implementation, training, validation, or confirmatory inference is executed here.

## 1. Amendment under review

PREREGISTRATION_AMENDMENT_002.md:

- commit: `f78e6bff990d1d0ef1956ff5a0c3054d95e958bf`;
- blob: `1a7015cab1df40eb9467b42b1b9992e30a18d911`.

Updated matching contract:

- BASELINES_AND_MATCHING.md blob: `4bca66437bbfe91b45a7762a61d213982f99da3f`.

Preregistration binding before this QA:

- HYPOTHESES_AND_PREREGISTRATION.md blob: `b5a1af6823b4cb1fb375c5063f50184e4dd7ba75`.

Current tokenizer source:

- `mindforge/tokenizer.py` blob: `68c7d687c684c800c98344e26be7c75425ea528f`.

## 2. Historical-artifact check

The exact Phase-2 run metadata points to training commit:

`159b5b793af1c18edcc3ebec5a4bd1fca5af0ea5`

and to tokenizer fingerprint:

`66a81f01511a62896089e8e2a510c95dad61b567cec12f0dbc5752529b11fb3e`.

The referenced tokenizer/data files are absent both from current HEAD and the exact historical training commit.

Therefore:

- historical checkpoint remains compatibility evidence only;
- no new tokenizer may be semantically substituted into that checkpoint;
- paired random B0 initialization remains required.

PASS.

## 3. Tokenizer procedure identity

Current `mindforge.tokenizer.train_tokenizer` freezes:

- BPE model;
- NFC normalization;
- ByteLevel pre-tokenizer;
- ByteLevel decoder;
- special tokens `<|endoftext|>` and `<|unk|>`;
- requested maximum vocabulary size.

Amendment 002 does not alter this implementation.

PASS.

## 4. Leakage boundary

Frozen contract requires:

- tokenizer fitting from TRAIN surfaces only;
- one resulting artifact for all arms and all seeds;
- no VALIDATION input in tokenizer fitting;
- no PRISTINE_CONFIRMATORY input in tokenizer fitting.

PASS.

## 5. Cardinality boundary

Frozen gate:

`258 <= V_actual <= 16,384`

with:

- B0 `ModelConfig.vocab_size = 16,384` unchanged;
- every encoded token ID < 16,384;
- both special tokens required;
- no synthetic/reserved token insertion solely to fill unused model vocabulary rows.

This preserves equal model capacity while avoiding a corpus-dependent exact-merge-count gate.

PASS.

## 6. Scientific-variable check

Amendment 002 changes none of:

- target ontology;
- Z/C layout;
- B0 architecture;
- model parameter count;
- paired model seeds;
- data namespaces;
- representation losses;
- H1a/H1b/H1c endpoints;
- acceptance thresholds.

The only change is tokenizer pre-training admission semantics.

PASS.

## 7. Scope check

At QA time:

- scientific data materialization = 0;
- scientific tokenizer fitting = 0;
- MK-1 model implementation = 0;
- MK-1 training = 0;
- validation outcome inspection = 0;
- pristine-confirmatory inference = 0.

PASS.

## 8. Decision

`ZERO_SCIENCE_QA_AMENDMENT_002_PASS`

The complete amended preregistration is now eligible for:

`MK1_IMPLEMENTATION_LOCK`

Still forbidden until that lock and its zero-fresh preflight pass:

- scientific data materialization;
- scientific tokenizer fitting;
- neural training.
