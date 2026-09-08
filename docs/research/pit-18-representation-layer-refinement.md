# PIT-18 Representation Layer Refinement

## 1. Motivation

PIT-17 established that a canonical semantic-fact layer can unify guardrail policy evaluation when representation is correct, but its deterministic extractor did not generalize sufficiently across historical and adversarial surfaces. PIT-18 therefore refined the representation layer while keeping Guardrail V3 frozen.

## 2. Interrupted Execution State

PIT-18 resumed from an interrupted development run on branch `research/pit` with baseline HEAD `f422f9c6b5f593f29293fce332c6eff9a8c4a503`. Existing `scripts/pit18/` work was preserved. The final held-out runs had not yet executed at the interruption point.

The resumed task verified the latest Representation V2 patch on DEV before any further refinement. API calls remained **0** and new teacher inference remained **0**.

## 3. Representation V2 Architecture

The frozen pipeline is:

`Evidence + Teaching Signal -> semantic primitives -> canonical facts -> support relations -> Guardrail V3`

`scripts/pit18/representation_v2.py` composes the primitive extractor, canonicalizer, support relation implementation, and the unchanged PIT-17 Guardrail V3.

Frozen Representation V2 SHA256: `ca83f3ebc3ab24812013f5819d14aee2309be7b196ab42f678fd76a0fc60ebd6`.

## 4. Semantic Primitive Layer

The primitive layer separates semantic roles into the families `CLAIM`, `RELATION`, `QUANTIFIER`, `TEMPORAL`, `FALLBACK`, `UNCERTAINTY`, and `SCOPE`. The refinement focused on semantic-role distinction, clarification semantics, recency, temporal-policy paraphrases, scope normalization, and primitive-to-canonical propagation.

Frozen primitive-schema SHA256: `3928c6ca3281c1dad0f6daaa315690ca978749a940d6162fb7d3dd028b6f7834`.

## 5. Canonical Facts

Canonicalization converts extracted primitives into evidence state, teaching-signal state, and provenance-backed semantic facts such as conflict, supersession, numeric-policy, temporal-policy, fallback, abstention/clarification, operational-signal, and asserted-scope state.

The final held-out failures show that canonical errors were downstream consequences of missing or extra primitives rather than an independently demonstrated canonicalizer defect.

## 6. Scope Lattice

The frozen lattice orders `OBSERVATION < SESSION < TASK < WORKFLOW < DOMAIN < GLOBAL` and computes `NARROWER`, `EQUAL`, or `BROADER` asserted-scope relationships.

Frozen scope-lattice SHA256: `615b2065eaf4243be65dfff979e0d252f272355a55cc8872658e21d4ce462514`.

Frozen support-relations V2 SHA256: `5c23b17aa6ecba5d864f1595db239018b6ec97d1ca7be1caf133ad8ea0694d3d`.

## 7. Frozen V3

Guardrail V3 remained unchanged throughout PIT-18.

Frozen/baseline Guardrail V3 SHA256: `1523ad7729f4f66ea67ac40704174a7207d7762e69d54d4d815754b432d7706f`.

No final failure demonstrated a `GUARDRAIL_POLICY_ERROR` with correct upstream primitives, canonical facts, scope, and support relations.

## 8. DEV Refinement

The current code was rerun on the permitted DEV evidence before freeze.

Representation DEV, 80 samples:

- Primitive precision: **100%**
- Primitive recall: **97.5%**
- Canonical fact precision: **100%**
- Canonical fact recall: **100%**
- Scope classification accuracy: **100%**
- Scope relation accuracy: **100%**
- Support relation accuracy: **100%**
- Conflict extraction accuracy: **100%**
- Numeric extraction recall: **100%**
- Temporal extraction recall: **100%**
- Fallback extraction recall: **100%**
- Clarification/abstention accuracy: **100%**
- Representation cluster consistency: **100%**

PIT-15 DEV regression remained 10/10 known failures detected, 100% conflict detection, 100% unsupported-heuristic detection, 100% Muse preservation, 100% lifecycle preservation, and 0% FPR.

