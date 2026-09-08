# PIT-14.1.D Expanded Candidate Qualification Review

## 1. Purpose

Review the frozen PIT-14.1.C NVIDIA NIM evidence and compare the five expanded candidates against the existing PIT-14 references under the same Personal Intelligence qualification semantics.

This milestone performs no API calls, reruns, new inference generation, training, distillation, or MindForge integration.

## 2. Evidence Boundary

NVIDIA candidates reviewed from `experiments/pit14_1/evidence/`:

- `moonshotai/kimi-k3`
- `meta/muse-glimmer-30b`
- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `google/gemma-4-31b-it`
- `openai/gpt-oss-20b`

Existing frozen PIT-14 references retained unchanged:

- `qwen/qwen3.7-max:free` — `NOT_SUITABLE`
- `deepseek/deepseek-v4-pro` — `NOT_SUITABLE`
- `minimax/minimax-m3:free` — `QUALIFIED_WITH_LIMITS`

The frozen seven-scenario manifest and PIT-13.1.B metric rubric are reused as evidence provenance. Existing candidate outputs and prior verdicts are not modified.

Kimi K3 has incomplete long-term evidence because `long_term_consistency_001` returned HTTP 429 during PIT-14.1.C. That missing behavior is not inferred and is not retried here.

## 3. Qualification Criteria

The same PIT-14 semantic priorities apply:

- unresolved conflicting evidence must remain unresolved unless evidence supports supersession;
- explicit user correction overrides prior inference;
- insufficient evidence must not become a stable personal claim;
- rare exceptions must not overwrite stable patterns;
- recency alone is not evidence of truth or supersession;
- unsupported numeric, temporal, fallback, or policy rules are qualification risks even when the primary inference is correct;
- applicability boundaries and revision triggers must remain evidence-grounded and safe for downstream Teaching Signal use.

No new numeric threshold or post-hoc scoring formula is introduced.

## 4. NVIDIA Candidate Reviews

### 4.1 Kimi K3

Candidate: `moonshotai/kimi-k3`

Strengths:

- Strong stable-pattern, preference-drift, correction, rare-exception, and insufficient-evidence handling in the six completed scenarios.
- Generally clear applicability boundaries and revision triggers.

Critical limits:

- In `conflicting_evidence_001`, Kimi partially resolves the deliberately unresolved conflict by treating the newer instruction as the best current default. This is `UNSUPPORTED_CONFLICT_RESOLUTION` because no correction, retraction, or contextual supersession evidence is present.
- `long_term_consistency_001` is unavailable because the single frozen attempt returned HTTP 429. No conclusion is drawn from the missing sample.

Verdict: **NOT_SUITABLE**

Reason: the observed conflict-collapse behavior is a material failure in a core Personal Intelligence semantic. The missing long-term sample lowers evidence completeness but does not negate the directly observed material failure.

Evidence confidence: **MODERATE-HIGH within the six completed PIT-14.1.C scenarios; incomplete for long-term consistency**.

### 4.2 Muse Glimmer 30B

Candidate: `meta/muse-glimmer-30b`

Strengths:

- Preserves unresolved conflicting evidence and explicitly avoids manufacturing supersession.
- Correctly abstains on insufficient evidence.
- Correctly applies explicit correction precedence.
- Keeps the rare regulatory/legal case scoped as a task-specific exception rather than replacing the stable checklist-first pattern.
- Strong long-term consistency behavior with the throwaway-test exception kept separate from costly benchmark policy.
- No unsupported heuristic or material semantic failure is identified in the frozen seven-scenario evidence profile.

Limit:

- The evidence set contains one instance per scenario family and therefore does not establish paraphrase, adversarial, or repeated-seed robustness.

Verdict: **QUALIFIED**

Reason: within the frozen PIT scope, Muse Glimmer is the only reviewed candidate with complete evidence, preserved core uncertainty semantics, correct lifecycle behavior, and no identified unsupported heuristic requiring a guardrail.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-14.1.C scope**.

### 4.3 Nemotron 3.5 Lightning 30B-A3B

Candidate: `nvidia/nemotron-3.5-lightning-30b-a3b`

Strengths:

- Preserves unresolved conflict.
- Correctly handles insufficient evidence, correction, drift, rare exception, and long-term consistency.
- Produces broadly usable Teaching Signals across all seven scenarios.

Critical limit:

- Revision logic introduces unsupported operational policies, including a three-consecutive-interaction threshold and satisfaction-metric decline trigger.
- The long-term applicability boundary also defaults tasks without explicit cost/value signaling toward discard-after-validation, which is broader than the supplied evidence.

Verdict: **QUALIFIED_WITH_LIMITS**

Reason: the core semantic inference remains safe in the frozen scenarios, but unsupported operational rules could become false downstream state-update policy if consumed without evidence-bound guardrails.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-14.1.C scope**.

### 4.4 Gemma 4 31B IT

Candidate: `google/gemma-4-31b-it`

Strengths:

- Strong stable-pattern, drift, correction, rare-exception, insufficient-evidence, and long-term handling.
- Clear, concise Teaching Signal structure.

