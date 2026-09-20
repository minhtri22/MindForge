# 07 — Export to llama.cpp / Ollama

## 1. Nguyên tắc

Export là một phase có gate riêng, không phải bước copy file.

## 2. Pin llama.cpp

`llama_cpp.lock.json` phải chứa commit SHA, source URL, build flags và converter path. Pipeline phải gọi converter từ source đã pin.

### Preflight trước training

- chạy converter capability inspection (hoặc registry tương đương);
- xác nhận architecture được nhận diện;
- xác nhận tokenizer/chat template support;
- ghi compatibility report.

## 3. HF → GGUF

Canonical path:

```text
canonical HF/Safetensors
   -> convert_hf_to_gguf.py
   -> F16/BF16 (high-fidelity GGUF)
   -> llama.cpp load test
   -> optional quantization targets
```

Không quantize trước khi high-fidelity GGUF load test PASS.

## 4. Quantization

Targets do config freeze, ví dụ:

```yaml
export:
  gguf:
    base: f16
    quantize:
      - q8_0
      - q4_k_m
```

Mỗi quantized artifact phải eval riêng. Không suy ra Q4 PASS từ F16 PASS.

## 5. llama.cpp runtime verification

Bắt buộc:

- model load;
- tokenizer/chat template smoke;
- deterministic fixture (temperature=0 khi hợp lệ);
- reasoning on/off fixture;
- context length basic test;
- latency/token stats;
- crash-free multi-turn chat fixture.

Nếu reasoning-capable template được dùng, verify parser/`reasoning_content` path hoặc tag parser đã freeze.

## 6. Ollama packaging

Pipeline sinh `Modelfile` từ artifact verified. Hai đường:

### GGUF-preferred

```text
FROM ./model-q4_k_m.gguf
```

### Safetensors direct
Chỉ dùng nếu architecture/import path được preflight support và đã test. GGUF vẫn là artifact portability bắt buộc của MVP.

## 7. Ollama verification

- `ollama create <ephemeral-test-name>`;
- `ollama run` hoặc API chat/generate;
- reasoning enabled nếu supported;
- verify separate `thinking` field nếu native;
- verify final content;
- capture version and response metadata;
- cleanup ephemeral model sau test nếu config yêu cầu.

## 8. Runtime parity

Pipeline phải chạy cùng fixture trên:

```text
HF canonical
GGUF high-fidelity / llama.cpp
GGUF quantized / llama.cpp
Ollama packaged artifact
```

Adjudicator so sánh task metrics, not exact text. Threshold regression freeze trước export.

## 9. Failure categories

- `EXPORT_UNSUPPORTED_ARCH`
- `EXPORT_TOKENIZER_MISMATCH`
- `GGUF_LOAD_FAIL`
- `GGUF_QUALITY_REGRESSION`
- `OLLAMA_CREATE_FAIL`
- `OLLAMA_RUNTIME_FAIL`
- `REASONING_PARSE_FAIL`
- `RUNTIME_PARITY_FAIL`

## 10. Current external compatibility references

Local agent phải đọc/kiểm tra version pin hiện tại trước implement:

- llama.cpp converter: https://github.com/ggml-org/llama.cpp/blob/master/convert_hf_to_gguf.py
- llama.cpp model docs: https://github.com/ggml-org/llama.cpp/blob/master/docs/models.md
- llama.cpp CLI reasoning options: https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md
- Ollama import: https://github.com/ollama/ollama/blob/main/docs/import.mdx
- Ollama Modelfile: https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx
- Ollama thinking: https://github.com/ollama/ollama/blob/main/docs/capabilities/thinking.mdx

Không hardcode assumptions từ tài liệu này nếu upstream version pin khác.
