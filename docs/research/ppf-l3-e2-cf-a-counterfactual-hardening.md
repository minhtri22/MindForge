# PPF-L3 E2-CF.A Counterfactual Contract Hardening

Status: **PASS**

E2-CF.A resolves the independent-review finding that the original E2 counterfactual checker was too permissive. The DEV dataset itself was not rerolled, replaced, or expanded. The correction is limited to the counterfactual contract checker, mutation tests, QA reporting, and research documentation.

## Provenance

| Field | Value |
| --- | --- |
| Starting commit | `8f44b55b7cd39d21fd33183e3408ff05ae390b46` |
| Benchmark version | `ppf-l3-benchmark/v1` |
| Generator/tool version | `ppf-l3-e2-generator/1` |
| Counterfactual contract version | `ppf-l3-e2-counterfactual-contract/2` |
| Master seed | `mindforge-ppf-l3-e2-dev-v1` |
| Reroll count | `0` |
| DEV histories | `38` |
| Validation generated | `NO` |
| Final generated | `NO` |
| Recognizer implemented | `NO` |
| L4 started | `NO` |

## Independent-review finding

Original E2-G6 was treated as **REVISE** for this closure task. The prior checker allowed broad changed roots such as `records`, `behavior`, `opportunities`, and `expected_answers`, then accepted a pair when at least one diff existed and no diff escaped those broad roots. That could miss two important failures:

1. an undeclared semantic change inside a broad allowed root, such as `records[*].context.period`;
2. a missing controlled difference, such as a permission-loss pair that no longer contains permission-loss semantics.

## Hardened checker

Each of the 14 frozen pair templates now has a declarative machine-enforced contract containing:

| Contract field | Meaning |
| --- | --- |
| `held_constant_paths` | semantic paths that must not change across arms |
| `allowed_changed_paths` | exact wildcard-aware paths where changes may occur |
| `required_changed_paths` | exact wildcard-aware paths that must actually change |
| semantic relation checks | pair-specific truth, behavior, observation, answer, and lineage checks |

The PASS rule is now:

```text
held_constant_violations == []
AND unexpected_changed_paths == []
AND missing_required_changes == []
AND all semantic_relation_checks == true
```

This replaces the old `bool(diffs) and not unexpected` sufficiency rule.

## Normalization policy

Normalization still removes non-semantic identity noise: opaque event IDs, source event IDs, opportunity IDs, relation target IDs, exact timestamps, and concrete input event references. It keeps semantic content such as event type, evidence kind, observability, opportunity state and alternatives, context values, quality, payload, provenance procedure state, relation type, lifecycle controls, and expected answers.

During hardening, raw list diffing exposed a legitimate insertion issue: same-origin, independent-corroboration, and derived-lineage pairs insert evidence records after the first base event, which makes a raw ordered list compare look like the remaining base records changed. The final checker normalizes visible records by semantic role:

```text
base_records
evidence_records
control_records
```

This preserves detection of undeclared base-record context changes while preventing valid evidence/control insertion from producing index-shift noise.

## Contract summary

| Pair | Template | Required controlled difference | Primary held constants |
| --- | --- | --- | --- |
| CF-01 | full observability vs permission loss | observation policy, observability state, opportunity observability, quality coverage, expected answers | truth, opportunities, behavior |
| CF-02 | normal quality vs degraded quality | quality state, coverage state, expected answers | truth, opportunities, behavior |
| CF-03 | single evidence vs same-origin replicas | added same-origin evidence lineage | truth, opportunities, behavior, base records, expected answers |
| CF-04 | true routine vs chance NO_PATTERN | truth kind, behavior, payload/action evidence, expected answers | scope, opportunities, observation policy |
| CF-05 | stable behavior vs fake drift | observation coverage collapse and lifecycle answer change | truth, opportunities, behavior |
| CF-06 | true drift vs observation-only change | true drift arm vs stable latent behavior plus observation-only degradation | scope, opportunities |
| CF-07 | meaningful alternatives vs constrained availability | alternatives removed from opportunities and visible records | behavior, scope, observation policy |
| CF-08 | conditional truth vs misleading aggregate | conditional truth vs no-global pattern with conflicting answer | scope, opportunities, observation policy |
| CF-09 | stable exception vs random deviation | scoped-exception truth vs random-deviation behavior | scope, opportunities, observation policy |
| CF-10 | correction absent vs correction applied | `CORRECTS` control and `USER_REJECTED` answer | truth, opportunities, behavior, base records |
| CF-11 | deletion absent vs deletion applied | `DELETES` control and `DELETED` answer | truth, opportunities, behavior, base records |
| CF-12 | known relationship vs unknown relationship | relationship context hidden and `UNKNOWN_CONTEXT` answer | truth, behavior, scope, observation policy |
| CF-13 | raw only vs raw plus derived lineage | `DERIVED_OBSERVATION`, `DERIVED_FROM`, and input refs | truth, opportunities, behavior, base records, expected answers |
| CF-14 | independent corroboration vs same-origin replication | `INDEPENDENT_CORROBORATION` vs `SAME_ORIGIN_REPLICATED` relation | truth, opportunities, behavior, base records, expected answers |

