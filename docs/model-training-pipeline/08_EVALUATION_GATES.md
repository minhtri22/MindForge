# 08 — Evaluation & Gates

Canonical required/optional/forbidden matrix is in 19_GATE_MATRIX_INFERENCE_CONTRACT.md.

## G0 Environment
Resolved dependencies, device/backend/precision, storage estimate, source/tool locks and sandbox capability.

## G1 Data integrity
Checksums, source identity, license/privacy/secret policy, dedup, contamination, splits, token stream and fingerprints.

## G2 Compatibility
Model/tokenizer/template + pinned llama.cpp/GGUF/Ollama + reasoning capability.

## G3 Zero-training preflight
No fresh resources. Forward/backward, save/resume, canonical save, tiny export when feasible, schema validation, reasoning parser, adjudicator.

## G4 Training health
Phase execution terminates according to contract with committed valid checkpoint and no health violation.

## G5 Quality
All gate-driving metrics must validate evaluation_contract schema and name baseline/comparator. Protected capability suite runs parent and after each phase.

## G6 Export
HF -> high-fidelity GGUF -> required quantized artifacts with verified hashes.

## G7 llama.cpp
Load/infer/parity/reasoning semantics PASS.

## G8 Ollama
Safe create/import + chat + reasoning semantics + parity PASS.

## G9 Reproducibility
Reference micro-replay or locked canonical regeneration according to run class.

## G10 Promotion
Only release/eligible confirmatory artifacts with every required gate PASS and evidence seal verified.

## Threshold policy
No universal real-experiment threshold. Calibration freezes threshold before fresh evidence. Smoke thresholds only prove plumbing/format.
