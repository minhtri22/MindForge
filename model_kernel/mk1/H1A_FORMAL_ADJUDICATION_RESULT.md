# MK-1 H1a Formal Adjudication v0.1

Status: **FORMALLY ADJUDICATED / H1A FAIL**

Date: **2026-09-23**

Formal H1a verdict:

`H1A_FAIL`

Preregistered MK-1 terminal verdict:

`LEARNED_STRUCTURED_REPRESENTATION_NOT_SUPPORTED`

## 1. Canonical one-shot execution

- workflow: `MK1 H1a One-Shot Confirmatory`
- run: `35888512940`
- execution head: `84a1e9db50ad0dc32200c68ed372ec7c12e486fe`
- run conclusion: `SUCCESS`

Frozen evidence artifact:

- artifact ID: `10763618301`
- name: `mk1-h1a-confirmatory-v0-1`
- ZIP SHA-256: `ac8ef000f58e3f529bfd1d8b5e7fd31f13e338020985101d12a3e4794cac261e`
- internal checksum entries: `12`
- internal checksum mismatches: `0`
- predictions: `1200` per seed × `5` seeds

The execution manifest binds the exact materialization, tokenizer bundle, five M1-Z frozen training artifacts, run ID, and execution HEAD.

## 2. Frozen adjudication rule

The seed-level rule was frozen before any PRISTINE_CONFIRMATORY model inference:

`H1A_PASS iff all five preregistered M1-Z seeds individually pass every H1a absolute gate.`

No seed averaging, replacement, exclusion, pooling, voting, or best-seed selection is permitted for the formal H1a verdict.

## 3. Per-seed result

| Seed | Z1 P | Z1 R | Z1 macro F1 | Z3 relation acc. | Z4 P | Z4 R | C field acc. | Invariance | Verdict |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 71001 | 0.9074 | 0.7978 | 0.8354 | 0.8733 | 0.9234 | 0.9319 | 0.8781 | 0.0983 | FAIL |
| 71002 | 0.8520 | 0.7375 | 0.7474 | 0.8600 | 0.9189 | 0.9411 | 0.8792 | 0.0850 | FAIL |
| 71003 | 0.8827 | 0.8062 | 0.8136 | 0.8992 | 0.9390 | 0.9350 | 0.9015 | 0.2400 | FAIL |
| 71004 | 0.8998 | 0.8149 | 0.8371 | 0.9258 | 0.9574 | 0.9525 | 0.9141 | 0.1450 | FAIL |
| 71005 | 0.9313 | 0.8379 | 0.8661 | 0.9342 | 0.9672 | 0.9542 | 0.9220 | 0.2533 | FAIL |

Frozen H1a thresholds relevant to this table:

- Z1 micro precision >= 0.95
- Z1 micro recall >= 0.95
- Z1 macro F1 >= 0.90
- Z3 scope-relation accuracy >= 0.95
- Z4 pooled precision >= 0.95
- Z4 pooled recall >= 0.90
- canonical-state field accuracy >= 0.95
- invariance-cluster consistency >= 0.95

## 4. Gate pattern

All five seeds fail:

- G01 Z1 micro precision;
- G02 Z1 micro recall;
- G03 Z1 macro F1;
- G04 Z3 scope-relation accuracy;
- G07 canonical field accuracy;
- G08 invariance-cluster consistency;
- G09 supported-class recall floor;
- G12 continuous Z2 scalar accuracy.

G05 Z4 pooled precision:

- fails 71001, 71002, 71003;
- passes 71004, 71005.

G06 Z4 pooled recall passes all five seeds.

G10 target-stability prerequisite and G11 observable-identifiability prerequisite remain PASS.

## 5. Continuous Z2 failure

For every seed, every supported scalar fails both the frozen mean-nAE and p95-nAE limits.

Observed mean nAE values are approximately `0.976..1.001`, versus the frozen maximum `0.05`.

Observed p95 nAE values are approximately `0.993..0.999`, versus the frozen maximum `0.10`.

This is not a threshold-edge failure.

## 6. Invariance failure

Invariance-cluster consistency by seed:

- 71001: `0.0983`
- 71002: `0.0850`
- 71003: `0.2400`
- 71004: `0.1450`
- 71005: `0.2533`

Frozen gate:

`>= 0.95`

This is also not a threshold-edge failure.

## 7. Scientific interpretation boundary

The valid conclusion is limited to the preregistered H1a claim:

> Under the frozen MK-1 architecture, supervision, training contract, five scientific seeds, checkpoint-selection rule, and pristine confirmatory distribution, M1-Z did not satisfy the frozen absolute semantic-representation gates.

The evidence does **not** by itself establish why the representation failed.

In particular, this adjudication does not independently prove:

- insufficient model capacity;
- wrong factorization;
- wrong optimizer;
- impossible learnability;
- a failure of structured representation as a general idea.

Those would require new, separately preregistered hypotheses.

## 8. Sequential adjudication consequence

The preregistration states:

`H1b/H1c cannot rescue H1a failure.`

Therefore:

- H1b: **BLOCKED / NOT AUTHORIZED**
- H1c: **BLOCKED / NOT AUTHORIZED**
- no DIRECT confirmatory comparison is opened;
- no D-PIT confirmatory comparison is opened.

The preregistered terminal MK-1 verdict is:

`LEARNED_STRUCTURED_REPRESENTATION_NOT_SUPPORTED`

## 9. Anti-rescue boundary

No current MK-1 rescue is authorized:

- no threshold tuning;
- no seed replacement;
- no checkpoint reselection;
- no hidden-width/depth increase;
- no direct-C auxiliary loss;
- no regeneration of PRISTINE_CONFIRMATORY;
- no selective confirmatory rerun.

Any further investigation must begin from a new uncertainty and a new preregistered research question.
