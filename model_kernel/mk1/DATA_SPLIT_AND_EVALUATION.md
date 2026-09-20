# MK-1 Data Split, Evaluation and Falsification Contract v0.1

Status: **FROZEN / AMENDED BY PREREGISTRATION_AMENDMENT_001 / NO DATA MATERIALIZED**

Date: **2026-09-21**

Original pre-amendment evaluation blob:

`9b07e5ade54054c5717bd54e3417c88bff9dff39`

## 1. Split principle

MK-1 measures generalization across semantic-scene and surface-form novelty.

All variants of one canonical semantic scene remain in exactly one split.

No canonical scene ID, surface template family reserved for held-out construction, or paraphrase cluster may cross its frozen boundary.

## 2. Reserved generation namespaces

- TRAIN: `7101000..7102999` — 2,000 canonical scenes;
- VALIDATION: `7103000..7103399` — 400 canonical scenes;
- PRISTINE_CONFIRMATORY: `7104000..7104599` — 600 canonical scenes.

These are scene-generation namespaces, not model-training seeds.

If support/integrity gates cannot be met, do not silently extend a namespace. A pre-outcome amendment is required.

## 3. Surface multiplicity

Each canonical scene must have at least two semantics-preserving surface realizations.

At least one confirmatory realization per scene must come from a surface-construction route not used for TRAIN realization families.

The renderer/toolchain and family partition must be implementation-locked before generation.

## 4. Composition coverage

PRISTINE_CONFIRMATORY must include:

- every primary Z1 family;
- every admitted Z3 scope level;
- every Z4 register field in both supported positive/negative states where logically possible;
- at least 30% multi-factor scenes with two or more independently scorable mechanisms.

Primary classes must satisfy TARGET_STABILITY_AUDIT.md support gates.

## 5. Pristine integrity

Before any neural training, target/data integrity additionally requires:

- gold C == frozen R(gold Z) for 100% of scenes;
- all C fields pass the same observable-identifiability audit as Z;
- target-stability support/margin gates PASS on the materialized pre-confirmatory contract.

Before confirmatory inference:

- raw-text duplicate count against TRAIN/VALIDATION = 0;
- canonical-scene duplicate count = 0;
- prohibited held-out renderer/template-family overlap = 0;
- gold targets frozen before model prediction;
- confirmatory execution count = 0.

Confirmatory evaluation is one-shot per frozen checkpoint set.

## 6. Frozen decoding

Binary prediction:

`logit >= 0 -> true`

Categorical prediction:

deterministic argmax; exact ties choose lowest frozen class index.

No validation-derived decision threshold is allowed.

## 7. H1a metrics — M1-Z detailed representation

### Z1

- micro precision;
- micro recall;
- macro F1 over supported classes;
- exact-set match.

### Z2

Categorical:

- comparator accuracy;
- temporal-precision accuracy.

Continuous, only when present:

`nAE = |prediction-gold| / max(|gold|, 1 canonical unit)`

Report per scalar:

- mean nAE;
- 95th percentile nAE.

### Z3

- evidence-scope accuracy;
- asserted-scope accuracy;
- scope-relation accuracy.

### Z4

For the fixed seven-field register:

- pooled binary precision;
- pooled binary recall;
- macro F1 over supported fields.

### Recomposed C

- C1 macro F1;
- C2 evidence-scope accuracy;
- C3 asserted-scope accuracy;
- C4 scope-relation accuracy;
- C5 macro F1;
- canonical-state field accuracy;
- full-state exact match.

### Invariance

For every semantics-preserving surface cluster, compare recomposed C predictions.

Cluster-consistent iff all surfaces produce the same decoded C.

Report fraction of consistent clusters.

## 8. H1a absolute gates

M1-Z H1a PASS requires all:

1. Z1 micro precision >= 0.95;
2. Z1 micro recall >= 0.95;
3. Z1 macro F1 >= 0.90;
4. Z3 scope-relation accuracy >= 0.95;
5. Z4 pooled precision >= 0.95;
6. Z4 pooled recall >= 0.90;
7. recomposed C canonical-state field accuracy >= 0.95;
8. invariance-cluster consistency >= 0.95;
9. no supported primary Z1 or Z4 binary class has recall < 0.80;
10. target-stability PASS;
11. observable-identifiability PASS;
12. each supported continuous Z2 scalar has mean nAE <= 0.05 and 95th percentile nAE <= 0.10.

H1b/H1c cannot rescue H1a failure.

## 9. H1b — matched direct-vs-structured comparison

B0-DIRECT and M1-Z are compared only on canonical C.

For each evaluated scene define the five-component canonical score from aggregate metrics:

1. C1 macro F1;
2. C2 evidence-scope accuracy;
3. C3 asserted-scope accuracy;
4. C4 scope-relation accuracy;
5. C5 macro F1.

The reported canonical-state balanced score is their unweighted mean.

For paired bootstrap, resample canonical scenes with replacement and recompute the complete five-component score for each arm on every resample.

Primary effect:

`Delta_C = score(R(M1-Z)) - score(B0-DIRECT)`

Gate:

- point >= +0.03;
- 95% paired whole-scene bootstrap lower bound > 0.

If H1a passes but H1b fails:

`LEARNED_REPRESENTATION_SUPPORTED_FACTORISATION_NOT_ESTABLISHED`

## 10. H1c — comparison with D-PIT

Use only fields with exact semantic correspondence between frozen PIT-v3 and MK-1.

For the common-field set:

- compute pooled representation error for M1-Z and D-PIT;
- report exact field/scene coverage;
- relative error reduction >= 20%;
- whole-scene bootstrap 95% lower bound >= 10%;
- M1-Z primitive precision may not be lower than D-PIT by more than 0.02 absolute.

If H1a/H1b pass but H1c fails:

`STRUCTURED_FACTORISATION_SUPPORTED_NO_DETERMINISTIC_CEILING_BREAK`

No deterministic-ceiling-break claim is allowed.

## 11. Formal adjudication order

1. data/split integrity;
2. target stability;
3. observable identifiability;
4. tokenizer contract;
5. B0 reconstruction;
6. implementation/matching integrity;
7. M1-Z H1a absolute gates;
8. H1b canonical-state paired comparison;
9. H1c D-PIT common-field comparison.

Terminal outcomes:

- pre-training integrity/target/identifiability/tokenizer failure:
  `MK1_INVALID_BEFORE_TRAINING`
- H1a FAIL:
  `LEARNED_STRUCTURED_REPRESENTATION_NOT_SUPPORTED`
- H1a PASS, H1b FAIL:
  `LEARNED_REPRESENTATION_SUPPORTED_FACTORISATION_NOT_ESTABLISHED`
- H1a PASS, H1b PASS, H1c FAIL:
  `STRUCTURED_FACTORISATION_SUPPORTED_NO_DETERMINISTIC_CEILING_BREAK`
- all PASS:
  `MK1_LEARNED_STRUCTURED_REPRESENTATION_SUPPORTED`

## 12. STOP rules

After a valid scientific FAIL:

- no threshold tuning;
- no seed replacement;
- no hidden-width/depth increase;
- no latent arm;
- no memory/history/future probe;
- no MK-2 decision loss;
- no regeneration of pristine confirmatory data;
- no direct-C auxiliary loss added to M1-Z;
- no Z auxiliary loss added to B0-DIRECT.

A new attempt requires a new uncertainty and new preregistration.

## 13. MK-2 boundary

MK-1 does not establish final decision sufficiency.

A full MK-1 PASS authorizes only designing MK-2.
