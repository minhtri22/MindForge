# MK-1 — Learned Structured Decision-State Representation v0.1

Status: **PREREGISTERED / AMENDMENT 001 QA PASS / AMENDMENT 002 QA PENDING / IMPLEMENTATION NOT AUTHORIZED**

Date: **2026-09-21**

Branch: **research/model_core**

## 1. Scientific question

Can the compact MindForge model learn, from current raw observation/context only, a structured and factorized semantic decision-state that generalizes on a pristine unseen distribution better than the matched direct learned baseline and the frozen deterministic PIT representation?

MK-1 tests **representation formation** only.

It does not test final decision sufficiency, memory, continual learning, resource control, invariance objectives, sparse execution, or runtime optimization.

## 2. Upstream evidence that motivates but does not substitute for MK-1

### PIT-19

PIT-19 closed:

`DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED`

with pristine CLEAN_HELD_OUT failures dominated by primitive-extraction false negatives.

Evidence anchors:

- report blob: `4eedeac78d0b3abf8ace037ef1f3603f39689325`;
- final-verdict blob: `b90a18bcb82f0364c809e44ac6fe84e733e41503`;
- schema blob: `6ab4104b4df3ce35980e558f5bacf4212df954cf`.

This motivates a learned representation study. It does not prove a learned extractor will work.

### CQG J3.14→J3.16

J3.14 did not qualify generic data-doubling or generic learner-class remedies under its frozen gates.

J3.15 prospectively established that the structured arm's raw-Spearman failure was a numerical/near-tie pathology rather than material-order failure.

J3.16 formally concluded:

`STRUCTURED_OBSERVABLE_ECV_SUPPORTED`

Evidence anchors:

- J3.15 report blob: `4244adcbab3865695896f48eb1a892a6e618f696`;
- J3.16 report blob: `89dbf55dfc2dd5edcc347bf40edb8c7a0698be3b`;
- J3.16 formal-evidence commit: `181758a70bac6477a88ee463cc8bc9c88e5a4c27`.

Transferable lesson: explicit structured/factorized observables can support a simple, stable downstream mapping.

Non-transferable object: CQG's exact 48-D PHI representation.

### KCL-6.5.9.x

The KCL chain formally closed with:

```
DIAGNOSTIC_CONVERGENCE_ACHIEVED
NO_QUALIFIED_BOUNDARY_CONTROLLER
ACTIVE_KCL_6_5_9_X_STOP
```

Evidence anchors:

- KCL branch HEAD at audit: `a9159ae8f17693453e7b6378c92deb5effc4a56f`;
- convergence-review blob: `a0cba485b5f59c8c60ae5806cb24e394edee4bef`.

Transferable lessons:

- real latent/mechanistic structure may still be non-identifiable from available observables;
- hard derived labels can collapse heterogeneous mechanisms;
- target stability and observable identifiability must be checked before blaming representation;
- repeated feature/history/capacity rescue without a new uncertainty must stop.

No KCL predictor/controller is imported.

## 3. Hypotheses

### H1a — learned representation formation

A learned structured representation M1-Z can satisfy prospectively frozen absolute semantic-representation gates on pristine confirmatory data.

### H1b — structured intermediate supervision adds value over direct canonical learning

Under matched neural substrate, parameters, current-input exposure, seeds, and compute, canonical state `R(M1-Z)` improves over direct `B0-DIRECT(C)` by the frozen canonical-state paired threshold.

The contrast is structured Z supervision plus deterministic recomposition versus direct C supervision. It is not monolithic-versus-split module layout.

### H1c — learned representation exceeds the frozen deterministic route

On fields shared with PIT-v3, M1-Z materially reduces representation error relative to D-PIT while preserving high precision.

These hypotheses are adjudicated sequentially. H1b/H1c cannot rescue H1a failure.

## 4. Frozen intervention and baselines

Exactly three routes:

```
B0-DIRECT  — exact B0 body -> direct canonical state C
D-PIT      — frozen deterministic PIT-v3 representation
M1-Z       — exact B0 body -> Z1-Z4 -> frozen R(Z) -> canonical state C
```

No fourth latent arm is authorized.

Detailed contract:

`BASELINES_AND_MATCHING.md`

blob:

`4bca66437bbfe91b45a7762a61d213982f99da3f`

## 5. Frozen target ontology

The primary target is structured state Z:

- Z1 semantic primitives;
- Z2 normalized observable arguments;
- Z3 scope state;
- Z4 support/composition relations.

Final action/guardrail labels are excluded from MK-1 representation training.

Target contract:

`TARGET_ONTOLOGY.md`

blob:

`65b152f54b7f2bb7ea45e97a433443e0956a7d11`

## 6. Target stability prerequisite

Before model training:

- categorical targets must be deterministically re-derivable;
- semantics-preserving variants must retain identical gold target;
- threshold-derived labels must retain their generating quantity;
- brittle near-margin hard labels cannot be primary endpoints.

Contract:

`TARGET_STABILITY_AUDIT.md`

blob:

`e4dfd62eb4aeb14595d03e299a753ac6711d9547`

## 7. Observable-identifiability prerequisite

Every target field must trace to information observable in the current serialized input.

Future/counterfactual outcomes, hidden simulator truth, final actions, retrieved memory, and later turns are forbidden.

Contract:

`OBSERVABLE_IDENTIFIABILITY_CONTRACT.md`

blob:

`53e37771fd3244df7f4c461305963afc7ff12221`

## 8. Frozen structured representation schema

M1-Z uses a shared B0 Transformer body and factorized Z1-Z4 readout heads.

A deterministic evaluation-only recomposer may recombine predicted factors into canonical semantic state.

There is no learned controller and no latent rescue arm.

Schema:

`STRUCTURED_Z_SCHEMA.md`

blob:

`045cafa9a8cc6bc9b207da9915f47f982152fbaa`

## 9. Data and pristine-confirmatory contract

Reserved canonical-scene namespaces:

- TRAIN: `7101000..7102999`;
- VALIDATION: `7103000..7103399`;
- PRISTINE_CONFIRMATORY: `7104000..7104599`.

All variants of one canonical scene remain within one split.

The confirmatory set requires unseen semantic scenes plus held-out surface-construction routes and one-shot execution.

Exact split/evaluation contract:

`DATA_SPLIT_AND_EVALUATION.md`

blob:

`5192a273e36911d5c9598f2de19884b71525c083`

## 10. Neural matching contract

B0-DIRECT and M1-Z must match:

- exact B0 body and final-token post-LayerNorm pooling;
- one saved paired B0 initialization state per seed;
- one TRAIN-only frozen tokenizer artifact;
- train/validation scenes and tokenized sequences;
- five paired training seeds `71001..71005`;
- optimizer family and schedule;
- training steps and effective batch;
- processed input tokens within 1%.

Frozen trainable totals:

- B0-DIRECT = `10,350,114`;
- M1-Z = `10,361,670`;
- difference ~= `0.112%`, inside the 1% gate.

No failed seed replacement is allowed.

D-PIT remains an unmatched deterministic comparator and cannot support compute-efficiency claims.

## 11. Primary metrics and gates

The authoritative thresholds are frozen in DATA_SPLIT_AND_EVALUATION.md.

M1-Z H1a absolute PASS requires, among other gates:

- Z1 micro precision >= 0.95;
- Z1 micro recall >= 0.95;
- Z1 macro F1 >= 0.90;
- Z3 scope-relation accuracy >= 0.95;
- Z4 pooled precision >= 0.95;
- Z4 pooled recall >= 0.90;
- recomposed C canonical-state field accuracy >= 0.95;
- invariance-cluster consistency >= 0.95;
- no supported primary Z1/Z4 class recall < 0.80;
- each supported continuous Z2 scalar mean nAE <= 0.05 and p95 nAE <= 0.10.

H1b compares only canonical C:

- `Delta_C >= +0.03`;
- paired whole-scene bootstrap 95% lower bound > 0.

M1-Z vs D-PIT on common fields:

- relative error reduction >= 20%;
- 95% lower bound >= 10%;
- primitive precision degradation no worse than -0.02 absolute.

No threshold may be changed after scientific training begins.

## 12. Formal verdicts

Sequentially:

1. data/split integrity;
2. target stability;
3. observable identifiability;
4. tokenizer contract;
5. B0 reconstruction;
6. implementation/matching integrity;
7. M1-Z H1a absolute gates;
8. H1b canonical-state paired comparison;
9. H1c D-PIT common-field comparison.

Possible terminal verdicts:

