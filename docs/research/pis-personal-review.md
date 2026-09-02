# PIS Personal Intelligence Review

Status: INDEPENDENT ARCHITECTURE / RESEARCH REVIEW
Date: 2026-09-03
MindForge repo: `D:\WORK\RESEARCH\MindForge`
MindForge commit inspected: `3042ba08afb1e3bfffcec1841b44b3b2bc345e73`
PIS repo inspected: `D:\WORK\hdc\pis`
PIS commit inspected: `25e7a075dfe4f557e8113d6e8d017edfed518d35`

## Decision

Decision: SALVAGE
Confidence: MEDIUM

PIS has enough research material to salvage principles, selected contracts, tests, and persistence patterns, but it does not have a clean enough or sufficiently proven foundation to be kept as the architecture for MindForge-Mobile Personal Pattern Intelligence.

The strongest salvageable assets are:

- candidate != truth boundary;
- support plus counterexample evidence vocabulary;
- no runtime authority by default;
- audit/provenance orientation;
- event-log/transition/repetition primitives as baseline material;
- SQLite validated pattern memory pattern from V2-33, adapted to personal events;
- point-in-time evidence pack discipline from V2-39.

The major gaps are:

- no dedicated personal/device event schema;
- no opportunity-denominator model for personal routines;
- weak or absent user correction semantics;
- no true per-pattern/person/date-range deletion semantics;
- drift exists as batch-drift reporting, not pattern confidence decay/reversal;
- retrieval is financial library filtering, not context-aware personal retrieval;
- HDC, SLM hierarchy, and repair loop remain unproven complexity for the personal mobile use case.

This is not KEEP because the current architecture is multi-generation, dirty, and domain-shifted toward financial pattern MVP work. It is not REBUILD because important governance primitives and test ideas remain valuable. It is not STOP because source evidence exists and the personal-pattern substrate thesis remains plausible.

## Target Rubric

MindForge strategic target: "Recognize me, not know everything."

Operational rubric for Track B:

1. Observe: ingest timestamped personal/device/context events over time without assuming numeric traces as the primary data shape.
2. Discover: propose routines, preferences, relationship-conditioned behaviors, sequences, context-action associations, exceptions, and drift candidates.
3. Distinguish: resist false correlation using opportunities, non-occurrences, counterexamples, minimum evidence, abstention, and uncertainty.
4. Adapt: reduce confidence in stale patterns, detect reversal, form competing newer patterns, and retire old patterns when evidence changes.
5. Retrieve: answer current-context queries with ranked, confidence-aware, exception-aware, bounded, explainable patterns.
6. Explain / Forget: expose provenance and evidence; support correction, hiding, deactivation, and true technical deletion from state/index/cache.

## Discovery Evidence

PIS source/evidence was found locally at `D:\WORK\hdc\pis`. Key evidence includes:

- `src/pis_core/engine.py`: canonical runtime loop: validate -> adapt -> represent -> primitives -> external primitives -> candidate builder -> evidence scorer -> classifier -> boundary/result.
- `src/pis_core/contracts/input_envelope.py`: input envelope, risk policy, observe-only mode, and runtime-effect denial.
- `src/pis_core/contracts/pattern_candidate.py`: candidate contract with support/contradiction fields and authority denial.
- `src/pis_core/contracts/memory_record.py`: support/counter counts, promotion ladder, confidence formula.
- `src/pis_core/core/pattern_memory.py`: in-memory domain-neutral pattern memory with support/counter update and quarantine.
- `src/pis_core/primitives/repetition_detector.py`, `transition_detector.py`, `counterexample_miner.py`: event/sequence pattern primitives.
- `src/pis_core/evidence/evidence_scorer.py`: evidence orchestration, uncertainty, counterexample scoring, advisory status.
- `src/pis_core/evidence/drift_scorer.py`: batch-level drift report.
- `src/pis_core/slm_adapter.py`: optional SLM loop with learning traces and "auto-promote" language while asserting advisory-only boundary.
- `src/v2/gde/event_stream_family_generator.py`: V2 event stream family.
- `src/v2/gve/validated_pattern_memory.py`: SQLite-backed validated pattern, occurrence, outcome, counterexample store.
- `src/v2/gve/financial_outcome_tracker.py`: 3/6/12 month outcome backfill.
- `src/v2/api/pattern_library_service.py`: investor-facing pattern library service.
- `src/v2/news/news_evidence_service.py`: point-in-time news evidence service.
- `docs/v2/V2-38_Market_Pattern_Map_Closeout.md` and `docs/v2/V2-39_News_Evidence_Service_Closeout.md`: latest closeouts by file time in `docs/v2`.

