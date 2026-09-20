# Evidence-Governed Model Training Pipeline — Bộ yêu cầu triển khai

## 1. Mục tiêu

Xây dựng một phần mềm pipeline có thể nhận **base model hoặc kiến trúc được hỗ trợ**, các **dataset công khai** (ví dụ Wikipedia, corpus lập trình), chạy quá trình chuẩn bị dữ liệu → training → evaluation → checkpointing → adjudication → export, và tạo ra một artifact cuối có thể:

1. chạy trực tiếp ở Hugging Face-compatible runtime để đối chiếu;
2. convert sang **GGUF**;
3. load và chạy bằng **llama.cpp**;
4. import/create và chạy bằng **Ollama**;
5. khi được yêu cầu, trả ra **reasoning trace/rationale** tách biệt với final answer theo contract của pipeline;
6. đi kèm đầy đủ provenance, hashes, config, metrics, lineage và evidence để tái lập.

Pipeline không được đánh đồng `train loss giảm` với `model đạt yêu cầu`. Checkpoint chỉ được promote nếu toàn bộ gate đã định trước PASS.

## 2. Kết quả người dùng phải nhận được sau một run hợp lệ

```text
runs/<run_id>/
├── frozen/
│   ├── run_config.yaml
│   ├── environment.lock.json
│   ├── git.lock.json
│   ├── data_manifest.json
│   └── execution_contract.json
├── data/
│   ├── fingerprints.json
│   └── sample_audit.jsonl
├── checkpoints/
│   ├── step-*/
│   └── canonical/
├── eval/
│   ├── hf/
│   ├── llama_cpp/
│   ├── ollama/
│   └── adjudication.json
├── export/
│   ├── hf/
│   ├── model-f16.gguf
│   ├── model-q8_0.gguf            # nếu cấu hình
│   ├── model-q4_k_m.gguf          # nếu cấu hình
│   ├── Modelfile
│   └── runtime_manifest.json
├── evidence/
│   ├── report.md
│   ├── metrics.json
│   ├── failures.jsonl
│   ├── SHA256SUMS
│   └── evidence.zip
└── lineage.jsonl
```

Một run chỉ có trạng thái `PROMOTED` khi `adjudication.json` nói PASS và tất cả artifact bắt buộc tồn tại + khớp hash.

## 3. Phạm vi phiên bản đầu (MVP)

MVP phải hỗ trợ:

- Causal decoder-only LLM.
- Continued pretraining (CPT) trên raw text/code.
- Supervised fine-tuning (SFT) cho instruction/chat.
- Reasoning SFT với output tách `reasoning` và `answer`.
- Full fine-tune **hoặc** PEFT/LoRA (ít nhất một đường phải chạy end-to-end; thiết kế không được khóa kiến trúc vào một framework duy nhất).
- Hugging Face/Safetensors làm canonical training artifact.
- GGUF export bằng llama.cpp converter đã pin commit.
- llama.cpp smoke/eval thật.
- Ollama create/import + chat smoke/eval thật.
- Resume từ checkpoint bảo toàn optimizer/scheduler/RNG khi mode training yêu cầu.
- Evidence/governance/hashing bắt buộc.

Không thuộc MVP: distributed multi-node, RLHF online, multimodal, Mixture-of-Experts custom architecture, serving cluster, UI web đầy đủ.

## 4. Nguyên tắc bất biến

1. **Freeze before fresh evidence.** Mọi metric, threshold, seed, split, checkpoint-selection rule và export rule phải freeze trước fresh run.
2. **No silent mutation.** Config/data/code thay đổi phải làm run mới hoặc invalid run cũ.
3. **Checkpoint != evidence.** Một checkpoint đẹp không thay thế được kết quả đa-seed/matched baseline khi claim yêu cầu thống kê.
4. **Runtime validation is mandatory.** GGUF tạo được nhưng không chạy llama.cpp/Ollama = FAIL export gate.
5. **Reasoning is an output contract, not proof of causality.** Rationale mà model sinh ra có thể là post-hoc; phần mềm phải gọi đúng tên và không tuyên bố đây là bằng chứng chắc chắn về cơ chế nội tại.
6. **Architecture compatibility first.** Không train hàng giờ rồi mới phát hiện llama.cpp/Ollama không hỗ trợ kiến trúc/tokenizer.
7. **License provenance is first-class.** Mỗi shard/document phải truy được nguồn/license theo mức khả thi của nguồn dữ liệu.

## 5. Thứ tự đọc cho local agent

Local agent phải đọc lần lượt:

1. `00_PRODUCT_REQUIREMENTS.md`
2. `01_SCIENTIFIC_GOVERNANCE.md`
3. `02_SYSTEM_ARCHITECTURE.md`
4. `03_DATA_PIPELINE.md`
5. `04_TRAINING_PIPELINE.md`
6. `05_REASONING_OUTPUT_CONTRACT.md`
7. `06_CHECKPOINT_PROVENANCE.md`
8. `07_EXPORT_LLAMA_OLLAMA.md`
9. `08_EVALUATION_GATES.md`
10. `09_CLI_CONFIG_API.md`
11. `10_TEST_PLAN.md`
12. `11_ACCEPTANCE_CRITERIA.md`
13. `12_IMPLEMENTATION_PLAN.md`
14. `13_SECURITY_LICENSE_REPRODUCIBILITY.md`
15. `14_REFERENCE_EXPERIMENTS.md`
16. `AGENT_MASTER_PROMPT.md`

Không được bỏ qua gate để “cho demo chạy được”.
