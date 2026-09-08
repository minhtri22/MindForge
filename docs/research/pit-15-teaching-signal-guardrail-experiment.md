# PIT-15 Teaching Signal Guardrail Experiment

## 1. Purpose

Test whether a deterministic, model-agnostic, evidence-bound post-generation guardrail can reduce known PIT Teaching Signal semantic failures without degrading already-correct behavior.

PIT-15 uses frozen historical Teaching Signals only. It performs no teacher API calls, no regeneration, no semantic repair, no training, and no MindForge integration.

## 2. Causal Question

For the same candidate, scenario, evidence, prompt contract, provider-produced Teaching Signal, and schema, compare:

- CONTROL: the previously recorded untreated Teaching Signal;
- TREATMENT: the identical Teaching Signal passed through deterministic guardrail validation.

The guardrail emits a separate `ACCEPT`, `FLAG`, or `BLOCK` result. It never edits the Teaching Signal.

## 3. Candidate Roles

Positive control:

- `meta/muse-glimmer-30b`

Heuristic-risk candidates:

- `minimax/minimax-m3:free`
- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `openai/gpt-oss-20b`

Negative conflict controls:

- `qwen/qwen3.7-max:free`
- `deepseek/deepseek-v4-pro`
- `google/gemma-4-31b-it`

`moonshotai/kimi-k3` is excluded because its frozen PIT-14.1.C long-term consistency evidence is incomplete after the preserved HTTP 429.

## 4. Control Condition

All 49 candidate × scenario control samples come from already-collected normalized evidence:

- xKiro/PIT-13.1.B controls: `experiments/pit13/evidence/normalized/`;
- NVIDIA/PIT-14.1.C controls: `experiments/pit14_1/evidence/normalized/`.

Historical evidence was referenced by SHA256 and was not copied back into, edited, regenerated, or repaired by PIT-15.

## 5. Treatment Condition

Guardrail version:

`pit15-deterministic-guardrails-v1`

Implementation:

- `scripts/pit15/guardrails.py`
- `scripts/pit15/evaluate_guardrails.py`
- `scripts/pit15/validate_pit15.py`

The same implementation is applied to all seven candidates. There is no candidate ID in guardrail decision logic.

## 6. Guardrail Definitions

The treatment validates four areas:

1. unresolved conflict must not be collapsed by recency without explicit supersession evidence;
2. unsupported numeric, temporal, fallback, or policy rules must be flagged;
3. material operational claims must remain grounded in scenario evidence;
4. valid correction, rare-exception, insufficient-evidence, drift, and long-term behavior must remain accepted.

Frozen violation classes:

- `UNSUPPORTED_CONFLICT_RESOLUTION`
- `UNSUPPORTED_NUMERIC_THRESHOLD`
- `UNSUPPORTED_TEMPORAL_RULE`
- `UNSUPPORTED_FALLBACK_POLICY`
- `UNSUPPORTED_SCOPE_GENERALIZATION`
- `EVIDENCE_GROUNDING_FAILURE`

## 7. Frozen Scenario Set

PIT-15 uses all seven canonical PIT-13.1.B scenarios, byte-referenced from `experiments/pit13/evidence/scenarios.json`:

- `stable_preference_001`
- `preference_drift_001`
- `conflicting_evidence_001`
- `user_correction_001`
- `rare_exception_001`
- `insufficient_evidence_001`
- `long_term_consistency_001`

The stable-preference case is retained because it contains previously documented unsupported heuristics for MiniMax and Nemotron that would otherwise be absent from the experiment.

## 8. Success Criteria

`experiments/pit15/protocol.json` froze the criteria before treatment execution:

- conflict failure detection rate: 100%;
- unsupported-heuristic sample detection rate: 100%;
- Muse material false BLOCK count: 0;
- Muse preservation rate: 100%;
- lifecycle material false BLOCK count: 0;
- lifecycle preservation rate: 100%.

The frozen oracle annotations are evaluation labels from PIT-14 and PIT-14.1.D. They are not consulted by guardrail decision logic.

