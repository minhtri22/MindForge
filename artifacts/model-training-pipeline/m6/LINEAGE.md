# M6 Ollama Qualification — Lineage

## ORIGIN

M6 opens only after the M5/M5Q post-quantization governance review adjudicated:

```text
M5 = PASS / CLOSED
M5Q = PASS / CLOSED
basis to open M6 = YES
```

Origin commit:

```text
7bcacfa8fb291a9a55e2acf19077c8e61f33c329
```

M6 does not reopen F16, Q8_0 or Q4_K_M and does not inherit their PASS as an
Ollama PASS.

## 2026-09-22 — Bounded M6 specification + implementation authorization opened

A new M6 branch is opened:

```text
research/model-pipeline-m6-ollama
```

Authorized scope:

```text
specification
implementation
zero-runtime unit/contract tests
exact implementation lock after tests PASS
lock-present zero-science/zero-runtime preflight
```

Forbidden during this stage:

```text
all Ollama executable invocation
ollama create
ollama run/chat
ollama pull/rm/serve
Ollama installation/update
M6 scientific qualification
M6 PASS claim
M7 opening
bulk training
```

The canonical smoke packaging parent is the exact formal Q4_K_M artifact from
M5Q, selected because the frozen canonical config already declares q4_k_m.
This does not establish a production-target preference.

M6 must create and freeze an exact Ollama lock, deterministic Modelfile contract,
ephemeral ownership/cleanup semantics, reasoning mapping, parity comparator and
adjudication contract before any runtime execution.

Next valid action:

```text
implement M6 specification/code + zero-runtime tests
```
