# PPF-L1/L2 Foundation Protocol

Status: **FROZEN DRAFT FOR REVIEW / IMPLEMENTATION NOT AUTHORIZED**

Date: 2026-09-03

Depends on:

- `docs/research/personal-intelligence-two-track.md`
- `docs/research/ppf-device-platform-research.md`

Track:

```text
Track B — Personal Pattern Foundation (PPF)
```

Mission:

> Prove, from first principles, the minimum foundation required for a local system to reliably recognize one person over time.

This protocol covers only:

```text
PPF-L1 — Define “Recognize Me”
PPF-L2 — Personal Event Foundation
```

It does **not** authorize a pattern engine, PIS port, HDC, SLM, graph, embeddings, LLM-based pattern discovery, mobile application, wearable integration, or MindForge-Mobile integration.

---

# 1. Research ladder

PPF is intentionally staged:

```text
L1 — Define “Recognize Me”
L2 — Personal Event Foundation
L3 — Ground-Truth Personal Pattern Benchmark
L4 — Minimal Baselines
L5 — Minimum Missing Mechanism
        ↓
Feasibility decision
        ↓
Only then compose proven layers
```

Each layer must earn the right to exist.

A later layer must not retroactively redefine an earlier layer merely to make an implementation succeed.

Core rule:

> **Architecture follows evidence; evidence does not follow architecture.**

---

# 2. Why L1/L2 must precede implementation

The device-platform survey establishes several facts:

1. personal signals exist across Android, iOS and wearables;
2. access is incomplete and permission-dependent;
3. event delivery may be delayed, batched or unavailable;
4. different devices may observe the same underlying behavior;
5. health data may be deliberately indistinguishable from absent data when permission is denied;
6. wearable/device connectivity may disappear temporarily;
7. platform capability differs significantly;
8. missing observation is therefore not equivalent to negative behavioral evidence.

If PPF starts by implementing a pattern algorithm before solving these semantics, the benchmark can produce scientifically invalid conclusions.

Therefore L1/L2 are **semantic and evidence-foundation proofs**, not application engineering milestones.

---

# 3. PPF-L1 — Define “Recognize Me”

## 3.1 Research question

> What observable outputs are necessary and sufficient for a system to demonstrate that it recognizes a person’s recurring behavior, preferences, context dependencies, exceptions and changes over time?

The answer must not depend on a specific algorithm.

---

## 3.2 L1 non-goals

L1 does not decide:

- how a pattern is discovered;
- how confidence is calculated;
- which database is used;
- whether vectors/embeddings exist;
- whether HDC exists;
- whether a neural model exists;
- how mobile permissions are implemented;
- how apps are invoked;
- whether actions are autonomous.

L1 specifies the **semantic output contract only**.

---

## 3.3 Minimum pattern semantics to define

L1 must define operational semantics for at least:

### Routine

A recurring behavior under identifiable opportunities/context.

Example:

```text
weekday + leaving work
→ usually navigates home
```

### Preference

A repeated choice among meaningful alternatives, not merely frequent occurrence.

Example:

```text
when dining with spouse
→ Japanese is chosen disproportionately often
```

### Relationship-conditioned behavior

Behavior changes based on person/entity context.

### Temporal sequence

A recurring ordered chain where temporal order matters.

### Context → action association

A behavior associated with a context, without claiming causality.

### Exception

A meaningful conditional deviation from a broader pattern.

### Change / drift

A prior pattern weakens, reverses, or is replaced over time.

### Explicit user correction

A user-provided correction that can invalidate or modify an inferred pattern.

---

## 3.4 Required distinction: fact vs pattern

L1 must distinguish:

```text
FACT
PATTERN
PREFERENCE
EXCEPTION
CURRENT CONTEXT
```

Example:

```text
Fact:
Person X is spouse.

Pattern:
After work, user often messages Person X.

Preference:
With Person X, user often chooses Japanese food.

Exception:
With children present, user usually chooses another category.
```

PPF must not become a generic personal-memory bucket.

---

## 3.5 Required output semantics

A future pattern result must be able to expose conceptually:

```text
pattern identity
pattern type
scope/context
supporting evidence summary
counterevidence summary
opportunity denominator
confidence/calibration value if later justified
exceptions
freshness/last evidence
status: candidate/admitted/stale/corrected/deleted/etc.
provenance reference
```

This is a semantic requirement, not a frozen JSON schema.

---

## 3.6 Required abstention semantics

“Recognize me” includes knowing when not to claim recognition.

L1 must define states equivalent to:

```text
SUPPORTED
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
STALE
UNKNOWN_CONTEXT
NOT_OBSERVABLE
USER_REJECTED
```

