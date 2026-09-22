# M6R2 S2 — Consolidated Infrastructure Binding

**Status:** SPECIFICATION ONLY / NOT AUTHORIZED

S2 is deliberately small. It does not qualify Ollama and it does not run M6R2 science.

## Dependency

```
OWRQ
  QUALIFIED_RUNTIME_SCOPE
          ↓
M6R2 S2
  one consolidated binding check
          ↓
BINDING_PASS
          ↓
separate S3 execution authorization
```

If OWRQ has not produced a qualified scope, S2 is simply `BLOCKED_INFRA_BINDING`.
This does not change M6R2's scientific state and consumes no attempt.

## Exact binding

S2 verifies the OWRQ artifact against the locked S1 consumer interface:

- exact qualification artifact SHA256;
- exact runtime-adapter Git blob;
- adapter contract `mindforge-owrq-runtime-adapter-v1`;
- exact local machine fingerprint;
- Ollama `0.34.2`;
- exact `ollama.exe` SHA256;
- `OLLAMA_KV_CACHE_TYPE=f16`;
- flash attention was not forced;
- recorded resolved flash-attention mode;
- qualified API host and `/api/chat` contract.

No individual item becomes a separate user-facing gate. The whole tuple yields one result:
`BINDING_PASS` or `BLOCKED_INFRA_BINDING`.

## Zero-science semantics

S2:
- does not invoke Ollama;
- does not call an API;
- does not create or load a model;
- does not read/execute eval_v1;
- does not expose a model output;
- does not consume the one M6R2 scientific attempt.

## Governance

A BINDING_PASS does **not** automatically authorize S3.
S3 remains a separate one-attempt execution authorization bound to:
1. the immutable S1 lock;
2. the exact S2 authorization/binding artifact;
3. the exact OWRQ qualification identity.

Current state: OWRQ qualification is not yet available, so S2 execution remains unauthorized.
