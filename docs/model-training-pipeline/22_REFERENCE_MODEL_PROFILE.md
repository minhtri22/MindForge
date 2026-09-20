# 22 — R0 Reference Model Profile

## 1. Purpose

R0 uses one fixed model to prove pipeline plumbing, not scientific quality:

- profile_id: `qwen2.5-0.5b-instruct-r0-v1`
- model: `Qwen/Qwen2.5-0.5B-Instruct`
- revision: `7ae557604adf67be50417f59c2c2f167def9a775`
- architecture: `qwen2`
- role: `smoke_reference`

The machine-readable source of truth is `profiles/qwen2.5-0.5b-instruct-r0.yaml`, validated by `schemas/model_profile.schema.json`.

Changing model, revision, serializer, reserved markers, or expected export architecture is a spec change requiring QA.

## 2. Chat/template handling

The adapter must load tokenizer/chat-template assets from the exact pinned revision. It must not re-create Qwen's chat template from memory.

For ordinary instruct/chat examples:
1. build semantic `messages`;
2. serialize through the pinned tokenizer's canonical chat template;
3. verify tokenizer/template hash against the resolved profile evidence.

## 3. R0 tagged-reasoning training serializer

Qwen2.5-0.5B-Instruct is used here as a small instruct model, not assumed to expose a native reasoning channel.

R0 `reasoning_sft` uses the explicit serializer `tagged_reasoning_v1`.

Semantic sample:

```json
{
  "messages": [{"role":"user","content":"..."}],
  "reasoning":"...",
  "answer":"..."
}
```

Assistant content before application of the canonical Qwen chat template:

```text
<think>{reasoning}</think>
<answer>{answer}</answer>
```

Rules:
- tags are literal reserved delimiters for R0 only;
- a sample containing any reserved delimiter inside reasoning/answer is quarantined in v1 rather than escaped ambiguously;
- loss mask is assistant-content only;
- reasoning and answer are both supervised for R0 reasoning_sft;
- data layer stores semantic fields; only ModelAdapter serializer creates tags;
- inference parser must require exactly one well-formed think block and one answer block for the R0 reasoning fixture;
- malformed/nested/multiple delimiter blocks -> parser FAIL;
- when reasoning mode is off, the R0 tagged profile does not claim native disable semantics; off-mode capability is determined by adapter/runtime packaging and may be unsupported.

## 4. Runtime expectations

The profile does not hardcode that every current llama.cpp/Ollama build supports the model. Preflight must prove support against pinned runtime versions.

Expected paths to test:
- HF/Safetensors reload using exact tokenizer/template;
- pinned llama.cpp HF->GGUF converter recognizes Qwen2 architecture;
- high-fidelity GGUF load/infer;
- required quantized GGUF load/infer;
- Ollama import of the verified GGUF;
- tagged reasoning parser behavior.

## 5. Why R0 does not define the scientific baseline

The exact experiment parent is the scientific baseline. R0 model only becomes the parent baseline when the experiment actually starts from this exact artifact.

A later 3B/7B/etc experiment must define its own exact parent and matched control where needed.
