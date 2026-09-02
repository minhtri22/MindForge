# MindForge Research Index

MindForge separates the active compact-kernel roadmap from optional research tracks. Research does not become kernel architecture merely because it may be interesting later.

## Completed research

- **R1 — Open-Source Learning/Memory Architecture Survey — PASS / CLOSED** — source-level survey of ten projects and six shortlisted candidates. It recommends minimal reservoir replay only for a future independently authorized prototype, keeps application memory outside the kernel, and concludes that Phase 1 needs no architectural change or preserved extension point. See the [survey](r1-open-source-learning-memory.md), [matrices](r1-candidate-matrix.md), and [machine-readable inventory](data/r1-candidates.json). R1 did not implement a candidate and is not a P0.9 retry.

## Deferred research

- Custom continual-learning research — STOP/FROZEN after P0.9 bounded falsification.
- Explicit custom memory research — STOP/FROZEN because no controlled memory-value substrate was established.
- Adaptive/PIS-like pattern research — inactive; prerequisite learning/memory evidence is absent.

See [deferred/continual-learning-memory.md](deferred/continual-learning-memory.md) for reopen conditions and adoption policy.

## Historical evidence

- [P0.9 frozen protocol](../phases/phase-0-continual-protocol.md)
- [P0.9 validation/STOP evidence](../phases/phase-0-continual-validation.md)
- [Phase-0 QA](../phases/phase-0-qa.md)
- [P0.9 qualification JSON](../../experiments/results/phase0_continual_qualification.json)
- [P0.9 final STOP record](../../experiments/results/phase0_continual_real.json)

Historical artifacts remain in their original locations; they are not renamed or moved as part of research archival.
