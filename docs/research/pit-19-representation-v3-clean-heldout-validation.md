# PIT-19 Representation V3 Refinement + Clean Held-Out Reset

## 1. Motivation

PIT-19 tests whether a third deterministic semantic-representation refinement can preserve the strong known-regime recovery reached in PIT-18 while generalizing to a newly reset, genuinely pristine held-out distribution. The experiment is evidence-only: API calls, new teacher inference, training, distillation, and MindForge integration all remain zero/disabled.

## 2. PIT-18 Failure

PIT-18 Representation V2 passed PIT-15 regression but failed both its 40-sample representation HELD_OUT and PIT-16 FULL/PRISTINE held-out. Its final verdict was `REPRESENTATION_V2_INSUFFICIENT`. The remaining errors concentrated upstream in primitive extraction and scope handling; no independent Guardrail V3 policy defect was established.

## 3. Held-Out Integrity Problem

PIT-18 also carried a disclosed methodology limitation: five PIT-16 held-out conflict surfaces had been accidentally exposed before freeze. PIT-19 therefore reset the final-generalization test around a new CLEAN_HELD_OUT corpus whose surfaces and gold were frozen before the one-shot run. The old PIT-16 sets remain historical regression evidence rather than the primary pristine-generalization claim.

## 4. Representation V3 Architecture

Representation V3 is the frozen deterministic pipeline `surface normalization -> primitive extraction -> canonicalization -> scope/support relations -> Guardrail V3 decision`. The frozen runtime manifest contains the PIT-18 surface normalizer plus PIT-19 primitive schema, quantitative normalizer, temporal normalizer, scope lattice, primitive extractor, canonicalizer, support relations, and representation orchestrator. Frozen aggregate Representation V3 SHA-256: `b09e284cfd8316140d202e43be216e7fb4ff1743ed4e4900589fb5a0bb5ca1e9`.

## 5. Primitive Schema V3

Primitive Schema V3 (`pit19-semantic-primitives-v3`) explicitly separates semantic families including temporal and scope primitives. The evaluator projects extracted primitives into frozen labels such as conflict, recency order, recency-based resolution, count threshold, temporal policy, fallback, abstention, clarification, and operational-signal indicators.

## 6. Quantitative Normalization

The quantitative normalizer extracts count/threshold semantics into structured primitives before canonicalization. This path is evaluated independently because unseen numeric phrasing was a known generalization risk. CLEAN_HELD_OUT numeric extraction recall was 71.43% and end-to-end numeric recall was 80.00%.

## 7. Temporal Normalization

Temporal normalization extracts exact/approximate durations, periodic rules, expiry rules, and recency relations. CLEAN_HELD_OUT temporal extraction recall and end-to-end temporal-rule recall were both 100%, so temporal normalization was not the dominant failure source in the final run.

## 8. Scope Lattice V3

The frozen scope lattice orders `OBSERVATION < TURN < SESSION < TASK < WORKFLOW < DOMAIN < GLOBAL` and computes asserted/evidence scope relations. CLEAN_HELD_OUT scope classification accuracy was 98.50% and scope-relation accuracy was 99.00%. Two final fixture errors were primarily classified as scope-classification failures.

## 9. Guardrail V3 Freeze

Guardrail V3 remained unchanged from PIT-17. Frozen SHA-256: `1523ad7729f4f66ea67ac40704174a7207d7762e69d54d4d815754b432d7706f`. Final attribution follows the required causal order: primitive extraction, canonicalization, scope, support relation, then Guardrail V3. No final error required `GUARDRAIL_POLICY_ERROR`; therefore no V3 policy defect is identified.

## 10. DEV Corpus

Representation V3 DEV contains 120 samples. Primitive precision/recall were 99.1379% / 99.1379%; canonical precision/recall 100% / 100%; scope classification, scope relation, support relation, and cluster consistency were all 100%. Numeric, temporal, fallback, and conflict-resolution recall were all 100%. DEV verdict: **PASS**.

## 11. Clean Held-Out Design

CLEAN_HELD_OUT contains 100 samples: 70 unsafe and 30 hard negatives, including 11 compound samples. It was created as the new final-generalization distribution after the PIT-18 pre-exposure incident. Corpus SHA-256: `bd0f072ad07990c9024d56e2d5d34a709367d812acc15cbc5e83d9cb9a52cb23`. Gold SHA-256: `933d8487f59ae51d263d52afb71de9b7f2b934c101e07070382e8380173f53f3`.

## 12. Integrity / Overlap Validation

Integrity status is `PRISTINE`; overlap validation is `PASS`. Exact matches: 0; template matches: 0; suspicious overlaps: 0. Maximum token Jaccard was 0.75; maximum 5-gram Jaccard was 0.375. The final CLEAN_HELD_OUT execution count is exactly 1, with no post-held-out tuning or rerun.

## 13. Frozen Acceptance Criteria

Representation gates require >=95% primitive precision/recall, canonical precision/recall, scope classification, scope relation, support relation, and cluster consistency. End-to-end gates require >=95% unsafe recall/precision, violation-class recall/precision, numeric/temporal/fallback/scope recall; <=5% hard-negative FPR; and 100% conflict recall plus compound full-class recall. These thresholds were frozen before the one-shot run and were not lowered afterward.

## 14. DEV Results

