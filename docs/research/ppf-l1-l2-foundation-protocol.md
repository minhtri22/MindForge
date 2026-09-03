# PPF-L1/L2 Foundation Protocol

Version: **2**

Status: **FROZEN FOR EXECUTION REVIEW**

Implementation: **NOT AUTHORIZED**

L1 execution: **NOT STARTED**

L2 execution: **NOT STARTED**

Date: 2026-09-03

Track:

```text
Track B — Personal Pattern Foundation (PPF)
```

Mission:

> Prove, from first principles, the minimum semantic and event foundation required for a local system to reliably recognize one person over time.

This protocol covers only:

```text
PPF-L1 — Define “Recognize Me”
PPF-L2 — Personal Event Foundation
```

It does not authorize L1/L2 proof execution, fixtures, schema/validator implementation, pattern algorithms, production PPF, mobile SDK integration, MindForge-Mobile integration, or L3/L4/L5 work.

Legacy PIS is **HISTORICAL ONLY** and outside the PPF execution path. PPF is **GREENFIELD FOUNDATION RESEARCH**.

---

# 1. Protocol v2 revision basis

Protocol v2 preserves the v1 first-principles rationale and strengthens it using completed research. Git history preserves v1 provenance; this document records the evidence that changed the frozen requirements.

Canonical inputs reviewed in full:

- `docs/research/personal-intelligence-two-track.md`
- `docs/research/ppf-device-platform-research.md`
- `docs/research/ppf-l1-l2-related-work-research.md`
- `docs/research/ppf-l1-l2-research-synthesis.md`
- `docs/research/README.md` (canonical research index/status)
- Protocol v1 in this file's Git history

Research-driven changes frozen into v2:

1. observation quality/coverage is explicit and distinct from pattern confidence;
2. time expands to `phenomenon_time`, `result_or_observed_time`, and `ingested_time`;
3. capture policy and expected observability become provenance;
4. context is compositional/multi-label;
5. explicit user feedback is provenance-bearing evidence rather than silent mutation;
6. the event envelope remains small while borrowing proven semantics from SOSA/SSN, SensorThings, OpenTelemetry, CloudEvents, and W3C PROV;
7. the L2 fixture floor increases from 27+ to **40+** to cover missingness, timing, multi-device, correction, and acquisition failure modes before algorithms exist.

These standards and systems are semantic references, not framework dependencies.

---

# 2. Research ladder and hard principle

PPF remains staged:

```text
L1 — Define “Recognize Me”
L2 — Personal Event Foundation
L3 — Ground-Truth Personal Pattern Benchmark
L4 — Minimal Baselines
L5 — Minimum Missing Mechanism
        ↓
Feasibility Decision
        ↓
Only then compose proven layers
```

Each layer must earn the right to exist. A later layer may not redefine an earlier layer merely to make an implementation succeed.

> **Architecture follows evidence; evidence does not follow architecture.**

No implementation architecture is selected during L1/L2 proof definition.

---

# 3. Why L1/L2 precede implementation

Completed research establishes that useful personal signals exist across phones, watches, accessories, health repositories, user input, and app/system sources, but their observability is inherently partial. Permission, entitlement, background limits, history windows, sampling policy, non-wear, disconnection, batching, synchronization, and source quality all affect what evidence exists.

Therefore these implications are invalid:

```text
no observation -> behavior did not occur
frequency -> preference
arrival order -> behavioral order
phone + watch records -> independent evidence
high observation quality -> high pattern confidence
context A precedes behavior B -> A caused B
```

L1/L2 are semantic and evidence-foundation proofs. They must make these distinctions testable before any pattern algorithm is admitted.

---

# 4. PPF-L1 — Define “Recognize Me”

## 4.1 Research question

> What observable, implementation-independent outputs are necessary and sufficient for a system to demonstrate that it recognizes a person's recurring behavior, preferences, context dependencies, exceptions, corrections, and changes over time?

