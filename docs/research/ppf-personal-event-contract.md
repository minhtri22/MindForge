# PPF-L2 Personal Event Foundation Contract

Status: **RESEARCH CONTRACT / L2 PROOF ARTIFACT**
Protocol authority: `ppf-l1-l2-foundation-protocol.md`
Schema: `data/ppf-l2/schema.json`
Scope: representability only; no pattern discovery, scoring, admission, retrieval, or production collection.

## 1. Purpose and success criterion

PPF-L2 asks one bounded question:

> Can one small, platform-neutral personal-event model represent the evidence distinctions required by the frozen PPF-L1 semantic contract across realistic and adversarial device/source situations?

The model succeeds only when a reviewer can inspect an event record and distinguish occurrence from missingness, opportunity from outcome, source time from ingestion time, raw from derived evidence, independent corroboration from replication, and correction/deletion lineage from silent overwrite.

The contract is deliberately weaker than a production event platform. It defines evidence semantics only.

## 2. Core envelope

Every event has the same small envelope:

| Field | Required | Semantic role |
|---|---:|---|
| `schema_version` | yes | Identifies the frozen research schema semantics. |
| `event_id` | yes | Foundation-local immutable identity for this evidence record. |
| `event_type` | yes | Platform-neutral semantic type of the evidence item. |
| `source` | yes | Platform/device/provider provenance and optional source identity. |
| `time` | yes | Three conceptual times: phenomenon, result/observed, ingestion. |
| `evidence_kind` | yes | Raw, derived, user assertion/feedback, source control, or observability record. |
| `capture_policy` | conditional | Provenance for source observability and collection limits. |
| `observability` | yes | Whether occurrence/non-occurrence was observable and why evidence may be missing. |
| `opportunity` | optional | A concrete opportunity/outcome relation when the claim requires a denominator or choice point. |
| `context` | yes | Compositional typed dimensions with known/unknown/conflicting state. |
| `entities` | optional | Opaque entity references plus known/unknown relationship semantics. |
| `quality` | yes | Observation quality and coverage, separate from pattern confidence. |
| `provenance` | yes | Derivation procedure and input references when applicable. |
| `relations` | optional | Cross-record provenance, replication, correction, deletion, and targeting. |
| `payload` | yes | Extensible event-specific observation data. |

Platform-specific SDK fields are not part of the core envelope. Platform/provider details may be retained under source metadata or payload only when they are evidence, not foundation semantics.

## 3. Identity and source semantics

`event_id` identifies the foundation record. `source.platform`, `source.device_class`, and `source.provider` identify where the evidence came from. `source.source_event_id` preserves a provider-side identity when one exists.

These identities serve different purposes:

- equal timestamps do not imply equal identity;
- repeated provider identity does not automatically create another behavioral occurrence;
- synchronized copies may remain separate records if `SAME_ORIGIN_REPLICATED` makes the relationship explicit;
- a reused provider identity for revision requires correction/supersession/invalidation/deletion lineage rather than silent replacement.

The contract does not require a broker, globally unique SDK identifier, or provider-specific identifier format.

## 4. Three-time model

Each event carries:

1. **phenomenon time** — when the underlying behavior/state occurred; it has `start` and optional `end`;
2. **result-or-observed time** — when the source produced or observed the result;
3. **ingested time** — when the foundation received the record.

The three times may be equal, close, or materially different. Delayed wearable synchronization, batching, offline upload, and out-of-order arrival must not rewrite behavioral order into ingestion order.

`phenomenon_time.timezone` may preserve named local-time context. Offset-aware timestamps remain the authoritative instants. `timing_quality` may state `KNOWN`, `APPROXIMATE`, `CLOCK_SKEW_SUSPECTED`, or `UNKNOWN`; the foundation does not silently correct uncertain device clocks.

An episode is represented by `phenomenon_time.start` plus `end`. A separate Episode class is unnecessary for the L2 distinctions.

## 5. Capture policy and expected observability

