# M6 Runtime Execution Authorization + Venue Qualification

## Authorization state

```text
M6 implementation: LOCKED
zero-runtime tests: PASS
zero-runtime preflight: PASS

RUNTIME VENUE:
GitHub Actions / windows-2025 / x64

OLLAMA:
v0.34.2
asset: ollama-windows-amd64.zip
sha256:
8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b

runtime venue qualification: AUTHORIZED
full M6 create/chat qualification: CONDITIONAL
```

No Ollama command was executed before this authorization.

## Critical parent-artifact admission gate

The reviewed repository contains no GGUF binary. The authoritative formal Q4
Actions artifact and the earlier accidental Q4 artifacts contain evidence only,
not the 397,807,456-byte Q4 GGUF.

Therefore the future venue workflow **must not silently quantize Q4 again**.

Before `ollama create`, the workflow must possess an already materialized
byte-identical parent satisfying:

```text
file: model-q4_k_m.gguf
size: 397807456
sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977
```

If those bytes are unavailable, the correct adjudication is:

```text
INVALID_PROVENANCE_PARENT_ARTIFACT_UNAVAILABLE
```

This is not an M6 scientific FAIL.

## Selected venue

```text
provider: GitHub Actions
runner label: windows-2025
architecture: x64
isolated host: 127.0.0.1:11467
isolated models directory: runner temp only
```

The run must record `ImageOS`, `ImageVersion`, `RUNNER_OS` and
`RUNNER_ARCH` as venue evidence.

Persistent user Ollama state must not be reused.

## Exact command budget

After this authorization, and only inside the bounded venue workflow, the
minimum runtime actions are authorized:

1. download the exact official Windows amd64 Ollama archive;
2. verify its pinned SHA256;
3. extract it to isolated runner temp;
4. run `ollama.exe --version`;
5. start an isolated `ollama.exe serve`;
6. inspect isolated model inventory/collision state;
7. **only after exact Q4 parent admission**, run `ollama create` for the owned
   ephemeral name;
8. execute the frozen chat fixtures through the local Ollama API;
9. adjudicate parity/reasoning gates;
10. run `ollama rm` only for the ownership-verified ephemeral model;
11. terminate the isolated server.

Forbidden:

```text
ollama pull
installer/update
persistent user model directory reuse
unowned model mutation
Q4 requantization
Q4 scientific rerun
fixture/inference/gate tuning
M7
bulk training
```

## Scientific boundary

M5Q PASS is not inherited as M6 PASS. An eventual M6 PASS requires every frozen
runtime gate.

The frozen comparator remains task/format preservation, not exact text, and does
not establish absolute task capability.

## Next action

Create the bounded Windows venue orchestration bound to this authorization.

It may execute venue/asset/version/isolated-server admission immediately.
It must stop before `ollama create` unless exact pre-existing Q4 bytes pass the
parent-artifact admission gate.
