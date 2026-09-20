# 18 — Reasoning Capability & Runtime Contract

## 1. Tách ba lớp bắt buộc

Không được coi runtime `thinking` field là training channel chung.

```text
SUPERVISED EXAMPLE
   -> MODEL-SPECIFIC TRAINING SERIALIZER
   -> TOKEN SEQUENCE / LOSS MASK
   -> MODEL
   -> RUNTIME-SPECIFIC OUTPUT PARSER
   -> NORMALIZED PIPELINE RESPONSE
```

Ba lớp có version/hash độc lập:

1. `TrainingSerializer` — model/chat-template specific.
2. `RuntimeReasoningParser` — HF/llama.cpp/Ollama specific.
3. `NormalizedReasoningResponse` — API stable của pipeline.

## 2. ReasoningCapability

ModelAdapter phải trả structured capability:

```yaml
supported: true
training_format: qwen2_chat_v1
transport_options: [native_runtime_field, tagged_text]
visibility_modes: [visible, hidden, off]
effort_levels: []
supports_disable: true
supports_hide: true
native_runtime_support:
  hf: parser
  llama_cpp: parser
  ollama: thinking_field
```

Không dùng `str` tự do.

## 3. Normalized request

```yaml
reasoning:
  mode: visible   # visible | hidden | off
  effort: default # default | low | medium | high | max, only when capability allows
```

- `visible`: reasoning được trả cho caller.
- `hidden`: model/runtime có thể reasoning nhưng normalized response không expose text; phải report `reasoning_present=true|false|unknown`.
- `off`: yêu cầu model/runtime tắt reasoning; nếu capability không cho phép -> explicit `UNSUPPORTED_REASONING_MODE`, không silently map.
- `unsupported`: là capability state, không phải request mode.

## 4. Normalized response

```json
{
  "answer": "final answer",
  "reasoning": "visible rationale or null",
  "reasoning_kind": "model_generated_rationale",
  "reasoning_mode": "visible",
  "reasoning_present": true,
  "transport": "native_runtime_field",
  "parser_status": "ok",
  "runtime": "ollama",
  "model_artifact": "sha256:..."
}
```

Rules:

- `answer` minLength 1.
- mode=`visible` + capability supported -> `reasoning` minLength 1 for reasoning fixture.
- mode=`hidden` -> `reasoning=null`.
- mode=`off` -> `reasoning=null`; if runtime cannot truly disable, request FAIL rather than pretend.
- parser ambiguity/malformed tags -> `parser_status != ok` and reasoning gate FAIL.

## 5. Native vs tagged transport

`native_runtime_field` chỉ mô tả output transport/runtime parser.

Training serializer phải dựa vào pinned model chat template/special tokens. Dataset fields `reasoning` và `answer` được serializer map theo model-specific format; không hardcode mọi model thành `<think>`.

`tagged_text` fallback chỉ hợp lệ khi:

- model/template contract explicitly supports tags;
- tags freeze trong config;
- escaping/nested-tag behavior defined;
- parser tests PASS;
- acceptance evidence ghi `transport=tagged_text`.

## 6. Reasoning metrics

`reasoning_nonempty_rate` chỉ là **format gate**.

Quality reasoning phải dùng task-aware evidence theo thứ tự ưu tiên:

1. deterministic verifier/solver/unit tests;
2. structured intermediate checks;
3. consistency with answer;
4. pinned LLM judge chỉ khi không có verifier mạnh hơn.

LLM judge contract bắt buộc pin:

- model ID/revision;
- prompt template hash;
- generation parameters;
- runtime/version;
- raw judge response;
- parser version.

Judge không được là sole gate cho objectively verifiable tasks.

## 7. Runtime capability resolution

Preflight tạo capability matrix trên exact pinned runtime versions. Không assume một boolean chung.

Ollama adapter phải map request vào capability của model/runtime cụ thể; nếu runtime dùng levels thay boolean, adapter giữ semantic level và evidence.

llama.cpp adapter phải pin parser/reasoning-format option tương ứng với build/commit.

## 8. Cross-runtime parity

Parity so:

- answer task metric;
- reasoning parse success;
- reasoning visibility semantics;
- capability behavior;
- no catastrophic answer regression.

Không yêu cầu exact reasoning string hoặc exact generated text.

## 9. Safety/semantics

Output rationale là `model_generated_rationale`; không tuyên bố là faithful hidden computation. UI/API có thể hide rationale mà vẫn giữ final answer.
