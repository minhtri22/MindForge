# PPF-L2 Personal Event Foundation — Independent Semantic Review

Status: **INDEPENDENT REVIEW / L2 PROOF ARTIFACT**
Protocol authority: `ppf-l1-l2-foundation-protocol.md`
Contract under review: `ppf-personal-event-contract.md`
Fixture catalog: `ppf-l2-fixtures.md`
Machine validation: `tools/research/ppf_l2_validate.py`

## 1. Primary research question

Can one small, implementation-independent and platform-neutral personal-event model represent the evidence distinctions required by the frozen L1 Recognize-Me contract?

**Review answer: YES.**

The proof covers 60 fixtures, including 35 adversarial fixtures, 5 explicit cross-platform equivalence pairs, and 81 event records. The model remains an evidence representation. It contains no pattern discovery, admission, scoring, retrieval, database, SDK adapter, synchronization engine, or production collection implementation.

## 2. Independent-review attack questions

The review re-applied the 13 Protocol-v2 L2 questions to the fixture set without relying on a future pattern algorithm.

| Attack question | Result | Evidence from the contract/fixtures |
|---|---|---|
| What underlying phenomenon happened, if known? | PASS | `event_type`, payload, phenomenon time, and evidence kind preserve what was observed without converting it into a pattern. |
| What observation/result was produced? | PASS | Every fixture contains one or more explicit evidence records with source and evidence kind. |
| Can phenomenon, result/observation, and ingestion time differ? | PASS | F013-F022 cover delay, batching, out-of-order arrival, interval, timezone, DST, approximate timing, and clock skew. |
| Was behavior observable under the applicable capture policy? | PASS | F023-F030 and F036 make capture mode, expected observability, coverage, and missingness explicit. |
| Was there an opportunity? | PASS | F031-F036 represent opportunity existence, alternatives, occurrence, observable non-occurrence, and unknown outcome. |
| Is observable non-occurrence distinguishable from missing/no observation? | PASS | F023-F030 vs F033-F034; validator rejects observable non-occurrence without explicit opportunity. |
| Which source/device/provider supplied the evidence? | PASS | Source platform, device class, provider, and optional source event identity are explicit in every event. |
| Is observation quality/coverage separate from pattern confidence? | PASS | F021-F022, F047, F059 carry degraded/partial evidence without any pattern confidence field. Validator rejects pattern-level payload leakage. |
| Is evidence raw or derived, and is derivation provenance available? | PASS | F041-F044 distinguish RAW/DERIVED; known derivations carry procedure/input lineage; unknown procedure remains explicit. |
| Is a second-device record a replica, independent corroboration, or unknown? | PASS | F037/F038/F039 represent all three states directly. |
| Can correction/deletion/supersession lineage be represented? | PASS | F040, F048, F050-F057 cover correction, context correction, targeting, supersession, invalidation, deletion, and reset scope. |
| Is context compositional where needed? | PASS | F045-F048 represent simultaneous dimensions, unknown dimensions, conflicts, and correction lineage. |
| Does the event stay evidence rather than a pattern conclusion? | PASS | All 60 fixtures remain evidence/control/observability records; negative tests reject pattern event/payload leakage. |

No attack question required a pattern algorithm or implementation assumption to answer.

## 3. Ambiguity review

### Ambiguities found and resolved inside L2

| ID | Ambiguity | Resolution |
|---|---|---|
| A1 | A record timestamp could mean behavior time, source-observation time, or backend arrival. | Three conceptual times are mandatory; batching and out-of-order fixtures prove arrival cannot substitute for behavior time. |
| A2 | No event arriving could be interpreted as the behavior not happening. | Missing-like observability states require an explicit reason; only `OBSERVABLE_NON_OCCURRENCE` with explicit opportunity is a negative observation. |
| A3 | Opportunity could become a separate subsystem or denominator engine. | L2 keeps one optional opportunity object containing only identity, state, alternatives, and observability. |
| A4 | A derived episode could be confused with a final pattern. | `DERIVED_OBSERVATION` requires derivation provenance when known and remains an evidence kind; pattern fields are forbidden. |
| A5 | Phone/watch duplicates could be counted as independent evidence. | Explicit relationship types separate replica, corroboration, and unknown relationship. |
| A6 | User correction could silently overwrite the source evidence. | User feedback/control is a new event with target/correction lineage. |
| A7 | Deletion lineage could be misread as a storage-retention policy. | `DELETES` proves semantic intent/target only; physical retention and privacy enforcement are outside L2. |
| A8 | Context could be forced into one categorical label. | Context is a map of independent dimensions, each known/unknown/conflicting. |
| A9 | `result_or_observed_time` combines two related concepts. | The field means the source-side time at which the observation/result became available. L2 needs this boundary from phenomenon and ingestion; splitting result and observation into two mandatory fields added no fixture-level distinction. |
| A10 | User feedback captured through Android/iOS UI could lose user provenance or platform provenance. | Semantic role is carried by `evidence_kind=USER_FEEDBACK`; the source envelope records the capture surface/provider. Direct user-origin events may use `source.platform=USER`. |
| A11 | Clinical-looking data could accidentally introduce diagnosis semantics. | Optional health/medical-looking payload is opaque source evidence; no diagnostic, treatment, risk, or clinical decision semantics exist in the contract. |

