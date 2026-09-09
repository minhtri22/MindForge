# QA REPORT — H3R v1.1 G7 FINAL CLOSURE

Date: 2026-09-09
Role: Final independent QA closure reviewer

## Final reconciliation

- G1 pre-execution readiness: `PASS`.
- G2 one-shot decisive execution: `COMPLETE`, exit code `0`, exactly one scientific access event.
- G3 execution integrity: `PASS_WITH_LIMITS`.
- G4 statistical QA: `PASS`.
- G5 researcher classification: `FALSIFIED_UNDER_TESTED_CONDITIONS`.
- G6 adversarial review: `PASS_WITH_LIMITS`.
- P0: `0`.
- P1: `0`.
- P2: decisive-cell observation-hash metadata erratum; synthetic/external-validity boundary retained.

## Final gate verdict

`GATE_VERDICT = PASS_WITH_LIMITS`

`SCIENTIFIC_VERDICT = FALSIFIED_UNDER_TESTED_CONDITIONS`

`CLOSURE_STATUS = CLOSED_WITH_LIMITS / NO_RERUN`

The process/integrity verdict and scientific verdict are intentionally separate. `PASS_WITH_LIMITS` means the one-shot execution is scientifically usable under the frozen protocol despite a documented provenance-only metadata defect. It does not convert the negative scientific result into a positive one.

## Immutable boundary

H3R v1.1 has consumed its only authorized decisive scientific access. The experiment, access log, negative result, and P2 erratum are now closure evidence. No rerun, result-dependent repair, seed replacement, baseline/candidate change, threshold adjustment, noise retuning, or evidence overwrite is permitted under v1.1.

H4 remains `NOT_OPENED / DEFERRED_BY_OWNER` and is not activated by this closure.
