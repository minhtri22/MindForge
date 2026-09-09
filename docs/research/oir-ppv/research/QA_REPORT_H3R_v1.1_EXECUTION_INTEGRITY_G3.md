# QA REPORT — H3R v1.1 G3 EXECUTION INTEGRITY

Date: 2026-09-09
Role: Independent QA execution-integrity reviewer
Experiment: `EXP-H3R-002`

## Verdict

- GATE_VERDICT: `PASS_WITH_LIMITS`
- SCIENTIFIC_VERDICT: `NOT_ASSIGNED_AT_G3`
- P0: none
- P1: none
- P2: one provenance metadata mismatch described in `governance/H3R_v1.1_DECISIVE_EVIDENCE_ERRATUM_001.md`.
- Rerun permitted: `NO`.
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`.

## Integrity checks

- Frozen protocol SHA256: `5cdecfe758b9908f0f2199b6e7cd5632e9636b887e141d265fdb9265c107334d`.
- Frozen test-manifest SHA256: `371799bb474f2f425db7acacf63cba3de7ca4876f61cbfa5a88549363d97255d`.
- Runtime source HEAD: `3d9db9e1528d962a28eb97cd189578956ea0fc55` on `oir-ppv-research`.
- Scientific-scope worktree at runtime: clean.
- Exactly one decisive access event: `H3R_V1_1_DECISIVE_ACCESS_001` at `2026-09-09T13:08:15.633202+00:00`.
- Decisive runner exit code: `0`.
- `EXP-H3R-002`: 20/20 expected cells present and valid.
- Test rows: `6039/6039`.
- Environment/seed key set: exact frozen 4 x 5 matrix.
- Per-cell test-row counts: 20/20 match frozen manifest.
- Realized-shift validator: 20/20 PASS; categorical channels preserved; maximum normalized L_inf remains within `delta=0.10`.
- Pre-execution test identity: 20/20 cells and all index/observation/label hashes match the frozen manifest.
- Runtime source hashes in `runtime_manifest.json`: 4/4 match current source bytes.
- Authorization snapshot is semantically identical to the G1 hash-bound authorization.
- No `failure.json` exists.

## P2 provenance finding

Each decisive cell JSON records `test_identity.observation_sha256` using `_sha256_array(clean_test_obs)`, while the frozen mixed/value-stable observation identity is defined and checked with `_sha256_observation(clean_test_obs)`. Therefore the recorded observation hash in that one post-check cell metadata field differs from the frozen manifest in 20/20 cells.

This does not invalidate scientific execution because `execute_decisive()` checks `_sha256_observation(clean_test_obs)` against the frozen manifest before any candidate metric is calculated, and `pre_execution_identity.json` independently preserves the correct 20/20 frozen identities. The finding is retained as P2 metadata debt; decisive artifacts are immutable and are not rewritten.

## Gate decision

Execution integrity is sufficient for statistical QA. G4 is open. The one-shot test access is consumed permanently; no rerun, seed replacement, tuning, threshold change, evidence overwrite, or post-access repair is permitted.