### Remaining ambiguity by class

```text
identity/source ambiguity:              0 unresolved
three-time ambiguity:                   0 unresolved
observability/missingness ambiguity:    0 unresolved
opportunity ambiguity:                  0 unresolved for L2 representability
multi-device ambiguity:                 0 unresolved
raw/derived ambiguity:                  0 unresolved
context ambiguity:                      0 unresolved at representation level
user-feedback lineage ambiguity:        0 unresolved
deletion/reset semantic ambiguity:      0 unresolved at representation level
pattern-admission ambiguity:            outside L2 by protocol
production storage/collection choices:  outside L2 by protocol
```

## 4. L1 → L2 dependency evaluation

The frozen L1 semantic review left concrete evidence-representation dependencies for L2. Each dependency was re-evaluated against the contract and fixtures.

| L1 dependency | L2 result | Evidence |
|---|---|---|
| observable opportunity/non-occurrence | **REPRESENTABLE** | Opportunity object plus F031-F036; F033/F034 make non-occurrence explicit. |
| observability/missingness | **REPRESENTABLE** | Capture policy, observability state, missingness reason, coverage; F023-F030/F036. |
| compositional context | **REPRESENTABLE** | Context dimensions with known/unknown/conflicting status; F045-F048. |
| temporal evidence | **REPRESENTABLE** | Three-time model and interval/timezone/timing quality; F013-F022/F052. |
| source/provenance | **REPRESENTABLE** | Source envelope and derivation provenance across all fixtures; F042-F044 are direct derivation tests. |
| observation quality | **REPRESENTABLE** | Quality and coverage are explicit and separate from pattern confidence; F021/F022/F047/F059. |
| relationship/entity identity | **REPRESENTABLE** | Entity references and known/unknown relationship state; F058 plus multi-device fixtures. |
| user feedback provenance/scope/time | **REPRESENTABLE** | F007/F008/F048-F052/F056/F057. |
| correction/supersession/deletion lineage | **REPRESENTABLE** | F040/F048/F050/F051/F053-F057. |
| raw/derived evidence | **REPRESENTABLE** | Evidence-kind vocabulary and derivation provenance; F041-F044. |

Result: **10/10 L1 dependencies REPRESENTABLE; 0 PARTIAL; 0 NOT REPRESENTABLE.**

## 5. Minimality review

The fixture set uses one JSON event model. Platform/device/source differences are data values, not subclasses. Instant and duration evidence share the same event with optional phenomenon `end`. Opportunity remains a small optional object. Provenance remains direct references and relation types rather than a graph engine.

The following concepts are required by at least one frozen gate and cannot be removed without losing a tested semantic distinction:

- local event identity and source identity;
- three conceptual times;
- evidence kind;
- capture policy;
- observability plus missingness reason;
- opportunity state and observability;
- compositional context;
- evidence quality/coverage;
- derivation provenance;
- multi-device relationship type;
- user/control provenance;
- correction/deletion/supersession relations.

The following were tested as unnecessary for L2 and remain absent: event subclasses, episode classes, SDK-specific core fields, broker semantics, device registry service, provenance database, opportunity engine, pattern confidence, pattern scores, admission thresholds, persistence/indexing/query design, background collectors, and mobile SDK dependencies.

**Minimality result: PASS.** The model is small enough to remain a foundation contract while retaining every distinction required by L1 and L2 gates.

## 6. Fixture audit

Machine validator result after fixture generation:

```text
PASS
fixtures=60
adversarial=35
cross_platform_pairs=5
events=81
negative_tests=8/8
```

The eight negative tests verify rejection of:

1. observable non-occurrence without explicit opportunity;
2. unresolved lineage target;
3. duplicate event identity;
4. known derivation without procedure reference;
5. invalid phenomenon interval;
6. unknown schema enum;
7. platform-specific field injected into the core event;
8. pattern-level confidence leakage.

