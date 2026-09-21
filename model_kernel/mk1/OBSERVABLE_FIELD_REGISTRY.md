# MK-1 Observable Field Registry v0.1

Status: **FROZEN BEFORE SCIENTIFIC MATERIALIZATION**

Date: **2026-09-21**

Purpose: satisfy the field-registration requirement of `OBSERVABLE_IDENTIFIABILITY_CONTRACT.md` before any scientific scene is materialized.

Common forbidden-information rule for every field below:

- no later turn;
- no future-task sample;
- no downstream policy/action outcome;
- no counterfactual outcome;
- no hidden simulator state;
- no episodic retrieval or external memory.

Expected ambiguity mode for the admitted primary cohort: **NONE**. Any scene whose serialized current input does not uniquely determine every primary field is excluded before training and recorded as an exclusion; Amendment 003 generator v0.2 is designed to generate only uniquely identifiable primary scenes.

## Z1 — binary semantic primitives

All Z1 fields are binary categorical targets. No continuous thresholding is involved. Deterministic baseline availability: **YES**, via exact current-input semantic phrase reconstruction used only by the pre-training identifiability audit. Primary metric: binary precision/recall/F1 and exact-set match.

| Field | Observable source span | Frozen derivation |
|---|---|---|
| CONFLICT_EXISTS | assertion sentence describing incompatible current statements | true iff explicit current contradiction statement is serialized |
| EXPLICIT_SUPERSESSION | assertion sentence describing explicit replacement | true iff explicit replacement statement is serialized |
| IMPLICIT_SELECTION | assertion sentence describing contextual preference without explicit replacement | true iff that selection statement is serialized |
| CORRECTION | assertion sentence describing a later correction | true iff correction statement is serialized |
| CONTEXT_SPLIT | assertion sentence describing different versions in different contexts | true iff context-split statement is serialized |
| EXCEPTS | assertion sentence describing a specific exception | true iff exception statement is serialized |
| EXACT_THRESHOLD | assertion sentence naming exact numeric cutoff | true iff exact-cutoff statement is serialized |
| LOWER_BOUND_THRESHOLD | assertion sentence naming minimum cutoff | true iff lower-bound statement is serialized |
| UPPER_BOUND_THRESHOLD | assertion sentence naming maximum cutoff | true iff upper-bound statement is serialized |
| ORDINAL_TRIGGER | assertion sentence naming ordinal activation | true iff ordinal-trigger statement is serialized |
| VAGUE_COUNT_POLICY | assertion sentence naming imprecise amount | true iff vague-count statement is serialized |
| EXACT_DURATION | assertion sentence naming precise duration | true iff precise-duration statement is serialized |
| APPROX_DURATION | assertion sentence naming approximate duration | true iff approximate-duration statement is serialized |
| PERIODIC_RULE | assertion sentence naming regular recurrence | true iff periodic-rule statement is serialized |
| EXPIRY_RULE | assertion sentence naming expiry after duration | true iff expiry statement is serialized |
| RECENCY_RELATION | assertion sentence saying relative recency matters | true iff recency-relation statement is serialized |
| FALLBACK_IF_UNKNOWN | assertion sentence naming fallback for unknown value | true iff unknown-fallback statement is serialized |
| FALLBACK_IF_CONFLICT | assertion sentence naming fallback under conflict | true iff conflict-fallback statement is serialized |
| FALLBACK_IF_UNAVAILABLE | assertion sentence naming fallback when source unavailable | true iff unavailable-fallback statement is serialized |
| ABSTAINS | assertion sentence explicitly withholding definite conclusion | true iff abstention statement is serialized |
| REQUESTS_CLARIFICATION | assertion sentence requesting clarification | true iff clarification-request statement is serialized |
| LOW_CONFIDENCE | assertion sentence explicitly expressing low confidence | true iff low-confidence statement is serialized |
| PRESERVES_CONFLICT | assertion sentence keeping disagreement unresolved | true iff preserve-conflict statement is serialized |
| OBSERVATION_SCOPE | serialized asserted-scope phrase | true iff asserted scope is OBSERVATION |
| TURN_SCOPE | serialized asserted-scope phrase | true iff asserted scope is TURN |
| SESSION_SCOPE | serialized asserted-scope phrase | true iff asserted scope is SESSION |
| TASK_SCOPE | serialized asserted-scope phrase | true iff asserted scope is TASK |
| WORKFLOW_SCOPE | serialized asserted-scope phrase | true iff asserted scope is WORKFLOW |
| DOMAIN_SCOPE | serialized asserted-scope phrase | true iff asserted scope is DOMAIN |
| GLOBAL_SCOPE | serialized asserted-scope phrase | true iff asserted scope is GLOBAL |
| CONTEXTUAL_SCOPE | serialized asserted-scope phrase | true iff asserted scope is CONTEXTUAL |
| OPERATIONAL_SIGNAL | assertion sentence describing actionable current signal | true iff operational-signal statement is serialized |

## Z2 — observable arguments

