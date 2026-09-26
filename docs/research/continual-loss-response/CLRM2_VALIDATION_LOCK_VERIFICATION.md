# CLRM2-B Independent Validation Lock Verification

Status: **PASS / CLOSED**

Date: 2026-09-26

## Exact verified Validation Lock

```text
bd5845eb350bc5bbe889d0d1e2570d9a97b51c8bc683585c6d344f53ee15abde
```

Validation Lock commit:

```text
7175664c7c4648361aabba5c62e082d5fd5eb9fe
```

Frozen candidate package SHA-256:

```text
310bd9805cb028691826722c8cf5ee365e85d549872f2f3e898d8e348cef2a83
```

Frozen D-train SHA-256:

```text
8e7e38357f2117e76337b454f40debeb7741f1a8f3993a61add9f50c490d1b28
```

## Canonical independent verification

Workflow:

```text
36256072896
```

Workflow head:

```text
3c7aa2132af06a9010d98f5c87eab98bc3809604
```

Tests:

```text
5/5 PASS
```

Verdict:

```text
CLRM2_VALIDATION_LOCK_VERIFICATION_PASS
```

Verification JSON SHA-256:

```text
389e3c9b031659da51dc42a6eefc440741b347a0b351ed72b759c93c5bebb7f6
```

Artifact:

```text
ID = 10910592362
name = clrm2-validation-lock-verification
ZIP SHA-256 =
f679e7ec7fbc155c240eb50cb4754d7cac6157c49758639817406e5259f2f461
```

## Independently verified contracts

PASS:

- exact Validation Lock bytes/hash;
- exact parent Training Lock bytes/hash;
- exact protocol and scientific-runner blobs;
- exact frozen D-train bytes/blob and spent state;
- exact frozen candidate bytes/blob;
- exact RBF-KRR-v1 candidate selection;
- exact frozen strongest baseline B2;
- exact B2 per-channel lambdas;
- exact 80-seed / 240-boundary D-val manifest;
- exact OBS11-v1 representation and six response targets;
- exact bootstrap count/seed;
- exact Gate-2 thresholds and no-recalibration rule;
- Phase-A workflow retired/hard-disabled;
- exact runtime;
- D-val absent;
- formal Gate-2 result absent;
- verifier independence / zero validation science.

Zero-science assertions:

```text
dval_outcomes_generated      = false
gate2_called                 = false
scientific_outcome_generated = false
```

## Governance decision

```text
CLRM2-A Phase A                 CLOSED
D-train                         SPENT
candidate package               FROZEN
strongest baseline              FROZEN = B2

CLRM2-B Validation Lock         VERIFIED PASS

sealed D-val collection         ELIGIBLE TO OPEN ONCE
D-val refit/tuning              PROHIBITED
Gate-2                          one-shot only after valid D-val preservation
controller                      CLOSED
KCL-7                           CLOSED
```

This closure authorizes exactly one sealed D-val execution under the verified
Validation Lock. It does not authorize any model, feature, threshold, baseline,
seed or calibration change.
