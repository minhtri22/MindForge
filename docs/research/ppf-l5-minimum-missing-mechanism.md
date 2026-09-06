# PPF-L5 — Minimum Missing Mechanism

Starting commit: `18dc5332e73d673e245baa365a173f169c2ee412`

Research status: **PASS — MINIMUM_MECHANISM_FOUND** on DEV + protected one-shot VALIDATION.

Confirmatory status: **NOT YET CONFIRMED ON A NEW BLIND HOLDOUT**.

## Scientific question

L5 asks for the smallest symbolic addition that causally improves the strongest L4 trivial baseline without turning into a full recognizer. L4 established B9 (Lifecycle-Naive Rule) as the strongest exact-state trivial baseline while leaving large observability, unknown-context, conflict, and staleness failure clusters.

The preregistered hypothesis was therefore a **Semantic Evidence Eligibility / Semantic Admissibility Gate** placed before frozen B9. The gate does not learn a personal pattern. It only decides whether currently visible evidence is eligible to sustain an active `SUPPORTED` claim.

## Why evidence eligibility was tested first

B9 already preserves explicit lifecycle dominance: correction and deletion do not resurrect an active claim. Its remaining failures are mainly cases where visible evidence exists but should not currently authorize promotion. This made admissibility a smaller causal hypothesis than replacing recurrence logic, adding a learned scorer, or introducing a richer recognizer.

The experiment remained Research & Tooling only. No Model, Kernel, host, production plugin, training, weight, or inference-contract changes were made.

## Preregistration and information boundary

Treatment registry was fixed before VALIDATION:

| Treatment | Components |
| --- | --- |
| T0 | frozen B9 control |
| T1 | E1 Observability Eligibility |
| T2 | E2 Context Eligibility |
| T3 | E3 Conflict Eligibility |
| T4 | E4 Currentness/Staleness Eligibility |
| T5 | E1 + E2 |
| T6 | E1 + E2 + E3 |
| T7 | E1 + E2 + E3 + E4 |

The selection rule was frozen before VALIDATION: a candidate had to improve exact state and false promotion on both DEV and VALIDATION, preserve `SUPPORTED` recall, preserve correction/deletion invariants, strictly improve at least one targeted hard-failure class, and worsen no untargeted hard-failure class. Qualifying treatments were ordered by fewest components, then lower VALIDATION false promotion, higher VALIDATION exact state, fewer hard violations, and deterministic treatment ID.

Mechanism inputs are limited to method-visible `history.json` and `checkpoints.json` fields. Truth kind, expected answer, identifiability, family labels, pair membership/arm, risk class, hidden lifecycle labels, holdout labels, and evaluator-private metadata are forbidden mechanism inputs.

The freeze-recorded preregistration content hash is `59ae47ad592e0c03a87e3564561533a0f10e7a5b0e70595d3c7dc772edf5f605`. The mechanism lock records the canonical hash of the completed preregistration artifact as `78037590d977c3931b023a5b284f320d47ad2807c06d5a03392a5dbfb595dd15`. Source hashes frozen before VALIDATION are:

- mechanism: `2d42bf29dfd890e8a2ae8e4b61c1c9a2522c7a36aa0e70dbee8b34d8954f1aa6`
- evaluator: `ca5635ac32332aaae0823e78f845f7095ac048a5fb738444ff4289bcd95e7749`
- runner: `98bd07c50983cf4562b1c2f1113146bf71fca93808c5812a3fc943d1ba2ad938`
- frozen DEV result: `30be9f0d984d900e9e14af1adc3811e7685448afeb8fd811d0a76f1fc7e996d3`

VALIDATION semantic run count is exactly **1**. Its canonical result hash is `d193aeccd5294382efd3048d72528fc6a7f18267bdd7c87e7d516002cec2a1e1`.

## Mechanism complexity ledger

All components are deterministic and have zero learned parameters.

| Component | Purpose | Main visible fields | State retained | Learned parameters |
| --- | --- | --- | ---: | ---: |
| E1 | block active support when current observability is explicitly unavailable/missing/delayed/unknown | `event_type`, `observability.state`, `opportunity.state` | 0 | 0 |
| E2 | block a context-specific promotion when required context remains explicitly unknown | `opportunity.state`, `context.*.status` | 0 | 0 |
| E3 | block only explicit frozen conflict semantics | `opportunity.id`, `opportunity.state`, `context.*.status` | 0 | 0 |
| E4 | block only explicit currentness loss; no fitted age threshold | `event_type`, `observability.state`, `opportunity.state` | 0 | 0 |

