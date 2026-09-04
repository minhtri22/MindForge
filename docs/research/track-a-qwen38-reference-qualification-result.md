# Track-A N3.R1-B — Qwen3.8-27B External Reference Qualification Result

## Executive result

Semantic reference verdict: **NOT EVALUATED**.

Local practicality verdict: **CONSTRAINED**.

The benchmark provenance gate was restored first and passed. Qwen3.8-27B Q4_K_M was acquired and runtime-characterized locally. A full held-out semantic qualification was not reached because calibration/development/determinism gates did not complete reliably enough for a valid one-shot held-out run.

## Benchmark provenance

Stage A restored the public materializer to the canonical R1 implementation with the Windows LF determinism fix.

```text
original reconstructed generator SHA-256:
41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d

patched generator SHA-256:
d9f2bf58b102d2cf9a19bba4468adc34de148682245e5e550bdbc6c18d6514b9

calibration.jsonl:
7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb

development.jsonl:
2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42

test.jsonl:
3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf

schema.json:
6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb

human-review-sample.jsonl:
d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693

manifest.json:
09660d9e3b1d294fa82fbde702083d0d818431692a55f30387c78adfc697a210
```

Frozen validation passed:

```text
validator: PASS
cases: 1400
counterfactual_groups: 140
heldout_counterfactual_cases: 280
split_template_leakage: 0
split_exact_utterance_leakage: 0
semantic audit: PASS
issues: []
pytest: 2 passed
```

## Model artifact

```text
model: Qwen/Qwen3.8-27B
GGUF repo: ggml-org/Qwen3.8-27B-GGUF
snapshot: 0669b98607d47046c7c2b3f801011d54a08cfccf
quant: Q4_K_M
file: Qwen3.8-27B-Q4_K_M.gguf
bytes: 18,973,870,432
SHA-256: 31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34
vision projector downloaded: NO
```

## Runtime

```text
OS: Microsoft Windows 11 Home Single Language 10.0.26200 Build 26200
CPU: Intel(R) Core(TM) Ultra 7 258V, 8 cores / 8 logical processors
RAM: 33,916,248,064 bytes
GPU: Intel(R) Arc(TM) 140V GPU (16GB)
GPU driver: 32.0.101.8860
Python: 3.12.10
llama.cpp: 0.3.0-dev build 10793 commit d230ddd76
```

Backends tested:

- SYCL full offload: failed during load with `n_gpu_layers`/free-device-memory abort.
- Vulkan full offload: failed with `ErrorOutOfDeviceMemory`.
- CPU-only: stable at 4096, 8192, and 16384 context.
- Vulkan partial offload (`-ngl 10`): loaded with pinned-memory warning and improved prompt evaluation, but multi-slot calibration showed timeout/server instability.

## Context characterization

| Context | Backend | Status | Load | Prompt tok/s | Decode tok/s | Notes |
|---:|---|---|---:|---:|---:|---|
| 4096 | CPU | stable | ~46.95s | 4.3174 | 1.5417 | smoke output `OK` |
| 8192 | CPU | stable | ~26.53s | 4.2773 | 1.5802 | smoke output `OK` |
| 16384 | CPU | stable | ~27.30s | 3.7508 | 1.3946 | characterization only |
| 8192 | Vulkan `-ngl 10` | partial / unstable under multi-slot | ~28.22s | 11.9887 single-case | 1.6792 single-case | 4-worker calibration had timeouts |

## Prompt

```text
version: track-a-reference-json-v1-v3-local-format
SHA-256: 6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d
temperature: 0
seed: 20260904
```

Dry-run leakage check passed: no prompt contained `expected`, `truth`, `gold`, `target answer`, or `counterfactual partner answer`.

## Calibration and determinism

Calibration v1 exposed hidden-thinking/content-empty behavior:

```text
20 cases
8 ok
0 parsed
12 timeout/error
```

Calibration v3 parser smoke:

```text
5 cases
5 ok
5 parsed
```

Vulkan partial 4-worker calibration was not reliable enough for full held-out:

```text
20 cases
13 ok
13 parsed
7 timeout/error
```

Determinism was not completed. A 20-case cross-family/language set was selected, but pass 1 returned connection-refused errors after the Vulkan server exited. This is recorded as runtime reliability evidence, not as model determinism evidence.

## Held-out metrics

Held-out evaluation was **not run**.

No held-out prompt tuning, threshold tuning, truth edit, or manual output repair was performed.

## Verdicts

Reference verdict: **NOT EVALUATED**.

Reason: final development, determinism, and one-shot held-out gates were not completed.

Local practicality: **CONSTRAINED**.

Reason: 4096 and 8192 context were stable locally, with decode rate between 1 and 4 tok/s. This machine can run the model, but not at practical reference-evaluation throughput for the full Track-A held-out protocol in this run.

## Scope confirmation

```text
benchmark truth changed: NO
scorer changed: NO
model/kernel changed: NO
PPF changed: NO
N4 started: NO
distillation started: NO
```

STOP. Do not start N4. Wait for independent ChatGPT review.
