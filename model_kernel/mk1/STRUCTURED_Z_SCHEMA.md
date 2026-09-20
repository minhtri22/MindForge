# MK-1 Structured / Factorized Z Schema v0.1

Status: **FROZEN SPECIFICATION / NO IMPLEMENTATION**

Date: **2026-09-21**

## 1. Design principle

The primary MK-1 intervention is:

```
raw current input
    |
    v
shared B0 Transformer body
    |
    +--> Z1 semantic primitives
    +--> Z2 normalized arguments
    +--> Z3 scope state
    +--> Z4 support/composition relations
```

The representation is factorized before recombination.

There is no scalar utility head, memory head, continual-learning head, resource-controller head, invariant head, or sparse-routing head in MK-1.

## 2. Shared encoder

The learned-Z arm uses the compact B0 Transformer defined in BASELINE_CONTRACT.md as the encoder substrate.

The architecture of the shared Transformer body is unchanged in MK-1.

Only representation readout heads and the prospectively frozen representation-training objective may differ from the direct learned baseline.

## 3. Typed factors

### Z1 head — primitives

Multi-label typed prediction over the frozen TARGET_ONTOLOGY.md primitive vocabulary.

Loss family: binary cross entropy over declared primitive labels.

### Z2 head — normalized arguments

Typed argument slots.

Depending on field type:

- categorical comparator/unit: cross entropy;
- explicit numeric/duration scalar: normalized regression;
- ordered relation: categorical relation prediction.

No scalar is used when the source text does not explicitly identify the quantity.

### Z3 head — scope

Separate predictions for:

- evidence scope;
- asserted scope;
- scope relation.

Do not predict only the final relation if the two generating scope factors are available.

### Z4 head — relation graph

Predict typed pairwise relation edges among frozen candidate atomic facts.

Primary edge types:

- conflicts;
- supports;
- supersedes;
- excepts;
- scope_support;
- value_support.

Candidate-node construction must be frozen before training and cannot use gold relation labels at inference time.

## 4. Deterministic recomposer

A frozen deterministic recomposer may derive:

- canonical semantic attributes;
- conflict state;
- normalized support state;
- composition consistency.

It may not derive or emit the final policy decision for MK-1 adjudication.

The recomposer exists only to test whether individually learned factors compose consistently.

## 5. No latent rescue arm

MK-1 v0.1 contains no additional free latent bottleneck arm.

Reason:

- CQG supports explicit structured decomposition in its own substrate;
- KCL shows repeated representation expansion without a new uncertainty can become rescue;
- adding a latent arm now would introduce another causal variable without a demonstrated need.

A latent arm requires a new preregistered hypothesis after MK-1 v0.1 outcome or a pre-execution governance amendment justified by new upstream evidence.

## 6. Representation outputs retained for evaluation

For every sample, archive:

- per-field logits/scores;
- thresholded typed outputs;
- normalized argument predictions;
- relation-edge scores;
- recomposed canonical state;
- model/checkpoint hash;
- input/sample ID.

No confirmatory prediction may be overwritten or selectively rerun.

## 7. Claim boundary

A PASS supports only the frozen Z schema and the tested B0-scale model.

It does not establish a universal ontology or controller architecture.