The validator additionally checks contiguous fixture IDs, global event-ID uniqueness, source-identity reuse with required replica/correction lineage, missingness reasons for missing-like states, required capture-policy provenance for passive/source evidence, resolvable input/relation references, exactly 60 fixtures, at least 18 adversarial cases, exactly 5 two-fixture cross-platform pairs, and aggregate coverage of L2-G1 through L2-G18.

## 7. Cross-platform equivalence review

The five equivalence pairs were reviewed for semantic sameness after ignoring platform/provider provenance:

| Pair | Result | Review |
|---|---|---|
| Android calendar / iOS calendar | PASS | Same `calendar.event` evidence semantics; only source provenance differs. |
| Wear OS workout / watchOS workout | PASS | Same interval event and wearable capture semantics. |
| Android geofence / iOS region | PASS | Same platform-neutral region-transition meaning. |
| Android UI rejection / iOS UI rejection | PASS | Same USER_FEEDBACK rejection semantics; capture surface remains provenance. |
| Health Connect / HealthKit measurement | PASS | Same optional health-measurement envelope with repository/provider difference only. |

No pair required a platform SDK field in the foundation model.

## 8. Independent fixture classification

For G18, every fixture was re-read as evidence records and assigned a primary foundation-level classification. The classification is intentionally coarser than the authoring family and does not use a pattern algorithm.

| Fixture | Independent classification | Match |
|---|---|:---:|
| L2-F001 | observed calendar/source event | PASS |
| L2-F002 | observed calendar/source event | PASS |
| L2-F003 | observed wearable interval | PASS |
| L2-F004 | observed wearable interval | PASS |
| L2-F005 | observed region transition | PASS |
| L2-F006 | observed region transition | PASS |
| L2-F007 | user feedback/rejection | PASS |
| L2-F008 | user feedback/rejection | PASS |
| L2-F009 | optional health measurement | PASS |
| L2-F010 | optional health measurement | PASS |
| L2-F011 | same-origin replication | PASS |
| L2-F012 | distinct identities at equal time | PASS |
| L2-F013 | delayed source result | PASS |
| L2-F014 | delayed ingestion | PASS |
| L2-F015 | batched observations | PASS |
| L2-F016 | out-of-order ingestion | PASS |
| L2-F017 | observed interval | PASS |
| L2-F018 | timezone-preserving observation | PASS |
| L2-F019 | DST spring-forward interval | PASS |
| L2-F020 | DST repeated-hour disambiguation | PASS |
| L2-F021 | clock-skew-suspected observation | PASS |
| L2-F022 | approximate-time observation | PASS |
| L2-F023 | no observation / sampling gap | PASS |
| L2-F024 | source unavailable / disconnect | PASS |
| L2-F025 | permission unavailable or unknown | PASS |
| L2-F026 | outside capture window | PASS |
| L2-F027 | history unavailable | PASS |
| L2-F028 | delayed data / sync gap | PASS |
| L2-F029 | unknown outcome | PASS |
| L2-F030 | no observation by design | PASS |
| L2-F031 | opportunity with unknown outcome | PASS |
| L2-F032 | opportunity with occurrence | PASS |
| L2-F033 | observable non-occurrence | PASS |
| L2-F034 | scoped/partial observable non-occurrence evidence | PASS |
| L2-F035 | observed opportunity/alternatives | PASS |
| L2-F036 | opportunity outcome unobservable by permission | PASS |
| L2-F037 | same-origin cross-device replica | PASS |
| L2-F038 | independent cross-device corroboration | PASS |
| L2-F039 | unknown cross-device relationship | PASS |
| L2-F040 | source correction under reused identity | PASS |
| L2-F041 | raw location observation | PASS |
| L2-F042 | derived visit with raw lineage | PASS |
| L2-F043 | derived evidence with unknown procedure | PASS |
| L2-F044 | multi-input derived observation | PASS |
| L2-F045 | compositional known context | PASS |
| L2-F046 | mixed known/unknown context | PASS |
| L2-F047 | conflicting context evidence | PASS |
| L2-F048 | user context correction | PASS |
| L2-F049 | user assertion | PASS |
| L2-F050 | user rejection targeting derived evidence | PASS |
| L2-F051 | user correction targeting source evidence | PASS |
| L2-F052 | temporally bounded user feedback | PASS |
| L2-F053 | source correction lineage | PASS |
| L2-F054 | derived supersession lineage | PASS |
| L2-F055 | source invalidation lineage | PASS |
| L2-F056 | deletion control lineage | PASS |
| L2-F057 | scoped reset control | PASS |
| L2-F058 | entity with unknown relationship | PASS |
| L2-F059 | degraded-quality partial-coverage evidence | PASS |
| L2-F060 | opaque optional clinical-looking evidence | PASS |

