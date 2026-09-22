# M6 F16 Parent — One-Attempt Existing-Byte Materialization Authorization

## Decision

```text
implementation:
24768d87f9f22b820ac02e7428d40ea3df015bf7

implementation lock / zero-science closure:
8055fdb382a0f6006ecd78ae0f4321e8e1516b8d

zero-science:
14/14 PASS

execution authorization:
AUTHORIZED_ONE_F16_EXISTING_BYTE_MATERIALIZATION
```

This commit authorizes exactly one existing-byte F16 recovery/materialization attempt.
It does not execute that attempt.

## Frozen F16 identity

```text
file: model-f16.gguf
size: 994156384
sha256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b
aggregate manifest:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8
scientific status: PASS / CLOSED
```

Admission requires exact filename, size, SHA256 and aggregate manifest, followed by exact reverification of the persisted copy.

## Authorized modes

```text
COPY_EXISTING_FILE
DOWNLOAD_EXISTING_OBJECT
EXTRACT_EXISTING_ARCHIVE_MEMBER
REASSEMBLE_EXISTING_CHUNKS
```

Every source must be explicit, provenance-bound and already represent serialized F16 bytes before the materialization operation.

## Regeneration remains forbidden

```text
F16 regeneration = FORBIDDEN
HF-to-GGUF conversion = FORBIDDEN
llama-cli evaluation = FORBIDDEN
F16 fixture/model inference = FORBIDDEN
F16 scientific re-adjudication = FORBIDDEN
```

## One-attempt semantics

Planning or inventory alone does not consume the attempt. The attempt becomes consumed when the first real authorized copy/download/extract/reassemble operation begins. No rerun-until-match policy is allowed.

## Terminal outcomes

```text
ADMITTED_EXISTING_F16_BYTES
F16_EXISTING_BYTES_NOT_FOUND
F16_EXISTING_BYTES_IDENTITY_MISMATCH
INVALID_PROVENANCE
INVALID_INFRASTRUCTURE
```

None changes F16 from PASS / CLOSED.

## Q4 reconstruction remains separate

The deterministic Q4 reconstruction authorization remains:

```text
9506e5fc205e641aba942a0bc9ff2fbaa7d881a5
consumed = false
```

The F16 materialization workflow cannot consume it. Even after F16 admission, the workflow must stop and freeze F16 evidence before a new Q4 reconstruction orchestration may be created.

## Next action

Create a one-attempt F16 existing-byte materialization orchestration bound to this authorization. Execute only byte-preserving recovery/materialization and freeze the terminal result before any Q4 reconstruction orchestration is considered.
