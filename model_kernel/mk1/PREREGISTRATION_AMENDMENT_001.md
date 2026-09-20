# MK-1 Preregistration Amendment 001 — Identifiable Direct-vs-Structured Contrast

Status: **PRE-OUTCOME / REQUIRED BEFORE IMPLEMENTATION**

Date: **2026-09-21**

Trigger:

`MATCHING_FEASIBILITY_REVISE`

Evidence trigger commit:

`6f802ea2592de68e784a7419970116fb72652d9b`

No MK-1 scientific data, model implementation, training, validation outcome, or confirmatory outcome existed when this amendment was frozen.

## 1. Purpose

The v0.1 specification allowed B0-DIRECT and M1-Z to become algebraically equivalent if both predicted the same serialized target vector through linear readouts.

This amendment makes the causal contrast identifiable:

```
B0-DIRECT:
raw input -> B0 body -> direct canonical state C

M1-Z:
raw input -> B0 body -> factorized Z1-Z4 -> frozen deterministic R(Z) -> canonical state C
```

The intervention is therefore **structured intermediate supervision and recomposition**, not Python module layout.

## 2. Frozen scene contract

Each MK-1 v0.1 canonical scene contains:

- one asserted proposition;
- one current observable evidence bundle;
- zero or more semantics-preserving surface variants.

A scene may express multiple semantic mechanisms simultaneously, but MK-1 v0.1 does not use a variable-size arbitrary entity/fact graph.

This restriction exists to keep the first representation experiment identifiable and implementation-independent.

## 3. Exact Z layout

The pooled B0 hidden width is 320.

### Z1 — 32 binary semantic primitives

Exact vocabulary:

RELATION, 6:
- CONFLICT_EXISTS
- EXPLICIT_SUPERSESSION
- IMPLICIT_SELECTION
- CORRECTION
- CONTEXT_SPLIT
- EXCEPTS

QUANTIFIER, 5:
- EXACT_THRESHOLD
- LOWER_BOUND_THRESHOLD
- UPPER_BOUND_THRESHOLD
- ORDINAL_TRIGGER
- VAGUE_COUNT_POLICY

TEMPORAL, 5:
- EXACT_DURATION
- APPROX_DURATION
- PERIODIC_RULE
- EXPIRY_RULE
- RECENCY_RELATION

FALLBACK, 3:
- FALLBACK_IF_UNKNOWN
- FALLBACK_IF_CONFLICT
- FALLBACK_IF_UNAVAILABLE

UNCERTAINTY, 4:
- ABSTAINS
- REQUESTS_CLARIFICATION
- LOW_CONFIDENCE
- PRESERVES_CONFLICT

SCOPE, 8:
- OBSERVATION_SCOPE
- TURN_SCOPE
- SESSION_SCOPE
- TASK_SCOPE
- WORKFLOW_SCOPE
- DOMAIN_SCOPE
- GLOBAL_SCOPE
- CONTEXTUAL_SCOPE

CLAIM, 1:
- OPERATIONAL_SIGNAL

Output dimensions:

`D_Z1 = 32`

Loss:

binary cross entropy with logits, mean over all 32 labels.

### Z2 — normalized observable arguments, 11 raw outputs

Categorical comparator:

`{NONE, EXACT, LOWER_BOUND, UPPER_BOUND}`

4 logits.

Temporal precision:

`{NONE, EXACT, APPROX}`

3 logits.

Four raw canonical scalars:

1. `numeric_value`
2. `ordinal_index`
3. `duration_seconds`
4. `period_seconds`

4 scalar outputs.

Total:

`D_Z2 = 4 + 3 + 4 = 11`

Scalar presence is a gold-derived loss/evaluation mask from the frozen canonical scene. Missing scalar values are not replaced by a learned sentinel.

Scalar training loss for each present field:

`SmoothL1((prediction - gold) / max(abs(gold), 1 canonical unit), 0)`

with beta = 1.0.

