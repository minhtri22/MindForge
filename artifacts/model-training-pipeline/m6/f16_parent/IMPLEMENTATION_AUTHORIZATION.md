# M6 F16 Parent Artifact Recovery / Materialization Program

## Purpose

This sub-program has exactly one objective:

```text
obtain one exact existing serialized copy of model-f16.gguf
```

for use as the parent of the already-authorized deterministic Q4 byte
reconstruction.

It does **not** regenerate F16.

## Frozen F16 identity

```text
file:
model-f16.gguf

size:
994156384

SHA256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b

aggregate manifest:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8

scientific status:
PASS / CLOSED
```

## Recovery/materialization versus regeneration

Permitted future materialization means byte-preserving acquisition of an
already-existing serialized F16 object:

- copy an existing local/user-supplied F16 file;
- download an existing immutable binary object;
- extract an archive that already contains the serialized F16;
- reassemble a provenance-bound chunk set without transforming bytes.

Not permitted:

```text
HF/model weights → converter → new F16 GGUF
```

No converter execution is opened by this program.

## Admission

A candidate can be admitted only when all are exact:

```text
filename
size
SHA256
aggregate manifest
persisted-copy reverification
```

A match means only:

```text
ADMITTED_EXISTING_F16_BYTES
```

It does not create a new F16 scientific PASS.

A miss or mismatch does not change:

```text
F16 = PASS / CLOSED
```

## Reconstruction authorization remains untouched

The Q4 deterministic reconstruction authorization:

```text
9506e5fc205e641aba942a0bc9ff2fbaa7d881a5
```

remains valid and unconsumed.

This F16 sub-program cannot execute it.

Only after exact F16 admission PASS may a **new reconstruction orchestration**
be created against that same still-unconsumed authorization.

## Current authorization

Authorized now:

```text
specification
implementation
zero-science tests
planning-only workflow
```

Not authorized now:

```text
real external/user-source recovery execution
F16 regeneration
converter execution
llama-cli evaluation
fixtures/inference
F16 re-adjudication
Q4 reconstruction
ollama create/chat
M6 scientific execution
M7
bulk training
```
