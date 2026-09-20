# 10 — Test Plan

## A. Unit tests

- canonical config hash stable;
- file/directory SHA256;
- split determinism;
- dataset manifest validation;
- reasoning parser native/tagged;
- checkpoint manifest schema;
- lineage hash chaining;
- adjudicator threshold boundaries;
- Modelfile generation.

## B. Integration tests

1. Tiny tokenizer/data -> 2 training steps -> save -> resume -> 2 steps.
2. Save HF canonical -> reload -> generate.
3. HF -> GGUF small supported model -> llama.cpp load.
4. GGUF -> Ollama create -> API inference.
5. Reasoning output parsed identically by wrappers.

## C. Failure injection

- corrupt shard;
- wrong checksum;
- disk full simulation;
- killed training process then resume;
- wrong base model for adapter;
- unsupported architecture;
- tokenizer mismatch;
- malformed `<think>` tags;
- Ollama unavailable;
- llama.cpp converter/version mismatch;
- metric just below threshold.

## D. Reproducibility test

Reference micro-run fixed seed/data/model must produce:
- same config/data hashes;
- same selected checkpoint step;
- metrics within declared deterministic/tolerance contract;
- same artifact inventory.

## E. Windows-specific

- PowerShell paths with spaces;
- long path handling;
- executable discovery `.exe`;
- subprocess quoting;
- symlink absence fallback;
- resume after terminal interruption.

## F. Acceptance test fixture

Repo phải có `tests/e2e/tiny_reasoning_model/` hoặc một supported tiny base model downloaded by script, cùng public/synthetic mini datasets để CI/local chạy end-to-end mà không cần hàng giờ training.
