# Research Ledger

Append-only research milestones.

## PIT-6.1 Completion

Date: 2026-09-07

Milestone: PIT-6.1 — Adversarial Personal Pattern Simulator

Status: Completed

Summary:

Extended PIT simulator from simple repeated preference scenarios into adversarial personal intelligence scenarios.

Evidence:

Dataset: 150 cases

Seed: 42

Scenario coverage:

- Preference drift
- Conflicting evidence
- Rare exception
- User correction
- Insufficient evidence

Compared systems:

- Context only
- Memory retrieval only
- PIT teaching signal pipeline

Results:

Context only: 0.0

Memory retrieval: 0.6

PIT: 1.0

Decision improvement: 0.4

Interpretation:

PIT-6.1 demonstrates that a teaching signal can improve decisions in a controlled synthetic adversarial environment.

This validates the experimental direction.

This does not prove final PIT architecture, teacher model choice, production applicability, or MindForge integration strategy.

Key finding:

PIT value appears when reasoning over evolving preferences, contradictory evidence, conditional behavior, exceptions, and corrections.

Decision:

Proceed to next PIT research phase. Do not select model yet. Do not train yet.

Scope boundary:

No model downloaded. No training. No runtime changes. No PPF changes.


## PIT-7 Start / Completion

Date: 2026-09-07

Milestone: PIT-7 — Teacher Strategy Selection

Status: Completed

Summary:

Defined the PIT teacher strategy space before selecting any implementation candidate.

Analyzed candidate strategies:

- Memory-centric strategy
- Reflection-centric strategy
- Hybrid teacher strategy

Key finding:

PIT should be treated as a teaching capability and strategy layer, not as a single model choice.

Evaluation criteria defined:

- Decision improvement
- Pattern quality
- Correction recovery
- Drift handling
- Uncertainty calibration
- Evidence traceability

Decision:

Do not select a teacher model yet.
Proceed to teacher strategy evaluation protocol.

Scope boundary:

No model selection. No model download. No training. No runtime integration.

## PIT-11.2 Completion

Milestone:
PIT-11.2 Candidate Qualification Execution

Status:
Completed

Summary:

Applied PIT-10 frozen evaluation contract to candidate teacher qualification methodology.

Evaluation dimensions:

- Pattern understanding
- Temporal reasoning
- Correction recovery
- Uncertainty calibration
- Supervision quality
- Evidence traceability
- Pattern Lifecycle Quality

Key finding:

Candidate teachers must be evaluated through teaching signal evidence, not model capability alone.

Decision:

Proceed to evidence generation phase.

Scope:

No teacher selected.
No model integrated.
No training.
No MindForge changes.

## PIT-12.1 Candidate Access Policy

Status:
Completed

Summary:

Defined separation between theoretical candidate universe and executable candidate pool.

Key decision:

Lack of API access does not eliminate a candidate from theoretical PIT research.

Scope:

No model selected.
No model downloaded.
No inference.
No training.


## PIT-12.2 Candidate Execution Strategy Update

Status:

Completed

Summary:

Defined API-first candidate qualification strategy.

Key decision:

Local LLM evaluation is deferred until teacher capability is validated.

Claude/Gemini:

Deferred from execution pool due to access constraints.

Not rejected from research universe.

Scope:

No model selected.
No inference.
No training.
No runtime changes.

## PIT-13.0 Candidate API Evaluation Freeze

Status:

Completed

Summary:

Frozen API-first candidate execution strategy before model qualification.

Key decision:

Evaluate teacher capability before local deployment feasibility.

Scope:

No model executed.
No benchmark executed.
No training.
No MindForge integration.
## PIT-13.0.1 API Candidate Manifest Freeze

Status:

Completed

Summary:

Frozen API candidate manifest before model execution.

Candidates:

- Qwen3.8-Max
- DeepSeek V4 Pro
- MiniMax M3
- Mistral Small 2603

Execution layer:

xKiro API

Security:

API credential stored externally only.

Scope:

No API calls. No inference. No benchmark. No teacher selected.

## PIT-13.1 Candidate API Evidence Collection

Status:

Defined

Summary:

Defined PIT-13.1 evidence collection execution record using the frozen PIT-10 teaching signal contract.

Candidates:

- Qwen3.8-Max
- DeepSeek V4 Pro
- MiniMax M3
- Mistral Small 2603

Planned phases:

- Smoke qualification
- Evidence collection

Scope:

No final teacher selected.
No training.
No MindForge integration.


## PIT-13.1.A.0 Runner Validation

Status:

Completed

Summary:

Validated API runner implementation before evidence execution. The OpenAI-compatible request path returned HTTP 200 for one diagnostic request with `mistralai/mistral-small-2603`; the model ID was unchanged.

Scope:

No PIT evidence generated.
No teacher evaluated.
No benchmark executed.
Smoke qualification not started.

## PIT-13.1.A Smoke Qualification

Status:

Failed

Summary:

Executed one frozen 16-sample smoke run across four candidates and four scenarios. DeepSeek completed 4/4 with valid Teaching Signal schema. Qwen returned HTTP 500 for 4/4. MiniMax and Mistral produced eight parse-path failures whose raw responses were not retained by the runner. Overall schema validity was 4/16, so the smoke acceptance gate failed.

Infrastructure correction:

Updated the runner after the failed attempt to preserve raw responses on content parse failure, classify API and parse status separately, and flush each record. No candidate, scenario, prompt, schema, temperature, or scoring contract changed. The failed attempt was not rerun.

Scope:

No model-specific tuning.
No manual repair.
No ranking or teacher selection.
PIT-13.1.B not started.