| Field | Type | Observable source span | Frozen derivation | Threshold involved | Deterministic baseline | Metric |
|---|---|---|---|---|---|---|
| comparator | 4-way categorical | numeric-cutoff wording | NONE / EXACT / LOWER_BOUND / UPPER_BOUND from explicit wording | no | yes | accuracy |
| temporal_precision | 3-way categorical | duration/expiry wording | NONE / EXACT / APPROX from explicit wording | no | yes | accuracy |
| numeric_value | continuous | serialized numeric cutoff value | parse canonical scalar when present | no | yes | nAE |
| ordinal_index | continuous | serialized ordinal position | parse canonical scalar when present | no | yes | nAE |
| duration_seconds | continuous | serialized duration in seconds | parse canonical scalar when present | no | yes | nAE |
| period_seconds | continuous | serialized recurrence interval in seconds | parse canonical scalar when present | no | yes | nAE |

Presence masks are deterministically identified from whether the corresponding scalar phrase exists in the current input. Missing scalar values are not point-labeled.

Amendment 003 declares that no primary hard target is produced by thresholding these continuous values. Therefore the near-threshold hard-label margin gate is not applicable.

## Z3 — scope state

All are categorical, use current serialized scope phrases only, involve no continuous threshold, have deterministic audit baselines, and are evaluated by accuracy.

| Field | Observable source | Frozen derivation |
|---|---|---|
| evidence_scope | evidence phrase `limited to <scope> scope` | exact eight-way scope label |
| asserted_scope | assertion/boundary phrase `applies at <scope> scope` | exact eight-way scope label |
| scope_relation | evidence_scope + asserted_scope | NARROWER / EQUAL / BROADER / INCOMPARABLE under frozen MK-1 scope rule |

For H1c only, scope_relation is excluded on contextual/non-contextual pairs because PIT-v3 uses a non-identical `CONTEXTUAL` relation label there.

## Z4 — fixed observable support register

All are binary categorical, have no continuous threshold, use evidence sentences only, have deterministic audit baselines, and are evaluated by precision/recall/F1.

| Field | Observable source | Frozen derivation |
|---|---|---|
| conflict_present | evidence contradiction sentence | explicit contradiction present vs absent |
| supersession_supported | evidence replacement-support sentence | evidence establishes replacement vs does not |
| scope_supported | evidence scope-support sentence | evidence sufficient for claimed scope vs not |
| numeric_value_supported | evidence numeric-support sentence | numeric quantity supported vs not |
| temporal_rule_supported | evidence temporal-support sentence | timing rule supported vs not |
| fallback_policy_supported | evidence fallback-support sentence | fallback supported vs not |
| operational_signal_supported | evidence operational-support sentence | actionable signal supported vs not |

## Canonical state C

C is never authored independently of Z.

Every C field is deterministically derived by the frozen parameter-free recomposer R from observable Z. The pre-training audit must independently reconstruct Z from current serialized input, independently recompute C, and verify exact identity with stored gold C.

| Field | Type | Observable source / derivation | Threshold | Deterministic baseline | Metric |
|---|---|---|---|---|---|
| C1.evidence_has_conflict | binary | Z4.conflict_present | no | yes | macro F1 component |
| C1.resolves_conflict | binary | conflict_present AND any explicit/implicit/correction resolution primitive | no | yes | macro F1 component |
| C1.asserts_numeric_threshold | binary | OR(EXACT, LOWER_BOUND, UPPER_BOUND) | no | yes | macro F1 component |
| C1.asserts_temporal_rule | binary | OR(EXACT_DURATION, APPROX_DURATION, PERIODIC_RULE, EXPIRY_RULE) | no | yes | macro F1 component |
| C1.asserts_fallback_policy | binary | OR three fallback primitives | no | yes | macro F1 component |
| C1.abstains | binary | Z1.ABSTAINS | no | yes | macro F1 component |
| C1.requests_clarification | binary | Z1.REQUESTS_CLARIFICATION | no | yes | macro F1 component |
| C1.has_operational_signal | binary | Z1.OPERATIONAL_SIGNAL | no | yes | macro F1 component |
| C2.evidence_scope | 8-way categorical | Z3 evidence_scope | no | yes | accuracy |
| C3.asserted_scope | 8-way categorical | Z3 asserted_scope | no | yes | accuracy |
| C4.scope_relation | 4-way categorical | Z3 scope_relation | no | yes | accuracy |
| C5.supersession_supported | binary | Z4 field | no | yes | macro F1 component |
| C5.scope_supported | binary | Z4 field | no | yes | macro F1 component |
| C5.numeric_value_supported | binary | Z4 field | no | yes | macro F1 component |
| C5.temporal_rule_supported | binary | Z4 field | no | yes | macro F1 component |
| C5.fallback_policy_supported | binary | Z4 field | no | yes | macro F1 component |
| C5.operational_signal_supported | binary | Z4 field | no | yes | macro F1 component |

## Admission proof required after materialization

The registry is specification evidence only.

Observable-identifiability PASS additionally requires the materialized audit to prove:

1. 100% of both surface realizations independently reconstruct the complete stored Z from `input_text` only;
2. independent C recomposition equals stored C for 100% of surfaces;
3. both surface realizations of each scene reconstruct the same Z and C;
4. no excluded/ambiguous primary scene exists;
5. no future/counterfactual/hidden metadata is read by the independent parser.

Failure blocks tokenizer fitting and training.
