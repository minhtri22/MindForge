# Track-A Qwen3.8 Reference Qualification Final

## Final result

Task `N3.R1-B.Q FRESH 700-CASE HELD-OUT QUALIFICATION` is complete.

```text
HELD-OUT: 700/700 COMPLETE
RVE: FAIL
TUE: FAIL
REFERENCE VERDICT: REJECT_AS_QUALITY_REFERENCE
```

The final one-shot completed all 700 held-out cases in exact frozen order with concurrency 1. It used one llama-server PID, 11556, for the complete run. The client runner PID 29256 exited normally with code 0, the heartbeat reached `COMPLETED`, the finalizer executed, and llama-server remained alive afterward.

## Frozen runtime

```text
llama-server: D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe
version/build: 0.3.0-dev / build 10793 / commit d230ddd76
model: D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf
model bytes: 18973870432
model SHA256: 31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34
backend/device: Vulkan / Intel(R) Arc(TM) 140V GPU
context: 8192
-ngl: 10
parallel: 1
KV K/V: f16 / f16
reasoning: off
temperature: 0
seed: 20260904
prompt version: track-a-reference-json-v1-v3-local-format
prompt SHA256: 6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d
```

Ollama was not used. The model directory name is storage only.

## Integrity

Independent verification of the durable predictions confirmed:

```text
planned/completed: 700/700
telemetry rows: 700
indices: exactly 1..700
unique sequence indices: 700
unique case IDs: 700
held-out order mismatches: 0
missing indices: 0
duplicate indices: 0
transport errors: 0
timeouts: 0
validator failures: 0
wrong PID rows: 0
server-dead-after rows: 0
heartbeat: COMPLETED
finalizer executed: YES
runner exit code: 0
server crashes: 0
server restarts: 0
server PID unchanged: YES, 11556
heldout.stderr.log bytes: 0
```

All 700 parse outcomes were recorded. There was one real model-output parse error at sequence 589, case `A6-H-088`. The raw output was truncated before closing the JSON object. The row remained durable and was passed unchanged to the frozen scoring path; no retry or manual repair occurred. The frozen scorer reported `missing_predictions: 0`.

## Performance

```text
mean latency: 33.269220 s
median latency: 29.362122 s
p95 latency: 60.754227 s
mean prompt throughput: 15.462327 tok/s
mean decode throughput: 1.562395 tok/s
peak runner RSS: 40,980,480 bytes
peak server RSS: 18,986,172,416 bytes
peak server private bytes: 29,686,554,624 bytes
peak system used RAM: 32,985,186,304 bytes
minimum system available RAM: 931,061,760 bytes
peak pagefile used: 18,431,528,960 bytes
GPU/shared-memory peak: unavailable
```

Under the frozen practicality criteria, the measured decode rate is in the `>=1 and <4 tok/s` band.

```text
CPU: CONSTRAINED
Vulkan: CONSTRAINED
overall: CONSTRAINED
```

## Semantic scores

| Family | Frozen primary metric | Score |
|---|---|---:|
| A1 | intent label accuracy | 0.600000 |
| A2 | entity-set F1 | 0.760000 |
| A3 | normalized interpretation accuracy | 0.010000 |
| A4 | action top-1 | 0.700000 |
| A5 | slot micro-F1 | 0.210992 |
| A6 | clarification accuracy | 0.770000 |
| A7 | route accuracy | 0.800000 |
| Macro | family-primary macro | 0.550142 |

Secondary and gate metrics:

| Metric | Score |
|---|---:|
| A2 resolved-value accuracy | 0.513333 |
| A2 clarification accuracy | 0.970000 |
| A5 exact-record match | 0.000000 |
| A6 under-clarification | 0.000000 |
| A6 over-clarification | 0.220000 |
| A7 false-local | 0.000000 |
| A7 unnecessary-external | 0.000000 |
| Unavailable-action false-selection | 1.000000 |
| Counterfactual consistency | 0.357143 |

Language slices, macro family-primary:

| Slice | Cases | Score |
|---|---:|---:|
| VI | 420 | 0.555431 |
| VI-EN | 175 | 0.542853 |
| EN | 105 | 0.541134 |

Difficulty slices, macro family-primary:

| Slice | Cases | Score |
|---|---:|---:|
| Straightforward | 280 | 0.564014 |
| Contextual | 245 | 0.540143 |
| Adversarial | 175 | 0.541946 |

## Frozen gates

RVE failed because macro was 0.550142 below 0.80; A1, A3, and A5 were below the per-family 0.70 floor; and unavailable-action false-selection was 1.00 above 0.05. A6 under-clarification and A7 false-local passed their RVE limits.

TUE failed because macro was below 0.90; every family was below the 0.85 floor; A2 resolved-value was below 0.90; A5 exact-record was below 0.85; unavailable-action false-selection exceeded 0.02; and counterfactual consistency was below 0.90. A6 under-clarification and A7 false-local passed their TUE limits.

No subjective override is applied:

```text
RVE FAIL -> REJECT_AS_QUALITY_REFERENCE
```

## Attempt history

The evidence history remains intact:

- Original held-out: `INVALID / INCOMPLETE 175/700`; not resumed or scored.
- First fresh final attempt: `INVALID / INCOMPLETE 21/700`; user reported external machine power loss; not resumed or scored.
- First power-loss retry: `INVALID / INCOMPLETE 220/700`; runner and server were absent when checked, root cause unproven; not resumed or scored. Its artifacts are preserved under `runs/track-a-qwen38-reference-v1-heldout-retry-powerloss-01/`.
- Final fresh retry: `700/700 COMPLETE`; scored once with the frozen scorer; no response retry, repair, skip, reorder, or partial-output reuse.

Closed prerequisite evidence is unchanged:

```text
Vulkan isolation: STABLE UNDER ISOLATION
V4: PASS WITH EVIDENCE CAVEAT
Harness certification: HARNESS CERTIFIED
```

## Scope confirmation

```text
OLLAMA USED: NO
benchmark truth changed: NO
scorer changed: NO
schema changed: NO
manifest changed: NO
RVE/TUE changed: NO
prompt changed: NO
model/kernel changed: NO
TokenModel changed: NO
PPF changed: NO
N4 started: NO
training started: NO
distillation started: NO
```

## Recommendation

Qwen fails RVE as a Track-A quality reference. Do not start N4 until independent review determines whether the result primarily reflects a reference-model limitation or a Track-A framing/data problem.
