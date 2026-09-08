# PIT-14 Candidate Qualification Review

## 1. Purpose

Review only the frozen PIT-13.1.B evidence and assign candidate-level qualification verdicts under the existing PIT contract. No API calls, new inference evidence, retraining, distillation, or MindForge integration are part of this review.

## 2. Evidence Boundary

Reviewed candidates:

- `qwen/qwen3.7-max:free`
- `deepseek/deepseek-v4-pro`
- `minimax/minimax-m3:free`

Evidence source: `experiments/pit13/evidence/`, including the frozen scenario manifest, normalized Teaching Signals, candidate metrics, and candidate profiles from the completed 21/21 PIT-13.1.B run.

`mistralai/mistral-small-2603` is not semantically reviewed because no full PIT-13.1.B evidence was collected. Its status remains `EXCLUDED_FROM_EXECUTION` due to `SMOKE_NOT_QUALIFIED`.

## 3. Qualification Criteria

The review follows PIT-10/PIT-11.2 semantics and gives greater weight to core semantic safety than to formatting or aggregate score. In particular:

- unresolved conflicting evidence must remain unresolved unless evidence supports supersession;
- explicit user correction overrides prior inference;
- insufficient evidence must not become a stable personal claim;
- rare exceptions must not overwrite stable patterns;
- recency is not by itself proof of truth or supersession;
- unsupported policy or heuristic invention is a separate risk even when the primary inference is correct.

No new numeric threshold or post-hoc scoring formula is introduced.

## 4. Candidate Review — Qwen3.7

Candidate: `qwen/qwen3.7-max:free`

Strengths:

- Strong stable-pattern identification and bounded applicability.
- Correct preference-drift detection without losing the phase-specific context.
- Correct user-correction handling.
- Strong rare-exception and long-term lifecycle handling.
- Clear and machine-usable Teaching Signal structure across all seven scenarios.

Critical limits:

- In `conflicting_evidence_001`, Qwen asserted that the latest instruction superseded the earlier one using a general temporal-precedence rule even though the frozen scenario explicitly supplied no retraction, correction, or context distinction. This is `UNSUPPORTED_CONFLICT_RESOLUTION` and violates the PIT semantic rule `CONFLICTING != RESOLVED`.
- In `insufficient_evidence_001`, Qwen correctly abstained from inferring a stable dark-mode preference but invented a two-additional-session / seven-day revision threshold that was not present in evidence. This is `MINOR_UNSUPPORTED_HEURISTIC`.

Verdict: **NOT_SUITABLE**

Reason: the conflict-collapse behavior is a material failure in a core Personal Intelligence semantic. The rest of the profile is strong, but the current evidence does not support using Qwen3.7 as the primary PIT teacher without first demonstrating reliable conflict abstention.

Required guardrails before reconsideration:

- conflicting-evidence abstention check;
- explicit evidence requirement before supersession;
- unsupported-heuristic detector for revision rules.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-13.1.B scope**.

## 5. Candidate Review — DeepSeek V4 Pro

Candidate: `deepseek/deepseek-v4-pro`

Strengths:

- Strong temporal drift reasoning.
- Correct correction recovery.
- Strong rare-exception handling and long-term consistency.
- Concise, usable applicability boundaries and revision triggers.
- Correct abstention on the insufficient-evidence scenario.

Critical limit:

- In `conflicting_evidence_001`, DeepSeek treated the newer instruction as the current preference despite the explicit absence of supersession evidence. This is `UNSUPPORTED_CONFLICT_RESOLUTION` and a material violation of the same core conflict-preservation semantic.

Verdict: **NOT_SUITABLE**

Reason: DeepSeek is otherwise strong and concise, but resolving an intentionally unresolved contradiction through recency creates unsafe personal-state certainty. Under the frozen PIT definition, that is sufficient to block current use as the primary PIT teacher.

Required guardrails before reconsideration:

- conflicting-evidence abstention check;
- supersession evidence requirement;
- confidence calibration for unresolved contradictions.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-13.1.B scope**.

## 6. Candidate Review — MiniMax M3

Candidate: `minimax/minimax-m3:free`

Strengths:

- Preserved the contradiction in `conflicting_evidence_001` and explicitly requested clarification rather than manufacturing certainty.
- Correctly abstained on insufficient evidence.
- Strong stable-pattern, drift, correction, rare-exception, and long-term lifecycle handling.
- Strong personalization-safety behavior across ambiguity and exception cases.
- Clear applicability boundaries and generally useful revision triggers.

Critical limit:

- MiniMax introduced unsupported operational rules in revision logic, including a sixty-day preference-decay condition not grounded in the frozen evidence. This is `MINOR_UNSUPPORTED_HEURISTIC` to `MATERIAL_UNSUPPORTED_HEURISTIC` depending on whether such rules are allowed to drive downstream state updates. Under the current evidence it is treated as a material limit requiring a guardrail, but it does not invalidate the core inference in the tested scenarios.

