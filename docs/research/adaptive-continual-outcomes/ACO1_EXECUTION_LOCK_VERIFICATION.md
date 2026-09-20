# ACO-1 Execution Lock Verification

Status: **PASS / CLOSED**

Date: 2026-09-20

## Scope

This step verifies the frozen ACO-1 execution package only.

No ACO-1 fresh seed was executed.

No scientific outcome was generated.

## Immutable lock

Lock commit:

```text
8b33b9373b4a45ea5df38f1f9e9f9d1e2f05560c
```

Lock file SHA-256:

```text
3a5e832c59b9099a3772e80c1cf8fd89d39f6dd45cf127a13ced2253ebc46457
```

The JSON field `status = LOCKED_PENDING_INDEPENDENT_VERIFICATION` is intentionally **not edited after verification**. Editing the lock merely to change its status would change its SHA-256 and invalidate the evidence. The effective verified state is therefore the immutable lock hash above plus the independent verification artifact below.

## Independent verification run

Workflow:

```text
ACO — ACO-1 execution-lock verification
```

Run ID:

```text
35510792383
```

Head commit:

```text
8b33b9373b4a45ea5df38f1f9e9f9d1e2f05560c
```

Verifier tests:

```text
5 passed in 0.04s
```

Canonical verdict:

```text
ACO1_EXECUTION_LOCK_VERIFICATION_PASS
```

## Scientific-source identity

Scientific implementation:

```text
e4e8f27b164ca938e6efa910bfb1ec2fc056f1a2
```

Runner Git blob at implementation:

```text
117bd3f16d576bf6f683d83747b6c1723a7ae471
```

Runner Git blob at verification HEAD:

```text
117bd3f16d576bf6f683d83747b6c1723a7ae471
```

Result:

```text
NO_POST_PREFLIGHT_SCIENTIFIC_SOURCE_CHANGE = PASS
```

The diff from implementation to lock commit contains only ACO documentation, lock/verifier tooling, verifier tests and the verification workflow.

## Runtime identity

Observed and matched exactly:

```text
architecture = x86_64
Python       = 3.12.14
pip          = 26.2.1
NumPy        = 2.3.3
pytest       = 8.4.2
PyTorch      = 2.10.0+cpu
system       = Linux
kernel       = 6.17.0-1022-azure
```

Execution platform contract remains GitHub-hosted `ubuntu-24.04`, CPU-only.

## Frozen scientific identities

Verified:

- protocol SHA-256 = `a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb`;
- 40-seed manifest SHA-256 = `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`;
- 40 unique fresh seeds;
- zero overlap with protected KCL confirmatory cohort;
- exact A/B/C runner identity;
- exact collection command;
- exact one-shot adjudication command;
- expected record count = 120;
- collection result absent;
- formal result absent;
- execution workflow absent.

## Retry / rerun contract

Verified as frozen:

- technical collection retry only if a complete valid collection does not exist;
- retry must use the same lock;
- no outcome inspection before technical retry;
- a complete valid collection must not be rerun;
- exactly one valid adjudication;
- technical adjudicator retry only if no valid formal result exists;
- any source/protocol/seed/dependency change invalidates the lock and requires return to zero-science preflight.

## Verification evidence

Verification JSON SHA-256:

```text
7bfda7f789e387d5e19a36e29d67e2558a440b2b91564ad05f5819d65f99010e
```

Artifact:

```text
artifact ID = 10605740452
artifact name = aco1-execution-lock-verification
artifact ZIP SHA-256 = 76c7d8ff21c298b614af4501c16b5a865fbf53a5a7c9930e19e538410773c853
```

## Zero-science assertion

```text
fresh_seed_execution_attempted = false
scientific_outcome_generated   = false
execution_workflow_absent      = true
```

## Decision

The execution package is now independently verified.

The frozen 40-seed ACO-1 scientific collection is **eligible to be opened in the next step**, but it is not executed by this verification milestone.

ACO-2, controller work, KCL-7, and protected KCL confirmatory seeds remain unauthorized.
