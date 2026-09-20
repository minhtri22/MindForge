# ACO-1 Fresh Execution Attempt 1 — Technical Failure

Status: **TECHNICAL FAILURE / NO SCIENTIFIC EXECUTION**

Workflow run: `35511036353`

Failed step: `Collect frozen 40-seed cohort`

## Failure point

The process terminated inside `_validate_execution_lock()` before the first fresh seed entered `build_boundary_records()`.

Observed exception:

```text
RuntimeError: ACO-1 execution lock invalid:
seed_manifest_sha256 expected frozen hash, observed None
protocol_sha256 expected frozen hash, observed None
```

## Root cause

The scientific runner's lock guard expected `seed_manifest_sha256` and `protocol_sha256` as top-level JSON keys.

The independently verified canonical lock stores them as:

```text
seed_manifest.sha256
protocol.sha256
```

The lock itself was valid; the runner/lock schema adapter was inconsistent.

## Scientific contamination assessment

- fresh seed entered counterfactual harness: **NO**
- collection output created: **NO**
- integrity validation reached: **NO**
- scientific metric inspected: **NO**
- adjudicator called: **NO**
- `FORMAL_RESULT.json` created: **NO**
- protected cohort touched: **NO**

Therefore this is a pure implementation/interface defect before scientific execution.

## Governance consequence

Changing the scientific runner invalidates the previously verified execution lock.

Required recovery:

```text
archive/supersede lock v1
→ remove active execution workflow
→ minimally fix canonical nested-lock validation
→ zero-science preflight
→ new execution lock
→ independent lock verification
→ only then retry fresh collection
```

Protocol, thresholds, materiality gates, seed manifest, and protected cohort remain unchanged.
