# QA Findings

## P0

### P0-01 — H3R2-R lacks a complete pre-test confirmatory decision rule

The frozen prospective protocol does not specify all criteria needed to convert observed metrics into a confirmatory decision: clean-recovery threshold/margin, reproducibility threshold, noise non-inferiority margin, validation-to-test tolerance, baseline/control decision rule, CI/statistical procedure, and a defined RelativeRecovery decision metric.

Evidence was subsequently accessed. These criteria cannot be added retroactively. Consequence: `CONFIRMATORY_ADJUDICATION = NOT_AVAILABLE`; historical H3R2-R status remains `PROTOCOL_DEVIATION`.

Severity: **P0**. This blocks a valid confirmatory scientific conclusion. Later documentation of the gap does not fix it.

## P1

### P1-01 — RESULTS.md disagrees with canonical execution evidence

`RESULTS.md` describes aggregation as 20 fresh seeds x 4 environments = 80 values per row. The run manifest and canonical prospective summary define 20 total cells, five seeds per L1-L4 environment, with 800 raw rows. The per-environment L0 linear values in `RESULTS.md` also disagree with the canonical summary.

This is a major reporting/provenance inconsistency. Raw evidence, manifests, and hashes remain preserved, so the defect is recoverable without rewriting consumed evidence. This review records the discrepancy and does not modify historical H3R2-R results.

Severity: **P1**.

### P1-02 — Closure provenance runner/protocol hashes disagree with the sealed evidence-access identity

`prospective_execution_v1/access.json` records evidence access at Git head `82861e2d406dc48b9dad4501e7d3b5935428d241` with runner SHA-256 `fb70812c9d7d9e0165c4a81ad106a9b13965817c3ef7592dbcf11ab989228d95` and protocol SHA-256 `a40a6737a29f3f1476cec810667074985cdc4e65c103c819c70a9ecb9ce67b26`. Direct hashing of those files from that Git head reproduces the access-event values.

`CLOSURE_PROVENANCE_v1.json` records different runner/protocol SHA-256 values. The closure commit does not modify the runner or protocol, so the closure-manifest identities cannot both describe the sealed evidence-access boundary.

This is a major provenance-record inconsistency, but the actual one-shot boundary remains recoverable from `access.json`, its Git head, the identity lock, raw artifacts, and the run manifest. Historical evidence must remain unchanged; the closure provenance file must not be treated as the sole canonical source for runner/protocol identity.

Severity: **P1**.

## P2

No independent P2 finding was established in this review.

## Provenance Governance

The current hardened H3R2-R provenance identifies the PLAN-required tuple:

- source
- config
- seed
- model_state
- dataset_identity
- artifact
- hash

It also identifies environment, preprocessing, runner, protocol, split identity, and artifact manifest. Runner/protocol content identity is recoverable from the sealed access event and its Git head, but `CLOSURE_PROVENANCE_v1.json` disagrees with that identity as recorded in P1-02. This traceability does not repair P0-01 or convert H3R2-R into confirmatory evidence.

## Scientific Distinction Check

No current closure claim reviewed here validly collapses the following distinctions:

- representation != mechanism
- causal sufficiency != transfer
- transfer != generation
- generation != counterfactual validity
- diagnostic evidence != confirmatory evidence
- execution integrity != scientific validity
- historical reconstruction != historical proof

The P1 reporting inconsistency is a reliability defect, not permission to reinterpret the raw evidence.

## Counts

`P0=1 / P1=2 / P2=0`