MindForge target source read first:

- `D:\WORK\RESEARCH\MindForge\docs\research\personal-intelligence-two-track.md`

## Evidence Audit

Evidence strength: sufficient for architecture review, insufficient for product-fit acceptance.

Confirmed by code:

- PIS has a real canonical core loop, contracts, adapters, primitives, evidence scoring, audit events, and authority denial.
- PIS has structural counterexample mechanisms and in-memory support/counter tracking.
- V2 has SQLite persistence for validated financial pattern occurrences, outcomes, and counterexamples.
- V2 has point-in-time news evidence and evidence-pack guardrails.

Not confirmed by code:

- personal/device event stream ingestion;
- opportunity-aware personal routine detection;
- personal correction/invalidation persistence;
- true per-pattern/person/date-range deletion;
- context-aware personal retrieval;
- pattern-level temporal decay/reversal handling.

Docs/code contradiction or tension:

- The legacy core says one canonical runtime loop, while V2 financial/news/API work forms a separate product path.
- SLM adapter comments say "auto-promotes" and "auto-apply" while also saying advisory-only; MindForge should treat that as an unsafe naming/design tension.
- `PatternCandidateBuilder` passes `metadata=` into a legacy `PatternCandidate` contract that does not declare that field in the inspected file; this suggests contract drift across PIS generations.

## Architecture Inventory

| Component | Status | Evidence | Review |
|---|---:|---|---|
| inputs | PARTIAL | `PISInputEnvelope.data_type`, payload dict; adapters for time series, tabular, event log, graph, text event, HDC trace | Can ingest generic events, but no personal/device event contract with person/app/location/opportunity fields. |
| normalization | EXISTS | adapter classes in `src/pis_core/adapters` | Generic and useful, but not tailored to privacy/minimization or mobile personal event capture. |
| representation | EXISTS | `SequenceRepr`, `EventLogRepr`, `StateTransitionRepr`, `GraphRepr`, `FeatureSpaceRepr` | Useful primitives; too generic to encode personal semantics by itself. |
| candidate generation | EXISTS | primitive orchestrator plus V2 family generators | Real code exists, but much evidence is synthetic/financial/log/workflow oriented. |
| pattern representation | PARTIAL | `PatternCandidate`, V2 `PatternCandidate` dataclass | Represents candidates and evidence summary; personal pattern semantics are absent. |
| scoring/confidence | PARTIAL | `EvidenceScorer`, `MemoryRecord.compute_confidence`, V2 validation confidence | Advisory confidence exists, but not calibrated for personal behavior and not opportunity-aware enough. |
| evidence store | PARTIAL | `EvidenceStore` in memory; V2 SQLite memory/outcomes/news | Evidence is available, but personal provenance/deletion model absent. |
| counterexample handling | PARTIAL | `CounterexampleMiner`, `CounterexampleScorer`, `CounterexampleIndex`, V2 counterexamples | Counterexamples exist structurally, but opportunity/non-occurrence modeling is weak. |
| promotion/admission | PARTIAL | promotion ladder, recommended status, V2 validation flags | Good governance vocabulary; SLM auto-promote wording conflicts with personal safety preference. |
| retrieval | PARTIAL | V2 `find_similar_patterns`, Pattern Library filters | Financial query/filtering only; no MindForge current-context retrieval. |
| adaptation/drift | PARTIAL | `DriftScorer`; memory counterexamples can demote/quarantine | Drift reporting exists, but no pattern-level decay/reversal/retirement loop. |
| repair | PARTIAL | `regenerative_repair`, `shadow_repair` | Large legacy machinery; unproven for personal patterns. |
| memory/state | PARTIAL | in-memory core memory; SQLite V2 validated memory | Persistence exists in V2 financial store; core memory is ephemeral. |
| host interaction | PARTIAL | `PISBoundService`, API services | Boundaries exist; no MindForge-Mobile interface yet. |
| action authority | EXISTS | `allow_runtime_effect` rejected; runtime authority defaults to NONE; services return no recommendation/human decision required | Strong salvage candidate. |
| persistence | PARTIAL | V2 SQLite stores | Strong financial persistence example; not generalized to personal events. |
| deletion | ABSENT | only `clear()` on in-memory stores found; no SQLite per-pattern delete/forget APIs | Major blocker for personal system. |
| audit/provenance | EXISTS | audit logger, result hashes, provenance/evidence refs | Good, but append-only audit can conflict with personal deletion unless redesigned. |

