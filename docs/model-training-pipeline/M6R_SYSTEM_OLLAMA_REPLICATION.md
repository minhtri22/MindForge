# M6R System Ollama Replication

## Status

Fresh replication program. M6 remains formally closed as `FAIL_PACKAGE`; M6R is not a rescue rerun and must never overwrite or reinterpret the M6 result.

## Why this venue changes

M6 used an isolated extracted Ollama runtime and invoked native CLI processes directly through a Windows PowerShell 5.1 pipeline. The single scientific attempt was consumed at `ollama create`, where native stderr was promoted into a terminating PowerShell exception before the wrapper could record the process return code.

M6R removes that confound in two independent ways:

1. use the user's installed Windows Ollama runtime and its normal localhost service at `127.0.0.1:11434`;
2. invoke every native Ollama CLI operation through `Start-Process` with owned stdout/stderr files and explicit exit-code adjudication.

The scientific model, Q4 bytes, fixture set, inference parameters, parity target and reasoning mapping remain frozen.

## Runtime upgrade policy

The target runtime is exact stable Ollama `0.34.2`.

- Installed `0.34.2`: no upgrade.
- Installed version older than `0.34.2`: exact official `OllamaSetup.exe` for v0.34.2 may be downloaded, SHA256 verified, Authenticode signer verified as Ollama Inc., and run silently with `/VERYSILENT /NORESTART /SUPPRESSMSGBOXES`.
- Installed version newer than `0.34.2`: stop before attempt; downgrade is not authorized.
- Missing Ollama: stop before attempt; fresh installation is intentionally not part of M6R.

Upgrade and service recovery are pre-attempt infrastructure operations. They cannot consume the scientific attempt.

## User state safety

M6R intentionally uses the existing system Ollama model store. Before creating the owned test model it snapshots `GET /api/tags`. The test namespace must be collision-free. Cleanup may remove only the model created by this run. The final model-name set must equal the initial model-name set exactly.

No `ollama pull`, no deletion of unowned models, no Q4 reconstruction or requantization, and no fixture/threshold/seed changes are allowed.

## Scientific attempt boundary

Exactly one M6R scientific attempt may be authorized after static QA.

The durable consumed marker is written atomically immediately before the installed `ollama create` process starts. Any failure after that point is terminal according to the frozen class map and cannot be rerun to seek PASS.

## Downstream

M6R PASS, if achieved, is a fresh replication result only. It does not change M6. M7 remains closed until a separate explicit governance decision after formal M6R adjudication.
