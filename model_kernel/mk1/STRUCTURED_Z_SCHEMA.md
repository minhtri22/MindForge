# MK-1 Structured / Factorized Z Schema v0.1

Status: **FROZEN / AMENDED BY PREREGISTRATION_AMENDMENT_001 / NO IMPLEMENTATION**

Date: **2026-09-21**

Original frozen blob before Amendment 001:

`cb9ad4a9e546b086502f56f9151809eb7f3b0fc4`

## 1. Primary intervention

```
raw current input
        |
        v
exact B0 Transformer body
        |
        v
final non-padding hidden state after final LayerNorm
        |
        +--------------------+
        |                    |
     B0-DIRECT             M1-Z
        |                    |
        v                    v
 direct canonical C      Z1/Z2/Z3/Z4
                             |
                             v
                       frozen R(Z)
                             |
                             v
                         canonical C
```

The intervention is structured intermediate supervision and deterministic recomposition.

There is no memory head, controller head, scalar utility head, continual-learning head, invariant head, sparse-routing head, learned pooling, CLS token, or extra encoder block.

## 2. Shared encoder and pooling

Both neural arms use the exact default B0 Transformer body.

Pooling is the final hidden state of the final non-padding input token **after** the B0 final LayerNorm.

Implementation must expose this hidden state without changing B0 language-model logits.

Required zero-fresh parity:

- same B0 weights;
- same token tensor;
- float32 CPU;
- pre-MK-1 logits and refactored logits exactly equal.

No learned pooling is allowed.

## 3. M1-Z output layout

Hidden width:

`d = 320`

### Z1

32 binary logits, exact vocabulary from TARGET_ONTOLOGY.md.

Loss:

`L_Z1 = BCEWithLogits(mean over 32 labels)`

### Z2

11 raw outputs:

- comparator: 4 logits;
- temporal precision: 3 logits;
- numeric_value: 1 scalar;
- ordinal_index: 1 scalar;
- duration_seconds: 1 scalar;
- period_seconds: 1 scalar.

Scalar masks are gold-derived presence masks.

For each present scalar:

`e = (prediction - gold) / max(abs(gold), 1 canonical unit)`

`L_scalar = SmoothL1(e, 0, beta=1.0)`

Z2 loss is the unweighted mean of active components:

- comparator CE;
- temporal-precision CE;
- each scalar loss with at least one present target in the evaluated batch/unit.

### Z3

20 logits:

- evidence scope: 8;
- asserted scope: 8;
- scope relation: 4.

`L_Z3` is the unweighted mean of the three categorical cross-entropies.

### Z4

7 binary logits for the fixed relation/support register.

`L_Z4 = BCEWithLogits(mean over seven fields)`

### Total

`D_Z = 32 + 11 + 20 + 7 = 70`

`L_M1Z = 0.25 * (L_Z1 + L_Z2 + L_Z3 + L_Z4)`

Family weights cannot be validation-tuned.

## 4. B0-DIRECT output layout

B0-DIRECT predicts C directly with exactly 34 raw outputs:

- C1 semantic booleans: 8 logits;
- C2 evidence scope: 8 logits;
- C3 asserted scope: 8 logits;
- C4 scope relation: 4 logits;
- C5 support register: 6 logits.

`D_C = 34`

Loss:

`L_DIRECT` is the unweighted mean of:

- C1 BCE;
- C2 CE;
- C3 CE;
- C4 CE;
- C5 BCE.

B0-DIRECT receives no Z target and no auxiliary Z loss.

## 5. Frozen decoding rules

Binary field:

- predicted true iff logit >= 0;
- equivalent sigmoid threshold = 0.5.

Categorical field:

- deterministic argmax over the frozen class order;
- ties resolve to the lowest frozen class index.

Continuous Z2 field:

- raw scalar output, no validation-derived clipping or calibration.

These rules are identical in validation and confirmatory evaluation.

## 6. Frozen deterministic recomposer R

R has no learned parameters and never sees gold at inference.

Required mapping:

- C1.evidence_has_conflict <- Z4.conflict_present;
- C1.asserts_numeric_threshold <- OR(EXACT_THRESHOLD, LOWER_BOUND_THRESHOLD, UPPER_BOUND_THRESHOLD);
- C1.asserts_temporal_rule <- OR(EXACT_DURATION, APPROX_DURATION, PERIODIC_RULE, EXPIRY_RULE);
- C1.asserts_fallback_policy <- OR(FALLBACK_IF_UNKNOWN, FALLBACK_IF_CONFLICT, FALLBACK_IF_UNAVAILABLE);
- C1.abstains <- Z1.ABSTAINS;
- C1.requests_clarification <- Z1.REQUESTS_CLARIFICATION;
- C1.has_operational_signal <- Z1.OPERATIONAL_SIGNAL;
- C1.resolves_conflict <- Z4.conflict_present AND OR(EXPLICIT_SUPERSESSION, IMPLICIT_SELECTION, CORRECTION);
- C2 <- Z3 evidence-scope argmax;
- C3 <- Z3 asserted-scope argmax;
- C4 <- Z3 scope-relation argmax;
- C5 <- Z4 fields 2..7.

R emits no ACCEPT/FLAG/BLOCK action.

## 7. Parameter counts

M1-Z readout:

`(320 + 1) * 70 = 22,470`

Total:

`10,339,200 + 22,470 = 10,361,670`

B0-DIRECT readout:

`(320 + 1) * 34 = 10,914`

Total:

`10,339,200 + 10,914 = 10,350,114`

Difference:

`11,556`

Relative difference versus larger arm:

approximately `0.112%`

Frozen maximum:

`1.0%`

Parameter matching is feasible without a padding layer.

## 8. Outputs retained for evaluation

For every evaluated sample archive:

- sample and canonical-scene IDs;
- input length;
- Z logits/scalars for M1-Z;
- decoded Z;
- recomposed C for M1-Z;
- C logits and decoded C for B0-DIRECT;
- checkpoint hash;
- tokenizer hash.

No confirmatory prediction may be overwritten or selectively rerun.

## 9. No latent rescue arm

MK-1 v0.1 contains no free latent bottleneck arm.

Any later latent arm requires a new scientific uncertainty and new preregistration.
