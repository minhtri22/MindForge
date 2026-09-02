# PPF-L1/L2 Research Synthesis — Frozen Inputs Before Protocol v2

Status: **FROZEN RESEARCH SYNTHESIS / PROTOCOL V2 NOT YET APPLIED**

Date: 2026-09-03

Scope: canonical synthesis of the two research passes completed before revising `ppf-l1-l2-foundation-protocol.md` to v2.

This document deliberately does **not** modify the protocol and does **not** authorize implementation. Its purpose is to preserve the evidence and exact revision inputs so that Protocol v2 can be traced back to research rather than design preference.

Depends on:

- `docs/research/ppf-device-platform-research.md`
- `docs/research/ppf-l1-l2-related-work-research.md`
- `docs/research/ppf-l1-l2-foundation-protocol.md` (current pre-v2 protocol)

Track:

```text
Track B — Personal Pattern Foundation (PPF)
```

Legacy PIS remains outside the PPF execution path.

---

## 1. Why this synthesis exists

PPF follows an evidence-gated rule:

> Architecture follows evidence; evidence does not follow architecture.

Before executing L1/L2, two independent research passes were completed:

1. **device/platform research** — Android, iOS, Wear OS, Apple Watch/watchOS, accessories, Health Connect, HealthKit, medical boundaries;
2. **related-work research** — academic papers, public datasets, event/provenance standards, and open-source sensing/personal-informatics systems.

The research substantially supports the feasibility premise of PPF, but it also shows that the current L1/L2 protocol should absorb several semantics before execution.

The correct sequence is therefore:

```text
research
→ freeze findings
→ revise protocol once
→ review/freeze Protocol v2
→ execute L1/L2 proofs
→ only then consider L3
```

---

# 2. Feasibility conclusions already supported by research

## 2.1 Longitudinal personal-device traces can expose recurring structure

Prior work such as Reality Mining, StudentLife, ExtraSensory, mobility-motif research, and personal sensing shows that smartphones and wearables can expose recurring routines, social/contextual structure, significant places, temporal behavior, and longitudinal change.

This supports PPF-L1 categories such as:

```text
routine
relationship-conditioned behavior
temporal sequence
context-action association
exception/change/drift
```

It does **not** justify treating recurrence as preference, causality, or truth without explicit evidence semantics.

Primary references:

- Eagle & Pentland, *Reality Mining: Sensing Complex Social Systems*, 2006. DOI: 10.1007/s00779-005-0046-3
- Reality Mining dataset: https://realitycommons.media.mit.edu/realitymining.html
- StudentLife: https://www.cs.dartmouth.edu/~xia/publication/ubicomp14-studentlife/
- ExtraSensory: https://extrasensory.ucsd.edu/
- Schneider et al., *Unravelling daily human mobility motifs*, 2013. DOI: 10.1098/rsif.2013.0246
- Mohr et al., *Personal Sensing*, 2017. DOI: 10.1146/annurev-clinpsy-032816-044949

Research status:

```text
L1 feasibility premise: SUPPORTED
```

---

## 2.2 Device observability is inherently partial

Android and Apple platforms expose useful signals, but access is constrained by permissions, entitlement, background execution, history windows, sensor availability, device state, synchronization behavior, and user choice.

Therefore the following equation is invalid:

```text
no event observed == event did not happen
```

This is not an edge case; missingness research in digital phenotyping shows that OS behavior, sampling design, device state, sensor non-collection, non-wear, user behavior, and technical disruption all create missing data.

Primary references:

- Android background restrictions: https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions
- Apple HealthKit privacy: https://developer.apple.com/documentation/healthkit/protecting_user_privacy
- Kiang et al., *Sociodemographic characteristics of missing data in digital phenotyping*, 2021. DOI: 10.1038/s41598-021-94516-7
- Currey et al., *Increasing the value of digital phenotyping through reducing missingness*, 2023: https://pmc.ncbi.nlm.nih.gov/articles/PMC10231441/
- JMIR 2026 digital phenotyping scoping review: https://www.jmir.org/2026/1/e84146

Research status:

```text
L2 missingness/observability premise: STRONGLY SUPPORTED
```

---

## 2.3 Wearables increase evidence density but must remain optional

Wear OS Health Services, Apple Watch/HealthKit, BLE accessories and other wearable sources can enrich context, but delivery can be batched, delayed or interrupted. Wearable absence/non-wear/disconnection must not become negative behavior.

