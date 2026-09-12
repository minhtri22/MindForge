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

It also sufficiently identifies environment, preprocessing, runner, protocol, split identity, and artifact manifest. This traceability improvement does not repair P0-01 or convert H3R2-R into confirmatory evidence.

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

`P0=1 / P1=1 / P2=0`
