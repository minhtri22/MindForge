# M6R Runtime Failure Decomposition — LINEAGE

## 2026-09-22 — RFD program opened post-closure

Parent:
63cfcd12fae036dd94cf8ce64854796142751b49

Inherited immutable outcomes:
- M6 = FAIL_PACKAGE / CLOSED
- M6R = FAIL_RUNTIME / CLOSED
- M6R attempts authorized=1, consumed=1, remaining=0

Observed M6R boundary:
- installed Ollama 0.34.2 healthy
- exact Q4 identity PASS
- frozen Modelfile PASS
- owned model create return code 0
- first /api/chat request returned HTTP 500
- owned cleanup PASS
- initial/final user model-name sets equal

RFD-C1 is evidence recovery only. It may read/hash/copy existing Windows Ollama logs
for the frozen M6R time window and a preregistered +/-120 second context.

It may not start, stop, restart, reconfigure or invoke Ollama; may not recreate
the M6R model; may not make inference/API requests; and may not open M6R2.

Mechanism classification is explicitly deferred until collected evidence is returned
and integrity/time-window QA is complete.


## 2026-09-22 — RFD-C1 collector locked / existing-evidence collection authorized

Authoritative implementation:
93dc9c10e8831165252576d4e760305a38a982b4

Exact blobs:
- preregistration: 739b01da076d8b17250c9c247aad748018b17b35
- methodology: 92249998ec5972aaa58aa0586972c6a4f7c89ef8
- collector script: 8e695819c4380b4eb93a0a42ce8399dd193ac6f5
- tests: bcb957bba605e1a7a1d7b06213cb50c9a7ee16b2
- workflow: dca995836ea246ebbf4704496c23ff131b15641c

Static zero-action QA:
- run 35739829174
- job 106786382958
- 12/12 contract tests PASS
- PowerShell parse PASS
- Ollama process invocation=false
- Ollama API request=false
- service state change=false
- model store mutation=false
- inference request=false

Collector semantics:
- source logs are read/hash/copy only
- raw forensic copies are preserved locally
- exact M6R window is frozen
- +/-120 second context is frozen
- RFC3339 and local timestamp forms are parsed explicitly
- unparseable timestamps are not guessed
- normal append activity in an active server.log is recorded rather than
  misclassified as collector mutation

RFD-C1 collection is not a scientific attempt and may be repeated only to
recover the same pre-existing evidence after an operational file-read/rotation
problem. It cannot create new M6R evidence or a new model outcome.

Mechanism assignment remains unauthorized until the returned collection report
passes integrity and time-window QA.

M6R2, M7 and bulk training remain closed.


## 2026-09-22 — RFD-C1 root cause identified / mechanism adjudicated

Returned RFD-C1 report:
- SHA256: cf6e6f4feab464cd0b920560405a674ee01eb19f07aff7ae4fed8bff7a20a8d1
- bytes: 40750
- collection integrity: PASS
- evidence adequacy: TIMESTAMPED_CONTEXT_EVIDENCE_PRESENT
- exact-window lines: 22
- authoritative server.log SHA256:
  ff84c9d93f846b49af1fe5eae0729f23581db8ffb885050fd817b5b20425dd3d

Direct failure chain:
1. /api/create returned 200.
2. Ollama launched llama-server with:
   --cache-type-k q4_0
   --cache-type-v q4_0
   --flash-attn off
3. llama-server exited status 1 during model initialization.
4. Ollama logged:
   llama_init_from_model: quantized V cache requires flash_attn to be enabled
5. /api/chat returned HTTP 500.

Authoritative preregistered mechanism class:
INTEL_GPU_OR_RUNTIME_BACKEND

Subtype:
RUNTIME_BACKEND_CONFIGURATION_CONFLICT

This class is selected through its runtime-backend branch. The evidence does not
support a claim that Intel GPU hardware itself caused the failure.

Exact Ollama v0.34.2 source commit:
dfabde4539e42ba1e1eab50a3a50b88aea7958a0

Source confirms:
- OLLAMA_KV_CACHE_TYPE is read into kvCacheType
- non-empty kvCacheType is emitted as both K and V cache type
- flash-attention is resolved independently

Therefore M6R remains FAIL_RUNTIME/CLOSED, but its HTTP 500 root cause is now
identified by direct positive evidence.

Packaging path is not invalidated; model package creation succeeded.

Fresh M6R2 is scientifically justified for preregistration only, with one
mechanism-specific intervention:
q4_0 KV cache -> f16 KV cache.

No flash-attention change is authorized. No Ollama version change, Q4 change,
Modelfile change, fixture/parameter change, parity-target change, or reasoning
change is authorized.

M6R2 implementation/execution remains unauthorized until a fresh specification,
adversarial QA, zero-science implementation lock, and explicit one-attempt gate.

M7 and bulk training remain closed.