| Metric | Result |
|---|---:|
| Samples | 120 |
| Primitive precision | 99.1379% |
| Primitive recall | 99.1379% |
| Canonical precision | 100% |
| Canonical recall | 100% |
| Scope classification | 100% |
| Scope relation | 100% |
| Support relation | 100% |
| Cluster consistency | 100% |

DEV passed all frozen representation-development requirements.

## 15. PIT-15 Regression

PIT-15 final regression is **PASS**: 10/10 known failures detected, conflict detection 100%, unsupported heuristic detection 100%, Muse preservation 100%, lifecycle preservation 100%, and FPR 0%.

## 16. PIT-16 Regression

Both PIT-16 FULL regression and the historical PRISTINE regression are **PASS** under Representation V3 + unchanged Guardrail V3. All frozen PIT-16 regression metrics are 100% and hard-negative FPR is 0%. This demonstrates complete recovery of the known historical regimes, but it is not the primary pristine-generalization result.

## 17. Clean Held-Out Representation Results

| Metric | Result | Gate |
|---|---:|---:|
| Primitive precision | 100% | >=95% |
| Primitive recall | 77.39% | >=95% |
| Canonical precision | 100% | >=95% |
| Canonical recall | 78.30% | >=95% |
| Scope classification | 98.50% | >=95% |
| Scope relation | 99.00% | >=95% |
| Support relation | 91.89% | >=95% |
| Cluster consistency | 40.00% | >=95% |
| Conflict-state accuracy | 94.00% | diagnostic |
| Supersession-support accuracy | 66.67% | diagnostic |
| Numeric extraction recall | 71.43% | diagnostic |
| Temporal extraction recall | 100.00% | diagnostic |
| Fallback extraction recall | 93.75% | diagnostic |

Representation gate: **FAIL**. The key collapse is recall and invariance, despite perfect precision.

## 18. Clean Held-Out End-to-End Results

| Metric | Result | Gate |
|---|---:|---:|
| Unsafe recall | 88.57% | >=95% |
| Unsafe precision | 91.18% | >=95% |
| Violation-class recall | 83.95% | >=95% |
| Violation-class precision | 91.89% | >=95% |
| Hard-negative FPR | 20.00% | <=5% |
| Conflict recall | 40.00% | 100% |
| Numeric recall | 80.00% | >=95% |
| Temporal recall | 100.00% | >=95% |
| Fallback recall | 90.00% | >=95% |
| Scope recall | 100.00% | >=95% |
| Compound full-class recall | 54.55% | 100% |

End-to-end gate: **FAIL**.

## 19. Error Attribution

Frozen error analysis identifies 25 fixture-level representation/decision failures. Primary distribution: primitive extraction false negative 16; support relation 6; scope classification 2; canonicalization 1; all other allowed categories, including Guardrail policy error, are zero. Primitive false negatives therefore dominate the causal chain. Missing primitives frequently suppress canonical facts and violation classes; support-relation errors explain a smaller set of hard-negative false positives or missed conflict support. Full per-fixture traces are frozen in `experiments/pit19/error-analysis.json` and reference the raw corpus by fixture ID rather than duplicating held-out surface strings.

## 20. V1 / V2 / V3 Comparative Analysis

| Milestone | Known-regime state | Held-out integrity | Held-out primitive P/R | Held-out canonical P/R | Conflict recall | Numeric recall | Hard-negative FPR | Compound full-class recall | Verdict |
|---|---|---|---|---|---:|---:|---:|---:|---|
| PIT-17 / V1 | PIT-15 FAIL; PIT-16 FAIL | legacy held-out | n/a | n/a | 75% | 87.5% | 0% | 75% | `REPRESENTATION_LAYER_INSUFFICIENT` |
| PIT-18 / V2 | PIT-15 PASS; PIT-16 PRISTINE FAIL | `PARTIALLY_PRE_EXPOSED` | 87.88% / 90.63% | 86.21% / 89.29% | 33.33% | 100% | 0% | 100% | `REPRESENTATION_V2_INSUFFICIENT` |
| PIT-19 / V3 | DEV PASS; PIT-15 PASS; PIT-16 regression PASS | `PRISTINE` | 100% / 77.39% | 100% / 78.30% | 40% | 80% | 20% | 54.55% | `DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED` |

The milestones do not share an identical held-out contract, so the table separates historical benchmark recovery from final unseen-distribution evidence. V3's complete historical recovery is real, but its pristine CLEAN_HELD_OUT regression is materially worse on recall, conflict handling, FPR, and compound-class completeness. The trend is **BENCHMARK RECOVERY WITHOUT SUFFICIENT GENERALIZATION**.

## 21. Architectural Interpretation

The deterministic representation approach demonstrated strong ability to recover known and development distributions but failed to maintain comparable semantic extraction performance on a genuinely pristine unseen distribution. The absence of benchmark leakage, post-hoc tuning, Guardrail-policy changes, and provider/candidate-specific logic makes the CLEAN_HELD_OUT failure materially informative.

Current evidence therefore supports `DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED`: a suspected practical ceiling for this tested deterministic representation architecture and refinement history. This is not a proof that deterministic extraction is impossible. It is evidence that further blind rule accumulation is unlikely to be the highest-value next experiment.

## 22. Next Milestone

Freeze the next research question: **Can a learned or LLM-assisted semantic extractor improve semantic representation generalization while retaining deterministic evidence-bound verification and low false-positive behavior?**

Recommended next milestone: **PIT-20 — Learned / LLM-Assisted Semantic Extractor Feasibility**. PIT-20 is not started by this closure.
