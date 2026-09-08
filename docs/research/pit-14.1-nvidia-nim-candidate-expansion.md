# PIT-14.1 NVIDIA NIM Candidate Expansion

## 1. Purpose

Freeze an additional external PIT teacher-candidate pool served through NVIDIA NIM before any inference execution.

Research question:

Do any NVIDIA NIM-accessible candidates outperform or materially alter the PIT-14 candidate picture under the same frozen Personal Intelligence semantics?

PIT-14.1.A is a documentation and execution-contract freeze only. It performs no API call, inference, qualification, ranking, training, distillation, or MindForge integration.

## 2. Existing PIT-14 State

The existing PIT-14 review remains unchanged:

- `qwen/qwen3.7-max:free`: `NOT_SUITABLE`
- `deepseek/deepseek-v4-pro`: `NOT_SUITABLE`
- `minimax/minimax-m3:free`: `QUALIFIED_WITH_LIMITS`
- `mistralai/mistral-small-2603`: semantic review not performed because full PIT-13.1.B evidence was not collected

Current strongest candidate under PIT-13 evidence remains:

`minimax/minimax-m3:free` — `STRONGEST_CURRENT_PIT_CANDIDATE_UNDER_PIT_13_EVIDENCE`

This is not a final teacher selection and must be reassessed after the NVIDIA expansion evidence is complete.

## 3. NVIDIA NIM Execution Layer

Provider / gateway:

`NVIDIA NIM API`

Base URL:

`https://integrate.api.nvidia.com/v1`

Chat Completions endpoint:

`/chat/completions`

Authentication environment variable:

`NVIDIA_API_KEY`

NVIDIA NIM is an execution layer only and is not a PIT teacher candidate.

Security rules:

- Read the credential from the process environment only during execution phases.
- Never print, serialize, store, or commit the credential.
- Never commit `.env`.
- Do not read `NVIDIA_API_KEY` during PIT-14.1.A.

## 4. Candidate Manifest

The PIT-14.1 NVIDIA candidate manifest is frozen exactly as follows:

| Candidate ID | Initial access status |
| --- | --- |
| `moonshotai/kimi-k3` | `ACCESS_UNVERIFIED` |
| `meta/muse-glimmer-30b` | `ACCESS_UNVERIFIED` |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | `ACCESS_UNVERIFIED` |
| `google/gemma-4-31b-it` | `ACCESS_UNVERIFIED` |
| `openai/gpt-oss-20b` | `ACCESS_UNVERIFIED` |

No candidate may be added, removed, replaced, or silently substituted within PIT-14.1.B/C without a separate reviewed manifest amendment.

## 5. Common PIT Contract

All NVIDIA candidates must use the existing frozen PIT Teaching Signal contract:

- `observation`
- `inference`
- `confidence`
- `applicability_boundary`
- `revision_trigger`

The following PIT semantics remain authoritative:

- `CONFLICTING != RESOLVED`
- `INSUFFICIENT != NEGATIVE`
- `RECENT != AUTOMATICALLY_SUPERSEDING`
- explicit correction overrides a prior inference
- `NO_OBSERVATION != OBSERVABLE_NON_OCCURRENCE`

No NVIDIA-specific semantic prompt tuning is permitted.

Scenario scope remains the existing seven PIT families:

1. Stable Preference
2. Preference Drift
3. Conflicting Evidence
4. User Correction
5. Rare Exception
6. Insufficient Evidence
7. Long-Term Consistency

PIT-14.1.B may use the existing four-scenario smoke subset. PIT-14.1.C must preserve the same seven-family scope used by PIT-13/PIT-14.

## 6. Transport Compatibility Policy

Transport differences may be adapted only when required to make the same semantic request executable through NVIDIA NIM.

Allowed compatibility adaptations include:

- `stream` compatibility
- supported `response_format` compatibility
- model-specific reasoning transport controls
- required `chat_template_kwargs`
- model-specific API token ceilings

Every such adaptation must be documented before the affected candidate's first evidence-producing request.

Forbidden semantic adaptation includes:

- rewriting the PIT instruction because a candidate fails a semantic test
- adding candidate-specific clarification hints
- changing scenario wording
- adding examples or answers for one candidate
- weakening schema or qualification thresholds

Transport compatibility must preserve the same task meaning.

## 7. Structured Output Policy

Frozen policy: **POLICY B — prompt-enforced JSON for all candidates**.

Rationale:

- Strict comparability is more important than exploiting candidate-specific structured-output capabilities.
- Access and feature support for the five frozen model IDs is still unverified in PIT-14.1.A.
- Using native JSON mode only for a subset would create an asymmetric serialization advantage during qualification.
- The existing PIT contract already relies on deterministic parsing and model-agnostic normalization.