## Mutation tests

All required mutation tests directly mutate checker inputs and expect the hardened checker to reject them.

| Mutation | Expected rejection reason | Result |
| --- | --- | --- |
| M1 undeclared `truth_kind` change | held/undeclared truth path changes | PASS |
| M2 undeclared opportunity context change | unexpected opportunity context path | PASS |
| M3 hidden behavior flip | behavior semantic relation fails | PASS |
| M4 unrelated record context-period change | unexpected `base_records[0].context.period.value` | PASS |
| M5 remove CF-01 permission-loss semantics | missing required observation/permission changes | PASS |
| M6 remove CF-03 `SAME_ORIGIN_REPLICATED` | missing evidence relation and semantic check fails | PASS |
| M7 remove CF-10 correction relation | correction semantic checks fail | PASS |
| M8 remove CF-13 derived lineage | derived-lineage semantic checks fail | PASS |
| M9 replace CF-14 independent relation with same-origin | CF-14 relation semantic checks fail | PASS |

Undeclared-change mutation tests: **4 / 4 PASS**.

Missing-controlled-change mutation tests: **5 / 5 PASS**.

## DEV pair results

The existing canonical DEV split passes the hardened checker without changing generated histories, truth, expected answers, checkpoints, seeds, or case IDs.

| Item | Result |
| --- | ---: |
| Current DEV pairs under hardened checker | 14 / 14 PASS |
| Held-constant violations | 0 |
| Unexpected changed paths | 0 |
| Missing required changes | 0 |

## Dataset immutability

Baseline hashes were captured before checker changes for:

```text
dev_scenario_registry.json
dev_manifest.json
public_benchmark_manifest.json
38 history.json files
38 checkpoints.json files
38 evaluator truth files
38 expected-answer files
```

After revalidation:

| Item | Result |
| --- | --- |
| Baseline canonical artifact count | 155 |
| Current canonical artifact count | 155 |
| Changed canonical artifacts | 0 |
| Missing canonical artifacts | 0 |
| Added canonical artifacts | 0 |
| Canonical DEV artifacts unchanged | YES |
| Master seed unchanged | YES |
| Seed registry unchanged | YES |
| Case registry unchanged | YES |
| Reroll count | 0 |

Only QA/report/contract metadata changed. The canonical method-visible histories and evaluator DEV truth remain byte-identical to the pre-hardening baseline.

## Regression evidence

Fresh regression was run after the hardened checker was integrated:

```text
Frozen L2 fixture corpus: 60/60 PASS
L2 negative tests:        8/8 PASS
E0:                       PASS
E1:                       PASS
E2:                       PASS, all E2-G1..E2-G18 PASS
Focused CF tests:         5/5 PASS
```

## E2-CF.A gates

| Gate | Result |
| --- | --- |
| CF-G1 14 declarative contracts | PASS |
| CF-G2 held constants machine-enforced | PASS |
| CF-G3 required controlled differences enforced | PASS |
| CF-G4 undeclared differences rejected | PASS |
| CF-G5 missing-control mutations rejected | PASS |
| CF-G6 current 14 DEV pairs pass hardened checker | PASS |
| CF-G7 canonical histories unchanged | PASS |
| CF-G8 seed registry unchanged | PASS |
| CF-G9 reroll remains zero | PASS |
| CF-G10 L2 regression | PASS |
| CF-G11 E0/E1 regression | PASS |
| CF-G12 E2 non-G6 regression | PASS |

## Final recommendation

E2-CF.A is **PASS**. Original E2-G6 was correctly reopened as **REVISE** for checker weakness, and the hardened E2-G6 is now **PASS** with declarative contracts, direct mutation rejection, 14/14 current DEV pair pass, and unchanged canonical DEV artifacts.

PPF-L3 E2 final state remains:

```text
PASS / DEV DATASET FROZEN
```

E3 Validation is the next candidate stage, but it is **not authorized by this task**. No validation, final, recognizer, L4, Model, Kernel, plugin-production, or Host work was started.
