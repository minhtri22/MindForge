# MK-1 Training Bundle Construction Lock v0.1

Status: **PASS / BUNDLE CONSTRUCTION HASH LOCKED / ONE RUN AUTHORIZED**

Date: **2026-09-21**

Formal candidate:

`TRAINING_BUNDLE_CONSTRUCTION_LOCK_PASS`

## 1. Governing specification

`model_kernel/mk1/SCIENTIFIC_TRAINING_EXECUTION_ENFORCEMENT_SPEC.md`

- Git blob: `57d8a6a95ae5fd1fdd15ed74feec293a13aebea1`
- SHA-256: `e75a6b78efa03b44e9a33b0023d68af4d0c71c3273f5b8e11bacff201850fbc8`

## 2. Prospective trainer enforcement

`experiments/model_core/mk1/trainer.py`

- Git blob: `a6add27a9751b4d34ca54eb81f54b0e3ac32bb18`
- SHA-256: `15b48da5ecd88f857afd12cd8103af9f90ba532122d90d6c5588d65953deffad`

This prospective edit is not executed by the bundle builder.

## 3. Bundle workflow

`.github/workflows/mk1-training-bundle.yml`

- Git blob: `d5b51c88975ca080d8870c05097f7417af314fb9`
- SHA-256: `cc90b280238971506220226ba838e1cac54a095934c25665717658668840aa49`

The workflow may run only from:

`model_kernel/mk1/TRAINING_BUNDLE_TRIGGER_v0.1.md`

## 4. Canonical source artifacts

Materialization:

- run `35553551910`
- artifact `10619711251`
- digest `sha256:b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Tokenizer:

- run `35562370974`
- artifact `10622602143`
- digest `sha256:3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Paired init/schedules:

- run `35572770344`
- artifact `10626846126`
- digest `sha256:01579c6643003aab615dfd9c530f5c1a0868250072f7e922e8aa90968af88ff3`

## 5. Exact bundle file set

Before manifest:

- `train.jsonl`
- `validation.jsonl`
- `mk1-tokenizer.json`
- `paired_init_seed_71001.pt`
- `paired_init_seed_71002.pt`
- `paired_init_seed_71003.pt`
- `paired_init_seed_71004.pt`
- `paired_init_seed_71005.pt`
- `schedule_seed_71001.jsonl`
- `schedule_seed_71002.jsonl`
- `schedule_seed_71003.jsonl`
- `schedule_seed_71004.jsonl`
- `schedule_seed_71005.jsonl`

Final bundle adds only:

`TRAINING_BUNDLE_MANIFEST.json`

No other file is admissible.

## 6. Construction boundary

The builder may:

- download the three exact canonical source artifacts;
- verify artifact digests;
- copy the exact frozen files listed above;
- verify every copied file SHA-256;
- write the bundle manifest;
- upload the immutable derived bundle.

The builder may not:

- invoke any data generator;
- train or modify a tokenizer;
- instantiate a model;
- create a paired initialization;
- generate a schedule;
- construct an optimizer;
- run forward/backward;
- run scientific training.

## 7. Independent-review gates

Before PASS:

1. all bindings in sections 1–3 re-match HEAD;
2. bundle trigger does not exist;
3. workflow trigger path appears only in push watch and authorization guard;
4. workflow contains the three exact upstream artifact IDs/digests;
5. workflow copies only TRAIN, VALIDATION, tokenizer, five paired-init files and five schedule files;
6. workflow contains no invocation of model/trainer/generator/tokenizer-fit/schedule-RNG/paired-init generation;
7. exact final file-set assertion is present;
8. no training trigger exists.

Only after review may status become:

`TRAINING_BUNDLE_CONSTRUCTION_LOCK_PASS`

This authorizes one bundle-construction run only. It does not authorize optimizer step 1.


## 8. Independent review closure

Independent static review after candidate-lock creation established:

- candidate-lock commit changed only this lock document;
- bundle trigger did not exist during review;
- scientific training trigger did not exist during review;
- workflow blob remained `d5b51c88975ca080d8870c05097f7417af314fb9`;
- trigger path appears exactly twice: push watch and authorization guard;
- all three canonical artifact IDs are hard-bound;
- no `train_arm`, `prepare_paired_initialization`, `deterministic_sample_indices`, `train_tokenizer`, data-generator, optimizer, or model-forward invocation exists;
- exact final bundle file-set assertion is present.

Formal verdict:

`TRAINING_BUNDLE_CONSTRUCTION_LOCK_PASS`

One immutable training-input bundle construction is authorized.

Scientific training remains forbidden.
