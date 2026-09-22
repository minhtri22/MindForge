# M6R2 LINEAGE

## 2026-09-22 — Science-only M6R2 specification opened

Parent governance:
750d6358a88e738cfaf971b3a5db3192f7622889

M6R2 is opened after the model-pipeline infrastructure/science separation amendment.

Historical outcomes remain immutable:
- M6 = FAIL_PACKAGE / CLOSED
- M6R = FAIL_RUNTIME / CLOSED
- RFD-C1 = ROOT_CAUSE_IDENTIFIED / CLOSED

The RFD-identified q4_0 KV-cache / flash-attention conflict is no longer modeled
as an M6R2 scientific intervention.

Runtime repair belongs to reusable OWRQ infrastructure qualification.

M6R2 is now a fresh no-treatment parity replication:
exact Q4 + exact Modelfile + exact eval_v1 + exact generation contract
against the frozen llama.cpp parent comparator.

Infrastructure is consumed through one consolidated binding check.

Design/static implementation may proceed while OWRQ remains unresolved.
Only runtime execution waits for OWRQ qualification.

Scientific outcome exposure begins with eval_v1 runtime output, not with
package/create/runtime plumbing.

No implementation or execution is authorized by this specification commit.


## 2026-09-22 — S0 specification QA PASS / S1 static implementation authorized

S0 reviewed commit:
d6d77951c381b3edf994ddf2567981a80f0eca8e

QA:
- unresolved findings = 0
- no-treatment replication preserved
- infrastructure externalization PASS
- one-binding-check rule PASS
- pre-outcome infra failure semantics PASS
- post-outcome anti-rescue semantics PASS

Decision:
S1 static implementation + zero-science QA is authorized.

OWRQ qualification is NOT required to begin S1.

Still forbidden:
- Ollama process/API execution
- local model create/load/delete
- eval_v1 execution
- S2 runtime binding execution
- S3 scientific execution
- M7
- bulk training
