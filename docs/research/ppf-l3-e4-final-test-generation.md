# PPF-L3 E4 Final Test Generation

Status: **PASS / FINAL TEST DATASET FROZEN**

E4 materializes the protected FINAL TEST split for `ppf-l3-benchmark/v1`. It is the last L3 dataset-generation stage. It does not implement a recognizer, baseline, Model change, Kernel change, production plugin, host integration, training path, L4 work, or L5 work.

## Provenance

| Field | Value |
| --- | --- |
| Starting commit | `d39ee271c8925d6dd5126e74a6e73439f0029f7d` |
| Generator/tool | `ppf-l3-e4-generator/1` |
| Benchmark version | `ppf-l3-benchmark/v1` |
| FINAL master seed | `mindforge-ppf-l3-e4-final-v1` |
| Split namespace | `final` |
| Registry | `benchmarks/ppf_l3/specs/final_scenario_registry.json` |
| Method-visible root | `benchmarks/ppf_l3/generated/final/` |
| Evaluator-only root | `benchmarks/ppf_l3/evaluator_private/final/` |
| Reroll count | `0` |

## Scientific Order

E4 follows the preregistration order required by the frozen execution plan:

```text
construct complete FINAL registry
write registry
read/hash registry
generate exactly registered cases once
retain all cases
write method-visible histories/checkpoints
write evaluator-private truth/expected answers
write manifests and QA reports
```

The registry was written and hashed before generation. E4 generated 112 histories and retained 112 histories with no replacements and no seed rerolls.

## Entry Gates

Before FINAL artifacts were created, the task verified the frozen foundation:

| Gate | Result |
| --- | --- |
| L2 frozen fixtures | 60 / 60 PASS |
| L2 negative tests | 8 / 8 PASS |
| PPF-L3 test suite before FINAL | 55 passed |
| FINAL artifacts present before generation | NO |

E4 also reruns E0, E1, E2, E2-CF.A, and E3 in its regression QA. E3 is run in a temporary benchmark root after E4 exists so the frozen E3 “no final artifacts” scope gate remains meaningful.

## FINAL Allocation

| Metric | Count |
| --- | ---: |
| Synthetic persons | 18 |
| Truth configurations | 18 |
| STANDARD configs | 10 |
| HIGH-RISK configs | 8 |
| Histories | 112 |
| STANDARD histories | 40 |
| HIGH-RISK histories | 72 |
| Visible L2 events | 3,980 |
| L2-valid visible events | 3,980 |
| Checkpoints | 616 |
| Evaluation units | 616 |

Replication arithmetic:

```text
STANDARD: 10 configs × 2 behavior seeds × 2 observation seeds = 40 histories
HIGH-RISK: 8 configs × 3 behavior seeds × 3 observation seeds = 72 histories
TOTAL: 112 histories
```

## History Regimes

| Regime | Histories |
| --- | ---: |
| SHORT | 22 |
| MEDIUM | 42 |
| LONG | 48 |

## Structural Holdouts

E4 preregisters four structural holdout configurations, exceeding the minimum of three:

| Truth config | Holdout rationale |
| --- | --- |
| `final-h02` | Drift/reversal plus partial observability and derived evidence pressure in one high-risk final-only configuration |
| `final-h04` | Exception and overlapping-pattern conflict combined under a distinct final-only context-action structure |
| `final-h07` | Simpson-like aggregate trap combined with scoped exception and conditional preference pressure |
| `final-h08` | Stacked correction/deletion/reset lifecycle with drift/reversal pressure in final-only order |

These are final-only compositions inside the frozen L1/L2/L3 semantics. No new semantic category is introduced.

## Split Disjointness

| Overlap | Count |
| --- | ---: |
| FINAL vs DEV persons | 0 |
| FINAL vs VALIDATION persons | 0 |
| FINAL vs DEV truth configs | 0 |
| FINAL vs VALIDATION truth configs | 0 |
| FINAL vs DEV case IDs | 0 |
| FINAL vs VALIDATION case IDs | 0 |
| Canonical history identity overlap | 0 |

History-level disjointness uses a derived canonical identity over split, person ID, truth config ID, behavior replica, observation replica, and case seed identity. DEV and VALIDATION registries were not mutated to add new fields.

## Counterfactual Coverage

| Metric | Count |
| --- | ---: |
| Counterfactual templates represented | 14 / 14 |
| Pair instances | 14 |
| Paired histories | 28 |
| Pair contracts passing | 14 / 14 |
| Held-constant violations | 0 |
| Unexpected changed paths | 0 |
| Missing required changes | 0 |

E4 reuses the frozen E2-CF.A pair contracts unchanged.

## Family Coverage

