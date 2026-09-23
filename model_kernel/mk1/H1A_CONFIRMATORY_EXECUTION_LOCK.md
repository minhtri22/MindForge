# MK-1 H1a Confirmatory Execution Lock v0.1

Status: **CANDIDATE / INFRASTRUCTURE ONLY / PRISTINE INFERENCE NOT YET AUTHORIZED**

Date: **2026-09-23**

This document is an implementation/infrastructure lock. It is not itself a scientific result.

## 1. Scientific boundary

The next scientific action is exactly one H1a PRISTINE_CONFIRMATORY inference over the five frozen M1-Z best checkpoints.

This infrastructure lock must not:

- change a scientific metric or threshold;
- change the five-seed rule;
- change any model checkpoint;
- change tokenizer/data membership;
- compute H1b or H1c;
- execute confirmatory inference before lock PASS.

## 2. Frozen H1a specification

- file: `model_kernel/mk1/H1A_CONFIRMATORY_ADJUDICATION_SPEC.md`
- blob: `8cbeff53c5f7ac2b91312621c9fdaaef5c57bb63`
- seed verdict rule: all five preregistered M1-Z seeds must individually pass all H1a gates.

## 3. Frozen evaluator

- file: `experiments/model_core/mk1/h1a_confirmatory.py`
- blob: `3492ccda1ef6c297d8626da080c4faaf302fb2b3`

Authoritative frozen dependencies:

- `metrics.py` blob `22e97e9ad29f3b483b8f100a363a934dc7612e1b`
- `recompose.py` blob `5e1ce91c4e6c176f7b6392adc35d96b36851219a`
- `modeling.py` blob `f6f79e044a7787d604b46b41a0c68b423cc600ab`
- `contracts.py` blob `cb9d8c067586dfc52b8b23cac7b88868b7498a9f`
- `mindforge/config.py` blob `91a3f92ea2449a82fb2d03e0442cbf6e72980caf`
- `mindforge/model.py` blob `b585945631a027fb1f124c780fc5f7fd330c0287`
- `mindforge/tokenizer.py` blob `68c7d687c684c800c98344e26be7c75425ea528f`

## 4. Zero-PRISTINE preflight evidence

Latest valid preflight:

- workflow: `MK1 H1a Confirmatory Preflight`
- run: `35787647479`
- head: `d18e7ee894a5a903d0088ac414a8f0926b561a7c`
- conclusion: `SUCCESS`
- fixture-only tests: `5 passed`

Earlier failed preflight runs are infrastructure-invalid and produced no confirmatory inference.

## 5. Frozen confirmatory workflow

- file: `.github/workflows/mk1-h1a-confirmatory.yml`
- blob: `eea31f74a0dc27a6deedd521c5ab9dfe9c4deb94`
- trigger path only: `model_kernel/mk1/H1A_CONFIRMATORY_TRIGGER_v0.1.md`
- no `workflow_dispatch`
- no scheduled trigger
- one confirmatory job
- one inference step
- one evidence upload step

The workflow contains zero DIRECT training-artifact references and zero H1b/H1c evaluation function references.

## 6. Exact frozen upstream artifacts

Materialization:

- artifact `10619711251`
- run `35553551910`
- artifact ZIP SHA-256 `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`
- PRISTINE file SHA-256 `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`

Tokenizer bundle:

- artifact `10629399106`
- run `35581007427`
- artifact ZIP SHA-256 `56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af`
- tokenizer SHA-256 `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

M1-Z best-checkpoint artifacts:

| Seed | Artifact | ZIP SHA-256 | best.pt SHA-256 | best step |
|---:|---:|---|---|---:|
| 71001 | 10635575980 | e413ce076530b7e47dfdd3ebaf518d8165f53d9e8a25ac05ea166a65dabf5a0f | 84c5c163877afb74caf9de4c72945b3c801bc6ff7ebdd701f6f03d40d850b699 | 5000 |
| 71002 | 10638036281 | 0f9b483a5f8979a92ec330974e56564e292737b5ba4185f081d384f88ba4bf13 | 0ed0d152f27ea9e3f8219ae3f47c5c205507296ac47181761df03672755bf1e3 | 3500 |
| 71003 | 10641678365 | 0df985887c5d4c58704317c5885574abee69d8ef63312568896c40954cc6826b | def7b229623fbca317f064b3d4af6156323dbfb34497954a28456ec3b29c7d12 | 5000 |
| 71004 | 10644396601 | 45d8c286954565cf0276105db87cebe01cbde14d1cb1446678f466f7d67b908a | 207a1443acb6266a699fe223b492bd2881857c3d2dbda0d21ee8b7e2b6087fd7 | 4750 |
| 71005 | 10647387273 | d107361f967f8ace604ba6cc8d53b4d1b6055178ee296b3bbe51f5f5581c06f1 | 5f37529a4948948b0e5a362c46f455b87ff65b5fb4d63027d294365f08313282 | 3000 |

No DIRECT checkpoint is admissible for H1a.

## 7. Runtime

Frozen evaluation runtime:

- Python 3.12
- numpy 2.5.2
- tokenizers 0.21.4
- psutil 7.2.2
- torch 2.12.1 CPU
- float32
- `PYTHONHASHSEED=0`
- `OMP_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`

## 8. Execution constraints

The confirmatory workflow must:

1. verify exact source blobs;
2. verify exact GitHub artifact names, digests, expiry state and originating run IDs;
3. download only the exact materialization, tokenizer-bundle and five M1-Z artifacts above;
4. verify all ZIP SHA-256 values;
5. verify exact PRISTINE/tokenizer/best.pt hashes before inference;
6. invoke the frozen evaluator exactly once;
7. require 1200 predictions for each of five seeds;
8. require formal status `H1A_PASS` or `H1A_FAIL`;
9. require `h1b_computed=false` and `h1c_computed=false`;
10. archive per-seed predictions/results, formal adjudication and execution manifest.

## 9. Trigger boundary

At candidate-lock time, `H1A_CONFIRMATORY_TRIGGER_v0.1.md` must not exist.

Only an independent infrastructure review PASS may authorize creation of that trigger.

## 10. Review verdict

Candidate status:

`H1A_CONFIRMATORY_EXECUTION_LOCK_REVIEW_REQUIRED`

No PRISTINE model inference is authorized by this candidate document.
