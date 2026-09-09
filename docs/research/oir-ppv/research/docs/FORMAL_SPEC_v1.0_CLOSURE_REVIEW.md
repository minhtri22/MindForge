# OIR-PPV FORMAL_SPEC v1.0 — Closure Review

**Ngày:** 2026-09-09  
**Nguồn review:** `formal_revised_v1.0.md`  
**Kết quả:** `PASS_WITH_AMENDMENTS -> FINAL`

## 1. Phán quyết

Bản revised draft đã giải quyết các lỗi khái niệm chính của ontology và hầu hết lỗi đặc tả đo lường. Closure review tìm thấy 7 điểm còn cần sửa trước khi có thể gọi là `FINAL`, và các điểm này đã được áp dụng trực tiếp vào `formal_spec_v1.0_FINAL.md`.

Không còn blocker ở cấp đặc tả.

## 2. Các blocker đã sửa

1. **Thiếu định nghĩa explicit cho transfer risk.**  
   Đã tách `R_int-suff` trong miền học/xác thực khỏi `R_transfer` trên held-out shift.

2. **Thiếu task/counterfactual risk rõ ràng.**  
   Đã thêm `R_task` và `R_cf`.

3. **Approximate equivalence không phải quan hệ tương đương toán học.**  
   Đã tách:
   - `~_Q`: functional equivalence;
   - `≈_{Q,epsilon}`: empirical indistinguishability.

4. **Shift classes có thể chồng lấn.**  
   Đã thêm `shift_profile_realized` đa nhãn.

5. **Một số estimand dùng shorthand chưa đủ điều kiện hóa.**  
   Đã chuẩn hóa theo `(I_M,S,Z,a)` và SCM `do(A=a)`.

6. **Thiếu metric registry chuẩn.**  
   Đã thêm schema bắt buộc cho orientation, evidence requirements, aggregation, uncertainty và acceptance.

7. **Closure gate của Formal Spec bị trộn với readiness của benchmark đầu tiên.**  
   Đã tách:
   - `Formal-Spec Closure Gate`;
   - `Benchmark Protocol Activation Gate`.

## 3. Closure matrix

| Hạng mục | Kết quả |
|---|---|
| Ontology consistency | PASS |
| Mechanism/representation/state/environment separation | PASS |
| Shift semantics | PASS |
| Observation/intervention/counterfactual separation | PASS |
| Interventional sufficiency | PASS |
| Transfer definition | PASS |
| Test leakage boundary | PASS |
| Noise semantics | PASS |
| Representation equivalence semantics | PASS |
| Cost scope | PASS |
| Statistical uncertainty contract | PASS |
| Evidence-level contract | PASS |
| Generation acceptance orientation | PASS |
| H1–H6 dependency typing | PASS |
| Provenance/versioning schema | PASS |

## 4. Claim boundary

`FINAL` có nghĩa đặc tả chuẩn hóa đã đủ rõ để một benchmark protocol độc lập có thể instantiate nó.

`FINAL` **không** có nghĩa:
- H1–H6 đã được chứng minh;
- benchmark H3/H4/H5/H6 đã sẵn sàng;
- thresholds/seeds/environments đã được khóa;
- OIR-PPV đã có bằng chứng causal trên dữ liệu thực.

Mỗi decisive benchmark vẫn phải vượt `Benchmark Protocol Activation Gate`.

## 5. Trạng thái cuối

`FORMAL_SPEC_v1.0 = FINAL`

`BENCHMARK_PROTOCOLS = REQUIRE_INDIVIDUAL_FREEZE_AND_QA`
