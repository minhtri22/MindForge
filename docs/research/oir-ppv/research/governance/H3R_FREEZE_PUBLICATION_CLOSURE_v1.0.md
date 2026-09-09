# H3R Freeze Publication Closure v1.0

Date: 2026-09-09
Branch: `oir-ppv-research`
Published freeze package commit: `7e90366fc062b425d0e5c529c4be81ad2bd54ac2`
Remote verification: `origin/oir-ppv-research` contained the exact published freeze commit before this governance closure update.

## Scope

This record closes publication/provenance debt only. It does not change H3R scientific semantics, protocol values, candidate identities, thresholds, test identity, test data access state, or prior H1/H2/H3 evidence.

The following frozen H3R artifacts remain byte-identical to the independently reviewed freeze package:

- `protocols/h3r/H3R_PROTOCOL_v1.0.md`
- `protocols/h3r/h3r_protocol_v1.0.json`
- `protocols/h3r/h3r_test_manifest_v1.0.json`
- `protocols/h3r/h3r_test_access_log.md`

The historical source anchor `0521c5754a32e2625930de75fe2635c6ce5ec9a0` remains intentionally preserved inside frozen artifacts; it identifies the pre-publication integration source and is not the publication commit SHA.

## Publication exclusions

Four historical M4 raw JSON artifacts exceeded GitHub's 100 MB blob limit and were omitted from Git publication. Their exact paths, byte sizes, SHA256 hashes, classification, and `h3r_freeze_semantic_impact = NONE` are recorded in `governance/publication_exclusions_v1.0.json`.

This omission does not alter the frozen H3R protocol or test identity.

## Debt closure

`P2 / PROVENANCE_PUBLICATION_DEBT` is `CLOSED` because the freeze package is committed, published, remotely verified, and its publication SHA is recorded in the source-of-truth manifest.

Publication closure does **not** authorize decisive H3R execution. H3R remains `NOT_EXECUTED / TEST_LOCKED` pending a separate explicit execution task. H4 remains `NOT_OPENED`.