E4 covers the required FINAL families: routine, preference, conditional preference, relationship-conditioned behavior, temporal sequence, context-action association, exception, drift, reversal, NO_PATTERN, insufficient support, conflicting structure, observability loss, quality degradation, same-origin replication, independent corroboration, raw/derived evidence, correction/rejection, deletion/reset, unknown relationship, confounding/misleading aggregate, fake drift, staleness, and pattern overlap.

## Identifiability and Negative Denominator

| Identifiability | Evaluation units |
| --- | ---: |
| YES | 318 |
| PARTIAL | 167 |
| NO | 131 |

Negative-denominator units: **467**.

All `NO` identifiability units avoid active `SUPPORTED` answers. The negative denominator is preregistered in `final_scenario_registry.json` and reconciles exactly with generated checkpoint answers.

## Oracle, Lifecycle, and Evidence QA

| Check | Result |
| --- | --- |
| L2 validation | 3,980 / 3,980 PASS |
| Checkpoint future leaks | 0 |
| Truth leaks in method-visible artifacts | 0 |
| Oracle freeze / no recognizer-like threshold | PASS |
| Correction/rejection lifecycle | PASS |
| Deletion/reset lifecycle | PASS |
| Supersession/invalidation lifecycle | PASS |
| True drift latent transition | PASS |
| Reversal latent transition | PASS |
| Fake drift has no latent behavior transition | PASS |
| Same-origin occurrence inflation | PASS |
| Raw-derived occurrence inflation | PASS |
| Independent vs same-origin evidence distinction | PASS |

## Seed Isolation

| Check | Result |
| --- | --- |
| Same full seed tuple is stable | PASS |
| Observation seed keeps truth/opportunity/behavior fixed | PASS |
| Behavior seed keeps truth/opportunity fixed | PASS |
| FINAL seed namespace independent from DEV/VALIDATION | PASS |

## Protected Artifact Immutability

| Frozen split | Canonical artifacts | Changed | Missing | Added | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| DEV | 155 | 0 | 0 | 0 | PASS |
| VALIDATION | 155 | 0 | 0 | 0 | PASS |

## FINAL Truth Protection

Method-visible FINAL artifacts are only:

```text
benchmarks/ppf_l3/generated/final/cases/<opaque-case-id>/history.json
benchmarks/ppf_l3/generated/final/cases/<opaque-case-id>/checkpoints.json
benchmarks/ppf_l3/manifests/final_public_manifest.json
```

Evaluator-only FINAL artifacts are under:

```text
benchmarks/ppf_l3/evaluator_private/final/truth/
benchmarks/ppf_l3/evaluator_private/final/expected/
benchmarks/ppf_l3/manifests/final_private_manifest.json
```

The public/method-visible FINAL payload contains no truth labels, expected answers, identifiability labels, family labels, risk classes, pair templates, pair arms, structural holdout labels, or seed semantics.

## E4 Gates

| Gate | Result |
| --- | --- |
| E4-G1 exact allocation | PASS |
| E4-G2 replication correctness | PASS |
| E4-G3 split disjointness | PASS |
| E4-G4 structural holdouts | PASS |
| E4-G5 full L2 validity | PASS |
| E4-G6 mandatory family coverage | PASS |
| E4-G7 counterfactual template coverage | PASS |
| E4-G8 hardened pair contracts | PASS |
| E4-G9 seed isolation | PASS |
| E4-G10 checkpoint correctness | PASS |
| E4-G11 oracle freeze | PASS |
| E4-G12 identifiability | PASS |
| E4-G13 negative denominator | PASS |
| E4-G14 lifecycle correctness | PASS |
| E4-G15 evidence non-inflation | PASS |
| E4-G16 no cherry-picking | PASS |
| E4-G17 truth leakage | PASS |
| E4-G18 DEV immutability | PASS |
| E4-G19 VALIDATION immutability | PASS |
| E4-G20 full regression | PASS |
| E4-G21 final-only scope | PASS |
| E4-G22 FINAL evaluator protection | PASS |

## Failed Attempts

No FINAL generation failure was retained. Before canonical FINAL materialization, a dry run exposed a wrapper-only preregistration mismatch: E4 initially prefixed checkpoint/evaluation-unit IDs with `final:` while the frozen E2 oracle produced IDs from the config/history tuple. The wrapper was corrected before any FINAL artifact was generated in the benchmark tree. No generator semantics, oracle semantics, pair contract, truth configuration, final seed, or final case was changed after observing final outcomes.

## Scientific Recommendation

E4 is **PASS / FINAL TEST DATASET FROZEN**. L3 dataset generation is now complete: DEV, VALIDATION, and FINAL are frozen, split-disjoint, L2-valid, and covered by hardened counterfactual contracts. This does not prove recognizer feasibility and does not authorize L4. The next candidate is **PPF-L4 — Minimal/Stupid Baselines**, pending ChatGPT review.