PIT-16 DEV remained 100% on unsafe recall/precision, violation-class recall/precision, conflict, numeric, temporal, fallback, scope, and compound full-class recall, with 0% hard-negative FPR.

Refinement used only PIT-15 historical evidence, PIT-16 DEV, Representation DEV gold, and DEV invariance clusters.

## 9. Held-out Integrity Incident

Before final freeze, a corpus-inspection command accidentally displayed the surface forms of five PIT-16 HELD_OUT samples:

- `conflict-04`
- `conflict-05`
- `conflict-06`
- `conflict-07`
- `conflict-08`

No labels or gold outputs were exposed. Repository/process validation found no evidence that the displayed surfaces were used for refinement. The five cases remained frozen and were retained in the full final evaluation.

This means PIT-18 cannot claim pristine held-out isolation for those five samples.

## 10. Pre-exposure Manifest

Final provenance classification is:

- `PRISTINE_HELD_OUT`: all PIT-16 held-out fixtures except the five IDs above.
- `PRE_EXPOSED_HELD_OUT`: exactly `conflict-04` through `conflict-08` as listed above.

Held-out integrity status: **`PARTIALLY_PRE_EXPOSED`**.

Pre-exposed labels exposed: **NO**.

Pre-exposed cases used for refinement: **NO**, based on repository/process evidence.

## 11. Freeze Boundary

`experiments/pit18/protocol.json` froze Representation V2, primitive schema, scope lattice, support relations, Guardrail V3, DEV gold, representation HELD_OUT gold, representation clusters, PIT-16 corpus/split, pre-exposure manifest, success criteria, and metric definitions before final evaluation.

Key frozen hashes include:

- Representation V2: `ca83f3ebc3ab24812013f5819d14aee2309be7b196ab42f678fd76a0fc60ebd6`
- Guardrail V3: `1523ad7729f4f66ea67ac40704174a7207d7762e69d54d4d815754b432d7706f`
- Representation HELD_OUT gold: `28f161c3b70ce53a539059763c9e6db8c6744b5ec0cd9f30acc4a50812c9fc22`
- Representation clusters: `e08f00f6c41543cd9d3d9a0030b0b75b5db2e1756a3787e5a28995899392e293`
- PIT-16 corpus: `e0787f36dddc0800baed00b4d01ccf33552e0d0873eb28b1b2abc996eb8602fe`
- PIT-16 split: `281faf219842dbf823dff1e783c6fc19424b66be7d8e02cc0bf9df0ce00970cf`
- Metric definitions: `9c0745f665cf1ec6f914728e3df4441a0e8bd94817478871cd723a8cc0da11b2`

No Representation V2, gold, dataset, label, or V3 modification was made after this boundary.

## 12. Representation HELD_OUT

The frozen 40-sample Representation HELD_OUT set was evaluated once.

- Primitive precision: **87.8788%**
- Primitive recall: **90.625%**
- Canonical fact precision: **86.2069%**
- Canonical fact recall: **89.2857%**
- Scope classification accuracy: **100%**
- Scope relation accuracy: **100%**
- Support relation accuracy: **92.5%**
- Conflict extraction accuracy: **100%**
- Numeric extraction recall: **50%**
- Temporal extraction recall: **75%**
- Fallback extraction recall: **100%**
- Clarification/abstention accuracy: **100%**
- Representation cluster consistency: **60%**

Frozen Representation HELD_OUT acceptance: **FAIL**.

## 13. PIT-15 Regression

Frozen Representation V2 + frozen V3 preserved the PIT-15 regression contract:

- Known failures detected: **10 / 10**
- Conflict detection: **100%**
- Unsupported heuristic detection: **100%**
- Muse preservation: **100%**
- Lifecycle preservation: **100%**
- False-positive rate: **0%**

PIT-15 final regression acceptance: **PASS**.

## 14. PIT-16 FULL Held-out

The single frozen PIT-16 held-out execution contains 67 samples. The FULL view retains all five disclosed pre-exposed cases.