Source textual units are not a separate primary target in MK-1 v0.1. Correct unit interpretation is tested through the canonical scalar.

Z2 loss is the unweighted mean of active:
- comparator CE;
- temporal-precision CE;
- four masked scalar losses with at least one present target.

### Z3 — scope state, 20 logits

Evidence scope:

8-way categorical.

Asserted scope:

8-way categorical.

Scope relation:

`{NARROWER, EQUAL, BROADER, INCOMPARABLE}`

4-way categorical.

Total:

`D_Z3 = 8 + 8 + 4 = 20`

Z3 loss is the unweighted mean of the three categorical losses.

### Z4 — fixed observable relation/support register, 7 binary outputs

MK-1 v0.1 replaces the under-specified variable candidate graph with exactly:

1. `conflict_present`
2. `supersession_supported`
3. `scope_supported`
4. `numeric_value_supported`
5. `temporal_rule_supported`
6. `fallback_policy_supported`
7. `operational_signal_supported`

Total:

`D_Z4 = 7`

Loss:

binary cross entropy with logits, mean over seven fields.

All seven fields must be derivable from the current assertion/evidence scene under OBSERVABLE_IDENTIFIABILITY_CONTRACT.md.

### Total M1-Z raw output dimension

`D_Z = 32 + 11 + 20 + 7 = 70`

## 4. M1-Z loss

The four factor-family losses have equal weight:

`L_M1Z = 0.25 * (L_Z1 + L_Z2 + L_Z3 + L_Z4)`

No validation-tuned family weights are allowed.

## 5. Frozen canonical state C

B0-DIRECT predicts C directly.

M1-Z produces C only through the frozen deterministic recomposer R.

C contains 34 raw outputs.

### C1 — canonical semantic booleans, 8

1. evidence_has_conflict
2. resolves_conflict
3. asserts_numeric_threshold
4. asserts_temporal_rule
5. asserts_fallback_policy
6. abstains
7. requests_clarification
8. has_operational_signal

### C2 — evidence scope

8-way categorical.

### C3 — asserted scope

8-way categorical.

### C4 — scope relation

4-way categorical:
- NARROWER
- EQUAL
- BROADER
- INCOMPARABLE

### C5 — support register, 6 binary outputs

1. supersession_supported
2. scope_supported
3. numeric_value_supported
4. temporal_rule_supported
5. fallback_policy_supported
6. operational_signal_supported

Total direct raw dimension:

`D_C = 8 + 8 + 8 + 4 + 6 = 34`

B0-DIRECT loss is the unweighted mean of:
- C1 BCE;
- C2 CE;
- C3 CE;
- C4 CE;
- C5 BCE.

## 6. Deterministic recomposer R

R is parameter-free and frozen before data materialization.

Required identities include:

- C1.evidence_has_conflict <- Z4.conflict_present;
- C1.asserts_numeric_threshold <- OR of Z1 quantifier threshold primitives;
- C1.asserts_temporal_rule <- OR of Z1 temporal rule primitives;
- C1.asserts_fallback_policy <- OR of Z1 fallback primitives;
- C1.abstains <- Z1.ABSTAINS;
- C1.requests_clarification <- Z1.REQUESTS_CLARIFICATION;
- C1.has_operational_signal <- Z1.OPERATIONAL_SIGNAL;
- C2 <- Z3 evidence scope;
- C3 <- Z3 asserted scope;
- C4 <- Z3 scope relation;
- C5 <- Z4 support fields 2..7.

`resolves_conflict` is true only when:
- conflict_present is predicted true;
- and a resolution primitive among EXPLICIT_SUPERSESSION, IMPLICIT_SELECTION, or CORRECTION is predicted true.

No final ACCEPT/FLAG/BLOCK policy is produced.

## 7. Pooling/readout boundary

MK-1 v0.1 uses the final hidden state at the final non-padding input token after B0 final LayerNorm.

Implementation must expose this hidden state without changing B0 logits.

Parity requirement before training:

for identical B0 weights and tokens, refactored B0 language-model logits must be exactly equal to the pre-MK-1 B0 logits in float32 CPU test execution.

No learned pooling, attention pooling, CLS token, or extra encoder block is allowed.

## 8. Parameter matching feasibility

M1-Z readout parameters:

`P_Z = (320 + 1) * 70 = 22,470`

Total M1-Z trainable parameters:

`10,339,200 + 22,470 = 10,361,670`

B0-DIRECT readout parameters:

`P_C = (320 + 1) * 34 = 10,914`

Total B0-DIRECT trainable parameters:

`10,339,200 + 10,914 = 10,350,114`

Absolute difference:

`11,556`

Relative difference versus larger arm:

`11,556 / 10,361,670 = 0.001115...`

= approximately **0.112%**

Frozen requirement:

<= 1.0%

Therefore:

`PARAMETER_MATCHING_FEASIBLE = true`

No capacity-padding layer is needed.

## 9. Compute matching

Both neural arms use:

- identical raw training scenes;
- identical tokenizer artifact;
- identical tokenized sequence per scene;
- identical sequence-length cap;
- identical per-seed scene order;
- identical optimizer family/schedule;
- identical optimization steps;
- identical effective batch;
- identical processed input-token count within 1%.

Readout FLOPs may differ because the structured arm emits more supervised fields. This difference is part of the representation intervention and is not compensated by adding useless computation to B0-DIRECT.

The primary resource matching variable remains processed Transformer input tokens and steps, not wall time.

## 10. Initialization and tokenizer contract

The historical Phase-2 checkpoint remains compatibility evidence only.

Because its exact tokenizer artifact is not repository-contained, it is **not** the scientific initialization for MK-1 v0.1.

For each paired seed 71001..71005:

1. set the frozen RNG seed;
2. instantiate the exact default B0 ModelConfig;
3. save one base initialization state;
4. initialize both B0-DIRECT and M1-Z from that exact same state.

Tokenizer procedure:

- train exactly one byte-level BPE tokenizer from TRAIN surfaces only;
- use current `mindforge.tokenizer.train_tokenizer`;
- requested vocab_size = 16,384;
- NFC normalization;
- ByteLevel pre-tokenization;
- current two special tokens;
- freeze tokenizer artifact/hash before any neural training;
- use the identical tokenizer for every neural arm and seed;
- confirmatory text must never participate in tokenizer fitting.

If resulting tokenizer vocab size is not exactly 16,384:

`TOKENIZER_CONTRACT_FAIL`

and neural training is forbidden.

## 11. Corrected H1b endpoint

H1b no longer compares detailed Z metrics between the two neural arms.

It compares canonical state C:

`R(M1-Z) vs B0-DIRECT(C)`

Define canonical-state balanced score as the unweighted mean of:

1. C1 macro F1 over eight booleans;
2. C2 evidence-scope accuracy;
3. C3 asserted-scope accuracy;
4. C4 scope-relation accuracy;
5. C5 macro F1 over six support fields.

Frozen H1b gate remains:

- mean paired improvement >= +0.03 absolute;
- whole-scene paired-bootstrap 95% lower bound > 0.

M1-Z detailed Z gates remain H1a-only representation-formation gates.

## 12. D-PIT comparison

D-PIT remains frozen and unmodified.

H1c compares only fields with exact semantic correspondence.

No missing MK-1-only field is scored as a D-PIT error.

Coverage of the common-field intersection must be reported.

## 13. Scientific claim after amendment

H1b now asks:

> Does explicit intermediate semantic factor supervision plus deterministic recomposition improve canonical-state generalization compared with direct canonical-state learning under the same B0 neural substrate and matched training exposure?

This is a distinct falsifiable hypothesis.

## 14. Authorization

This amendment repairs the preregistration only.

It does not authorize:

- data materialization;
- model implementation;
- tokenizer fitting;
- training.

Required next step:

`ZERO_SCIENCE_QA_AMENDMENT_001`

Only after that QA passes may implementation lock be reconsidered.