L1 defines semantics only. It does not choose discovery, scoring, storage, retrieval, inference, or mobile architecture.

## 4.2 L1 semantic categories

L1 must define and keep distinct:

```text
FACT
OBSERVATION
CURRENT CONTEXT
PATTERN
ROUTINE
PREFERENCE
RELATIONSHIP-CONDITIONED BEHAVIOR
TEMPORAL SEQUENCE
CONTEXT→ACTION ASSOCIATION
EXCEPTION
CHANGE/DRIFT
EXPLICIT USER CORRECTION
```

### Fact

A directly asserted or otherwise established personal datum whose semantics are not themselves a recurring behavioral pattern.

### Observation

A provenance-bearing record that a source observed, derived, or explicitly reported something. An observation is evidence; it is not automatically a fact, preference, routine, or pattern.

### Current context

The currently applicable contextual dimensions relevant to interpretation. Context may be multi-label/compositional rather than one exclusive category.

### Pattern

A supported recurring or conditional personal-behavior assertion derived from evidence under a defined scope. A pattern is not a raw observation, immutable fact, preference by default, or causal claim. Routine, preference, relationship-conditioned behavior, temporal sequence, context-action association, exception, and change/drift are distinct pattern semantics with their own proof obligations.

### Routine

A recurring behavior under comparable **observable opportunities and context**. Repetition count alone is insufficient.

```text
18 home commutes / 27 observable commute opportunities
```

is semantically different from:

```text
18 observed home commutes / unknown opportunity denominator
```

### Preference

A repeated selection when a meaningful choice opportunity and meaningful alternatives existed. Frequency without alternatives does not establish preference.

```text
choice opportunity + alternatives + selected outcome
```

must be representable. `15 Japanese meals` alone does not prove preference.

### Relationship-conditioned behavior

Behavior whose association changes with a person/entity relationship or social context.

### Temporal sequence

A recurring ordered relation in which temporal ordering is semantically relevant.

### Context→action association

A recurring association between a compositional context and an action/outcome. It is an association, not a causal claim.

Allowed language includes `associated with`, `conditioned on`, and `observed under`. Causal claims require a future separately authorized causal framework.

### Exception

A meaningful conditional deviation from a broader pattern without automatically invalidating the broader pattern.

### Change/drift

A previously supported behavior weakens, reverses, changes scope, or becomes stale. Apparent change caused only by telemetry coverage degradation must not be labeled drift.

### Explicit user correction

Provenance-bearing user feedback that confirms, rejects, edits, qualifies, corrects, deletes, or resets personal state. Correction does not silently overwrite historical evidence.

## 4.3 Context composition

L1 must allow simultaneous contextual dimensions such as:

```text
time = Friday 17:40
location_category = work_exit
social = alone
activity = walking
calendar = workday-ended
device_state = phone+watch available
```

No large universal context ontology is frozen. Context must remain small, extensible, typed enough to test, and platform-neutral.

## 4.4 Pattern is not causality

L1 must reject causal overclaim. These are invalid without separate causal evidence:

```text
A often precedes B -> A causes B
context C co-occurs with action D -> C causes D
```

L1 scenarios must later include false-correlation cases such as sparse coincidence, confounder/context split, Simpson-like aggregate effects, rare exceptions, and missing telemetry.

## 4.5 Abstention and semantic state

Recognizing a person includes knowing when not to claim a pattern.

Mandatory semantic states include equivalents of:

```text
SUPPORTED
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
STALE
UNKNOWN_CONTEXT
NOT_OBSERVABLE
USER_REJECTED
SUPERSEDED
DELETED
```

`SUPERSEDED` belongs at semantic level because replacement/correction must be distinguishable from deletion.

A numeric confidence score is **OPTIONAL / FUTURE / REQUIRES CALIBRATION PROOF**. L1/L2 do not require numeric pattern confidence.

## 4.6 Observation quality is not pattern confidence

This is a hard invariant:

```text
observation_quality != pattern_confidence
```

