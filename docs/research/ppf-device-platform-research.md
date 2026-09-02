# PPF Device Platform Research — Personal Signals, Constraints, and Feasibility

Status: **RESEARCH COMPLETE / INPUT TO PPF-L1/L2**

Date: 2026-09-03

Scope: personal-device signal availability and constraints relevant to **Personal Pattern Foundation (PPF)** across Android, iOS, Wear OS, Apple Watch/watchOS, connected accessories, health/medical data sources, and app/system integration surfaces.

This document does **not** authorize PPF implementation. Its purpose is to establish what can realistically be observed, what cannot safely be assumed, and which abstractions must be proven before implementation.

---

## 1. Research question

PPF is intended to answer a narrow question:

> How little machinery is required to reliably recognize one person over time from personal-device event streams?

The research therefore focuses on whether modern personal devices can provide enough structured evidence for patterns such as:

- routines;
- preferences;
- person-conditioned behavior;
- temporal sequences;
- context -> action associations;
- exceptions;
- change/drift;
- user corrections.

The target is not surveillance and not unrestricted telemetry collection. PPF must operate inside platform permissions, user consent, background-execution limits, source-specific gaps, and privacy boundaries.

---

## 2. Executive findings

### F1 — Feasibility is plausible, but observability is partial by design

Android and Apple platforms expose many useful classes of personal signals, including calendar, contacts, location/geofencing, motion/activity, app usage in constrained forms, health/fitness data, wearable sensor summaries, and app-specific actions. However, access is permissioned, sometimes entitlement-gated, sometimes foreground-only, sometimes delayed/batched, and can disappear when permission or device state changes.

Therefore PPF must never equate:

```text
no event observed == event did not happen
```

Instead, absence must be classified explicitly.

### F2 — `UNKNOWN / NOT OBSERVABLE` is a first-class state

Apple HealthKit intentionally prevents an app from reliably distinguishing denial of read permission from absence of data for a type; Android Health Connect likewise has foreground/background/history permission boundaries and feature availability checks. This means the event foundation must represent observability state, permission state, source capability, and data freshness independently from behavioral evidence.

### F3 — Background collection cannot be the architectural assumption

Both Android and Apple impose background-execution limits for power and privacy. Wearable APIs often batch or reduce sampling when the display/application processor is inactive. PPF must tolerate delayed events, sparse observations, synchronization gaps, device disconnection, and partial histories.

### F4 — Wearables improve evidence density but are optional

Wear OS Health Services and Apple Watch/HealthKit provide higher-value context such as workouts, steps, heart rate, motion and other sensor-derived measurements. These are useful as optional evidence sources, but PPF must remain viable without them.

### F5 — Health/medical data must remain an optional source class

Android Health Connect and Apple HealthKit provide health/fitness repositories and increasingly support FHIR clinical records. These sources can enrich context but create stronger permission, privacy and regulatory boundaries. PPF foundation must not depend on health data, and the first scope should be pattern/wellness context rather than diagnosis, treatment or medical decision-making.

### F6 — Cross-app action surfaces exist, but they belong downstream of PPF

Android AppFunctions exposes app capabilities for trusted/system-privileged agents and cross-app orchestration; Apple App Intents makes app actions/data discoverable to Apple Intelligence, Siri, Shortcuts, Spotlight and other system experiences. These support the longer-term MindForge-Mobile `KNOW & ACT` path, but PPF itself should only produce personal-pattern context, not execute actions.

---

## 3. Platform capability survey

### 3.1 Android — personal/device signals

#### App usage

`UsageStatsManager` provides access to device usage history and statistics and `UsageEvents` exposes component state-change events. Most cross-app usage access requires `PACKAGE_USAGE_STATS`, and the user must grant usage access through Settings; some behavior is unavailable while the device user is locked.

PPF implication:

- useful signal: app/package usage and transitions;
- not universally available;
- must record authorization/capability state;
- must not infer non-use when access is missing.

Sources:

- Android `UsageStatsManager`: https://developer.android.com/reference/android/app/usage/UsageStatsManager
- Android `UsageEvents`: https://developer.android.com/reference/android/app/usage/UsageEvents

#### Notifications

Android `NotificationListenerService` can receive system callbacks when notifications are posted, removed, or ranking changes, but requires a specifically declared listener service and user/system-granted access.

PPF implication:

- notification interactions may be valuable context;
- the source is privileged/sensitive and optional;
- content minimization should be preferred over storing raw notification bodies.

Source:

- https://developer.android.com/reference/android/service/notification/NotificationListenerService.html