- Unsafe recall: **93.4783%**
- Unsafe precision: **100%**
- Violation-class recall: **94%**
- Violation-class precision: **94%**
- Hard-negative FPR: **0%**
- Critical conflict recall: **75%**
- Numeric threshold recall: **100%**
- Temporal rule recall: **100%**
- Fallback recall: **100%**
- Scope-generalization recall: **88.8889%**
- Compound full-class recall: **100%**

FULL held-out acceptance: **FAIL**.

## 15. PIT-16 PRISTINE Held-out

The PRISTINE view is derived from the same one-shot raw run and excludes only the five disclosed pre-exposed IDs. It contains 62 samples and is the strongest basis for generalization claims.

- Unsafe recall: **92.6829%**
- Unsafe precision: **100%**
- Violation-class recall: **93.3333%**
- Violation-class precision: **97.6744%**
- Hard-negative FPR: **0%**
- Critical conflict recall: **33.3333%**
- Numeric threshold recall: **100%**
- Temporal rule recall: **100%**
- Fallback recall: **100%**
- Scope-generalization recall: **88.8889%**
- Compound full-class recall: **100%**

PRISTINE held-out acceptance: **FAIL**.

## 16. PRE_EXPOSED Diagnostic Subset

The five pre-exposed cases are diagnostic only and cannot rescue a failed pristine result.

- Sample recall: **100%**
- Violation-class recall: **100%**
- Conflict recall: **100%**

The fact that this subset performs better than the pristine conflict subset strengthens the requirement to base generalization claims on PRISTINE HELD_OUT.

## 17. Error Attribution

Final post-freeze error distribution:

- `SURFACE_NORMALIZATION_ERROR`: **0**
- `PRIMITIVE_EXTRACTION_FALSE_NEGATIVE`: **5**
- `PRIMITIVE_EXTRACTION_FALSE_POSITIVE`: **4**
- `CANONICALIZATION_ERROR`: **0**
- `SCOPE_CLASSIFICATION_ERROR`: **4**
- `SCOPE_RELATION_ERROR`: **0**
- `SUPPORT_RELATION_ERROR`: **0**
- `GUARDRAIL_POLICY_ERROR`: **0**
- `AMBIGUOUS_INPUT`: **0**

The dominant valid failures are primitive coverage and scope classification. Four representation HELD_OUT clarification rows are also scored as primitive false positives against frozen gold even though their surfaces explicitly describe unresolved conflict; this is recorded as a held-out annotation limitation, and the gold was not changed after freeze.

Detailed per-case attribution is preserved in `experiments/pit18/error-analysis.json`.

## 18. Methodology Limitations

Methodology status: **`PASS_WITH_PRE_EXPOSURE_LIMITATION`**.

Validation found no candidate-specific logic, provider-specific logic, scenario-ID decision logic, exact known-phrase patching, gold-label leakage, post-freeze held-out tuning, or V3 modification. The known pre-exposure is explicitly disclosed and separately measured.

The methodology result does not mean fully pristine adversarial isolation because five PIT-16 conflict surfaces were seen before freeze.

## 19. Final Verdict

**`REPRESENTATION_V2_INSUFFICIENT`**

Representation HELD_OUT failed its frozen gates, PIT-16 FULL failed, and PIT-16 PRISTINE failed. PIT-15 regression passed. Therefore PIT-18 cannot be upgraded to `REPRESENTATION_V2_VALIDATED` or `REPRESENTATION_V2_VALIDATED_WITH_LIMITS`.

## 20. Architectural Interpretation

The experiment supports the architectural separation between representation and policy: the frozen V3 policy continued to behave correctly when given the represented facts, while the remaining generalization failures were concentrated upstream in primitive extraction and scope classification.

PIT-18 does not demonstrate a V3 policy defect. It also does not justify teacher selection, training, distillation, or MindForge integration.

Teacher selected: **NO**. Training: **NO**. Distillation: **NO**. MindForge integration: **NO**.

## 21. Next Milestone

Recommended next milestone: **PIT-19 — Representation V3 Refinement**.

PIT-19 is not started by this task. Any change to the frozen representation belongs to that next milestone.
