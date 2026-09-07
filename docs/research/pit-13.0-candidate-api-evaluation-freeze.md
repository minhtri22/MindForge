# PIT-13.0 Candidate API Evaluation Freeze

Status:

Completed

## Research objective

Freeze API-based candidate evaluation protocol before any model execution.

PIT qualification starts with API-accessible teachers so teaching capability can be evaluated before local deployment feasibility.

## API execution layer

Execution gateway:

xKiro API

Role:

Access layer only.

xKiro is not a teacher candidate. Teacher candidates are models exposed through the API.

API compatibility:

OpenAI-compatible chat completion interface.

Model selection:

Explicit model identifier only. No automatic model switching.

## Candidate execution pool

- Qwen family
- DeepSeek family
- MiniMax family
- GLM family
- Other free API candidates meeting reproducible access requirements

## Deferred candidates

- GPT frontier
- Claude
- Gemini

Deferred does not mean rejected. These remain in the theoretical candidate universe.

## Evaluation configuration

Each execution records candidate name, provider, model id, API endpoint, execution date, temperature, max tokens, prompt versions, response format, retry policy, timeout policy, and streaming policy.

## Teaching Signal contract

Required output:

- Observation
- Inference
- Confidence
- Applicability Boundary
- Revision Trigger
- Evidence references
- Exception handling

## Evaluation rules

- Same scenario set
- Same evaluation contract
- No adaptive prompting
- No per-model prompt optimization
- No manual answer correction
- No scoring changes after execution

## Acceptance criteria

Allowed conclusions:

- PROMISING
- NEEDS MORE EVIDENCE
- LIMITED FIT
- NOT SUITABLE

Not allowed:

- WINNER
- BEST MODEL
- FINAL TEACHER

## Next step

PIT-13.1 Candidate API Evidence Collection