A system that always returns a pattern fails L1 by definition.

---

## 3.7 Required correction semantics

L1 must define how explicit user feedback affects semantic truth.

At minimum:

```text
user confirms pattern
user rejects pattern
user edits scope/context
user marks exception
user requests forgetting/deletion
```

No algorithm is chosen yet, but the semantic outcome must be unambiguous.

---

## 3.8 Required deletion semantics

L1 must distinguish:

```text
HIDE
DEACTIVATE
INVALIDATE
DELETE
RESET PERSONALIZATION
```

`DELETE` must mean that the pattern cannot continue to be returned from active PPF state merely because stale derived state/index/cache remains.

Actual storage mechanics belong to implementation later.

---

## 3.9 Required authority boundary

PPF semantics stop at recognition.

```text
PPF:
recognize / retrieve / explain uncertainty

MindForge-Mobile:
understand / reason / decide / route

Host / OS / app:
authorize and execute
```

PPF cannot autonomously perform device/app actions.

---

# 4. PPF-L1 proof artifacts

Before L1 PASS, produce:

### A. `recognize-me-contract.md`

Defines every semantic category above with examples and non-examples.

### B. scenario set

At least 30 hand-authored examples spanning:

- routine;
- preference;
- conditional preference;
- relationship-conditioned behavior;
- temporal sequence;
- exception;
- drift;
- reversal;
- correction;
- deletion;
- insufficient evidence;
- conflicting evidence.

Each scenario must specify the expected semantic answer independently of implementation.

### C. ambiguity review

A reviewer must be able to answer each scenario without needing to know which algorithm PPF will later use.

---

# 5. PPF-L1 PASS gates

L1 = PASS only if all are true:

```text
L1-G1 semantic categories defined without algorithm leakage
L1-G2 fact vs pattern distinction unambiguous
L1-G3 occurrence vs preference distinction explicit
L1-G4 exception semantics defined
L1-G5 drift/reversal semantics defined
L1-G6 insufficient-evidence/abstention semantics defined
L1-G7 user correction semantics defined
L1-G8 delete/reset semantics defined
L1-G9 authority boundary explicit
L1-G10 >=30 scenario expectations independently reviewable
```

If these cannot be defined coherently, PPF should STOP before implementation.

---

# 6. PPF-L2 — Personal Event Foundation

## 6.1 Research question

> Can one small, platform-neutral event model faithfully represent the minimum personal observations needed by future PPF experiments across phone, wearable and optional health sources without confusing missingness, opportunity, duplication, delay or permission gaps with behavior?

This is the most important pre-implementation proof.

---

## 6.2 L2 design principle

PPF must learn from **behavioral evidence**, not telemetry artifacts.

Therefore the model must separate:

```text
what happened
what was observable
what opportunity existed
what source reported it
when it happened
when it was received
whether another device reported the same thing
```

---

# 7. L2 minimum event concepts

## 7.1 Event identity

Each observation must support:

```text
event_id
source_event_id (optional)
correlation/dedup key (optional)
```

Requirement:

Two devices observing one underlying event must not automatically become two units of evidence.

---

## 7.2 Time model

Must represent separately:

```text
occurred_at
ingested_at
interval_start / interval_end where relevant
timezone or canonical time basis
```

Required because wearable/health signals may arrive batched or delayed.

Arrival order must not define behavioral order.

---

## 7.3 Source/provenance model

At minimum:

```text
platform
source device class
source adapter/type
source provider/app where relevant
source record identifier when available
raw vs derived
```

Example device classes:

```text
PHONE
WATCH
WEARABLE
ACCESSORY
HEALTH_REPOSITORY
CALENDAR_PROVIDER
APP_USAGE_PROVIDER
USER_INPUT
```

These are examples, not final enum requirements.

---

## 7.4 Observability model

L2 must distinguish at least:

```text
SOURCE_AVAILABLE
SOURCE_UNAVAILABLE
PERMISSION_GRANTED
PERMISSION_DENIED when knowable
PERMISSION_UNKNOWN
HISTORY_LIMITED
BACKGROUND_UNAVAILABLE
DATA_DELAYED
NOT_OBSERVABLE
```

The exact schema may differ, but semantic distinction is mandatory.

Important:

On platforms such as HealthKit, denial may deliberately be indistinguishable from no data. Therefore `PERMISSION_UNKNOWN / NOT_OBSERVABLE` must be possible.

---

## 7.5 Opportunity model

This is a hard requirement.

PPF must distinguish:

```text
OPPORTUNITY
OCCURRENCE
OBSERVABLE_NON_OCCURRENCE
UNKNOWN_OUTCOME
```

