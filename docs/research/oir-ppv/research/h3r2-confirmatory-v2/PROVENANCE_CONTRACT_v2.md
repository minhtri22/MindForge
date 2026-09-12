# H3R2-CONFIRMATORY-v2 Provenance Contract

Status: `REVIEWED / NOT_FROZEN`

## Representation provenance

Every L0-L4 / ENV / historical-state-seed record must bind:

- source commit;
- learner config + config hash;
- historical state seed;
- model-state artifact + SHA-256;
- preprocessing artifact/version + SHA-256;
- dataset identity + hash;
- historical train-representation artifact + SHA-256;
- reconstructed representation artifact + SHA-256;
- split identity;
- environment identity;
- reconstruction manifest identity/hash.

Required historical source snapshot: `e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51`.

Known reconstruction result: 100/100 exact representation SHA-256 matches, mismatch count 0. Future freeze must bind the canonical reconstruction manifest; reconstruction fidelity is provenance evidence, not M6 evidence.

## Fresh test identity policy

This review creates no fresh seed or dataset identity.

At the future authorization stage, after the protocol freeze commit exists, generate exactly one prospective test seed for each of the 20 predeclared ENV×historical-state-seed cells using a deterministic SHA-256 derivation from the frozen bundle hash, cell ID and an authorization nonce. Reject collisions with every historical, Q-H3R.1 and H3R2-R seed by deterministic counter increment before any dataset is generated.

The locked test manifest must include seeds, environment IDs, generator/config version, row IDs/counts, dataset hash, split hash, clean/noisy artifact hashes, representation hashes and zero-overlap proof.

## Required freeze/execution hashes

- `protocol_hash`
- `decision_rule_hash`
- `metric_registry_hash`
- `threshold_justification_hash`
- `statistical_plan_hash`
- `representation_manifest_hash`
- `readout_config_hash`
- `test_manifest_hash`
- `runner_hash`
- `adjudicator_hash`

## Access governance

Before decisive access: `scientific_test_access_count=0`.

First label/metric consumption must atomically record one event and transition to `1`. Maximum authorized decisive access is one. `rerun_count=0` after evidence consumption.

A crash before labels/metrics are consumed may restart only if access remains 0 and all frozen identities are byte-identical. Any retry after access 1 requires a new protocol version and a completely fresh evidence identity.

## Execution output provenance

Every emitted metric/artifact must include source/config/seed/model_state/dataset_identity/artifact/hash plus the freeze hashes above and software/environment versions sufficient to reproduce preprocessing, readout fitting, noise generation and adjudication.