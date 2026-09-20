# CL-PO — LINEAGE

Tài liệu này **append-only**.

## 2026-09-20 — Program Open

- Chương trình: `CL-PO — Continual Learning Potential Outcomes`.
- Nhánh: `research/cl-potential-outcomes`.
- Fork từ:
  - repo: `minhtri22/MindForge`;
  - branch: `research/kernel-cl`;
  - SHA: `a9159ae8f17693453e7b6378c92deb5effc4a56f`.
- Lý do mở:
  - KCL được sinh ra để chứng minh capability học liên tục của MindForge kernel;
  - KCL-6.5.9.x đã hội tụ chẩn đoán nhưng không tìm được qualified hard-label predictor/controller;
  - convergence review cấm tiếp tục feature-rescue trong `KCL-6.5.9.x`.
- Pivot:
  - từ `state → hard label → action`;
  - sang `state → action-specific continuous outcomes → contrasts/uncertainty → decision`.
- Research inputs:
  - KCL-6.5.9.x Formal Convergence Review;
  - reverse-synthesis backlog BL-1, BL-2, BL-4;
  - literature framing từ potential outcomes, dynamic treatment regimes, Q/A-learning, multi-action policy learning và uncertainty-aware decision.
- Scope khóa:
  - không mở KCL-6.5.9.9;
  - không mở KCL-7;
  - không implement controller;
  - không dùng protected KCL confirmatory seeds;
  - chưa chạy science experiment nào.
- Bước tiếp theo đúng khoa học:
  - thiết kế và freeze `CL-PO-P0 — Target-Margin / Label-Stability Qualification`.