## Actual Data Flow

Legacy core flow in `src/pis_core/engine.py`:

```text
PISInputEnvelope
-> schema/payload/source validation
-> adapter dispatch
-> canonical representation enrichment
-> internal primitives
-> optional external primitive registry
-> PatternCandidateBuilder
-> EvidenceScorer
-> PatternClassifier
-> boundary reports
-> PISAnalysisResult with audit events and hashes
-> optional SLM trace export if enabled
```

V2 financial product flow:

```text
financial/source/news payloads
-> financial adapters/case detectors/family generators
-> GVE validation
-> ValidatedPatternMemoryStore SQLite record_validation
-> FinancialOutcomeTracker records 3m/6m/12m outcomes
-> PatternLibraryService / AI evidence packs / Market Map / News Evidence
```

Real vs test/demo:

- Real code exists for generic core processing, V2 SQLite persistence, API service serialization, and news/document import.
- Much validation evidence is test/demo data: V2 financial snapshots, PNJ/FPT-style cases, generated benchmarks, synthetic log/text/workflow/event streams.
- V2-39 explicitly remains an MVP skeleton without live crawler dependency.

Persisted vs ephemeral:

- Persisted: V2 SQLite patterns, occurrences, outcomes, counterexamples, news documents/events; AI reader JSON state.
- Ephemeral: core `PatternMemory`, `EvidenceStore`, `CounterexampleIndex`, SLM pending traces/learned patterns unless external SLM persists elsewhere.

Decisions:

- PIS discovers/scores/recommends review status.
- Host/governance/user is supposed to decide actions.
- Some SLM comments say "auto-promotes"; this is risky language and should not be inherited for MindForge without redesign.

Confidence updates:

- Core memory confidence is `support / (support + counter + 2.0)`.
- Evidence confidence comes from support, recurrence, stability, predictive, compression, counterexample, uncertainty.
- V2 pattern confidence is stored/upserted from validation results; market map/news enrichment does not mutate confidence.

Negative evidence:

- Candidate contracts support contradicting observations.
- Counterexample miner and scorer exist.
- V2 financial store records failed outcomes as counterexamples.
- Missing piece: explicit opportunity/non-occurrence model for personal routines.

## Original Assumptions

| Assumption | Original reason | Evidence supporting it | Evidence against it | Still relevant? |
|---|---|---|---|---:|
| numeric trace first | Easy to define motifs/anomalies/recurrence on sequences | sequence/time-series adapters and early benchmarks | Personal behavior is event/context/person/action heavy | NO as default |
| HDC representation | Prior HDC integration and trace analysis | `HDCTraceAdapter`, `PISBoundService`, HDC trace data type | No evidence HDC beats simpler personal baselines; explain/delete harder | UNKNOWN |
| broad multidomain genericity | Reusable substrate across numeric/workflow/log/text/financial | many adapters/families | Personal MVP needs a smaller semantic vocabulary | PARTIAL |
| pattern-family taxonomy | Organize detectors and validation gates | family generators and GVE checks | Complexity outpaces personal use-case proof | PARTIAL |
| SLM hierarchy | Learn from traces, semantic layer | SLM adapter files | Auto-promote language and no causal evidence for personal benefit | UNKNOWN |
| repair loop | General recovery/repair research | regenerative/shadow repair packages | Does not directly solve correction, drift, retrieval, deletion | NO for MVP |
| workflow/log transfer | Prove family extensibility | V2-20..V2-22 docs/tests | Transfer success does not prove personal mobile value | PARTIAL |
| synthetic benchmarks | Fast controlled validation | many V2 test suites | Can overfit to invented cases; personal benchmark absent | PARTIAL |

