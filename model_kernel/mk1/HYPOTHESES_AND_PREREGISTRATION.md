# MK-1 — Learned Structured Decision-State Representation v0.1

Status: **FROZEN PREREGISTRATION CANDIDATE / ZERO-SCIENCE QA PENDING**

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

### H1b — factorized structure adds value over matched direct learning

Under matched neural substrate, parameters, data, seeds, and compute, M1-Z improves the balanced representation score over B0-DIRECT by the frozen paired threshold.

### H1c — learned representation exceeds the frozen deterministic route

On fields shared with PIT-v3, M1-Z materially reduces representation error relative to D-PIT while preserving high precision.

These hypotheses are adjudicated sequentially. H1b/H1c cannot rescue H1a failure.

## 4. Frozen intervention and baselines

Exactly three routes:

```
B0-DIRECT  — matched learned direct/monolithic representation
D-PIT      — frozen deterministic PIT-v3 representation
M1-Z       — learned structured/factorized Z1-Z4 representation
```

No fourth latent arm is authorized.

Detailed contract:

`BASELINES_AND_MATCHING.md`

blob:

`dec5747a7bf11857bcddcda25f3f431ced9f3156`

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

`90849d77dbcd9fabdbd67b735ba9296a3d0756a5`

## 6. Target stability prerequisite

Before model training:

- categorical targets must be deterministically re-derivable;
- semantics-preserving variants must retain identical gold target;
- threshold-derived labels must retain their generating quantity;
- brittle near-margin hard labels cannot be primary endpoints.

Contract:

`TARGET_STABILITY_AUDIT.md`

blob:

`9cfe8ad74a821b09135366c010ece962787a4ab9`

## 7. Observable-identifiability prerequisite

Every target field must trace to information observable in the current serialized input.

Future/counterfactual outcomes, hidden simulator truth, final actions, retrieved memory, and later turns are forbidden.

Contract:

`OBSERVABLE_IDENTIFIABILITY_CONTRACT.md`

blob:

`2d5b5f92a8787c244dc13f1b4d1111054d30ee71`

## 8. Frozen structured representation schema

M1-Z uses a shared B0 Transformer body and factorized Z1-Z4 readout heads.

A deterministic evaluation-only recomposer may recombine predicted factors into canonical semantic state.

There is no learned controller and no latent rescue arm.

Schema:

`STRUCTURED_Z_SCHEMA.md`

blob:

`cb9ad4a9e546b086502f56f9151809eb7f3b0fc4`

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

`9b07e5ade54054c5717bd54e3417c88bff9dff39`

## 10. Neural matching contract

B0-DIRECT and M1-Z must match:

- B0 body;
- initialization family;
- tokenizer/context;
- train/validation samples;
- five paired training seeds `71001..71005`;
- optimizer family;
- training steps;
- effective batch;
- processed training tokens within 1%;
- trainable parameter count within 1%.

No failed seed replacement is allowed.

D-PIT remains an unmatched deterministic comparator and cannot support compute-efficiency claims.

## 11. Primary metrics and gates

The authoritative thresholds are frozen in DATA_SPLIT_AND_EVALUATION.md.

M1-Z absolute PASS requires, among other gates:

- Z1 micro precision >= 0.95;
- Z1 micro recall >= 0.95;
- Z1 macro F1 >= 0.90;
- Z3 scope-relation accuracy >= 0.95;
- Z4 edge precision >= 0.95;
- Z4 edge recall >= 0.90;
- recomposed canonical-state field accuracy >= 0.95;
- invariance-cluster consistency >= 0.95;
- no supported primary class recall < 0.80.

M1-Z vs B0-DIRECT:

- balanced-score improvement >= +0.03;
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
4. B0 reconstruction and arm matching;
5. M1-Z absolute gates;
6. M1-Z vs B0-DIRECT;
7. M1-Z vs D-PIT.

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

## 15. Current authorization state

This preregistration candidate authorizes **documentation and zero-science QA only**.

It does not authorize:

- MK-1 model-code changes;
- data materialization;
- training;
- workflow execution;
- scientific outcome inspection.

After zero-science QA PASS, the next gate is exact B0 reconstruction / implementation planning under the frozen specification.
