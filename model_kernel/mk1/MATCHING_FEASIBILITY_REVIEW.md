# MK-1 B0-DIRECT ↔ M1-Z Matching Feasibility Review v0.1

Status: **REVISE BEFORE IMPLEMENTATION**

Date: **2026-09-21**

Verdict:

`MATCHING_FEASIBILITY_REVISE`

## 1. Scope

This review occurs after B0 reconstruction PASS and before any MK-1 model implementation, scientific data materialization, or training.

It asks whether the frozen B0-DIRECT and M1-Z contracts can support an identifiable causal comparison under the current preregistration.

## 2. Positive feasibility result

Capacity matching itself is feasible.

If a shared B0 hidden state of width `d=320` feeds linear outputs whose total dimension is `D`, then:

- one monolithic linear readout has `(d+1)D` parameters;
- multiple factorized linear readouts with dimensions `d_1...d_k`, where `sum(d_i)=D`, also have exactly `(d+1)D` parameters.

Therefore parameter equality is algebraically achievable.

The shared B0 body is already 10,339,200 parameters, so even modestly different readout dimensions can remain inside the preregistered total-trainable-parameter tolerance of 1%.

## 3. Blocking finding F1 — current H1b contrast can be functionally null

The v0.1 baseline contract states:

- B0-DIRECT uses one monolithic output projection over the serialized target vector;
- M1-Z uses typed factorized heads over the same target factors.

If both:

- consume the same pooled hidden state;
- emit the same serialized targets;
- use the same field-wise losses;

then concatenating the M1-Z linear heads is mathematically equivalent to the B0-DIRECT linear head.

The claimed intervention:

`factorized heads vs monolithic head`

would then be module organization rather than a distinct representational hypothesis.

This makes H1b scientifically non-identifying.

## 4. Blocking finding F2 — exact Z2 tensor contract is under-specified

The current ontology names normalized arguments but does not yet freeze:

- exact scalar slots;
- exact categorical vocabularies;
- missing-value masking semantics;
- canonical unit conversion;
- maximum multiplicity per scene.

Without these, output dimension and loss accounting can change at implementation time.

## 5. Blocking finding F3 — Z4 candidate-node layout is under-specified

The current Z4 text permits typed pairwise relation edges among candidate atomic facts but does not freeze:

- how candidate nodes are formed without gold leakage;
- maximum candidate count;
- edge serialization order;
- null/missing-edge semantics.

Choosing these after implementation begins would introduce hidden degrees of freedom.

## 6. Infrastructure finding F4 — historical tokenizer/data are not repository-contained

B0 reconstruction recovered and restored the real Phase-2 checkpoint, but the referenced historical tokenizer and train/validation token arrays are absent from the current Git tree.

Therefore MK-1 cannot rely on a repository-contained historical tokenizer artifact for automated execution.

This is not a B0 architecture failure.

A later implementation/data lock must prospectively define the tokenizer procedure/artifact used by both neural arms and must not claim historical Phase-2 metric parity unless the original artifact is recovered.

## 7. Required pre-outcome correction

Before implementation lock, revise the preregistration so that:

1. B0-DIRECT predicts a frozen **direct canonical state C**, not the same detailed Z factors;
2. M1-Z predicts detailed factors Z and uses a deterministic frozen recomposer `R(Z) -> C`;
3. H1b compares B0-DIRECT(C) against `R(M1-Z)` on the same canonical-state endpoints;
4. exact Z2 slots and masks are frozen;
5. Z4 uses a fixed observable relation register rather than an implementation-time variable candidate graph in MK-1 v0.1;
6. a fixed pooling/readout boundary is declared;
7. parameter/compute matching is recalculated under the corrected layout;
8. tokenizer/data artifact handling is made explicit before training.

## 8. Gate decision

`IMPLEMENTATION_LOCK = BLOCKED`

This is a successful pre-outcome design review, not a scientific FAIL.

No model code or scientific data has been created.

Next admissible action:

`MK1_PREREGISTRATION_AMENDMENT_001`