- `MK1_INVALID_BEFORE_TRAINING`
- `LEARNED_STRUCTURED_REPRESENTATION_NOT_SUPPORTED`
- `LEARNED_REPRESENTATION_SUPPORTED_FACTORISATION_NOT_ESTABLISHED`
- `STRUCTURED_FACTORISATION_SUPPORTED_NO_DETERMINISTIC_CEILING_BREAK`
- `MK1_LEARNED_STRUCTURED_REPRESENTATION_SUPPORTED`

## 13. Anti-rescue rules

After any valid scientific outcome is observed, do not:

- alter target ontology;
- alter field derivation;
- alter seed ranges;
- alter train/validation/confirmatory membership;
- replace failed seeds;
- change acceptance thresholds;
- tune D-PIT;
- add a latent arm;
- add memory/history/future probes;
- add a decision/controller loss;
- change only one neural arm's compute;
- rerun pristine confirmatory results selectively.

A new attempt requires a new explicitly named hypothesis and preregistration.

## 14. Evidence contract for later execution

A valid MK-1 execution must archive:

1. preregistration commit/blob/hash;
2. exact B0 source/config/checkpoint hashes;
3. exact ontology/schema blobs;
4. data-generation source and environment;
5. canonical-scene manifest and split hashes;
6. target-stability result;
7. observable-identifiability result;
8. model parameter counts;
9. optimizer/schedule/token-budget manifests;
10. five paired seed checkpoints;
11. one-shot pristine predictions;
12. raw per-scene metrics;
13. bootstrap outputs;
14. formal adjudication JSON;
15. append-only lineage entry.


## 15. Pre-outcome Amendment 001 and B0 gate

B0 reconstruction formally passed before implementation:

- B0 reconstruction document blob: `173dd942fd703755dd253d785ca5f3993cbd5c38`;
- canonical workflow run: `35526336632`;
- execution head: `6f54872d0825f07a3394747576c537ca447c999b`;
- parameter count: `10,339,200`;
- historical checkpoint restore: PASS;
- deterministic zero-science eval/generation replay: PASS.

The subsequent matching-feasibility review found the original H1b formulation potentially algebraically non-identifying and returned:

`MATCHING_FEASIBILITY_REVISE`

Review blob:

`981942426e2933579e733e347bafd78cbbc1284d`

Before any MK-1 implementation or scientific data, Amendment 001 was frozen:

- amendment blob: `0ec12864118e1b95d579318edab0dc8c00552656`;
- amendment commit: `4d8e9a8e9e22e17ee35270991e027526600296bf`.

Amendment 001 supersedes conflicting v0.1 clauses and freezes:

- B0-DIRECT -> C directly;
- M1-Z -> 70-dimensional Z -> deterministic R -> C;
- 34-dimensional direct C layout;
- exact Z1/Z2/Z3/Z4 layouts and loss families;
- final-token post-LayerNorm pooling;
- exact parameter totals;
- TRAIN-only tokenizer procedure;
- H1b on canonical C only.

The original ZERO_SCIENCE_QA.md remains historical evidence for the pre-amendment package and does not by itself validate Amendment 001.

## 16. Current authorization state

Current state:

```
B0_RECONSTRUCTION                PASS
MATCHING_FEASIBILITY_V0_1        REVISE
PREREGISTRATION_AMENDMENT_001    FROZEN
AMENDMENT_001_ZERO_SCIENCE_QA    PASS
AMENDMENT_002_ZERO_SCIENCE_QA    PENDING
IMPLEMENTATION_LOCK              BLOCKED
SCIENTIFIC_DATA_MATERIALIZATION  BLOCKED
TRAINING                         BLOCKED
```

Amendment 001 QA evidence:

- QA blob: `dd67636b08afea8b38d491e3081e8b60c054270e`;
- QA commit: `238d9f7c9f7d242eb7bff455fd0f46b13eb4cf43`.

A subsequent historical-artifact feasibility audit froze Amendment 002:

- amendment blob: `1a7015cab1df40eb9467b42b1b9992e30a18d911`;
- amendment commit: `f78e6bff990d1d0ef1956ff5a0c3054d95e958bf`.

Amendment 002 changes only tokenizer cardinality admission: the tokenizer is still trained from TRAIN only with requested 16,384 vocabulary, while actual corpus-dependent vocabulary may be between 258 and 16,384. The B0 model vocabulary remains exactly 16,384 and no artificial tokens may pad the tokenizer.

Current next gate is `ZERO_SCIENCE_QA_AMENDMENT_002`.