Poor observation quality or coverage describes weakness in a source/window. It does not itself determine support for a later pattern because other evidence may exist. High-quality observation likewise does not establish a high-confidence pattern.

If numeric pattern confidence is ever added, calibration must be independently proven in a later layer.

## 4.7 User correction operations

L1 must define semantic operations equivalent to:

```text
CONFIRM
REJECT
EDIT_SCOPE
DECLARE_EXCEPTION
CORRECT_OBSERVATION
REQUEST_DELETE
RESET_PERSONALIZATION
```

The future system must conceptually preserve what was believed, what was corrected, when the correction occurred, who/what supplied it, and what observation/pattern assertion it referenced.

Actual persistence mechanics remain deferred.

## 4.8 Deletion and replacement semantics

L1 must distinguish:

```text
HIDE
DEACTIVATE
INVALIDATE
SUPERSEDE
DELETE
RESET PERSONALIZATION
```

`DELETE` means deleted information cannot remain retrievable from active PPF state merely because derived state, cache, or index remains stale. Deletion lineage must be sufficient for future derived state to be invalidated. Physical storage mechanics are not frozen here.

## 4.9 Authority boundary

```text
PPF:
recognize
retrieve
report evidence/uncertainty

MindForge-Mobile:
understand
reason
route

Host / OS / app:
authorize
execute
```

PPF has no action authority.

---

# 5. PPF-L1 proof artifacts and scenario floor

L1 execution, when separately authorized, must produce at least:

1. `ppf-recognize-me-contract.md` defining categories, examples, non-examples, uncertainty, correction, and deletion semantics;
2. **>=30 independently reviewable scenarios**;
3. an ambiguity review demonstrating that expected semantic answers can be classified without knowing an algorithm.

Scenario coverage must include at least:

```text
routine
preference
conditional preference
relationship-conditioned behavior
sequence
context-action association
exception
drift
reversal
correction
deletion
insufficient evidence
conflicting evidence
unknown/unobservable
multi-label context
false correlation
sparse evidence
```

Tiny examples inside this protocol do not count toward the execution scenario set.

---

# 6. PPF-L1 PASS gates

L1 = PASS only if all are independently demonstrated:

```text
L1-G1  semantic categories are algorithm-independent
L1-G2  fact/observation/context/pattern/preference remain distinct
L1-G3  routine semantics require comparable observable opportunities/context
L1-G4  preference requires choice opportunity and meaningful alternatives
L1-G5  multi-label/compositional context is representable
L1-G6  exception semantics are coherent
L1-G7  drift/reversal semantics distinguish behavioral change from coverage change
L1-G8  abstention/uncertainty semantics are first-class
L1-G9  correction semantics preserve provenance and do not require silent overwrite
L1-G10 hide/deactivate/invalidate/supersede/delete/reset remain distinct
L1-G11 context-action semantics make no causal overclaim
L1-G12 authority boundary is explicit and PPF has no action authority
L1-G13 >=30 scenario expectations are independently reviewable
```

If these cannot be defined coherently, PPF must STOP or REVISE before implementation.

---

# 7. PPF-L2 — Personal Event Foundation

## 7.1 Research question

> Can one small, platform-neutral event model faithfully represent the minimum personal evidence required by future PPF experiments across phone, wearable, user-input, and optional health sources without confusing missingness, opportunity, replication, delay, quality, or platform restrictions with behavior?

L2 proves representability only. It does not infer patterns.

## 7.2 Event-foundation principle

PPF must learn from behavioral evidence rather than telemetry artifacts. The event layer must keep separable:

```text
what happened
what was observed or derived
what was observable
what opportunity existed
which source produced evidence
when the phenomenon occurred
when the source produced/recognized the result
when PPF ingested it
what capture policy governed observability
whether evidence is raw or derived
whether another device record is a replica or independent corroboration
what correction/deletion lineage exists
```

---

# 8. L2 minimal conceptual envelope

