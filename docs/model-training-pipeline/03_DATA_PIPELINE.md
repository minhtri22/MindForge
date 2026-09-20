# 03 — Data Pipeline

## 1. Dataset spec

Mỗi source khai báo tối thiểu:

```yaml
id: wikipedia_en
kind: text
source_type: dump
uri: ...
snapshot: 2026-xx-xx
license: ...
weight: 0.70
```

Không cho `snapshot: latest` trong execution-locked run.

## 2. Required stages

```text
ACQUIRE -> VERIFY -> LICENSE -> NORMALIZE -> FILTER -> DEDUP
-> CONTAMINATION CHECK -> SPLIT -> TOKENIZE -> FINGERPRINT -> FREEZE
```

### Acquire
- download resumable;
- checksum upstream artifact nếu có;
- cache theo content hash.

### Verify
- file readable;
- schema expected;
- counts and sizes recorded.

### License
- source-level license bắt buộc;
- code corpus ưu tiên metadata per-file/repository;
- unknown/disallowed licenses được quarantine hoặc fail theo policy.

### Normalize text
- Unicode normalization cấu hình rõ;
- loại control chars không hợp lệ;
- không làm thay đổi code indentation ngoài rule cho phép;
- giữ document boundaries.

### Filter
Text: min/max length, language filter nếu bật, markup cleanup.
Code: binary/generated/minified/vendor mirror detection theo config.

### Dedup
- exact hash dedup bắt buộc;
- near-dedup configurable;
- report số document/token loại bỏ.

### Contamination
- eval fixtures phải có hashes/n-gram signatures;
- scan train corpus trước freeze;
- policy: remove/quarantine/fail.

### Split
- deterministic bởi seed + document identity;
- split manifest lưu IDs/hashes, không chỉ percentages.

### Tokenize
- dùng tokenizer canonical của base model trừ khi experiment explicitly thay tokenizer;
- mọi tokenizer change phải coi là architecture-level change và rerun compatibility/export preflight.

## 3. Data lineage

Mỗi processed shard phải ghi:

```json
{
  "source_id": "...",
  "source_snapshot": "...",
  "input_hash": "...",
  "transform_version": "...",
  "output_hash": "...",
  "document_count": 0,
  "token_count": 0,
  "license_summary": {}
}
```

## 4. Dataset mixture

Mixture phải freeze bằng token budget, không chỉ số document.

Ví dụ:

```yaml
mixture:
  - source: wikipedia
    target_token_fraction: 0.60
  - source: code
    target_token_fraction: 0.40
```

Report actual achieved fraction và deviation.

## 5. Dữ liệu reasoning

Raw Wikipedia/code không đủ để dạy chat reasoning. Reasoning SFT dataset phải normalize về schema:

```json
{
  "messages": [...],
  "reasoning": "...",
  "answer": "...",
  "source": "...",
  "license": "...",
  "verifier": {"type": "...", "result": "..."}
}
```

Ưu tiên rationale có final answer kiểm chứng được (math/code/unit tests/factual citation target). Không gắn nhãn rationale là “faithful internal reasoning”; chỉ là supervised reasoning trace.
