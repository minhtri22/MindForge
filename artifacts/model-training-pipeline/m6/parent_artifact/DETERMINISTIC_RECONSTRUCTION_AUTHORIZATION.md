# M6 Parent Artifact — Deterministic Reconstruction Authorization

## Decision

```text
RECOVERY:
NOT_FOUND_RECOVERY_EXHAUSTED / CLOSED

DETERMINISTIC RECONSTRUCTION:
AUTHORIZED EXACTLY ONCE

SCIENTIFIC Q4 RERUN:
NOT AUTHORIZED
```

This authorization exists only to reconstruct the already-qualified Q4 artifact
bytes from the exact frozen F16 parent and compare them against the pre-existing
Q4 byte identity.

It does not reopen Q4 science.

## Frozen F16 parent

Reconstruction may start only if an existing materialized F16 artifact passes:

```text
file:
model-f16.gguf

size:
994156384

sha256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b

aggregate manifest:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8
```

This authorization does **not** authorize regenerating F16.

If exact F16 bytes are unavailable, reconstruction must stop with an invalid
provenance classification before the quantizer runs.

## Frozen reconstruction runtime

```text
llama.cpp:
ce8caa6e60a03093351d6016a818720e0d46f0fb

quantizer:
Q4_K_M
```

The only permitted artifact-production command shape is:

```text
<llama-quantize>
<exact-frozen-model-f16.gguf>
<output-model-q4_k_m.gguf>
Q4_K_M
```

No target, parent, source commit, fixture, inference, or gate change is allowed.

## Frozen target identity

The reconstructed artifact is admitted only if it exactly matches:

```text
file:
model-q4_k_m.gguf

size:
397807456

sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977

aggregate manifest:
e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b
```

The comparison is byte/provenance identity only.

## Interpretation

A match means:

```text
ADMITTED_DETERMINISTIC_RECONSTRUCTION
```

It does **not** mean a new Q4 scientific PASS.

A mismatch means:

```text
RECONSTRUCTION_IDENTITY_MISMATCH
```

It does **not** change Q4 from its frozen terminal state:

```text
Q4_K_M = PASS / CLOSED
```

## Forbidden

The reconstruction orchestration may not:

- run Q4 fixtures;
- invoke `llama-cli` for model evaluation;
- perform model inference;
- emit a new M5Q Q4 scientific result;
- scientifically adjudicate Q4;
- modify Q4 thresholds or gates;
- regenerate F16;
- run Ollama create/chat;
- open M7;
- start bulk training.

## One-attempt rule

Exactly one deterministic reconstruction attempt is authorized after exact F16
parent admission.

The emitted byte-identity result must be frozen as-is. There is no
rerun-until-match policy.

## Next action

Create a deterministic reconstruction orchestration bound to this authorization.
It must first admit the exact F16 parent. Only then may it execute exactly one
`Q4_K_M` quantizer invocation and compare the produced bytes against the frozen
Q4 identity.
