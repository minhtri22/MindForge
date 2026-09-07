# PIT-13.0.1 API Candidate Manifest Freeze

Status: Completed

## Purpose

Freeze API candidate configuration before any API inference execution.

## API Provider

Execution provider: xKiro API

Role: API access layer only. xKiro is not a teacher candidate.

Authentication:

- External environment credential only
- API key is not stored in documentation or repository history

## Candidate Manifest

| Candidate | Model ID | Role |
| --- | --- | --- |
| Qwen3.8-Max | qwen/qwen3.8-max:free | General Intelligence Teacher candidate |
| DeepSeek V4 Pro | deepseek/deepseek-v4-pro | Reasoning / reflection teacher candidate |
| MiniMax M3 | minimax/minimax-m3:free | Long-context teacher candidate |
| Mistral Small 2603 | mistralai/mistral-small-2603 | Efficient general teacher candidate |

## Future Execution Metadata

Each execution must record:

- candidate_id
- provider
- model_id
- role
- execution_date
- API endpoint
- system prompt version
- PIT evaluation prompt version
- temperature
- max_tokens
- response format
- retry policy
- timeout policy

## Evaluation Contract

Interface: OpenAI-compatible chat completion API.

Teaching Signal output:

- Observation
- Inference
- Confidence
- Applicability Boundary
- Revision Trigger

## Deferred Candidates

Deferred, not rejected:

- GPT frontier
- Claude
- Gemini
- GLM

Reason: no current reproducible execution access in this research phase.

## Execution Rules

Freeze:

- scenario set
- system prompt
- evaluation prompt
- temperature
- output schema
- scoring criteria

No model-specific prompt tuning or manual answer repair during evaluation.

## Next Step

PIT-13.1 Candidate API Evidence Collection
