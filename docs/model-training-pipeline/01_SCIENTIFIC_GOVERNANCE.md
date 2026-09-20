# 01 — Scientific Governance

## 1. Evidence classes

development dùng sửa/tune; calibration dùng khóa thresholds/hyperparameters; fresh_confirmatory chỉ dùng sau execution lock.

Freshness registry bảo vệ seed IDs, split IDs và fixture-set IDs. Development/calibration không được inspect fresh resources.

## 2. Execution lock

Execution contract phải validate schemas/execution_contract.schema.json và freeze software SHA, exact model revision, data hash, phases, token stream, baseline/comparator, seed/split/fixture registry, metrics, checkpoint selection, resource/device/precision, toolchain, retry policy và export/inference contract.

Mutation sau lock tạo run mới.

## 3. Retry

INFRA_RETRY chỉ resume exact committed checkpoint. INVALID_RUN_REPAIR làm run cũ terminal INVALID và tạo run mới có supersedes_run_id. SCIENTIFIC_RETRY bị cấm nếu chưa có execution contract mới.

## 4. Checkpoint selection

Selection phải phase-scoped: phase_id, rule, metric_id, direction, tie-breaker. Không chọn checkpoint/seed sau khi nhìn fresh result.

## 5. Baselines

Canonical semantics ở 15_BASELINE_COMPARATOR_CONTRACT.md. Mọi quality metric phải name baseline/comparator. Exact parent checkpoint là scientific baseline mặc định; smoke_reference không thay parent/matched control.

## 6. Multi-seed

Claim A > B cần matched control cùng parent, matched seeds, same data/eval split và matched budget theo frozen claim.

## 7. Phase verdict

Phase FAIL vẫn giữ lịch sử ngay cả khi phase sau recover final quality.

## 8. Adjudicator

Deterministic trên fixed evidence; đọc frozen metric contracts; xuất PASS/FAIL/INVALID; không edit threshold; không launch training; REQUIRED gate SKIPPED không phải PASS.
