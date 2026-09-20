# MK-1 Baselines and Capacity / Compute Matching v0.1

Status: **FROZEN / AMENDED BY PREREGISTRATION_AMENDMENT_001 / NO TRAINING**

Date: **2026-09-21**

Original frozen blob before Amendment 001:

`dec5747a7bf11857bcddcda25f3f431ced9f3156`

## 1. Comparison set

Exactly three routes are allowed.

### B0-DIRECT

Question:

Can the shared B0 body learn canonical semantic state C directly?

Contract:

- exact B0 body;
- final-token post-LayerNorm pooling;
- one 320 -> 34 linear readout;
- direct supervision only on C;
- no Z supervision;
- no auxiliary representation head;
- no final action/controller head.

### D-PIT

Frozen deterministic PIT-v3 comparator.

Contract:

- unchanged PIT-19 deterministic representation implementation;
- no tuning on MK-1 outcomes;
- comparison only on exact common semantic fields;
- unmatched deterministic comparator, not a compute-matched neural causal control.

### M1-Z

Question:

Does explicit structured intermediate supervision help representation generalization?

Contract:

- exact same B0 body and pooling as B0-DIRECT;
- one 320 -> 70 linear readout interpreted as frozen Z1-Z4 slices;
- Z family losses frozen in STRUCTURED_Z_SCHEMA.md;
- canonical C produced only by frozen deterministic R;
- no direct C loss;
- no latent rescue or controller head.

## 2. Identifiable primary causal contrast

Primary contrast:

`R(M1-Z) - B0-DIRECT(C)`

Both arms have the same neural substrate and current-input exposure.

The difference is:

- direct canonical supervision; versus
- structured intermediate supervision plus deterministic recomposition.

The earlier monolithic-versus-split-linear formulation is superseded because it could be algebraically equivalent.

## 3. Parameter matching

Frozen totals:

- M1-Z: `10,361,670`;
- B0-DIRECT: `10,350,114`;
- absolute difference: `11,556`;
- relative difference versus larger arm: approximately `0.112%`.

Gate:

<= 1.0%.

Result at specification level:

`PARAMETER_MATCHING_FEASIBLE`

No dummy/padding capacity is allowed.

At implementation preflight, observed trainable counts must equal these exact totals.

## 4. Compute matching

Both neural arms require:

- identical raw TRAIN scenes;
- identical tokenizer artifact;
- identical token sequence for each scene;
- identical sequence-length cap;
- identical per-seed scene order;
- identical optimizer family;
- identical learning-rate schedule;
- identical maximum optimization steps;
- identical micro-batch and accumulation;
- processed input-token count within 1.0%;
- same validation checkpoint-selection rule;
- no confirmatory-data early stopping.

Readout FLOPs differ because the representation intervention emits 70 versus 34 outputs. This is not compensated by useless computation.

Wall-clock equality is not required.

## 5. Paired seed contract

Exactly:

```
71001
71002
71003
71004
71005
```

For each seed:

1. set the frozen RNG seed;
2. instantiate exact default B0;
3. save/hash one base initialization state;
4. initialize both neural arms from that exact same B0 state;
5. initialize each arm's readout deterministically from that seed under the frozen framework procedure.

No failed seed may be replaced.

## 6. Historical checkpoint boundary

The Phase-2 seed-101 checkpoint is verified compatibility evidence.

It is not the MK-1 scientific initialization because the exact historical tokenizer artifact is not repository-contained.

No historical Phase-2 BPB parity claim is part of MK-1.

## 7. Tokenizer contract

Before neural training, after TRAIN surfaces are materialized and integrity-audited:

- train exactly one tokenizer from TRAIN surfaces only;
- use current `mindforge.tokenizer.train_tokenizer`;
- requested vocab_size = 16,384;
- NFC normalization;
- ByteLevel pre-tokenization/decoding;
- current special tokens only;
- freeze artifact and SHA-256;
- use the exact same tokenizer for all arms and all seeds;
- VALIDATION and PRISTINE_CONFIRMATORY surfaces never participate in tokenizer fitting.

If actual vocab size != 16,384:

`TOKENIZER_CONTRACT_FAIL`

and neural training is forbidden.

## 8. Checkpoint-selection rule

The exact selection metric and training schedule must be frozen in IMPLEMENTATION_LOCK.md before scientific training.

It must be identical for B0-DIRECT and M1-Z and cannot depend on pristine-confirmatory outcomes.

## 9. D-PIT interpretation

D-PIT answers whether the learned structured route improves over the frozen deterministic route on shared fields.

It does not answer neural compute efficiency or capacity matching.

Common-field coverage must be reported explicitly.

## 10. Forbidden changes after scientific training begins

Do not:

- change B0 width/depth;
- change pooling in one arm;
- change optimizer or schedule in one arm;
- add an auxiliary loss to one arm;
- change seed count;
- replace failed seeds;
- change token budget asymmetrically;
- tune D-PIT;
- add a latent arm;
- add direct-C supervision to M1-Z;
- add Z supervision to B0-DIRECT.
