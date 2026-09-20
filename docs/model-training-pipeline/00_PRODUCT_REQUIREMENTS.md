# 00 — Product Requirements

## PR-001: Job-to-be-done

Người dùng cần một lệnh hoặc workflow thống nhất để biến:

```text
(base model | architecture config)
+ public datasets
+ frozen training config
```

thành:

```text
validated canonical checkpoint
+ reproducible evidence
+ GGUF
+ llama.cpp runnable model
+ Ollama runnable model
+ reasoning-capable chat behavior
```

## PR-002: User stories bắt buộc

### US-1 — Wikipedia CPT
Người dùng khai báo nguồn Wikipedia/public text. Pipeline tải/đọc snapshot cụ thể, kiểm manifest/license, normalize, deduplicate theo cấu hình, tokenize, freeze fingerprint rồi CPT trên base model.

### US-2 — Code CPT
Người dùng khai báo corpus code công khai. Pipeline phải giữ metadata nguồn/license/language, có filter binary/minified/generated files, contamination checks theo evaluation fixture, rồi train.

### US-3 — Instruction + reasoning
Sau CPT, người dùng chạy SFT trên dữ liệu conversation/instruction có cặp `reasoning` + `answer`, hoặc tiếp tục từ base model reasoning-capable. Kết quả phải hỗ trợ inference trả hai trường này riêng biệt thông qua pipeline runtime adapter.

### US-4 — Resume
Một run bị ngắt được resume từ checkpoint mà không làm mất training state. Resume phải tạo evidence cho biết checkpoint parent, step, RNG state và config hash.

### US-5 — Export
Sau PASS, `pipeline export <run_id>` sinh Safetensors/HF folder và GGUF theo các quantization target được freeze.

### US-6 — Runtime verification
`pipeline verify-runtime <run_id>` phải khởi chạy llama.cpp và Ollama thật, chạy fixture prompts, thu output/latency/tokens và adjudicate.

### US-7 — Evidence pack
`pipeline bundle <run_id>` tạo ZIP evidence có SHA256SUMS, không phụ thuộc database riêng để audit.

## PR-003: Non-functional

- Windows và Linux là target bắt buộc cho orchestration CLI.
- Python là control plane ưu tiên; trainer backend có thể dùng PyTorch/Transformers/Accelerate hoặc backend tương đương.
- Tất cả path phải hỗ trợ spaces và Unicode.
- Mọi command có `--dry-run` khi lệnh có side effect đáng kể.
- Log: JSONL machine-readable + console human-readable.
- Exit code khác 0 khi gate FAIL/INVALID.
- Idempotent cho các bước download/prepare/export nếu input hashes không đổi.
- Không ghi secret/token vào evidence.

## PR-004: Run state machine

```text
DRAFT
 -> DATA_PREPARED
 -> PREFLIGHT_PASS
 -> EXECUTION_LOCKED
 -> TRAINING
 -> TRAINED
 -> EVALUATED
 -> ADJUDICATED_PASS | ADJUDICATED_FAIL | INVALID
 -> EXPORTED
 -> RUNTIME_VERIFIED
 -> PROMOTED
```

Không cho phép nhảy từ `TRAINED` thẳng sang `PROMOTED`.

## PR-005: Success definition

Một model chỉ được gọi là “dùng được” khi:

- load được từ canonical HF checkpoint;
- generate được expected chat format;
- GGUF conversion PASS;
- llama.cpp load + inference PASS;
- Ollama create/import + inference PASS;
- reasoning contract PASS trên fixture;
- quality regression nằm trong ngưỡng đã freeze;
- evidence pack đầy đủ và checksum PASS.
