# Evidence-Governed Model Training Pipeline — Specification

## 1. Mục tiêu

Xây dựng pipeline biến một exact base model + public/local datasets + frozen execution contract thành canonical HF/Safetensors checkpoint, auditable evidence, GGUF, llama.cpp/Ollama runnable artifacts và normalized answer/reasoning API.

Pipeline không dùng train loss đơn lẻ làm verdict. PASS/FAIL phải dựa vào frozen gate + baseline/comparator contract.

## 2. Canonical contracts

Nếu tài liệu tóm tắt mâu thuẫn với contract/schema dưới đây, contract/schema thắng:

- 15_BASELINE_COMPARATOR_CONTRACT.md
- 16_CANONICAL_CONFIG_STATE_MACHINE.md
- 17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md
- 18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md
- 19_GATE_MATRIX_INFERENCE_CONTRACT.md
- 20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md
- 21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md
- schemas/experiment_config.schema.json
- schemas/execution_contract.schema.json
- schemas/data_manifest.schema.json
- schemas/evaluation_contract.schema.json
- schemas/checkpoint_manifest.schema.json
- schemas/run_manifest.schema.json
- schemas/reasoning_response.schema.json

Không được tạo vocabulary/config field mới ngoài schema mà không sửa schema + QA.

## 3. Artifact layout

runs/<run_id>/ chứa frozen config/contracts, per-phase manifests/checkpoints/eval, canonical checkpoint, runtime eval, export artifacts, evidence payload, external evidence.zip.sha256 và lineage.jsonl.

## 4. MVP scope

Required: decoder-only causal LLM; CPT; instruction/reasoning SFT; một PEFT hoặc full-finetune end-to-end path; exact checkpoint/resume; HF reload; GGUF convert/quantize; llama.cpp + Ollama verification; baseline/comparator evaluation; security/license/privacy checks; evidence sealing.

Not MVP: multi-node, online RLHF, multimodal, custom MoE, serving cluster/UI.

## 5. Canonical smoke model

R0 plumbing reference:
- Qwen/Qwen2.5-0.5B-Instruct
- pinned revision: 7ae557604adf67be50417f59c2c2f167def9a775
- role: smoke_reference, not scientific quality baseline.

Scientific baseline là exact parent artifact; matched-control bắt buộc khi claim so sánh phương pháp.

## 6. Read order

Đọc 00..14, sau đó 15..21, schemas/examples và cuối cùng AGENT_MASTER_PROMPT.md. QA_REMEDIATION_CHECKLIST.md là audit index.

## 7. Spec lock

Không gọi spec LOCKED cho tới khi QA vòng 2 có zero unresolved BLOCKER, examples validate schema, checklist có proof refs và SHA256SUMS đã regenerate.
