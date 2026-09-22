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
