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
