# 01 — Scientific Governance

## 1. Tách development và confirmatory

Mỗi experiment config phải phân loại seed/split:

- `development`: dùng để sửa code/tune.
- `calibration`: dùng khóa threshold/hyperparameter trước execution lock.
- `fresh_confirmatory`: chỉ được chạm sau `EXECUTION_LOCKED`.

CLI phải chặn dùng seed thuộc `fresh_confirmatory` khi lock chưa PASS.

## 2. Execution contract

Trước training confirmatory, tạo `execution_contract.json` chứa:

- claim/hypothesis id;
- model/base SHA hoặc artifact hash;
- exact dataset fingerprints + split hashes;
- trainer config hash;
- seed list;
- max steps/tokens;
- optimizer/scheduler;
- checkpoint-selection rule;
- evaluation metrics;
- thresholds;
- failure policy;
- allowed retry policy;
- llama.cpp commit SHA;
- Ollama version expectation;
- expected export formats.

Contract immutable sau lock. Nếu thay đổi -> run mới.

## 3. Retry policy

Phân biệt:

- `INFRA_RETRY`: process crash, disk full, runner lost. Cho phép nếu training state được resume đúng và config hash không đổi.
- `INVALID_RUN_REPAIR`: bug làm evidence vô hiệu; phải record invalidation và mở run mới/repair theo policy.
- `SCIENTIFIC_RETRY`: không được tự động chạy seed mới chỉ vì metric FAIL.

## 4. Checkpoint-selection rule

Phải freeze một trong các kiểu:

- fixed step;
- min validation loss;
- max frozen metric;
- early stopping với exact patience/min_delta;
- last checkpoint.

Cấm chọn checkpoint/seed sau khi nhìn fresh result mà không có rule định trước.

## 5. Multi-seed evidence

Nếu claim là “phương pháp A tốt hơn B”, pipeline phải hỗ trợ matched seed/budget và report distribution. Deployment checkpoint có thể là một artifact duy nhất nhưng không được dùng artifact đó thay cho claim-level evidence.

## 6. Adjudicator

Adjudicator phải:

- deterministic với cùng input evidence;
- đọc threshold từ frozen contract;
- xuất `PASS | FAIL | INVALID` + reasons;
- không tự sửa threshold;
- không tự mở training mới.
