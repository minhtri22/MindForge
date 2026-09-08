# PIT-17 Semantic Fact Representation / Guardrail Unification

## 1. Motivation

PIT-15 and PIT-16 showed that direct surface guardrails behave differently across historical and adversarial representation regimes. PIT-17 tested whether a canonical semantic-fact layer could unify those regimes.

## 2. Architecture Tested

`Raw Evidence + Raw Teaching Signal -> Semantic Fact Extractor -> Support Relations -> Unified Guardrail V3`

V3 consumes canonical facts only and does not read candidate/provider identity, scenario IDs, or gold labels.

## 3. Frozen Representation

- Semantic fact schema: `pit17-semantic-facts-v1`
- Unified guardrail: `pit17-unified-semantic-fact-guardrail-v3`
- Frozen implementation SHA256: `a954733c888250962f70fc062046a0c1b74fdf4423e827006c51f083ba458f11`
- Fact goldset: 36 samples including PIT-15 historical samples, PIT-16 DEV, hard negatives, and compound violations.
- Representation invariance: 4 semantic clusters / 16 surface variants.

## 4. Development / Methodology Results

- Fact precision: **100%**
- Fact recall: **100%**
- Conflict-state accuracy: **100%**
- Supersession-support accuracy: **100%**
- Numeric-policy extraction recall: **100%**
- Temporal-policy extraction recall: **100%**
- Fallback extraction recall: **100%**
- Scope-support accuracy: **100%**
- Abstention/clarification accuracy: **100%**
- Representation cluster consistency: **100%**
- PIT-16 DEV V3 sample/class precision and recall: **100%**
- DEV false-positive rate: **0%**

These development results satisfied the frozen pre-final gates.

## 5. Frozen Final Evaluation

Final evaluation was executed once after freezing V3. V3 and the extractor/support implementation were not modified afterward.

### PIT-15 regression

- Known failures detected: **6 / 10**
- Conflict detection: **33.3333%**
- Unsupported heuristic detection: **71.4286%**
- False-positive rate: **7.6923%**
- Muse preservation: **85.7143%**
- Lifecycle preservation: **90.3226%**
- Violation-class recall: **61.5385%**
- Violation-class precision: **72.7273%**

PIT-15 regression acceptance: **FAIL**.

### PIT-16 HELD_OUT

- Unsafe sample recall: **91.3043%**
- Unsafe sample precision: **100%**
- Violation-class recall: **90%**
- Violation-class precision: **93.75%**
- Hard-negative FPR: **0%**
- Critical conflict recall: **75%**
- Numeric-threshold recall: **87.5%**
- Temporal-rule recall: **100%**
- Fallback recall: **75%**
- Scope-generalization recall: **100%**
- Evidence-grounding recall: **100%**
- Compound full-class recall: **75%**

PIT-16 held-out acceptance: **FAIL**.

## 6. Error Taxonomy

- `FACT_EXTRACTION_FALSE_NEGATIVE`: **8**
- `FACT_EXTRACTION_FALSE_POSITIVE`: **2**
- `SCOPE_NORMALIZATION_ERROR`: **5**
- `SUPPORT_RELATION_ERROR`: **0**
- `GUARDRAIL_POLICY_ERROR`: **0**
- `AMBIGUOUS_INPUT`: **0**

The dominant failure is representation coverage/generalization. Once facts and support relations are represented correctly, no independent V3 policy error was identified in the frozen outputs.

## 7. Verdict

**`REPRESENTATION_LAYER_INSUFFICIENT`**

The representation hypothesis remains plausible, but this deterministic fact extractor and scope normalizer do not generalize sufficiently across both historical PIT-15 language and PIT-16 held-out surfaces. This result does not justify candidate-specific or phrase-specific patching.

## 8. Scope Closure

- API calls: 0
- New teacher inference: 0
- PIT-15 artifacts modified: NO
- PIT-16 artifacts modified: NO
- Teacher verdicts changed: NO
- Teacher selected: NO
- Training: NO
- Distillation: NO
- MindForge integration: NO
- Kernel / TokenModel / PPF changes: NO
- Held-out post-hoc tuning: NO

## 9. Next Milestone

Recommended: **PIT-18 — Representation Layer Refinement**.

Do not automatically start PIT-18.
