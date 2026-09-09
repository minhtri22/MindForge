# H3R v1.1 DECISIVE EVIDENCE ERRATUM 001

Date: 2026-09-09
Scope: provenance metadata only; no scientific-byte repair and no rerun.

## Finding

In `EXP-H3R-002/cells/*.json`, `test_identity.observation_sha256` was serialized with `_sha256_array(clean_test_obs)`. The frozen test manifest and decisive identity gate use the value-stable `_sha256_observation(clean_test_obs)` encoding.

Result: the post-check observation-hash metadata field differs from the frozen manifest in 20/20 cell files.

## Why scientific validity is unchanged

Before any scientific metric access for a cell, the decisive runner recomputes `_sha256_observation(clean_test_obs)` and requires exact equality with the frozen manifest. `pre_execution_identity.json` records 20/20 matching frozen identities. All 20 cells completed with valid realized-shift validators.

The mismatch therefore occurs only in a redundant post-check metadata field. It does not change observations, labels, predictions, risks, paired effects, bootstrap inputs, thresholds, or verdict logic.

## Governance treatment

- Classification: `P2 / PROVENANCE_METADATA_ONLY`.
- Frozen/decisive evidence is preserved byte-for-byte after execution.
- No correction of the cell JSON files is authorized.
- No rerun is authorized.
- QA and closure reports must cite this erratum when asserting execution integrity.
