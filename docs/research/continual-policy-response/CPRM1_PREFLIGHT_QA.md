# CPRM-1 Zero-Science Preflight QA

Status: **PASS / CLOSED**

Date: 2026-09-20

## Scope

This closure covers CPRM-1 protocol/implementation/execution-lock qualification
only.

No CPRM-1 fresh scientific seed was executed.
No CPRM-1 scientific collection was created.
No predictor was fitted.
No scientific geometry was observed.
No controller was implemented.

## Frozen scientific identity

Preregistered implementation commit:

```text
e955c4962846cda8cac633c4c9fd49b40a901750
```

Execution-lock commit:

```text
00d3002c847fb4182821200cf7e6a47495a82c5e
```

Protocol Git blob:

```text
f61aabc5605400faea30e5d2af4349a2b32c792f
```

Runner Git blob:

```text
18774a9349adeb4a0e5d66ce46416564640f41aa
```

Seed manifest SHA-256:

```text
d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3
```

## Pre-lock workflow note

Workflow run `35517287667` was auto-triggered when the preregistration commit
introduced the preflight workflow but before `CPRM1_EXECUTION_LOCK.json`
existed.

It failed at the preflight phase as expected.

Classification:

```text
EXPECTED_PRELOCK_ZERO_SCIENCE_FAILURE
```

Synthetic/contract tests had already passed. No fresh science was attempted.

This run is non-canonical and does not alter CPRM-1.

## Canonical zero-science preflight

Workflow run:

```text
35517327267
```

Focused tests:

```text
5 passed
```

Verdict:

```text
CPRM1_ZERO_SCIENCE_PREFLIGHT_PASS
```

Preflight JSON SHA-256:

```text
0ef730573e70397bd45edc2b99ccc5b35d6f723e3e0156342189c40875a24f8f
```

Execution-lock SHA-256:

```text
26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274
```

Protocol SHA-256:

```text
2663cb2b28f73e02bbac19c537e16632f978d2d754488932924bf37e7c8ea084
```

Artifact:

```text
ID = 10606759798
name = cprm1-zero-science-preflight
ZIP SHA-256 = 7fceeb3b178ab6feddbf49b18c9f374998f9b4eff38c9cfa57662559bc194fd2
```

## Qualified contracts

The canonical preflight closes PASS on:

- exact A/B/C policy identity;
- exact checkpoint identity;
- exact 60-seed manifest/hash;
- historical KCL collision audit;
- protected KCL disjointness;
- spent ACO-1 disjointness;
- exact CPRM-1 lock binding to protocol/runner;
- historical seed `9595` response extraction integrity;
- exact deterministic repeat on the historical probe;
- absence of fresh CPRM-1 collection;
- absence of `FORMAL_RESULT.json`;
- absence of independent lock-verification closure;
- fresh execution still blocked;
- no predictor/model-fitting API in the CPRM-1 runner.

## Zero-science assertions

```text
fresh_seed_execution_attempted = false
scientific_outcome_generated   = false
model_fitting_performed        = false

fresh collection               = absent
FORMAL_RESULT.json              = absent
independent lock verification  = absent
fresh execution authorized     = false
```

## Decision

```text
CPRM-1 PROTOCOL              = FROZEN
CPRM-1 IMPLEMENTATION        = FROZEN
CPRM-1 EXECUTION LOCK        = FROZEN
CPRM-1 ZERO-SCIENCE PREFLIGHT= PASS

CPRM-1 FRESH SCIENCE         = NOT YET AUTHORIZED
CPRM-2                       = CLOSED
CONTROLLER                   = CLOSED
KCL-7                        = CLOSED
```

The next admissible action is independent verification of the exact CPRM-1
execution lock.

Only after independent lock verification PASS may the frozen 60-seed CPRM-1
collection be opened.
