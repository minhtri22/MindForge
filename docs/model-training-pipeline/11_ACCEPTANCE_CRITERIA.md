# 11 — Acceptance Criteria

Local agent chỉ được coi implementation hoàn tất MVP khi demo end-to-end đáp ứng tất cả AC sau.

## AC-01 — One-command preflight

```text
pipeline preflight -c examples/end_to_end_small.yaml
```

PASS và sinh compatibility + environment + data reports.

## AC-02 — Public data path
Có ít nhất một adapter text public (Wikipedia-style) và một adapter code public, snapshot/fingerprint reproducible.

## AC-03 — Train/resume
Training chạy >1 checkpoint, kill/restart test resume PASS và lineage thể hiện parent checkpoint đúng.

## AC-04 — CPT + reasoning SFT
Reference run phải thực hiện ít nhất hai phases hoặc một minimal equivalent demonstrating raw-domain training + reasoning/chat behavior.

## AC-05 — Canonical Safetensors
Artifact HF canonical reload được trong fresh process và output đúng chat template.

## AC-06 — GGUF
High-fidelity GGUF tạo được từ canonical checkpoint và llama.cpp load/infer PASS.

## AC-07 — Quantized GGUF
Ít nhất một quantized target (khuyến nghị Q4_K_M cho demo) load/infer PASS; quality regression nằm trong frozen smoke threshold.

## AC-08 — Ollama
`ollama create` từ generated Modelfile PASS và chat request trả final answer.

## AC-09 — Reasoning
Với fixture reasoning-enabled, wrapper/API trả:

```json
{"reasoning":"...non-empty...","answer":"...non-empty..."}
```

và raw runtime path được evidence ghi rõ là native thinking hay tag-based fallback.

## AC-10 — Cross-runtime parity
Cùng fixture set chạy HF, llama.cpp và Ollama; adjudicator PASS theo threshold freeze.

## AC-11 — Evidence
`evidence.zip` tự đủ để audit run: config, hashes, metrics, logs summary, versions, export manifests, adjudication.

## AC-12 — No fresh-seed leakage
Test chứng minh fresh seed bị CLI từ chối trước execution lock.

## AC-13 — Unsupported architecture fail-fast
Cho một model fixture unsupported; pipeline phải FAIL ở compatibility gate trước training.

## AC-14 — No silent rescue
Khi quality gate FAIL, command kết thúc FAIL và không tự đổi LR, threshold, seed hoặc rerun training.
