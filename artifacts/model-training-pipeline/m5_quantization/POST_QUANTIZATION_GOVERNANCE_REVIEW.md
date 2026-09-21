# M5Q Post-Quantization Governance Review

## Review verdict

```text
M5 F16: PASS / CLOSED
Q8_0:   PASS / CLOSED
Q4_K_M: PASS / CLOSED

M5Q PROGRAM:
PASS / CLOSED

M5 EXIT:
PASS / CLOSED

BASIS TO OPEN M6:
YES — SPECIFICATION / IMPLEMENTATION GOVERNANCE ONLY

M6 SCIENTIFIC OR RUNTIME EXECUTION:
NOT AUTHORIZED
```

This review adjudicates the complete M5 export/runtime sequence from qualified
F16 through Q8_0 and Q4_K_M. It does not execute Ollama and does not claim M6
PASS.

## Evidence reviewed

The review is bound to the frozen F16, Q8 and formal Q4 evidence already present
on the authoritative M5Q branch.

The terminal scientific result hashes are:

```text
F16:
0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57

Q8_0:
16b3ce2f4522481ab086068c4a0ce625f9c0a2759d9d946a3deffc7bcf44c1c8

Q4_K_M:
da5e1bcb6b542c0dbecbabfb26f79cd1f986d49546181bede2779693426570ef
```

Q8 and Q4 reruns are closed.

## Claims established by M5/M5Q

### High-fidelity GGUF preservation

The exact canonical HF lineage was converted to the frozen F16 GGUF identity and
loaded/inferred by pinned llama.cpp. The frozen task/format behavior was
preserved.

This satisfies the M5-side substance of AC-06.

### Quantized GGUF preservation

Both preregistered quantized targets independently passed all required
target-specific gates:

```text
Q8_0  = PASS / CLOSED
Q4_K_M = PASS / CLOSED
```

Both artifacts were generated from the exact frozen F16 parent, loaded by the
real pinned llama.cpp runtime, produced non-empty format-valid outputs, preserved
the frozen F16 task vector and accuracy, passed reasoning-runtime mapping, and
were smaller than F16.

This satisfies the M5-side substance of AC-07.

### Q4 formal replication

The formal Q4 replication was executed after the accidental outcome exposure
had been disclosed and quarantined.

The formal implementation, gates and thresholds were locked without embedding
the exposed Q4 outcome. The formal run independently reproduced the previously
exposed artifact identity.

That identity match is corroborative reproducibility evidence only. It was not
an acceptance threshold.

### Shard awareness

The M5 implementation includes shard-set manifest handling and unit coverage for
ordered shard manifests. The authoritative F16/Q8/Q4 artifacts themselves are
single-file.

Therefore this review recognizes **shard-aware implementation/unit coverage**,
but does not claim shard-set runtime qualification.

## Claims not established

M5Q does **not** establish:

- useful absolute task capability;
- model-quality improvement;
- a preferred/production quantization target;
- Ollama runtime compatibility;
- Ollama packaging correctness;
- HF ↔ llama.cpp ↔ Ollama full parity;
- release or full AC-01..AC-18 completion.

The absolute-capability limitation remains material:

```text
F16 task vector = [false, false]
Q8 task vector  = [false, false]
Q4 task vector  = [false, false]

accuracy = 0.0 for all three
```

Thus the M5 results are preservation/runtime results, not an absolute-capability
claim.

## M5 exit adjudication

The repository implementation plan states that a next milestone may not begin
until the current milestone exit gate passes.

The M5 evidence set is now terminal:

```text
high-fidelity F16: PASS / CLOSED
Q8_0:              PASS / CLOSED
Q4_K_M:            PASS / CLOSED
target reruns:     NOT AUTHORIZED
```

The export/runtime requirements owned by M5 have therefore reached a closed PASS
state under the frozen fixture/runtime contract.

Verdict:

```text
M5_EXIT = PASS / CLOSED
M5Q = PASS / CLOSED
```

## Separate M6 admission decision

There **is sufficient governance basis to open M6**, but only at the
specification/implementation level.

Reason:

1. M5 is now PASS/CLOSED.
2. The implementation plan defines M6 as the Ollama milestone.
3. AC-08 is explicitly Ollama-owned and remains untested.
4. AC-10 remains partial because its Ollama packaged-target leg is missing.
5. The reviewed tree has no Ollama lock or M6 runtime evidence, so execution
   cannot be inherited from M5.

The permitted next state is:

```text
M6:
MAY OPEN SPECIFICATION / IMPLEMENTATION GOVERNANCE

M6 scientific execution:
NOT AUTHORIZED

M6 runtime execution:
NOT AUTHORIZED

M6 PASS claim:
NOT AUTHORIZED
```

M5Q PASS must never be interpreted as M6 PASS.

## Required M6 work before any runtime execution

A bounded M6 program must first specify and lock:

- exact Ollama version/runtime identity;
- deterministic Modelfile generation from the frozen inference contract;
- safe ephemeral model namespace and ownership markers;
- create/cleanup semantics that cannot delete unrelated user models;
- exact packaged GGUF target policy;
- reasoning/think mapping for the pinned Ollama runtime;
- HF/llama.cpp/Ollama parity contract;
- failure/adjudication classes;
- tests and zero-science preflight.

The current repository tree does not contain an Ollama lock, so this is a
required M6 deliverable rather than something inferred from M5.

## Downstream boundary

This review itself does not create or run M6.

```text
Q8 rerun = NOT AUTHORIZED
Q4 rerun = NOT AUTHORIZED

M6 runtime/scientific execution = NOT AUTHORIZED
bulk training = NOT AUTHORIZED
```

## Next valid action

Open a bounded **M6 specification + implementation authorization** program.

That new program may design and implement the Ollama path, but must remain
zero-science/zero-runtime until it has its own exact lock and preflight PASS.
