# MK-1 Baselines and Capacity / Compute Matching v0.1

Status: **FROZEN SPECIFICATION / NO TRAINING**

Date: **2026-09-21**

## 1. Comparison set

MK-1 uses exactly three representation routes.

### B0-DIRECT — matched learned direct baseline

Purpose: test whether the frozen factorized Z objective provides value beyond a learned direct representation under the same neural substrate.

Contract:

- same B0 Transformer body and initialization family as M1-Z;
- same tokenizer and context limit;
- same training samples and split;
- same optimizer family;
- same number of optimization steps;
- same token budget;
- same random-seed set;
- one monolithic output projection over the serialized target vector rather than typed factorized heads.

B0-DIRECT is a learned comparator, not the untouched historical B0 checkpoint.

### D-PIT — deterministic PIT-v3 comparator

Purpose: preserve the historical deterministic representation baseline and error surface.

Contract:

- freeze the PIT-19 deterministic Representation V3 implementation and provenance;
- execute it unchanged on compatible fresh MK-1 surfaces;
- do not tune or add rules after seeing MK-1 data;
- where a new MK-1 field has no PIT-v3 analogue, exclude that field from the direct D-PIT comparison and report coverage explicitly.

D-PIT is not compute-matched to neural training and is not used for causal compute-efficiency conclusions.

### M1-Z — primary learned structured representation

Purpose: test factorized structured representation formation.

Contract:

- same B0 Transformer body and initialization family as B0-DIRECT;
- typed Z1-Z4 heads defined in STRUCTURED_Z_SCHEMA.md;
- no latent rescue head;
- no downstream action/controller head.

## 2. Parameter matching

For B0-DIRECT vs M1-Z:

- total trainable parameter counts must differ by no more than 1.0%;
- if factorized heads exceed the direct-head budget, use a prospectively fixed bottleneck width or parameter-neutral projection before training;
- no hidden auxiliary head may exist in only one arm.

If 1.0% matching cannot be achieved without changing the B0 body, the implementation must stop and issue a pre-outcome amendment.

## 3. Compute matching

For B0-DIRECT vs M1-Z require:

- identical train/validation sample sequence per seed;
- identical maximum sequence length;
- identical batch-size × accumulation effective batch;
- identical optimizer family and base schedule;
- identical maximum optimization steps;
- total processed training tokens within 1.0%;
- no arm-specific early stopping based on confirmatory data;
- validation-based checkpoint selection rule identical for both arms.

Wall-clock equality is not required.

## 4. Seed contract

Primary neural comparison uses exactly five training seeds:

```
71001
71002
71003
71004
71005
```

The same seed controls initialization and data order for paired B0-DIRECT / M1-Z runs.

No failed seed may be replaced.

## 5. Initialization

Both neural arms begin from the exact same B0 base checkpoint per paired seed.

If no canonical trained B0 checkpoint is available at implementation lock, both arms must begin from the same prospectively frozen initialization procedure and this limitation must be recorded.

## 6. Primary causal comparison

The primary causal contrast is:

```
M1-Z - B0-DIRECT
```

because both use the same neural substrate and matched resources.

The D-PIT comparison answers a different question:

```
learned representation vs frozen deterministic representation
```

and must not be interpreted as a compute-matched architectural causal effect.

## 7. Forbidden changes

After training begins, do not:

- increase one arm's width/depth;
- change only one optimizer;
- add auxiliary losses to one arm;
- change seed count;
- rerun only failed seeds;
- increase one arm's token budget;
- tune D-PIT;
- add a latent arm.