Therefore PIT-14.1.B/C must use the same JSON-only PIT instruction for all candidates and must not add `response_format={"type":"json_object"}` selectively.

If later evidence proves that a model cannot execute the common prompt-enforced contract without a transport-only compatibility mechanism, that fact must be documented prospectively before any amended execution. It must not be introduced after observing semantic output quality.

## 8. Reasoning Policy

Frozen policy: **POLICY R1 — direct / non-thinking response where technically supported**.

Rationale:

- PIT evaluates the final Teaching Signal, not hidden or extended reasoning traces.
- Extended reasoning can consume the output budget and truncate the required Teaching Signal JSON.
- NVIDIA NIM exposes model-dependent reasoning controls rather than one uniform parameter across all model families.

Execution rule:

- Prefer disabling extended thinking where a documented transport control exists.
- Do not add candidate-specific reasoning instructions to the semantic prompt.
- If a candidate does not expose a semantically equivalent disable control, use the provider-supported default and record that as a transport compatibility exception before evidence execution.
- Reasoning controls must never be changed after observing candidate semantic performance.

## 9. Temperature and Token Policy

Temperature:

`temperature = 0`

Reason:

This preserves the existing PIT execution setting and minimizes avoidable sampling variance. A model-specific compatibility exception is allowed only if the API rejects the frozen value; that exception must be documented before candidate evidence is collected.

Maximum output budget:

`max_tokens = 4096`

Reason:

- Large enough for a complete five-field Teaching Signal under the observed PIT evidence shape.
- Small enough to avoid adopting oversized sample-code defaults unrelated to PIT.
- Compatible with the direct/non-thinking target so budget is reserved for the final JSON rather than reasoning traces.

If a candidate has a lower API ceiling, use the highest supported value at or below 4096 and record the ceiling before execution. Do not increase a single candidate above 4096 for semantic advantage.

Streaming:

`stream = false`

Reason:

Each evidence record should preserve one canonical complete API response. If a candidate technically requires streaming, the transport layer may assemble the stream into one raw response artifact without altering semantic content, and that exception must be frozen before evidence execution.

## 10. Smoke Qualification Policy

Reuse the PIT-13.1.A.2 **PER-CANDIDATE** gate.

A candidate becomes `SMOKE_QUALIFIED` only if all frozen smoke cases satisfy:

- API completion for every smoke case
- schema validity for every smoke case
- zero model identity mismatch
- zero credential leakage
- zero manual repair
- zero semantic retry
- zero per-model semantic tuning

One candidate failure must not block independently qualified candidates.

Initial candidate access state remains `ACCESS_UNVERIFIED` until PIT-14.1.B.

## 11. Full Evidence Policy

Only `SMOKE_QUALIFIED` NVIDIA candidates may proceed to PIT-14.1.C.

PIT-14.1.C must preserve:

- the same seven PIT scenario families
- the same Teaching Signal schema
- the same semantic criteria
- the same no-manual-repair rule
- the same no-semantic-retry rule
- the same model identity validation
- the same candidate-specific evidence boundary

Transport compatibility metadata must be recorded alongside each candidate so PIT-14.1.D can separate provider mechanics from teacher semantics.

## 12. Cross-Candidate Comparison Policy

PIT-14.1.D will compare new NVIDIA candidates against the already-frozen PIT-14 references:

- Qwen3.7
- DeepSeek V4 Pro
- MiniMax M3

The existing candidates should not be rerun unless a later protocol decision demonstrates that the comparison is invalid without a fairness rerun.

The comparison must prioritize the same core Personal Intelligence semantics, especially conflict preservation, correction handling, insufficient-evidence abstention, evidence grounding, unsupported heuristic invention, and pattern lifecycle quality.

## 13. Security and Provenance

PIT-14.1.A creates no inference evidence.

Frozen provenance boundary:

- candidate IDs frozen before API access validation
- policies frozen before candidate outputs exist
- NVIDIA transport treated separately from model semantics
- no credential read during this milestone
- existing PIT-13/PIT-14 evidence remains immutable
- existing PIT-14 verdicts remain unchanged

Every future execution record must capture at least:

- `provider`
- `candidate_id`
- `requested_model`
- `returned_model` if supplied
- scenario ID
- timestamp
- transport compatibility parameters actually used

Silent model substitution is a failure.

## 14. Frozen Execution Sequence

The NVIDIA candidate-expansion sequence is frozen as:

1. `PIT-14.1.A` — NVIDIA NIM Candidate Manifest & Execution Freeze
2. `PIT-14.1.B` — NVIDIA NIM Smoke Qualification
3. `PIT-14.1.C` — NVIDIA NIM Full Evidence Collection
4. `PIT-14.1.D` — Expanded Candidate Qualification Review

Only after PIT-14.1.D may the research track reassess whether `PIT-15 Teaching Signal Guardrail Experiment` remains the smallest justified next step.

PIT-15 is not started by this milestone.

## PIT-14.1.B NVIDIA NIM Smoke Qualification

Status: **COMPLETED**

Execution date: 2026-09-08.

Runner: `scripts/pit14_1/run_nvidia_smoke.py`

Runner SHA256: `6a43760bffcf9cbc6a9d40b1c3e2877f5b4dbf45779e66924bc40b5f8d1100b5`

Provider: `NVIDIA NIM`

Frozen candidates executed:

- `moonshotai/kimi-k3`
- `meta/muse-glimmer-30b`
- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `google/gemma-4-31b-it`
- `openai/gpt-oss-20b`

Frozen smoke scenarios:

- `stable_preference_001`
- `preference_drift_001`
- `user_correction_001`
- `insufficient_evidence_001`

Scenario source: `experiments/pit13/smoke/scenarios.json`

Scenario SHA256: `af797edf9aa70aff74df219e9444b27b3ac1ea9ec10bbfb9476a3708cc8cb1df`

Planned samples: 20 (`5 candidates x 4 scenarios`).

| Candidate | API completed | Schema valid | Identity mismatch | Smoke status |
| --- | ---: | ---: | ---: | --- |
| `moonshotai/kimi-k3` | 4/4 | 4/4 | 0 | `SMOKE_QUALIFIED` |
| `meta/muse-glimmer-30b` | 4/4 | 4/4 | 0 | `SMOKE_QUALIFIED` |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 4/4 | 4/4 | 0 | `SMOKE_QUALIFIED` |
| `google/gemma-4-31b-it` | 4/4 | 4/4 | 0 | `SMOKE_QUALIFIED` |
| `openai/gpt-oss-20b` | 4/4 | 4/4 | 0 | `SMOKE_QUALIFIED` |

Pool summary:

- Completed API samples: 20/20.
- Schema-valid samples: 20/20.
- Smoke-qualified candidates: 5/5.
- Parse failures: 0.
- Identity mismatches: 0.
- Credential leakage: 0.
- Manual repair: 0.
- Semantic retries: 0.
- Per-model semantic tuning: 0.

Execution policies remained frozen:

- prompt-enforced JSON for all candidates;
- direct/non-thinking where technically supported;
- `temperature=0`;
- `max_tokens=4096`;
- `stream=false`;
- per-candidate smoke qualification.

Artifacts:

- `experiments/pit14_1/smoke/raw.jsonl`
- `experiments/pit14_1/smoke/normalized.jsonl`
- `experiments/pit14_1/smoke/results.json`
- `experiments/pit14_1/smoke/smoke-summary.json`
- `experiments/pit14_1/smoke/execution-metadata.json`

Interpretation boundary:

This smoke result establishes only machine-consumable PIT Teaching Signal interface compliance under the frozen NVIDIA execution contract. It does not establish semantic teacher quality.

No teacher ranking was performed. No semantic qualification verdict was assigned. No comparison against PIT-13 candidates was performed. No teacher was selected.

## PIT-14.1.C NVIDIA NIM Full Evidence Collection

Status: **COMPLETED**

Execution date: 2026-09-08.

Runner: `scripts/pit14_1/run_nvidia_evidence.py`

Runner SHA256: `8e7413dd2310c312912fe21373ad505474289fd536b85b68ec2057cb7473b05c`

Provider: `NVIDIA NIM`

Candidates executed:

- `moonshotai/kimi-k3`
- `meta/muse-glimmer-30b`
- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `google/gemma-4-31b-it`
- `openai/gpt-oss-20b`

Scenario families: 7.

Scenario provenance source: `experiments/pit13/evidence/scenarios.json`.

Scenario SHA256: `3f8c71eba9cadc18854c2c6bf9f76926f29243d37a968481a72d6b3b5ff43fc1`.

The NVIDIA execution copy at `experiments/pit14_1/evidence/scenarios.json` is byte-identical to the PIT-13.1.B source.

Metric rubric source: `experiments/pit13/evidence/metric-rubric.json`.

Metric rubric SHA256: `f34b52ba10c8f250e5a7c0e4226c70211be1600eaa6e4797254574c2a93e5227`.

Planned sample pairs: 35 (`5 candidates x 7 scenarios`).