The frozen requirement is a **tiny event envelope**, not a schema implementation and not an ontology.

It must be capable of supporting conceptually:

```text
event_id
source
event_type
phenomenon_time
result_or_observed_time
ingested_time
payload / context
provenance
observation quality / coverage
observability / opportunity state
```

Where needed it must also support:

```text
source_event_id
correlation key
lineage reference
schema/version reference
```

The exact field names are intentionally deferred to L2 execution review.

## 8.1 Identity and source

Identity must allow one semantic event to be recognized across retransmission or synchronization without requiring a dedup algorithm now.

Source/provenance must be able to identify relevant origin information such as platform, device class, provider/adapter, source record identifier, capture policy reference, and raw/derived status without leaking platform-specific behavior into pattern semantics.

## 8.2 Three-time model

L2 must support three conceptual time layers:

```text
phenomenon_time
= when the underlying behavior/event happened

result_or_observed_time
= when the source produced, recognized, or observed the result

ingested_time
= when PPF received it
```

Example:

```text
08:00 behavior occurs
08:02 watch creates/derives observation
10:00 phone receives synchronized record
```

All three may be equal in simple cases. Arrival order never defines behavioral order. Interval and timezone/canonical-time metadata must be representable when relevant.

These semantics borrow from SOSA/SSN, OGC SensorThings, and OpenTelemetry without adopting those frameworks.

## 8.3 Capture-policy provenance

Evidence provenance must be able to reference why data should or should not have been observable. Relevant capture policies include:

```text
continuous
periodic sample
event-driven
foreground-only
background-enabled
history-window-limited
user-triggered
wearable passive monitoring
batched
```

Conceptual metadata must support:

```text
capture policy
expected observability
history/access window
sampling/duty cycle when relevant
```

Every event need not duplicate full policy metadata; referenceable provenance is sufficient.

## 8.4 Observability and missingness

The model must distinguish at least the semantics of:

```text
OBSERVED_OCCURRENCE
OBSERVABLE_NON_OCCURRENCE
NO_OBSERVATION
SOURCE_UNAVAILABLE
PERMISSION_UNAVAILABLE_OR_UNKNOWN
OUTSIDE_CAPTURE_WINDOW
HISTORY_UNAVAILABLE
DATA_DELAYED
UNKNOWN_OUTCOME
```

Exact enum names are deferred. The invariants are not:

```text
NO_OBSERVATION != OBSERVABLE_NON_OCCURRENCE
NOT_OBSERVED != BEHAVIOR_DID_NOT_OCCUR
```

Missingness mechanisms that must remain distinguishable in evidence provenance include:

```text
missing by design
sensor non-collection
platform restriction
permission limitation
device disconnected
wearable non-wear
sampling gap
sync delay
unknown
```

L2 does not require MCAR/MAR/MNAR statistical modeling.

## 8.5 Opportunity model

Opportunity remains a PPF-specific hard requirement. L2 must support:

```text
OPPORTUNITY
OCCURRENCE
OBSERVABLE_NON_OCCURRENCE
UNKNOWN_OUTCOME
```

Example:

```text
30 commute opportunities
27 observable
3 unknown
18 home
7 other destination
2 observable no-navigation
```

This must remain distinguishable from `18 observed home events` with an unknown denominator. No frequency algorithm is chosen.

## 8.6 Multi-device evidence relationship

L2 must represent at least:

```text
SAME_ORIGIN_REPLICATED
INDEPENDENT_CORROBORATION
UNKNOWN_RELATIONSHIP
```

Example A:

```text
watch workout -> synchronized into HealthKit -> phone reads repository copy
= same-origin replicated evidence unless proven otherwise
```

Example B:

```text
phone geofence + watch motion
= potentially independent corroboration of one behavioral episode
```

No deduplication algorithm is authorized; only relationship representability is required.

## 8.7 Raw observation, derived observation, and pattern

L2 must keep distinct:

```text
RAW OBSERVATION
DERIVED OBSERVATION
PATTERN
```