Verdict: **QUALIFIED_WITH_LIMITS**

Reason: MiniMax demonstrates the strongest preservation of core PIT uncertainty semantics in the frozen evidence, including the deliberate conflict test. Its unsupported heuristic invention prevents unrestricted qualification, but the limitation is narrower and more guardrail-addressable than conflict collapse.

Required guardrails:

- unsupported-heuristic detector or evidence-bound revision-trigger validator;
- provenance requirement for any numeric/time threshold introduced into a Teaching Signal;
- reject or strip policy rules that cannot be traced to scenario evidence or a separately frozen policy.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-13.1.B scope**.

## 7. Cross-Candidate Semantic Comparison

| Dimension | Qwen3.7 | DeepSeek V4 Pro | MiniMax M3 |
| --- | --- | --- | --- |
| Pattern Understanding | Strong | Strong | Strong |
| Temporal Reasoning | Strong | Strong | Strong |
| Correction Recovery | Strong | Strong | Strong |
| Conflict Handling | **Material failure: recency-based collapse** | **Material failure: recency-based collapse** | **Strong: preserved conflict and requested clarification** |
| Insufficient Evidence | Correct abstention | Correct abstention | Correct abstention |
| Rare Exception | Strong | Strong | Strong |
| Pattern Lifecycle | Strong | Strong | Strong |
| Evidence Grounding | Strong primary grounding; unsupported conflict rule and dark-mode threshold | Strong primary grounding; unsupported conflict rule | Strong primary grounding; some unsupported operational heuristics |
| Unsupported Heuristic Risk | Moderate | Moderate, concentrated in conflict resolution | Moderate, concentrated in revision-policy invention |
| Personalization Safety | Limited by conflict collapse | Limited by conflict collapse | Strongest under tested ambiguity cases |
| Teaching Signal Usability | Strong structure | Strong and concise | Strong but sometimes over-elaborate |

The decisive dimension is not aggregate quality. It is whether unresolved personal evidence remains unresolved. Under the frozen PIT semantics, MiniMax is the only reviewed candidate that passed this critical discriminator.

## 8. Unsupported Heuristic Analysis

Qwen3.7:

- `UNSUPPORTED_CONFLICT_RESOLUTION`: newest observation treated as automatically superseding older contradictory evidence.
- `MINOR_UNSUPPORTED_HEURISTIC`: specific dark-mode evidence-count/time-window revision rule introduced without provenance.

DeepSeek V4 Pro:

- `UNSUPPORTED_CONFLICT_RESOLUTION`: recency used as sufficient basis to resolve an explicitly unresolved conflict.

MiniMax M3:

- `MINOR_UNSUPPORTED_HEURISTIC` / guardrail-relevant policy invention: sixty-day preference-decay logic and other operational revision conditions not grounded in the scenario evidence.

These findings are distinct from general reasoning strength. They matter because unsupported rules can become false personal-state update policies if used as teacher supervision.

## 9. Qualification Verdicts

| Candidate | Verdict | Critical basis |
| --- | --- | --- |
| `qwen/qwen3.7-max:free` | **NOT_SUITABLE** | Material unresolved-conflict collapse plus unsupported revision heuristic |
| `deepseek/deepseek-v4-pro` | **NOT_SUITABLE** | Material unresolved-conflict collapse |
| `minimax/minimax-m3:free` | **QUALIFIED_WITH_LIMITS** | Preserves core uncertainty semantics; unsupported heuristic invention requires guardrails |

Qualified or qualified-with-limits candidates: **1 / 3**.

No candidate receives unrestricted `QUALIFIED` under the current evidence.

## 10. Strongest Current Candidate

**`minimax/minimax-m3:free` — `STRONGEST_CURRENT_PIT_CANDIDATE_UNDER_PIT_13_EVIDENCE`**

This is not a final teacher selection.

Critical discriminator: MiniMax preserved unresolved conflicting evidence and requested clarification, while Qwen3.7 and DeepSeek converted the same ambiguity into an unsupported current preference.

## 11. Limitations of PIT-14

- Seven frozen scenario instances are sufficient for this qualification review but do not establish broad robustness.
- Each semantic family has limited instance diversity.
- PIT-14 evaluates candidate behavior under the current xKiro/model/prompt interface only.
- No adversarial perturbation, repeated-seed robustness, paraphrase invariance, or guardrail intervention has yet been tested.
- Qualification here does not imply local deployment feasibility or production readiness.

## 12. Recommended Next Experiment

**PIT-15 — Teaching Signal Guardrail Experiment**

Smallest justified next step:

Test whether explicit, model-agnostic guardrails can prevent the two observed PIT failure classes without weakening valid lifecycle reasoning:

1. preserve unresolved conflict unless explicit supersession evidence exists;
2. reject unsupported numeric/time/policy heuristics unless grounded in evidence or a frozen policy source.

Run this as a focused controlled experiment on the existing reviewed candidates before any teacher selection, distillation, training, or MindForge integration.