PPF foundation must remain valid with phone-only sources.

Primary references:

- Wear OS Health Services: https://developer.android.com/health-and-fitness/health-services
- Wear OS compatibility/delivery behavior: https://developer.android.com/health-and-fitness/health-services/compatibility
- Wear OS Data Layer: https://developer.android.com/training/wearables/data/sync
- Apple HealthKit: https://developer.apple.com/documentation/healthkit

Research status:

```text
wearable evidence: OPTIONAL ENRICHMENT
foundation dependency: NO
```

---

## 2.4 Health/medical data must not define the foundation

Health Connect and HealthKit can provide useful personal context and increasingly support clinical/FHIR records, but medical/clinical information creates stronger permission, provenance, privacy and regulatory constraints.

PPF foundation remains in personal-pattern/general-wellness territory and must not depend on clinical data.

Primary references:

- Android Health Connect: https://developer.android.com/health-and-fitness/health-connect
- Health Connect Medical Records: https://developer.android.com/health-and-fitness/health-connect/medical-records
- Apple health records: https://developer.apple.com/documentation/healthkit/accessing-health-records
- FDA General Wellness guidance: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices

Research status:

```text
health/fitness: OPTIONAL SOURCE
clinical/medical: OPTIONAL / OUTSIDE FOUNDATION REQUIREMENT
diagnosis/treatment: OUT OF SCOPE
```

---

# 3. Prior work that constrains L1 semantics

## 3.1 Context is compositional, not necessarily one label

ExtraSensory demonstrates ordinary-life contexts where multiple labels coexist.

PPF consequence:

```text
context must support multiple simultaneous dimensions
```

Examples:

```text
location + activity + social context + device state
```

Protocol v2 should ensure L1 scenarios include overlapping/multi-label contexts.

---

## 3.2 Pattern is not preference

Prior sensing literature can expose recurrence, mobility structure and behavioral markers, but recurrence alone does not establish that a person prefers an option.

PPF consequence:

A `preference` requires meaningful alternatives/opportunities, not merely frequent occurrence.

Protocol v2 must preserve a hard semantic distinction:

```text
OCCURRENCE != PREFERENCE
```

---

## 3.3 User correction belongs in the personal truth contract

Personal Informatics and interactive-learning literature support preserving user control, correction and iterative reflection. Interactive activity-recognition studies show user correction can materially improve recognition.

Primary references:

- Li, Dey & Forlizzi, *A Stage-Based Model of Personal Informatics Systems*, CHI 2010. DOI: 10.1145/1753326.1753409
- Tegen et al., *Activity recognition through interactive machine learning in a dynamic sensor setting*. DOI: 10.1007/s00779-020-01414-2
- Zhang, *Personal Context Recognition via Skeptical Learning*, IJCAI 2019: https://www.ijcai.org/proceedings/2019/930

PPF consequence:

User correction must be a provenance-bearing event/evidence item, not a silent database overwrite.

---

## 3.4 Numeric confidence must not be admitted without calibration evidence

Confidence-calibration work in human activity recognition shows that high predictive accuracy can coexist with overconfident probabilities.

Primary reference:

- Roy et al., *Confidence-Calibrated Human Activity Recognition*, Sensors 2021. DOI: 10.3390/s21196566

PPF consequence:

L1 must require semantic states such as:

```text
SUPPORTED
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
STALE
NOT_OBSERVABLE
USER_REJECTED
```

A numeric confidence field may be introduced only in a later layer if calibration is independently demonstrated.

---

# 4. Mature event semantics PPF should borrow rather than reinvent

PPF-L2 does not need to invent generic observation/event semantics from scratch.

## 4.1 SOSA/SSN

Useful concepts:

```text
Observation
Sensor / Platform
FeatureOfInterest
observed property
result
phenomenonTime
resultTime
result quality
```

Source:

- W3C/OGC SOSA/SSN: https://www.w3.org/TR/vocab-ssn-2023/

PPF adoption rule:

```text
BORROW SEMANTICS
DO NOT IMPORT RDF/OWL STACK
```

---

## 4.2 OGC SensorThings

Useful concepts:

```text
phenomenonTime
resultTime
result
resultQuality
validTime
parameters
```

Source:

- OGC SensorThings API Part 1: https://docs.ogc.org/is/18-088/18-088.html

PPF implication:

Observation quality should remain separate from the behavioral payload and separate from any later pattern confidence.

---

## 4.3 OpenTelemetry Events

Useful distinction:

```text
Timestamp
= when event occurred

ObservedTimestamp
= when collector observed/received it
```

Source:

- OpenTelemetry event semantic conventions: https://opentelemetry.io/docs/specs/semconv/general/events/

PPF implication:

Current two-time semantics should be expanded conceptually to allow:

```text
phenomenon_time
result_or_observed_at
ingested_at
```

Not every source must populate all three independently, but the model must be able to represent the distinction.

---

## 4.4 CloudEvents

Useful minimal envelope concepts:

```text
id
source
type
time
data
```

`source + id` also provides a useful duplicate/retransmission identity pattern.

Source:

- CloudEvents specification: https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md

PPF adoption rule:

Borrow a small event envelope; do not introduce event brokers or cloud infrastructure.

---

## 4.5 W3C PROV

Useful concepts:

```text
entity
activity
agent
generation
invalidation
provenance lineage
```

Source:

- W3C PROV: https://www.w3.org/TR/prov-overview/

PPF implication:

Correction/deletion/supersession should preserve enough lineage to explain why derived personal state changed.

---

# 5. Open-source systems worth learning from, not depending on

## AWARE

Learn:

- sensor adapters;
- real-world permissions/background constraints;
- mobile acquisition experience.

Do not adopt:

- plugin/server/framework architecture.

Source:

- https://github.com/awareframework/aware-client

## Beiwe

Learn:

- longitudinal mobile sensing;
- realistic Android/iOS collection constraints;
- research-oriented provenance/collection design.

Source:

- https://github.com/onnela-lab

## mindLAMP

Learn:

- longitudinal sensing;
- operational missingness lessons.

Do not make clinical architecture part of PPF core.

Source:

- https://github.com/BIDMCDigitalPsychiatry/LAMP-platform

## RAPIDS

Learn:

- raw → feature separation;
- reproducible transformation;
- sensor preprocessing provenance.

Do not adopt the workflow stack into PPF foundation.

Source:

- https://github.com/carissalow/rapids

## ActivityWatch

Learn:

- how little event structure can still support useful personal activity tracking.

Reference event shape is intentionally tiny (`timestamp`, `duration`, `data`), which is useful as a lower bound but insufficient for PPF observability/opportunity/provenance requirements.

Source:

- https://github.com/ActivityWatch/activitywatch

## Open mHealth

Learn:

- schema-first design;
- test data;
- validator approach;
- bounded domain schemas.

Do not make health ontology a PPF foundation dependency.

Source:

- https://github.com/openmhealth/schemas

---

# 6. Frozen revision inputs for PPF-L1/L2 Protocol v2

The following seven changes are now evidence-backed revision requirements.

## R1 — Observation quality / coverage becomes first-class

Protocol v2 must represent source/observation quality or coverage independently from event payload.

Reason:

- SensorThings result-quality semantics;
- digital-phenotyping missingness literature;
- mobile/wearable operational constraints.

Must not become pattern confidence.

---

## R2 — Expand time semantics to three conceptual times

Protocol v2 must support:

```text
phenomenon_time
result_or_observed_at
ingested_at
```

Reason:

- SOSA/SSN;
- SensorThings;
- OpenTelemetry;
- wearable batching/synchronization.

Arrival order must never define behavioral order.

---

## R3 — Capture policy / expected observability becomes provenance

Where applicable the event/source contract must be able to carry enough information to distinguish:

```text
continuous expected observation
scheduled/duty-cycle sampling
history-window limitation
foreground-only capability
background capability unavailable
source temporarily unavailable
```

Reason:

Missingness by design and unexpected non-collection have different semantics.

---

## R4 — Context must support multi-label/compositional representation

Protocol v2 fixtures must include contexts where multiple dimensions coexist.

Reason:

ExtraSensory and context-aware computing literature.

PPF must not force all context into one mutually exclusive category.

---

## R5 — Observation quality and pattern confidence must be distinct

Protocol v2 must prohibit a generic `confidence` field from ambiguously mixing:

```text
sensor/observation quality
pattern support
prediction confidence
calibrated probability
```

