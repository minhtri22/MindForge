# 02 — System Architecture

## 1. Modules

Pipeline gồm cli, config, registry, data, training, reasoning, eval, export, provenance, runtime, security và evidence modules.

## 2. Typed adapter contracts

ModelAdapter phải cung cấp immutable identity/revision, compatibility report, train load/save, tokenizer/chat-template hash, structured ReasoningCapability và model-specific training serializer.

DatasetAdapter phải cung cấp immutable source identity, license/privacy/secret policy, document stream/identity, transform manifest, fingerprint và freshness class.

TrainingBackend phải cung cấp resolved device/precision/determinism, phase train, declared resume fidelity, atomic checkpoint writer và metrics.

RuntimeAdapter tách locate read-only khỏi explicit installation; cung cấp load/infer/unload, capability resolution, runtime-specific reasoning parser và translation từ frozen InferenceGenerationContract.

## 3. Storage

Critical state phải reconstruct được từ runs/<run_id> không cần private DB. Cache ngoài được phép nhưng không là sole evidence.

## 4. Tool locks

Confirmatory/release pin exact trainer, llama.cpp commit/build và Ollama version.

## 5. Compatibility matrix

Trước production training phải PASS HF model/tokenizer, tokenizer round-trip, chat template khi needed, pinned llama.cpp support, GGUF path, Ollama path, reasoning serializer/parser khi required, sandbox capability cho code benchmarks và disk/resource preflight.
