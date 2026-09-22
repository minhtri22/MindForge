# MK-1 H1a Confirmatory Adjudication Specification v0.1

Status: **FROZEN BEFORE PRISTINE_CONFIRMATORY MODEL INFERENCE**

Date: **2026-09-23**

Pre-confirmatory HEAD:

`a7e4f64fba80e1d38ef0d721e72d124b0ed8c733`

## 1. Scope

This specification authorizes H1a adjudication only.

It does not authorize:

- H1b comparison;
- H1c comparison;
- DIRECT confirmatory inference;
- D-PIT execution;
- retraining;
- checkpoint reselection;
- seed replacement;
- threshold tuning;
- data regeneration.

H1a asks whether the frozen learned structured representation M1-Z satisfies the preregistered absolute semantic-representation gates on PRISTINE_CONFIRMATORY.

## 2. Why a pre-confirmatory seed rule is required

The preregistration freezes five scientific training seeds `71001..71005`, freezes all H1a metric thresholds, forbids failed-seed replacement, and defines the H1a metric bundle.

The original documents do not state an explicit cross-seed H1a aggregation operator.

This ambiguity is closed **before any PRISTINE_CONFIRMATORY model prediction is produced**.

Frozen seed-level adjudication rule:

`H1A_PASS iff every one of the five preregistered M1-Z seeds individually passes every H1a absolute gate.`

No seed averaging, pooling, voting, replacement, exclusion, or best-seed selection is permitted for the formal H1a verdict.

Rationale:

- H1a gates are absolute, not paired-effect gates;
- all five seeds are preregistered scientific executions;
- no failed seed may be replaced;
- the rule prevents an easy seed from masking a failed seed;
- no H1a confirmatory outcome exists at freeze time.

This clarification changes no metric, threshold, checkpoint, seed, data row, model, or decoding rule.

## 3. Frozen confirmatory data

Canonical materialization:

- run `35553551910`
- artifact `10619711251`
- ZIP SHA-256 `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

PRISTINE_CONFIRMATORY:

- scenes: `600`
- surfaces: `1200`
- scene IDs: `7104000..7104599`
- source SHA-256: `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`

This is the only confirmatory dataset authorized for H1a.

## 4. Frozen tokenizer

Training-only bundle:

- run `35581007427`
- artifact `10629399106`
- ZIP SHA-256 `56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af`

Tokenizer file:

- SHA-256 `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

No tokenizer fit or modification is authorized.

## 5. Frozen M1-Z checkpoint artifacts

Only these five frozen scientific-training artifacts are admissible:

| Seed | Artifact | Artifact ZIP SHA-256 | Frozen best step |
|---:|---:|---|---:|
| 71001 | `10635575980` | `e413ce076530b7e47dfdd3ebaf518d8165f53d9e8a25ac05ea166a65dabf5a0f` | 5000 |
| 71002 | `10638036281` | `0f9b483a5f8979a92ec330974e56564e292737b5ba4185f081d384f88ba4bf13` | 3500 |
| 71003 | `10641678365` | `0df985887c5d4c58704317c5885574abee69d8ef63312568896c40954cc6826b` | 5000 |
| 71004 | `10644396601` | `45d8c286954565cf0276105db87cebe01cbde14d1cb1446678f466f7d67b908a` | 4750 |
| 71005 | `10647387273` | `d107361f967f8ace604ba6cc8d53b4d1b6055178ee296b3bbe51f5f5581c06f1` | 3000 |

For each artifact, H1a must consume `best.pt` only.

`latest.pt` is not an admissible substitute.

## 6. Frozen decoding and metrics

Authoritative pre-outcome implementation:

- `experiments/model_core/mk1/recompose.py`
  - blob `5e1ce91c4e6c176f7b6392adc35d96b36851219a`
  - uses binary `logit >= 0` and deterministic argmax;
  - `decode_z_logits`;
  - `recompose_decoded_z`.

- `experiments/model_core/mk1/metrics.py`
  - blob `22e97e9ad29f3b483b8f100a363a934dc7612e1b`
  - `h1a_representation_summary`.

No validation-derived threshold is allowed.

## 7. Frozen H1a gates

Each seed passes only if all are true:

1. Z1 micro precision >= `0.95`;
2. Z1 micro recall >= `0.95`;
3. Z1 macro F1 >= `0.90`;
4. Z3 scope-relation accuracy >= `0.95`;
5. Z4 pooled precision >= `0.95`;
6. Z4 pooled recall >= `0.90`;
7. recomposed C canonical-state field accuracy >= `0.95`;
8. invariance-cluster consistency >= `0.95`;
9. no supported primary Z1 or Z4 field recall < `0.80`;
10. target-stability prerequisite = PASS;
11. observable-identifiability prerequisite = PASS;
12. every supported continuous Z2 scalar has mean nAE <= `0.05` and p95 nAE <= `0.10`.

The materialized pre-training audits already established gates 10 and 11 and they are carried into H1a as immutable prerequisites.

## 8. One-shot execution

Exactly one H1a confirmatory workflow invocation is authorized after an independent execution lock passes.

The invocation must:

- download the exact materialization artifact;
- download the exact training-only tokenizer bundle;
- download the exact five M1-Z artifacts;
- verify all artifact metadata/digests;
- verify PRISTINE source SHA before inference;
- verify tokenizer SHA before inference;
- verify each `best.pt` arm, seed, tokenizer provenance, paired-init provenance and frozen best step;
- evaluate every one of the 1200 PRISTINE surfaces for every one of the five seeds;
- preserve per-surface predictions for reproducibility;
- compute one H1a summary per seed using the frozen metric implementation;
- apply the frozen 12-gate rule per seed;
- assign overall H1a PASS only if all five seed verdicts are PASS.

No rerun is authorized merely because H1a is unfavorable.

## 9. Output evidence

The one-shot artifact must contain:

- exact execution provenance;
- per-seed checkpoint provenance;
- one prediction JSONL per seed for all 1200 surfaces;
- one H1a metric/gate JSON per seed;
- one formal aggregate H1a adjudication JSON;
- environment/runtime identity.

The evaluator must not compute H1b or H1c.

## 10. Stop rule

If the evaluator cannot apply the frozen H1a metrics or gates without changing semantics, stop before confirmatory inference.

If the one-shot execution is valid, its H1a outcome is binding.

H1b remains blocked until H1a is formally adjudicated.
