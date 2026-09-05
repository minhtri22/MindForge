# Track-A Qwen3.8 Pre-Held-Out Harness Certification

## Purpose

N3.R1-B.H certifies client-process durability and observability before another Track-A held-out one-shot. It is infrastructure qualification only. No held-out/test truth was opened by the certification runner, no semantic score was produced, and N4 was not started.

## Previous failure review

The previous held-out one-shot stopped after `A2-H-074`, case 175/700, while llama-server PID 28096 remained alive. The 175 completed rows had no transport error. The frozen classification remains `CLIENT_RUNNER_TERMINATED_SERVER_ALIVE`; root cause remains `UNPROVEN`.

The old held-out runner already opened predictions with exclusive-create semantics and flushed plus `os.fsync()` after every completed row. Therefore loss of a large in-memory telemetry buffer is not supported by the evidence. The old runner caught `BaseException` around the request loop and stopped its resource monitor in `finally`, but it did not maintain a separate durable process heartbeat, explicit external-termination evidence, or finalizer/exit-reason evidence that could distinguish a Python failure from an external shell/session termination after the process disappeared.

Attempt 01 of this certification reproduced the same broad failure class under a foreground Codex tool session: 24 durable rows were preserved, heartbeat showed case 25 started, runner PID 12364 disappeared, `finalizer_executed=false`, and llama-server PID 28096 remained alive. The Codex session handle also disappeared. This makes shell/session lifetime a live hypothesis, but it does not prove the historical root cause.

Attempt 02 was launched as a separate PowerShell `Start-Process` child with stdout/stderr redirected to durable artifacts. It then completed the entire workload without intervention. This establishes a launch mode that survives the tool-session lifetime observed in attempt 01; it does not retroactively prove why the previous held-out runner died.

## Harness changes

`scripts/certify_qwen38_preheldout_harness.py` adds a dedicated certification runner that reuses the frozen `SYSTEM`, `prompt_for`, and `parse_prediction` behavior from the Track-A reference runner. It reads only `development.jsonl` for certification requests. Model-facing prompt semantics, benchmark truth, scorer, RVE/TUE, model/kernel, TokenModel, and PPF are unchanged.

Reliability and observability additions are:

- exact 2 × 420 development workload construction with fixed order and concurrency 1;
- per-case append-only JSONL telemetry with `flush` plus `fsync` after each completed request;
- atomic heartbeat/status writes before and after each case;
- sequence, missing-index, duplicate-index, repeat-index, and server-PID checks;
- explicit HTTP/transport classification without retry-to-rescue;
- top-level exception, SIGINT/SIGTERM, interruption, finalizer, and exit-code evidence;
- server process-lifetime and inference-isolation checks throughout the run;
- resource snapshots at start, 25%, 50%, 75%, 100%, and final;
- frozen model, prompt, development, calibration, schema, manifest, and scorer hash checks.

`tests/test_qwen38_preheldout_harness.py` adds regression coverage for the prior leakage false-positive class and for certification workload/index behavior. Ordinary values containing `gold`, `golden`, or `goldfish` do not trigger the leakage guard, while a structured `"gold": ...` key still does.

## Frozen runtime

- llama-server: `D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe`
- version/build: `0.3.0-dev`, build `10793`, commit `d230ddd76`
- server PID: `28096`
- model: `D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf`
- model bytes: `18973870432`
- model SHA256: `31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34`
- backend/device: Vulkan / Intel Arc 140V
- context: `8192`
- `-ngl`: `10`
- parallel: `1`
- KV K/V: `f16` / `f16`
- temperature: `0`
- seed: `20260904`
- reasoning: off
- prompt version: `track-a-reference-json-v1-v3-local-format`
- prompt SHA256: `6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d`

Exact server command:

```text
D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe -m D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf -c 8192 -ngl 10 --parallel 1 --cache-type-k f16 --cache-type-v f16 --reasoning off --reasoning-budget 0 --no-reasoning-preserve --host 127.0.0.1 --port 8080 --verbose
```

Isolation precheck found exactly one inference runtime: llama-server PID 28096. Ollama was not used.

## Pre-run gates

Python compile passed. Harness unit tests passed 6/6. Frozen hashes matched for the development and calibration materializations, schema, manifest, prompt template, scorer, and model. The held-out/test file was deliberately not opened for certification.

The 10-case smoke passed 10/10 with 10 durable telemetry rows, zero missing or duplicate indices, heartbeat `COMPLETED`, finalizer executed, exit code 0, zero transport errors/timeouts, and the same server PID alive afterward.

## Certification attempts

### Attempt 01 — FAIL

- planned: 840
- completed/durable rows: 24
- last completed: 24
- last started: 25
- completed-row transport errors: 0
- runner PID: 12364, later absent
- server PID: 28096, still alive
- heartbeat: remained `RUNNING`
- finalizer executed: no
- result: `CLIENT_RUNNER_TERMINATED_SERVER_ALIVE`
- root cause: `UNPROVEN`

Attempt 01 evidence is preserved and was not resumed.

### Attempt 02 — PASS

- planned/completed: 840/840
- durable client telemetry rows: 840
- workload: development cases 1–420, then the same 1–420 again
- source-order mismatches: 0
- repeat-index mismatches: 0
- missing indices: 0
- duplicate indices: 0
- transport errors: 0
- connection refused: 0
- unrecovered timeouts: 0
- parse outcomes: 840
- parse successes: 840
- validator outcomes: 840
- validator failures: 0
- runner unexpected termination: no
- unhandled exception: none
- heartbeat final state: `COMPLETED`
- finalizer executed: yes
- runner exit code: 0
- server PID unchanged: yes, PID 28096
- server alive after request 840: yes
- stderr bytes: 0

Latency over successful requests was 16.535 s minimum, 24.115 s median, 26.193 s mean, and 70.335 s maximum.

Resource snapshots were captured at the required milestones. Peak observed runner RSS was 38,416,384 bytes; peak server RSS was 20,084,330,496 bytes; peak server private bytes was 29,665,357,824 bytes; minimum observed system-available memory was 1,686,429,696 bytes. These values are characterization only and no runtime setting was changed in response.

## Verdict

```text
HARNESS CERTIFIED
```

```text
FRESH HELD-OUT ONE-SHOT:
AUTHORIZED
```

Authorization means one future fresh 700-case held-out run may start from case 1 under the already frozen llama-server Vulkan configuration and with the certified detached process-lifetime pattern. The previous 175-case run must not be resumed. No held-out run is performed by this task.

## Previous evidence preserved

Canonical V4 wording remains:

```text
V4 runtime stability:
PASS WITH EVIDENCE CAVEAT

420/420 responses completed/confirmed

163/420 direct client telemetry
257/420 server-log corroborated/reconstructed

server crashes:
0

same PID throughout:
YES
```

The previous held-out remains `INVALID / INCOMPLETE — 175/700`, and the reference verdict remains `NOT EVALUATED`.

## Scope confirmation

- OLLAMA USED: NO
- held-out truth accessed for certification: NO
- held-out run started: NO
- benchmark truth changed: NO
- scorer changed: NO
- RVE/TUE changed: NO
- prompt semantics changed: NO
- model/kernel changed: NO
- TokenModel changed: NO
- PPF changed: NO
- N4 started: NO
- distillation started: NO