Example:

```text
Opportunity:
workday ended and commute context became available

Occurrence:
user navigated home

Observable non-occurrence:
full observation available and user selected another route/destination

Unknown outcome:
phone/watch source unavailable during the opportunity window
```

A missing event must never be silently counted as a non-occurrence.

---

## 7.6 Behavioral semantics

The event foundation must be able to represent minimally:

```text
actor/person
context
behavior/action
object/target
outcome/result
explicit vs observed
authorized user correction
```

The foundation should avoid encoding pattern conclusions into raw observations.

Bad:

```text
user_prefers_japanese = true
```

Good observation:

```text
context: dinner_with_person_X
choice_set: [Japanese, Vietnamese, Korean]
selected: Japanese
```

Pattern interpretation belongs later.

---

## 7.7 Missingness semantics

L2 must explicitly prove the difference among:

```text
NO EVENT
NO OBSERVATION
NO PERMISSION
SOURCE DISCONNECTED
DATA NOT YET ARRIVED
HISTORY OUTSIDE ACCESS WINDOW
OBSERVABLE NON-OCCURRENCE
```

If the schema collapses any of these in a way that biases future learning, L2 fails.

---

## 7.8 Multi-device deduplication semantics

Scenario:

```text
Apple Watch records workout
HealthKit syncs workout to iPhone
phone-side adapter observes HealthKit record
```

These may represent one underlying behavior, not multiple independent confirmations.

L2 must define a way to represent:

```text
same-origin replicated evidence
independent corroborating evidence
unknown relationship
```

No dedup algorithm is required yet; representability is required.

---

## 7.9 Correction and deletion lineage

An event may later be:

```text
corrected
superseded
deleted by source
removed by user request
```

L2 must represent lineage so future derived patterns can be invalidated/recomputed.

---

# 8. L2 platform-neutral fixture set

Before implementation, create a fixture specification covering at least:

### Android fixtures

1. app usage event with usage permission;
2. app usage unknown because permission unavailable;
3. calendar meeting end as opportunity;
4. geofence enter/leave context;
5. notification signal with content minimized;
6. delayed background ingestion.

### iOS fixtures

7. calendar full-access event;
8. calendar write-only state that cannot observe history;
9. geofence event;
10. app-usage data available through entitlement/authorization;
11. health data absent but read authorization unknowable;
12. limited health-history window.

### Wearable fixtures

13. Wear OS passive event;
14. Wear OS batched delivery;
15. watch-phone duplicate observation;
16. disconnected wearable / unknown outcome;
17. Apple Watch workout record later synchronized to phone.

### User/semantic fixtures

18. explicit user preference statement;
19. user correction of an old observation;
20. user deletion request;
21. source record deletion;
22. timezone change;
23. duplicated event IDs;
24. out-of-order arrival.

### Optional medical fixtures

25. permissioned health measurement as context only;
26. clinical record source unavailable/permission absent;
27. medical context explicitly excluded from diagnostic interpretation.

Minimum fixture count: **27**.

Fixtures must contain no PPF pattern algorithm.

---

# 9. L2 proof implementation boundary

A small **throwaway validator/schema prototype** is allowed only if necessary to prove representability.

Allowed:

```text
JSON fixtures
JSON Schema / dataclass / typed record draft
parser/validator
round-trip serialization test
fixture consistency checks
```

Not allowed:

```text
pattern scoring
confidence learning
HDC
SLM
embedding generation
vector retrieval
graph database
LLM inference
mobile SDK integration
live telemetry collection
agent/tool execution
```

The purpose is proof of the event contract, not production code.

---

# 10. PPF-L2 proof questions

For every fixture, reviewer must be able to answer:

1. What actually happened?
2. Was the behavior observable?
3. Was there an opportunity?
4. Was a non-occurrence observable or merely missing?
5. Which device/provider supplied evidence?
6. Is the event raw or derived?
7. Did it arrive late?
8. Could it duplicate another event?
9. Can it later be corrected/deleted?
10. Does the event encode only observation, not a pattern conclusion?

If any answer is ambiguous because of schema limitations, L2 is not PASS.

---

# 11. L2 PASS gates

L2 = PASS only if all are true:

```text
L2-G1 one platform-neutral event model covers all 27+ fixtures
L2-G2 occurrence time and ingestion time are separate
L2-G3 source provenance is preserved
L2-G4 observability state is explicit
L2-G5 opportunity semantics are explicit
L2-G6 observable non-occurrence != missing observation
L2-G7 unknown/unobservable is representable
L2-G8 delayed/batched events remain semantically correct
L2-G9 multi-device duplicate/correlation semantics are representable
L2-G10 correction/deletion lineage is representable
L2-G11 explicit user input is distinguishable from passive observation
L2-G12 no pattern conclusion leaks into raw event schema
L2-G13 health/medical sources are optional, not foundation dependencies
L2-G14 no mobile/platform SDK dependency exists in foundation model
L2-G15 independent reviewer can classify all fixtures consistently
```

---

# 12. Scientific falsification cases required before L2 PASS

The fixture review must explicitly test failure-prone scenarios.

## Falsification A — Missing permission

```text
Expected:
UNKNOWN / NOT OBSERVABLE

Forbidden interpretation:
behavior did not occur
```

## Falsification B — Wearable disconnected

```text
Expected:
source unavailable

Forbidden interpretation:
no activity
```

## Falsification C — Delayed batch

```text
Occurred: 08:00
Ingested: 10:00

Expected behavior time: 08:00
```

## Falsification D — Duplicate cross-device record

```text
watch observation + phone synchronized copy
```

Must not imply two independent occurrences.

## Falsification E — Opportunity denominator

```text
10 observed choices / 30 opportunities
```

must differ from:

```text
10 observed choices / 10 opportunities
```

## Falsification F — Explicit correction

User correction must be representable as higher-authority evidence metadata without mutating historical raw facts invisibly.

## Falsification G — Delete lineage

Deleted/superseded observations must be traceable so later pattern evidence can be invalidated.

---

# 13. What must be proven before any PPF pattern implementation

Implementation of L3/L4 pattern experiments is forbidden until all of the following are established:

```text
P1 “recognize me” semantic contract is frozen
P2 fact/pattern/preference/exception semantics are distinct
P3 abstention/insufficient evidence is first-class
P4 opportunity denominator is first-class
P5 missingness/observability states are first-class
P6 event time != ingest time
P7 provenance is preserved
P8 multi-device duplication is representable
P9 correction/delete lineage is representable
P10 platform-specific absence cannot masquerade as behavioral evidence
P11 health/medical is optional
P12 action authority remains outside PPF
```

Only then may PPF proceed to:

```text
L3 — Ground-Truth Personal Pattern Benchmark
```

---

# 14. L3 entry criteria

L3 is authorized only after L1 and L2 both PASS.

L3 may then define synthetic/semi-synthetic event histories with hidden ground truth for:

```text
routine formation
coincidence / false correlation
routine drift
preference emergence
preference reversal
conditional preference
rare exception
relationship-conditioned behavior
temporal sequence
context-action association
conflicting evidence
user correction
deletion / forgetting
insufficient evidence / abstention
contextual retrieval
```

No baseline or algorithm should see ground-truth generator rules.

---

# 15. Explicit STOP conditions

PPF foundation should STOP or REVISE before implementation if:

```text
S1 “recognize me” cannot be defined independently of algorithm
S2 event model needs platform-specific semantics in the core
S3 missing telemetry cannot be distinguished from negative evidence
S4 opportunity denominator cannot be represented coherently
S5 correction/delete semantics require hidden irreversible state
S6 multi-device replication systematically inflates evidence
S7 benchmark ground truth cannot be expressed using the L2 event model
```

A STOP is a valid research outcome.

---

# 16. Minimalism constraints

PPF must remain greenfield and small.

Before L3/L4 evidence, do not introduce:

```text
legacy PIS code
HDC
SLM
repair subsystem
complex taxonomy
graph DB
vector DB
embedding model
LLM classifier
agent framework
plugin architecture
production sync engine
mobile SDK adapters
medical logic
```

If a later benchmark exposes a failure, add only the smallest mechanism necessary to test that failure.

---

# 17. Deliverables for the next research execution

The next agent task should produce only:

```text
docs/research/ppf-recognize-me-contract.md
docs/research/ppf-l1-scenarios.md
docs/research/ppf-l2-event-contract.md
docs/research/data/ppf-l2-fixtures.json
(optional) tiny validation schema/tests
```

No production package/module should be added to `mindforge/`.

---

# 18. Final protocol status

```text
PPF-L1:
PROTOCOL DEFINED / EXECUTION NOT YET RUN

PPF-L2:
PROTOCOL DEFINED / EXECUTION NOT YET RUN

PPF-L3:
BLOCKED BY L1/L2

PPF-L4:
BLOCKED

PPF-L5:
BLOCKED

Legacy PIS:
OUTSIDE EXECUTION PATH

MindForge-Mobile integration:
NOT AUTHORIZED

PPF implementation:
NOT AUTHORIZED
```
