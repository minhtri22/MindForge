# MK-1 Preregistration Amendment 002 — Tokenizer Cardinality Decoupling

Status: **PRE-OUTCOME / REQUIRED BEFORE IMPLEMENTATION LOCK**

Date: **2026-09-21**

## 1. Trigger

B0 reconstruction and historical Git audit established:

- the Phase-2 checkpoint is repository-contained and restorable;
- its tokenizer fingerprint is known;
- the referenced tokenizer file is not present at current HEAD;
- the referenced tokenizer file is also absent from the exact Phase-2 training commit `159b5b793af1c18edcc3ebec5a4bd1fca5af0ea5`.

Therefore the historical checkpoint cannot be used as MK-1 scientific initialization with a newly fitted tokenizer.

Amendment 001 already moved MK-1 to paired random B0 initialization.

A second implementation-feasibility issue remains: `mindforge.tokenizer.train_tokenizer(..., vocab_size=16384)` treats 16,384 as a requested maximum; the actual learned BPE vocabulary is corpus-dependent. Requiring exact equality would make scientific admission depend on whether a small controlled corpus happens to expose enough distinct merge opportunities.

No MK-1 scientific data, tokenizer, model training, validation outcome, or confirmatory outcome existed when this amendment was frozen.

## 2. Corrected tokenizer contract

Train exactly one tokenizer from TRAIN surfaces only using the unchanged current MindForge tokenizer procedure:

- `mindforge.tokenizer.train_tokenizer`;
- requested `vocab_size=16,384`;
- NFC normalization;
- ByteLevel pre-tokenizer;
- ByteLevel decoder;
- current two special tokens.

Freeze the resulting tokenizer artifact and SHA-256 before neural training.

The exact same tokenizer artifact is used by both neural arms and all five paired seeds.

VALIDATION and PRISTINE_CONFIRMATORY surfaces never participate in fitting.

## 3. Cardinality gate

Let `V_actual = tokenizer.get_vocab_size()`.

Required:

- `V_actual >= 258` (byte alphabet + two frozen special tokens);
- `V_actual <= 16,384`;
- every encoded token ID < 16,384;
- both frozen special tokens exist;
- tokenizer metadata matches the frozen NFC/ByteLevel/BPE contract.

The B0 model vocabulary remains exactly 16,384.

Unused embedding rows are permitted and remain identically available to both neural arms.

No reserved/artificial padding tokens may be injected merely to force `V_actual=16,384`.

## 4. Scientific rationale

The causal comparison requires identical tokenization and identical B0 capacity across arms, not that every embedding row be reachable.

This amendment removes a corpus-complexity artifact without changing:

- B0 parameter count;
- neural architecture;
- target ontology;
- Z/C layouts;
- scientific seed ranges;
- training scenes;
- comparison metrics;
- acceptance thresholds.

## 5. Historical checkpoint boundary

The Phase-2 checkpoint remains:

- B0 compatibility evidence;
- checkpoint-format evidence;
- runtime restore evidence.

It is not MK-1 scientific initialization.

No attempt may map a newly trained tokenizer onto the historical checkpoint's embedding semantics.

## 6. Authorization

This amendment changes only the pre-training tokenizer cardinality gate.

Implementation remains blocked until this amendment receives zero-science QA.

Scientific data materialization and training remain forbidden.