## Personal Pattern Fit

Routine: PARTIAL. Repetition and event-stream windows can find repeated sequences, but no opportunity denominator like "17 occurrences / 21 leaving-office opportunities".

Preference: WEAK. Frequent occurrence can be detected, but preference vs availability vs habit vs companion constraint is not represented.

Relationship-conditioned behavior: WEAK. Person/contact can be arbitrary tokens, but no first-class relationship semantics or privacy treatment.

Sequence: PARTIAL/GOOD. Event n-grams and transition detectors are salvageable as baselines.

Context -> Action: PARTIAL. Transitions/correlation exist, but trigger vs coincidence is not distinguished strongly enough.

Exception: WEAK. Counterexamples exist, but "normally X, Friday Y" needs explicit conditional exception modeling.

Change / Drift: PARTIAL. Batch drift exists; pattern-level reversal and retirement do not.

## Counterexample / False-Correlation Audit

PIS has a real counterexample vocabulary, but it is not sufficient for personal intelligence.

Mechanisms found:

- contradicting observations in `PatternCandidate`;
- `CounterexampleMiner` searches structurally similar but non-matching regions;
- `CounterexampleScorer` weakens evidence based on contradiction ratio;
- `PatternMemory.record_counterexample` demotes/quarantines after counterexamples;
- V2 financial memory stores counterexamples from rejected/failed outcomes.

Missing mechanisms:

- explicit opportunities;
- non-occurrences;
- causal abstention;
- pattern-specific false-correlation tests for personal contexts;
- correction-weighted negative evidence;
- decay of old support.

Answer: PIS partially knows when not to conclude through evidence levels, uncertainty, and recommended statuses, but it does not yet have the opportunity/non-occurrence machinery needed to prevent "A happened before B five times, therefore user wants B" in personal event streams. This is a major flaw for MindForge-Mobile.

## Drift / Reversal Audit

Scenario: weeks 1-4 coffee at 08:00; weeks 5-8 no morning coffee, coffee at 14:00.

Expected personal PIS behavior:

- reduce confidence in old 08:00 pattern;
- form competing 14:00 pattern;
- explain that behavior changed around week 5;
- eventually retire or demote old pattern;
- avoid presenting two simultaneous stable preferences without caveat.

Current PIS:

- Batch-level drift can report distribution differences.
- Core memory confidence only accumulates support/counter and has no time decay.
- Counterexamples can demote/quarantine if explicitly recorded.
- No clear automatic path converts non-occurrence after week 5 into counterevidence against 08:00.

Verdict: PARTIAL. Drift is detected as batch/statistical difference, not maintained as personal pattern adaptation.

## User Correction Audit

Scenario: PIS says "You usually do X"; user says "No, I don't. Stop using that."

Current support:

- `PatternMemory.apply_feedback` can increment support or counter count.
- `CounterexampleIndex.add_from_feedback` can store a counterexample from feedback.
- SLM comments mention feedback loop.

Gaps:

- no first-class correction intake contract;
- no forced invalidation policy;
- no retrieval exclusion;
- no persisted correction ledger in the V2 memory store;
- no cache/index cleanup;
- no weighting model where explicit user correction dominates passive observation.

Verdict: ABSENT/PARTIAL. The pieces exist as generic feedback, but not as a safe product-grade personal correction mechanism.

## Forget / Delete Audit

Required deletion scenarios:

- delete pattern X;
- delete all patterns involving person Y;
- delete events from date range;
- reset all personalization.

Current support:

