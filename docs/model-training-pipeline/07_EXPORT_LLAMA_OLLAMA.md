# 07 — Export to llama.cpp / Ollama

Canonical runtime/export semantics: 19_GATE_MATRIX_INFERENCE_CONTRACT.md.

## 1. Pinning

llama_cpp.lock.json pins commit SHA, source URL, build flags and converter path/hash. ollama.lock.json pins exact Ollama version.

## 2. Preflight

Before production training, evidence must show pinned converter/model capability inspection, tokenizer/chat-template compatibility and runtime target support. Registry-only support is insufficient for release.

## 3. HF -> GGUF

Canonical path:
HF/Safetensors -> high-fidelity GGUF -> llama.cpp load/infer -> required quantized targets.

High-fidelity dtype policy is exactly one of preserve_source, f16, bf16 and resolved dtype is recorded.

## 4. Quantization

Each required quantized artifact has its own load/infer/quality gate. Q4 cannot inherit F16 PASS.

## 5. Artifact topology

GGUF may be single_file or shard_set. Shard manifest stores ordered filenames/hashes and aggregate hash.

## 6. llama.cpp verification

Use frozen InferenceGenerationContract for prompt/generation semantics, reasoning modes and context. Capture build/version, latency/tokens and parser behavior.

## 7. Ollama packaging

Generated Modelfile derives all inference parameters from frozen contract. Do not hardcode independent temperature/top_p. Ephemeral model naming/cleanup follows 19 contract.

## 8. Runtime parity

Run same fixture + normalized generation contract across HF, high-fidelity GGUF, required quantized GGUF and Ollama. Compare task metrics/format/capability, not exact text.

## 9. Tool installation

Runtime locate is read-only. Installation/update is explicit according to 20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md.

## 10. Failure codes

EXPORT_UNSUPPORTED_ARCH, EXPORT_TOKENIZER_MISMATCH, GGUF_LOAD_FAIL, GGUF_QUALITY_REGRESSION, OLLAMA_CREATE_FAIL, OLLAMA_RUNTIME_FAIL, REASONING_PARSE_FAIL, RUNTIME_PARITY_FAIL.
