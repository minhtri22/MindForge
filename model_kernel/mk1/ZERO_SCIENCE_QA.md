# MK-1 Zero-Science QA v0.1

Status: **PASS**

Date: **2026-09-21**

Verdict:

`ZERO_SCIENCE_QA_PASS`

This QA validates only the MK-1 specification/preregistration package. It does not execute data generation, model code, training, inference, or scientific evaluation.

## 1. Package under QA

Frozen supporting blobs:

- TARGET_ONTOLOGY.md — `90849d77dbcd9fabdbd67b735ba9296a3d0756a5`
- TARGET_STABILITY_AUDIT.md — `9cfe8ad74a821b09135366c010ece962787a4ab9`
- OBSERVABLE_IDENTIFIABILITY_CONTRACT.md — `2d5b5f92a8787c244dc13f1b4d1111054d30ee71`
- STRUCTURED_Z_SCHEMA.md — `cb9ad4a9e546b086502f56f9151809eb7f3b0fc4`
- BASELINES_AND_MATCHING.md — `dec5747a7bf11857bcddcda25f3f431ced9f3156`
- DATA_SPLIT_AND_EVALUATION.md — `9b07e5ade54054c5717bd54e3417c88bff9dff39`
- HYPOTHESES_AND_PREREGISTRATION.md — `eb0ff3897823cc72d63529f9acb0b19ce376ac34`

## 2. Governance checks

PASS:

- MK-1 scope is representation formation only.
- MK-2 decision sufficiency remains separate.
- memory is forbidden;
- continual-learning control is forbidden;
- resource control is forbidden;
- invariance objectives are forbidden;
- sparse/runtime mechanisms are forbidden;
- no latent rescue arm is authorized;
- no final action/guardrail target is used as the primary representation target.

## 3. Upstream-evidence checks

PASS:

- PIT-19 is used as negative motivation/comparator, not proof that learning works.
- CQG J3.16 transfers a design lesson, not the 48-D PHI implementation.
- KCL convergence transfers target/identifiability/factorization constraints, not its predictor/controller.
- CQG J3.17+ and KCL post-convergence pivots are not used as blockers for MK-1 representation formation.

## 4. Target checks

PASS:

- target ontology is explicit;
- target stability audit precedes training;
- observable-identifiability contract precedes training;
- underlying continuous quantities are retained for threshold-derived targets;
- ambiguous/underdetermined targets cannot be silently forced to a point label;
- forbidden future/counterfactual information is explicitly excluded.

## 5. Representation checks

PASS:

- Z1/Z2/Z3/Z4 factors are frozen;
- factorization precedes recombination;
- recomposer is evaluation-only and deterministic;
- no controller is present;
- no latent rescue arm is present.

## 6. Baseline and matching checks

PASS:

- exactly three routes are defined: B0-DIRECT, D-PIT, M1-Z;
- primary causal comparison is M1-Z vs B0-DIRECT;
- neural arms share B0 substrate, data, seeds, optimizer family, steps and token budget;
- trainable parameter difference is limited to 1%;
- five paired training seeds are frozen;
- failed seeds cannot be replaced;
- D-PIT is explicitly not compute-matched.

## 7. Split and leakage checks

PASS:

- scene-level split isolation is explicit;
- TRAIN, VALIDATION and PRISTINE_CONFIRMATORY namespaces are disjoint;
- repository search found zero prior uses of namespace anchors `7101000`, `7103000`, `7104000`, and training-seed anchor `71001` at QA time;
- confirmatory scene/template overlap is forbidden;
- confirmatory execution is one-shot;
- support gates must pass before training.

## 8. Metric and threshold checks

PASS after one pre-outcome correction.

Initial QA found that Z2 continuous scoring had a degree of freedom deferred to implementation.

Correction commit:

`75dcb4771c2535a57ebaf5432a43a23672ee1dab`

The final contract now freezes:

`nAE = |prediction-gold| / max(|gold|, 1 canonical unit)`

with primary continuous-field gates:

- mean nAE <= 0.05;
- 95th percentile nAE <= 0.10.

The balanced Z2 score is also explicitly defined.

No scientific data or outcome existed when this correction was made.

## 9. Documentation-integrity checks

PASS after one pre-outcome correction.

Initial QA found a stale literal `\n` and stale J3.14-in-progress text in RESEARCH_ROADMAP.md.

Correction commit:

`d89a7a4ec49edaf006fc589e18c5e88729c2757b`

Final scan:

- no literal escaped newline remains in the audited MK-1 package/roadmap;
- no stale J3.14-in-progress status remains;
- no document states that model training is authorized;
- preregistration references all current supporting blob hashes exactly.

## 10. Repository-delta check

Compared with governance checkpoint:

`69bcd1abf9b297493ed3969a6fb77917f2a8a2ba`

the MK-1 specification work changes only:

- model_kernel/RESEARCH_ROADMAP.md;
- seven files under model_kernel/mk1/ before this QA record.

No model source, dataset, workflow, test, experiment result, or training artifact is changed by the preregistration package.

## 11. Remaining gate

Zero-science QA PASS does **not** authorize MK-1 implementation or training.

The next scientific gate is:

`B0_RECONSTRUCTION_AND_IMPLEMENTATION_LOCK`

Before any MK-1 model code or data materialization, the project must:

1. reconstruct exact B0 source/config/runtime compatibility;
2. freeze implementation mappings from the specification to concrete code/data structures;
3. prove parameter/compute matching can be satisfied;
4. run a zero-fresh implementation preflight;
5. record exact hashes before training authorization.
