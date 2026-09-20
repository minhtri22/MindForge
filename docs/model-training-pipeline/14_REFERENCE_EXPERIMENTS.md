# 14 — Reference Experiments

## R0 — End-to-end micro smoke

Mục tiêu: chứng minh plumbing, không chứng minh quality.

- supported tiny decoder model;
- vài nghìn dòng public/synthetic text+code;
- vài trăm reasoning SFT examples;
- 10–100 training steps;
- HF save;
- GGUF convert;
- llama.cpp infer;
- Ollama infer;
- reasoning contract.

## R1 — Wikipedia CPT qualification

Mục tiêu: CPT không phá chat/reasoning vượt threshold.

1. base evaluation;
2. fixed Wikipedia snapshot subset;
3. CPT token budget freeze;
4. evaluate held-out text + instruction + reasoning;
5. adjudicate catastrophic forgetting;
6. export only if PASS.

## R2 — Code CPT qualification

1. code corpus with license metadata;
2. contamination scan against code eval fixtures;
3. CPT;
4. held-out loss + syntax/unit test benchmark;
5. instruction/reasoning regression checks;
6. export.

## R3 — Mixed Wikipedia + code + reasoning SFT

Đây là reference gần với mục tiêu người dùng:

```text
Base reasoning/instruct model
 -> CPT mixture: Wikipedia + code
 -> SFT/replay: chat instruction
 -> Reasoning SFT
 -> fresh eval
 -> HF canonical
 -> F16 GGUF
 -> Q4_K_M GGUF
 -> llama.cpp
 -> Ollama
 -> evidence bundle
```

### Expected user-facing demo

Prompt:

```text
Một hàm Python đang có độ phức tạp O(n^2). Hãy đề xuất cách giảm xuống O(n log n) nếu có thể và giải thích lý do.
```

Normalized API response:

```json
{
  "reasoning": "...các bước phân tích được model sinh ra...",
  "answer": "...kết luận cuối...",
  "runtime": "ollama",
  "model_artifact": "...",
  "reasoning_kind": "model_generated_rationale"
}
```

Acceptance không chấm reasoning theo độ dài; chấm task correctness, consistency và parseability.
