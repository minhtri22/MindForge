# PPF-L3 E3 Validation Generation

Status: **PASS / VALIDATION DATASET FROZEN**

E3 generated the canonical VALIDATION split for `ppf-l3-benchmark/v1` after E2 DEV and E2-CF.A were frozen. Scope remained research tooling, validation benchmark artifacts, evaluator validation truth, QA, and research documentation only. No FINAL, recognizer, L4, L5, Model, Kernel, plugin-production, or Host work was introduced.

## Provenance

| Field | Value |
| --- | --- |
| Starting commit | `a6f2f630d42cc62c48d2b170cc76797656bf7ef7` |
| Benchmark version | `ppf-l3-benchmark/v1` |
| Generator/tool version | `ppf-l3-e3-generator/1` |
| Validation master seed | `mindforge-ppf-l3-e3-validation-v1` |
| DEV master seed | `mindforge-ppf-l3-e2-dev-v1` |
| Reroll count | `0` |
| Split generated | `VALIDATION` |
| Final generated | `NO` |
| Recognizer implemented | `NO` |
| L4 started | `NO` |

Generation order was frozen and executed as:

```text
PREREGISTER 38 validation histories/evaluation units
-> WRITE validation_scenario_registry.json
-> READ/HASH registry
-> GENERATE ONCE from validation namespace seed tuples
-> RETAIN ALL 38 histories
```

## Entry Gates

Pre-E3 entry checks passed before canonical validation artifacts were created:

```text
Frozen L2 fixture corpus: 60/60 PASS
L2 negative tests:        8/8 PASS
E0:                       PASS
E1:                       PASS
E2:                       PASS
E2-CF.A:                  PASS, 14/14 DEV pairs and M1-M9 mutation rejection
DEV canonical artifacts:  155 captured before E3
DEV reroll count:         0
```

## Validation Allocation

| Item | Count |
| --- | ---: |
| Synthetic persons | 6 |
| Truth configurations | 7 |
| STANDARD truth configurations | 5 |
| HIGH-RISK truth configurations | 2 |
| Histories/cases | 38 |
| STANDARD histories | 20 |
| HIGH-RISK histories | 18 |
| Visible L2 events | 1,298 |
| L2-valid visible events | 1,298 / 1,298 |
| Checkpoints | 207 |
| Evaluation units | 207 |
| Counterfactual pair instances | 14 |
| Paired histories | 28 |
| Counterfactual templates covered | 14 / 14 |
| Preregistered false-promotion denominator | 148 |

Replication arithmetic:

```text
STANDARD: 5 configs x 2 behavior seeds x 2 observation seeds = 20 histories
HIGH-RISK: 2 configs x 3 behavior seeds x 3 observation seeds = 18 histories
TOTAL: 38 histories
```

History regimes:

| Regime | Histories |
| --- | ---: |
| SHORT | 9 |
| MEDIUM | 16 |
| LONG | 13 |

## Protected Split Disjointness

VALIDATION uses a distinct protected split namespace, new person keys, new truth-configuration IDs, new history IDs, new case IDs, and a validation-specific master seed.

| Overlap Check | Count |
| --- | ---: |
| DEV person overlap | 0 |
| DEV truth-config overlap | 0 |
| DEV history overlap | 0 |
| DEV case-ID overlap | 0 |

The validation configs intentionally share frozen semantic families with DEV while changing concrete structure: person keys, config IDs, opportunity counts, occurrence plans, available alternatives, scope strings, and high-risk construction lengths differ from DEV.

## Counterfactual Coverage

All 14 frozen templates have one validation pair instance and pass the frozen E2-CF.A hardened checker unchanged.

| Item | Result |
| --- | ---: |
| Pair contracts passing | 14 / 14 |
| Held-constant violations | 0 |
| Unexpected changed paths | 0 |
| Missing required changes | 0 |

The validation split covers full observability vs permission loss, degraded quality, same-origin replication, true routine vs NO_PATTERN, fake drift, true drift vs observation-only change, constrained availability, misleading aggregate, scoped exception vs random deviation, correction, deletion, hidden relationship identity, raw plus derived lineage, and independent corroboration vs same-origin replication.

## Family Coverage

Required validation families pass: routine, preference, conditional/context-dependent truth, relationship-conditioned behavior, temporal sequence/association, exception, drift, reversal, NO_PATTERN, insufficient/conflicting support, observability loss, quality degradation, same-origin replication, independent corroboration, correction/rejection, deletion/reset, unknown relationship, raw/derived evidence, confounding/misleading aggregate, and fake drift.

## Identifiability And Negative Denominator

| Identifiability | Evaluation units |
| --- | ---: |
| YES | 144 |
| PARTIAL | 54 |
| NO | 9 |

