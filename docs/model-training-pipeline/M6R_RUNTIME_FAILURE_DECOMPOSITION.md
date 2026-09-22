# M6R Post-Closure Runtime Failure Decomposition

## Status

Program: **M6R_RUNTIME_FAILURE_DECOMPOSITION**

This program starts after M6R was formally closed as `FAIL_RUNTIME`. It does not reopen M6R and it is not a rescue rerun.

## Origin

The exact M6R package was created successfully under installed Ollama 0.34.2. The first frozen inference request, task `arith-1`, then failed at `POST /api/chat` with HTTP 500. Cleanup succeeded and the user model-name set was restored exactly.

The current evidence does **not** contain the HTTP 500 response body or authoritative server diagnostics for the failing request. Therefore root cause is unresolved.

## RFD-C1 — Existing-evidence collection only

RFD-C1 may only recover evidence that already existed because of the failed M6R run.

Primary Windows sources are the Ollama server logs documented for v0.34.2:

- `%LOCALAPPDATA%\Ollama\server.log`
- rotated `%LOCALAPPDATA%\Ollama\server-#.log`

`%LOCALAPPDATA%\Ollama\app.log` is treated as a supplemental source if it exists.

No inference, model recreation, API call, service restart or debug-mode enablement is permitted.

## Frozen time window

Exact M6R report window:

- UTC start: `2026-09-22T14:09:47.4135943Z`
- UTC end: `2026-09-22T14:09:56.6906965Z`

Expected local equivalent for the user's +07:00 venue:

- `2026-09-22T21:09:47.4135943+07:00`
- `2026-09-22T21:09:56.6906965+07:00`

For mechanism diagnosis only, the collector also extracts a **frozen ±120 second context** around the run window so model-load, backend-selection and allocation messages immediately preceding the 500 are not lost.

The raw source files are copied and hashed unchanged. The excerpt is derivative evidence only.

## Timestamp handling

The collector attempts to parse:

1. RFC3339 timestamps with `Z` or explicit offset;
2. `time=<RFC3339>`;
3. GIN-style `yyyy/MM/dd - HH:mm:ss`;
4. plain `yyyy-MM-dd HH:mm:ss`.

Timestamp strings with no offset are interpreted using the Windows local timezone recorded in the collection report. Unparseable lines are **not assigned a time**. Raw files remain available for later audit.

## Mechanism decomposition

After C1 evidence is returned, the only admissible mechanism classes are:

- `MODEL_LOAD_OR_GGUF_COMPATIBILITY`
- `MEMORY_OR_BACKEND_ALLOCATION`
- `INTEL_GPU_OR_RUNTIME_BACKEND`
- `CONTEXT_TEMPLATE_OR_TOKENIZER`
- `OLLAMA_SERVER_OTHER`
- `UNRESOLVED`

A mechanism requires positive supporting log evidence. Keyword absence is not evidence of absence.

## Decision gate after collection

Only after C1 evidence QA:

```
existing logs recovered
        ↓
integrity + time-window QA
        ↓
mechanism evidence table
        ↓
root cause identified?
   ├─ yes → decide whether a fresh M6R2 preregistration is scientifically justified
   └─ no  → close C1 as insufficient evidence; decide whether a separate diagnostic experiment is justified
```

No M6R2, M7 or bulk training is authorized by this program.