Lifecycle controls retain precedence. Eligibility gates only intercept a B9 `SUPPORTED` promotion; they do not invent a new state when B9 already abstains.

## DEV results

| T | Exact | Precision proxy | Recall proxy | FDR | False promotion | Negative exact | Lifecycle exact | NO-as-current | UNKNOWN+ | Conflict+ | Stale-current | Corr resurrect | Deleted return |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T0 | 0.739130 | 0.533333 | 0.949153 | 0.466667 | 0.331081 | 0.655405 | 0.892857 | 4 | 4 | 0 | 3 | 0 | 0 |
| T1 | 0.758454 | 0.565657 | 0.949153 | 0.434343 | 0.290541 | 0.682432 | 0.892857 | 0 | 4 | 0 | 1 | 0 | 0 |
| T2 | 0.758454 | 0.554455 | 0.949153 | 0.445545 | 0.304054 | 0.682432 | 0.892857 | 4 | 0 | 0 | 3 | 0 | 0 |
| T3 | 0.739130 | 0.533333 | 0.949153 | 0.466667 | 0.331081 | 0.655405 | 0.892857 | 4 | 4 | 0 | 3 | 0 | 0 |
| T4 | 0.739130 | 0.533333 | 0.949153 | 0.466667 | 0.331081 | 0.655405 | 0.892857 | 4 | 4 | 0 | 3 | 0 | 0 |
| T5 | 0.777778 | 0.589474 | 0.949153 | 0.410526 | 0.263514 | 0.709459 | 0.892857 | 0 | 0 | 0 | 1 | 0 | 0 |
| T6 | 0.777778 | 0.589474 | 0.949153 | 0.410526 | 0.263514 | 0.709459 | 0.892857 | 0 | 0 | 0 | 1 | 0 | 0 |
| T7 | 0.777778 | 0.589474 | 0.949153 | 0.410526 | 0.263514 | 0.709459 | 0.892857 | 0 | 0 | 0 | 1 | 0 | 0 |

T0 exactly reproduced committed L4 B9 on DEV for the frozen metric projection.

## VALIDATION results

| T | Exact | Precision proxy | Recall proxy | FDR | False promotion | Negative exact | Lifecycle exact | NO-as-current | UNKNOWN+ | Conflict+ | Stale-current | Corr resurrect | Deleted return |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T0 | 0.753623 | 0.542857 | 0.966102 | 0.457143 | 0.324324 | 0.668919 | 0.892857 | 4 | 4 | 1 | 3 | 0 | 0 |
| T1 | 0.772947 | 0.575758 | 0.966102 | 0.424242 | 0.283784 | 0.695946 | 0.892857 | 0 | 4 | 1 | 1 | 0 | 0 |
| T2 | 0.772947 | 0.564356 | 0.966102 | 0.435644 | 0.297297 | 0.695946 | 0.892857 | 4 | 0 | 1 | 3 | 0 | 0 |
| T3 | 0.753623 | 0.542857 | 0.966102 | 0.457143 | 0.324324 | 0.668919 | 0.892857 | 4 | 4 | 1 | 3 | 0 | 0 |
| T4 | 0.753623 | 0.542857 | 0.966102 | 0.457143 | 0.324324 | 0.668919 | 0.892857 | 4 | 4 | 1 | 3 | 0 | 0 |
| T5 | 0.792271 | 0.600000 | 0.966102 | 0.400000 | 0.256757 | 0.722973 | 0.892857 | 0 | 0 | 1 | 1 | 0 | 0 |
| T6 | 0.792271 | 0.600000 | 0.966102 | 0.400000 | 0.256757 | 0.722973 | 0.892857 | 0 | 0 | 1 | 1 | 0 | 0 |
| T7 | 0.792271 | 0.600000 | 0.966102 | 0.400000 | 0.256757 | 0.722973 | 0.892857 | 0 | 0 | 1 | 1 | 0 | 0 |

T0 exactly reproduced committed L4 B9 on VALIDATION. No post-VALIDATION treatment redesign or semantic rerun occurred.

## Causal component findings