**Independent classification result: 60/60 consistent.**

The most adversarial distinctions remain readable from the records themselves: F011 is a replica rather than a second occurrence; F023-F030 are missing/unobservable rather than negative behavior; F033 is an actual observable non-occurrence; F039 declines to guess cross-device independence; F043 preserves unknown derivation procedure; F047 preserves conflicting context; F050/F051 preserve user target scope; and F060 carries source evidence without clinical inference.

## 9. Frozen L2 gate evaluation

| Gate | Result | Evidence |
|---|---|---|
| **L2-G1** one small platform-neutral event model covers >=40 fixtures | **PASS** | One schema covers 60 fixtures across phone/watch/service/user/health sources. |
| **L2-G2** event identity/source semantics are unambiguous | **PASS** | Contract §§2-3; F001-F012, F037-F040; validator checks duplicate IDs/source-identity reuse. |
| **L2-G3** phenomenon/result-or-observed/ingestion timing is representable | **PASS** | Contract §4; F003/F004, F013-F022, F052. |
| **L2-G4** source and derivation provenance are preserved | **PASS** | Contract §§3,10; F042-F044, F054. |
| **L2-G5** capture policy, expected coverage, and history/sampling limits are representable | **PASS** | Contract §§5,9; F003/F004/F009/F010/F015/F021-F030/F034/F036/F059/F060. |
| **L2-G6** observability/missingness state is explicit | **PASS** | Contract §6; F023-F031/F036/F046. |
| **L2-G7** opportunity semantics are explicit | **PASS** | Contract §7; F031-F036. |
| **L2-G8** observable non-occurrence remains distinct from missing/no observation | **PASS** | F023-F030/F036 vs F033/F034; validator negative test. |
| **L2-G9** delayed/batched/out-of-order events remain semantically correct | **PASS** | F013-F016/F019. |
| **L2-G10** same-origin replication, independent corroboration, and unknown relationship are representable | **PASS** | Contract §11; F011/F037/F038/F039. |
| **L2-G11** raw and derived observations are distinguishable | **PASS** | Contract §10; F041-F044/F054. |
| **L2-G12** user feedback/correction is provenance-bearing evidence | **PASS** | Contract §12; F007/F008/F048-F052/F056/F057. |
| **L2-G13** correction/delete/supersession lineage is representable | **PASS** | Contract §13; F040/F048/F050/F051/F053-F057. |
| **L2-G14** context is compositional and platform-neutral | **PASS** | Contract §8; F005/F006/F045-F048/F052/F058. |
| **L2-G15** health/medical evidence is optional and does not expand clinical scope | **PASS** | Contract §§16-17; F009/F010/F060. |
| **L2-G16** no pattern conclusion leaks into the event layer | **PASS** | Contract §§9-10,15; fixtures contain no pattern conclusions; validator rejects pattern event/payload fields. |
| **L2-G17** no mobile/platform SDK dependency exists in the foundation model | **PASS** | Cross-platform pairs use one schema; SDK-specific core-field negative test fails as required. |
| **L2-G18** an independent reviewer classifies all fixtures consistently | **PASS** | §8 reclassification table: 60/60 consistent. |

All frozen L2 gates PASS.

## 10. Additional scope checks

```text
Pattern algorithm selected:                  NO
Pattern discovery implemented:               NO
Pattern confidence/calibration implemented: NO
Routine/preference scoring implemented:      NO
Database/storage selected:                   NO
Mobile SDK adapter selected:                 NO
Collection service implemented:              NO
Health diagnosis/treatment semantics added:  NO
L3 benchmark execution started:              NO
L4/L5 execution started:                     NO
Production PPF implementation started:       NO
```

## 11. Scientific verdict

```text
PPF-L2: PASS / FROZEN
```

The L2 success criterion is met: one small platform-neutral event foundation can represent the evidence semantics required by frozen L1 across the bounded fixture set, including the failure modes most likely to create false behavioral evidence.

This PASS proves **representability only**. It does not prove that real-world data collection is complete, that pattern ground truth exists, that a pattern can be discovered reliably, that thresholds are calibrated, or that PPF is production-feasible.

L3/L4/L5 and production PPF remain **BLOCKED / NOT AUTHORIZED** by this proof.

## 12. Recommendation

Freeze the L2 event contract, schema, fixtures, validator, and semantic review at this branch revision. The next scientific layer would require a separately authorized L3 ground-truth benchmark proof. Stop here after repository verification and publication of the L2 research commit.
