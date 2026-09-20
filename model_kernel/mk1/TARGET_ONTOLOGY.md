# MK-1 Target Ontology v0.1

Status: **FROZEN / AMENDED BY PREREGISTRATION_AMENDMENT_001 / NO DATA / NO TRAINING**

Date: **2026-09-21**

Original frozen blob before Amendment 001:

`90849d77dbcd9fabdbd67b735ba9296a3d0756a5`

Amendment:

`PREREGISTRATION_AMENDMENT_001.md`

## 1. Purpose

MK-1 tests representation formation from current raw observation/context. It does not test memory, continual learning, resource control, invariance, sparse routing, or final guardrail policy.

The learned structured target is Z. The common comparison endpoint is canonical semantic state C.

## 2. Frozen scene boundary

Each canonical scene contains exactly:

- one asserted proposition;
- one current observable evidence bundle;
- zero or more semantics-preserving surface variants.

A scene may contain multiple semantic mechanisms at once.

MK-1 v0.1 does not use a variable-size arbitrary entity/fact graph.

Forbidden target information:

- final ACCEPT / FLAG / BLOCK decision;
- violation-class decision labels;
- resource value or ShadowPrice;
- later turns;
- future-task outcomes;
- counterfactual action outcomes;
- episodic retrieval or retrieved examples;
- hidden simulator truth unavailable in the serialized current input.

## 3. Z1 — semantic primitives

Z1 is exactly 32 binary labels.

### RELATION — 6

- CONFLICT_EXISTS
- EXPLICIT_SUPERSESSION
- IMPLICIT_SELECTION
- CORRECTION
- CONTEXT_SPLIT
- EXCEPTS

### QUANTIFIER — 5

- EXACT_THRESHOLD
- LOWER_BOUND_THRESHOLD
- UPPER_BOUND_THRESHOLD
- ORDINAL_TRIGGER
- VAGUE_COUNT_POLICY

### TEMPORAL — 5

- EXACT_DURATION
- APPROX_DURATION
- PERIODIC_RULE
- EXPIRY_RULE
- RECENCY_RELATION

### FALLBACK — 3

- FALLBACK_IF_UNKNOWN
- FALLBACK_IF_CONFLICT
- FALLBACK_IF_UNAVAILABLE

### UNCERTAINTY — 4

- ABSTAINS
- REQUESTS_CLARIFICATION
- LOW_CONFIDENCE
- PRESERVES_CONFLICT

### SCOPE — 8

- OBSERVATION_SCOPE
- TURN_SCOPE
- SESSION_SCOPE
- TASK_SCOPE
- WORKFLOW_SCOPE
- DOMAIN_SCOPE
- GLOBAL_SCOPE
- CONTEXTUAL_SCOPE

### CLAIM — 1

- OPERATIONAL_SIGNAL

PIT-19 supplies provenance for this vocabulary family. The PIT deterministic extractor is not the gold-authoring mechanism for fresh MK-1 data.

## 4. Z2 — normalized observable arguments

Z2 has exactly 11 raw outputs.

Comparator, four-way categorical:

- NONE
- EXACT
- LOWER_BOUND
- UPPER_BOUND

Temporal precision, three-way categorical:

- NONE
- EXACT
- APPROX

Four canonical scalar slots:

- numeric_value
- ordinal_index
- duration_seconds
- period_seconds

Scalar presence is determined from the frozen gold scene and used only as a loss/evaluation mask. Missing scalars do not receive a learned sentinel.

The source textual unit is not a separate primary target. Correct interpretation is tested through the canonical scalar.

No Z2 value may be inferred from future or counterfactual outcome.

## 5. Z3 — scope state

Z3 contains:

- evidence scope: eight-way categorical using the frozen SCOPE vocabulary;
- asserted scope: eight-way categorical using the frozen SCOPE vocabulary;
- scope relation: four-way categorical:
  - NARROWER
  - EQUAL
  - BROADER
  - INCOMPARABLE

The generating scopes remain separate from the derived relation.

## 6. Z4 — fixed observable relation/support register

Z4 is exactly seven binary targets:

1. conflict_present
2. supersession_supported
3. scope_supported
4. numeric_value_supported
5. temporal_rule_supported
6. fallback_policy_supported
7. operational_signal_supported

All seven must be reconstructable from the current assertion/evidence scene under OBSERVABLE_IDENTIFIABILITY_CONTRACT.md.

The earlier variable candidate-graph wording is superseded by Amendment 001.

## 7. Canonical comparison state C

C is the common comparison endpoint for H1b.

### C1 — eight semantic booleans

- evidence_has_conflict
- resolves_conflict
- asserts_numeric_threshold
- asserts_temporal_rule
- asserts_fallback_policy
- abstains
- requests_clarification
- has_operational_signal

### C2 — evidence scope

Eight-way categorical.

### C3 — asserted scope

Eight-way categorical.

### C4 — scope relation

Four-way categorical:

- NARROWER
- EQUAL
- BROADER
- INCOMPARABLE

### C5 — six support booleans

- supersession_supported
- scope_supported
- numeric_value_supported
- temporal_rule_supported
- fallback_policy_supported
- operational_signal_supported

C contains no final policy/action label.

## 8. Factorize before recombination

M1-Z predicts Z1-Z4.

A frozen parameter-free recomposer R derives C from thresholded/categorical Z predictions.

B0-DIRECT predicts C directly and never receives Z supervision.

Therefore H1b tests structured intermediate supervision plus deterministic recomposition versus direct canonical-state learning.

## 9. Hard-label discipline

A discrete target is admissible only when:

1. it is directly observable as a categorical property; or
2. it is deterministically derived from a stable canonical gold object; and
3. when threshold-derived, its generating quantity and target-margin audit are retained.

A convenient downstream decision label is not automatically an MK-1 representation target.

## 10. Non-goals

MK-1 does not claim this ontology is universal.

A PASS supports only this frozen target contract on the tested B0-scale substrate.
