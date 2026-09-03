# Track A N3.R1-A — Qwen3.8-27B External Reference Qualification Protocol

Status: **PASS / PROTOCOL FROZEN / LOCAL EXECUTION NOT STARTED**

Authority:
- `docs/research/track-a-reference-model-policy.md`
- `docs/research/track-a-foundation-protocol.md`

## Purpose

Determine whether Qwen3.8-27B is useful as a reproducible external reference/teacher candidate for Track A. It is not a compact-model candidate and does not alter the MKS model contract.

## Model identity frozen for first qualification

```text
canonical upstream: Qwen/Qwen3.8-27B
license: Apache-2.0
model class: dense 27B vision-language causal model
language-model layers: 64
native context: 262,144
local artifact target: ggml-org/Qwen3.8-27B-GGUF
quantization: Q4_K_M
qualification: text-only
vision projector: not required
runtime: llama.cpp
```

Exact downloaded filename, bytes, SHA256, llama.cpp version/build/backend and runtime settings must be recorded in N3.R1-B.

## Context matrix

Characterize 4096 / 8192 / 16384. 4096 must be stable. 8192 must be stable for admission as a local Track-A reference. 16384 is characterization only. First semantic reference score uses 8192.

## Prompt freeze

Prompt version: `track-a-reference-json-v1`.

Each request receives only family, user utterance, current context, personal state, available actions/local capabilities/external capabilities, and required output schema.

Forbidden in prompt: expected labels, benchmark truth, target answer, or counterfactual-partner truth.

Model returns one JSON object. Thinking/prose is not benchmark truth and is excluded from parsed prediction.

## Decoding

```text
temperature = 0
seed = 20260904
one response per case
no majority vote
no self-consistency
no tools
no web/retrieval
no vision
```

## Qualification sequence

1. Artifact identity: path, bytes, SHA256, source, license.
2. Runtime smoke: 10 fixed short prompts at 4096; require 10/10 completion, no OOM/crash, valid text.
3. Context characterization: same workload at 4096/8192/16384.
4. Calibration/development qualification: prompt/parser corrections allowed only here; each correction increments prompt version.
5. Freeze prompt.
6. Held-out reference evaluation: run the 700 frozen held-out cases once; score with `scripts/score_track_a_v1.py`; no post-heldout tuning.

## Resource measures

Record RAM before/after load, peak RAM where practical, load time, context, prompt tok/s, decode tok/s, end-to-end latency, completion/parse rate, and OOM/crash count. Do not infer Arc/iGPU results from other hardware.

## Semantic classification

```text
TUE PASS -> ADMIT_STRONG_REFERENCE
RVE PASS but TUE FAIL -> ADMIT_LIMITED_REFERENCE
RVE FAIL -> REJECT_AS_QUALITY_REFERENCE
```

This does not make Qwen3.8 a size-sweep candidate.

## Local practicality

```text
PRACTICAL: 8192 stable and decode >= 4 tok/s
CONSTRAINED: 4096/8192 stable and decode >= 1 but < 4 tok/s
IMPRactical: 4096 unstable/OOM/crash or decode < 1 tok/s
```

These are qualification labels, not product SLAs.

## Determinism

Preselect 20 calibration/development cases; run each twice after prompt freeze. Report parsed-prediction exact-match rate; target >=95%.

## Leakage protection

Forbidden: feeding expected labels to Qwen; using Qwen as final truth authority; tuning on held-out errors; teacher-generating training data from held-out truth; distilling held-out responses before benchmark closure.

## Sandbox harness validation

`scripts/run_qwen38_track_a_reference.py` implements a local OpenAI-compatible llama.cpp-server client. Sandbox dry-run on seven calibration cases completed 7/7 and explicit prompt inspection found no `expected` truth field leakage. No model was downloaded or executed.

## Decision

```text
N3.R1-A: PASS / PROTOCOL READY
QWEN3.8-27B: NOT YET QUALIFIED
N3.R1-B: REQUIRES USER WINDOWS MACHINE
REFERENCE ADMISSION: PENDING
DISTILLATION: NOT AUTHORIZED
MODEL CONTRACT CHANGE: NO
TRACK-A N4: NOT AUTHORIZED
```
