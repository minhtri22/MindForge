# MK-1 Zero-Science QA — Amendment 001

Status: **PASS**

Date: **2026-09-21**

Formal verdict:

`ZERO_SCIENCE_QA_AMENDMENT_001_PASS`

This QA evaluates only preregistration consistency after Amendment 001. It does not execute MK-1 scientific data generation, tokenizer fitting, model training, validation, or confirmatory inference.

## 1. Trigger

Matching feasibility review:

`MATCHING_FEASIBILITY_REVISE`

Review blob:

`981942426e2933579e733e347bafd78cbbc1284d`

Amendment 001:

- commit: `4d8e9a8e9e22e17ee35270991e027526600296bf`
- blob: `0ec12864118e1b95d579318edab0dc8c00552656`

## 2. Authoritative post-amendment package

- TARGET_ONTOLOGY.md — `65b152f54b7f2bb7ea45e97a433443e0956a7d11`
- TARGET_STABILITY_AUDIT.md — `e4dfd62eb4aeb14595d03e299a753ac6711d9547`
- OBSERVABLE_IDENTIFIABILITY_CONTRACT.md — `53e37771fd3244df7f4c461305963afc7ff12221`
- STRUCTURED_Z_SCHEMA.md — `045cafa9a8cc6bc9b207da9915f47f982152fbaa`
- BASELINES_AND_MATCHING.md — `82517e3cb4d03b0cdc6fb6c99a289ad935372623`
- DATA_SPLIT_AND_EVALUATION.md — `5192a273e36911d5c9598f2de19884b71525c083`
- B0_RECONSTRUCTION.md — `173dd942fd703755dd253d785ca5f3993cbd5c38`
- HYPOTHESES_AND_PREREGISTRATION.md binding before this QA — `53a8f0211225bc59e1a34cbd6c548509b7c956ef`

## 3. Finding closure

### F1 — algebraically null H1b contrast

Original risk:

monolithic versus split linear heads could represent the same function over the same targets.

Correction:

- B0-DIRECT predicts canonical C directly;
- M1-Z predicts detailed Z and reaches C only through frozen deterministic R.

Result:

**CLOSED**

The intervention is now structured intermediate supervision/recomposition versus direct canonical supervision.

### F2 — under-specified Z2

Correction freezes:

- comparator: 4 logits;
- temporal precision: 3 logits;
- four scalar slots;
- exact scalar masks;
- exact normalized SmoothL1 training form;
- exact confirmatory nAE metrics/gates.

Result:

**CLOSED**

### F3 — under-specified Z4 graph

Correction removes the variable candidate graph from MK-1 v0.1.

Z4 is exactly seven binary observable relation/support fields.

Result:

**CLOSED**

### F4 — missing historical Phase-2 tokenizer/data

Correction:

- historical checkpoint is compatibility evidence only;
- it is not MK-1 scientific initialization;
- one tokenizer will later be fitted from TRAIN surfaces only;
- VALIDATION/PRISTINE surfaces cannot fit the tokenizer;
- exact vocab size 16,384 is a hard pre-training gate.

Result:

**CLOSED AS AN IMPLEMENTATION BOUNDARY**

No historical Phase-2 metric parity claim is made.

## 4. Additional QA findings repaired before PASS

### QA-A — stale B0 document blob reference

A preregistration binding referenced the wrong B0 reconstruction document blob.

Correct current blob:

`173dd942fd703755dd253d785ca5f3993cbd5c38`

Repair commit:

`1d07b6deb9c531d8fa439be8debc972353141628`

No scientific contract changed.

### QA-B — C target audit boundary

Because B0-DIRECT learns C directly, C must satisfy the same target-integrity and observable-identifiability boundary as Z.

Corrections require:

- complete field contract for Z and C;
- zero forbidden-information dependence for Z or C;
- `gold C == R(gold Z)` for 100% of admitted scenes.

Relevant commits:

- `1c69881687d0764e589f57c4fa44c3bee68a4fdb`
- `f34554a3530125ced88cedcb04e737f5f4c5fb92`
- `599b4ed777c50239db3ae34c75163be4fad5f007`

### QA-C — stability-gate numbering

The first consistency edit accidentally swapped the documented failure consequence for the near-margin gate and the support-count gate.

Final mapping:

- gate 6 failure -> `HARD_TARGET_UNSTABLE`;
- gate 7 failure -> `TARGET_SUPPORT_INSUFFICIENT`.

Repair commit:

`b0e97fbd6fe0c87bfc050e6fd37601511011e158`

### QA-D — ambiguity contract versus frozen output vocabulary

The pre-amendment identifiability document allowed adding UNKNOWN/AMBIGUOUS/SET-VALUED targets, but Amendment 001 freezes exact output vocabularies.

Final rule:

- an underdetermined primary scene is not admissible;
- exclusion is recorded before training;
- no point label may be forced;
- no new dynamic class may be added.

Repair commit:

`1f03e3855b4f77a07c6f375c50a782d0c485a00b`

## 5. Dimensional and parameter arithmetic

Z dimensions:

`32 + 11 + 20 + 7 = 70`

C dimensions:

`8 + 8 + 8 + 4 + 6 = 34`

M1-Z readout:

`321 * 70 = 22,470`

M1-Z total:

`10,339,200 + 22,470 = 10,361,670`

B0-DIRECT readout:

`321 * 34 = 10,914`

B0-DIRECT total:

`10,339,200 + 10,914 = 10,350,114`

Difference:

`11,556`

Relative difference versus larger arm:

approximately `0.112%`

Frozen maximum:

`1.0%`

Result:

**PASS**

## 6. Causal-identifiability checks

PASS:

- same B0 body;
- same pooling boundary;
- same current-input information;
- same TRAIN scenes and tokenizer;
- same paired model seeds;
- same optimizer/schedule/steps/effective batch contract;
- direct arm has C supervision only;
- structured arm has Z supervision only;
- R is deterministic and parameter-free;
- no final policy/action target exists;
- no memory/history/future/counterfactual input exists;
- no latent rescue arm exists.

## 7. Target-integrity checks

PASS:

- exact Z vocabulary/layout frozen;
- exact C layout frozen;
- binary threshold frozen at logit >= 0;
- categorical decoding frozen to deterministic argmax;
- continuous Z2 has fixed scale/error definition;
- ambiguous primary scenes cannot enter;
- gold C must equal R(gold Z) exactly;
- target stability/margin audit remains pre-training;
- support-count audit remains pre-training.

## 8. Data/tokenizer leakage checks

PASS at specification level:

- TRAIN/VALIDATION/PRISTINE namespaces remain disjoint;
- all surfaces of one scene stay in one split;
- tokenizer fit is TRAIN-only;
- confirmatory surfaces never fit tokenizer;
- held-out renderer-family requirement remains frozen;
- one-shot confirmatory rule remains frozen.

## 9. Repository-scope check

Compared with Model Core head before B0/implementation-gate work:

`50c9f962e3a16a90318ab5346ea5938d0e576b62`

the work up to this QA contains:

- documentation;
- one B0 reconstruction workflow.

It contains:

- zero changes under `mindforge/`;
- zero new/changed scientific data under `experiments/`;
- zero MK-1 model implementation;
- zero MK-1 tokenizer fitting;
- zero MK-1 training.

## 10. Historical QA boundary

`ZERO_SCIENCE_QA.md` remains valid historical evidence for the original v0.1 package only.

This document supersedes it for the amended preregistration.

No prior frozen result is rewritten.

## 11. Decision

`ZERO_SCIENCE_QA_AMENDMENT_001_PASS`

Amendment 001 is internally coherent enough to permit the next non-scientific gate:

`MK1_IMPLEMENTATION_LOCK`

Still forbidden:

- scientific data materialization;
- tokenizer fitting on scientific TRAIN data;
- neural training;
- validation outcome inspection;
- pristine-confirmatory inference.
