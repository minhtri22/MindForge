# M6 Parent-Artifact Materialization / Provenance Program

## Purpose

This program exists for one reason only:

```text
obtain one byte-identical copy of the already-qualified Q4_K_M GGUF
for M6 packaging
```

Frozen identity:

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

Q4 remains `PASS / CLOSED`. This program cannot reopen or re-adjudicate it.

## Source order

The program must use recovery-first ordering.

### 1. Existing bytes

Prefer an already-existing byte copy from an explicit provenance-safe source,
including a user-supplied/local file or another persistent store.

Admission requires exact size and SHA256.

### 2. Deterministic artifact reconstruction

Only if recovery is exhausted may the program reconstruct Q4 bytes from the
exact frozen identities.

That reconstruction is **not** a new Q4 scientific run.

It may execute only the minimum deterministic artifact-production path needed
to reproduce the frozen GGUF. It may not:

- run scientific fixtures;
- invoke llama-cli for Q4 preservation evaluation;
- emit a new Q4 scientific result;
- alter Q4 gates or thresholds;
- change Q4 status.

The sole reconstruction acceptance criterion is equality with the already-frozen
artifact identity.

## Interpretation

A byte match means:

```text
M6_PARENT_ARTIFACT = ADMITTED
```

It does not mean:

```text
new Q4 PASS
new scientific evidence
Q4 rerun
```

A mismatch means materialization/reconstruction failed. It does not retroactively
change the closed Q4 verdict.

## Downstream boundary

Until parent admission PASS:

```text
ollama create = FORBIDDEN
ollama chat = FORBIDDEN
M6 scientific execution = FORBIDDEN
M6 PASS claim = FORBIDDEN
M7 = CLOSED
bulk training = CLOSED
```

Only after an admitted binary is persisted with exact provenance may a separate
M6 create → chat parity → owned cleanup authorization be opened.
