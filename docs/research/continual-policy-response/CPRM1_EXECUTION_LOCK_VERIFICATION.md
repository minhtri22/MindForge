# CPRM-1 Independent Execution-Lock Verification

Status: **PASS / CLOSED**

Date: 2026-09-20

## Canonical lock

Execution-lock SHA-256:

```text
26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274
```

Lock commit:

```text
00d3002c847fb4182821200cf7e6a47495a82c5e
```

Scientific implementation commit:

```text
e955c4962846cda8cac633c4c9fd49b40a901750
```

Protocol Git blob:

```text
f61aabc5605400faea30e5d2af4349a2b32c792f
```

Runner Git blob:

```text
18774a9349adeb4a0e5d66ce46416564640f41aa
```

## Verification method

The verifier was intentionally independent from the CPRM-1 scientific runner.

It did not import or call:

```text
preflight
collect_fresh
adjudicate_records
build_response_records
```

It performed static Git/source/lock/runtime/workflow checks only.

## Technical verifier attempt 1

Initial verification workflow:

```text
35517792454
```

Result:

```text
TECHNICAL VERIFIER FAILURE / NON-CANONICAL
```

Cause:

The verifier's raw-source self-audit searched for a forbidden literal such as
`--phase collect`; the same literal existed inside the verifier's own deny-list,
causing a self-referential false failure.

The defect was corrected only in verifier self-audit logic by commit:

```text
825ddb27c41246a72920dec0f5bff8936767cac3
```

No scientific lock, protocol, runner, seed, support gate, geometry gate,
dependency or retry policy changed.

No fresh scientific seed was executed.

## Canonical independent verification

Workflow run:

```text
35517842681
```

Independent verifier tests:

```text
4 passed
```

Canonical verdict:

```text
CPRM1_EXECUTION_LOCK_VERIFICATION_PASS
```

Verification JSON SHA-256:

```text
fa88ea8e1a6fc37f18be445c7b84a1ce755b1aa2c8ea38a92c8bcd9b64f4c3c1
```

Artifact:

```text
ID = 10607531332
name = cprm1-execution-lock-verification
ZIP SHA-256 = 47dbf246f25a0406cb0f418bf7e56e60b493e32d088d6f8989213136746e8c9c
```

## Verified invariants

The independent verifier closed PASS on:

- exact execution-lock SHA-256;
- exact protocol Git blob;
- exact scientific runner Git blob;
- exact synthetic-test Git blob;
- exact preflight-workflow Git blob;
- exact 60-seed manifest and manifest SHA-256;
- source seed tuple consistency;
- runtime/dependency identity;
- historical KCL seed disjointness;
- protected KCL cohort disjointness;
- spent ACO-1 cohort disjointness;
- exact 60×3 support contract;
- exact response geometry gates;
- exact B-A/C-A contrast geometry gates;
- exact one-shot adjudication contract;
- exact technical retry policy;
- CPRM-2 transition gated only by `PASS_RESPONSE_SUPPORT`;
- controller remains closed;
- KCL-7 remains closed;
- fresh collection absent;
- `FORMAL_RESULT.json` absent;
- fresh execution workflow absent.

Collision result:

```text
historical_kcl = []
protected_kcl  = []
spent_aco      = []
```

## Zero-science verification assertions

```text
fresh_seed_execution_attempted = false
scientific_outcome_generated   = false
model_fitting_performed        = false
fresh_execution_workflow       = absent
fresh collection               = absent
FORMAL_RESULT.json              = absent
```

## Governance decision

```text
CPRM-1 PROTOCOL                  FROZEN
CPRM-1 IMPLEMENTATION            FROZEN
CPRM-1 EXECUTION LOCK            VERIFIED PASS
CPRM-1 ZERO-SCIENCE PREFLIGHT    PASS
INDEPENDENT LOCK VERIFICATION    PASS

FRESH CPRM-1 COLLECTION          ELIGIBLE TO OPEN
FRESH COLLECTION STARTED         NO

CPRM-2                           CLOSED
CONTROLLER                       CLOSED
KCL-7                            CLOSED
```

This document authorizes only the next frozen CPRM-1 execution step under the
verified lock. It does not authorize CPRM-2 or predictor training.

The execution lock itself is not edited after verification; its immutable hash
plus this verification closure defines the verified state.
