# Track-A Qwen3.8 Reference Qualification Final

## Scope

Task: `N3.R1-B.Q FRESH 700-CASE HELD-OUT QUALIFICATION`.

The run reused the frozen Qwen3.8 llama-server Vulkan configuration and the certified detached process-lifetime pattern. V0-V4 and harness certification were not rerun. The previous invalid 175/700 held-out run was not resumed. The fresh one-shot marker authorized a new run from case 1 with `resume_allowed=NO`.

No N4, training, distillation, model/kernel, TokenModel, or PPF work was started.

## Preserved prior evidence

- Vulkan isolation: `STABLE UNDER ISOLATION`
- V4: `PASS WITH EVIDENCE CAVEAT`
- Harness: `HARNESS CERTIFIED`
- Previous held-out: `INVALID / INCOMPLETE 175/700`
- Reference verdict before this run: `NOT EVALUATED`

## Pre-held-out freeze

Precheck passed before the one-shot marker was written:

- repository HEAD matched origin at `4437dba66fd3ebbf3749479c180dfe5355d3eafe`;
- only expected llama-server PID 28096 was present;
- Ollama and other inference runtimes were absent;
- server command matched the frozen Vulkan configuration;
- model bytes and SHA256 matched;
- prompt SHA256 matched;
- calibration/development/test/schema/human-review hashes matched the frozen manifest;
- scorer, schema, and manifest hashes matched;
- harness verdict was `HARNESS CERTIFIED` and fresh held-out authorization was `AUTHORIZED`;
- harness regression tests passed 6/6.

Frozen runtime:

```text
llama-server: D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe
version/build: 0.3.0-dev / build 10793 / commit d230ddd76
server PID: 28096
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

## Fresh one-shot result

The fresh run started from case 1. It produced 21 durable prediction rows in exact sequence, ending at `A1-H-020`. All 21 durable rows had HTTP 200 transport success, parse outcomes, validator outcomes, and `server_alive_after=true`.

The heartbeat then recorded:

```text
last_case_completed: 21
last_case_started: 22
status: RUNNING
finalizer_executed: false
```

After the failure was observed, neither runner PID 43236 nor llama-server PID 28096 existed, and no Ollama/llama/lmstudio/kobold inference runtime was present. The server log ends while processing case 22 and contains no clean shutdown or explicit crash message in the preserved tail. Therefore the ordering/root cause of the two process terminations cannot be proven.

Failure classification:

```text
SERVER_AND_CLIENT_TERMINATED_DURING_CASE_22
root cause: UNPROVEN
```

Per the frozen no-recovery rule, the run was not resumed, the server was not restarted, and the partial predictions were not scored.

## Held-out integrity verdict

```text
planned: 700
completed: 21
durable telemetry rows: 21
last completed case: A1-H-020
last started case index: 22
transport errors in completed rows: 0
timeouts in completed rows: 0
runner unexpected termination: YES
server termination: YES
server restart: NO
heartbeat final: RUNNING
finalizer executed: NO
runner exit code: NOT CAPTURED

HELD-OUT:
INVALID / INCOMPLETE
```

## Partial performance characterization

These values are computed only from the 21 durable successful requests and are not qualification scores:

```text
mean latency: 34.120129 s
median latency: 29.625149 s
p95 latency: 59.396967 s
mean prompt tok/s: 13.433258
mean decode tok/s: 1.601137
```

Run-specific RAM/GPU peak telemetry is unavailable. Resource snapshots were retained in memory by the runner and were only persisted in its finalizer; because the runner terminated unexpectedly, no final resource summary existed. No values from a different run are substituted.

## Semantic qualification

The frozen scorer was not invoked because the 700/700 success gate was not met.

```text
RVE: NOT EVALUATED
TUE: NOT EVALUATED
REFERENCE VERDICT: NOT EVALUATED
```

No A1-A7, macro, slice, gate, or counterfactual metric is reported from the partial run.

## Practicality

The previously frozen CPU practicality remains `CONSTRAINED`. The partial held-out decode mean of 1.601 tok/s lies in the frozen Vulkan `CONSTRAINED` band (`>=1 and <4 tok/s`), but the qualification run itself is invalid because the server and client did not survive to 700/700.

```text
CPU: CONSTRAINED
Vulkan: CONSTRAINED, qualification run invalid
overall: CONSTRAINED
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

Reference remains `NOT EVALUATED`. Do not start N4. Independent review is required before deciding whether another qualification attempt is methodologically permissible and, if so, whether server-process durability must be addressed first.
