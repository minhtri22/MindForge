# Master Prompt cho Local Coding Agent

Bạn đang triển khai **Evidence-Governed Model Training Pipeline**.

## Nhiệm vụ

Đọc toàn bộ tài liệu trong bundle theo thứ tự README chỉ định, sau đó xây phần mềm production-oriented MVP thỏa `11_ACCEPTANCE_CRITERIA.md`.

## Quy tắc làm việc

1. Không tự đơn giản hóa các gate governance chỉ để demo PASS.
2. Không train production/fresh run trước khi compatibility + zero-training preflight PASS.
3. Không hardcode một model ID; dùng registry/adapter và một model nhỏ chỉ cho test.
4. Không giả định mọi Hugging Face model convert được sang GGUF. Phải preflight compatibility với llama.cpp version pin.
5. Không coi “convert file thành công” là runtime success; phải load/infer bằng llama.cpp và Ollama thật.
6. Reasoning API phải trả `reasoning` tách `answer`. Ưu tiên native runtime thinking/reasoning field; fallback tag parser phải được ghi rõ.
7. Không tuyên bố model-generated rationale là faithful hidden chain-of-thought.
8. Không dùng `latest/main` cho confirmatory execution; resolve version/commit rồi freeze.
9. Mọi run phải tạo hashes, lineage và evidence.
10. Mọi milestone phải có test + exit gate trước khi sang milestone sau.

## Cách báo cáo sau mỗi milestone

```text
MILESTONE: Mx
STATUS: PASS | FAIL | BLOCKED
GIT_SHA: ...
TESTS: passed/failed
ARTIFACTS: ...
EVIDENCE: ...
BLOCKERS: ...
NEXT_SCIENTIFIC_STEP: ...
```

## Không được làm

- tự đổi threshold sau khi xem fresh results;
- tự thêm fresh seeds để cứu FAIL;
- bỏ qua license/data provenance;
- merge adapter vào sai base model;
- thay tokenizer mà không rerun compatibility gates;
- xóa checkpoint/evidence trước bundle verification;
- báo “Ollama compatible” khi chưa chạy Ollama;
- báo “reasoning supported” chỉ vì prompt yêu cầu giải thích.

## Definition of Done

Chỉ DONE khi AC-01..AC-14 đều có machine-verifiable evidence. Nếu một AC chưa thể thực hiện do upstream/runtime/hardware, báo `BLOCKED`, nêu chính xác AC và evidence; không đánh dấu PASS giả.
