# CL-PO — Research Roadmap

Trạng thái: **FROZEN PROGRAM ORDER / CHƯA MỞ SCIENCE RUN**

## P0 — Target-Margin / Label-Stability Qualification

Mục tiêu:

Kiểm tra hard labels hiện tại có bị chi phối bởi các trường hợp nằm sát threshold hay không.

Không train predictor.

Primary outputs:

- distance của từng A/B/C outcome tới các plasticity/retention/accuracy thresholds;
- tỷ lệ record nằm trong các frozen margin bands;
- stability của hard label dưới các perturbation bands đã preregister;
- mechanism-specific concentration gần các giao điểm threshold.

Decision:

- PASS diagnostic nếu label-instability/material near-margin concentration được chứng minh;
- NEGATIVE nếu hard labels chủ yếu ổn định và xa threshold;
- cả hai outcome đều cho phép P1, nhưng interpretation khác nhau.

## P1 — Continuous Outcome Predictability

Mục tiêu:

Dự đoán trực tiếp continuous outcomes của A/B/C.

Frozen initial model order:

1. stage-conditioned mean baseline;
2. independent Ridge regressions;
3. multi-output Ridge / shared linear representation.

Không mở nonlinear model ở P1.

Primary metrics:

- MAE/RMSE từng action × outcome;
- calibration/bias theo seed và boundary;
- performance so với stage-only baseline;
- whole-seed bootstrap.

STOP nếu không có outcome nào vượt baseline với effect đủ material theo preregistered gate.

## P2 — Action Contrast / Advantage Predictability

Chỉ mở nếu P1 có signal.

Targets:

```
Delta_BA = Y_B - Y_A
Delta_CA = Y_C - Y_A
Delta_CB = Y_C - Y_B
```

*Advantage* — **lợi thế tương đối của action**.

Mục tiêu:

Kiểm tra contrast có predict ổn định hơn absolute outcomes hay không.

Không derive controller trong cùng study.

## P3 — Policy-Conditioned Factorization

Chỉ mở nếu P1/P2 cho thấy predictable quantities.

Giữ identity B/C thay vì exchange-invariant quá sớm.

Kiểm tra:

- B-specific outcome function;
- C-specific outcome function;
- shared representation vs policy-specific heads;
- ordered failure-mode stability trên fresh cohort.

## P4 — Nonlinear Comparator

Chỉ mở khi linear studies đã chứng minh signal nhưng còn residual structure có cơ sở.

Candidate order phải freeze trước:

- tree/forest-style nonlinear comparator;
- shared-trunk multi-head MLP chỉ nếu comparator trước đó cho lý do rõ.

Không dùng nonlinear model để rescue một P1/P2 null result.

## P5 — Uncertainty / Abstention Qualification

*Uncertainty* — **độ bất định**.

*Abstention* — **từ chối quyết định khi chưa đủ chắc**.

Mục tiêu:

- calibrated prediction intervals;
- coverage;
- safety-margin coverage;
- abstain rate;
- error severity conditional on non-abstained decisions.

## P6 — Policy Utility / Regret Qualification

*Regret* — **mức thiệt hại so với action oracle tốt nhất**.

Chỉ mở nếu P1–P5 đủ điều kiện.

So sánh:

- fixed A;
- fixed B;
- fixed C;
- stage-only policy;
- outcome-derived policy;
- oracle upper bound.

Primary:

- constraint-aware policy value;
- regret;
- retention violations;
- plasticity failures;
- abstention behavior.

## P7 — Independent Replication

Bất kỳ policy candidate nào trước controller đều phải replicate trên fresh cohort.

## P8 — Controller Qualification

Chỉ khi P7 PASS.

Đây mới là lúc một Task-Boundary Coordinator có thể được xem xét.

Không đồng nghĩa KCL-7 cũ tự động được mở.

---

## Protected assets

KCL protected confirmatory seeds:

```
13635,13837,14039,14241,14443,
14645,14847,15049,15251,15453,
15655,15857,16059,16261,16463,
16665,16867,17069,17271,17473
```

Trạng thái:

```
DO NOT USE IN CL-PO EXPLORATION
```

Chúng không được dùng trong P0–P6.

## Governance

Mỗi phase phải có:

```
hypothesis
→ protocol freeze
→ implementation
→ contract tests
→ fresh execution
→ evidence preserve
→ adjudication
→ paper
→ append-only lineage
```

Technical failure = REVISE.

Scientific threshold failure = NEGATIVE/STOP.

Không relax gate sau outcome.