- In-memory stores have `clear()`.
- V2 SQLite store exposes record/list/get/find functions but no per-pattern/person/date delete or forget API in inspected code.
- Audit logs are append-only, which is good for provenance but needs privacy-aware deletion/redaction design.

Verdict: ABSENT. This blocks KEEP for personal use. MindForge must define hide, deactivate, delete, and audit-redact semantics before integration.

## Retrieval Audit

Scenario:

```text
Friday
17:40
leaving office
user says: "nhu moi khi"
```

Useful PIS response should return a ranked routine candidate, confidence, context match, exceptions, evidence/counterexamples, and uncertainty.

Current PIS:

- V2 `find_similar_patterns` ranks by confidence/last_seen with optional financial filters.
- Pattern Library exposes details, outcomes, counterexamples, and evidence refs.
- No inspected API accepts current personal context and returns routine/preference/exception candidates.

Verdict: PARTIAL. Retrieval infrastructure exists, but context-aware personal retrieval is absent.

## Authority / Safety Boundary

This is one of PIS's strongest salvageable properties.

Current PIS can discover, score, validate, and recommend review status. It should not execute actions. Evidence:

- input risk policy rejects runtime effects;
- candidate runtime authority defaults to none and rejects non-none;
- drift report has no runtime authority;
- V2 financial/news services set recommendation policy to none and human decision required.

Risk:

- SLM adapter comments describe "auto-promote" and "auto-apply", even while stating advisory-only. For MindForge, this language should be removed or fenced behind host/user governance.

Verdict: SALVAGE with stricter naming.

## HDC Review

HDC is not protected architecture for MindForge.

Potential value:

- compact signatures;
- similarity search;
- possible robustness for noisy traces.

Problems:

- no evidence found that HDC beats counts+decay, context-conditioned counts, Markov transitions, embeddings, or small online classifiers on personal patterns;
- categorical/person/context explainability is harder than simple symbolic event patterns;
- deletion and provenance are harder when raw events collapse into dense representations;
- mobile cost is unknown.

Verdict: UNKNOWN / UNPROVEN. Keep HDC only as an optional benchmark contestant, not as the core default.

## SLM / Hierarchy Review

SLM modules exist and include semantic disambiguation plus autonomous trace learning. However:

- the user value for personal patterns is not demonstrated;
- autonomous promotion language is misaligned with MindForge's host/user authority boundary;
- actual end-to-end use appears optional and trace-export based;
- simpler state logic may solve the first personal benchmark subset.

Verdict: UNPROVEN COMPLEXITY. Do not carry into MVP architecture unless benchmark evidence justifies it.

## Repair Loop Review

Repair mechanisms exist as regenerative/shadow repair research and validation-bound suggestions. They are not a direct answer to personal pattern intelligence.

For MindForge, repair should mean user correction, drift handling, counterexample pressure, and retrieval quality improvement. The existing repair loop is broader and heavier than necessary.

Verdict: candidate for removal from MVP. Salvage only tests/principles around counterexample survival and audit trail.

## Mobile / Edge Suitability

Mobile-friendly:

- event-log primitives can be incremental if redesigned;
- SQLite local persistence is plausible;
- no-runtime-authority contract is mobile/OS compatible;
- evidence packs can minimize context sent to external models.

Mobile-risky:

- large generic detector zoo;
- pairwise window comparisons and full-history scans;
- optional external primitive plugins;
- SLM/autonomous learning loop;
- HDC or dense representations without deletion cost proof.

Unknown:

- RAM and CPU cost under real mobile event volume;
- battery impact;
- write amplification for audit/provenance;
- encrypted local storage plan.

## Privacy Architecture

Current PIS is privacy-compatible in principle, not privacy-complete.

Good:

- can keep derived patterns local;
- evidence refs/provenance exist;
- V2 secret registry redacts tokens;
- AI reader prompt forbids outside knowledge and requires evidence refs.

Gaps:

- no personal data minimization contract;
- no field-level sensitivity labels;
- no delete/forget semantics;
- no event retention policy;
- no guarantee external models receive only minimized context;
- append-only audit needs privacy-aware redaction/deletion policy.