Numeric pattern confidence is not required for L1/L2 and must earn admission later through calibration evidence.

---

## R6 — User feedback/correction is a provenance-bearing event

Protocol v2 must model user correction as explicit evidence with:

```text
actor/source
reference to target observation/pattern assertion
occurred time
lineage/supersession semantics
```

It must not silently mutate historical evidence.

---

## R7 — Keep the event envelope tiny; borrow standards semantics, not their frameworks

Protocol v2 should aim for:

```text
JSON fixtures
small schema/dataclass
validator
round-trip tests
```

It must explicitly reject foundation dependencies on:

```text
RDF/OWL
OGC server stack
CloudEvents broker
OpenTelemetry collector
vector DB
graph DB
LLM
HDC
SLM
mobile SDK
server infrastructure
```

unless a later evidence gate proves one is necessary.

---

# 7. Additional fixture requirements before L2 execution

The pre-v2 protocol currently sets a 27+ fixture floor. Research now justifies expanding the execution target to **40+ fixtures** so that failure-prone acquisition semantics are covered before any pattern algorithm exists.

Additional fixture families required in Protocol v2:

```text
sampling-by-design gap
unexpected sensor non-collection
wearable non-wear
source quality degradation
phenomenon/result/ingestion time divergence
derived synchronized record vs independent corroboration
platform capability/permission state change
explicit user correction lineage
multi-label context
DST/timezone transition
history-window truncation
stale sync / delayed delivery
observation-quality ambiguity
```

The increased fixture count is not product scope. It is cheaper falsification before implementation.

---

# 8. Opportunity remains a PPF-specific proof requirement

The related standards provide mature event/observation semantics but do not solve PPF's personal opportunity denominator.

PPF must still prove a distinction such as:

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
3 unknown/unobservable
18 home
7 other destination
2 observable non-occurrence
```

This must not collapse into naive `18 / 30` frequency.

Opportunity semantics therefore remain one of the central original proof obligations of PPF-L2.

---

# 9. Multi-device evidence relationship remains a PPF-specific proof requirement

Generic duplicate event identity is not enough.

PPF must be able to represent at least:

```text
SAME_ORIGIN_REPLICA
INDEPENDENT_CORROBORATION
RELATIONSHIP_UNKNOWN
```

Example:

```text
watch workout
→ synchronized HealthKit record
→ phone observes repository copy
```

must not automatically count as multiple independent behavioral occurrences.

---

# 10. What is now considered supported vs still unproven

Supported enough to proceed to protocol revision:

```text
personal-device signals can expose longitudinal recurring structure
context can be represented as compositional/multi-label
missingness/observability must be first-class
event time and processing/ingestion time must be separable
source provenance and quality matter
user correction/control is legitimate foundation semantics
minimal standards-inspired event envelopes are feasible
```

Still unproven and must not be implemented yet:

```text
which patterns can be reliably recognized
how many observations are sufficient
which opportunity semantics are adequate
which confidence model is valid
how patterns should be discovered
whether counts/decay are sufficient
whether embeddings/neural/HDC mechanisms add value
how retrieval should be implemented
whether mobile live telemetry is necessary
how Track A and PPF should integrate
```

---

# 11. Gate status after research synthesis

```text
Device/platform research:       COMPLETE
Paper/OSS/standards research:   COMPLETE
Research synthesis:             FROZEN

PPF-L1 feasibility premise:     SUPPORTED
PPF-L2 feasibility premise:     SUPPORTED

PPF-L1/L2 Protocol v1:          SUPERSEDED ONLY AFTER v2 IS REVIEWED
PPF-L1/L2 Protocol v2:          NOT YET WRITTEN

L1 execution:                   NOT STARTED
L2 execution:                   NOT STARTED
L3:                             BLOCKED
L4:                             BLOCKED
L5:                             BLOCKED

Pattern implementation:         NOT AUTHORIZED
Mobile SDK integration:         NOT AUTHORIZED
MindForge-Mobile integration:   NOT AUTHORIZED
```

---

# 12. Next authorized action

The only next authorized action is:

> Revise `ppf-l1-l2-foundation-protocol.md` into Protocol v2 using the frozen research inputs R1–R7 above, expand the L2 falsification fixture plan to 40+, then review/freeze the protocol before executing any L1/L2 proof.

No pattern implementation is authorized by this document.
