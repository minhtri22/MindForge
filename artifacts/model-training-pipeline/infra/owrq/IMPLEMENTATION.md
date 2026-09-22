# OWRQ Implementation

Status: STATIC IMPLEMENTATION / ZERO-SCIENCE QA PENDING

The implementation consists of:

- `tools/ollama_windows_adapter.py` — reusable runtime adapter consumed later by M6R2;
- `tools/owrq_qualify.py` — non-scientific local qualification orchestrator;
- `scripts/owrq_qualify_local.ps1` — future one-click local wrapper.

The adapter contract is the exact M6R2 consumer interface snapshot blob:
`0973749fc01dfe873ec7be92e55d2898fc67b9ed`.

Qualification never imports `eval_v1`, does not pull/create/delete the fixture, and does not score fixture output.