Verdict: requires redesign before mobile personal use.

## Personal Pattern Benchmark v0

| ID | Scenario | Event stream | Hidden truth | Expected pattern / abstention | Counterexamples | Metric | Failure |
|---|---|---|---|---|---|---|---|
| B1 | Routine formation | 21 weekday leave-office sessions; 17 include Maps->home->playlist | commute-home routine | detect routine with confidence and denominator | 4 non-routine days | precision, time-to-discovery | no denominator or overconfident claim |
| B2 | Routine absence/coincidence | A precedes B 5 times in sparse data | coincidence | abstain / observe more | many opportunities where A not followed by B | abstention accuracy | promotes false routine |
| B3 | Routine drift | coffee 08:00 weeks 1-4, 14:00 weeks 5-8 | routine shifted | old decays, new emerges | missing 08:00 after week 5 | adaptation lag | reports two stable routines without drift |
| B4 | Preference emergence | lunch choices across contexts | Japanese preference in solo meals | preference candidate | group meals not Japanese | precision | confuses availability/frequency with preference |
| B5 | Preference reversal | prefers A then switches to B | reversal | old preference demoted, new candidate | old support before reversal | reversal detection | old remains dominant |
| B6 | Conditional preference | with spouse prefers Japanese; with coworkers prefers quick meals | condition matters | relationship-conditioned preference | same restaurant type absent in other relationship contexts | conditional precision | emits global preference |
| B7 | Rare exception | usually drive, but heavy rain -> taxi | rare important exception | exception candidate with uncertainty | normal dry days | exception recall | averages exception away |
| B8 | Relationship behavior | after work messages person X, except Fridays | relationship-conditioned routine | routine plus Friday caveat | Fridays no message or message Y | relationship/context accuracy | person treated as arbitrary token only |
| B9 | Temporal sequence | app sequence mail->calendar->maps | ordered sequence | sequence pattern | same actions in different order | sequence precision | bag-of-events false positive |
| B10 | Context-action | leaving gym -> music app | context action association | candidate with opportunity base | music app opened in other contexts | false discovery rate | treats generic frequent action as triggered |
| B11 | Conflicting evidence | same context produces two actions | ambiguous | abstain or expose split | balanced evidence | calibration/conflict metric | picks one as truth |
| B12 | User correction | user rejects "usually X" | correction authoritative | invalidated/excluded pattern | prior passive support | correction response time | keeps retrieving rejected pattern |
| B13 | Deletion/forgetting | delete patterns involving person Y | true removal | no retrieval, no stale index regeneration without new events | old cached/indexed refs | deletion correctness | pattern resurfaces from stale cache |
| B14 | Insufficient evidence | only 2 occurrences | no pattern yet | abstain | low sample count | abstention accuracy | creates high confidence pattern |
| B15 | Contextual retrieval | Friday 17:40 leaving office, "nhu moi khi" | commute routine with Friday exception | ranked routine, exception, evidence | Friday alternatives | top-k retrieval precision | irrelevant or unqualified pattern returned |

## Metrics

Quality metrics:

- pattern precision;
- pattern recall;
- false discovery rate;
- false promotion rate;
- confidence calibration;
- evidence provenance completeness;
- counterexample recall;
- abstention accuracy.

Adaptation metrics:

- time-to-discovery;
- drift adaptation lag;
- reversal detection accuracy;
- stale pattern retirement lag;
- user-correction response time;
- correction dominance over passive evidence.

Systems metrics:

- memory footprint;
- local storage growth;
- update latency;
- query latency;
- background CPU;
- battery proxy if available;
- deletion correctness;
- index/cache cleanup latency.

First bounded experiment:

- B1, B2, B3, B12, B13, B15.

Reason: this subset tests the minimum viable personal loop: form a routine, avoid false correlation, adapt to drift, obey user correction, delete truly, and retrieve in context.

## Baselines

Baseline A: frequency/count + threshold.

- Per context bucket, count action/sequence occurrences and promote only above threshold.
- Purpose: prove whether simple counts solve B1/B14.

