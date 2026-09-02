# MindForge Research Index

MindForge separates the active compact-kernel roadmap from optional research tracks. Research does not become kernel architecture merely because it may be interesting later.

## Strategic research directions

- **Personal Intelligence — Two-Track Direction — FOUNDATION RESEARCH ONLY** — Track A investigates whether a <=20M-class MindForge-Mobile model can focus on personal understanding/routing rather than world knowledge. Track B is now **Personal Pattern Foundation (PPF)**, a greenfield research track asking how little machinery is required to reliably recognize one person over time. PPF must progress through five proof layers: define "Recognize Me"; define the personal event foundation; freeze a ground-truth benchmark; test minimal baselines; add only the minimum mechanism justified by measured failure. Legacy PIS is outside the PPF execution path and is historical only. Track A/PPF integration is not authorized. See [personal-intelligence-two-track.md](personal-intelligence-two-track.md).

## PPF foundation research

- **Device/platform research — COMPLETE / INPUT TO L1-L2** — surveys Android, iOS, Wear OS, Apple Watch/watchOS, connected accessories, Health Connect/HealthKit and the medical-software boundary. Main conclusion: personal-device evidence is feasible but inherently partial, delayed, permission-dependent and multi-device; `unknown/not observable`, source provenance and opportunity semantics must therefore be first-class. See [ppf-device-platform-research.md](ppf-device-platform-research.md).
- **L1/L2 related-work research — COMPLETE / PRE-EXECUTION INPUT** — surveys Reality Mining, Eigenbehaviors, StudentLife, ExtraSensory, personal sensing/informatics, context-aware computing, missingness/data-quality research, SOSA/SSN, SensorThings, OpenTelemetry, CloudEvents, W3C PROV, and OSS systems including AWARE, Beiwe, mindLAMP, RAPIDS, ActivityWatch, and Open mHealth. Main conclusion: PPF should reuse minimal event/provenance semantics instead of inventing them, while directly proving its unique `opportunity + observability + correction/deletion + abstention` contract. See [ppf-l1-l2-related-work-research.md](ppf-l1-l2-related-work-research.md).
- **PPF-L1/L2 Foundation Protocol — DEFINED / EXECUTION NOT YET RUN** — freezes the proof requirements for defining "Recognize Me" and a platform-neutral personal-event foundation before any pattern algorithm may be implemented. The related-work pass recommends a small pre-execution revision covering observation quality/coverage, three conceptual times (phenomenon/result/ingest), capture-policy provenance, multi-label context, and provenance-bearing user correction. L3/L4/L5 and PPF implementation remain blocked until L1 and L2 pass. See [ppf-l1-l2-foundation-protocol.md](ppf-l1-l2-foundation-protocol.md).

## Completed research

- **R1 — Open-Source Learning/Memory Architecture Survey — PASS / CLOSED** — source-level survey of ten projects and six shortlisted candidates. It recommends minimal reservoir replay only for a future independently authorized prototype, keeps application memory outside the kernel, and concludes that Phase 1 needs no architectural change or preserved extension point. See the [survey](r1-open-source-learning-memory.md), [matrices](r1-candidate-matrix.md), and [machine-readable inventory](data/r1-candidates.json). R1 did not implement a candidate and is not a P0.9 retry.

## Deferred research

- Custom continual-learning research — STOP/FROZEN after P0.9 bounded falsification.
- Explicit custom memory research — STOP/FROZEN because no controlled memory-value substrate was established.
- Legacy PIS / adaptive-pattern research — historical only under the old framing. It is not a prerequisite, baseline requirement, compatibility target or salvage source for PPF.

See [deferred/continual-learning-memory.md](deferred/continual-learning-memory.md) for reopen conditions and adoption policy.

## Historical evidence

- [P0.9 frozen protocol](../phases/phase-0-continual-protocol.md)
- [P0.9 validation/STOP evidence](../phases/phase-0-continual-validation.md)
- [Phase-0 QA](../phases/phase-0-qa.md)
- [P0.9 qualification JSON](../../experiments/results/phase0_continual_qualification.json)
- [P0.9 final STOP record](../../experiments/results/phase0_continual_real.json)

Historical artifacts remain in their original locations; they are not renamed or moved as part of research archival.
