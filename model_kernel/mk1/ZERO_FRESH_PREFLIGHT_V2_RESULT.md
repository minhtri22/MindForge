# MK-1 Canonical Zero-Fresh Preflight V2 Result

Status: **PASS**

Date: **2026-09-21**

Formal verdict:

`ZERO_FRESH_PREFLIGHT_V2_PASS`

## 1. Canonical execution

Valid replacement run:

`35553426498`

Head:

`9158031d43b5e4c05e11e672a75485f216a304dd`

The earlier run `35553272015` is excluded as `INVALID_BEFORE_ZERO_FRESH_EXECUTION` because it failed the authorization guard before dependencies/tests/preflight.

## 2. Artifact

- artifact name: `mk1-zero-fresh-preflight-v0-2`
- artifact id: `10619885524`
- artifact ZIP SHA-256: `37a5050c581e1934740334b573110cebc5ac32bdd0760e8bac620b99750053b1`
- size: 816 bytes

Schema:

`MK1-ZERO-FRESH-PREFLIGHT-v0.2`

## 3. Test suite

Combined legacy MKS + MK-1 tests:

`16 passed in 3.33s`

Result:

**PASS**

The suite includes independent observable-text reconstruction tests on non-scientific fixture scenes.

## 4. Core implementation gates

- B0 parameter count: `10,339,200` — PASS
- hidden-state exact-logit parity: true — PASS
- B0-DIRECT parameters: `10,350,114` — PASS
- M1-Z parameters: `10,361,670` — PASS
- parameter gap fraction: `0.001115264238293634` — PASS
- tensor slices: PASS
- zero readout initialization: PASS
- recomposer identities: PASS
- fixture gold C == R(gold Z): PASS
- direct synthetic loss finite: true
- M1-Z synthetic loss finite: true
- paired synthetic schedule: true
- synthetic tokenizer plumbing: PASS

## 5. Amendment-003 projected generator QA

Projected ordinals only were used. No reserved scientific scene ID was invoked.

Observed:

- projected TRAIN scenes: 2,000
- projected confirmatory scenes: 600
- projected total scenes: 3,000
- canonical Z signatures unique: true
- every projected scene has at least one scalar: true
- confirmatory multi-factor fraction: `1.0`
- H1c scope-relation exact-correspondence coverage: `0.719`

Minimum support:

| Gate | TRAIN | PRISTINE_CONFIRMATORY |
|---|---:|---:|
| Z1 positive class | 180 | 54 |
| Z2 scalar presence | 333 | 100 |
| scope-relation class | 500 | 150 |
| Z4 positive/negative binary cell | 500 | 150 |
| C1 positive/negative binary cell | 400 | 120 |
| C5 positive/negative binary cell | 500 | 150 |

Frozen support requirements:

- TRAIN >= 100
- PRISTINE_CONFIRMATORY >= 40

All projected support gates PASS.

Target-margin gate:

`NOT_APPLICABLE_NO_THRESHOLD_DERIVED_PRIMARY_HARD_TARGETS`

## 6. Zero-fresh boundary

Artifact records:

- scientific_namespace_touched = false
- scientific_seed_touched = false
- scientific_data_created = false

No scientific tokenizer was fitted.

No scientific training occurred.

## 7. Scientific interpretation

This result supports only:

- Amendment-003 generator schedule is mechanically capable of satisfying prospective support/integrity requirements;
- independent observable parser can recover fixture Z/C;
- implementation V2 remains compatible with B0 and the frozen neural contracts.

It does not prove actual materialized data pass split/duplicate/identifiability audits.

It does not prove learnability or any H1a/H1b/H1c model outcome.

## 8. Authorization

The next and only newly authorized scientific action is:

`ONE_SHOT_SCIENTIFIC_MATERIALIZATION_AND_PRETRAINING_DATA_AUDIT_v0.1`

The run may create the reserved data exactly once and audit it.

Scientific tokenizer fitting remains blocked until the actual materialized data audit PASS.

Neural training remains blocked.