Example:

```text
accelerometer samples
-> derived walking episode
-> later routine
```

L2 may consume a derived observation without retaining raw high-rate data, but provenance must identify derivation and source/procedure. Pattern conclusions remain outside L2.

## 8.8 Compositional context

Context inside the event foundation must be small, extensible, typed enough to test, and platform-neutral. It may carry multiple simultaneous dimensions and must not require a generic ontology.

## 8.9 User feedback as evidence

Explicit feedback/correction must be representable as provenance-bearing evidence with conceptually:

```text
feedback event
reference target
feedback type
user source
timestamp
lineage
```

This prevents `user correction -> silent database mutation`.

## 8.10 Lineage and invalidation

Borrowing minimally from W3C PROV concepts, L2 must be able to represent relationships equivalent to:

```text
derived_from
supersedes
invalidates
corrects
deletes
```

No graph database, RDF, or provenance engine is implied.

## 8.11 Health/medical boundary

```text
health/fitness: OPTIONAL SOURCE
medical/clinical: OPTIONAL / NOT FOUNDATION DEPENDENCY
```

PPF foundation may recognize personal/wellness context. It must not diagnose, recommend treatment, control medical devices, or convert personal pattern confidence into clinical risk.

---

# 9. L2 fixture specification floor

L2 execution must later define **>=40 fixtures**. This task freezes required families only; no fixtures are created here.

Minimum families:

### Platform acquisition

```text
Android
iOS
Wear OS
Apple Watch/watchOS
user input
optional health source
```

### Time

```text
normal event
delayed event
batched event
out-of-order event
timezone change
DST boundary
```

### Missingness

```text
permission missing
source unavailable
outside history window
sampling gap
wearable disconnected
wearable non-wear
data delayed
unknown reason
```

### Opportunity

```text
occurrence
observable non-occurrence
unknown outcome
partial observability
```

### Multi-device

```text
same-origin replication
independent corroboration
unknown relationship
duplicate source event ID
```

### Context

```text
single context
multi-label context
conflicting context
unknown context
```

### Correction/deletion

```text
user correction
source correction
superseded event
source deletion
user deletion request
reset semantics
```

### Raw/derived

```text
raw observation
derived observation
derived observation with procedure provenance
```

The fixture set must include cross-platform semantic equivalence, capture-policy changes, observation-quality degradation, and false-negative traps caused by missing telemetry.

---

# 10. L2 proof implementation boundary

No schema, fixtures, validator, or executable PPF logic is created by this protocol-freeze task.

During a later explicitly authorized L2 execution, the maximum permitted proof implementation may be a throwaway, platform-neutral representability harness such as:

```text
JSON fixtures
small JSON Schema / dataclass / typed record draft
parser/validator
round-trip serialization test
fixture consistency checks
```

It may exist only to prove the frozen event contract.

Forbidden during L1/L2 proof definition and forbidden now:

```text
database selection
graph DB
vector DB
embedding model
HDC
SLM
neural model
LLM
mobile framework
mobile SDK
event broker
RDF
ontology stack
production synchronization engine
pattern scoring/discovery
agent/tool execution
```

---

# 11. PPF-L2 proof questions

For every future fixture an independent reviewer must be able to answer without knowing a pattern algorithm:

1. What underlying phenomenon happened, if known?
2. What observation/result was produced?
3. When did the phenomenon, result/observation, and ingestion occur?
4. Was the behavior observable under the applicable capture policy?
5. Was there an opportunity?
6. Was a non-occurrence observable or merely missing?
7. What source/device/provider supplied the evidence?
8. What was the observation quality/coverage, and is it clearly distinct from pattern confidence?
9. Is the evidence raw or derived, and is derivation provenance available?
10. Is another device record a replica, independent corroboration, or unknown relationship?
11. Can correction/deletion/supersession lineage be represented?
12. Is context compositional where needed?
13. Does the event remain an observation/evidence item rather than a pattern conclusion?

