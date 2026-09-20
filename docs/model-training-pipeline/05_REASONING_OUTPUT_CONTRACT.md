# 05 — Reasoning Output Contract

Canonical semantics: 18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md và schemas/reasoning_response.schema.json.

## 1. Normalized response

Response chứa non-empty answer, reasoning string hoặc null theo mode, reasoning_kind=model_generated_rationale, reasoning_mode, reasoning_present, transport, parser_status, runtime và artifact identity.

## 2. Modes

visible yêu cầu non-empty parsed rationale trên reasoning fixture; hidden trả reasoning=null; off yêu cầu runtime/model thật sự hỗ trợ disable, nếu không phải explicit unsupported failure.

## 3. Three layers

Model-specific training serializer, runtime-specific parser/transport và normalized API là ba lớp khác nhau. Runtime thinking field không phải universal training channel.

## 4. Tagged fallback

Chỉ khi model/template contract approve tags và escaping/parser tests PASS.

## 5. Metrics

Format validity, answer correctness, reasoning non-empty như format gate, verifier-aware reasoning checks, answer/reasoning consistency, on/off/hidden behavior và cross-runtime parity. Reasoning length không là quality metric.

## 6. Interpretation

Rationale là model-generated explanatory output, không phải proof của faithful hidden computation.