Source observations can only support absence/non-occurrence reasoning when collection conditions are explicit enough to know what could have been observed.

`capture_policy` therefore records a small provenance vocabulary such as continuous, periodic, event-driven, foreground-only, background-enabled, history-limited, user-triggered, passive wearable, batched, or unknown capture. `expected_observability` records whether the source was expected to cover the relevant period.

Optional details may describe sampling intervals, duty cycle, history windows, or provider limitations. These details remain source provenance; they are not a new scheduling or collection subsystem.

## 6. Observability and missingness

`observability.state` separates:

- `OBSERVED_OCCURRENCE`;
- `OBSERVABLE_NON_OCCURRENCE`;
- `NO_OBSERVATION`;
- `SOURCE_UNAVAILABLE`;
- `PERMISSION_UNAVAILABLE_OR_UNKNOWN`;
- `OUTSIDE_CAPTURE_WINDOW`;
- `HISTORY_UNAVAILABLE`;
- `DATA_DELAYED`;
- `UNKNOWN_OUTCOME`.

Missing-like states require a `missingness_reason`, such as sampling gap, platform restriction, permission limitation, device disconnection, wearable non-wear, sync delay, history unavailability, or missing-by-design.

The critical invariant is:

```text
NO_OBSERVATION != OBSERVABLE_NON_OCCURRENCE
```

Missing evidence cannot become behavioral negative evidence merely because no event arrived.

## 7. Opportunity representation

Opportunity is represented as one small optional object on the evidence record:

```text
opportunity.id
opportunity.state
opportunity.alternatives[]
opportunity.observability
```

The allowed states are opportunity, occurrence, observable non-occurrence, and unknown outcome.

This is intentionally not a separate opportunity service, denominator engine, or architecture. L1 needs a reviewer to know that an opportunity existed, what outcome was observed when applicable, whether a non-occurrence was observable, and what alternatives were meaningful. One relation/context object is sufficient for that representability proof.

An `OBSERVABLE_NON_OCCURRENCE` event is invalid unless an explicit opportunity carries the same outcome state. A known opportunity with permission loss or incomplete coverage remains `UNKNOWN_OUTCOME`, not a false negative.

## 8. Context and entities

Context is compositional. Each dimension is independent and may be:

- `KNOWN`, with an optional value;
- `UNKNOWN`;
- `CONFLICTING`, with optional competing values and source references.

This lets one event simultaneously carry place, social, temporal, environmental, or other dimensions without flattening them into a single platform-specific context label.

Entity references are opaque foundation identifiers. A relationship may be known or unknown. Unknown identity/relationship semantics must remain unknown rather than being filled from a behavioral guess.

## 9. Observation quality and coverage

`quality.quality_state` is `GOOD`, `DEGRADED`, or `UNKNOWN`. `quality.coverage_state` is `COMPLETE`, `PARTIAL`, `UNKNOWN`, or `NOT_APPLICABLE`.

These fields describe the evidence record and collection coverage. They are explicitly separate from confidence in a future personal pattern. L2 defines no pattern confidence, routine score, preference score, admission score, or calibrated probability.

## 10. Raw, derived, user, and control evidence

`evidence_kind` separates six roles:

| Kind | Meaning |
|---|---|
| `RAW_OBSERVATION` | Source-reported observation before a higher-level derivation. |
| `DERIVED_OBSERVATION` | Observation produced by a derivation/feature/episode procedure. |
| `USER_ASSERTION` | Explicit user-supplied factual/semantic statement. |
| `USER_FEEDBACK` | User confirmation, rejection, correction, annotation, or contextual feedback. |
| `SOURCE_CONTROL` | Invalidation, deletion, reset, or source-level control evidence. |
| `OBSERVABILITY_RECORD` | Evidence about whether another phenomenon/outcome could be observed. |

A derived observation is still evidence, not a pattern. If the derivation procedure is known, `provenance.procedure` is required and `input_event_refs` may identify source evidence. If imported evidence is known to be derived but its procedure is unavailable, `procedure_status=UNKNOWN` preserves that uncertainty rather than fabricating provenance.

