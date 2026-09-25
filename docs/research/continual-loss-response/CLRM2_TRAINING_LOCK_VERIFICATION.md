# CLRM2-A Independent Training Lock Verification

Status: **PASS / CLOSED**

Date: 2026-09-25

## Exact verified Training Lock

```text
e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5
```

Training Lock commit:

```text
fde86df15e3d78b5c20b550875af21af47ee5098
```

CLRM-2 preregistration commit:

```text
3d359e3cc8a101c4f8b0c2be5a8f278931645129
```

## Verification history

Attempt 1:

```text
workflow = 36100100251
classification = TECHNICAL_VERIFIER_FALSE_POSITIVE / ZERO-SCIENCE
```

The verifier self-safety detector interpreted its own
`clrm2_predictive_discovery.py` string literal as a scientific-runner launch.

No Training Lock, protocol, feature, target, candidate, baseline, CV, manifest,
Gate-2, runtime or downstream contract changed.

Recovery commit:

```text
e99f7d40cd42c1bb6d8ccb159f14c0d270c5965c
```

Recovery restricted launch detection to actual subprocess call sites only.

## Canonical independent verification

Workflow:

```text
36100335778
```

Tests:

```text
6/6 PASS
```

Verdict:

```text
CLRM2_TRAINING_LOCK_VERIFICATION_PASS
```

Verification JSON SHA-256:

```text
5a4646b04ac24a6d1377d5ddb86c6b927df137b3060076b5a04158b448ef0f71
```

Artifact:

```text
ID = 10849321095
name = clrm2-training-lock-verification
ZIP SHA-256 = f73ee175e00a29e39e02ceab7609ed3dd0fa0b9cb00034c31f1a4c2d0950b4d2
```

## Independently verified contracts

PASS:

- exact Training Lock SHA-256;
- exact protocol / manifest / runner / test / preflight-workflow blobs;
- exact OBS11-v1 historical tuple;
- OBS11 extractor is pre-boundary and has no `next_task` argument;
- exact six CLRM direct response targets;
- exact eight substrate blobs;
- deterministic 240-seed regeneration;
- D-train = 160 seeds / 480 boundaries;
- sealed D-val = 80 seeds / 240 boundaries;
- D-train and D-val are disjoint;
- actual collisions with historical KCL = zero;
- actual collisions with protected KCL = zero;
- actual collisions with ACO-1 = zero;
- actual collisions with CPRM-1 = zero;
- actual collisions with MSA-1 = zero;
- actual collisions with MSA-3 = zero;
- actual collisions with CLRM-1 Role-S = zero;
- exact RBF-KRR-v1 candidate grids;
- exact B2 ridge grid;
- exact five-fold seed-grouped CV rule;
- exact bootstrap count/seed;
- exact Phase-A-only authorization;
- exact separate CLRM2-B Validation Lock requirement;
- exact runtime;
- zero-science preflight closure exact;
- D-train absent;
- candidate package absent;
- D-val absent;
- formal result absent;
- fresh execution workflows absent.

## Zero-science assertions

```text
fresh_seed_execution_attempted      = false
fresh_predictor_fitting_performed   = false
dval_outcomes_generated             = false
scientific_outcome_generated        = false
```

## Governance decision

```text
CLRM-2 protocol                    FROZEN
CLRM2-A Training Lock              VERIFIED PASS

PHASE A:
  D-train collection               ELIGIBLE TO OPEN
  D-train-only fitting/tuning      ELIGIBLE TO OPEN
  strongest baseline selection     ELIGIBLE TO OPEN
  candidate package freeze         ELIGIBLE TO OPEN

PHASE B:
  D-val collection                 PROHIBITED
  D-val inspection                 PROHIBITED
  Gate-2 adjudication              PROHIBITED

CLRM2-B Validation Lock            NOT YET CREATED
controller                         CLOSED
KCL-7                              CLOSED
```

This closure authorizes only Phase A under the exact verified Training Lock.

It does not authorize sealed validation.