All 35 planned pairs were attempted exactly once. API completion was 34/35 and schema validity was 34/35. The single non-completed sample was `moonshotai/kimi-k3` / `long_term_consistency_001`, where NVIDIA returned HTTP 429. It is preserved as `TRANSPORT_OR_API_FAILURE`; no retry or repair was performed.

| Candidate | Attempts | API completed | Schema valid | Evidence collection note |
| --- | ---: | ---: | ---: | --- |
| `moonshotai/kimi-k3` | 7/7 | 6/7 | 6/7 | One HTTP 429 on `long_term_consistency_001`; no retry |
| `meta/muse-glimmer-30b` | 7/7 | 7/7 | 7/7 | Complete |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 7/7 | 7/7 | 7/7 | Complete |
| `google/gemma-4-31b-it` | 7/7 | 7/7 | 7/7 | Complete |
| `openai/gpt-oss-20b` | 7/7 | 7/7 | 7/7 | Complete |

Candidate evidence profiling used only the already-frozen PIT-13.1.B metric rubric. `qualification_verdict` remains `null` for every NVIDIA candidate.

Descriptive semantic findings for later PIT-14.1.D review:

- Kimi K3: strong handling on available stable-pattern, drift, correction, rare-exception, and insufficient-evidence cases; the conflict case partially selects the newer instruction as the current default despite unresolved contradiction; long-term consistency evidence is missing due HTTP 429.
- Muse Glimmer 30B: preserves unresolved conflicting evidence, abstains on insufficient evidence, and produces bounded lifecycle signals across all seven scenarios.
- Nemotron 3.5 Lightning 30B-A3B: preserves unresolved conflict and strong lifecycle behavior; some revision triggers introduce unsupported operational thresholds or external signals.
- Gemma 4 31B IT: strong across most scenario families, but resolves the deliberately unresolved conflict via recency.
- GPT-OSS 20B: preserves unresolved conflict and handles lifecycle cases well; some fallback/boundary language extends beyond supplied evidence.

These are candidate evidence findings only. No qualification verdict, ranking, winner, or strongest-model declaration is made in PIT-14.1.C.

Artifacts:

- Raw: `experiments/pit14_1/evidence/raw/`
- Normalized: `experiments/pit14_1/evidence/normalized/`
- Metrics: `experiments/pit14_1/evidence/metrics/`
- Candidate profiles: `experiments/pit14_1/evidence/candidate-profiles.json`
- Evidence summary: `experiments/pit14_1/evidence/evidence-summary.json`
- Execution metadata: `experiments/pit14_1/evidence/execution-metadata.json`
- Scenario copy: `experiments/pit14_1/evidence/scenarios.json`

Scope controls:

- Manual repair: 0.
- Semantic retries: 0.
- Per-model semantic tuning: 0.
- Identity mismatches: 0.
- Parse failures: 0.
- No ranking.
- No winner declaration.
- No teacher selection.
- No cross-provider comparison.
- No training, distillation, or MindForge integration.

Next: `PIT-14.1.D Expanded Candidate Qualification Review`.

## PIT-14.1.D Expanded Candidate Qualification Review

Status: **COMPLETED**

Review source: frozen PIT-14.1.C evidence only. No API calls, reruns, or new inference evidence were produced.

NVIDIA qualification verdicts:

| Candidate | Verdict | Critical basis |
| --- | --- | --- |
| `moonshotai/kimi-k3` | `NOT_SUITABLE` | Material recency-based conflict collapse; long-term sample missing due preserved HTTP 429 |
| `meta/muse-glimmer-30b` | `QUALIFIED` | Preserved conflict and uncertainty semantics; complete 7/7 evidence; no unsupported heuristic identified |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | `QUALIFIED_WITH_LIMITS` | Core semantics preserved; unsupported operational thresholds/external signals require guardrails |
| `google/gemma-4-31b-it` | `NOT_SUITABLE` | Material recency-based conflict collapse |
| `openai/gpt-oss-20b` | `QUALIFIED_WITH_LIMITS` | Core conflict semantics preserved; unsupported fallback and scope-generalization language require guardrails |

Existing PIT-14 verdicts remain unchanged.

Strongest current candidate under expanded evidence:

`meta/muse-glimmer-30b` — `STRONGEST_CURRENT_PIT_CANDIDATE_UNDER_EXPANDED_PIT_14_1_EVIDENCE`

This is not a final teacher selection.

Detailed review: `docs/research/pit-14.1-d-expanded-candidate-qualification-review.md`.

Next: `PIT-15 Teaching Signal Guardrail Experiment`.
