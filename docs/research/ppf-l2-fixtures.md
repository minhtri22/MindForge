# PPF-L2 Fixture Catalog

Status: **RESEARCH PROOF ARTIFACT**
Schema: `data/ppf-l2/schema.json`
Validator: `tools/research/ppf_l2_validate.py`

This catalog is the human-review index for the 60 frozen PPF-L2 representability fixtures. Each fixture is a standalone JSON artifact with expected semantics and applicable frozen L2 gates.

```text
fixtures:             60
adversarial:          35
cross-platform pairs: 5
event records:        81
```

## Fixture index

| ID | Family | Expected interpretation | File | ADV | Cross-platform pair |
|---|---|---|---|:---:|---|
| L2-F001 | cross-platform-calendar | A calendar commitment occurred and is represented as a source observation. | `data/ppf-l2/fixtures/L2-F001.json` | no | XP-CALENDAR |
| L2-F002 | cross-platform-calendar | The same semantic class of calendar commitment is representable from iOS. | `data/ppf-l2/fixtures/L2-F002.json` | no | XP-CALENDAR |
| L2-F003 | cross-platform-workout | A workout episode is an observation with start/end phenomenon time. | `data/ppf-l2/fixtures/L2-F003.json` | no | XP-WORKOUT |
| L2-F004 | cross-platform-workout | The same workout episode semantics are representable from watchOS. | `data/ppf-l2/fixtures/L2-F004.json` | no | XP-WORKOUT |
| L2-F005 | cross-platform-region | A region-entry transition occurred; the region is an opaque semantic identifier. | `data/ppf-l2/fixtures/L2-F005.json` | no | XP-REGION |
| L2-F006 | cross-platform-region | The same region-entry transition semantics are representable from iOS. | `data/ppf-l2/fixtures/L2-F006.json` | no | XP-REGION |
| L2-F007 | cross-platform-feedback | The user explicitly rejected an interpretation; the UI surface is provenance, not semantics. | `data/ppf-l2/fixtures/L2-F007.json` | no | XP-FEEDBACK |
| L2-F008 | cross-platform-feedback | The same explicit rejection semantics are representable from iOS. | `data/ppf-l2/fixtures/L2-F008.json` | no | XP-FEEDBACK |
| L2-F009 | cross-platform-health | An optional health-repository measurement is ordinary evidence in the foundation envelope. | `data/ppf-l2/fixtures/L2-F009.json` | no | XP-HEALTH |
| L2-F010 | cross-platform-health | The same optional health measurement semantics are representable from HealthKit. | `data/ppf-l2/fixtures/L2-F010.json` | no | XP-HEALTH |
| L2-F011 | identity | Two records are replicas of one source event, not two behavioral occurrences. | `data/ppf-l2/fixtures/L2-F011.json` | yes | — |
| L2-F012 | identity | Two distinct source identities at one timestamp remain two observations. | `data/ppf-l2/fixtures/L2-F012.json` | yes | — |
| L2-F013 | three-time | The phenomenon happened at 06:00; the source produced the result at 06:30. | `data/ppf-l2/fixtures/L2-F013.json` | yes | — |
| L2-F014 | three-time | The event was observed promptly but reached the foundation a day later. | `data/ppf-l2/fixtures/L2-F014.json` | yes | — |
| L2-F015 | three-time | Two observations uploaded together retain distinct behavioral times. | `data/ppf-l2/fixtures/L2-F015.json` | yes | — |
| L2-F016 | three-time | The 09:30 phenomenon arrived first, but behavioral order remains 09:00 then 09:30. | `data/ppf-l2/fixtures/L2-F016.json` | yes | — |
| L2-F017 | three-time | An episode is represented by phenomenon start/end in the same event model. | `data/ppf-l2/fixtures/L2-F017.json` | no | — |
| L2-F018 | three-time | Local-time context is retained while all three times remain absolute instants. | `data/ppf-l2/fixtures/L2-F018.json` | no | — |
| L2-F019 | three-time | Offset-aware timestamps preserve a ten-minute real interval across the skipped wall-clock hour. | `data/ppf-l2/fixtures/L2-F019.json` | yes | — |
| L2-F020 | three-time | Two 01:30 local observations are distinct absolute instants because offsets differ. | `data/ppf-l2/fixtures/L2-F020.json` | yes | — |
| L2-F021 | three-time | Timing is retained as reported and explicitly marked as skew-suspected. | `data/ppf-l2/fixtures/L2-F021.json` | yes | — |
| L2-F022 | three-time | The behavior time is approximate, while result and ingestion timestamps remain precise. | `data/ppf-l2/fixtures/L2-F022.json` | no | — |
| L2-F023 | observability-missingness | A periodic sampling gap means no observation, not behavioral non-occurrence. | `data/ppf-l2/fixtures/L2-F023.json` | yes | — |
| L2-F024 | observability-missingness | Device disconnection makes behavior unobservable for the interval. | `data/ppf-l2/fixtures/L2-F024.json` | yes | — |
| L2-F025 | observability-missingness | Unavailable/unknown read permission cannot be converted into absence evidence. | `data/ppf-l2/fixtures/L2-F025.json` | yes | — |
| L2-F026 | observability-missingness | A foreground-only source intentionally does not cover the background interval. | `data/ppf-l2/fixtures/L2-F026.json` | yes | — |
| L2-F027 | observability-missingness | A bounded history API cannot answer about older behavior. | `data/ppf-l2/fixtures/L2-F027.json` | yes | — |
| L2-F028 | observability-missingness | Data is known to be delayed, so current absence is not a negative observation. | `data/ppf-l2/fixtures/L2-F028.json` | yes | — |
| L2-F029 | observability-missingness | The source cannot classify the behavioral outcome from available evidence. | `data/ppf-l2/fixtures/L2-F029.json` | yes | — |
| L2-F030 | observability-missingness | A deliberate duty cycle leaves intervals with no observation by design. | `data/ppf-l2/fixtures/L2-F030.json` | yes | — |
| L2-F031 | opportunity | A lunch opportunity existed, but the outcome is unknown. | `data/ppf-l2/fixtures/L2-F031.json` | yes | — |
| L2-F032 | opportunity | The observed occurrence is explicitly tied to a commute opportunity. | `data/ppf-l2/fixtures/L2-F032.json` | no | — |
| L2-F033 | opportunity | An explicit exercise opportunity had an observable non-occurrence. | `data/ppf-l2/fixtures/L2-F033.json` | yes | — |
| L2-F034 | opportunity | The model can carry a non-occurrence claim together with explicitly partial opportunity observability. | `data/ppf-l2/fixtures/L2-F034.json` | yes | — |
| L2-F035 | opportunity | A decision opportunity and alternatives are representable before outcome evidence arrives. | `data/ppf-l2/fixtures/L2-F035.json` | no | — |
| L2-F036 | opportunity | The opportunity exists, but permission state makes its outcome unknown. | `data/ppf-l2/fixtures/L2-F036.json` | yes | — |
| L2-F037 | multi-device | Phone and watch records identify one synchronized source occurrence. | `data/ppf-l2/fixtures/L2-F037.json` | yes | — |
| L2-F038 | multi-device | Two independently sourced observations corroborate one phenomenon while retaining separate identity. | `data/ppf-l2/fixtures/L2-F038.json` | no | — |
| L2-F039 | multi-device | The two records may be related, but the evidence does not justify replica or independent labels. | `data/ppf-l2/fixtures/L2-F039.json` | yes | — |
| L2-F040 | identity-lineage | The provider reused a source identity for a corrected representation, with explicit correction lineage. | `data/ppf-l2/fixtures/L2-F040.json` | yes | — |
| L2-F041 | raw-derived | A raw location sample is evidence, not a place-visit conclusion. | `data/ppf-l2/fixtures/L2-F041.json` | no | — |
| L2-F042 | raw-derived | A derived visit is distinguishable from its raw input. | `data/ppf-l2/fixtures/L2-F042.json` | no | — |
| L2-F043 | raw-derived | The evidence remains usable as a derived record while derivation procedure is explicitly unknown. | `data/ppf-l2/fixtures/L2-F043.json` | yes | — |
| L2-F044 | raw-derived | One derived observation references two raw inputs and a known procedure. | `data/ppf-l2/fixtures/L2-F044.json` | no | — |
| L2-F045 | context | Place, social, and weather dimensions coexist independently on one event. | `data/ppf-l2/fixtures/L2-F045.json` | no | — |
| L2-F046 | context | Known social context can coexist with unknown place context. | `data/ppf-l2/fixtures/L2-F046.json` | yes | — |
| L2-F047 | context | Conflicting place evidence remains explicitly conflicting. | `data/ppf-l2/fixtures/L2-F047.json` | yes | — |
| L2-F048 | context-lineage | The user supplies a corrected place value targeting the original event. | `data/ppf-l2/fixtures/L2-F048.json` | no | — |
| L2-F049 | user-evidence | A user assertion is first-class provenance-bearing evidence. | `data/ppf-l2/fixtures/L2-F049.json` | no | — |
| L2-F050 | user-evidence | The user rejected one derived visit; that feedback does not erase the source record. | `data/ppf-l2/fixtures/L2-F050.json` | yes | — |
| L2-F051 | user-evidence | The user corrects one source fact while the original remains auditable. | `data/ppf-l2/fixtures/L2-F051.json` | no | — |
| L2-F052 | user-evidence | User feedback carries a bounded phenomenon interval as its temporal scope. | `data/ppf-l2/fixtures/L2-F052.json` | no | — |
| L2-F053 | lineage | A source-provided correction updates interpretation through lineage without deleting history. | `data/ppf-l2/fixtures/L2-F053.json` | no | — |
| L2-F054 | lineage | The v2 derived result supersedes v1 while both remain inspectable. | `data/ppf-l2/fixtures/L2-F054.json` | yes | — |
| L2-F055 | lineage | A source-control record invalidates earlier evidence while preserving audit lineage. | `data/ppf-l2/fixtures/L2-F055.json` | yes | — |
| L2-F056 | lineage | Deletion is explicit source-control evidence targeting one event. | `data/ppf-l2/fixtures/L2-F056.json` | yes | — |
| L2-F057 | lineage | A user reset targets selected evidence records and retains explicit provenance. | `data/ppf-l2/fixtures/L2-F057.json` | yes | — |
| L2-F058 | entities | An opaque entity can be referenced without inventing a relationship label. | `data/ppf-l2/fixtures/L2-F058.json` | yes | — |
| L2-F059 | quality | The event remains an occurrence while its observation quality and coverage are degraded/partial. | `data/ppf-l2/fixtures/L2-F059.json` | yes | — |
| L2-F060 | optional-health-boundary | A clinical-looking source item can be carried as opaque evidence without interpreting medical meaning. | `data/ppf-l2/fixtures/L2-F060.json` | yes | — |

