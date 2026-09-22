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


## 2026-09-22 — M6 zero-runtime implementation tests PASS; exact implementation locked

Authoritative zero-runtime test run:

```text
run: 35672110940
job: 106570655074
conclusion: success
tests: 13/13 PASS
```

The run proved:

```text
ollama_executable_invoked=false
ollama_runtime_execution_executed=false
m6_scientific_execution_executed=false
m7_authorized=false
```

M6 now has a deterministic zero-runtime implementation for:

```text
exact Ollama release lock
frozen Q4 source identity verification
deterministic Modelfile generation
ephemeral namespace construction
ownership-gated cleanup planning
reasoning/think request mapping
frozen llama.cpp-parent parity comparison
hard downstream boundaries
```

The Ollama release lock is pinned to official release `v0.34.2` and retains
authoritative asset digests for Windows amd64 and Linux amd64. No Ollama binary
was downloaded, installed, probed or executed.

The implementation and its transitive governance/runtime-contract dependencies
are frozen in `IMPLEMENTATION_LOCK.json`.

Current boundary:

```text
M6 implementation: LOCKED
zero-runtime tests: PASS
Ollama runtime execution: NOT AUTHORIZED
M6 scientific execution: NOT AUTHORIZED
M7: CLOSED
bulk training: CLOSED
```

Next valid gate: lock-present zero-science / zero-runtime preflight.