**Q1 — E1 Observability.** Yes. T1 reduced `NOT_OBSERVABLE`-as-current from 4→0 on both splits, with `SUPPORTED` recall unchanged. False promotion improved from 0.331081→0.290541 on DEV and 0.324324→0.283784 on VALIDATION. It also reduced stale-as-current from 3→1 because some stale controls share explicit observability/currentness-loss signals. This secondary effect is reported rather than reclassified as an E4 win.

**Q2 — E2 Context.** Yes. T2 reduced `UNKNOWN_CONTEXT` positive violations from 4→0 on both splits with recall unchanged. It independently qualifies as a one-component improvement, but its VALIDATION false promotion (0.297297) is worse than T1 (0.283784), so the preregistered tie-break selects T1.

**Q3 — E3 Conflict.** No measurable causal gain under the strict method-visible conflict signal used here. T3 equals T0 on DEV and VALIDATION. The remaining VALIDATION conflict-positive violation is 1.

**Q4 — E4 Currentness/Staleness.** No measurable causal gain under the explicit currentness-loss signal alone. T4 equals T0. A fitted time threshold was deliberately rejected: DEV showed overlapping recency between `STALE` and `SUPPORTED`, so an oracle-derived age cutoff would violate the intended minimum symbolic experiment.

**Q5 — Additivity.** E1 + E2 is additive: T5 removes both targeted clusters and reaches exact 0.777778 / 0.792271 with false promotion 0.263514 / 0.256757. T6 and T7 are identical to T5 because E3/E4 add no effective signal in these splits.

**Q6 — Smallest subset that dominates B9.** T1 and T2 both qualify with one component. The deterministic tie-break selects **T1 = E1 Observability Eligibility** because it has lower VALIDATION false promotion. T5/T6/T7 qualify but contain more components and therefore cannot be selected as the minimum.

**Q7 — Relationship to B8 safety frontier.** T1 does not dominate B8 on every metric. On DEV, B8 false promotion is 0.189189 versus T1 0.290541; on VALIDATION, B8 is 0.222973 versus T1 0.283784. T1 is much stronger on exact state (0.758454/0.772947 vs 0.671498/0.618357), recall (0.949153/0.966102 vs 0.610169/0.559322), and lifecycle safety (B8 lifecycle exact 0 with correction/deletion resurrection violations; T1 lifecycle exact 0.892857 with both resurrection counts zero). B8 therefore remains a lower-false-promotion Pareto frontier rather than being globally dominated.

## Counterfactual analysis

For selected T1, each split contains all 14 registered pair templates. On DEV and VALIDATION respectively, T1 distinguished 9/14 templates, had 2/14 templates in the evaluator's `correct_direction` summary, and left 5/14 unchanged. These results prevent interpreting the aggregate metric gain as full controlled semantic recognition. The complete per-template predictions and expected sequences remain in `dev-results.json` and `validation-results.json`.

The mechanism does improve the observability-controlled pairs by changing previously active promotions to the frozen abstention state where explicit observability is lost, but many other controlled distinctions remain unresolved.

## Identifiability analysis

Selected T1 slices:

| Split | Identifiability | Exact / units | Exact accuracy | Predicted SUPPORTED |
| --- | --- | ---: | ---: | ---: |
| DEV | YES | 116 / 144 | 0.805556 | 81 |
| DEV | PARTIAL | 39 / 54 | 0.722222 | 13 |
| DEV | NO | 2 / 9 | 0.222222 | 5 |
| VALIDATION | YES | 114 / 144 | 0.791667 | 85 |
| VALIDATION | PARTIAL | 44 / 54 | 0.814815 | 9 |
| VALIDATION | NO | 2 / 9 | 0.222222 | 5 |

E1 improves abstention in some partially identifiable observability cases, but `NO` remains weak. This is direct negative evidence against interpreting T1 as a complete recognizer.

## Lifecycle preservation

For T1 on both DEV and VALIDATION:

- correction resurrection = 0
- deleted active return = 0
- `SUPPORTED` recall is unchanged from T0
- lifecycle exact accuracy remains 0.892857

The selected mechanism therefore preserves the B9 lifecycle gain and does not obtain its improvement by collapsing toward Always Abstain.

## Mechanism selection and lock

Qualifying treatments: **T1, T2, T5, T6, T7**.

Selected minimum treatment: **T1**.

Selected component: **E1 — Observability Eligibility**.

Component count: **1**.

Learned parameters: **0**.

Mechanism lock canonical SHA-256: `092cb0bb367eac49284f377d1f7e3cfba425edf1f5298136bf8068dbe7cd4e70`.

