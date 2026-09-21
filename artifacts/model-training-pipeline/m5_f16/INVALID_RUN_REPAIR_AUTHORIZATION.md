# M5 F16 — Invalid-Run Repair Authorization

## Status

AUTHORIZED — specification only.

This document authorizes one bounded repair to the M5 F16 runtime invocation contract.
It does not adjudicate F16 parity and does not authorize quantization, M6, or bulk training.

## Superseded invalid invocation

Local report:

`M5_F16_LOCAL_REPORT_20260921-200308.json`

Observed terminal classification:

- `overall_status = EXECUTION_FAIL`
- `scientific_outcome = UNADJUDICATED`
- `f16_result = null`
- `quantization_executed = false`
- `quantization_authorized = false`

The invocation reached exact HF prefetch, foundation regressions, exact llama.cpp checkout,
converter qualification, CMake configure/build, and build-manifest generation before the
F16 requalification harness was externally terminated.

No `M5_F16_REQUALIFICATION_RESULT.json` existed.

## Root cause

The pinned llama.cpp commit is:

`ce8caa6e60a03093351d6016a818720e0d46f0fb`

At this commit, `llama-cli` is conversational by default. With a predefined `--prompt`,
it generates the first assistant turn and then returns to the interactive input loop unless
`--single-turn` / `-st` is supplied.

The frozen MindForge runtime helper `run_llama_fixture()` launches `llama-cli` through
`subprocess.run(..., capture_output=True)` but does not pass `--single-turn`.
Therefore the child process can remain alive waiting for another user turn after generation,
preventing the harness from reaching its one-shot adjudicator.

This is a runtime invocation contract defect, not evidence about HF↔llama.cpp parity.

## Authorized repair

Exactly one scientific production change is authorized:

- add `--single-turn` to the `llama-cli` command constructed by
  `pipeline.m5.run_llama_fixture()`.

Required regression coverage:

- assert that `run_llama_fixture()` invokes `llama-cli` with `--single-turn`;
- preserve the existing prompt, model path, max-new-tokens, context length, sampling,
  seed, thread count, output parsing, task-success rule, and parity rule.

The M5 F16 workflow must include `pipeline/m5.py` and its regression test in its trigger
surface so this runtime contract cannot change silently.

## Explicitly forbidden changes

This repair must not change:

- model ID or pinned model revision;
- M2 tokenizer repair semantics;
- training phases, weights, checkpoints, datasets, fixtures, prompts, or expected answers;
- seed, context length, max-new-tokens, temperature, top-p, top-k, or thread count;
- llama.cpp commit or converter identity;
- F16 output type;
- parity/adjudication logic or thresholds;
- quantization authorization;
- M6 or bulk-training authorization.

## Identity and retry rule

The prior invocation is terminal `INVALID_INFRASTRUCTURE / UNADJUDICATED`.
The implementation commit produced by this authorization becomes a new scientific code
identity. A later helper-only commit may bind the local fallback runner to that exact
scientific commit/blob set.

Only one new execution is authorized after:

1. implementation diff is bounded to the authorized runtime contract and regression coverage;
2. regression tests are present;
3. local fallback provenance is rebound to the new scientific identity;
4. zero-science comparison proves the helper-only rebinding did not alter scientific files.

A genuine PASS or FAIL from the repaired one-shot harness must be adjudicated as-is and
must not be rescued by tuning.