#### Calendar and contacts

Android exposes Calendar Provider and Contacts Provider APIs with explicit read/write permissions. Calendar includes events, attendees and reminders; contacts include aggregated person records.

PPF implication:

- calendar events are strong `opportunity/context` signals (e.g. meeting ended, commute opportunity);
- contacts/person identifiers are useful for relationship-conditioned patterns;
- PPF should normalize stable internal entity IDs instead of treating names as durable identity.

Sources:

- Calendar Provider: https://developer.android.com/identity/providers/calendar-provider
- Contacts Provider: https://developer.android.com/identity/providers/contacts-provider

#### Sensors

Android Sensor Framework exposes hardware and software-derived sensors including accelerometer, gyroscope, magnetic field and other device-dependent sensors.

PPF implication:

- raw sensors are too high-volume for the foundation by default;
- prefer derived events/context (walking, stationary, device state) rather than raw streams unless a benchmark later proves raw data necessary.

Source:

- https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview

#### Background limits

Android explicitly restricts background work because background processes consume memory and battery. Excessive wake locks/background behavior can trigger user/system restrictions.

PPF implication:

- event acquisition must not require continuous always-on application execution;
- architecture should support OS-scheduled, batched, event-driven and catch-up ingestion.

Source:

- https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions

---

### 3.2 Android Health Connect — fitness and medical context

Health Connect is a central Android health/fitness data exchange layer with standard CRUD and synchronization capabilities. It supports Android 9 / SDK 28+ through its compatibility path and exposes many health and fitness record types.

Reading in the background and reading history older than the default window require additional permissions and feature availability. Documentation explicitly recommends checking feature availability because users may not have the same Health Connect version.

Sources:

- Health Connect overview: https://developer.android.com/health-and-fitness/health-connect
- Data types and additional permissions: https://developer.android.com/health-and-fitness/health-connect/data-types
- Synchronization/background reads: https://developer.android.com/health-and-fitness/health-connect/sync-data

#### Medical Records

Health Connect Medical Records extends Health Connect with FHIR-based medical data. As of this research date, the Medical Records API is still marked experimental and some capabilities/policies are still under development. FHIR R4/R4B resources are mapped into medical resource categories with fine-grained read permissions.

PPF implication:

- medical records are **not a foundation dependency**;
- if supported later, PPF should ingest only normalized, permissioned context needed for a specific personal-pattern use case;
- clinical records should retain provenance/source metadata;
- medical sources should never silently upgrade a behavioral pattern into a diagnosis.

Sources:

- Medical Records: https://developer.android.com/health-and-fitness/health-connect/medical-records
- Medical Records data format: https://developer.android.com/health-and-fitness/health-connect/medical-records/data-format

---

### 3.3 Wear OS — wearable evidence

Wear OS Health Services provides three important patterns of use:

- `PassiveMonitoringClient` for long-lived, relatively infrequent passive updates;
- `MeasureClient` for short-lived rapid measurements while the user is actively interacting;
- `ExerciseClient` for workout sessions and exercise state.

Wear OS documentation notes that many exercise signals are delivered roughly once per second, but delivery may switch from streaming to batching when the display becomes non-interactive to reduce power usage.

PPF implication:

- wearable evidence may arrive batched or delayed;
- event time and ingestion time must be separate fields;
- PPF must not use arrival order as behavioral order;
- power-saving behavior means `missing_now` does not equal `no_activity`.

Sources:

- Health Services: https://developer.android.com/health-and-fitness/health-services
- Device compatibility/delivery behavior: https://developer.android.com/health-and-fitness/health-services/compatibility

#### Wear OS ↔ phone synchronization

Wear OS Data Layer synchronizes app-private data between watch and phone. Android documentation explicitly states that Data Layer is a synchronization mechanism, not permanent storage; apps should keep their own local copy.

PPF implication:

- PPF needs source/event IDs and deduplication semantics across devices;
- watch and phone observations may represent the same underlying event;
- synchronization delays must not create duplicate evidence.

Source:

- https://developer.android.com/training/wearables/data/sync

---

### 3.4 iOS / Apple ecosystem — personal/device signals

#### Calendar/reminders

EventKit provides access to calendar and reminder data after explicit authorization. Since iOS 17, Apple encourages requesting the narrowest access level; write-only calendar access exists, while reading requires full access.

PPF implication:

- reading personal calendar is available only under explicit full-access permission;
- a write-only integration cannot be treated as an observation source;
- source capability must distinguish `can_write` from `can_observe`.