Any ambiguity caused by the event model is an L2 failure or revision trigger.

---

# 12. PPF-L2 PASS gates

L2 = PASS only if all are independently demonstrated:

```text
L2-G1  one small platform-neutral event model covers >=40 fixtures
L2-G2  event identity/source semantics are unambiguous
L2-G3  phenomenon/result-or-observed/ingestion timing is representable
L2-G4  source and derivation provenance are preserved
L2-G5  capture policy, expected coverage, and history/sampling limits are representable
L2-G6  observability/missingness state is explicit
L2-G7  opportunity semantics are explicit
L2-G8  observable non-occurrence remains distinct from missing/no observation
L2-G9  delayed/batched/out-of-order events remain semantically correct
L2-G10 same-origin replication, independent corroboration, and unknown relationship are representable
L2-G11 raw and derived observations are distinguishable
L2-G12 user feedback/correction is provenance-bearing evidence
L2-G13 correction/delete/supersession lineage is representable
L2-G14 context is compositional and platform-neutral
L2-G15 health/medical evidence is optional and does not expand clinical scope
L2-G16 no pattern conclusion leaks into the event layer
L2-G17 no mobile/platform SDK dependency exists in the foundation model
L2-G18 an independent reviewer classifies all fixtures consistently
```

---

# 13. Required falsification families

Future L1/L2 execution must include cases that could make a naive system falsely claim recognition:

```text
sparse coincidence
confounder/context split
Simpson-like aggregate effect
rare exception
missing telemetry
permission unavailable/unknown
sampling-by-design gap
unexpected sensor non-collection
wearable non-wear/disconnection
delayed batch
out-of-order delivery
same-origin cross-device replica
source-quality degradation
apparent drift caused by coverage change
user correction conflicting with passive evidence
source correction/deletion
```

These requirements freeze falsification coverage only. They do not authorize execution in this task.

---

# 14. PPF-L1/L2 PRE-IMPLEMENTATION GATE

Implementation remains blocked until all of the following are independently demonstrated:

```text
semantic contract coherent
opportunity semantics coherent
missingness semantics coherent
time semantics coherent
provenance coherent
multi-device semantics coherent
correction/deletion lineage coherent
scenario review PASS
fixture review PASS
no algorithm leakage
no platform dependency
```

Only after both L1 and L2 PASS may a later, separately authorized task begin:

```text
L3 — Ground-Truth Personal Pattern Benchmark design
```

Passing this gate does **not** automatically authorize pattern implementation.

---

# 15. STOP / REVISE conditions

PPF must STOP or REVISE before implementation if any of these occur:

```text
S1 “recognize me” cannot be defined independently of algorithm
S2 core event semantics require platform-specific behavior
S3 missing telemetry cannot be distinguished from behavioral negative evidence
S4 opportunity denominator cannot be represented coherently
S5 observation quality and pattern confidence cannot be kept distinct
S6 correction/delete semantics require hidden destructive overwrite
S7 multi-device replication inflates evidence by construction
S8 three-time semantics cannot represent delayed/derived/synchronized records
S9 context requires a fixed global ontology to be testable
S10 benchmark ground truth cannot later be expressed using the L2 event model
```

A STOP or REVISE outcome is valid research evidence.

---

# 16. Status after Protocol v2 freeze

```text
PPF-L1/L2 Protocol v2:
FROZEN / READY FOR EXECUTION REVIEW

PPF-L1:
NOT EXECUTED

PPF-L2:
NOT EXECUTED

PPF-L3:
BLOCKED

PPF-L4:
BLOCKED

PPF-L5:
BLOCKED

Legacy PIS:
HISTORICAL ONLY / OUTSIDE EXECUTION PATH

PPF implementation:
NOT AUTHORIZED

MindForge-Mobile integration:
NOT AUTHORIZED
```

The next authorized action after external review is **PPF-L1 semantic proof only**. Do not execute L1 until that review authorizes it. L2 execution remains separately gated.