## 9. Results

Control samples: **49**.

Treatment samples: **49**.

Known semantic-failure samples: **10**.

Known-valid samples: **39**.

Primary metrics:

| Metric | Result |
| --- | ---: |
| Semantic Failure Detection Rate | **100% (10/10)** |
| False Positive Rate | **0% (0/39)** |
| Conflict Failure Detection Rate | **100%** |
| Unsupported Heuristic Sample Detection Rate | **100%** |
| Muse Positive-Control Preservation Rate | **100% (7/7)** |
| Lifecycle Preservation Rate | **100%** |

Secondary diagnostic:

- expected violation-class instances: 13;
- correctly identified expected violation-class instances: 12;
- violation-class recall: **92.3077%**;
- samples with at least one expected class missed: 1.

The single class-level miss is Nemotron `stable_preference_001`: the sample was correctly `FLAG`ged for `EVIDENCE_GROUNDING_FAILURE` because it invoked satisfaction metrics absent from evidence, but the phrase "three or more consecutive interactions" was not separately classified as `UNSUPPORTED_NUMERIC_THRESHOLD` by v1. The guardrail implementation was not modified after observing this result.

## 10. Candidate Effects

| Candidate | Effect |
| --- | --- |
| `meta/muse-glimmer-30b` | `UNCHANGED_VALID` |
| `minimax/minimax-m3:free` | `IMPROVED_BY_GUARDRAIL` |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | `IMPROVED_BY_GUARDRAIL` |
| `openai/gpt-oss-20b` | `IMPROVED_BY_GUARDRAIL` |
| `qwen/qwen3.7-max:free` | `IMPROVED_BY_GUARDRAIL` |
| `deepseek/deepseek-v4-pro` | `IMPROVED_BY_GUARDRAIL` |
| `google/gemma-4-31b-it` | `IMPROVED_BY_GUARDRAIL` |

These are system-level treatment effects. They do not change any raw teacher qualification verdict.

## 11. Positive-Control Preservation

Muse Glimmer remained accepted on all 7/7 frozen scenarios.

Material false BLOCKs: **0**.

This satisfies H15-3 under the frozen evidence set.

## 12. Failure Analysis

The guardrail caught all previously documented unsafe Teaching Signal samples at the sample level, including all three negative conflict controls.

The class-level miss demonstrates a narrower limitation: deterministic lexical guardrails can catch the unsafe sample while still incompletely characterizing every unsupported rule inside it. PIT-15 therefore establishes treatment effectiveness on this frozen corpus, not exhaustive semantic parsing.

No post-result guardrail tuning was performed.

## 13. Architectural Implications

Guardrail verdict: **GUARDRAIL_EFFECTIVE** under the frozen PIT-15 acceptance contract.

The supported architectural interpretation is:

`Teacher * Evidence-Bound Guardrail`

This improves system-level semantic safety on the known PIT failure surface while preserving the qualified positive control.

This does not mean Qwen, DeepSeek, Gemma, MiniMax, Nemotron, or GPT-OSS became intrinsically better teachers. Their raw outputs and PIT-14/PIT-14.1.D verdicts remain unchanged.

## 14. Limitations

- The corpus contains one canonical instance per PIT scenario family.
- The deterministic v1 rules are lexical and do not prove paraphrase robustness.
- Violation-class recall is 92.3077%, despite 100% unsafe-sample detection.
- No adversarial wording, equivalent paraphrases, repeated seeds, or novel unsupported-policy constructions were tested.
- The experiment establishes guardrail behavior on frozen historical outputs only; it does not establish production readiness.

## 15. Next Step

Recommended next milestone:

**PIT-16 — Guardrail Refinement / Adversarial Validation**

Freeze a new guardrail version prospectively, include the observed numeric-threshold blind spot as a regression case, then test paraphrase and adversarial variants without changing raw teacher verdicts or selecting a final teacher.

PIT-15 does not authorize teacher selection, training, distillation, or MindForge integration.