## 11. Multi-device relationships

Cross-device evidence must not force the reviewer to guess whether two records are duplicates or independent support. The minimal relationship vocabulary is:

- `SAME_ORIGIN_REPLICATED` — synchronized copies of one origin;
- `INDEPENDENT_CORROBORATION` — separately sourced observations supporting the same phenomenon;
- `UNKNOWN_RELATIONSHIP` — records may be related, but available provenance cannot decide.

The contract does not deduplicate, weight, or score these relationships. It only makes the distinction representable.

## 12. User evidence: provenance, target, scope, and time

User feedback is an evidence event, not an out-of-band overwrite. Its source/provider identifies the feedback surface or user origin; the event time identifies when it was made; `TARGETS`, `CORRECTS`, or `CONTEXT_CORRECTS` links it to affected evidence; payload may carry bounded scope such as one event or a date range.

This supports the L1 requirement that explicit user statements and corrections have provenance without granting them implicit global scope.

## 13. Correction, supersession, invalidation, deletion, and reset lineage

The relation vocabulary includes:

- `DERIVED_FROM`;
- `CORRECTS`;
- `SUPERSEDES`;
- `INVALIDATES`;
- `DELETES`;
- `TARGETS`;
- `CONTEXT_CORRECTS`.

Lineage is append-only at the semantic level: a later record expresses what happened to an earlier record. The contract does not dictate database retention after a deletion request. It proves that deletion intent and its target can be represented before a storage/privacy policy applies physical removal.

Reset is represented as a source-control event with explicit target scope. L2 does not define pattern reset, model reset, device control, or execution authority.

## 14. Schema version decision

The frozen research schema version is:

```text
ppf-l2/1
```

The version is intentionally local to this proof. It means the record obeys the L2 semantic contract and fixture schema frozen in this research execution. It is not a public API version, migration promise, or production storage contract.

A version field is retained because later scientific review must be able to distinguish evidence encoded under different contract semantics. A more elaborate compatibility/version-negotiation system would add no L2 proof value.

## 15. Minimality review

The model uses one event object plus small nested semantic groups. No subclass hierarchy is required for calendar, location, workout, wearable, health, feedback, correction, or observability evidence.

The following tempting additions were rejected because the fixtures do not require them:

- separate Episode/Event classes;
- separate Opportunity architecture;
- device registry service;
- provenance graph database;
- broker/event-bus semantics;
- platform SDK adapter types in the core model;
- pattern status, confidence, scoring, or admission fields;
- storage, indexing, query, retention, or synchronization implementation;
- ontology/RDF/OGC/OpenTelemetry/CloudEvents runtime dependencies.

The standards and related-work research informed distinctions; none becomes a runtime dependency.

## 16. Compatibility with frozen L1 semantics

The L1→L2 dependencies are representable as follows:

| L1 dependency | L2 representation |
|---|---|
| observable opportunity/non-occurrence | `opportunity` plus `observability` |
| observability/missingness | capture policy, observability state, missingness reason, coverage |
| compositional context | independent context dimensions with known/unknown/conflicting status |
| temporal evidence | phenomenon/result-or-observed/ingested time |
| source/provenance | source envelope plus derivation provenance |
| observation quality | quality and coverage fields |
| relationship/entity identity | entity references and relationship status |
| user feedback provenance/scope/time | USER_FEEDBACK/USER_ASSERTION events plus relations and phenomenon/event time |
| correction/supersession/deletion lineage | explicit lineage/control relations |
| raw/derived evidence | `evidence_kind` plus derivation procedure/input references |

No L1 semantic category is redefined here. L2 only supplies the evidence representation L1 said a later layer would require.

## 17. Authority boundary

This contract gives PPF no authority to diagnose, treat, control a device, execute a user action, infer a pattern, or make a product decision. Health/medical-looking evidence remains optional source data and is carried opaquely unless a later separately authorized layer establishes additional semantics.

L3/L4/L5 and production PPF remain outside this contract.
