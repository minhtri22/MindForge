# 06 — Checkpoint & Provenance

## 1. Checkpoint content

Recoverable checkpoint phải chứa hoặc tham chiếu bằng hash tới:

```text
model weights
optimizer state
scheduler state
AMP/scaler state (nếu có)
RNG states (Python/NumPy/framework CPU/GPU)
dataloader/sampler progress
global step / consumed tokens
trainer config hash
data manifest hash
parent checkpoint id
```

## 2. Canonical checkpoint

Canonical checkpoint là artifact được checkpoint-selection rule chọn. Folder tối thiểu:

```text
canonical/
├── config.json
├── generation_config.json          # nếu dùng
├── tokenizer.json / tokenizer.model
├── tokenizer_config.json
├── special_tokens_map.json         # nếu có
├── chat_template metadata          # theo format framework
├── model*.safetensors
├── training_state.json
├── provenance.json
└── SHA256SUMS
```

## 3. provenance.json

Bắt buộc có:

```json
{
  "run_id": "...",
  "parent_model": {"id": "...", "hash": "..."},
  "git": {"commit": "...", "dirty": false},
  "data_manifest_hash": "...",
  "config_hash": "...",
  "seed": 0,
  "global_step": 0,
  "consumed_tokens": 0,
  "checkpoint_selection_rule": "...",
  "environment_hash": "...",
  "trainer_backend": "...",
  "created_at_utc": "..."
}
```

## 4. Hash policy

- SHA-256 cho files/artifacts.
- Canonical JSON serialization trước khi hash config/manifest.
- Directory hash = sorted list `relative_path + file_sha256` rồi hash manifest.
- Không hash dựa trên mtime.

## 5. Append-only lineage

`lineage.jsonl` append-only:

```json
{"event":"RUN_CREATED", ...}
{"event":"DATA_FROZEN", ...}
{"event":"EXECUTION_LOCKED", ...}
{"event":"CHECKPOINT_WRITTEN", ...}
{"event":"CANONICAL_SELECTED", ...}
{"event":"GGUF_EXPORTED", ...}
{"event":"OLLAMA_VERIFIED", ...}
{"event":"PROMOTED", ...}
```

Mỗi event có previous-event hash để phát hiện chỉnh sửa lịch sử.
