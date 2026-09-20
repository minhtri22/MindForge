# 12 — Implementation Plan for Local Agent

## Milestone M0 — Skeleton + contracts
- package layout;
- typed config models;
- run state machine;
- schemas;
- hashing/lineage;
- CLI skeleton;
- tests.

**Exit:** config resolve/hash + run creation + state transitions PASS.

## M1 — Data plane
- local files;
- Wikipedia-style public text adapter;
- public code adapter interface;
- normalization/filter/dedup/split/tokenize;
- data manifest/fingerprint;
- license policy.

**Exit:** deterministic micro dataset output + contamination fixture PASS.

## M2 — Trainer backend
- one PyTorch/HF-compatible backend;
- CPT;
- SFT/reasoning SFT;
- checkpoint/resume;
- metrics logging.

**Exit:** tiny model micro-run save/resume/reload PASS.

## M3 — Governance
- preflight;
- execution lock;
- fresh-seed guard;
- adjudicator;
- evidence report.

**Exit:** intentional FAIL cannot auto-rescue.

## M4 — Reasoning contract
- native field adapter interface;
- tag-based fallback parser;
- data formatter;
- reasoning tests.

**Exit:** API returns `{reasoning, answer}`.

## M5 — llama.cpp export
- version/commit lock;
- converter invocation;
- GGUF verify;
- quantize;
- llama runtime fixtures.

**Exit:** tiny trained model runs in llama.cpp.

## M6 — Ollama
- Modelfile generation;
- create/import;
- API/runtime test;
- thinking/reasoning extraction;
- cleanup.

**Exit:** tiny trained model runs through Ollama and passes reasoning contract.

## M7 — Full E2E reference
- Wikipedia mini snapshot;
- code mini corpus;
- reasoning SFT mini set;
- end-to-end command;
- evidence ZIP.

**Exit:** AC-01..AC-14 PASS.

## M8 — Hardening
- Windows PowerShell installer/bootstrap;
- structured logs;
- failure injection;
- docs;
- reproducibility replay.

## Implementation rule
Không merge milestone kế tiếp nếu exit gate milestone hiện tại chưa PASS. Commit SHA phải được ghi vào `LINEAGE.md` hoặc machine lineage sau mỗi milestone.
