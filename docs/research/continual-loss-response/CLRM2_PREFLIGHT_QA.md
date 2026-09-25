# CLRM-2 Zero-Science Training Preflight

Status: **PASS / CLOSED**

Date: 2026-09-25

## Frozen identity

CLRM-2 preregistration commit:

```text
3d359e3cc8a101c4f8b0c2be5a8f278931645129
```

CLRM2-A Training Lock commit:

```text
fde86df15e3d78b5c20b550875af21af47ee5098
```

Training Lock SHA-256:

```text
e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5
```

Protocol SHA-256:

```text
7d97a956fb4d5df8d4ed1ba452fe0a4f81009dd103fa361d127ad8a786b01611
```

## Canonical preflight

Workflow:

```text
36099718392
```

Frozen tests:

```text
5/5 PASS
```

Verdict:

```text
CLRM2_ZERO_SCIENCE_PREFLIGHT_PASS
```

Preflight JSON SHA-256:

```text
d790f55f0e599bcdb4f774d154dff2cf05ee7a045320b331e4dcf0ddf73c7140
```

Artifact:

```text
ID = 10849305182
name = clrm2-zero-science-preflight
ZIP SHA-256 = 3ae6000cdadaeadafc8660920a54744971f1f24c5d1caa188b4994fc10f01dcd
```

## Qualified zero-science state

PASS:

- OBS11-v1 historical feature order exact;
- frozen feature extractor blob exact;
- frozen historical KCL-6.5.9.2 source blob exact;
- CLRM-1 response extractor blob exact;
- 240-seed discovery manifest deterministic;
- D-train = 160 seeds / 480 boundaries;
- sealed D-val = 80 seeds / 240 boundaries;
- D-train/D-val disjoint;
- historical KCL/protected/CLRM-1 collision checks clean;
- historical seed 9595 OBS11 extraction integrity PASS;
- candidate family/baseline procedures covered by frozen source/tests;
- D-train absent;
- candidate package absent;
- D-val absent;
- formal result absent;
- Training Lock execution blocked;
- Validation Lock execution blocked.

The complete ACO/CPRM/MSA/CLRM-1 spent-cohort collision audit is reserved for
the independent Training Lock verifier, which reads the frozen source
manifests without importing or executing the CLRM-2 scientific runner.

## Zero-science assertions

```text
fresh_seed_execution_attempted      = false
fresh_predictor_fitting_performed   = false
dval_outcomes_generated             = false
scientific_outcome_generated        = false
```

## Governance state

```text
CLRM-2 protocol                     FROZEN
OBS11-v1                            FROZEN
RBF-KRR-v1                          FROZEN
B0/B1/B2                            FROZEN
D-train manifest                    FROZEN
D-val manifest                      FROZEN / SEALED
Gate-2                              FROZEN
CLRM2-A Training Lock               FROZEN
zero-science preflight              PASS

independent Training Lock verify    PENDING
D-train collection                  NOT AUTHORIZED
predictor fitting                   NOT AUTHORIZED
D-val collection                    PROHIBITED
controller                          CLOSED
```

The next admissible step is independent static verification of the exact
Training Lock SHA-256 above.