## Remaining unsolved dimensions

T1 leaves several material clusters unresolved:

1. `UNKNOWN_CONTEXT` active promotion remains 4 on DEV and 4 on VALIDATION. E2 causally repairs this, but it is a second component and therefore is not the selected minimum.
2. conflict handling remains unresolved under the strict explicit signal; VALIDATION still has 1 conflict-positive violation.
3. explicit staleness/currentness is only partially improved through E1 overlap; one stale-as-current violation remains on each split.
4. counterfactual controlled-direction performance remains weak.
5. identifiability=`NO` remains poor.
6. compositional context, provenance semantics, and richer personal-pattern recognition remain outside L5.

These are the dimensions a later mechanism must address if future research proceeds.

## FINAL prohibition and confirmatory limitation

**L3 FINAL was not used for any L5 treatment evaluation. No L5 FINAL predictions or `final-results.json` were created.** L3 FINAL was already consumed by L4 and is scientifically spent for L5 mechanism discovery.

Accordingly, the allowed conclusion is limited to: **a minimum symbolic mechanism was identified that causally improves the frozen L4 B9 baseline on DEV and protected one-shot VALIDATION.** This is not proof that PPF works in production and is not blind confirmatory evidence.

Any confirmatory continuation requires a new protected blind experiment/split or an explicit decision to keep L5 exploratory. That continuation is outside this task.

## Regression and integrity evidence

Pre-L5 regression:

- L2 fixtures: 60/60 PASS
- L2 negatives: 8/8 PASS
- L4 focused tests: 6/6 PASS before L5 work
- frozen L3 snapshot regression: 50 PASS / 5 FAIL, where all five failures are historical phase-scope guards that intentionally reject later L4/L5 paths; no semantic/data regression was identified and the old guards were not modified

L5 focused tests directly cover the exact T0–T7 registry, B9 delegation, E1/E2/E3/E4 behavior, lifecycle dominance, private-field rejection, FINAL refusal, and deterministic minimum-component selection.

Frozen canonical trees at starting HEAD:

- `benchmarks/ppf_l3/`: `8c99caccda8cedeb21ad32475015876f2d775b1d`
- `docs/research/data/ppf-l4/`: `5c87ddceef18d7b09f1eaaf7dbb038afba29fc37`

No L3 or committed L4 evidence files were modified during L5.

## L5 gates

| Gate | Result | Evidence |
| --- | --- | --- |
| L5-G1 | PASS | frozen L3 unchanged |
| L5-G2 | PASS | committed L4 evidence unchanged |
| L5-G3 | PASS | T0 exactly reproduces B9 on DEV and VALIDATION |
| L5-G4 | PASS | T0–T7 fixed before VALIDATION |
| L5-G5 | PASS | learned parameters = 0 |
| L5-G6 | PASS | mechanism reads method-visible inputs only; private fields rejected |
| L5-G7 | PASS | DEV used for implementation/debugging only |
| L5-G8 | PASS | VALIDATION semantic run count = 1 after freeze |
| L5-G9 | PASS | deterministic selection policy preregistered |
| L5-G10 | PASS | correction/deletion lifecycle invariants preserved |
| L5-G11 | PASS | `SUPPORTED` recall preserved; no Always-Abstain collapse |
| L5-G12 | PASS | all 14 pair templates reported per treatment/split |
| L5-G13 | PASS | YES/PARTIAL/NO identifiability slices reported |
| L5-G14 | PASS | minimum-component selection chose T1 |
| L5-G15 | PASS | L3 FINAL not used by L5 |
| L5-G16 | PASS | no Model/Kernel/production change |
| L5-G17 | PASS | research ledger updated in this completion commit |
| L5-G18 | PASS WITH HISTORICAL-GUARD NOTE | valid semantic/data regression preserved; old L3 post-phase guards remain expected failures |

## Research verdict

**PASS — MINIMUM_MECHANISM_FOUND.**

The minimum causal addition in the preregistered ladder is **T1 / E1 Observability Eligibility**. It improves exact semantic state and false promotion on both DEV and one-shot VALIDATION, removes the targeted `NOT_OBSERVABLE` false-promotion cluster, preserves positive recall, and preserves B9 lifecycle invariants.

This result establishes a stronger research floor; it does not establish a production PPF design.

Next scientific candidate: a decision on a **new protected blind confirmatory experiment/split**. No further stage is authorized by this task.
