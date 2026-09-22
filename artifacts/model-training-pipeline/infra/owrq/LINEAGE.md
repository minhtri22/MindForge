# OWRQ LINEAGE

## 2026-09-22 — Program opened

Parent governance:
750d6358a88e738cfaf971b3a5db3192f7622889

Program type:
NON-SCIENTIFIC INFRASTRUCTURE QUALIFICATION

Origin:
M6R RFD-C1 identified a runtime configuration conflict:
quantized V-cache q4_0 + flash-attn off caused llama-server initialization failure.

OWRQ does not rerun M6R and does not test parity.

Its role is to qualify a reusable installed-Ollama Windows runtime scope for future studies.

Initial repair target:
- dedicated installed-Ollama process on 127.0.0.1:11468
- process-scoped OLLAMA_KV_CACHE_TYPE=f16
- do not set OLLAMA_FLASH_ATTENTION
- no global environment mutation
- no mutation of existing port-11434 service
- no pull/create/delete of user models

M6R2 specification may proceed independently.
M6R2 runtime execution remains blocked until a future OWRQ-qualified scope is available.


## 2026-09-22 — Specification QA PASS

Reviewed commit:
4e22791a667aa055810ec8491544be9e1f3784fd

Result:
- specification QA PASS
- unresolved findings = 0
- scientific firewall PASS
- reusable-scope contract PASS
- M6R2 execution remains unauthorized

OWRQ implementation remains a separate infrastructure-lane next step.
It does not block M6R2 static design/implementation.
