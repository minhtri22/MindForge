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


## 2026-09-22 — S1 static implementation / zero-science QA PASS

Canonical implementation commit:
069ad295d9b3a7a52bf203212daa63c628b6d5ef

Canonical implementation blobs:
- runner: b591b55d3e19554507c2c559387c9b947862fd18
- pure contract: e7312efa54876fe59348d7408352bcc36dcaf5e7
- OWRQ adapter consumer interface: 0973749fc01dfe873ec7be92e55d2898fc67b9ed
- tests: 598377f386ae261c0baef6d7e05d873973205dc9
- workflow: 3645d04a504e3683a48cede8850bbc0a2f8c4546

Adversarial implementation review found seven implementation-only issues.
All seven were repaired without changing S0 science.

Most important correction:
M6R2 no longer implements Ollama serve/create/API logic.
It consumes the exact independently-qualified OWRQ adapter blob.

Zero-science QA:
- authoritative run 35745858995 / job 106807189138: PASS
- confirming run 35745524564 / job 106806033750: PASS
- 23/23 tests
- Python compile PASS
- PowerShell parse PASS
- no Ollama process/API/model/eval/outcome execution

S1 is now CLOSED/LOCKED.

S2 remains unauthorized and waits only for a formally qualified OWRQ scope.
S3 remains unauthorized.
M7 and bulk training remain closed.


## 2026-09-22 — S1 supplemental zero-science confirmation / S2 specification opened

Canonical S1 lock remains unchanged:
- implementation commit: 069ad295d9b3a7a52bf203212daa63c628b6d5ef
- lock blob: 124b21063675e6d37202a81b88c04efc4aa2254e
- runner blob: b591b55d3e19554507c2c559387c9b947862fd18
- contract blob: e7312efa54876fe59348d7408352bcc36dcaf5e7
- adapter interface blob: 0973749fc01dfe873ec7be92e55d2898fc67b9ed

Supplemental confirmation:
- HEAD 9f7f9cc0a9fb2f7cec12ec20e7eee858c4706c96
- run 35751922131 / job 106827978783
- 23/23 tests PASS
- Python compile PASS
- PowerShell parse PASS
- zero runtime/API/model/eval/outcome execution

The supplemental run changed only QA harness plumbing and does not replace or
mutate the canonical S1 lock.

S2 is now specified as one consolidated metadata/hash binding check to a future
OWRQ QUALIFIED_RUNTIME_SCOPE.

S2 execution is NOT authorized.
S3 execution is NOT authorized.
OWRQ qualification is still required before S2 can bind.
M7 and bulk training remain closed.
