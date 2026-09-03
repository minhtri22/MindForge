# MindForge Research Index

MindForge separates the active compact-kernel roadmap from optional research tracks. Research does not become kernel architecture merely because it may be interesting later.

## Strategic research directions

- **Personal Intelligence — Two-Track Direction — FOUNDATION RESEARCH ONLY** — Track A investigates whether a <=20M-class MindForge-Mobile model can focus on personal understanding/routing rather than world knowledge. Track B is now **Personal Pattern Foundation (PPF)**, a greenfield research track asking how little machinery is required to reliably recognize one person over time. PPF must progress through five proof layers: define "Recognize Me"; define the personal event foundation; freeze a ground-truth benchmark; test minimal baselines; add only the minimum mechanism justified by measured failure. Legacy PIS is outside the PPF execution path and is historical only. Track A/PPF integration is not authorized. See [personal-intelligence-two-track.md](personal-intelligence-two-track.md).

## PPF foundation research

- **Device/platform research — COMPLETE / INPUT TO L1-L2** — surveys Android, iOS, Wear OS, Apple Watch/watchOS, connected accessories, Health Connect/HealthKit and the medical-software boundary. Main conclusion: personal-device evidence is feasible but inherently partial, delayed, permission-dependent and multi-device; `unknown/not observable`, source provenance and opportunity semantics must therefore be first-class. See [ppf-device-platform-research.md](ppf-device-platform-research.md).
- **L1/L2 related-work research — COMPLETE / PRE-EXECUTION INPUT** — surveys Reality Mining, Eigenbehaviors, StudentLife, ExtraSensory, personal sensing/informatics, context-aware computing, missingness/data-quality research, SOSA/SSN, SensorThings, OpenTelemetry, CloudEvents, W3C PROV, and OSS systems including AWARE, Beiwe, mindLAMP, RAPIDS, ActivityWatch, and Open mHealth. Main conclusion: PPF should reuse minimal event/provenance semantics instead of inventing them, while directly proving its unique `opportunity + observability + correction/deletion + abstention` contract. See [ppf-l1-l2-related-work-research.md](ppf-l1-l2-related-work-research.md).
- **PPF-L1/L2 research synthesis — FROZEN / INPUT TO PROTOCOL V2** — freezes the evidence-backed revision requirements R1-R7: observation quality/coverage, three conceptual times, capture-policy provenance, compositional context, quality-vs-confidence separation, provenance-bearing user feedback, and a tiny standards-inspired event envelope. See [ppf-l1-l2-research-synthesis.md](ppf-l1-l2-research-synthesis.md).
- **PPF-L1/L2 Foundation Protocol v2 — FROZEN / L1 PASS / L2 PASS** — freezes the implementation-independent L1 semantic contract and platform-neutral L2 event-foundation proof requirements. L1 passed with 41 scenarios. L2 passed with one small event model covering 60 fixtures, including explicit opportunity, missingness, three-time, provenance, multi-device, raw/derived, correction/deletion, compositional-context, and optional health-boundary semantics. Numeric pattern confidence is not required. The L3 benchmark protocol is separately frozen below; L3 benchmark execution, L4/L5, and PPF implementation remain blocked. See [ppf-l1-l2-foundation-protocol.md](ppf-l1-l2-foundation-protocol.md).
- **Protocol v2 research traceability — FROZEN PRE-EXECUTION ARTIFACT** — maps each research finding to its Protocol v2 requirement, affected gate, and later proof artifact. Its embedded execution status records the protocol-freeze point before L1 execution. See [ppf-l1-l2-protocol-v2-traceability.md](ppf-l1-l2-protocol-v2-traceability.md).
- **Protocol v2 QA — PASS / FROZEN PRE-EXECUTION REVIEW** — verifies research coverage, frozen gates, scope integrity, and no architecture leakage at the protocol-freeze point. Its statement that L1/L2 were unexecuted is historical to that review; current L1 status is recorded below. See [ppf-l1-l2-protocol-v2-qa.md](ppf-l1-l2-protocol-v2-qa.md).
- **PPF-L1 — PASS / FROZEN; PPF-L2 — PASS / FROZEN** — the L1 semantic proof defines the implementation-independent Recognize-Me contract and passes L1-G1 through L1-G13 over 41 scenarios. The separately authorized L2 proof defines the [Personal Event Foundation contract](ppf-personal-event-contract.md), validates [60 fixtures](ppf-l2-fixtures.md) including 35 adversarial cases and 5 cross-platform equivalence pairs, and passes L2-G1 through L2-G18 in the [independent semantic review](ppf-l2-semantic-review.md). The L3 benchmark protocol is separately frozen below; L3 benchmark execution, L4/L5, and production PPF remain blocked.
- **PPF-L3 Benchmark Protocol — PASS / FROZEN; BENCHMARK EXECUTION — NOT STARTED** — defines method-independent latent personal truth, a separate expected visible semantic answer, identifiability, opportunity-grounded synthetic generation, adversarial/negative controls, protected split/seed discipline, counterfactual pairs, semantic matching, and a metric vector that makes false promotion, abstention, scope, drift, correction, deletion, and staleness failures individually visible. Protocol QA passes L3P-G1 through L3P-G21. See the [benchmark protocol](ppf-l3-benchmark-protocol.md), [ground-truth contract](ppf-l3-ground-truth-contract.md), and [benchmark QA](ppf-l3-benchmark-qa.md). No generator or pattern method has been implemented or evaluated; L4/L5 and production PPF remain blocked.

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
