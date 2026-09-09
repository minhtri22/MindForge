DEV_TASK_004 — M2 Baseline Benchmark Suite Implementation
Mục tiêu:
- Chuyển từ M1 (Controlled Environment Implementation) sang M2 (Baseline Benchmark Suite).
- Xây dựng framework benchmark reproducible trên ENV-1 → ENV-4 đã freeze.
Phạm vi:
- Benchmark runner.
- Baseline interface B0-B5.
- Metric collection:
  - Generalization
  - Intervention stability
  - Generation quality
  - Provenance completeness
Acceptance:
- Cùng protocol đánh giá cho mọi baseline.
- Deterministic với seed cố định.
- Sinh artifact evidence.
- Chuẩn bị HANDOFF_003.md.
Đã khóa constraint:
- Không sửa M1 environment generators nếu không có QA blocking defect.
- Không tối ưu model trong task này.
- Giữ nguyên provenance format.