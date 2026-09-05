# Track-A Qwen3.8-27B Vulkan Isolation Retry

Date: 2026-09-05

Branch: `research/track-a-benchmark-v1`

Starting HEAD: `df8914f1593556bcf6e490a9869ea081e9400741`

## Result

Vulkan partial offload verdict: **STABLE UNDER ISOLATION**.

Held-out: **INVALID / INCOMPLETE — 175/700**.

Reference verdict: **NOT EVALUATED**.

Local practicality: **CONSTRAINED**.

The clean isolation experiment established that the frozen Qwen3.8-27B Q4_K_M artifact can run the Track-A development workload on one `llama-server` process using Vulkan partial offload, one slot, and f16 KV cache. The 700-case held-out run was authorized and started once, but its client runner disappeared after case 175 while the same `llama-server` remained alive. The protocol forbids resume/rerun to rescue an interrupted one-shot held-out evaluation, so no scorer was invoked.

## Runtime isolation

```text
Ollama process count before server start: 0
Ollama service running: NO
other inference runtimes before server start: 0
llama-server path: D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe
llama-server version: 0.3.0-dev build 10793 commit d230ddd76
server PID: 28096
server start: 2026-09-05T13:56:59.8669652+07:00

OLLAMA USED: NO
```

The same PID was still alive when the interrupted held-out run was closed. No second inference runtime was introduced.

## Model

```text
path: D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf
bytes: 18,973,870,432
SHA256: 31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34
artifact match: PASS
```

The `2.Ollama` directory was used only as filesystem storage. The Ollama runtime, API, service, and model registry were not used.

## Frozen server configuration

```text
backend: Vulkan
device: Vulkan0 : Intel(R) Arc(TM) 140V GPU (16GB)
context: 8192
gpu layers: 10 (10/65 layers offloaded)
parallel: 1
KV cache K: f16
KV cache V: f16
Flash Attention: llama.cpp default/auto; not explicitly enabled
temperature: 0
seed: 20260904
prompt SHA256: 6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d
```

Exact command:

```text
D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe -m D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf -c 8192 -ngl 10 --parallel 1 --cache-type-k f16 --cache-type-v f16 --reasoning off --reasoning-budget 0 --no-reasoning-preserve --host 127.0.0.1 --port 8080 --verbose
```

The optional higher-`-ngl` characterization was not run. The safest frozen configuration remained `-ngl 10`.

## V0 — single request

```text
PASS
latency: 52.3400 s
prompt: 0.3216 tok/s
decode: 1.5317 tok/s
server alive afterward: YES
PID unchanged: YES
```

## V1 — 10 sequential requests

```text
PASS
transport success: 10/10
transport errors: 0
timeouts/crashes observed: 0
mean latency: 2.8890 s
mean decode: 1.3301 tok/s
PID unchanged: YES
```

## V2 — 20 Track-A calibration cases

```text
PASS
transport success: 20/20
parsed: 20/20
transport errors: 0
timeouts/crashes observed: 0
mean latency: 26.0637 s
mean decode: 1.4458 tok/s
PID unchanged: YES
```

## V3 — determinism 20 x 2

```text
PASS
pass 1 transport success: 20/20
pass 2 transport success: 20/20
pass 1 parsed: 20/20
pass 2 parsed: 20/20
raw exact match: 20/20 = 100%
parsed exact match: 20/20 = 100%
PID unchanged: YES
```

## V4 — 420 development cases

```text
PASS
total completed: 420/420
parsed: 420/420
server restarts: 0
PID unchanged: YES
server alive after case 420: YES
```

Evidence caveat: the original V4 client was interrupted around case 258 before its first 257 HTTP/client rows were checkpointed. Ordered server logs reconstruct those 257 model responses. The resumed segment persisted direct client evidence for 163/163 cases with 0 transport errors. The full V4 artifact therefore records 420 server-side completions and the user-confirmed 420-case completion, while retaining `transport_errors_full_run: null` rather than inventing missing client telemetry.

Known V4 resume resource peaks:

```text
server private bytes: 29,689,966,592
server RSS bytes: 23,252,754,432
system used physical bytes: 33,910,566,912
swap used bytes: 15,850,749,952
samples: 3,622
GPU memory peak: UNAVAILABLE
```

No authoritative per-device GPU peak was persisted, so no GPU-memory value is inferred from unmapped Windows adapter counters.

## Vulkan verdict

**STABLE UNDER ISOLATION**

V0, V1, V2, V3, and V4 all passed on the same `llama-server` PID 28096 with concurrency exactly 1 and no server restart.

## Held-out one-shot

The held-out run was started exactly once after the isolation gate passed. `heldout-start.json` froze the server lifetime/configuration, model hash, prompt hash, benchmark hashes, binary hash, source hashes, context 8192, `-ngl 10`, parallel 1, f16/f16 KV, temperature 0, and seed 20260904.

Last persisted held-out state:

```text
status: INVALID / INCOMPLETE
completed: 175/700
last case: A2-H-074
transport success: 175/175
transport errors: 0
parsed: 175/175
mean latency: 29.6497 s
mean prompt: 15.7799 tok/s
mean decode: 1.9388 tok/s
server PID: 28096
server alive after case 175: YES
```

After case 175, the one-shot client runner process was no longer present. The same `llama-server` PID remained alive. The available evidence does not prove the root cause of the client-runner termination, so it is recorded as `CLIENT_RUNNER_TERMINATED_SERVER_ALIVE / root cause UNPROVEN`, not as a server crash.

The run was not resumed from case 176 and was not rerun. `heldout-score.json` records `NOT SCORED` and `scorer_invoked: false`, because the frozen scorer may run only after 700/700 completion.

## Reference verdict

**NOT EVALUATED**

No A1-A7, macro, language, difficulty, adversarial, counterfactual, RVE, or TUE score is reported because the held-out run did not complete.

## Practicality

```text
CPU: CONSTRAINED
Vulkan: CONSTRAINED
overall: CONSTRAINED
```

The isolated Vulkan runtime is stable at context 8192, but observed decode rates remain in the frozen `>=1 and <4 tok/s` constrained range. The partial held-out mean decode rate was 1.9388 tok/s.

## Scope confirmation

```text
OLLAMA USED: NO
benchmark truth changed: NO
scorer changed: NO
model/kernel changed: NO
PPF changed: NO
N4 started: NO
distillation started: NO
```

STOP. Do not start N4.
