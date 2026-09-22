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


## 2026-09-22 — OWRQ implementation locked / local infra qualification authorized

Canonical implementation:
f40c3ffcdfdd56dd0e50ae16ecf119d19434f587

Exact blobs:
- adapter: 075b3b354bbd0c7674d629070d99769d201ad619
- qualifier: ea0935f4f56e8aed5de099a711ca2bd8c86a0454
- wrapper: dfe0a2fe4ffc4f07289131d54f8722aa0aeec184
- tests: 809e3c6301c7131c845619e38053c2a46ba80a09
- workflow: 3f934063560b2f0c496d11f4182ce0cb79395435
- M6R2 consumer interface snapshot: 0973749fc01dfe873ec7be92e55d2898fc67b9ed

Static QA:
- run 35751137271 / job 106825278054
- 17/17 tests PASS
- Python compile PASS
- PowerShell parse PASS
- no local OWRQ qualification in CI
- no scientific execution

All seven adversarial implementation findings are repaired.

OWRQ local qualification is now authorized as reusable NON-SCIENTIFIC
infrastructure work. It is not a one-shot scientific attempt.

Every run must use a unique evidence directory and exact locked implementation.

M6R2 S2/S3 remain unauthorized. A successful local OWRQ qualification only
produces a reusable QUALIFIED_RUNTIME_SCOPE artifact for later S2 binding.


## 2026-09-22 — Local qualification PASS / OWRQ formally closed

Source artifacts:
- OWRQ_QUALIFICATION_REPORT.json
  - SHA256 e5bafb7d07707f57bf274649683e50f929ea7f8d973d1e5d0efc6f359d7df689
  - status QUALIFIED_RUNTIME_SCOPE
- QUALIFIED_RUNTIME_SCOPE.json
  - SHA256 4c15da27c2087b14d9c48689e5e811520c422b4b45eaddc3838bd4432ceb0370
  - status QUALIFIED_RUNTIME_SCOPE

Observed qualified tuple:
- Ollama 0.34.2
- ollama.exe SHA256 ad41dcf55c5de96d4a0bff7c559a17285c3aa064a6f12d23db3ebf59ad8e4125
- adapter blob 075b3b354bbd0c7674d629070d99769d201ad619
- machine fingerprint a208a4c542eeaf70363b77344cac81eec531cc0c9be85aada22d61c112c08993
- host 127.0.0.1:11468
- KV cache f16
- flash attention forced false / resolved off
- fixture llama3.2:1b digest baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878

All ten qualification gates PASS.
Scientific firewall PASS:
no eval_v1, no quality/reasoning scoring, no model pull/create/delete.

Terminal result:
QUALIFIED_RUNTIME_SCOPE / FORMALLY_CLOSED

This authorizes no M6R2 science by itself.
The exact scope may now be consumed by M6R2 S2 metadata binding.
