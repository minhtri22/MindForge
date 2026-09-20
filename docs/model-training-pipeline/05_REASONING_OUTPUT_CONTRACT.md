# 05 — Reasoning Output Contract

## 1. Mục tiêu

Khi người dùng hỏi model, hệ thống phải có chế độ trả:

```json
{
  "reasoning": "Chuỗi lập luận/rationale mà model xuất ra",
  "answer": "Câu trả lời cuối",
  "reasoning_kind": "model_generated_rationale"
}
```

`reasoning` là **output do model sinh ra**, hữu ích để kiểm tra và debug, nhưng không được mô tả như bằng chứng chắc chắn rằng đây là toàn bộ cơ chế tính toán nội tại của model.

## 2. Hai đường runtime

### Native reasoning channel — ưu tiên
Nếu base architecture/chat template/runtime hỗ trợ thinking/reasoning native:
- giữ đúng template;
- training samples map reasoning vào reasoning/thinking channel tương ứng;
- Ollama adapter đọc `message.thinking`/`thinking`;
- llama.cpp adapter đọc `reasoning_content` hoặc output parser tương ứng.

### Tag-based fallback
Nếu runtime không có native channel nhưng model/template cho phép:

```text
<think>
...
</think>
<answer>
...
</answer>
```

Runtime adapter phải parse và trả JSON contract ở trên. Raw tag không phải API contract cuối.

## 3. Không phụ thuộc prompt hack

Acceptance không được chỉ dùng system prompt “hãy giải thích”. Model phải PASS reasoning fixture sau training/template packaging. Nếu tắt reasoning, final answer vẫn phải parse được.

## 4. Reasoning dataset rules

- final answer phải có ground truth/verifier khi khả thi;
- rationale phải nhất quán với answer;
- loại rationale chứa answer sai dù văn phong tốt;
- không train hidden/private chain-of-thought từ hệ thống đóng nếu không có quyền sử dụng;
- cho phép synthetic rationale từ model/solver có license/quyền phù hợp, nhưng ghi provenance.

## 5. Evaluation

Tối thiểu đo:

1. `format_valid_rate` — parse reasoning + answer.
2. `answer_accuracy` — metric task-specific.
3. `reasoning_nonempty_rate` khi reasoning được bật.
4. `reasoning_answer_consistency` — verifier/LLM-judge chỉ là metric phụ nếu không có verifier chính xác.
5. `final_answer_without_reasoning_regression` — ability to answer khi reasoning disabled/hidden.
6. `runtime_reasoning_field_parity` giữa HF adapter, llama.cpp, Ollama.

Không dùng “reasoning dài” làm quality metric.

## 6. API behavior

```python
result = pipeline.chat(
    model="run:abc123",
    messages=[...],
    reasoning=True,
)
assert result.reasoning is not None
assert result.answer is not None
```

CLI:

```text
pipeline chat --model run:abc123 --reasoning on
```

## 7. Compatibility note

Pipeline phải detect base model có native thinking template hay không. Nếu target bắt buộc là reasoning field native trong Ollama/llama.cpp mà model không hỗ trợ, preflight phải FAIL hoặc yêu cầu tag-based wrapper explicitly approved; không được giả vờ native support.
