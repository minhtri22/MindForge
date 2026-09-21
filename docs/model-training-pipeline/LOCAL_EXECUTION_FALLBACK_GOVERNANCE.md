# Local Execution Fallback Governance

## Purpose

GitHub Actions remains the preferred independent execution venue. When an
authoritative workflow is terminated by infrastructure before it emits a
scientific result (runner shutdown, hosted-runner cancellation, resource/timeout
termination), the study may switch to **Local Execution Fallback**.

The fallback changes only the execution venue. It must not change the scientific
code, model/config identity, fixtures, thresholds, pinned external revisions, or
adjudication rules.

## Trigger

Local fallback is permitted only when the preceding workflow is classified
**INVALID_INFRASTRUCTURE / INCOMPLETE**, not when it produced a valid scientific
PASS/FAIL.

For the current M5 F16 case:

- invalid GitHub run: `35577280214`
- scientific code SHA: `8dd08cbd7cd1b9050f6ae7eda6f3ab41d6edbc0a`
- failure: hosted runner shutdown before
  `M5_F16_REQUALIFICATION_RESULT.json` existed.

## Operator handoff

The assistant prepares and commits the deterministic local runner. The human
operator:

1. clones or pulls the repository;
2. runs the supplied PowerShell/CMD entry point without editing scientific code;
3. lets the invocation finish once;
4. uploads the generated JSON report to the assistant.

The assistant then independently adjudicates the JSON evidence.

## Mandatory local-run properties

The runner must:

- verify Git blob identities of all scientific production/config files against
  the frozen scientific SHA;
- reject unexpected dirty tracked files;
- record OS/CPU/RAM, Python, Git and CMake identities;
- create isolated pipeline and converter Python environments;
- checkout the exact pinned llama.cpp commit;
- use the pinned upstream converter requirements;
- build llama.cpp from source with the frozen flags/targets;
- run the same foundation tests;
- run the same F16-only requalification harness;
- never invoke quantization;
- emit a JSON report on PASS, scientific FAIL, or ordinary execution failure.

A local scientific FAIL is a valid result if the harness reaches its one-shot
adjudication. It must not be rerun with changed code/settings to seek PASS.

## Evidence file

Default output:

```text
local-reports/m5-f16/M5_F16_LOCAL_REPORT_<timestamp>.json
```

The operator uploads only this JSON unless the assistant requests an additional
specific artifact.

## Current command

PowerShell:

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_m5_f16_local.ps1
```

or one-click CMD:

```text
scripts\run_m5_f16_local.cmd
```

## Governance boundary

Local F16 PASS may authorize a *separate* quantization qualification. The local
fallback runner itself must not execute Q8/Q4 and cannot authorize M6 or bulk
training.
