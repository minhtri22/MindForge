# H3R E0 Provenance Reconciliation v1.0

Status: **CLOSED / E0 READY**
Scientific semantics changed: **NO**
Scientific H3R test metric access: **NO**
Scientific test access count increment: **0**

## Blocker

The frozen H3R source/test manifests require the historical learner-definition manifest:

`experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json`

with SHA256:

`f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`

The publication worktree initially contained byte hash:

`ddb3d0d4b9871f7ba2f0037d97d6de6d498ee8e3ec848a4dcf36e3e72dcf4b87`

## Root cause

The canonical frozen copy uses CRLF line endings (5517 bytes, 185 CRLF lines). The published copy used LF line endings (5332 bytes, 185 LF lines). After EOL normalization, the two files are text-identical. Parsed scientific content was also identical for learner definitions, environment definitions, seeds, splits, interventions, failed-run policy, frozen timestamp, source commit, source branch, and source-tree SHA256.

The byte drift was caused by repository-level `*.json text eol=lf` normalization during publication/migration. This is publication/provenance drift only, not a scientific-definition change.

## Remediation

1. Restored the canonical CRLF bytes from the preserved migration backup.
2. Added a path-specific nested `.gitattributes` rule:
   `experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json -text`
3. Verified the staged Git blob is exactly 5517 bytes and SHA256 `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`.
4. No protocol, threshold, seed, learner, environment, candidate, metric, acceptance rule, or test identity was changed.

## E0 implementation bindings

The following mechanical bindings are fixed before decisive execution and are independent of H3R test outcomes:

- `std_train(X_j)` = `numpy.std(axis=0, ddof=0)`.
- `uint32(SHA256(...))` = SHA-256 digest interpreted as an integer, reduced modulo `2^32` (low 32 bits).
- Bootstrap percentile CI = `numpy.quantile` default linear method at the frozen 98.75% two-sided confidence level.

These bindings do not change the frozen candidate set, seeds, thresholds, noise amplitude, replicate count, aggregation order, or acceptance rules.
## E0 readiness evidence

- Static frozen-contract checks: **28/28 PASS**.
- H3R E0 unit/readiness tests: **6/6 PASS**.
- Frozen test identity hash-only validation: **20/20 cells PASS**.
- Runtime smoke validation on non-frozen seed `424242`: **20/20 system/environment checks PASS**.
- Preflight artifact SHA256: `8952146262514606506c5da6eccbd8c8f41b1535984a2a1346dcf224ccac021f`.
- Frozen test access-log SHA256 remains `145e154542c85fafb35e5c0fe276de477889c06bb8e06ebc52bfcbc991b37e44`.
- Scientific test access count remains **0**.
- H4 remains **NOT_OPENED**.

## Gate verdict

**H3R-E0: PASS / BLOCKER CLOSED / READY_FOR_SEPARATE_EXPLICIT_DECISIVE_EXECUTION_AUTHORIZATION**

This reconciliation does **not** authorize H3R decisive execution and does **not** alter the frozen H3R v1.0 scientific contract.