All three identifiability classes are represented. `NO` identifiability does not receive active `SUPPORTED` answers.

The negative denominator was preregistered before validation generation and exactly matches generated evaluation units:

```text
negative-denominator units: 148
```

## Oracle, Checkpoint, Lifecycle, And Evidence QA

Checkpoint prefixes use `ingested_time`; future-leak violations are zero. Static oracle-boundary review found no recognizer-like count, confidence, probability, classifier, pattern score, ratio, or frequency admission threshold.

Lifecycle QA passes for correction, rejection, supersession, invalidation, deletion, reset, true drift, reversal, staleness, coverage-induced fake drift, and no passive resurrection after control events.

Evidence non-inflation QA passes:

```text
same-origin replica != new behavior
raw-derived evidence != new behavior
independent corroboration != same-origin replication
unknown relationship remains unknown
```

Truth leakage in method-visible validation artifacts is zero.

## DEV Immutability

E3 captured DEV hashes before validation generation and compared them after writing validation artifacts.

| Item | Result |
| --- | --- |
| Baseline DEV artifact count | 155 |
| Current DEV artifact count | 155 |
| Changed DEV artifacts | 0 |
| Missing DEV artifacts | 0 |
| Added DEV artifacts | 0 |
| Canonical DEV unchanged | YES |
| DEV master seed unchanged | YES |
| DEV registry unchanged | YES |
| DEV case registry unchanged | YES |

No canonical DEV history, checkpoint request, evaluator truth, expected-answer file, DEV registry, DEV manifest, or public DEV manifest changed.

## Failed Intermediate Attempt

A pre-artifact dry run on a temporary root initially returned **REVISE** only for E3-G18 because the E3 regression harness checked the E2-CF.A report file inside the temporary root. Temporary E2 generation writes that report without the repository-level DEV hash comparison, so the report file was not a suitable regression oracle in temp. The fix changed E3-G18 to execute the frozen E2-CF.A pair checker and mutation harness directly. No validation truth configuration, seed, pair assignment, oracle answer, generated history, or counterfactual contract was changed.

The subsequent dry run and canonical workspace run both passed all gates.

## Regression Evidence

Fresh local regression evidence after E3 implementation:

```text
Frozen L2 fixture corpus: 60/60 PASS
L2 negative tests:        8/8 PASS
E0:                       PASS
E1:                       PASS
E2:                       PASS
E2-CF.A:                  PASS
E3 focused tests:         6/6 PASS
PPF-L3 test suite:        PASS
```

## E3 Gates

| Gate | Result |
| --- | --- |
| E3-G1 exact allocation | PASS |
| E3-G2 replication correctness | PASS |
| E3-G3 protected split disjointness | PASS |
| E3-G4 full L2 validity | PASS |
| E3-G5 mandatory family coverage | PASS |
| E3-G6 counterfactual template coverage | PASS |
| E3-G7 hardened pair contracts | PASS |
| E3-G8 seed isolation | PASS |
| E3-G9 checkpoint correctness | PASS |
| E3-G10 oracle boundary | PASS |
| E3-G11 identifiability | PASS |
| E3-G12 negative denominator | PASS |
| E3-G13 lifecycle correctness | PASS |
| E3-G14 evidence non-inflation | PASS |
| E3-G15 no cherry-picking | PASS |
| E3-G16 truth leakage | PASS |
| E3-G17 DEV immutability | PASS |
| E3-G18 full regression | PASS |
| E3-G19 validation-only scope | PASS |

## Artifact Boundary

Validation method-visible artifacts are under:

```text
benchmarks/ppf_l3/generated/validation/cases/<opaque-case-id>/
  history.json
  checkpoints.json
```

Validation evaluator artifacts are under:

```text
benchmarks/ppf_l3/evaluator/validation/
  truth/
  expected/
```

Validation registry, manifests, and reports are under:

```text
benchmarks/ppf_l3/specs/validation_scenario_registry.json
benchmarks/ppf_l3/manifests/validation_manifest.json
benchmarks/ppf_l3/manifests/validation_public_manifest.json
benchmarks/ppf_l3/reports/validation_generator_qa.json
benchmarks/ppf_l3/reports/validation_dataset_summary.json
```

No `generated/final/` or `evaluator/final/` artifact was created.

## Scientific Recommendation

E3 is **PASS / VALIDATION DATASET FROZEN**. The frozen generator foundation, oracle, L2 validation bridge, seed-isolation rules, and E2-CF.A counterfactual contracts generalized from DEV to a protected validation split with new persons/configurations, zero DEV overlap, zero rerolls, and unchanged DEV artifacts.

L3-E4 FINAL TEST Generation is the next candidate stage, but it is **not authorized by this task**. Do not generate FINAL, implement a recognizer, or begin L4 from this artifact.