Baseline B: frequency + exponential decay.

- Same as A, but old evidence decays by time.
- Purpose: test B3/B5 drift/reversal before adding complex PIS machinery.

Baseline C: context-conditioned counts/rules.

- Buckets include weekday/time/location/person/app/device state.
- Purpose: test B6/B8/B10/B15.

Optional Baseline D: Markov/sequential baseline.

- Estimate transition probabilities between actions in context.
- Purpose: test B9 sequence with a simple method.

Optional Baseline E: embedding retrieval baseline.

- Store compact pattern summaries and retrieve nearest pattern by current context.
- Purpose: compare retrieval quality, not discovery.

Answer to adversarial question: if a 100-line counts+decay baseline solves most of B1/B2/B3/B12/B15, legacy PIS should not remain complex. It should contribute contracts, evidence vocabulary, tests, and maybe selected primitives only.

## Salvage Matrix

| Area | Keep | Modify | Discard for MVP |
|---|---|---|---|
| candidate != truth | yes | rename fields for personal patterns | no |
| authority denial | yes | harden SLM language | no |
| evidence/counterexample contracts | yes | add opportunities/non-occurrences/corrections | no |
| core event primitives | yes | simplify as baselines | no |
| financial V2 memory | concept only | adapt schema to personal events | no |
| V2 news point-in-time evidence | concept only | use for provenance/evidence history pattern | no |
| HDC | no default | benchmark optional | maybe |
| SLM/autonomous hierarchy | no default | benchmark optional | likely |
| repair loop | no default | keep audit/counterexample lessons | likely |
| market map | concept only | transform into personal pattern map | no |
| AI reader guardrails | yes conceptually | use as evidence-only explanation layer | no |

## Recommended Next Research Plan

1. Freeze legacy PIS as research input, not product architecture.
2. Define `PersonalEvent` and `PersonalPatternCandidate` contracts from MindForge target, not from financial PIS.
3. Build Personal Pattern Benchmark v0 with B1-B15 fixtures.
4. Implement only baselines A/B/C first.
5. Run legacy PIS primitives as optional contestants where they can consume the same event stream.
6. Decide whether HDC/SLM/repair earn inclusion from measured benchmark results.
7. Only after B1/B2/B3/B12/B13/B15 pass, define MindForge-Mobile retrieval API.

## Final Architecture Recommendation

Use PIS as a research ancestor, not as the first MindForge-Mobile PIS architecture.

The first MindForge PIS should be a smaller local personal-pattern service:

```text
PersonalEvent stream
-> privacy/minimization filter
-> opportunity builder
-> simple baseline detectors
-> candidate/evidence/counterexample store
-> pattern-level decay/drift/correction/delete loop
-> context-aware retrieval API
-> evidence-only explanation pack
-> MindForge-Mobile interpreter
```

Legacy PIS should enter this as:

- source of contract language;
- detector/baseline candidates;
- cautionary examples of over-generalization;
- test seeds for counterexamples, advisory boundary, provenance, and point-in-time evidence.

Final decision remains SALVAGE.

## What Evidence Would Change This Decision

Evidence that could upgrade SALVAGE to KEEP:

- PIS passes Personal Pattern Benchmark v0 B1-B15 against simple baselines with materially better precision, abstention, drift, correction, deletion, and retrieval metrics.
- HDC/SLM/repair provide measured benefit over counts+decay/context-count baselines on personal event streams.
- A clean personal retrieval API exists and returns ranked, exception-aware, explainable results for current MindForge context.
- Deletion and user correction are technically complete across store, index, cache, audit, and retrieval.

Evidence that could downgrade SALVAGE to REBUILD:

- Simple baselines solve the first bounded benchmark subset at similar or better quality and much lower cost.
- Legacy PIS cannot be made opportunity-aware without distorting its contracts.
- HDC/SLM/repair dominate implementation cost without measured personal benefit.

Evidence that could downgrade to STOP:

- Explicit pattern substrate does not improve MindForge-Mobile outcomes over simple local memory plus retrieval.
- Users reject or ignore pattern explanations even when technically correct.
