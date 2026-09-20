# 08 — Evaluation & Gates

## Gate G0 — Environment
PASS nếu Python/backend/device/storage/dependencies/model source đều khả dụng và version lock được tạo.

## Gate G1 — Data integrity
PASS nếu checksums, schema, license policy, dedup, split, contamination checks và fingerprints đều hợp lệ.

## Gate G2 — Model/runtime compatibility
PASS trước training production nếu kiến trúc + tokenizer có đường export/load llama.cpp và Ollama được xác minh ở mức preflight.

## Gate G3 — Zero-training preflight
Dùng tiny synthetic/sample data, **không chạm fresh seeds**. Kiểm:
- forward/backward;
- save/resume;
- canonical save;
- tiny HF → GGUF conversion nếu feasible;
- reasoning parser format;
- evaluator/adjudicator one-shot.

## Gate G4 — Training health
PASS khi training kết thúc theo contract, không NaN/corruption và checkpoint canonical selection valid.

## Gate G5 — Quality
Metric suite tùy experiment, nhưng tối thiểu:

### General text/Wikipedia
- held-out causal LM loss/perplexity;
- factual QA fixture hoặc retrieval-free closed-book fixture nếu claim cần.

### Code
- held-out code loss;
- syntax validity;
- unit-test/function completion benchmark phù hợp.

### Chat/instruction
- instruction-following fixture;
- refusal/format compliance nếu scope có;
- catastrophic forgetting checks.

### Reasoning
- answer correctness;
- reasoning format valid;
- rationale/answer consistency metric;
- reasoning on/off behavior.

## Gate G6 — Export
HF canonical -> high-fidelity GGUF -> quantized artifacts sinh thành công và hash verify.

## Gate G7 — llama.cpp runtime
Load/inference/parity/reasoning parser PASS.

## Gate G8 — Ollama runtime
Create/import + chat + reasoning contract + parity PASS.

## Gate G9 — Reproducibility QA
Tối thiểu một trong:
- exact deterministic replay trên small reference run;
- canonical regenerate smoke with matching config/data hashes và expected metric tolerance.

## Gate G10 — Promotion
Chỉ PASS nếu G0..G9 theo required matrix đều PASS và evidence bundle checksum verified.

## Threshold policy

Không ship hardcoded universal thresholds. Repo cung cấp baseline defaults cho smoke tests; real experiment phải freeze threshold trong execution contract trước fresh run.