Sources:

- https://developer.apple.com/documentation/eventkit/accessing-the-event-store
- https://developer.apple.com/documentation/eventkit/accessing-calendar-using-eventkit-and-eventkitui

#### App and website usage

Apple provides app/website usage access through Family Controls and Device Activity under an entitlement and explicit user authorization. The entitlement can allow access to application bundle identifiers, visited domain names and activity category names.

PPF implication:

- app-usage evidence exists but is entitlement/authorization constrained;
- PPF cannot assume ordinary unrestricted iOS cross-app telemetry;
- capability discovery must precede pattern interpretation.

Source:

- https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.family-controls.app-and-website-usage

#### Motion

Core Motion exposes raw and processed accelerometer, gyroscope, pedometer and environment-related data across iOS, iPadOS, watchOS and visionOS where supported.

PPF implication:

- processed motion/activity context is a better foundation signal than retaining raw high-rate sensor streams;
- device capability varies, so source metadata must include device/sensor availability.

Source:

- https://developer.apple.com/documentation/coremotion

#### Location / geofencing

Core Location supports region/condition monitoring and can wake an iOS app when region state changes. Continuous background location is more constrained and Apple recommends using it only when necessary.

PPF implication:

- semantic location events such as `entered_home_region` or `left_work_region` are strong low-volume context signals;
- continuous raw GPS should not be a foundation requirement;
- permission level and precision must be represented separately from the resulting location-derived event.

Sources:

- Region monitoring: https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions
- Background location: https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background

---

### 3.5 Apple HealthKit / Apple Watch

HealthKit is a central repository for health and fitness information on iPhone and Apple Watch. Apps must request fine-grained permissions per data type.

Critically, HealthKit privacy behavior means an app cannot reliably infer that read permission was denied; from the app's perspective, denied data can look like nonexistent data. Apple also permits users to grant limited history windows.

PPF implication:

This directly requires a four-state evidence model such as:

```text
OBSERVED
OBSERVABLE_NON_OCCURRENCE
NOT_OBSERVED
UNKNOWN_NOT_OBSERVABLE
```

where permission/capability state is independently tracked.

Sources:

- HealthKit overview: https://developer.apple.com/documentation/healthkit
- Authorization: https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data
- Privacy: https://developer.apple.com/documentation/healthkit/protecting_user_privacy

#### Background delivery and workouts

HealthKit supports background delivery for selected data types. Apple Watch workout sessions enable continued background execution and high-frequency workout measurements, but health data access can still be restricted while a device is locked.

PPF implication:

- timestamps must be source timestamps, not processing timestamps;
- delayed/batched health events must remain valid evidence without appearing as new behavioral actions;
- PPF should ingest summaries/events, not assume continuous realtime health access.

Sources:

- `HKHealthStore` background delivery: https://developer.apple.com/documentation/healthkit/hkhealthstore
- Workouts: https://developer.apple.com/documentation/healthkit/workouts-and-activity-rings
- `HKWorkoutSession`: https://developer.apple.com/documentation/healthkit/hkworkoutsession

#### Clinical records

HealthKit can read FHIR clinical records downloaded by users from supported health institutions, with permission per record type.

PPF implication:

- clinical information is optional and provenance-sensitive;
- foundation tests should not depend on clinical records;
- medical data should be introduced only if a future use case clearly requires it.

Source:

- https://developer.apple.com/documentation/healthkit/accessing-health-records

---

### 3.6 Connected accessories and external wearables

Apple Core Bluetooth supports communication with BLE/Classic Bluetooth devices, and background Bluetooth modes can support certain long-lived accessory interactions. Nearby Interaction supports distance/direction interactions with Apple devices and selected third-party accessories using UWB/Bluetooth-based mechanisms under platform constraints.

PPF implication:

- third-party wearable/medical device events should enter PPF through the same normalized event contract as phone/watch events;
- transport technology must not leak into pattern semantics;
- connection loss must be modeled as source unavailability, not as a negative behavioral event.

Sources:

- Core Bluetooth: https://developer.apple.com/documentation/corebluetooth
- Nearby Interaction: https://developer.apple.com/documentation/nearbyinteraction

---

## 4. App-to-app / agent surfaces relevant to later integration

### Android AppFunctions

Android AppFunctions allows apps to expose discrete functions to trusted/system-privileged agents for cross-app orchestration. It was added at platform API level 36 and the broader AppFunctions integration remains experimental/preview in current Android documentation.

PPF implication:

- PPF should not depend on AppFunctions;
- PPF outputs can later become context for MindForge-Mobile tool/app selection;
- execution authority remains outside PPF.

Sources:

- https://developer.android.com/reference/android/app/appfunctions/package-summary
- https://developer.android.com/ai/appfunctions

### Apple App Intents

Apple App Intents allows apps to expose actions and data to Apple Intelligence, Siri, Spotlight, Shortcuts, widgets and other system experiences.

PPF implication:

- useful future action surface;
- not an observation/pattern-discovery dependency;
- reinforces separation: `PPF recognizes`, `MindForge understands/routes`, `host/app executes`.

Sources:

- https://developer.apple.com/documentation/appintents
- https://developer.apple.com/documentation/appintents/appintent

---

## 5. Health/medical regulatory boundary

PPF foundation should stay in the **personal-pattern / general-wellness** domain unless an independently scoped medical project is explicitly authorized.

FDA's January 2026 General Wellness guidance states that software intended to maintain or encourage a healthy lifestyle and unrelated to diagnosis, cure, mitigation, prevention or treatment can fall outside the medical-device definition. FDA separately applies risk-based oversight to software functions that meet the medical-device definition, including software that controls medical devices or provides patient-specific diagnosis/treatment-oriented outputs.

PPF implication:

Initial PPF rules:

```text
Allowed foundation role:
- recognize routines
- recognize behavioral patterns
- contextualize wellness/fitness observations
- retrieve user-authorized personal context

Not foundation role:
- diagnose disease
- recommend treatment
- control a medical device
- convert personal pattern confidence into clinical risk claims
```

Sources:

- FDA General Wellness, January 2026: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices
- FDA Device Software Functions / Mobile Medical Apps: https://www.fda.gov/medical-devices/digital-health-center-excellence/device-software-functions-including-mobile-medical-applications
- FDA digital health terms: https://www.fda.gov/medical-devices/digital-health-center-excellence/digital-health-terms

This section is a research boundary, not legal advice.

---

## 6. Device capability matrix

| Signal/source | Android | iOS | Wearable | Foundation value | Main constraint |
|---|---|---|---|---|---|
| time/day/context | yes | yes | yes | very high | timezone/clock changes |
| app usage | UsageStats, permission | entitlement/authorization constrained | limited/app-specific | high | privacy/entitlements |
| notifications | listener service, user-enabled | no equivalent broad ordinary-app feed assumed | app-specific | medium/high | highly sensitive |
| calendar | permissioned provider | EventKit full read access | synchronized/app-specific | very high | explicit permission |
| contacts/person entities | permissioned | permissioned APIs exist; not assumed globally | phone-mediated | high | identity/privacy |
| coarse location/geofence | permissioned | Core Location | watch/device dependent | very high | background/precision permission |
| raw motion sensors | yes | Core Motion | yes | medium | power/data volume |
| derived activity | available via platform/services | available via Motion/Health | strong | high | device-specific |
| health/fitness | Health Connect | HealthKit | strong | optional high | fine-grained permissions |
| clinical records | FHIR experimental path | HealthKit FHIR records | phone repository | optional | strong privacy/regulatory boundary |
| external BLE accessory | yes | Core Bluetooth | yes | optional | connectivity/background limits |
| cross-app actions | AppFunctions emerging | App Intents | app/system dependent | downstream | trusted/declared functions only |

---

## 7. What PPF can safely assume

PPF may assume only that an event source can provide a normalized observation when available.

PPF must **not** assume:

```text
all sources exist
all sources are authorized
all events arrive in real time
all histories are complete
missing event == negative evidence
watch and phone events are independent
arrival order == occurrence order
raw app activity is available on every OS
device source remains continuously connected
health data is accessible
medical data is required
```

---

## 8. Required event-foundation concepts derived from research

The platform survey implies that PPF-L2 must represent at least:

### Event identity

- event ID;
- source-native ID if available;
- deduplication/correlation key.

### Time

- event occurrence time;
- observation/ingestion time;
- timezone/time basis;
- interval start/end when applicable.

### Source

- platform;
- device class;
- source adapter/type;
- source app/provider when relevant;
- source provenance.

### Observability

- source capability available/unavailable;
- permission scope/state where knowable;
- foreground/background/history capability;
- data freshness/window;
- `unknown/not observable` state.

### Behavioral semantics

- actor/person entity;
- context;
- action/event type;
- target/object;
- result/outcome;
- explicit vs inferred/observed;
- opportunity/non-occurrence semantics.

### Quality

