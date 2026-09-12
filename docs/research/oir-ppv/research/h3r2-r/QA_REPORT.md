# H3R2-R QA Report

Final QA classification: **PROTOCOL_DEVIATION**

Confirmatory scientific acceptance blocker: **P0**.

## Gates that passed

The implementation and evidence-preservation path is internally valid:

- exact historical reconstruction: 100/100 representation hashes match;
- historical replay smoke: 20/20 exact comparisons;
- frozen prospective runner and runner contract present;
- pretest QA and identity lock present;
- 20 fresh prospective seeds are unique and disjoint from historical seeds;
- 20/20 prospective cells completed;
- source/protocol identity remained fixed through the one-shot execution;
- evidence access advanced exactly `0 -> 1`;
- `rerun=0`;
- raw prospective evidence remains preserved unchanged.

These checks support execution integrity and provenance. They do not supply a missing confirmatory decision rule.

## P0 finding: missing pre-test confirmatory criteria

The frozen protocol omitted quantitative acceptance/statistical criteria required to adjudicate the prospective hypothesis. In particular, it did not freeze:

- clean-recovery margin;
- reproducibility fraction;
- noise non-inferiority margin;
- validation-to-test tolerance;
- baseline-control acceptance rule;
- CI/statistical decision plan.

The protocol's decision section only constrains how linear and degree-2 readouts are reported and interpreted. That is insufficient to map observed values to a confirmatory pass/fail hypothesis decision.

Severity is P0 for **confirmatory scientific acceptance** because prospective labels/metrics have already been opened. A threshold or statistical plan written now would be informed by the observed data and cannot retroactively restore preregistration. This does not invalidate the preserved observations themselves; it invalidates a confirmatory verdict from this run.

## QA disposition

- Execution integrity: `PASS`.
- Evidence preservation: `PASS`.
- Reconstruction fidelity: `PASS`.
- Prospective seed separation: `PASS`.
- Confirmatory decision-rule completeness: `FAIL_P0`.
- Prospective hypothesis verdict: `PROTOCOL_DEVIATION`.
- Retroactive threshold repair: `PROHIBITED_FOR_THIS_RUN`.
- Rerun of consumed decisive evidence: `PROHIBITED`.
- H4 opening: `NO`.

Any future confirmatory retry must be a new preregistered protocol with the full decision rule frozen before access and must use new prospective evidence. That future work is not opened by this closure.