## PIT-13.1.A Candidate Amendment — Qwen3.7-Max

Status:

Completed

Summary:

Replaced `qwen/qwen3.8-max:free` with `qwen/qwen3.7-max:free` for future PIT smoke execution after Qwen3.8 returned HTTP 500 for all four scenarios. xKiro listed the new model ID, and one non-evidence connectivity diagnostic returned HTTP 200 with an exact model identity match.

Scope:

Only the Qwen candidate ID changed.
Previous Qwen3.8 smoke evidence preserved unchanged.
No scenario, prompt, Teaching Signal schema, temperature, or scoring change.
No smoke rerun in this amendment.
No teacher selected.
PIT-13.1.B not started.

## PIT-13.1.A Smoke Retry — Qwen3.7 Amendment

Status:

Failed

Summary:

Executed one complete 16-sample smoke run using the amended Qwen3.7 candidate manifest. All 16 API requests completed with exact model identity matches and no credential leakage. Nine responses satisfied the frozen JSON schema. Three MiniMax and four Mistral responses wrapped JSON in Markdown code fences and failed strict parsing.

Scope:

No retries.
No model-specific tuning.
No manual output repair or fence stripping.
No prompt, schema, temperature, scoring, or PIT contract change.
No ranking or teacher selection.
PIT-13.1.B not started.

## PIT-13.1.A.1 Smoke Harness Contract Audit

Status:

COMPLETED

Scope:

Deterministic fence normalization frozen.
Scenario evidence mapping frozen.
No API evidence generated.
No teacher evaluated.
Previous PIT-13.1.A FAIL preserved.

## PIT-13.1.A Smoke Qualification Rerun

Status:

COMPLETED

Result:

FAIL

Evidence:

16 frozen samples executed with deterministic normalization active and frozen scenario evidence active. API completion was 16/16, schema validity was 15/16, model identity mismatches were 0, credential leakage was 0, and manual repair/retry count was 0.

Failure classification:

SERIALIZATION_NONCONFORMANCE_AFTER_FROZEN_NORMALIZATION

Scope:

No teacher ranking.
No teacher selection.
No training.
No MindForge integration.
PIT-13.1.B remains blocked.

## PIT-13.1.A.2 Smoke Gate Semantics Review

Status:

COMPLETED

Decision:

ADOPT_PER_CANDIDATE_GATE

Summary:

Reviewed the semantic unit of PIT-13.1.A smoke qualification against the frozen PIT teacher architecture. PIT-10, PIT-11.2, and PIT-12 define qualification evidence and verdicts per candidate, while PIT-12.1 already separates the research universe from the executable candidate pool. The smoke gate is therefore clarified prospectively as a per-candidate gate without changing any per-sample requirement or historical verdict.

Candidate consequences from the existing frozen rerun:

- Qwen3.7-Max: SMOKE_QUALIFIED
- DeepSeek V4 Pro: SMOKE_QUALIFIED
- MiniMax M3: SMOKE_QUALIFIED
- Mistral Small 2603: SMOKE_NOT_QUALIFIED

Pool state:

PARTIAL_CANDIDATE_QUALIFICATION

Scope:

No API calls.
No inference.
No evidence modified.
No raw response modified.
No parser or Teaching Signal contract change.
No teacher ranked.
No teacher selected.
Historical smoke FAIL verdicts preserved.
PIT-13.1.B not executed.

## PIT-13.1.B Evidence Collection

Status:

PARTIAL / BLOCKED BEFORE API EXECUTION

Candidates planned:

- Qwen3.7-Max
- DeepSeek V4 Pro
- MiniMax M3

Excluded:

- Mistral Small 2603 — `SMOKE_NOT_QUALIFIED`; zero PIT-13.1.B calls.

Preparation:

Frozen the seven-family evidence scenario manifest before candidate execution. Reused all four PIT-13.1.A.1 smoke instances verbatim and materialized the three required missing full-evidence families from existing PIT protocol semantics. Froze a candidate-level metric rubric before candidate outputs because PIT-10 defines dimensions but no numeric formulas.

Blocker:

`XTROUTER_API_KEY` was absent from the process environment. The credential contract forbids reading `.env` as a substitute, so no API execution was attempted.

Scope:

Raw candidate evidence generated: NO.
Normalized candidate evidence generated: NO.
Candidate metrics generated: NO.
No manual repair.
No semantic retries.
No per-model tuning.
No ranking.
No teacher selection.
No training.
No MindForge integration.

## PIT-13.1.B Evidence Collection — Resume and Completion

Status:

COMPLETED

Execution:

Resumed the previously prepared PIT-13.1.B run after explicit authorization to load `XTROUTER_API_KEY` from the existing local `.env` file. The credential was loaded into process memory only and was not printed, copied into evidence, or committed.

Candidates executed:

- Qwen3.7-Max: 7/7 API completed, 7/7 schema valid.
- DeepSeek V4 Pro: 7/7 API completed, 7/7 schema valid.
- MiniMax M3: 7/7 API completed, 7/7 schema valid.

Excluded:

- Mistral Small 2603 — `SMOKE_NOT_QUALIFIED`; PIT-13.1.B calls: 0.

Evidence:

Raw evidence generated: YES.
Normalized evidence generated: YES.
Candidate metrics generated: YES.
Candidate profiles generated: YES.
Total planned samples: 21.
Total completed samples: 21.
Schema-valid samples: 21.
Model identity mismatches: 0.
Manual repair: 0.
Semantic retries: 0.
Per-model tuning: 0.

Scope:

No ranking.
No winner declaration.
No qualification verdict.
No teacher selection.
No training.
No MindForge integration.
