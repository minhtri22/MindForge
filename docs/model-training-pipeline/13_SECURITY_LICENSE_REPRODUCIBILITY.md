# 13 — Security, License, Reproducibility

## 1. Secrets

- HF tokens, Git tokens, private credentials chỉ lấy từ env/keyring.
- Redact logs/evidence.
- Config được bundle không chứa secrets.

## 2. Remote code

Model/dataset nào yêu cầu `trust_remote_code` phải bị deny mặc định. Chỉ enable bằng explicit allowlist + source revision pin + code review record.

## 3. Dataset licenses

Mỗi data source có license declaration. Với mixed code datasets, unknown license phải được xử lý theo policy `deny|quarantine|allow_with_record`, mặc định `deny` cho release artifact.

## 4. Model license

Base model license phải được copy/reference trong release manifest. Pipeline không tự tuyên bố quyền redistribute nếu upstream không cho phép.

## 5. Supply-chain

- pin Python packages;
- record wheels/package hashes khi possible;
- pin llama.cpp commit;
- record Ollama exact version;
- checksum downloaded model/data artifacts.

## 6. Reproducibility bundle

Evidence phải đủ để một machine tương thích biết:

- code SHA nào;
- dependency versions nào;
- model revision nào;
- data snapshot nào;
- preprocess transforms nào;
- config nào;
- seed nào;
- training resource class nào;
- export tool version nào.

Không bắt buộc exact bitwise equality trên mọi GPU/backend; reproducibility contract phải nêu rõ mức kỳ vọng.
