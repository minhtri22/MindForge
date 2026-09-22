# M6 Venue-Independence Governance Amendment

## Why this amendment exists

The existing lineage is correct about what GitHub/repository recovery actually
observed:

```text
Q4 bytes were not persisted in the inspected GitHub sources
F16 bytes were not persisted in the inspected GitHub sources
```

But the previous downstream wording was too strong. It effectively treated:

```text
not found in GitHub-hosted persistence
```

as:

```text
research cannot continue
```

That interpretation is withdrawn.

GitHub Actions is an evidence/execution venue, not a scientific dependency.

## Venue-independent rule

A qualified local Windows machine is an admissible authoritative venue.

Scientific validity depends on frozen identities, commands, configuration,
artifact hashes, raw evidence and no-rescue rules—not on whether the execution
occurred on GitHub.

Therefore M6 may continue locally without uploading model binaries to GitHub.

## Local decision tree

```text
local exact Q4 exists
    -> verify exact frozen identity
    -> admit Q4
    -> local Ollama M6 qualification

else local exact F16 exists
    -> verify exact frozen identity
    -> exact llama.cpp source/build contract
    -> Q4_K_M reconstruction
    -> verify exact frozen Q4 identity
    -> local Ollama M6 qualification

else neither binary exists
    -> separate PRE-OUTCOME local artifact-regeneration program
    -> exact frozen model revision + converter contract -> F16
    -> exact frozen llama.cpp source + Q4_K_M -> Q4
    -> compare against pre-existing frozen identities
    -> only then local Ollama M6 qualification
```

The third path is artifact reproducibility/materialization. It must not run
scientific fixtures, model-quality evaluation or re-adjudicate F16/Q4.

## Cross-OS runtime identity

Executable byte hashes are venue-specific.

A Linux/GitHub-built `llama-quantize` SHA256 is evidence for that venue and
must not be imposed as a byte-equality requirement on a Windows local build.

The authoritative cross-venue lock is:

```text
llama.cpp source commit
build contract
quantizer target
commands
input artifact identity
output artifact identity
```

The local executable SHA256 must still be recorded as provenance.

For Ollama, the already-pinned official Windows v0.34.2 asset remains a valid
local runtime target.

## What does not change

```text
F16 = PASS / CLOSED
Q4_K_M = PASS / CLOSED
no threshold tuning
no fixture changes
no rerun-to-seek-PASS
M6 PASS requires real Ollama create/chat/parity/owned-cleanup
M7 remains closed
```

## Correct interpretation of prior NOT_FOUND results

Prior `F16_EXISTING_BYTES_NOT_FOUND` and
`PARENT_ARTIFACT_UNAVAILABLE` results remain valid for the exact sources and
venues inspected.

They are not global impossibility claims and are not scientific blockers.

## Next valid action

Open a bounded local-Windows M6 venue/pre-outcome execution package.

It must first inspect/admit local Q4/F16 bytes. If neither exists, it must stop
and preregister deterministic local artifact regeneration before any converter
or quantizer regeneration command is executed.
