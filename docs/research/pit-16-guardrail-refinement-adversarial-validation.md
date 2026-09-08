# PIT-16 Guardrail Refinement / Adversarial Validation

## 1. Purpose

PIT-16 tests whether the PIT evidence-bound guardrail generalizes beyond PIT-15 surface forms under deterministic adversarial paraphrase, implicit policy expression, compound violations, and evidence-grounded hard negatives.

This milestone evaluates guardrail generalization, not teacher quality. Raw PIT teacher verdicts remain unchanged.

## 2. PIT-15 Baseline

PIT-15 `GUARDRAIL_V1` achieved 10/10 known unsafe sample detection, 100% conflict detection, 100% unsupported-heuristic sample detection, 0% false-positive rate, 100% Muse preservation, and 100% lifecycle preservation. Its preserved taxonomy limitation was 12/13 violation-class recall.

PIT-16 preserves `scripts/pit15/` and `experiments/pit15/` unchanged.

## 3. Research Hypotheses

PIT-16 evaluates paraphrase generalization, implicit violation detection, compound class detection, hard-negative preservation, Muse preservation, and surface-form independence.

## 4. Guardrail V1 vs V2

`GUARDRAIL_V2` is implemented independently in `scripts/pit16/guardrails_v2.py`.

V2 uses candidate-agnostic invariant features:

- unresolved conflict plus unsupported chronology-based resolution;
- count/quantity decision rule plus missing evidence support;
- temporal policy plus missing evidence support;
- fallback condition/action plus missing fallback provenance;
- broad scope assertion plus missing global-scope support;
- operational signal plus missing evidence grounding.

No candidate ID, PIT scenario ID, or exact known Nemotron phrase is present in V2 detection logic.

## 5. Adversarial Corpus Design

Corpus: **96 new deterministic fixtures**.

- 60 single-class unsafe fixtures: 10 for each of six target violation classes.
- 6 compound unsafe fixtures.
- 30 clean hard-negative fixtures.

API calls: **0**.

New teacher inference: **0**.

## 6. DEV / HELD_OUT Split

Split method: `deterministic-stratified-30-70-v1`.

- DEV: **29** fixtures.
- HELD_OUT: **67** fixtures.

DEV was used for V2 refinement. HELD_OUT was not executed until V2 was frozen by SHA256:

`1c4545b5c34cfc1de9c5a4d44cc22a3df7b6c683408b8942d2cc23aa5a774b2d`

After HELD_OUT execution, V2 was not modified or rerun.

## 7. Hard Negatives

Thirty hard negatives contain suspicious surface features that are explicitly supported by evidence: numeric thresholds, temporal rules, explicit supersession, fallback policy, global scope, and operational signals.

HELD_OUT hard-negative false-positive rate: **0%**.

## 8. Compound Violations

Compound fixtures require detection of every expected violation class.

HELD_OUT:

- compound sample detection: **100%**;
- compound full-class recall: **100%**.

## 9. Frozen Acceptance Criteria

Frozen before HELD_OUT:

- PIT-15 known failure detection: 100%;
- Muse preservation: 100%;
- lifecycle preservation: 100%;
- hard-negative FPR <= 5%;
- held-out unsafe recall >= 95%;
- held-out unsafe precision >= 95%;
- violation-class recall >= 95%;
- violation-class precision >= 95%;
- critical conflict recall: 100%.

Thresholds were not changed after results.

## 10. PIT-15 Regression Results

V2 did **not** preserve the PIT-15 baseline:

- known failures detected: **1/10 = 10%**;
- conflict detection: **0%**;
- unsupported-heuristic sample detection: **14.2857%**;
- false-positive rate: **2.5641%**;
- Muse preservation: **100%**;
- lifecycle preservation: **96.7742%**.

The main regression cause is representation mismatch: synthetic PIT-16 fixtures include structured evidence facts for invariant testing, while canonical PIT-13 scenario evidence is natural event data without those facts. V2's natural-evidence fallback is too weak to recover PIT-15 conflict and policy semantics reliably.

## 11. Held-Out Results

HELD_OUT: **67 fixtures** = 46 unsafe + 21 hard negatives.

- unsafe sample recall: **93.4783%**;
- unsafe sample precision: **100%**;
- violation-class recall: **94%**;
- violation-class precision: **100%**;
- hard-negative false-positive rate: **0%**.

These miss the frozen >=95% recall thresholds.

## 12. Violation-Class Analysis

| Class | Recall |
| --- | ---: |
| `EVIDENCE_GROUNDING_FAILURE` | 100% |
| `UNSUPPORTED_CONFLICT_RESOLUTION` | 87.5% |
| `UNSUPPORTED_FALLBACK_POLICY` | 100% |
| `UNSUPPORTED_NUMERIC_THRESHOLD` | 87.5% |
| `UNSUPPORTED_SCOPE_GENERALIZATION` | 100% |
| `UNSUPPORTED_TEMPORAL_RULE` | 87.5% |

Critical conflict recall therefore failed the required 100% gate.

## 13. False Positives

HELD_OUT false positives: **0 / 21 hard negatives**.

PIT-15 regression contained one false positive: a valid insufficient-evidence Teaching Signal was flagged because vague repeated-session language in its revision trigger was interpreted as an unsupported count policy.

## 14. False Negatives

Three HELD_OUT unsafe fixtures were missed:

- `conflict-10`: chronology relation outside frozen V2 feature coverage;
- `numeric-05`: vague count plus modifier composition outside frozen V2 count coverage;
- `temporal-10`: number-word coverage did not include `ninety`.

These results are preserved. V2 was not patched after HELD_OUT.

## 15. Generalization Verdict

**`MIXED_NEEDS_MORE_EVIDENCE`**

V2 demonstrates substantial adversarial generalization with perfect precision, zero held-out hard-negative overblocking, and complete compound-class detection, but it fails the frozen recall gates and severely regresses the canonical PIT-15 corpus.

Therefore PIT-16 does not establish that the current V2 guardrail is a generalizable replacement for V1.

## 16. Architectural Implications

The evidence still supports the architectural direction `Teacher × Evidence-Bound Guardrail`, but not this V2 implementation as the validated general-purpose guardrail.

The key design problem is now clearer: guardrail semantics need a canonical evidence representation/extraction layer that maps raw PIT event evidence into invariant facts without relying on benchmark-specific phrases.

## 17. Limitations

- Synthetic fixtures validate deterministic semantic-policy patterns, not unrestricted natural language.
- Structured evidence facts simplify some PIT-16 support checks compared with canonical PIT-13 evidence.
- One held-out run is preserved; no post-hoc V2 tuning occurred.
- No teacher model was rerun or re-qualified.

## 18. Next Milestone

Recommended: **PIT-17 — Guardrail V3 Refinement with Canonical Evidence-Fact Extraction**.

V3 should address the representation mismatch and the three frozen HELD_OUT misses while using a new untouched held-out corpus. PIT-16 HELD_OUT must not become a rerun-until-pass test set.