Critical limit:

- In `conflicting_evidence_001`, Gemma infers that the preference shifted and treats the most recent instruction as likely current despite the explicit absence of supersession evidence. This is `UNSUPPORTED_CONFLICT_RESOLUTION`.

Verdict: **NOT_SUITABLE**

Reason: recency-based conflict collapse violates the same critical PIT semantic that blocked Qwen3.7 and DeepSeek V4 Pro.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-14.1.C scope**.

### 4.5 GPT-OSS 20B

Candidate: `openai/gpt-oss-20b`

Strengths:

- Preserves unresolved conflicting evidence and asks for clarification.
- Correctly abstains on insufficient evidence.
- Strong correction, rare-exception, and long-term lifecycle handling.
- Complete 7/7 evidence and schema-valid Teaching Signals.

Critical limit:

- In the conflict case it proposes a balanced summary-plus-inline fallback if clarification cannot be obtained. That fallback is not grounded in the supplied evidence.
- Some applicability and future-policy wording extends beyond the exact observed scope.

Verdict: **QUALIFIED_WITH_LIMITS**

Reason: core uncertainty semantics remain intact, but unsupported fallback and scope-generalization language require an evidence-bound policy guardrail before use as an unrestricted teacher.

Evidence confidence: **HIGH within the frozen seven-scenario PIT-14.1.C scope**.

## 5. Expanded Cross-Candidate Comparison

| Candidate | Conflict handling | Insufficient evidence | Lifecycle quality | Unsupported heuristic / policy risk | Verdict |
| --- | --- | --- | --- | --- | --- |
| `qwen/qwen3.7-max:free` | Material failure: recency-based collapse | Correct abstention | Strong | Conflict rule + dark-mode threshold | `NOT_SUITABLE` |
| `deepseek/deepseek-v4-pro` | Material failure: recency-based collapse | Correct abstention | Strong | Conflict rule | `NOT_SUITABLE` |
| `minimax/minimax-m3:free` | Preserved conflict | Correct abstention | Strong | Unsupported preference-decay / revision heuristics | `QUALIFIED_WITH_LIMITS` |
| `moonshotai/kimi-k3` | Material failure: partial recency-based collapse | Correct abstention | Long-term sample missing | Recency default-selection rule | `NOT_SUITABLE` |
| `meta/muse-glimmer-30b` | Preserved conflict | Correct abstention | Strong | None identified in frozen evidence | `QUALIFIED` |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | Preserved conflict | Correct abstention | Strong | Unsupported thresholds, external metric trigger, broader discard default | `QUALIFIED_WITH_LIMITS` |
| `google/gemma-4-31b-it` | Material failure: recency-based collapse | Correct abstention | Strong | Recency supersession rule | `NOT_SUITABLE` |
| `openai/gpt-oss-20b` | Preserved conflict | Correct abstention | Strong | Unsupported fallback and scope generalization | `QUALIFIED_WITH_LIMITS` |

Expanded qualified / qualified-with-limits count: **4 / 8 reviewed candidates**.

Unrestricted `QUALIFIED`: **1 / 8**.

## 6. Strongest Current Candidate

**`meta/muse-glimmer-30b` — `STRONGEST_CURRENT_PIT_CANDIDATE_UNDER_EXPANDED_PIT_14_1_EVIDENCE`**

This is not a final teacher selection.

Critical basis:

- preserves unresolved conflict;
- abstains under insufficient evidence;
- respects explicit correction precedence;
- preserves rare exceptions without replacing stable patterns;
- maintains long-term evidence/checkpoint policy boundaries;
- has complete 7/7 evidence;
- has no unsupported heuristic identified in the frozen candidate profile.

MiniMax M3, Nemotron 3.5 Lightning, and GPT-OSS 20B remain credible candidates but require evidence-bound guardrails for unsupported operational or fallback policy invention.

## 7. Implication for PIT-15

PIT-14.1.D does not remove the need for a guardrail experiment. The expanded evidence strengthens its justification while refining the target population.

Recommended next step remains:

**PIT-15 — Teaching Signal Guardrail Experiment**

The smallest justified controlled experiment should test whether model-agnostic guardrails can:

1. block recency-based conflict collapse unless explicit supersession evidence exists;
2. reject unsupported numeric, temporal, fallback, or policy rules unless grounded in evidence or a separately frozen policy source;
3. preserve the valid behavior of Muse Glimmer while improving MiniMax, Nemotron, and GPT-OSS without degrading correction, exception, and lifecycle handling.

No teacher selection, training, distillation, or MindForge integration is authorized by this review.

## 8. Scope Closure

- API calls: 0.
- Reruns: 0.
- New inference evidence: 0.
- Existing PIT-13/PIT-14/PIT-14.1.C evidence modified: NO.
- Historical verdicts modified: NO.
- Training: NO.
- Distillation: NO.
- Teacher selected: NO.
- MindForge integration: NO.
- Kernel / TokenModel / PPF changes: NO.

PIT-14.1.D status: **COMPLETED**.