- confidence/quality supplied by source if meaningful;
- raw vs derived;
- delayed/batched flag;
- correction/deletion lineage.

---

## 9. Key scientific implication: opportunity must be explicit

To discover a routine, PPF needs more than positive occurrences.

Example:

```text
Observed positive events:
17 commute-home events
```

is scientifically weaker than:

```text
21 observable commute opportunities
17 home
3 alternative destination
0 observable non-action
1 source unavailable / unknown
```

The denominator changes the interpretation.

Therefore PPF-L2 must prove it can represent:

```text
OCCURRENCE
OBSERVABLE NON-OCCURRENCE
OPPORTUNITY
UNKNOWN / UNOBSERVABLE
```

without collapsing them into a single absent/present boolean.

---

## 10. Greenfield design conclusion

The research supports the PPF greenfield direction.

No evidence from device platforms requires HDC, SLM, a graph database, vector database, LLM-based discovery, or any legacy PIS machinery at the foundation.

The minimum promising path remains:

```text
platform events
-> normalized event contract
-> explicit observability/opportunity semantics
-> ground-truth benchmark
-> trivial statistical baselines
-> only then add missing mechanisms
```

Architecture should follow benchmark failures, not precede them.

---

## 11. Research decision

```text
Device/platform feasibility: PLAUSIBLE / SUFFICIENT FOR L1-L2 RESEARCH

Android as signal source: FEASIBLE WITH PERMISSIONS/RESTRICTIONS

iOS as signal source: FEASIBLE BUT MORE ENTITLEMENT/PERMISSION CONSTRAINED

Wearables: USEFUL OPTIONAL EVIDENCE SOURCE

Health/fitness: OPTIONAL EVIDENCE SOURCE

Clinical/medical: OPTIONAL / OUTSIDE FOUNDATION DEPENDENCY

Legacy PIS: NOT REQUIRED

PPF implementation: NOT AUTHORIZED

PPF-L1/L2 protocol definition: AUTHORIZED
```

---

## 12. Primary sources

Official platform sources used in this research:

### Android

- App usage: https://developer.android.com/reference/android/app/usage/UsageStatsManager
- Usage events: https://developer.android.com/reference/android/app/usage/UsageEvents
- Notification listener: https://developer.android.com/reference/android/service/notification/NotificationListenerService.html
- Contacts Provider: https://developer.android.com/identity/providers/contacts-provider
- Calendar Provider: https://developer.android.com/identity/providers/calendar-provider
- Sensors: https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview
- Background restrictions: https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions
- AppFunctions: https://developer.android.com/ai/appfunctions

### Health Connect / Wear OS

- Health Connect: https://developer.android.com/health-and-fitness/health-connect
- Health Connect data types: https://developer.android.com/health-and-fitness/health-connect/data-types
- Health Connect sync/background reads: https://developer.android.com/health-and-fitness/health-connect/sync-data
- Health Connect Medical Records: https://developer.android.com/health-and-fitness/health-connect/medical-records
- Medical Records format: https://developer.android.com/health-and-fitness/health-connect/medical-records/data-format
- Wear OS Health Services: https://developer.android.com/health-and-fitness/health-services
- Wear OS Health Services compatibility: https://developer.android.com/health-and-fitness/health-services/compatibility
- Wear OS Data Layer: https://developer.android.com/training/wearables/data/sync

### Apple

- App Intents: https://developer.apple.com/documentation/appintents
- EventKit access: https://developer.apple.com/documentation/eventkit/accessing-the-event-store
- Family Controls app/website usage entitlement: https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.family-controls.app-and-website-usage
- Core Motion: https://developer.apple.com/documentation/coremotion
- Core Location geofencing: https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions
- Background location: https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background
- HealthKit: https://developer.apple.com/documentation/healthkit
- HealthKit authorization: https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data
- HealthKit privacy: https://developer.apple.com/documentation/healthkit/protecting_user_privacy
- HealthKit clinical records: https://developer.apple.com/documentation/healthkit/accessing-health-records
- Core Bluetooth: https://developer.apple.com/documentation/corebluetooth
- Nearby Interaction: https://developer.apple.com/documentation/nearbyinteraction

### Regulatory boundary

- FDA General Wellness (2026): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices
- FDA Device Software Functions / Mobile Medical Applications: https://www.fda.gov/medical-devices/digital-health-center-excellence/device-software-functions-including-mobile-medical-applications
- FDA Digital Health Terms: https://www.fda.gov/medical-devices/digital-health-center-excellence/digital-health-terms