## Cross-platform equivalence pairs

| Pair | Fixtures | Foundation-level equivalence under review |
|---|---|---|
| XP-CALENDAR | L2-F001 / L2-F002 | Android and iOS calendar occurrences use the same semantic envelope. |
| XP-WORKOUT | L2-F003 / L2-F004 | Wear OS and watchOS workout episodes differ by source provenance, not core semantics. |
| XP-REGION | L2-F005 / L2-F006 | Android geofence and iOS region transitions map to one platform-neutral transition meaning. |
| XP-FEEDBACK | L2-F007 / L2-F008 | Android and iOS feedback surfaces preserve identical rejection semantics with different source provenance. |
| XP-HEALTH | L2-F009 / L2-F010 | Health Connect and HealthKit measurements remain optional repository evidence under one envelope. |

## Required family coverage

The fixture set includes identity/retransmission, same-timestamp identity, three-time delay/batching/out-of-order arrival, interval/timezone/DST/clock-skew cases, observability and missingness, opportunity outcomes, multi-device relation, raw/derived provenance, compositional/unknown/conflicting context, user assertions and feedback, correction/supersession/invalidation/deletion/reset lineage, evidence quality, entity uncertainty, and optional health/medical-boundary examples.

No fixture contains a pattern conclusion, pattern confidence, routine/preference score, admission threshold, or production collection implementation.
