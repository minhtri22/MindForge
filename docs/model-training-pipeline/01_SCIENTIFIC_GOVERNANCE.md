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


## 9. Infrastructure / science separation

Canonical amendment: `23_INFRASTRUCTURE_SCIENCE_SEPARATION.md`.

Three distinct control objects are mandatory:

- `SCIENCE_GATE`: hypothesis/treatment/endpoint/comparator/freshness/outcome rules.
- `INFRA_QUALIFICATION`: runtime/harness/substrate/tooling qualification using non-study evidence.
- `INFRA_BINDING_CHECK`: exact binding of a study to an already-qualified infra scope.

An infrastructure failure may block dependent execution but may not set a scientific FAIL.

Before scientific outcome exposure, a pure infrastructure/orchestration/substrate defect does not consume scientific retry/repair budget. After outcome exposure, an infrastructure invariant violation invalidates interpretation and replacement is allowed only under the frozen invalid-run policy with exact-unchanged science.

Scientific design, prior-art work, static implementation and zero-science QA may proceed while infrastructure remains unresolved.

A reusable infra qualification is not rerun when its scope tuple is unchanged; future studies perform one consolidated binding check instead.
